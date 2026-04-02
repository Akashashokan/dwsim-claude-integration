# Engineering Data Package for an Ethylene Cracker Recovery Section Simulation in DWSIM

## Thermodynamics and DWSIM digital-twin execution basis

### Thermodynamic model selection for this recovery section
DWSIM’s own guidance is to use **Equation-of-State (EOS)** models (e.g., Peng–Robinson) for **non‑polar gases at high pressures (>10 atm)**, and to consider **hydrogen-system-specialized models** (e.g., Lee–Kesler–Plöcker / Chao–Seader / Grayson–Streed) for **systems with high hydrogen content**. citeturn15view0

For an ethylene recovery section, the most simulation-stable starting point is typically:

| Section | Recommended DWSIM Property Package | Typical industry guidance | Simulation starting assumption | Needs project-specific validation |
|---|---|---|---|---|
| Main hydrocarbon system (compression → drying → cold section → demeth/deeth/C2 splitter) | **Peng–Robinson (PR)** (or PRSV2 if parameters exist) | EOS is standard for high-pressure, nonpolar/light hydrocarbon systems citeturn15view0turn22view0 | Use **PR** globally for first converged steady-state | Check binary interaction parameters vs. plant test data; PRSV2 parameter availability can be incomplete citeturn15view0 |
| Hydrogen-rich tail gas and demeth overhead | PR or Lee–Kesler–Plöcker (LKP) | DWSIM notes **LKP/Chao–Seader/Grayson–Streed** can be used for high H₂ systems citeturn15view0 | Keep **PR** for entire flowsheet initially; validate tail gas properties separately with LKP sensitivity | Validate compressor/expander polytropic head and cold-end VLE for H₂/CH₄-rich mixtures vs. plant data |
| Caustic/water wash | Surrogate (component removal) or Aqueous Electrolytes PP | True electrolyte chemistry is complex; ethylene plants often implement caustic wash and water wash around treating citeturn12view0turn11view1 | Use **component split + pressure drop + temperature approach** (simulation-friendly) | If you later need NaOH/CO₂/H₂S speciation, migrate treating to a specialized electrolyte model outside DWSIM or via CAPE-OPEN citeturn15view0turn9view3 |
| Refrigeration cycles | Not modeled rigorously (per your scope) | Interface-only duties/ΔT setpoints are common for digital-twin foundations | Use fixed outlet temperatures / fixed UA per exchanger | Validate temperature levels against actual cold box temperature profile |

### Steady-state vs. dynamic feasibility in DWSIM
DWSIM’s dynamic mode supports (among others) **Valve, Gas–Liquid Separator, Tank, Compressor, Expander, Pump, Heater, Cooler, Mixer, Splitter, Heat Exchanger, General Reactors (conversion/equilibrium/gibbs), CSTR, PFR, Python Script Block**, and a **Specification Logical Block**. citeturn9view3  
Unsupported unit operations show an “unsupported” icon when dynamic mode is enabled. citeturn9view5turn9view1

Practical implication for this recovery section:  
- **Rigorous distillation columns** are best treated as **steady-state “anchors”** (demethanizer, deethanizer, C2 splitter).  
- A realistic “hybrid” digital twin in DWSIM is built by keeping columns steady-state and running **dynamic holdup + controls** around: KO drums, tanks, valves, compressors, coolers/heaters, reactors, and boundary controllers. citeturn9view3turn8view1

### Synthetic data generation hooks (native DWSIM)
- **Monitored Variables**: integrators can store selected object properties every integration step, exportable for later use. citeturn8view1  
- **Automation**: DWSIM exposes COM/.NET automation interfaces; the Automation API includes methods such as `CalculateFlowsheet(...)`. citeturn15view3turn15view2  
- **Property codes**: DWSIM publishes “object property codes” for stream properties (T, P, flows, densities, enthalpy/entropy, phase properties, Z, viscosities, etc.), enabling consistent historian-like tag extraction. citeturn15view1

Referenced entities (used once for navigation): entity["organization","National Institute of Standards and Technology","us measurement standards agency"] entity["organization","Sulzer","process separation equipment company"] entity["organization","KLM Technology Group","engineering guidelines publisher | johor bahru, my"] entity["organization","American Petroleum Institute","industry standards body"] entity["people","Daniel Wagner Oliveira de Medeiros","dwsim developer"]

## Master table – Ethylene cracker recovery unit list

| Unit Name | Function | Main KPIs | Main Utilities | Main Sizing Parameters | DWSIM Modeling Approach |
|---|---|---|---|---|---|
| Quench Overhead Cracked Gas Source (Boundary) | Defines inlet cracked gas conditions | Feed rate stability, C₂H₂/CO₂/H₂S variability | None | N/A | Material Stream + boundary controllers |
| Suction KO Drum | Knock out liquids before CGC | Liquid carryover, ΔP | None | Souders–Brown KS; liquid holdup | Separator (dynamic-capable) citeturn9view3turn32view0 |
| Cracked Gas Compressor Train (5 stages) | Compress ~1 bar to ~32 bar | Stage efficiency, discharge T, power, surge margin | Electricity/driver | Stage PR, polytropic efficiency | Compressors + anti-surge recycle loop citeturn5view0turn22view0turn9view3 |
| Interstage Intercoolers (x5) | Cool gas between stages | Outlet T approach, duty | Cooling water | UA/ΔT approach | Cooler/Heat Exchanger citeturn5view0turn9view3 |
| Interstage KO Drums (x5) | Remove condensed water/HC | Liquid capture, level stability | None | Residence time; KS | Separators (dynamic-capable) citeturn5view0turn9view3 |
| Condensate Flash/Degassing | Stabilize condensate, vent dissolved gases | Vent rate, HC losses | Cooling/Heating (minor) | Holdup time | Separator + valve + tank |
| Anti-Surge Recycle & Discharge Pressure Control | Protect compressors, maintain header P | Surge margin, head-flow stability | None | Cv sizing basis | Valve + splitter + controller scripting citeturn9view3turn15view1 |
| Caustic Wash Tower Package | Remove CO₂/H₂S + polymer precursors | CO₂/H₂S ppm, caustic usage, ΔP | Caustic, circulation power | Stages/packing height surrogate | Absorber surrogate or Component Splitter + ΔP citeturn11view1turn12view0turn10view0 |
| Water Wash Tower Package | Remove caustic carryover | pH, Na carryover | Water + pump power | Stages/packing surrogate | Absorber surrogate + separator |
| Caustic Circulation / Blowdown | Maintain caustic strength | NaOH wt%, blowdown rate | Caustic make-up | Pump sizing | Pump + tank + recycle |
| Dryer Inlet Coalescer/Pre-separator | Protect sieve beds | Liquid carryover | None | KS; ΔP | Separator |
| Molecular Sieve Dryer Beds (2–3 beds) | Dry gas to <1 ppmv H₂O | Outlet moisture, bed ΔP, cycle time | Regen heater duty | Bed volume, ΔP 5–8 psi | Hybrid: steady adsorber surrogate + scripted switching citeturn6view4turn6view7turn9view3 |
| Regeneration Gas Compressor/Blower | Circulate regen gas | Flow stability | Electricity | Flow/head | Compressor |
| Regeneration Heater | Heat regen gas | Outlet T | Fuel gas/steam/electric | Duty/ΔT | Heater citeturn6view2 |
| Regeneration Cooler | Cool regen gas | Outlet T | Cooling water | Duty | Cooler |
| Regeneration KO Drum | Remove condensed water | Level stability | None | Holdup | Separator |
| Regen Purge to Fuel Gas (Boundary) | Dispose wet purge | Purge ratio | None | N/A | Valve + boundary |
| Warm-End Chillers | Start chilling before cold box | Outlet T, duty | Refrigeration interface | UA | Cooler |
| Refrigeration Interface Coolers | Represent propylene/ethylene refrigeration users | Tmin approach | Refrigeration interface | UA | Cooler/Heat Exchanger |
| Cold Box Multi-Stream HX Network | Deep chill & recover refrigeration | Tmin, pinch margin | Refrigeration interface | UA per section | Heat exchangers + split streams |
| Demeth Feed Prep (multi-level) | Flash/split to feed trays | Vapor fraction per branch | Refrigeration interface | Flash drum holdup | Splitter + valves + separators + (optional) expander citeturn20view2turn22view0turn9view3 |
| Demethanizer Column Package | Remove H₂/CH₄ overhead | C₂ loss to tail gas, CH₄ in bottoms, recovery | Refrigeration duty | ~65 stages; multi-feed stages | Distillation column (steady-state anchor) citeturn22view0turn9view3 |
| Deethanizer Column Package | Separate C₂ overhead from C₃+ bottoms | C₂ recovery, C₃ slip | Reboiler + condenser duties | ~25–40+ stages; ~26 bar | Distillation column (steady-state anchor) citeturn22view0turn20view1 |
| C₂H₂ Hydrogenation Feed Conditioning | Trim H₂ addition, preheat | H₂/C₂H₂ ratio, inlet T | Hydrogen | Mixer/valve Cv | Mixer + valve + heater |
| Selective Acetylene Hydrogenation Reactor | Convert acetylene selectively | C₂H₂ ppm, ethylene loss, ΔT | Cooling + hydrogen | GHSV/WHSV; conversion target | Conversion/PFR/CSTR reactor (dynamic-capable) citeturn1search14turn20view3turn9view3 |
| Reactor Effluent Cooler/Quench | Control reactor outlet | Outlet T | Cooling water/refrigeration interface | Duty | Cooler |
| C2 Splitter Column Package | Produce polymer-grade ethylene | Purity ≥99.9%, recovery, ethane slip | Refrigeration + reboiler | Up to ~125 stages; high reflux | Distillation column (steady-state anchor) citeturn22view5turn4view2turn12view0 |
| Ethylene Product Conditioning | Condense/cool PG ethylene for export | Product subcooling margin | Refrigeration interface | Duty | Cooler + separator |
| Product Pump | Transfer to storage/export | Flow, cavitation margin | Electricity | Head, NPSH margin | Pump (dynamic-capable) citeturn9view3 |
| Ethane Recycle Boundary | Return ethane to furnaces | Ethane recycle rate | None | N/A | Valve + boundary |
| Tail Gas to Fuel / H₂ Recovery Boundary | Route H₂/CH₄ | Fuel HV, H₂ purity boundary | None | N/A | Splitter + boundary |
| Ethylene Storage Tank Surrogate | Dynamic holdup + export | Inventory stability | Refrigeration (if refrigerated) | Holdup volume | Tank (dynamic-capable) citeturn9view3turn12view0 |

