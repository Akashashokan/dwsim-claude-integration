# /dwsim - DWSIM Process Simulation

Activates the DWSIM simulation workflow using natural language input.
Delegates analysis to the `dwsim-expert` agent and executes via the Python library.

## Usage

```
/dwsim <describe what you want to simulate or calculate>
```

## Examples

### Flash calculation
```
/dwsim flash PT at 300 K and 10 bar for a 50/50 methane-ethane mixture
```

### Property package question
```
/dwsim which property package should I use for ethanol-water distillation?
```

### Full flowsheet
```
/dwsim build a simple distillation flowsheet: feed is 100 mol/s of 40% benzene 60% toluene at 1 atm, need 95% benzene distillate
```

### Compound lookup
```
/dwsim what are the critical properties of n-decane?
```

### Troubleshooting
```
/dwsim my distillation column is not converging, reflux ratio is 3.5, 20 stages, ethanol-water feed
```

### Bubble and dew points
```
/dwsim bubble point of propane-butane 60/40 mixture at 5 bar
```

---

## What Happens

1. The `dwsim-expert` agent analyzes your request
2. Selects the appropriate property package
3. Generates Python code using the `src/` library
4. Runs or provides step-by-step instructions
5. Returns results with units and validation notes

For large flowsheets, it must build one unit operation at a time, only connect
new sections after each step converges, and export `.dwxmz`, `.xlsx`, and `.py`
artifacts after every successful modification. It must not use any PRO-only
features.

---

## Execution Template

```python
# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.core.automation import DWSIMAutomation
from src.core.flowsheet import FlowsheetManager
from src.thermo.property_packages import PropertyPackageManager

# Initialize (reads DWSIM_PATH from environment or config.json)
dwsim = DWSIMAutomation()
dwsim.initialize()
fs = dwsim.create_flowsheet()
manager = FlowsheetManager(fs, dwsim)

# Compounds and property package (filled based on user request)
manager.add_compounds([...])
manager.set_property_package(...)

# Build and run
result = dwsim.calculate(fs)
print(f"Status: {'Converged' if result['success'] else 'Did not converge'}")
if result["errors"]:
    for err in result["errors"]:
        print(f"  Error: {err}")
```

---

## Troubleshooting

If DWSIM fails to initialize:
1. Check that `DWSIM_PATH` environment variable is set, or
2. Update `install_path` in `config.json` to point to your DWSIM installation
3. Ensure pythonnet >= 3.0.3 is installed: `pip install pythonnet`
4. Run `python run.py --check` to diagnose the environment
