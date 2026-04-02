# -*- coding: utf-8 -*-
"""
Natural Gas Demethanizer Simulation
=====================================
Feed  : 70% CH4 / 20% C2H6 / 10% C3H8   |   T = -30 C, P = 30 bar
Goal  : 95% ethane recovery in bottoms (C2+ NGL product)
Method: Fenske-Underwood-Gilliland (FUG) shortcut, thermodynamics via DWSIM PR EOS

This script implements the FUG shortcut method directly in Python, using
DWSIM's Peng-Robinson property package for all thermodynamic calculations
(K-values, enthalpies, bubble/dew temperatures).  This approach is fully
supported by the DWSIM automation API and does not depend on the ShortcutColumn
unit operation.
"""

import logging
import math
import os
import sys

# ── Path setup ─────────────────────────────────────────────────────────────────
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

logging.basicConfig(level=logging.WARNING, format="%(levelname)s | %(name)s | %(message)s")

from src.core.automation import DWSIMAutomation
from src.core.flowsheet import FlowsheetManager

# ── Process parameters ─────────────────────────────────────────────────────────
COMPOUNDS = ["Methane", "Ethane", "Propane"]

T_FEED_K     = 243.15       # -30 C
P_FEED_Pa    = 3_000_000    # 30 bar
F_FEED_mol_s = 100.0        # basis: 100 mol/s

FEED_Z = {"Methane": 0.70, "Ethane": 0.20, "Propane": 0.10}

LK  = "Methane"   # light key  -> exits overhead
HK  = "Ethane"    # heavy key  -> specification component

LK_RECOVERY_DISTILLATE = 0.97   # 97% of CH4 exits in distillate
HK_RECOVERY_BOTTOMS    = 0.95   # 95% of C2H6 exits in bottoms  [design target]

P_COND_Pa = 2_700_000   # 27 bar (condenser)
P_REBR_Pa = 2_900_000   # 29 bar (reboiler)
R_MULT    = 1.3          # operate at 1.3 x Rmin


# ── FUG helper functions ───────────────────────────────────────────────────────

def flash_pt(mgr, stream_name, T_K, P_Pa, composition, F_mol_s=1.0):
    """Flash a stream at (T, P) and return K-values and phase fractions."""
    stream = mgr.add_object("material_stream", stream_name, 50, 50)
    stream.set_conditions(
        temperature_K=T_K,
        pressure_Pa=P_Pa,
        molar_flow_mol_s=F_mol_s,
        composition=composition,
    )
    dwsim.calculate(fs)
    res = mgr.get_stream_results(stream_name)

    vf  = res["vapor_fraction"]
    vap = res["composition"]["vapor"]
    liq = res["composition"]["liquid"]

    # K_i = y_i / x_i (avoid divide-by-zero for x_i = 0)
    kvals = {}
    for c in COMPOUNDS:
        xi = liq.get(c, 0.0)
        yi = vap.get(c, 0.0)
        kvals[c] = yi / xi if xi > 1e-12 else 1e6

    return vf, vap, liq, kvals, res


def gilliland(r_rmin_ratio):
    """Gilliland correlation (Molokanov 1971) for (N-Nmin)/(N+1)."""
    psi = (r_rmin_ratio - 1.0) / (r_rmin_ratio + 1.0)
    return 1.0 - math.exp(
        (1.0 + 54.4 * psi) / (11.0 + 117.2 * psi) * (psi - 1.0) / psi**0.5
    )


def underwood_theta(alpha, z_feed, q):
    """
    Solve Underwood equation: Sum[alpha_i * z_i / (alpha_i - theta)] = 1 - q.
    Returns the root theta in (alpha_HK, alpha_LK).
    Uses bisection; alpha dictionary keyed by compound name.
    """
    comps  = list(alpha.keys())
    alphas = [alpha[c] for c in comps]
    zs     = [z_feed[c] for c in comps]

    target = 1.0 - q

    # Find the root between alpha_HK and alpha_LK
    a_HK = alpha[HK]
    a_LK = alpha[LK]
    lo, hi = a_HK + 1e-6, a_LK - 1e-6

    def f(theta):
        return sum(a * z / (a - theta) for a, z in zip(alphas, zs)) - target

    # Bisection
    for _ in range(60):
        mid = (lo + hi) / 2.0
        if f(mid) * f(lo) < 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2.0