## Detailed unit datasheets

Unit: Quench Tower Overhead Cracked Gas Source (Boundary)

Purpose  
Define cracked-gas inlet conditions and disturbance profiles entering recovery section (composition, flow, temperature, pressure).

Connected Streams  
Inlet: N/A (battery-limit source)  
Outlet: Cracked Gas to Suction KO Drum

Critical KPIs  
Feed flow stability; acetylene load; CO₂/H₂S load; water carryover risk; hydrogen fraction (drives compression power and cold-end VLE).

Recommended Process Variables to Monitor

| Variable | Symbol / Tag Suggestion | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Pressure | PT-001 | bar(a) | 0.95–1.30 | 1.05 | Lisbon case compressor inlet ~1 bar; baseline for CGC suction citeturn22view0 |
| Temperature | TT-001 | °C | 25–45 | 35–40 | Quench typically cools toward ambient (~40°C in reference model) citeturn22view0 |
| Molar flow | FT-001 | kmol/h | (est.) 30,000–120,000 | 70,000 | Drives compressor power and column sizing (normalize to your plant) |
| H₂ mole fraction | AI-001-H2 | mol% | 20–45 | 35–37 | One published ethane-cracking cracked gas example includes ~36.9 mol% H₂ citeturn20view2 |
| CH₄ mole fraction | AI-001-CH4 | mol% | 3–15 | 5–6 | Affects demeth overhead and refrigeration loads citeturn20view2 |
| C₂H₄ mole fraction | AI-001-C2H4 | mol% | 25–45 | 34–36 | Defines ethylene capacity (example ~34.2 mol%) citeturn20view2 |
| C₂H₆ mole fraction | AI-001-C2H6 | mol% | 10–30 | 20–22 | Ethane recycle + splitter duty (example ~21.0 mol%) citeturn20view2 |
| C₂H₂ mole fraction | AI-001-C2H2 | mol% | 0.05–1.0 | 0.3–0.6 | Hydrogenation duty; example shows ~0.3 mol% citeturn20view2turn11view1 |
| CO+CO₂ | AI-001-COx | mol% | 0.05–1.0 | 0.6 | Cold-end freeze risk; example includes CO/CO₂ ~0.6 mol% citeturn20view2 |
| H₂S | AI-001-H2S | ppmv | 1–100 | 20 (est.) | Design treating for low residual acids downstream citeturn11view1 |

Control-Relevant Variables

| Controlled Variable (CV) | Manipulated Variable (MV) | Disturbance Variable (DV) | Control Objective |
|---|---|---|---|
| Feed flow to recovery | FT boundary setpoint | Furnace severity / feed | Realistic disturbance injection for ML/APC |
| Feed acetylene | N/A (DV) | Furnace severity | Stress hydrogenation section |
| Feed CO₂/H₂S | N/A (DV) | Feedstock sulfur/CO₂ | Stress caustic wash + freezer risk |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---|---|
| None | — | — | — | Boundary stream only |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| N/A | — | — | Battery-limit boundary |

Preliminary Pipe Sizing Basis

| Line Service | Recommended Velocity Range | Pressure Drop Consideration | Preliminary Sizing Basis | Notes |
|---|---:|---|---|---|
| Cracked gas suction header | (est.) 10–20 m/s | Keep ΔP low to protect CGC surge | Start with low ΔP (<0.02 bar/100 m) | Validate with acoustic/noise constraints |

DWSIM Implementation Notes  
- Object(s): **Material Stream** (source boundary).  
- Fix first: T, P, total flow, composition.  
- Free later: apply scripted disturbances (DV profiles) for synthetic data generation.  
- Convergence cautions: none (boundary).  
- Dynamic cautions: ensure downstream volumes exist so boundary disturbances create realistic transients. citeturn8view1turn9view3

---

Unit: Suction KO Drum

Purpose  
Prevent liquid slugging into the cracked gas compressor; remove free water/pygas droplets.

Connected Streams  
Inlet: Cracked Gas from quench overhead  
Outlet: Vapor to CGC Stage 1 suction; liquid to condensate handling

Critical KPIs  
Liquid carryover to CGC; drum level stability; ΔP.

Recommended Process Variables to Monitor

| Variable | Symbol / Tag Suggestion | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Inlet pressure | PT-101 | bar(a) | 0.95–1.30 | 1.05 | Defines CGC suction (Lisbon uses 1 bar inlet basis) citeturn22view0 |
| Outlet pressure | PT-102 | bar(a) | 0.93–1.25 | 1.03 | ΔP trending = fouling |
| Temperature | TT-101 | °C | 25–45 | 35–40 | Condensation sensitivity citeturn22view0 |
| Vapor fraction | VF-101 | – | 0.98–1.00 | 0.995 | Detects unexpected condensation |
| Liquid level | LT-101 | % | 10–80 | 50 | Carryover risk if high |
| Liquid outflow | FT-101L | t/h | (est.) 1–30 | 10 | Early warning for upstream upset |
| Droplet carryover indicator | AI-101-DEM | ppmv | 0–50 | <5 | Health monitoring proxy |
| Mixture Z | Z-101 | – | 0.85–1.05 | 0.95 | Compression performance indicator |
| Gas density | RHO-101 | kg/m³ | 1–10 | 5 | Needed for Souders–Brown sizing |
| Gas viscosity | MU-101 | cP | 0.008–0.02 | 0.012 | Separator + piping hydraulics |

Control-Relevant Variables

| Controlled Variable (CV) | Manipulated Variable (MV) | Disturbance Variable (DV) | Control Objective |
|---|---|---|---|
| Level (LT-101) | LV-101 (liquid outlet valve) | Feed liquid rate | Prevent CGC carryover |
| Level high-high | ESD permissive | Sudden slug | Trip protection logic |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| None | — | — | 0 | Passive vessel |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| Separator vapor sizing | Use Souders–Brown Ks method | Use Ks from API 12J ranges for vertical separators (0.055–0.107 m/s typical depending on geometry) | J. M. Campbell tip summarizes Ks approach and API 12J ranges citeturn32view0 |
| Liquid holdup | 1–5 min (est.) | 3 min | Improves dynamic realism |
| Mist eliminator | Mesh pad typical | Include as performance factor in Ks | Detailed internals not modeled; emulate by Ks |

Preliminary Pipe Sizing Basis

| Line Service | Recommended Velocity Range | Pressure Drop Consideration | Preliminary Sizing Basis | Notes |
|---|---:|---|---|---|
| Suction gas to CGC | (est.) 10–15 m/s | Minimize ΔP | Oversize early pipes | Anti-surge sensitivity |
| Condensate drain | 0.5–2.0 m/s | Avoid flashing | Limit ΔP | Two-phase risk downstream |

DWSIM Implementation Notes  
- Object(s): **Gas-Liquid Separator** (dynamic-supported). citeturn9view3  
- Fix first: outlet pressure = inlet pressure − small ΔP (e.g., 0.02 bar), initial level.  
- Free later: enable level control (PID) and use measured level to drive LV-101.  
- Convergence: stable; avoid specifying both outlet pressure and valve ΔP inconsistently.  
- Dynamic: fully feasible; add realistic holdup volume (tank/separator volume). citeturn9view3turn8view1

---

Unit: Cracked Gas Compressor Train (Stages 1–5)

Purpose  
Compress cracked gas from low pressure to high pressure required by cold section and fractionation.

Connected Streams  
Inlet: From Suction KO Drum  
Outlet: To treating/drying (mid/late stages) and to cold box feed

Critical KPIs  
Per-stage polytropic efficiency; total power; discharge temperature constraints; surge margin; discharge pressure achievement.

Recommended Process Variables to Monitor

| Variable | Symbol / Tag Suggestion | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| CGC suction pressure | PT-201S | bar(g) | 0.3–0.9 | 0.5 | Typical cracked gas low pressure range cited for CGC suction citeturn5view0 |
| Stage count | N-201 | – | 4–6 | 5 | CGC often 4–6 steps; baseline 5 stages citeturn5view0turn12view0turn22view0 |
| Final discharge pressure | PT-201D | bar(a) | 25–38 | 32 | Example flowsheet uses 1→32 bar with constant PR=2 and 5 stages citeturn22view0turn20view1 |
| Stage pressure ratio | PR-201-i | – | 1.8–2.8 | 2.0 | Lisbon uses constant PR=2 (1–2–4–8–16–32 bar) citeturn22view0 |
| Stage 5 discharge temperature | TT-201-5D | °C | 75–110 | 90 | Lisbon constraint: stage 5 outlet T ~76.85–100°C citeturn22view0 |
| Total power | MW-201 | MW | (est.) 8–40 | 20 | Key utility KPI; validate against plant |
| Polytropic efficiency | ETA-201-i | % | 70–82 | 75 | Performance monitoring; degrade for reliability cases citeturn5view0 |
| Surge recycle valve position | XV-201-AS | % | 0–100 | <10 normal | Surge margin proxy |
| Interstage liquid rate | FT-201L-i | t/h | (est.) 0–30 | 5–15 | Predicts KO drum duty |
| Discharge Z | Z-201D | – | 0.8–1.1 | 0.95 | Compression head sensitivity |

Control-Relevant Variables

| Controlled Variable (CV) | Manipulated Variable (MV) | Disturbance Variable (DV) | Control Objective |
|---|---|---|---|
| Discharge pressure | Speed/driver power or discharge PCV | Feed flow/composition | Maintain cold section header P |
| Surge margin | Anti-surge recycle valve | Suction P/T, flow | Protect compressor |
| Discharge temperature | Intercooler duty / cooling valve | CW temperature | Protect downstream / avoid fouling |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Electricity / driver | Consumed | MW | 15–25 MW (est.) | Calibrate with plant/driver curve |
| Cooling water (intercoolers) | Removed | MW | 20–40 MW duty (est.) | Depends on feed H₂ and suction T |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| Number of stages | 4–6 | 5 | Both industry guideline and reference flowsheets show 4–6 and commonly 5 citeturn5view0turn12view0turn22view0 |
| Suction pressure | 0.3–0.9 barg | 0.5 barg | Per CGC guideline citeturn5view0 |
| Discharge pressure | 25–38 bar(a) | 32 bar(a) | Reference high-pressure demeth scheme uses ~32 bar citeturn22view0turn20view1 |
| Stage PR | 1.8–2.5 typical | 2.0 | Simplifies convergence and matches example 1–2–4–8–16–32 bar citeturn22view0 |
| Anti-surge line size | 25–40% of main flow (est.) | 30% | Provide capacity for upset + startup |

