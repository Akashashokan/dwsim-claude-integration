# Engineering-Grade Plan to Build an Ethylene Cracker Recovery Section Simulation in DWSIM

## Recovery section architecture and hierarchy

This plan targets a **recovery section digital-twin foundation** starting at **quench tower overhead cracked gas outlet** (treated as a boundary stream) and ending at **polymer‑grade ethylene storage**. The baseline configuration is a **front‑end, high‑pressure demethanizer train** with: multi‑stage cracked gas compression and intercooling; interstage knock‑out drums; caustic (or amine) acid gas removal located mid/late compression; molecular‑sieve dehydration; a cold box / chilling train with multiple temperature levels feeding a demethanizer; demethanizer → deethanizer → acetylene hydrogenation → C₂ splitter; ethane recycle and tail‑gas routing. This is consistent with industrial descriptions (5‑stage compression with caustic wash mid‑train; cold box feeding a demethanizer; deethanizer overhead to acetylene converter then C₂ splitter; ethane recycle) and with a detailed published ethylene cold‑end flowsheet (32 bar demethanizer, 26 bar deethanizer, 19 bar C₂ splitter; multi‑feed cold box levels). citeturn8view2turn8view1turn8view0

image_group{"layout":"carousel","aspect_ratio":"16:9","query":["ethylene plant recovery section cracked gas compressor cold box demethanizer flowsheet","C2 splitter ethylene ethane separation tower schematic","molecular sieve cracked gas dryer regeneration schematic"],"num_per_query":1}

### LNG-train-style structured hierarchy

The hierarchy below is written so you can translate it directly into a DWSIM flowsheet “block-by-block” (Level 1), “unit-by-unit” (Level 2), and “equipment objects” (Level 3).

| Level 1 Subsystem | Level 2 Sub‑Units | Level 3 Key Equipment Objects (DWSIM) |
|---|---|---|
| Cracked Gas Compression & Primary Condensate Handling | Suction separation & stage sequencing | Suction KO drum (Gas‑Liquid Separator), suction cooler if needed (Cooler/Heat Exchanger) citeturn8view2turn9search21 |
|  | Multi‑stage compression with intercooling and KO | Stage 1–5 compressors (Compressor), intercoolers (Cooler/Heat Exchanger), interstage KO drums (Gas‑Liquid Separator) citeturn8view1turn9search21turn1search11 |
|  | Interstage condensate routing | Liquid pumps (Pump), flash/separator for degassing (Gas‑Liquid Separator), boundary “condensate stripper” placeholder (optional) citeturn8view2 |
|  | Compression constraints & protection | Temperature constraints (<100 °C discharge to limit olefin polymerization/fouling), anti‑surge recycle path (Valve + Recycle) for dynamic/hybrid citeturn8view1turn12view2 |
| Acid Gas Removal | Caustic wash (baseline) | Absorber surrogate (Absorption Column or staged Mixer/Separator + Reactor), caustic circulation pumps, lean/rich caustic streams, spent caustic purge citeturn8view0turn8view2 |
|  | Water wash / caustic carryover control | Water wash column surrogate (Absorption Column or Mixer/Separator), KO drum, blowdown citeturn8view2 |
| Drying | Molecular sieve adsorption representation | Dryer “bed A/B” surrogate (Component Separator or Python Script UO removing H₂O), inlet coalescing/KO drum, outlet moisture analyzer tag points citeturn7search6turn7search8turn8view0 |
|  | Regeneration loop (simplified) | Regen gas slipstream splitter, regen heater (Heater), cooler (Cooler), regen KO drum (Gas‑Liquid Separator), wet regen offgas to fuel boundary citeturn2search21turn8view0 |
| Cold Section / Chilling Train | Warm‑end chilling prior to cold box | Coolers/Heat Exchangers with refrigeration “interfaces” as energy streams (propylene/ethylene levels modeled as fixed‑T utilities) citeturn8view1turn12view2 |
|  | Cold box multi‑stream exchanger network | Multi‑exchanger train (Heat Exchanger blocks in series/parallel) with multiple demethanizer feed temperature levels; additional “interstage coolers” between exchangers citeturn8view1turn12view2 |
|  | Cold-end KO and expander interfaces | Cold KO drum(s) (Gas‑Liquid Separator), optional expander objects (Expander) for selected streams if you emulate JT/expansion cooling structurally citeturn12view2turn2search4 |
| Cryogenic Separation Train | Demethanizer (HP) | Rigorous Distillation Column (≈65 stages; multiple feeds; 32 bar class); condenser/reboiler duties tied to refrigeration interfaces citeturn8view1 |
|  | Deethanizer | Rigorous Distillation Column (≈60 stages; ~26 bar class); overhead C₂ cut to hydrogenation; bottoms C₃⁺ to depropanizer block (optional) citeturn8view1turn8view2 |
|  | Depropanizer (optional for full olefin recovery context) | Rigorous Distillation Column; outlets to C₃ hydrogenation + C₃ splitter (can be stubbed as boundary if not needed) citeturn8view2 |
| Hydrogenation | Selective acetylene hydrogenation | Reactor (Conversion Reactor or PFR) with two parallel reactions and controlled selectivity; H₂ addition (Mixer + H₂ source) citeturn8view1turn3search2 |
| C₂ Fractionation | C₂ splitter (ethylene/ethane) | Rigorous Distillation Column (≥120 stages typical baseline), high reflux sensitivity; product draw strategy with vent/light‑ends handling citeturn8view1turn10view1turn15view0 |
| Recycle & Routing | Ethane recycle to furnaces | Ethane recycle stream to boundary sink (furnaces excluded) with optional pressure conditioning (Valve/Expander + Heater) citeturn8view2turn15view0 |
|  | Tail gas (H₂/CH₄) to fuel / H₂ recovery | Tail gas boundary sink (fuel gas) with optional split to H₂ recovery boundary; warmed through cold box exchangers citeturn8view1turn8view0 |
|  | Light-ends recycle from C₂ handling to compression | Overhead vent condenser / “lights” separator; recycle loop back to CGC suction or mid‑compression tie-in citeturn8view2turn15view0 |
| Product Handling | Polymer-grade ethylene export conditioning | Product condenser (Cooler/Heat Exchanger using refrigeration interface), product flash drum (Gas‑Liquid Separator), pump (Pump) citeturn15view0turn10view1 |
|  | Ethylene storage representation | Dynamic storage surrogate as a vessel with holdup (Gas‑Liquid Separator in dynamics mode) plus pressure control valve and level control outlet valve citeturn8view3 |