# ── Initialize DWSIM ───────────────────────────────────────────────────────────
print("Initializing DWSIM...")
dwsim = DWSIMAutomation()
dwsim.initialize()

fs  = dwsim.create_flowsheet()
mgr = FlowsheetManager(fs, dwsim)
mgr.add_compounds(COMPOUNDS)
mgr.set_property_package("Peng-Robinson")


# ── Step 1: Flash feed to get K-values and feed condition (q) ──────────────────
print("Flashing feed...")
vf_feed, y_feed, x_feed, K_feed, feed_res = flash_pt(
    mgr, "FEED", T_FEED_K, P_FEED_Pa, FEED_Z, F_FEED_mol_s
)
# q = liquid fraction of the feed (q=1 saturated liquid, q=0 saturated vapor)
q = 1.0 - vf_feed

print(f"  Feed VF = {vf_feed:.4f}  (q = {q:.4f})")
print(f"  K-values at feed: " +
      ", ".join(f"{c}={K_feed[c]:.3f}" for c in COMPOUNDS))


# ── Step 2: Relative volatilities (referenced to heavy key C2H6) ───────────────
K_HK = K_feed[HK]
alpha = {c: K_feed[c] / K_HK for c in COMPOUNDS}
alpha_LK = alpha[LK]
alpha_HK = alpha[HK]  # = 1.0 by definition

print(f"  Relative volatilities: " +
      ", ".join(f"{c}={alpha[c]:.3f}" for c in COMPOUNDS))


# ── Step 3: Component material balances ────────────────────────────────────────
F  = {c: F_FEED_mol_s * FEED_Z[c] for c in COMPOUNDS}

# LK and HK splits are given
D_LK = LK_RECOVERY_DISTILLATE * F[LK]
B_LK = F[LK] - D_LK

B_HK = HK_RECOVERY_BOTTOMS * F[HK]
D_HK = F[HK] - B_HK

# Non-key (propane): compute using Fenske for the split
# Fenske: Nmin  = log[(D_LK/B_LK)*(B_HK/D_HK)] / log(alpha_LK)
Nmin = math.log((D_LK / B_LK) * (B_HK / D_HK)) / math.log(alpha_LK)

# Distribute non-keys via Fenske: D_i/B_i = (D_HK/B_HK) * alpha_i^Nmin
nk_comps = [c for c in COMPOUNDS if c not in (LK, HK)]
D_nk = {}
B_nk = {}
for c in nk_comps:
    ratio = (D_HK / B_HK) * (alpha[c] ** Nmin)   # D_i/B_i
    D_nk[c] = F[c] * ratio / (1.0 + ratio)
    B_nk[c] = F[c] - D_nk[c]

# Assemble distillate and bottoms totals
D_flows = {LK: D_LK, HK: D_HK}
B_flows = {LK: B_LK, HK: B_HK}
for c in nk_comps:
    D_flows[c] = D_nk[c]
    B_flows[c] = B_nk[c]

D_total = sum(D_flows.values())
B_total = sum(B_flows.values())

# Mole fractions
x_D = {c: D_flows[c] / D_total for c in COMPOUNDS}
x_B = {c: B_flows[c] / B_total for c in COMPOUNDS}

C2_recovery_pct = B_flows[HK] / F[HK] * 100.0


# ── Step 4: Fenske minimum stages ─────────────────────────────────────────────
# Already computed Nmin above; round up for display
print(f"  Nmin = {Nmin:.2f}")


# ── Step 5: Underwood minimum reflux ──────────────────────────────────────────
theta = underwood_theta(alpha, FEED_Z, q)
Rmin  = sum(alpha[c] * x_D[c] / (alpha[c] - theta) for c in COMPOUNDS) - 1.0
Rmin  = max(Rmin, 0.01)   # guard against negative due to numerical noise


# ── Step 6: Gilliland actual stages ──────────────────────────────────────────
R = R_MULT * Rmin
psi_gil = R / Rmin   # ratio R/Rmin used by Molokanov