Preliminary Pipe Sizing Basis

| Line Service | Recommended Velocity Range | Pressure Drop Consideration | Preliminary Sizing Basis | Notes |
|---|---:|---|---|---|
| CG suction | (est.) 10–15 m/s | Very low allowable ΔP | Oversize | Surge sensitivity |
| CG discharge | (est.) 15–25 m/s | Moderate ΔP | Keep ΔP <0.1 bar between equipment | Noise check needed |
| Anti-surge recycle | (est.) 20–30 m/s | Allow higher ΔP | Size for worst-case recycle | Provide robust Cv |

DWSIM Implementation Notes  
- Object(s): **Compressor** blocks (5), with **Cooler** blocks and **Separators** between stages. citeturn9view3turn5view0turn22view0  
- Fix first: stage outlet pressures (absolute) to 2/4/8/16/32 bar; fix polytropic efficiency (e.g., 75%); fix intercooler outlet temperatures (e.g., 35–45°C) until recycles close. citeturn22view0turn5view0  
- Free later: replace fixed outlet pressures with compressor curves (if available) and let discharge pressure controller adjust speed or discharge valve.  
- Convergence cautions: avoid starting with anti-surge recycle closed at low flow; seed recycle with small flow.  
- Dynamic cautions: compressors are dynamic-supported, but “surge” is not native—implement surge logic via **Python Script Block + Specification block** and valve position limits. citeturn9view3turn15view1turn8view1  
- ML/reliability tags: per-stage efficiency, discharge T, recycle valve %, vibration proxy (scripted), suction KO level excursions.

---

Unit: Interstage Intercoolers (E-201A…E)

Purpose  
Cool compressed cracked gas to condense water/heavies and reduce compressor power.

Connected Streams  
Inlet: CGC stage discharge gas  
Outlet: cooled gas to interstage KO drum

Critical KPIs  
Outlet temperature; approach temperature; duty; fouling (UA drop).

Recommended Process Variables to Monitor

| Variable | Symbol / Tag Suggestion | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Cooler outlet temperature | TT-2xx | °C | 30–55 | 40 | Reference model cools toward ~40°C after quench and intercooling citeturn22view0turn5view0 |
| Cooler duty | Q-2xx | MW | (est.) 2–15 each | 6 | Major energy KPI |
| CW inlet temperature | TT-CW-IN | °C | 25–35 | 30 | Seasonality impacts compressor discharge T |
| CW outlet temperature | TT-CW-OUT | °C | 30–45 | 38 | Heat balance |
| ΔP gas side | DP-2xx | bar | 0.02–0.20 | 0.05 | Fouling detection |
| UA (effective) | UA-2xx | kW/°C | (est.) 200–2000 | 800 | Fouling proxy |
| Condensed liquid rate downstream | FT-2xxL | t/h | (est.) 0–30 | 5–15 | Checks expected condensation |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Outlet temperature | CW valve / duty | CW temperature | Protect downstream and improve KO |
| ΔP high | Bypass valve | Fouling | Maintain header pressure |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Cooling water | Removed | MW | 2–15 MW per cooler (est.) | Calibrate after steady-state converges |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| Approach temperature | 5–15°C (est.) | 10°C | Use fixed outlet T for convergence |
| Gas ΔP | 0.02–0.2 bar (est.) | 0.05 bar | Set per stage; validate |

Preliminary Pipe Sizing Basis

| Line Service | Recommended Velocity Range | Pressure Drop Consideration | Preliminary Sizing Basis | Notes |
|---|---:|---|---|---|
| Interstage gas | (est.) 15–25 m/s | Moderate | Keep DP small | Avoid vibration & noise |

DWSIM Implementation Notes  
- Object(s): **Cooler** (or Heat Exchanger if assigning UA). citeturn9view3  
- Fix first: outlet temperature setpoints (one by one from stage 1 to 5) to stabilize condensation and KO loads.  
- Free later: replace fixed outlet T with UA and CW heat exchanger representation if needed for utility model.  
- Dynamic cautions: supported, but UA fouling must be scripted for reliability analytics. citeturn9view3turn15view1

---

Unit: Interstage KO Drums (V-201A…E)

Purpose  
Remove condensed liquids after each intercooler.

Connected Streams  
Inlet: Cooled interstage gas  
Outlet: vapor to next compressor stage; liquid to condensate handling

Critical KPIs  
Carryover; level control; condensate composition split (water vs hydrocarbon).

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Drum pressure | PT-2xx | bar(a) | 2–32 (stage-dependent) | per stage | Drives VLE and condensation |
| Drum temperature | TT-2xx | °C | 30–55 | 40 | Condensation sensitivity |
| Liquid level | LT-2xx | % | 10–80 | 50 | Carryover risk |
| Liquid draw | FT-2xxL | t/h | (est.) 0–30 | 5–15 | Water balance to dryer |
| Vapor fraction | VF-2xx | – | 0.95–1.00 | 0.99 | Detects excessive condensation |
| Water content in vapor | AI-2xx-H2O | ppmv | (est.) 100–10,000 | 2,000 | Dryer loading indicator |
| Hydrocarbon slip to water | AI-2xx-HC | wt% | (est.) 0.1–5 | 1 | Spent water handling |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Level | LV-2xx | Condensation rate | Maintain separation, prevent carryover |
| Level high-high | ESD permissive | Liquid slug | Compressor protection |

Utility Requirements  
None (passive), unless heated tracing for cold climates.

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| Vapor capacity | Souders–Brown Ks | Use Ks within API 12J ranges | Ks sizing method and ranges summarized by Campbell citeturn32view0 |
| Liquid holdup time | (est.) 2–10 min | 5 min | Enables dynamic realism |

Preliminary Pipe Sizing Basis

| Line Service | Recommended Velocity Range | Pressure Drop Consideration | Preliminary Sizing Basis | Notes |
|---|---:|---|---|---|
| Liquid transfer to flash | 0.5–2 m/s | Avoid flashing/cavitation | Keep ΔP low | Consider two-phase in lines |

DWSIM Implementation Notes  
- Object(s): **Gas-Liquid Separators** with level controllers. citeturn9view3  
- Fix first: outlet pressure (match upstream), set initial level, ensure liquid outlet path exists.  
- Free later: enable PID level control and realistic valve Cv.

---

Unit: Condensate Flash / Condensate Handling / Degassing

Purpose  
Stabilize KO condensate streams, remove dissolved light gases, and provide realistic vent/fuel-gas tie-ins and liquid routing for a digital twin.

Connected Streams  
Inlet: Combined interstage liquids (water-rich + hydrocarbon-rich as two drains or combined)  
Outlet: Degassed liquid to wastewater/pygas handling boundary; flash gas to fuel/flare boundary

Critical KPIs  
Flash gas rate; hydrocarbon losses; stable level control; vent composition.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Flash drum pressure | PT-301 | bar(a) | 1.2–8 | 2.0 | Sets degassing severity |
| Flash drum temperature | TT-301 | °C | 30–60 | 45 | Flash equilibrium sensitivity |
| Flash gas flow | FT-301G | kmol/h | (est.) 0.5–5% of liquid feed | 2% | Fuel system impact |
| Liquid outflow | FT-301L | t/h | (est.) 5–50 | 20 | Wastewater load |
| Level | LT-301 | % | 10–80 | 50 | Stability |
| HC in water phase | AI-301-HC | ppmw | (est.) 50–5,000 | 500 | Environmental + loss KPI |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Drum pressure | PV-301 vent valve | downstream header pressure | Stabilize venting |
| Level | LV-301 | KO liquid surges | Prevent flooding |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Cooling (optional) | Removed | MW | 0–1 (est.) | Only if needing stable flash temperature |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Holdup time | (est.) 5–15 min | 10 min | Make transients realistic |
| Vapor sizing | Souders–Brown | Use conservative Ks | Use Campbell Ks method citeturn32view0 |

Preliminary Pipe Sizing Basis

| Line Service | Velocity Range | ΔP Consideration | Basis | Notes |
|---|---:|---|---|---|
| Flash gas vent | (est.) 10–25 m/s | avoid noise | size for peak | Include choked-flow checks |
| Liquid to effluent | 0.5–2 m/s | avoid flashing | low ΔP | |

DWSIM Implementation Notes  
- Object(s): Separator + valve + tank (if providing extra surge).  
- Fix first: flash pressure and temperature (or allow PT flash) to match downstream header.  
- Dynamic: supported.

---

Unit: Anti-Surge Recycle Loops / Pressure-Control Interfaces

Purpose  
Protect the CGC against surge and emulate real compressor control behavior (critical for realistic synthetic data).

Connected Streams  
Inlet: CGC discharge (or interstage discharge)  
Outlet: return to suction or earlier stage

Critical KPIs  
Surge margin; recycle fraction; stability of discharge pressure.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Recycle valve position | XV-AS-201 | % | 0–100 | <10 normal | Surge indicator |
| Recycle flow | FT-AS-201 | kmol/h | 0–40% of main | 0–5% normal | Startup/upset realism |
| Suction flow | FT-201S | kmol/h | varies | — | Surge line reference |
| Discharge pressure | PT-201D | bar(a) | 25–38 | 32 | Cold section stability citeturn22view0 |
| Compressor speed (if modeled) | N-201 | rpm | (est.) 6,000–15,000 | 10,000 | Driver model |
| Surge margin (computed) | SM-201 | % | 0–30 | 10 | Reliability metric (scripted) |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Surge margin | Recycle valve | Suction P/T/composition | Avoid surge |
| Discharge pressure | Speed or discharge PCV | Feed flow | Maintain header pressure |
| Suction pressure | Speed | upstream pressure | Maintain stable suction |

Utility Requirements  
None directly (control-only).

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Recycle Cv | Size for 30–40% of main flow (est.) | 30% | Ensures startup feasibility |

Preliminary Pipe Sizing Basis

| Line Service | Velocity Range | ΔP Consideration | Basis | Notes |
|---|---:|---|---|---|
| Anti-surge line | (est.) 20–35 m/s | higher ΔP acceptable | size for max recycle | noise checks |

DWSIM Implementation Notes  
- Object(s): **Splitter + Valve + Mixer**, plus **Python Script Block/Specification** to compute surge margin proxy and drive MV. citeturn9view3turn9view3turn15view1  
- Fix first: keep recycle cracked slightly open (1–2%) during initialization to prevent low-flow failures.  
- Free later: close recycle and enable control logic after steady-state convergence.  
- Dynamic caution: implement valve stroke limits + rate limits to avoid numerical chatter. citeturn8view1turn9view3