## Subsystem modeling strategy in DWSIM

DWSIM is a **sequential modular steady‑state and dynamic simulator** with CAPE‑OPEN integration and automation interfaces, which matters because **recycle closure strategy and tear stream selection** are the main determinants of whether a large olefins recovery flowsheet converges robustly. citeturn8view3turn14search1turn3search19

The table below consolidates, per subsystem, what you should implement, what you should *not* over‑model (to preserve solver stability), and the practical convergence approach.

| Subsystem | Build requirement (simulation behavior you need) | Recommended DWSIM unit ops | Key streams & phase behavior to model explicitly | Operating envelope to enforce | Recycle handling & sequencing | Convergence strategy you can actually execute in DWSIM |
|---|---|---|---|---|---|---|
| Cracked gas compression train | Reproduce 4–5 (often 5) stage compression with intercooling, KO drums, condensate removal; enforce discharge temperature limit to avoid olefin polymerization/fouling | Compressor + Cooler/Heat Exchanger + Gas‑Liquid Separator (KO) per stage | Water condensation + hydrocarbon condensation between stages; keep trace acid gases in vapor until scrubber; maintain realistic vapor/liquid splits | Suction in the ~0.3–0.9 barg range (varies); discharge typically in the ~32 bar class for HP demethanizer schemes; discharge temperature constraint around ≤100 °C is a standard physical/operability bound | Anti‑surge recycle (dynamic/hybrid) is a loop around each compressor stage; steady‑state can be modeled as “inactive” design (valve closed) | Initialize compression as **single pseudo‑compressor** to final pressure, then split into stages; add KO drums one‑by‑one; only after stable V/L splits are achieved, add acid gas removal and dryers. Stage pressure ratio ~2 across five stages is a stable initialization pattern (1–2–4–8–16–32 bar) | citeturn1search11turn9search21turn8view1turn12view2turn1search23 |
| Acid gas removal (baseline caustic) | Remove CO₂/H₂S enough to avoid freezing in cryogenic exchangers/columns and protect product quality | Absorption Column (steady‑state) **or** staged Mixer + Equilibrium/Conversion Reactor + Separator; include water wash surrogate downstream | CO₂ & H₂S dissolution/reaction into aqueous phase; aqueous phase must exist and be purged | Located mid/late compression (often after stage 3 or before last stage depending on design); caustic wash described after the third stage in common process descriptions | Treat as **separate aqueous sub‑flowsheet** with limited feedback into hydrocarbon network; avoid recycles unless you deliberately simulate caustic strength control loops | Start with **fixed removal split** (Component Separator approach) to achieve stable cold section, then upgrade to absorber+reactions. Keep the treating unit outside major recycle loops to prevent “nested recycles” early | citeturn8view2turn8view0turn7search2 |
| Drying (molecular sieve) | Achieve ultra‑dry cracked gas (sub‑ppm H₂O) before cold box; represent bed switching/regeneration as simplified but realistic | For steady‑state: Component Separator (remove H₂O to spec) + Heater/Cooler/Separator for regen loop; for hybrid/dynamics: Python Script UO + Schedule/Event Sets | Water removal to <1 ppmv is the controlling constraint; protect cold box from hydrate/ice | Dryer is placed after high pressure is reached to reduce dryer size/cost and after substantial water is condensed out in interstage coolers/KO drums | Bed cycling should be modeled as **hybrid logic** (events forcing which “bed” is online) rather than a fully rigorous adsorption PDE | Use two parallel dryer blocks (Bed A / Bed B) and a logic switch (valves + event scheduler) that routes flow through one at a time; regen loop runs on the off‑line bed with fixed heater outlet temperature and a KO drum to remove condensed water | citeturn7search6turn7search8turn8view0turn8view3 |
| Chilling train + cold box | Create correct temperature‑level structure feeding demethanizer; represent multi‑stream heat exchange and “crossover” constraints without fully building refrigeration cycles | Heat Exchanger network + Coolers with fixed outlet temperatures (utility) and Energy Streams representing refrigeration levels | Capture dewpointing/partial condensation and cold‑end KO; keep realistic enthalpy matching (don’t just set temperatures everywhere) | Representative multi‑feed demethanizer levels can be implemented (e.g., −121/−96/−71/−43 °C feeds), plus interstage coolers using propylene then ethylene refrigeration interfaces | Avoid putting cold‑box exchangers inside large recycle loops unless absolutely required; treat tail‑gas warming as a once‑through heat sink | Add cold box incrementally: first add warm‑end chillers, then a single exchanger segment, then KO, then additional exchanger segments and additional feed splits. Only then add the demethanizer column | citeturn8view1turn12view2 |
| Demethanizer | Split H₂/CH₄ “tail gas” overhead from C₂⁺ bottoms; multiple feed injections from cold box | Rigorous Distillation Column (steady‑state) | Strong sensitivity to VLE at cryogenic T; overhead vapor, bottoms liquid; reflux and condenser approach must be consistent with refrigeration interfaces | Example industrial-grade basis: ~32 bar operation with 65 stages and four feed locations in a front‑end scheme | Overhead routing is preferably non‑recycled (fuel gas boundary). If you add “tail gas warming” heat integration, keep it as feed‑forward (energy only) | Start demethanizer as **shortcut column** to estimate reflux and feed stage distribution; then switch to rigorous with fewer stages (e.g., 25–35), converge, and gradually increase toward target stage count and multi‑feed structure | citeturn8view1turn12view2turn1search14 |
| Deethanizer | Produce C₂ overhead (to acetylene hydrogenation) and C₃⁺ bottoms (to depropanizer block) | Rigorous Distillation Column | Less cryogenic than demethanizer, but still sensitive to phase behavior; overhead tends to be vapor/liquid depending on condenser spec | Example basis: 60 stages, feed at ~mid‑column, ~26 bar after expanding demethanizer bottoms from ~32 bar | No essential recycle in the C₂ path until you include C₂ splitter overhead vent recycle; keep bottoms as boundary if you exclude C₃+ recovery | Converge deethanizer with fixed reflux ratio first; then add product specs (ethylene in bottoms limit, propane in overhead limit) via Adjust/Specification after base convergence | citeturn8view1turn9search6turn8view2 |
| Acetylene hydrogenation | Convert acetylene selectively with controlled ethylene loss to ethane; represent H₂ addition and reaction exotherm simplistically | Conversion Reactor or PFR (steady‑state; dynamics feasible for PFR/CSTR) + Heater (to set reactor inlet temperature) + Mixer (H₂ addition) | Trace acetylene in a C₂‑rich stream; H₂ as limiting reagent for selectivity control | Representative basis: ~26 bar, ~340 K (≈66.9 °C), with explicit parallel reactions C₂H₂+H₂→C₂H₄ and C₂H₂+2H₂→C₂H₆ and a defined yield split | Hydrogen addition can be a controlled variable for optimization/APC; keep H₂ source as boundary to avoid adding a closed loop early | Implement as two conversion reactions with conversions tied to acetylene consumption fraction; tune selectivity by splitting acetylene conversion between the two reactions (e.g., 37% to ethylene, 63% to ethane used in a published model basis) | citeturn8view1turn3search2turn0search6 |
| C₂ splitter | Achieve polymer‑grade ethylene separation from ethane; represent light‑ends venting and product draw strategy realistically | Rigorous Distillation Column + overhead vent condenser / reflux drum surrogate (separator) | Extremely sensitive binary separation; must handle “lights” (H₂/CH₄) via vent/overhead system and not force them into ethylene product | Typical designs span low pressure (≈7–12 bar top) and high pressure (≈20–24 bar top) with large stage counts and reflux/feed ratios; polymer‑grade ethylene is commonly ~99.9% purity with >99% recovery | Ethane bottoms recycle to furnaces is a boundary sink; light‑ends vent can be recycled to compressors (optional), but add only after base convergence | Use a staged approach: (1) converge C₂ splitter without light‑ends vent recycle, (2) add vent/recycle once column stable, (3) increase stage count / refine feed stage. Use the “product side draw near top” pattern if you want realistic handling of ultra‑light components | citeturn10view1turn15view0turn8view1turn8view2 |
| Product handling & storage surrogate | Condense/export polymer‑grade ethylene and include storage holdup for dynamic studies/data generation | Cooler/Heat Exchanger + Gas‑Liquid Separator + Pump; storage is best represented as a “dynamic vessel” in dynamics mode | Two‑phase behavior during depressurization/condensation; vent handling | Storage conditions depend on plant design; you can keep it abstracted as “liquid product out” plus vapor vent to fuel gas | No recycle required; keep as termination boundary for C₂ train | For dynamics, ensure the storage surrogate has holdup + pressure control + level control loops so you can generate realistic inventory dynamics | citeturn8view3turn0search4 |

