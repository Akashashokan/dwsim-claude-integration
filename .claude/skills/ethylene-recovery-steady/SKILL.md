---
name: ethylene-recovery-steady
description: Build and converge a steady-state ethylene cracker recovery section in DWSIM from quench tower overhead through polymer-grade ethylene product using incremental unit-op assembly, realistic operating windows, and artifact persistence.
---

# Ethylene Recovery (Steady-State) Skill

Use this skill when the user asks to create, expand, or troubleshoot the **ethylene cracker recovery section** in DWSIM.

## Scope

Covers the recovery path from **quench tower overhead cracked gas boundary** to **polymer-grade ethylene product/export**:
- Cracked gas compression (multi-stage + intercooling + KO drums)
- Acid gas removal (surrogate first, then rigorous if needed)
- Molecular sieve drying (steady-state surrogate)
- Chilling/cold-box structure
- Demethanizer, deethanizer, acetylene hydrogenation, C2 splitter
- Ethane recycle and tail-gas boundary handling

Use open-source DWSIM functionality only.

## Required source of truth

Before building, read:
1. `Ethylene Cracker Engineering Data.md` for operating windows, compositions, and sequencing.
2. Existing repository skill rules in `.claude/skills/dwsim/SKILL.md`.

If values are missing, prefer the ranges in `Ethylene Cracker Engineering Data.md` over generic defaults.

## Mandatory build strategy (do not skip)

1. Build one section at a time and solve after each addition.
2. Keep early model acyclic (no destabilizing recycle loops).
3. Add columns in strict order:
   - Demethanizer
   - Deethanizer
   - Acetylene hydrogenation
   - C2 splitter
4. Only add light-ends recycle after the once-through train converges.
5. For each successful step, persist artifacts:
   - `.dwxmz`
   - `.xlsx`
   - `.py`

## Default component list

Start with:
- H2, CH4, C2H4, C2H6, C2H2, C3H6, C3H8
- 1-Butene (C4 surrogate), 1,3-butadiene
- Benzene (C6+ surrogate)
- CO, CO2, H2S, H2O

## Thermodynamic policy

- Hydrocarbon network: use **PR or PRSV2** (default PRSV2 when cryogenic sections are present).
- Keep a consistent EOS across tightly coupled hydrocarbon sections to avoid recycle instability.
- For caustic/aqueous treating, start with surrogate removal first; only move to electrolyte treatment after hydrocarbon core converges.

## Convergence guardrails

- Compression ladder initialization: 1→4→16→32 bar then refine to 5-stage (1→2→4→8→16→32 bar equivalent).
- Enforce compressor discharge/interstage constraints (target <= 100 °C).
- Dryer outlet target: < 1 ppmv H2O before cold section.
- Begin demethanizer/deethanizer/C2 splitter with reduced stage count and relaxed specs, then ramp to target design.

## Output contract

When executing this skill in a task response:
- Report assumptions and chosen operating ranges explicitly.
- Report convergence status per section (compression, treating, drying, cold box, columns).
- Call out unresolved specs that block full polymer-grade target attainment.