---

Unit: Caustic Wash Tower (Acid Gas Removal)

Purpose  
Remove CO₂/H₂S (and in practice other acid/sulfur species), reduce downstream freezing/corrosion, and protect catalysts.

Connected Streams  
Inlet: Compressed cracked gas (mid/late compression)  
Outlet: Treated gas to water wash/dryer; spent caustic to blowdown/treatment

Critical KPIs  
CO₂ and H₂S in overhead treated gas; caustic consumption; ΔP; foaming and carryover.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Column inlet pressure | PT-401-IN | bar(a) | 6–20 | 8 (if after stage 3) | Intratec indicates caustic/water wash after 3rd stage in 5-stage compression citeturn12view0turn22view0 |
| Column ΔP | DP-401 | bar | 0.05–0.5 | 0.2 | Fouling/foaming proxy |
| Treated gas CO₂ | AI-401-CO2 | ppmv | <5 to <0.2 | 0.2 | CO₂/H₂S in caustic wash overhead typically below ~0.2 ppm (Ullmann) citeturn11view1 |
| Treated gas H₂S | AI-401-H2S | ppmv | <5 to <0.2 | 0.2 | Same as above citeturn11view1 |
| Caustic circulation rate | FT-401-CAU | m³/h | (est.) 10–300 | 120 | Removal capacity |
| Caustic strength | AI-401-NaOH | wt% | (est.) 1–15 | 5 | Controls CO₂ pickup and polymer formation tendency |
| Caustic outlet pH | pH-401 | – | 10–14 | 12.5 | Carryover control |
| Carryover (Na) in gas | AI-401-Na | ppbw | (est.) 0–200 | <50 | Downstream dryer fouling risk |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| CO₂ slip | Caustic circulation / strength | Feed CO₂ | Achieve low ppm spec citeturn11view1turn10view1 |
| Column ΔP | Antifoam (scripted) / bypass | Polymer precursors | Prevent flooding (digital twin fault) |
| pH / NaOH strength | Caustic make-up & blowdown | CO₂/H₂S load | Maintain treating capacity |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Electricity | Consumed | kW | 20–150 (est.) | circulation pumps |
| Caustic (NaOH) | Consumed | kg/h | (est.) 50–500 | depends on CO₂/H₂S |
| Cooling (optional) | Removed | MW | 0–2 (est.) | if controlling absorber temperature |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| Column model | Tray/packing surrogate | Use 8–15 “theoretical stages” surrogate | DWSIM-friendly treating representation |
| Removal target | “low ppm” | Set CO₂ and H₂S treated gas to 0.2 ppm | Ullmann gives typical below 0.2 ppm citeturn11view1 |
| Polymer precursor KO upstream | Optional | include separator before caustic tower | Patent describes KO drum and mixer upstream to reduce polymer deposition citeturn10view0 |

Preliminary Pipe Sizing Basis

| Line Service | Velocity Range | ΔP Consideration | Basis | Notes |
|---|---:|---|---|---|
| Gas to absorber | (est.) 10–20 m/s | moderate | low ΔP | avoid excessive pressure loss |
| Caustic circulation | 1–2.5 m/s | avoid erosion | keep ΔP moderate | liquid velocity guidance typically ~2.1±0.9 m/s for normal service citeturn7view0 |
| Blowdown | 0.5–2 m/s | avoid flashing | low ΔP | corrosive service |

DWSIM Implementation Notes  
- Object(s): For realism without electrolyte complexity: **Component Splitter** (remove CO₂/H₂S according to efficiency) + **Cooler (ΔT)** + **Valve (ΔP)** + **Recycle** for caustic circulation (optional).  
- Fix first: target treated-gas CO₂/H₂S specs; set column ΔP fixed.  
- Free later: introduce caustic inventory tank + concentration balance (scripted) for realistic consumption and blowdown.  
- Dynamic cautions: absorption is simplified; represent foam/flood faults using scripted ΔP increase and carryover spikes.

---

Unit: Water Wash Section

Purpose  
Remove entrained caustic and salt aerosols from treated gas to protect dryers and cold box.

Connected Streams  
Inlet: Caustic-treated gas  
Outlet: Washed gas to dryer inlet separator; spent wash water to effluent boundary

Critical KPIs  
Na carryover; pH of wash water; ΔP.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Column ΔP | DP-402 | bar | 0.02–0.3 | 0.1 | Carryover/fouling |
| Wash water rate | FT-402-W | m³/h | (est.) 5–200 | 80 | Controls Na removal |
| Outlet Na carryover | AI-402-Na | ppbw | 0–200 | <20 | Protect molecular sieve |
| Outlet pH | pH-402 | – | 7–10 | 8.5 | Residual caustic indicator |
| Gas outlet temperature | TT-402 | °C | 30–55 | 40 | Impacts dryer water load |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Na carryover | Wash water flow | Caustic carryover | Low Na to dryer |
| Column ΔP | Bypass/maintenance | Fouling | Maintain throughput |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Electricity | Consumed | kW | 10–80 (est.) | water pumps |
| Water | Consumed | m³/h | 50–150 (est.) | make-up water |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Stage count surrogate | 4–10 | 6 | Sufficient for carryover removal |

Preliminary Pipe Sizing Basis

| Line Service | Velocity Range | ΔP Consideration | Basis | Notes |
|---|---:|---|---|---|
| Wash water lines | 1–2.5 m/s | avoid erosion | standard | liquid guideline ~2.1±0.9 m/s citeturn7view0 |

DWSIM Implementation Notes  
- Object(s): Separator + “absorber surrogate” (or component split for Na carryover proxy).  
- Dynamic: feasible with tank holdup.

---

Unit: Caustic Circulation Pumps / Blowdown / Purge Handling

Purpose  
Maintain caustic strength and provide realistic consumables and effluent loads.

Connected Streams  
Inlet: Caustic tower bottoms / caustic tank  
Outlet: Circulation to caustic tower; blowdown to treatment boundary; make-up caustic from utility boundary

Critical KPIs  
Caustic strength; blowdown rate; pump reliability (availability for synthetic reliability studies).

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Pump flow | FT-403 | m³/h | (est.) 10–300 | 120 | Treating capacity |
| Pump discharge pressure | PT-403D | bar | (est.) +2 to +6 over column | +4 | Hydraulic feasibility |
| Caustic tank level | LT-403 | % | 20–80 | 50 | Inventory management |
| NaOH strength | AI-403-NaOH | wt% | (est.) 1–15 | 5 | Treating performance |
| Blowdown flow | FT-403-BD | m³/h | (est.) 0.2–5 | 1.0 | Effluent load |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| NaOH strength | Make-up and blowdown valves | CO₂ load | Maintain treating effectiveness |
| Tank level | Make-up water/caustic | blowdown | prevent pump cavitation |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Electricity | Consumed | kW | 20–150 (est.) | Pump motor |
| Caustic make-up | Consumed | kg/h | (est.) 50–500 | dependent on feed acid gases |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Pump head | 20–80 m (est.) | 50 m | Validate with piping |
| Tank holdup | 0.5–2 h circulation (est.) | 1 h | Stabilizes dynamics |

Preliminary Pipe Sizing Basis

| Line Service | Velocity Range | ΔP Consideration | Basis | Notes |
|---|---:|---|---|---|
| Caustic circulation | 1–2.5 m/s | corrosion/erosion | standard | liquid guideline ~2.1±0.9 m/s citeturn7view0 |

DWSIM Implementation Notes  
- Object(s): **Pump + Tank + Valves** (dynamic-supported). citeturn9view3  
- For reliability analytics: inject pump efficiency drift and random trips as scripted events. citeturn8view1turn15view1

---

Unit: Dryer Inlet Coalescer / Pre-Dryer Separator

Purpose  
Remove aerosols/liquid carryover to protect molecular sieve beds from liquid water and caustic mist.

Connected Streams  
Inlet: Washed treated gas  
Outlet: gas to dryer beds; liquid drain to effluent

Critical KPIs  
Carryover; dryer bed ΔP stability; moisture load to beds.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Pressure | PT-501 | bar(a) | 6–32 | 30 | Matches upstream compression levels citeturn22view0 |
| Temperature | TT-501 | °C | 30–55 | 40 | Controls equilibrium water content |
| Liquid carryover | AI-501-DEM | ppmv | 0–20 | <5 | Bed protection |
| Water in gas | AI-501-H2O | ppmv | (est.) 200–10,000 | 2,000 | Defines drying duty |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Level | LV-501 | liquid surges | prevent carryover |

Utility Requirements  
None.

Preliminary Equipment Sizing Basis  
Use KS-based sizing and 2–5 min liquid holdup (est.) for dynamic realism; size per Campbell separator Ks method. citeturn32view0

Preliminary Pipe Sizing Basis  
Same as suction KO.

DWSIM Implementation Notes  
- Object(s): Separator.  
- Dynamic: feasible.

---

Unit: Molecular Sieve Dryer Beds and Bed Switching Logic

Purpose  
Dry cracked gas to very low moisture to prevent hydrates/ice downstream; implement realistic bed cycling and regeneration.

Connected Streams  
Inlet: Treated gas from pre-dryer separator  
Outlet: Dry gas to cold box; offline bed to regeneration loop