## Thermodynamics and component management

### Property package selection by section (DWSIM‑practical)

DWSIM supports common hydrocarbon EOS and several advanced models depending on installed packs (e.g., PR/SRK; PRSV2; PC‑SAFT; GERG‑2008; and bridges to additional EOS libraries). citeturn6search9turn14search12

| Section | Recommended property package | Justification for buildability + realism in this specific recovery flowsheet |
|---|---|---|
| Compression and bulk hydrocarbon handling (CGC + KO + condensate flashes) | Peng‑Robinson (PR) **or** PRSV2 | Robust cubic EOS behavior for mixed light gases and hydrocarbons; widely used in gas processing and olefins recovery simulations; PRSV2 is available in DWSIM and can improve some mixture behavior versus base PR in hydrocarbon systems (still cubic‑EOS‑robust). citeturn6search9turn5search6 |
| Cold section / cryogenic fractionation (cold box, demethanizer, deethanizer, C₂ splitter) | PRSV2 or SRK as primary; consider PC‑SAFT/Advanced EOS for sensitivity benchmarking | Cryogenic VLE is where cubic EOS errors can materially affect column duties and key splits; DWSIM can bridge to advanced EOS implementations (e.g., PC‑SAFT via the Advanced EOS Library) so you can **benchmark** PR/SRK vs an advanced model without changing flowsheet topology. citeturn6search9turn14search12 |
| Hydrogen‑rich systems (tail gas, H₂ addition to hydrogenation) | Same EOS as the cold section (avoid switching) | Keeping one EOS across the hydrocarbon network reduces “thermo discontinuities” that destabilize recycle convergence; DWSIM workflows emphasize checking interaction parameters for the chosen model where relevant. citeturn1search0turn3search19 |
| Acetylene hydrogenation reactor | Same EOS as upstream C₂ stream | Reaction selectivity/extent is what you need; thermodynamic consistency to upstream/downstream separation is more important than using a different model for the reactor alone. citeturn8view1turn3search2 |
| Acid gas removal (caustic) | Aqueous electrolyte modeling via DWSIM electrolyte packages (Extended UNIQUAC / LIQUAC / Electrolyte NRTL) when you want reactive absorption; otherwise a calibrated “removal surrogate” with the hydrocarbon EOS retained for the gas phase | DWSIM explicitly supports aqueous electrolyte equilibrium packages and an Electrolyte NRTL implementation in its thermo library, enabling electrolytic speciation/pH/ionic strength where needed. For a **simplified but realistic** olefins caustic scrubber, a surrogate approach (calibrated removals + correct phase split) is often far more stable than attempting full-rate-based reactive absorption on day one. citeturn5search3turn5search1turn8view0 |
| Acid gas removal (amine option) | If available: DWSIM Pro “Amines Property Package”; if not: treat amine as a simplified separation surrogate or use electrolyte packages with custom reactions | DWSIM Pro advertises an integrated amine package for CO₂/H₂S absorption modeling, while open-source users often rely on electrolyte packages or simplified surrogates depending on project needs. citeturn5search14turn5search32turn5search18 |

