# DWSIM Automation Skill

## What This Skill Does

Enables Claude Code to operate DWSIM process simulations programmatically via
the Python automation library in `src/`. Use this skill when you need to:

- Run thermodynamic flash calculations
- Build and solve chemical process flowsheets
- Analyze compound properties from the DWSIM database
- Debug convergence issues in existing simulations
- Generate phase diagrams and simulation reports
- Select the correct property package for a given system

## When to Activate

TRIGGER this skill automatically when the user mentions:

- "flash calculation", "PT flash", "PH flash", "bubble point", "dew point"
- "property package", "Peng-Robinson", "NRTL", "steam tables"
- "flowsheet", "unit operation", "distillation", "reactor"
- "DWSIM", "process simulation", "thermodynamic calculation"
- "vapor fraction", "phase equilibrium", "VLE", "LLE"

## Skill Execution Steps

### Step 1 — Understand the System

Ask or infer:
- What chemical species are present?
- What temperature and pressure ranges?
- Are there polar compounds, water, electrolytes, or polymers?
- Is this a new simulation or debugging an existing one?
- Is dynamic behavior required (startup/shutdown, control loops, disturbances)?
- Confirm that only open-source / non-PRO DWSIM capabilities are allowed.

### Step 2 — Select Property Package

Apply the selection table from the `dwsim-expert` agent. When uncertain,
default to Peng-Robinson and note that it may need adjustment.

### Step 3 — Write Python Code

Use the library from `src/`:

```python
from src.core.automation import DWSIMAutomation
from src.core.flowsheet import FlowsheetManager
from src.thermo.flash_calculations import FlashCalculator
from src.thermo.property_packages import PropertyPackageManager
from src.thermo.compound_properties import CompoundDatabase
from src.core.incremental import IncrementalSimulationWorkflow
```

### Step 4 — Build Incrementally (Mandatory for Big Flowsheets)

For multi-unit process plans, solve one unit operation at a time:

1. Build and converge the first unit operation with feed/product streams.
2. Build the next unit operation in isolation (or on a copy), converge it.
3. Connect it to the previous converged section **only after success**.
4. Repeat until the whole train is assembled.
5. If a step fails, stop and troubleshoot before adding more units.

After each successful build/modify step, save all three artifacts:

- Updated flowsheet snapshot (`.dwxmz`)
- Excel workbook (`.xlsx`) with stream + equipment properties
- Python automation script (`.py`) used for that step

Use `IncrementalSimulationWorkflow` when possible to automate this process.

### Step 5 — Validate Results

Before presenting results, verify:
- [ ] Mass balance closes (sum of outlet flows = inlet flows)
- [ ] Mole fractions sum to 1.0 per phase
- [ ] Temperature and pressure are physically reasonable
- [ ] Phase behavior is consistent with expected VLE

### Step 6 — Present Results

Format outputs with:
- Values with units explicitly stated (K, bar, mol/s, kJ/kg)
- Phase split clearly labeled (vapor / liquid / solid)
- Key derived quantities (bubble point, dew point, enthalpy)
- Suggestion for next steps

---

## Quick Reference Templates

### Minimal Flash Script

```python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.automation import DWSIMAutomation
from src.core.flowsheet import FlowsheetManager
from src.thermo.property_packages import PropertyPackageManager
from src.thermo.flash_calculations import FlashCalculator

compounds = ["Methane", "Ethane", "Propane"]
composition = {"Methane": 0.85, "Ethane": 0.10, "Propane": 0.05}
T_K = 250.0     # -23.15 C
P_Pa = 5e6      # 50 bar

dwsim = DWSIMAutomation()
dwsim.initialize()
fs = dwsim.create_flowsheet()
manager = FlowsheetManager(fs, dwsim)
manager.add_compounds(compounds)
manager.set_property_package("Peng-Robinson")

stream = manager.add_object("material_stream", "Feed", 100, 100)
stream.set_conditions(
    temperature_K=T_K,
    pressure_Pa=P_Pa,
    molar_flow_mol_s=1.0,
    composition=composition
)
dwsim.calculate(fs)

calc = FlashCalculator(fs)
result = calc.pt_flash(stream.dwsim_object, T_K, P_Pa)
print(f"Vapor fraction:    {result.vapor_fraction:.4f}")
print(f"Liquid phase:      {result.liquid_composition}")
print(f"Vapor phase:       {result.vapor_composition}")
```

### Find Compounds by Name

```python
from src.core.automation import DWSIMAutomation
from src.thermo.compound_properties import CompoundDatabase

dwsim = DWSIMAutomation()
dwsim.initialize()
db = CompoundDatabase()

matches = db.search("propyl")
for name in matches[:10]:
    print(name)
```

### Recommend Property Package

```python
from src.thermo.property_packages import PropertyPackageManager

manager = PropertyPackageManager()
recommended = manager.recommend_for_system(
    compounds=["Water", "Ethanol"],
    has_polar=True,
    has_water=True
)
print(f"Recommended: {recommended[0]}")
print(f"Alternatives: {recommended[1:]}")
```

---

## Error Handling Patterns

```python
import logging
logger = logging.getLogger(__name__)

try:
    result = dwsim.calculate(fs)
    if not result["success"]:
        logger.warning("Simulation did not converge: %s", result["errors"])
        # Suggest adjustments
except Exception as exc:
    logger.error("Calculation failed: %s", exc)
    raise RuntimeError(f"DWSIM calculation error: {exc}") from exc
```

---

## Environment Setup Check

Before running any simulation, verify:

```python
import os

import json

dwsim_path = os.environ.get("DWSIM_PATH")
if not dwsim_path:
    # Fall back to config.json
    try:
        with open("config.json") as f:
            dwsim_path = json.load(f).get("dwsim", {}).get("install_path", "")
    except FileNotFoundError:
        dwsim_path = ""

if not dwsim_path:
    raise EnvironmentError(
        "DWSIM_PATH not set. "
        "Set the DWSIM_PATH environment variable or update config.json "
        "with the path to your DWSIM installation."
    )
```

## Notes for Claude Code

- The `dwsim-expert` agent handles the *thinking* part (analysis, selection, strategy)
- This skill handles the *doing* part (code templates, validation steps, error patterns)
- Always import from `src/` using relative paths
- Never hardcode compound compositions from real projects as examples
- Use descriptive variable names matching chemical engineering conventions
  (T_K, P_Pa, x_mol_frac, V_m3, H_kJ_kg)
- Never rely on DWSIM PRO-only features; use only open-source features/API.
- For dynamic simulation requests, prefer standard DWSIM dynamic mode and
  explicitly avoid any PRO-exclusive functionality.