Critical KPIs  
Outlet moisture spec; bed ΔP; cycle time; regeneration effectiveness.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Outlet moisture | AI-601-H2O | ppmv | <10 to <1 | 0.5 | MTZ reduces water content to <1 ppm; adsorption used for very low water citeturn6view7turn6view2turn20view1 |
| Target minimum moisture capability | KPI-H2O-MIN | ppmv | 0.1–1 | 0.1 | Molecular sieve effluent can reach ~0.1 ppmv in guideline table citeturn6view1 |
| Bed ΔP | DP-601 | psi | 2–8 | 6 | Design bed ΔP about 5–8 psi; >8 psi not recommended citeturn6view4 |
| Adsorption time | CT-601-ADS | h | 8–24 | 12 | Typical online duration 8–24 h citeturn6view2 |
| Breakthrough indicator | AI-601-BKT | ppmv | 0–50 | alarm at 1 | Breakthrough begins when MTZ leaves bed citeturn6view7 |
| Bed temperature profile | TT-601-TOP/MID/BOT | °C | 20–80 | 40 | Detect channeling |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Outlet moisture | Bed switch command | Feed moisture | Maintain spec |
| Bed ΔP | Bypass / maintenance | Fouling | Protect beds |
| Regen completion | Regen time/temperature | regen gas flow | Ensure capacity restored |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Regen heating | Consumed | °C | 200–315°C | Molecular sieve regen temp range ~200–315°C (400–600°F) citeturn6view1turn6view2 |
| Fuel gas / steam / electric | Consumed | MW | 3–10 MW (est.) | Calibrate from regen flow and ΔT |
| Cooling water | Removed | MW | 1–5 MW (est.) | Regen cooler |
| Electricity | Consumed | kW | 50–300 (est.) | blower + valves |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes / Assumptions |
|---|---|---|---|
| Bed count | 2 (min) | 2 online/regen | Continuous duty requires ≥2 vessels citeturn6view2 |
| Online time | 8–24 h | 12 h | From guideline citeturn6view2 |
| Bed ΔP | 5–8 psi | 6 psi | From guideline citeturn6view4 |
| Effluent water target | <1 ppm (often 0.1–1) | 0.5 ppm | From guideline and patent preference <1 ppm citeturn6view7turn20view1 |

Preliminary Pipe Sizing Basis

| Line Service | Velocity Range | Pressure Drop Consideration | Preliminary Sizing Basis | Notes |
|---|---:|---|---|---|
| Dry cracked gas | (est.) 10–20 m/s | low ΔP | size for max flow | cold box ΔP sensitivity |
| Regen gas | (est.) 10–25 m/s | allow moderate ΔP | size for heat-up flow | high temperature |

DWSIM Implementation Notes  
- Object(s): **Hybrid modeling required**. DWSIM does not natively simulate adsorption breakthrough physics in dynamic mode; implement as:  
  1) a **Component Splitter** (H₂O removal to near-zero) +  
  2) scripted “capacity” state (bed loading) +  
  3) timed switching events and gradual moisture slip near end-of-cycle. citeturn9view3turn8view1turn15view1  
- Fix first: force “perfect drying” (H₂O removal fraction = 1) to converge cold section. citeturn22view0  
- Free later: introduce time-varying removal efficiency and ΔP rise for realistic degradation.

---

Unit: Regeneration Gas Compressor/Blower

Purpose  
Provide regen circulation flow through heaters, beds, and coolers.

Connected Streams  
Inlet: Regen loop return  
Outlet: To regen heater / bed

Critical KPIs  
Regen flow; compressor power; stable operation; availability.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Regen flow | FT-701 | kmol/h | (est.) 1–10% of dry gas | 5% | Defines heater duty |
| Discharge pressure | PT-701D | bar | (est.) +0.2 to +1.0 over loop | +0.5 | Overcomes ΔP |
| Power | KW-701 | kW | (est.) 50–500 | 200 | Utility KPI |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Regen flow | Speed | bed ΔP | Maintain regen velocity |

Utility Requirements  
Electricity (blower/compressor).

Sizing Basis  
Size for regen flow and loop ΔP; treat as reliability-critical component.

Pipe sizing  
Regen gas: (est.) 10–25 m/s.

DWSIM Implementation Notes  
- Object(s): Compressor. Dynamic supported. citeturn9view3

---

Unit: Regeneration Heater

Purpose  
Heat regen gas to desorb water from molecular sieve.

Connected Streams  
Inlet: Regen gas  
Outlet: Hot regen gas to bed

Critical KPIs  
Regen temperature; duty; heater outlet stability.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Heater outlet temperature | TT-702 | °C | 200–315 | 260 | Regen temperature ranges for molecular sieve ~200–315°C citeturn6view1turn6view2 |
| Heater duty | Q-702 | MW | (est.) 1–10 | 5 | Utility consumption |
| Fuel gas flow (if modeled) | FT-FG-702 | Nm³/h | (est.) 200–4000 | 1500 | Energy KPI |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Heater outlet temperature | Fuel valve / duty | Regen flow | Achieve regen target T |

Utility Requirements  
Fuel gas / steam / electric.

Sizing basis  
Duty = ṁ·Cp·ΔT + losses; include margin 10–20%.

Pipe sizing  
Fuel gas: (est.) 10–25 m/s, validate noise; hot gas: (est.) 15–30 m/s.

DWSIM Implementation Notes  
- Object(s): Heater (dynamic supported). citeturn9view3

---

Unit: Regeneration Cooler

Purpose  
Cool wet regen gas so condensed water can be separated.

Connected Streams  
Inlet: Hot wet regen gas  
Outlet: cooled gas to regen KO drum

Critical KPIs  
Outlet temperature; water knockout rate.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Cooler outlet temperature | TT-703 | °C | 30–60 | 40 | Water condensation |
| Duty | Q-703 | MW | (est.) 1–5 | 2 | Utility KPI |
| ΔP | DP-703 | bar | 0.02–0.2 | 0.05 | Fouling |

Control-Relevant Variables  
Outlet temperature control via CW valve.

Utility Requirements  
Cooling water.

Sizing basis  
Approach 5–15°C (est.).

DWSIM Implementation Notes  
Cooler/Heat Exchanger; dynamic-supported. citeturn9view3

---

Unit: Regeneration KO Drum

Purpose  
Separate condensed water from cooled regen gas.

Connected Streams  
Inlet: cooled regen gas  
Outlet: dry regen gas recycle; liquid water drain to effluent

Critical KPIs  
Water removal; level stability; carryover.

Recommended Process Variables to Monitor  
Same pattern as KO drums: PT, TT, LT, FT-L, FT-G, carryover indicator.

Utility Requirements  
None.

Sizing basis  
Use Souders–Brown Ks method and 5–10 min holdup (est.) for dynamic realism; Ks method summarized by Campbell. citeturn32view0

DWSIM Implementation Notes  
Separator (dynamic supported). citeturn9view3

---

Unit: Wet Regeneration Gas Outlet / Purge / Fuel-Gas Tie-in

Purpose  
Dispose of purge and prevent buildup of contaminants in regen loop; provide realistic fuel system disturbance.

Connected Streams  
Inlet: purge stream from regen loop  
Outlet: fuel gas boundary / flare boundary

Critical KPIs  
Purge fraction; moisture to fuel; environmental/purge constraints.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Purge fraction | FR-704 | % | 0.5–5 | 1.5 | Stabilizes contaminants |
| Purge flow | FT-704 | kmol/h | (est.) 0–2% of dry gas | 0.5% | Fuel imbalance |
| Purge H₂O | AI-704-H2O | ppmv | 100–10,000 | 2,000 | Fuel combustion impacts |

Control-Relevant Variables  
Purge ratio control.

Utility Requirements  
None.

DWSIM Implementation Notes  
Valve + boundary stream; in dynamic, apply schedule events for purge changes. citeturn8view1

---

Unit: Warm-End Chillers and Refrigeration Interface Coolers

Purpose  
Represent chilling train upstream of cold box (without full refrigeration cycle).

Connected Streams  
Inlet: dry cracked gas  
Outlet: chilled cracked gas / partially condensed to feed prep

Critical KPIs  
Approach temperature; lowest warm-end temperature; refrigeration duty.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Chiller outlet temperature | TT-801 | °C | -10 to -60 | -35 | Patent shows partial condensate/separation around -30 to -40°C region citeturn20view2 |
| Duty | Q-801 | MW | (est.) 5–25 | 12 | Refrigeration KPI |
| Vapor fraction | VF-801 | – | 0.7–1.0 | 0.9 | Determines KO load |

Control-Relevant Variables  
Outlet temperature control by refrigeration interface duty.

Utility Requirements  
Refrigeration interface duty (ethylene/propylene cycle not modeled).

Sizing basis  
Define outlet temperature setpoints first; later replace with UA.

DWSIM Implementation Notes  
Coolers or heat exchangers (dynamic supported). citeturn9view3

---

Unit: Cold Box Multi-Stream Exchanger Network

Purpose  
Deep chill and recover cold energy; generate multiple temperature levels and split feeds for demethanizer.

Connected Streams  
Inlet: dry cracked gas; returning cold streams  
Outlet: multiple chilled/partially condensed branches; warmed tail gas/product streams

Critical KPIs  
Minimum temperature approach (pinch); temperature crossover avoidance; total cold duty.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Cold box minimum ΔT | DTmin-901 | °C | 2–10 | 5 | Lisbon model monitors minimum ΔT (2–50°C used as constraint) citeturn22view0 |
| Key temperature levels | TT-901-L1/L2/L3 | °C | -30 to -110 | -35/-55/-75/-101 | Published separator temperature levels include -30 to -40, -45 to -55, -65 to -75, and -90 to -100°C ranges citeturn20view2turn20view4turn22view2 |
| Total duty | Q-901 | MW | (est.) 10–60 | 30 | Utility KPI |
| ΔP gas | DP-901 | bar | 0.1–1.0 | 0.5 | Affects demeth pressure |

Control-Relevant Variables  
Cold box outlet temperature levels via refrigeration interface duty.

Utility Requirements  
Refrigeration interface duties (track as energy streams).

Preliminary Equipment Sizing Basis  
Use UA partitioning by temperature zone; start with fixed outlet temperature approach, then back-calculate UA.

Preliminary Pipe Sizing Basis  
Cryogenic vapor lines: (est.) 10–25 m/s; cryogenic liquid: 0.5–2 m/s.

DWSIM Implementation Notes  
- Object(s): network of **Heat Exchangers/Coolers** + splitters.  
- Fix first: set target outlet temperatures for each branch to seed column convergence.  
- Free later: convert to UA-mode and solve for duties.  
- Dynamic: heat exchangers are dynamic-supported; multi-stream cold box dynamics still best represented as multiple simpler exchangers with holdup only where meaningful. citeturn9view3turn8view1

---

Unit: Multi-Level Demethanizer Feed Preparation (split/flash/JT/expander + cold separators)

Purpose  
Create multiple feed conditions to demethanizer trays (vapor/liquid splits at different temperatures) and remove free liquids before column entry.

Connected Streams  
Inlet: chilled cracked gas branches  
Outlet: demeth feed vapor/liquid to defined stages; cold-end separator liquids to deeth feed path