### Practical thermo limitations you should explicitly plan around

DWSIM guidance emphasizes that many models rely on fitted binary interaction parameters (BIPs); you should verify availability for your component set and EOS, especially with olefins/acetylene and lumped heavies. citeturn1search0

For a recovery section “digital twin foundation,” a **two‑tier thermo strategy** is usually the most buildable:

1. **Hydrocarbon network:** one EOS (PR or PRSV2) end‑to‑end from CGC suction through cold section and fractionation.
2. **Aqueous network:** electrolyte property package only inside the caustic/amine loop blocks, exchanging material with the hydrocarbon network as boundary streams (gas in, treated gas out, spent liquor out).

This avoids a common failure mode: nested recycles with inconsistent phase equilibrium across property packages.

## Industrial data ranges and specifications

This section gives **parameter ranges** you can use to seed the DWSIM model, and also to generate “realistic plant data” for ML/optimization once the model is stable.

### Boundary stream and internal specifications (typical ranges)

| Parameter | Typical / usable range for simulation seeding | Basis / notes |
|---|---|---|
| Quench tower overhead cracked gas temperature at recovery battery limit | ~35–45 °C for a water‑quench overhead boundary (site dependent) | A detailed ethylene model basis describes cooling to near ambient (about 40 °C) after the quench tower before compression. citeturn8view1turn12view2 |
| Cracked gas compressor stage count | 4–6 stages, commonly 5 with intercooling | Multiple references describe 4–5 (or more) stages with interstage cooling; common process descriptions use 5 stages. citeturn9search21turn1search11turn8view2 |
| CGC suction pressure | ~0.3–0.9 barg (design guideline range) | A cracked gas compressor design guideline gives ~0.3–0.9 barg suction range and 4–6 stage compression. citeturn1search11 |
| CGC discharge pressure | ~32 bar class (often chosen to enable methane condensation / HP demethanizer) | A detailed flowsheet basis uses 1→32 bar across five stages; an entity["organization","AIChE","professional society"] conference presentation notes discharge pressure high enough to condense methane and indicates five stages as inevitable for that duty. citeturn8view1turn1search23 |
| Interstage discharge temperature constraint | ≤100 °C (hard constraint for operability) | A detailed ethylene model basis explicitly enforces ≤100 °C to prevent olefin polymerization/fouling. citeturn8view1turn12view2 |
| Intercooler cooling water temperature levels (example for sizing/feasibility) | CW in ~25 °C, CW out ~40 °C (representative) | A published ethylene model basis uses CW 25→40 °C in intercoolers. citeturn8view1turn7search24 |
| Acid gas removal location | After ~3rd stage (common), or before last stage (alternate common) | One industrial process description places caustic scrub after the third stage; another detailed ethylene model basis states acid gas scrubbing usually occurs before the last compression stage. citeturn8view2turn8view0 |
| CO₂ removal rationale | Prevent freezing in low‑temperature heat exchange/fractionation; protect ethylene quality | Explicitly stated in a detailed ethylene model basis. citeturn8view0 |
| Dryer outlet water specification | <1 ppmv H₂O (sub‑ppm moisture) | Industrial analyzer application notes explicitly describe molecular sieve drying of cracked gas to <1 ppmv before cold box entry; design guidance also calls 1 ppmv a very low spec typically only molecular sieves achieve. citeturn7search6turn7search8 |
| Cold box demethanizer feed temperature “levels” | Multi‑feed levels such as −121/−96/−71/−43 °C (example baseline) | A published ethylene cold‑end model basis describes four multi‑stream exchangers and four demethanizer feed temperature levels at those values. citeturn8view1turn12view2 |
| Demethanizer operating pressure & staging | ~32 bar, ~65 stages, 4 feed locations (example basis) | Detailed ethylene model basis. citeturn8view1 |
| Demethanizer overhead temperature regime | ~160–190 K (≈ −113 to −83 °C) in low‑temperature light‑gas streams around dephlegmators | Patented cryogenic recovery schemes cite attained temperatures in the 160–190 K range for CH₄/H₂ rich streams in dephlegmator service. citeturn1search14 |
| Deethanizer pressure & staging | ~26 bar after demethanizer bottoms expansion; ~60 stages | Detailed ethylene model basis. citeturn8view1 |
| Acetylene hydrogenation basis | ~26 bar; ~340 K (≈66.9 °C); defined ethylene vs ethane yield split | Detailed model basis assumes reactor at 26 bar and 340 K, with acetylene conversion to ethylene/ethane using a 37%/63% yield split. citeturn8view1 |
| C₂ splitter staging | 120+ stages (example basis), commonly 125–150+ trays in industry; pressure depends on design philosophy | A detailed basis uses 120 stages; industry papers describe 125→153 tray revamps and multi‑product draw schemes. citeturn8view1turn15view0 |
| Polymer-grade ethylene specification (target) | ≥99.9% ethylene purity | C₂ splitter design literature states ethylene produced overhead typically has 99.9% purity; industry flowsheets describe polymer‑grade ethylene withdrawal from the C₂ splitter. citeturn10view1turn8view2turn15view0 |