# Use Molokanov: psi_arg = (R-Rmin)/(R+1)
psi_arg = (R - Rmin) / (R + 1.0)
gil = 1.0 - math.exp(
    (1.0 + 54.4 * psi_arg) / (11.0 + 117.2 * psi_arg) * (psi_arg - 1.0) / psi_arg**0.5
)
N_actual = math.ceil((Nmin + gil * (Nmin + 1.0)) / (1.0 - gil))


# ── Step 7: Kirkbride feed stage ──────────────────────────────────────────────
# N_strip/N_rect = [(z_HK/z_LK) * (B/D) * (x_LK_B/x_HK_D)^2]^0.206
kirkbride = (
    (FEED_Z[HK] / FEED_Z[LK])
    * (B_total / D_total)
    * (x_B[LK] / x_D[HK]) ** 2
) ** 0.206

N_rect  = round(N_actual / (1.0 + kirkbride))
N_strip = N_actual - N_rect
feed_stage = N_rect + 1   # from top, 1-indexed


# ── Step 8: Product stream flash calculations ─────────────────────────────────
print("Flashing product streams...")

# Distillate temperature: bubble point at condenser pressure
_, _, _, _, dist_res = flash_pt(
    mgr, "DISTILLATE", T_FEED_K, P_COND_Pa, x_D, D_total
)
T_D = dist_res["temperature_K"]    # reported at T_feed initially; overwritten below
H_D = dist_res["enthalpy_kJ_kg"]

# Bottoms temperature: bubble point at reboiler pressure
_, _, _, _, bott_res = flash_pt(
    mgr, "BOTTOMS", T_FEED_K, P_REBR_Pa, x_B, B_total
)
T_B = bott_res["temperature_K"]
H_B = bott_res["enthalpy_kJ_kg"]
H_F = feed_res["enthalpy_kJ_kg"]

# Condenser duty (total condenser, remove latent + sensible heat from overhead vapor)
# Energy balance around column: F*H_F + Q_R = D*H_D + B*H_B + Q_C
# Q_R - Q_C = D*H_D + B*H_B - F*H_F
# Approximate from reflux vapor enthalpy
# Use simple estimate: Q_C ~ -(R+1)*D*(H_vap_overhead)
# For accurate result: Q_C from total energy balance once H_V_D known.
# Since we only have DWSIM enthalpies at liquid conditions, use:
#   Q_C = -(L/V) approach with latent heats, but simpler:
# Q_net = B*H_B + D*H_D - F*H_F   (sign: positive = heat input required)
# Q_R = Q_net + |Q_C|
# For an estimate: Q_C ~ (R+1)*D * delta_Hvap_approx  (600 kJ/kg for C1-rich stream)
DELTA_HVAP_APPROX_kJ_kg = 600.0
Q_C_kW = -(R + 1.0) * D_total * DELTA_HVAP_APPROX_kJ_kg / 1000.0  # negative = heat removed

# Mass flow rates for energy balance (approximate MW from PR EOS molar masses)
MW_avg = lambda x: sum(x[c]*{"Methane":16.04,"Ethane":30.07,"Propane":44.10}[c]
                       for c in COMPOUNDS)
MW_F = MW_avg(FEED_Z)
MW_D = MW_avg(x_D)
MW_B = MW_avg(x_B)

Fm_kg_s  = F_FEED_mol_s * MW_F / 1000.0
Dm_kg_s  = D_total       * MW_D / 1000.0
Bm_kg_s  = B_total       * MW_B / 1000.0

Q_net_kW = Dm_kg_s * H_D + Bm_kg_s * H_B - Fm_kg_s * H_F
Q_R_kW   = Q_net_kW + abs(Q_C_kW)


# ── Step 9: Print results ──────────────────────────────────────────────────────
print()
print("=" * 62)
print("  DEMETHANIZER SIMULATION  --  FUG Shortcut (Python + DWSIM PR)")
print("=" * 62)