Critical KPIs  
Branch vapor fractions; liquid recovery; H₂/CH₄ slip; ethylene loss risk.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Flash drum temperatures | TT-92x | °C | -30 to -100 | -40/-55/-75/-95 | Temperature levels cited above citeturn20view2turn20view4turn22view2 |
| Flash drum pressures | PT-92x | bar(a) | 26–32 | 31 | Maintain high-pressure demeth scheme citeturn22view0 |
| Vapor fraction per branch | VF-92x | – | 0.2–0.95 | 0.6 | Feed distribution |
| Liquid C₂H₄ recovery | REC-92x | % | 95–99.9 | 99 | Prevent ethylene losses |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Branch vapor fraction | JT valve / expander setting | feed composition | Stable column feed conditions |
| Separator level | LV | load changes | prevent carryover |

Utility Requirements  
Refrigeration interface (embedded in cold box).

Preliminary Equipment Sizing Basis  
Flash drums sized by Souders–Brown + holdup 2–5 min (est.), using Campbell Ks method. citeturn32view0

Preliminary Pipe Sizing Basis  
Cryogenic liquid: 0.5–1.5 m/s; cryogenic vapor: 10–25 m/s (est.).

DWSIM Implementation Notes  
- Object(s): **Separators + Valves (JT) + optional Expander**. citeturn9view3  
- Fix first: set branch outlet temperatures/pressures; set demeth feed stage locations later.  
- Dynamic: feasible for these units; use volumes to get realistic residence time.

---

Unit: Demethanizer Column Package

Purpose  
Separate methane and lighter (plus hydrogen) overhead from C₂+ bottoms with high ethylene recovery.

Connected Streams  
Inlet: multi-level feeds from cold box  
Outlet: overhead tail gas; bottoms to deethanizer

Critical KPIs  
Ethylene recovery; methane in bottoms; hydrogen/methane routing stability.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Column pressure | PT-1001 | bar(a) | 28–34 | 32 | High-pressure demeth commonly near 32 bar; methane condensed around -100°C citeturn22view0 |
| Top temperature | TT-1001-TOP | °C | -90 to -110 | -100 | Methane condensed at top around -100°C at ~32 bar citeturn22view0 |
| Bottom temperature | TT-1001-BOT | °C | -40 to -10 | -25 | Typical for C₂+ bottoms at high pressure (est.) |
| Stage count | NTRAY-1001 | – | 40–70 | 65 | Lisbon model uses 65 stages citeturn22view0 |
| Feed stages | STG-1001 | – | multiple | 15/20/25/33 | Example uses 4 feed locations (15,20,25,33) citeturn22view0 |
| Reflux ratio | RR-1001 | – | 0.5–3 | 1.5 | Impacts ethylene loss to tail gas |
| C₂H₄ in overhead | AI-1001-C2H4 | mol% | 0.01–1.0 | 0.1 | Loss KPI |
| CH₄ in bottoms | AI-1001-CH4 | mol% | 0.01–1.0 | 0.2 | Spec KPI |
| Tail gas flow | FT-1001-OVHD | kmol/h | (est.) 10–40% of feed | 25% | Fuel/H₂ recovery load |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Overhead composition | Reflux | feed composition | Minimize C₂ loss |
| Bottom methane slip | Reboil/boilup | column pressure | Maintain bottoms quality |
| Column pressure | Overhead condenser duty | refrigeration | Stable operation |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Refrigeration | Removed | MW | 10–40 (est.) | major cold duty |
| Reboiler duty | Added | MW | 5–20 (est.) | depends on integration |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Stages | 40–70 | 65 | As reference citeturn22view0 |
| Column diameter | From vapor load | start with 2–6 m (est.) | compute from DWSIM vapor rates; use conservative design margins |
| Reflux drum holdup | 5–15 min (est.) | 10 min | Needed if surrogate dynamics around column |

Preliminary Pipe Sizing Basis  
Cryogenic overhead vapor: (est.) 10–25 m/s. Bottoms liquid: 0.5–2 m/s.

DWSIM Implementation Notes  
- Object(s): **Distillation Column** (steady-state anchor). citeturn9view3turn22view0  
- Fix first: pressure, number of stages, feed stages, and provide initial T profile if needed (DWSIM column convergence improves with good initial estimates). citeturn9view4  
- Free later: optimize reflux/boilup to meet compositions.  
- Dynamic caution: since columns are not in the supported dynamic list, use a **hybrid strategy**:  
  - keep column steady-state;  
  - add dynamic holdup on reflux drum and downstream separator/tank objects. citeturn9view3turn9view1

---

Unit: Deethanizer Column Package

Purpose  
Separate C₂ overhead from C₃+ bottoms; prepare C₂ cut for acetylene hydrogenation and C₂ splitter.

Connected Streams  
Inlet: demethanizer bottoms  
Outlet: C₂ overhead to hydrogenation; bottoms to depropanizer boundary (stub) or downstream C3 train boundary

Critical KPIs  
C₂ recovery; C₃ slip to overhead; stable pressure.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Column pressure | PT-1101 | bar(a) | 20–30 | 26 | Reference indicates deethanizer about 26 bar citeturn22view0 |
| Top temperature | TT-1101-TOP | °C | -40 to -10 | -20 | Deeth condenser user at -20°C level in reference citeturn22view4 |
| Bottom temperature | TT-1101-BOT | °C | 40–90 | 70 | Typical C₃+ bottom temp (est.) |
| Stage count | NTRAY-1101 | – | 25–50 | 35 | Typical for separation (est.) |
| Overhead C₂ recovery | REC-1101-C2 | % | 98–99.9 | 99.5 | Drives total ethylene production |
| Overhead C₃ slip | AI-1101-C3 | mol% | 0.01–1.0 | 0.1 | Hydrogenation catalyst protection |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Overhead composition | Reflux | feed variability | keep C₃ slip low |
| Bottom composition | Reboiler duty | C₃+ load | meet bottoms |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Condenser duty | Removed | MW | 2–15 (est.) | refrigeration interface |
| Reboiler duty | Added | MW | 2–15 (est.) | heat integration |

Preliminary Equipment Sizing Basis  
Pressure range for deethanizer in one patent is 10–30 bar (preferably 14–24 bar) for a de-ethanizer in an olefins recovery context; your baseline at ~26 bar is consistent but must be validated to your refrigeration levels. citeturn20view1turn22view0

Preliminary Pipe Sizing Basis  
Overhead vapor: 10–25 m/s; bottoms liquid: 0.5–2 m/s.

DWSIM Implementation Notes  
Steady-state column anchor; hybrid dynamics around reflux drum if needed.

---

Unit: Optional Depropanizer Stub / Boundary (if included)

Purpose  
Represent boundary if your model stops at C₂ recovery; keep realistic C₃+ draw, pressure, and heat duties.

Connected Streams  
Inlet: Deethanizer bottoms  
Outlet: C₃ overhead boundary; C₄+ bottoms boundary

KPIs  
C₂ leak to bottoms; C₃ rate.

DWSIM Implementation Notes  
Use a separator + split fraction surrogate if not modeling full C₃ train.

---

Unit: Hydrogen Addition / Mixer / Feed Conditioning

Purpose  
Add controlled hydrogen to C₂ stream to meet acetylene conversion without excessive ethylene hydrogenation.

Connected Streams  
Inlet: Deethanizer overhead C₂ stream; hydrogen make-up  
Outlet: Reactor feed

Critical KPIs  
H₂/C₂H₂ mol ratio; inlet temperature; reactor risk of runaway.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Reactor feed pressure | PT-1201 | bar(a) | 20–30 | 26 | Matches deeth overhead pressure basis citeturn22view0 |
| Reactor feed temperature | TT-1201 | °C | 20–100 | 60 | Industry references show feed heated into ~20–100°C range in some practice descriptions (varies) citeturn1search14turn20view3 |
| H₂ addition flow | FT-1201-H2 | kmol/h | (est.) 0–5% of C₂ | set by ratio | Control variable |
| H₂/C₂H₂ | R-1201 | mol/mol | 1.0–3.0 | 2.0 | Common starting ratio; validate for selectivity (estimate) |
| C₂H₂ in feed | AI-1201-C2H2 | ppmv | 500–10,000 | 3,000 | Reactor load |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| C₂H₂ slip | H₂ flow control valve | feed C₂H₂ | Achieve ppm spec |
| Reactor inlet T | Heater duty | feed T variation | control reaction rate |

Utility Requirements  
Hydrogen supply; small heater duty.

Sizing basis  
H₂ control valve sized for max C₂H₂ upset; include 2× ratio margin.

DWSIM Implementation Notes  
Mixer + valve + heater; all dynamic-supported. citeturn9view3

---

Unit: Selective Acetylene Hydrogenation Reactor

Purpose  
Selective hydrogenation: convert acetylene to ethylene while minimizing ethylene → ethane hydrogenation.

Connected Streams  
Inlet: Hydrogenated C₂ feed  
Outlet: Reactor effluent to cooler and C₂ splitter feed system

Critical KPIs  
C₂H₂ outlet ppm; ethylene loss to ethane; reactor temperature rise (runaway risk).

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Reactor pressure | PT-1301 | bar(a) | 4.5–35.5 | 26 | Patent describes contacting at 4.5–35.5 bar citeturn1search14 |
| Reactor inlet temperature | TT-1301-IN | °C | 50–200 | 80 | Patent describes 50–200°C range citeturn1search14 |
| Reactor outlet temperature | TT-1301-OUT | °C | 60–220 | 95 | Exotherm control |
| C₂H₂ conversion | X-1301 | % | 95–99.9 | 99.5 | Meet product spec |
| C₂H₂ outlet | AI-1301-C2H2 | ppmv | 0.1–10 | 1 | Polymer-grade feed expectation |
| Ethane make | AI-1301-C2H6 | mol% | (est.) +0–1 | +0.3 | Selectivity KPI |
| GHSV | GHSV-1301 | h⁻¹ | 50–10,000 | 2,000 | Patent gives GHSV range 50–10,000 citeturn1search14 |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Reactor outlet T | Quench/cooler duty or H₂ ratio | feed C₂H₂ | avoid runaway |
| C₂H₂ slip | H₂ ratio | feed composition | keep ppm spec |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Cooling | Removed | MW | (est.) 1–10 | depends on C₂H₂ load |
| Hydrogen | Consumed | kmol/h | set by ratio | track as KPI |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Reactor model | Multi-bed with quench (industry) | Single PFR surrogate + cooler | Patents describe staged beds/quench for runaway avoidance concepts citeturn1search5turn20view3 |
| Residence time/GHSV | 50–10,000 h⁻¹ | 2,000 h⁻¹ | Use mid-range for stability citeturn1search14 |

Preliminary Pipe Sizing Basis  
Hydrogen line: (est.) 10–25 m/s; reactor feed gas: 10–20 m/s.