### Feed composition ranges you can seed and later randomize

You need two layers of composition definition for credible data generation:

* **Dry cracked gas composition vector** (major hydrocarbons + lights).
* **Contaminants and saturations** (H₂O saturation, trace CO₂/H₂S/CO, depending on upstream and quench chemistry).

A practical “starter” dry composition vector (molar %) for a mixed‑feed style cracked gas after dehydration is explicitly tabulated in a detailed ethylene modeling work (and compared against Ullmann’s). This is immediately implementable in DWSIM as a baseline case for convergence. citeturn13view3turn8view0

| Component (example “dry cracked gas”) | Example mol% (published basis) | How to use in your model |
|---|---:|---|
| CH₄ | 22.90 | Dominant light component; strongly affects demethanizer overhead load citeturn13view3 |
| C₂H₆ | 2.87 | Impacts ethane recycle and C₂ splitter load citeturn13view3 |
| C₂H₄ | 36.28 | Main product precursor citeturn13view3 |
| C₂H₂ | 0.27 | Drives hydrogenation sizing and selectivity tuning citeturn13view3turn8view1 |
| C₃H₈ | 9.98 | Influences deethanizer bottoms and depropanizer duty if modeled citeturn13view3 |
| C₃H₆ | 14.45 | Same as above; plus impacts downstream propylene recovery if later extended citeturn13view3 |
| C₄H₈ (1‑butene used as surrogate) | 1.15 | Lump “C4 olefins” if needed for carbon balance citeturn13view3 |
| 1,3‑butadiene | 3.00 | Lump for C4 dienes in heavies balance citeturn13view3 |
| “Benzene” (often used as C₆+ lump in models) | 7.37 | Convenient surrogate for C6+ heavies remaining in gas; treat carefully in EOS citeturn13view3turn12view1 |
| H₂ | 1.75 | Affects tail gas composition and hydrogenation hydrogen balance citeturn13view3 |

For contaminants/specs:
- Add **CO₂ and H₂S traces** as separate components and set their removal in the scrubber (their freeze‑out risk is explicitly called out). citeturn8view0  
- Add **H₂O** as a component and set the quench overhead gas as **water‑saturated** at the battery limit, then remove it progressively through interstage condensation and the dryers until <1 ppmv at dryer outlet. citeturn8view0turn7search6  

## Step-by-step implementation and convergence plan

This procedure is written so you can build the flowsheet **once**, then drive it via automation for scenario generation.

### Build order (keep this order: it is optimized for convergence, not for PFD aesthetics)