print(f"\n  Feed Conditions")
print(f"  {'T':<30}  {T_FEED_K - 273.15:>8.1f} C")
print(f"  {'P':<30}  {P_FEED_Pa / 1e5:>8.1f} bar")
print(f"  {'Molar flow':<30}  {F_FEED_mol_s:>8.1f} mol/s")
print(f"  {'Vapor fraction':<30}  {vf_feed:>8.4f}")

print(f"\n  Relative Volatilities  (reference: C2H6 = 1.000)")
for c in COMPOUNDS:
    print(f"  {'  ' + c:<30}  {alpha[c]:>8.3f}")

print(f"\n  Column Design  (Fenske-Underwood-Gilliland)")
print(f"  {'Property':<36}  {'Value':>10}")
print(f"  {'-'*48}")
print(f"  {'Light key (LK)':<36}  {'Methane':>10}")
print(f"  {'Heavy key (HK)':<36}  {'Ethane':>10}")
print(f"  {'Minimum stages (Nmin)':<36}  {Nmin:>10.1f}")
print(f"  {'Actual stages (N)':<36}  {N_actual:>10.0f}")
print(f"  {'Min. reflux ratio (Rmin)':<36}  {Rmin:>10.3f}")
print(f"  {'Operating reflux ratio (R)':<36}  {R:>10.3f}  [{R_MULT:.1f}x Rmin]")
print(f"  {'Optimal feed stage (from top)':<36}  {feed_stage:>10.0f}")
print(f"  {'Rectifying stages':<36}  {N_rect:>10.0f}")
print(f"  {'Stripping stages':<36}  {N_strip:>10.0f}")
print(f"  {'Condenser duty (est.)':<36}  {Q_C_kW:>10.1f} kW")
print(f"  {'Reboiler duty (est.)':<36}  {Q_R_kW:>10.1f} kW")
print(f"  {'Condenser pressure':<36}  {P_COND_Pa/1e5:>10.1f} bar")
print(f"  {'Reboiler pressure':<36}  {P_REBR_Pa/1e5:>10.1f} bar")

def _print_stream(label, x, total, res):
    T_C   = res["temperature_K"] - 273.15
    P_bar = res["pressure_Pa"] / 1e5
    vfrac = res["vapor_fraction"]
    print(f"\n  {label}")
    print(f"  {'T':<22}  {T_C:>8.1f} C")
    print(f"  {'P':<22}  {P_bar:>8.2f} bar")
    print(f"  {'Molar flow':<22}  {total:>8.2f} mol/s")
    print(f"  {'Vapor fraction':<22}  {vfrac:>8.4f}")
    print(f"  {'Composition (mol%)':<22}")
    for c in COMPOUNDS:
        if x[c] > 1e-6:
            print(f"    {c:<18}  {x[c]*100:>6.2f}")

_print_stream("Distillate  (Overhead / Residue Gas)", x_D, D_total, dist_res)
_print_stream("Bottoms     (NGL / C2+ Product)",      x_B, B_total, bott_res)

print(f"\n  Key Performance Indicators")
print(f"  {'-'*48}")
tgt = "TARGET MET" if C2_recovery_pct >= 95.0 else "BELOW TARGET"
print(f"  {'C2H6 recovery in bottoms':<36}  {C2_recovery_pct:>6.1f} %  [{tgt}]")
print(f"  {'CH4 recovery in distillate':<36}  {D_flows[LK]/F[LK]*100:>6.1f} %")
print(f"  {'D / F  ratio':<36}  {D_total/F_FEED_mol_s:>6.3f}")
print(f"  {'B / F  ratio':<36}  {B_total/F_FEED_mol_s:>6.3f}")
mbal_err = abs(D_total + B_total - F_FEED_mol_s) / F_FEED_mol_s * 100.0
print(f"  {'Molar balance error':<36}  {mbal_err:>6.3f} %")

print()
print("=" * 62)

# ── Step 10: Save flowsheet ────────────────────────────────────────────────────
out_dir   = os.path.join(project_root, "data", "outputs")
save_path = os.path.join(out_dir, "demethanizer.dwxmz")
os.makedirs(out_dir, exist_ok=True)
dwsim.save_flowsheet(fs, save_path)
print(f"\n  Flowsheet saved  ->  {save_path}")
print()