DWSIM Implementation Notes  
- Object(s): **Conversion Reactor** or **PFR** (both dynamic supported). citeturn9view3  
- Fix first: conversion (e.g., 99%) and small ethylene hydrogenation byproduct (ethane make) to converge.  
- Free later: implement kinetic surrogate (rate-based) in script if needed for APC work.

---

Unit: Reactor Cooling / Quench / Outlet Conditioning

Purpose  
Control reactor effluent temperature and stabilize feed to C2 splitter.

Connected Streams  
Inlet: reactor effluent  
Outlet: conditioned C2 stream to C2 splitter feed / expander

KPIs  
Outlet temperature stability; ethylene dewpoint margin; condenser duty.

DWSIM Implementation Notes  
Cooler + separator if partial condensation.

---

Unit: C2 Splitter Column Package (incl. condenser / reflux drum / vent)

Purpose  
Separate ethylene/ethane to meet polymer-grade ethylene specification and provide ethane recycle.

Connected Streams  
Inlet: hydrogenated C₂ stream  
Outlet: polymer-grade ethylene product; ethane recycle

Critical KPIs  
Ethylene purity ≥99.9%; ethylene recovery; ethane slip; reflux ratio and condenser duty.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Ethylene purity | AI-1401-C2H4 | mol% | ≥99.9 | 99.95 | Sulzer notes ethylene overhead purity ~99.9% typical; Intratec defines PG ≥99.9% min citeturn4view2turn12view0 |
| Ethylene recovery | REC-1401 | % | >99 | 99.5 | Sulzer notes recovery often >99% citeturn4view2 |
| Column top pressure | PT-1401 | bar(a) | 7–24 | 20 | Sulzer examples show low-pressure 7–12 bar, high-pressure 20–24 bar citeturn4view2 |
| Stage count | NTRAY-1401 | – | 80–125 | 100 | Sulzer notes if it has ~80 stages or more, pressure becomes key variable; another reference cites as many as 125 stages citeturn4view2turn22view5 |
| Reflux/feed ratio | RR-1401 | – | 2–6 (typical) | 4 | Sulzer provides plates vs reflux behavior; use mid value for start citeturn4view2 |
| Condenser temperature | TT-1401-CND | °C | -90 to -40 | -60 | C2 splitter overhead condenser typically in this cryogenic range citeturn22view5turn4view2 |
| Reboiler temperature | TT-1401-RB | °C | -65 to -15 | -35 | C2 splitter reboiler temperature range cited citeturn22view5 |
| Ethane in product | AI-1401-C2H6 | mol% | <0.1 | 0.05 | Key spec |

Control-Relevant Variables

| CV | MV | DV | Control Objective |
|---|---|---|---|
| Ethylene purity | Reflux | feed composition | meet ≥99.9% spec citeturn4view2turn12view0 |
| Ethane in overhead | Reflux/pressure | refrigeration | stabilize separation |

Utility Requirements

| Utility Type | Consumed / Removed | Typical Basis | Recommended Starting Estimate | Notes |
|---|---|---|---:|---|
| Refrigeration (condenser) | Removed | MW | (est.) 10–40 | largest cold consumer |
| Reboiler duty | Added | MW | (est.) 10–40 | heat pump/prop/ethy interface |

Preliminary Equipment Sizing Basis

| Sizing Parameter | Typical Range / Rule | Recommended Starting Basis | Notes |
|---|---|---|---|
| Stage count | 80–125 | 100 | Use 60 stages first for convergence; then scale to 100+ |
| Pressure selection | 7–12 (LP) or 20–24 (HP) bar | 20 bar | Align with “high pressure” mode for easier condensation citeturn4view2 |

Preliminary Pipe Sizing Basis  
Cryogenic reflux liquid: 0.5–1.5 m/s; overhead vapor: 10–25 m/s.

DWSIM Implementation Notes  
- Object(s): Distillation Column (steady-state anchor). citeturn9view3  
- Fix first (for convergence):  
  1) Reduce stage count (e.g., 40–60)  
  2) Fix pressure and reflux ratio  
  3) Use relaxed purity spec (e.g., 99.5%)  
- Free later: increase to 100+ stages and tighten spec; use good initial temperature profile estimates. citeturn9view4  
- Dynamic caution: not in supported dynamic list; represent dynamics via product reflux drum and downstream tanks (holdup). citeturn9view3turn9view5

---

Unit: Ethane Bottoms / Recycle-to-Furnace Boundary

Purpose  
Return ethane to furnaces as recycle feed; provide realistic boundary disturbance and recycle metrics.

Connected Streams  
Inlet: C2 splitter bottoms  
Outlet: Ethane recycle battery limit stream

Critical KPIs  
Ethane recycle rate; ethylene slip in ethane; pressure/temperature.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Ethane recycle flow | FT-1501 | kmol/h | (est.) 20–60% of ethylene product molar | 1.0× ethylene kmol/h | Furnace severity coupling |
| Ethylene slip in recycle | AI-1501-C2H4 | mol% | 0.3–1.5 | 0.5 | Sulzer example indicates bottoms ethylene can be ~0.3–1.4% depending on mode citeturn4view2 |
| Pressure | PT-1501 | bar(a) | 15–25 | 20 | Match splitter bottoms |
| Temperature | TT-1501 | °C | -30 to +20 | 0 | boundary conditioning |

Control-Relevant Variables  
Recycle flow is DV to furnaces; optionally maintain boundary pressure.

Utility Requirements  
None at BL.

DWSIM Implementation Notes  
Valve + boundary stream.

---

Unit: Tail Gas / H₂–CH₄ Rich Gas Routing to Fuel or H₂ Recovery Boundary

Purpose  
Route demeth overhead to fuel system or to PSA boundary; provide realistic hydrogen availability and fuel-gas balance.

Connected Streams  
Inlet: Demethanizer overhead  
Outlet: Fuel gas boundary; PSA boundary (optional split)

Critical KPIs  
H₂ purity and flow; ethylene losses; heating value.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Tail gas flow | FT-1601 | kmol/h | (est.) 10–40% feed | 25% | Fuel balance |
| H₂ mole fraction | AI-1601-H2 | mol% | 30–70 | 50 | PSA applicability |
| C₂H₄ loss | AI-1601-C2H4 | mol% | 0.01–1.0 | 0.1 | Recovery KPI |

Control-Relevant Variables  
Split ratio between fuel/PSA as MV for optimization studies.

DWSIM Implementation Notes  
Splitter + boundary streams.

---

Unit: Polymer-Grade Ethylene Condenser / Cooler

Purpose  
Condense and subcool polymer-grade ethylene for export/storage; ensure stable product quality measurement.

Connected Streams  
Inlet: Ethylene product (overhead or side draw)  
Outlet: Liquid ethylene to product drum/pump; vapor to vent/flare (if any)

Critical KPIs  
Product temperature margin; condensation completeness; vent rate.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Ethylene dewpoint/boiling reference | BP-C2H4 | °C | ~-104 at 1 bar | -103.7 | Ethylene normal boiling point is -103.7°C citeturn1search3turn1search0 |
| Condenser outlet temperature | TT-1701 | °C | -110 to -30 | -100 | For refrigerated storage, close to -104°C at ~1 bar; shipping uses ~-104°C at atm citeturn12view0turn1search3 |
| Duty | Q-1701 | MW | (est.) 1–10 | 4 | Refrigeration KPI |
| Vapor fraction outlet | VF-1701 | – | 0–0.2 | 0.02 | Product stability |

Control-Relevant Variables  
Outlet temperature control.

Utility Requirements  
Refrigeration interface duty.

DWSIM Implementation Notes  
Cooler (dynamic supported). citeturn9view3

---

Unit: Product Flash Drum (if used)

Purpose  
Separate any remaining vapor; give holdup for dynamic realism.

Connected Streams  
Inlet: condensed product  
Outlet: liquid to pump; vapor to vent recovery

Critical KPIs  
Stable level; vapor vent rate.

DWSIM Implementation Notes  
Separator.

---

Unit: Product Pump

Purpose  
Transfer liquid ethylene to storage/export.

Connected Streams  
Inlet: product drum  
Outlet: storage / export boundary

Critical KPIs  
Flow; NPSH margin; pump power.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Pump flow | FT-1801 | t/h | (est.) 50–300 | 200 | Matches plant capacity basis |
| Discharge pressure | PT-1801D | bar | (est.) 2–20 | 6 | Storage pressure boundary |
| Power | KW-1801 | kW | (est.) 100–800 | 250 | Utility KPI |
| NPSH margin (proxy) | NPSH-1801 | m | (est.) 1–5 | 2 | Cavitation risk |

Control-Relevant Variables  
Flow control to storage.

Utility Requirements  
Electricity.

DWSIM Implementation Notes  
Pump is dynamic-supported. citeturn9view3

---

Unit: Ethylene Storage Representation / Dynamic Holdup Surrogate

Purpose  
Provide inventory dynamics, export interface behavior, and realistic linepack/holdup for synthetic data.

Connected Streams  
Inlet: product pump discharge  
Outlet: export pipeline boundary, truck/ship loading boundary, boiloff vent boundary (optional)

Critical KPIs  
Inventory (mass); boiloff rate; purity retention.

Recommended Process Variables to Monitor

| Variable | Tag | Unit | Typical Range | Recommended Design Value | Why It Matters |
|---|---|---:|---:|---:|---|
| Tank level/inventory | LT-1901 | % | 10–90 | 60 | Operability |
| Tank pressure | PT-1901 | bar(a) | 1.1–20 | 1.2 (refrigerated) | Shipping case described at ~atm and -104°C; storage can be cryogenic citeturn12view0turn1search3 |
| Tank temperature | TT-1901 | °C | -110 to -30 | -104 | Refrigerated ethylene reference citeturn12view0turn1search3 |
| Boiloff rate | FT-BOG-1901 | kmol/h | (est.) 0–0.2%/h | 0.05%/h | Reliability and energy KPI |

Control-Relevant Variables  
Level control via export flow; pressure control via boiloff/condensation.

Utility Requirements  
Refrigeration (if refrigerated storage).

Preliminary Equipment Sizing Basis  
- For digital twin only: choose storage volume that gives 6–24 h inventory at design production (estimate).  
- Validate with site logistics.

DWSIM Implementation Notes  
- Object(s): **Tank** (dynamic supported). citeturn9view3  
- Use DWSIM **Monitored Variables** to export tank inventory time-series for ML. citeturn8view1

---