**Step 1 — Create a “Hydrocarbon Core” simulation skeleton**
1. Define components: H₂, CH₄, C₂H₄, C₂H₆, C₂H₂, C₃H₆, C₃H₈, at least one C₄ surrogate (e.g., 1‑butene), optionally 1,3‑butadiene and a C₆+ surrogate (often benzene), plus CO, CO₂, H₂S, and H₂O. citeturn13view3turn8view0  
2. Select one EOS (PR or PRSV2) for the hydrocarbon network; verify interaction parameters availability where needed (especially with olefins/acetylene and lumped heavies). citeturn1search0turn6search9  

**Step 2 — Add cracked gas compression as a convergent “ladder,” but start simplified**
1. Start with *one* compressor from suction to final pressure (target ~32 bar class), then add intercooler + KO drum blocks at the outlet; confirm stable V/L split across KO. citeturn8view1turn1search23turn9search21  
2. Split into 3 compressors (e.g., 1→4→16→32 bar) with intercooling and KO at each step.  
3. Split into 5 stages (1–2–4–8–16–32 bar) once the 3‑stage version converges. citeturn8view1turn12view2  
4. Enforce discharge temperature constraints via intercooler outlet specifications so no compressor discharge exceeds ~100 °C. citeturn12view2turn8view1  

**Step 3 — Insert acid gas removal with “surrogate first, rigorous later”**
1. Add a **caustic scrubber surrogate** as a Component Separator that removes CO₂ and H₂S to a very low value; route removed “acid gas” to a boundary sink. This stabilizes the cold section build because CO₂ freeze‑out is explicitly problematic. citeturn8view0  
2. Once the cold section and columns converge, replace the surrogate by:
   - Absorption Column + electrolyte package in the caustic loop, or  
   - Mixer + Equilibrium Reactor + Separator cascade if you need simpler numerics.  
   DWSIM supports aqueous electrolyte packages for such chemistry. citeturn5search3turn5search1turn8view0  

**Step 4 — Implement drying as a controllable “spec block”**
1. Add a dryer outlet specification enforcing <1 ppmv H₂O at the dry cracked gas outlet. citeturn7search6turn7search8  
2. In steady state, represent dryers as a Component Separator removing water.  
3. Add a simplified regeneration loop (slipstream → heater → “wetting” block → cooler → KO → vent) so energy and purge flows exist with realistic tags for data generation. Regeneration design concepts and cracked gas dryer flow schemes (including use of demethanizer system gas as regen gas) are documented in industry references. citeturn2search21turn8view0  

**Step 5 — Build the chilling train and cold box incrementally**
1. Add warm‑end chillers: after drying, cool to ~30 °C with water and then to ~15 °C with a “propylene refrigeration interface” (modeled as a cooler with fixed outlet). citeturn8view1  
2. Implement cold box as a sequence of heat exchangers that progressively cool cracked gas and warm tail gas / hydrogen‑rich streams. A published basis uses four multi‑stream exchangers and explicitly notes crossover limitations requiring additional inter‑coolers between exchangers (propylene then ethylene refrigeration levels). citeturn8view1turn12view2  
3. Split the cracked gas into multiple feed branches and set their outlet temperatures to match your demethanizer feed levels (for example −43/−71/−96/−121 °C). citeturn8view1turn12view2  

**Step 6 — Add fractionation columns in this strict order: demethanizer → deethanizer → hydrogenation → C₂ splitter**
1. Demethanizer: start as shortcut, then rigorous with reduced stage count, then increase to target (example basis 65 stages, 4 feeds, 32 bar). citeturn8view1  
2. Deethanizer: add after demethanizer converges; use example basis (60 stages, ~26 bar after expansion). citeturn8view1  
3. Hydrogenation reactor: add after deethanizer overhead is stable; implement selective acetylene conversion with defined yield split and H₂ addition. citeturn8view1turn0search6  
4. C₂ splitter: add last; start with fewer stages and moderate reflux/feed, converge, then increase toward industrial stage counts. Design literature shows pressure and stage count strongly affect reflux/feed requirements; use that to choose whether your base case is “high pressure” or “low pressure” and tune accordingly. citeturn10view1turn15view0  

**Step 7 — Close recycles only after the once-through core is robust**
1. Keep ethane recycle as a boundary sink first. Add ethane recycle to furnaces only as a data tag (furnaces excluded). citeturn8view2turn15view0  
2. Keep tail gas as a boundary sink (fuel gas) first.  
3. Only then add the **light‑ends recycle loop** (C₂ splitter vent/light ends back to compression). This is one of the most destabilizing loops because it couples cryogenic separation back to warm-end compression. Process descriptions and industrial column PFDs explicitly include a light-ends vent from the C₂ splitter overhead system. citeturn8view2turn15view0  

### “Hard problems” and DWSIM-specific workarounds you should plan into the build

**PT flash nonconvergence and side draws:** Users report “maximum iterations reached PT flash” issues in distillation columns when adding complexity like side draws. The mitigation in practice is to introduce side draws only after a converged base case, and to use good initial estimates (shortcut → rigorous) and gentle pressure/temperature specifications. citeturn3search15turn3search16  

**Avoid early nested recycles:** Published DWSIM evaluations and documentation highlight large flowsheets with multiple unit operations and recycles (tear streams) as a realistic use case, but these converge reliably only if recycles are introduced after a stable acyclic core exists. citeturn3search19turn8view3  