Unit: Optional Amine-Based Treating Surrogate (if you swap caustic to amine)

Purpose  
Alternative acid gas removal representation where caustic is not used.

DWSIM Approach  
Prefer a surrogate: component split to low ppm targets; amine regenerator is out-of-scope.

Reference target  
Low ppm acid gas levels consistent with ethylene plant needs; multi-section caustic tower patents describe removal to low single-digit ppm in treated gas. citeturn10view1turn11view1

## Stream KPI matrix

All values below are **engineering estimates** meant to seed a DWSIM model and historian tag plan. Abs/enthalpy/entropy depend on DWSIM reference state and will be exported directly using property codes. citeturn15view1turn8view1

| Stream Name | Section | Pressure | Temperature | Mass Flow | Molar Flow | Vapor Fraction | Density | Enthalpy | Entropy | Main Composition Notes | Why this stream matters operationally |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|
| Quench OH cracked gas | Feed | 1.05 bar(a) | 35–40°C | (est.) 400–900 t/h | (est.) 30k–120k kmol/h | ~1.0 | (est.) 2–8 kg/m³ | DWSIM | DWSIM | Example ethane cracking gas: ~37% H₂, ~34% C₂H₄, ~21% C₂H₆ citeturn20view2turn22view0 | Drives all downstream utilities and constraints |
| CGC stage 3 discharge | Compression | ~8 bar(a) | 80–120°C | (est.) similar | — | ~1.0 | (est.) 20–40 kg/m³ | DWSIM | DWSIM | Treating often after stage 3 in 5-stage compression citeturn12view0turn22view0 | Treating inlet operating point |
| Treated gas after caustic/water wash | Treating | (est.) 7.5–8 bar(a) | 35–45°C | — | — | ~1.0 | — | DWSIM | DWSIM | CO₂/H₂S typically <0.2 ppm after caustic wash citeturn11view1 | Freeze/corrosion protection |
| CGC final discharge to cold section | Compression | 32 bar(a) | 80–100°C | — | — | ~1.0 | (est.) 80–150 kg/m³ | DWSIM | DWSIM | Reference uses 32 bar discharge; stage 5 outlet temp constraint ~76.85–100°C citeturn22view0 | Cold box pressure anchor |
| Dry cracked gas | Drying | 31–32 bar(a) | 35–45°C | — | — | ~1.0 | — | DWSIM | DWSIM | Water <1 ppm preferred; dehydration reduces to <1 ppm; can reach 0.1 ppm citeturn6view7turn6view1turn20view1 | Hydrate/ice prevention |
| Cold-box feed branch (warm) | Cold | 31 bar(a) | -35°C | — | — | 0.8–1.0 | — | DWSIM | DWSIM | Temperature levels -30 to -40°C cited for partial condensation stage citeturn20view2 | Feed split stability |
| Cold-box feed branch (deep) | Cold | 31 bar(a) | -75°C | — | — | 0.3–0.9 | — | DWSIM | DWSIM | -65 to -75°C cited temperature level citeturn20view2turn22view2 | Demeth feed conditioning |
| Demethanizer overhead | Cryogenic | 32 bar(a) | ~-100°C | (est.) 5–20% of mass | (est.) 15–35% of molar | ~1.0 | (est.) 10–40 kg/m³ | DWSIM | DWSIM | CH₄ + H₂ rich; minimize C₂ loss citeturn22view0 | Fuel/H₂ recovery balance |
| Demethanizer bottoms | Cryogenic | 32 bar(a) | -40 to -10°C | (est.) 60–90% mass | — | liquid-rich | (est.) 450–600 kg/m³ | DWSIM | DWSIM | C₂+ enriched to deethanizer citeturn22view0 | C₂ recovery |
| Deethanizer overhead | Cryogenic | ~26 bar(a) | -20°C | (est.) 30–60% mass | — | vapor-rich | — | DWSIM | DWSIM | C₂ stream to hydrogenation and C₂ splitter citeturn22view0turn12view0 | Product quality path |
| Reactor feed | Hydrogenation | ~26 bar(a) | 60–90°C | — | — | vapor | — | DWSIM | DWSIM | Controlled H₂/C₂H₂ ratio citeturn1search14turn20view3 | Yield vs. selectivity |
| Reactor outlet | Hydrogenation | ~26 bar(a) | 80–110°C | — | — | vapor | — | DWSIM | DWSIM | C₂H₂ removal; ethane make | Affects splitter duty |
| C2 splitter overhead/product | C2 | 20 bar(a) | -60 to -100°C | ~ethylene product | ~ethylene product | vapor/liquid depending | — | DWSIM | DWSIM | PG ethylene ≥99.9% citeturn4view2turn12view0 | Final quality KPI |
| C2 splitter bottoms/ethane recycle | C2 | 20 bar(a) | -35 to +10°C | — | — | liquid | — | DWSIM | DWSIM | bottoms ethylene typically 0.3–1.4% in examples citeturn4view2 | Furnace recycle economics |
| Product ethylene to storage | Product | 1.2 bar(a) (refrig) | -104°C | (est.) 150–250 t/h | (est.) 5k–9k kmol/h | liquid | (est.) 500–650 kg/m³ | DWSIM | DWSIM | Ethylene BP -103.7°C; shipping at -104°C, ~atm described citeturn1search3turn12view0 | Inventory and export stability |

## Utility summary across the recovery section

All utilities below are first-pass estimates intended for early digital twin and synthetic data generation. Where available, ranges are anchored by published operating descriptions (e.g., 5-stage compression and cold-separation sequence). citeturn12view0turn22view0turn4view2

| Utility Category | Major Consumers | Typical Range | Recommended Starting Estimate | Notes |
|---|---|---:|---:|---|
| Electric power | CGC train, pumps, regen blower | (est.) 15–40 MW | 25 MW | Calibrate to compressor map and feed flow; CGC is critical equipment citeturn5view0turn22view0 |
| Cooling water duty | Intercoolers, regen cooler, product coolers (warm services) | (est.) 20–60 MW | 40 MW | Intercooling explicitly used between compressor steps citeturn5view0turn22view0 |
| Refrigeration interface duty | Cold box, demeth condenser, C2 splitter condenser | (est.) 20–80 MW equiv. | 45 MW | C2 splitter and cold train are major cryogenic consumers citeturn22view5turn4view2 |
| Heating duty | Deeth/C2 reboilers, regen heater | (est.) 15–60 MW | 30 MW | Strongly integrated in real plants; track with energy streams |
| Dryer regeneration | Heater duty + purge to fuel | (est.) 3–10 MW | 5 MW | Online 8–24 h; regen 200–315°C; DP constraints citeturn6view2turn6view1turn6view4 |
| Hydrogen consumption | Acetylene hydrogenation | (est.) 0.05–0.5% of cracked gas molar | 0.2% | Depends on C₂H₂ load and selectivity; patents show wide operating envelope citeturn1search14turn20view3 |
| Caustic make-up & blowdown | Caustic wash | (est.) 50–500 kg/h | 200 kg/h | Depends on CO₂/H₂S feed; treated gas typically <0.2 ppm citeturn11view1turn10view1 |

## Instrumentation and synthetic data recommendations

### Tag architecture and extraction method in DWSIM
Use DWSIM “Monitored Variables” during dynamic runs to record the same tag list at every integrator step. citeturn8view1  
For steady-state sampling (and for higher-rate synthetic historians), use DWSIM automation interfaces and property codes for stream/unit operation properties. citeturn15view2turn15view1turn15view3  

### Suggested top historian tags (80 tags) for APC/ML/reliability
Tag naming below is indicative; map to DWSIM property codes (streams: `PROP_MS_*`) where possible. citeturn15view1

| Tag Group | Example Tags (representative) | Sampling | Best Use |
|---|---|---|---|
| Feed disturbances | FT-001, PT-001, TT-001, AI-001-H2, AI-001-CH4, AI-001-C2H4, AI-001-C2H6, AI-001-C2H2, AI-001-CO2, AI-001-H2S | 1–5 s (dynamic) / per case (SS) | Fault detection; robustness training |
| CGC health | PT-201S/PT-201D, TT-201-1D…TT-201-5D, MW-201, ETA-201-1…ETA-201-5, XV-AS-201, FT-AS-201 | 1–2 s | Reliability/condition monitoring; surge avoidance APC |
| KO drums | LT-101, LT-201A…E, FT-2xxL, carryover ppm proxy, DP across demister (DP-2xx) | 2–5 s | Fault detection (flooding, carryover) |
| Treating performance | AI-401-CO2, AI-401-H2S, DP-401, FT-401-CAU, AI-403-NaOH, FT-403-BD, AI-402-Na | 5–10 s | Quality prediction; corrosion/freezing prevention |
| Drying performance | AI-601-H2O, DP-601, CT-601-ADS, TT-702, Q-702, FT-701, FT-704 | 2–10 s | Early warning of breakthrough; maintenance planning |
| Cold box integrity | DTmin-901, TT-901 key levels, DP-901, VF-92x branches | 5–10 s | Energy optimization; exchanger fouling |
| Demeth (steady-state anchor outputs) | AI-1001-C2H4 (loss), AI-1001-CH4(bottoms), RR-1001, PT-1001, TT-TOP/BOT | per SS solve / 10–30 s (hybrid) | Recovery KPI; energy optimization |
| Deeth outputs | AI-1101-C3 slip, AI-1101-C2 recovery, PT/TT | per SS / 10–30 s | Downstream catalyst protection |
| Hydrogenation | PT/TT inlet/outlet, FT-H2, ratio R-1201, conversion X-1301, C2H2 outlet ppm | 1–5 s | Runaway/fault detection; quality prediction |
| C2 splitter (steady-state anchor outputs) | Purity AI-1401-C2H4, ethane slip AI-1401-C2H6, PT-1401, RR-1401, condenser duty Q-1401C | per SS / 10–30 s | Quality control; energy APC |
| Product & storage | TT-1701, VF-1701, LT-1901, PT-1901, FT-export, FT-BOG-1901 | 2–10 s | Inventory optimization; logistics; anomaly detection |

### High-frequency (1–2 s) tags recommended
- CGC anti-surge loop: PT-201S/PT-201D, FT-201S, XV-AS-201, MW-201, TT-201-*  
- Reactor outlet temperature and H₂ ratio: TT-1301-OUT, FT-1201-H2, AI-1301-C2H2  
- KO drum high level: LT-101, LT-201*  
These align with DWSIM dynamic-mode supported equipment and schedule/monitoring framework. citeturn9view3turn8view1