**Thermo discontinuities:** DWSIM documentation recommends ensuring the chosen thermo model has needed interaction parameters; mixing property packages across tightly coupled recycle loops is a frequent cause of solver instability. citeturn1search0  

## Dynamic, hybrid, and automation execution

### What is feasible in native DWSIM dynamics (and what is not)

DWSIM’s own feature list explicitly distinguishes steady‑state vs dynamics-capable unit operations. In dynamics mode, DWSIM supports mixers, splitters, separators, pumps, compressors, expanders, heaters, coolers, valves, PFR/CSTR, heat exchangers, spreadsheets, and Python scripts—**but not rigorous distillation/absorption columns**. citeturn8view3turn6search2

That constraint forces a **hybrid strategy** if you want “digital twin style” dynamic behavior across an ethylene recovery section.

### Practical hybrid strategy that works for an ethylene recovery section

**Core idea:** keep the large cryogenic columns steady‑state (quasi‑steady) and simulate dynamics around them using holdups, valves, and controllers.

A workable architecture:

1. **Dynamic envelope around a steady-state fractionation core**
   - Dynamic: CGC suction drum + interstage KOs (as dynamic separators), aftercoolers (dynamic heat exchangers), surge vessels, control valves, compressor speed/anti-surge loops. citeturn8view3turn0search4  
   - Quasi‑steady: demethanizer, deethanizer, C₂ splitter (rigorous steady‑state objects). citeturn8view3  

2. **At each dynamic integration step**
   - Update boundary conditions and manipulated variables (compressor speed surrogate, valve openings, refrigeration utility temperatures/duties).
   - Recalculate the steady-state core to a new consistent point.
   - Push resulting outlet conditions back to the dynamic envelope.

This mirrors “implicit/quasi-steady column” approaches used in other environments, and is consistent with DWSIM’s capability split.

### Converting the steady-state model into a hybrid/dynamic model in DWSIM

DWSIM provides dynamic modeling infrastructure including a PID controller, event scheduler, monitored variables, configurable integrator, and cause‑and‑effect matrices. citeturn8view3

A concrete conversion workflow:

1. **Create a parallel “dynamic wrapper flowsheet”**
   - Replace key boundary material streams with dynamic boundary patterns (inlet flow specified through a valve; outlet pressure specified through a valve) as recommended in DWSIM dynamic guidance examples. citeturn4search12turn8view3  
2. **Add holdup volumes**
   - Use dynamic separators/vessels to represent suction drums, interstage KO drums, and product storage surge. (Dynamics require accumulation; instantaneous blocks won’t respond realistically.) citeturn0search4turn8view3  
3. **Add control structure**
   - Anti-surge: compressor discharge → recycle valve to suction; controlled by flow/ΔP or approach-to-surge surrogate.
   - Interstage KO level control: liquid outlet valve manipulates level; vapor outlet valve or backpressure valve manipulates pressure.
   - Dryer switching: event-driven valve routing Bed A vs Bed B using schedule/events. citeturn8view3turn4search12  
4. **Use event sets and schedules for “faults” and operating campaigns**
   - Step changes in feed composition, refrigeration utility temperature shifts, compressor efficiency degradations, valve stiction events. DWSIM documents “Event Sets” and “Cause-and-Effect Matrices” as first-class dynamic tools. citeturn4search12turn8view3  

### Automation approach for ML/reliability/optimization workloads

DWSIM exposes its main classes/interfaces for automation via COM/.NET (documented since v4.2), enabling programmatic creation, manipulation, and calculation of flowsheets. citeturn0search1turn14search7

For engineering-grade data generation, treat DWSIM as a **simulation kernel**:

1. **Scenario generator (Python/C#):**
   - Generates randomized but physically constrained inputs (feed vector, CGC suction pressure, refrigeration utility temperatures, catalyst selectivity parameter, etc.).
2. **DWSIM automation executor:**
   - Loads a baseline flowsheet.
   - Writes the scenario inputs to stream/unit properties.
   - Runs a calculation.
   - Extracts outputs and logs them (CSV/Parquet).
   DWSIM’s automation API documents a `CalculateFlowsheet` method for executing a flowsheet solve. citeturn14search15turn14search6  
3. **Tag map for sensor realism:**
   - Use DWSIM object property codes (e.g., material stream temperature/pressure/flow indices) for standardized read/write access when building a “plant tag dictionary” for ML pipelines. citeturn4search6  

If you want your digital twin to interface with external control stacks, DWSIM supports CAPE‑OPEN for both property packages and unit operations (so you can plug in external column proxy models or advanced thermodynamics), and it has an OPC UA client plugin for mapping monitored variables from an OPC UA server into flowsheet properties. citeturn14search1turn14search2

A practical integration pattern for APC/optimization experiments:
- External controller writes manipulated variables to an OPC UA server.
- DWSIM reads them via the OPC UA client plugin mapping.
- DWSIM calculates and exports measured variables via automation/logging.
The OPC UA plugin is documented as a client mapping tool; historical discussion indicates it was designed primarily to read from the OPC server into DWSIM (not necessarily write back). citeturn14search2turn14search14  

## Validation and digital-twin expansion plan

### Steady-state validation checks (acceptance tests before any ML data generation)

You should treat validation as “automated unit tests” for the flowsheet:

1. **Total mass balance closure**
   - Over the full battery limit: (quench overhead in) – (tail gas + ethane recycle + ethylene product + C₃⁺ out + spent caustic + condensed water out) should close within a tight tolerance.
   - On each major block: CGC, scrubber, dryers, cold box, each column.  
   This is essential because DWSIM large flowsheets with recycles/tear streams are intended but will mask errors if you don’t enforce systematic closure checks. citeturn3search19  

2. **Spec validation**
   - **Dryness:** verify dryer outlet <1 ppmv H₂O in the dry cracked gas line to cold box. citeturn7search6turn7search8  
   - **Acid gas:** verify CO₂ low enough to avoid freezing risk; the explicit freeze‑out rationale is documented. citeturn8view0  
   - **Polymer‑grade ethylene:** verify ethylene purity ≥99.9% at the product node (either overhead product after vent removal or near‑top side draw strategy). citeturn10view1turn15view0turn8view2  

3. **Recovery metrics**
   - Ethylene recovery relative to ethylene in the deethanizer overhead feed to the C₂ splitter should be in the “high‑99% class” for a healthy recovery section; C₂ splitter design literature explicitly notes >99% and up to ~99.9% recovery for typical configurations. citeturn10view1  

4. **Energy and trend sanity**
   - Increasing C₂ splitter reflux/feed should increase condenser and reboiler loads and typically improve separation; published C₂ splitter design discusses plates vs reflux/feed tradeoffs and the sensitivity of capacity and reflux to column pressure. citeturn10view1  

### Sensitivity and robustness tests that matter for an ethylene recovery digital twin

Run these as automated “stress tests” after base convergence:

- **Feed composition perturbations:** vary CH₄/H₂ and C₂H₄/C₂H₆ fractions across realistic ranges (use the published dry cracked gas vector as a baseline and perturb ±10–30% relative while renormalizing). citeturn13view3  
- **Suction pressure and compression ratio disturbances:** vary CGC suction in the cited range and watch dewpointing and KO drum liquid rates. citeturn1search11  
- **Refrigeration interface degradation:** impose +2 to +10 °C shifts in “effective” refrigerant utility temperatures and verify the cold box still meets demethanizer feed targets (or quantify how targets slip). This aligns with the multi‑level refrigeration interface concept used in published ethylene cold‑end models. citeturn12view2turn8view1  
- **Hydrogenation selectivity shifts:** perturb acetylene conversion split and H₂ feed ratio; quantify downstream ethane make and ethylene loss. citeturn8view1turn0search6  

DWSIM includes built‑in sensitivity analysis and constrained optimization tooling, which you can use either interactively or via automation to formalize these studies. citeturn8view3turn2search17  

### Turning the model into a synthetic time-series + ML + optimization platform

Once steady-state and hybrid dynamics are stable, extend in three layers.

**Layer A — Synthetic historian generation**
- Define a tag list (flows, pressures, temperatures, compositions, duties, levels, valve positions).
- Add sensor noise and lag: implement as Python Script UO filters (first‑order + white noise) at the tag extraction level so the underlying physics remains clean but measured values mimic plant instruments. DWSIM’s Python scripting and dynamic event infrastructure supports such custom logic. citeturn8view3turn6search6turn6search8  

**Layer B — Reliability/fault studies**
- Use dynamic “Event Sets” and “Cause‑and‑Effect Matrices” to emulate trips and interlocks at the flowsheet level (e.g., compressor trip → anti‑surge fully open → suction pressure collapses; dryer breakthrough alarm → switch beds; refrigeration warm‑up event). DWSIM documents these constructs explicitly. citeturn4search12turn8view3  
- Fault parameterization examples:
  - Compressor polytropic efficiency degradation curve (fouling proxy).
  - Heat exchanger UA degradation.
  - Control valve stiction / saturation.  
  Dynamic control realism requires holdup and valves; community discussion explicitly notes PIDs won’t behave realistically without flow control elements and accumulation volumes. citeturn0search4turn8view3  

**Layer C — Optimization/APC-grade experimentation**
- Implement an “APC sandbox” around the steady-state core:
  - Manipulated variables: CGC discharge pressure (via speed proxy), caustic circulation/strength proxy, refrigeration interface temperatures, demethanizer reflux, deethanizer reflux, hydrogenation H₂ rate, C₂ splitter reflux/feed ratio and pressure.
  - Controlled variables: dryer outlet moisture, demethanizer overhead methane purity proxy, deethanizer bottoms C₂ slip proxy, ethylene product purity, ethylene recovery proxy, total refrigeration duty proxy.  
- Execute multivariate constrained optimization either using DWSIM’s built-in optimizer or via external optimizers driving DWSIM through automation. DWSIM documents constrained optimization/sensitivity utilities and automation interfaces for running studies externally. citeturn8view3turn0search1turn14search15  

Finally, if you need to push beyond DWSIM-native limitations (notably, dynamic distillation), plan a **CAPE‑OPEN or custom‑plugin column surrogate** (reduced-order dynamic column models) to replace the quasi‑steady column core while keeping your flowsheet connectivity intact; DWSIM supports CAPE‑OPEN unit operations and property packages, explicitly enabling this extension path. citeturn14search1turn3search19