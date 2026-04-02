# DWSIM Dynamic Simulation Skill

## What This Skill Does

Enables Claude Code to build and troubleshoot **dynamic** DWSIM simulations
using only open-source capabilities (no PRO-only features).

Use this skill when users ask for:
- Dynamic simulation setup (holdup, startup/shutdown, time trajectories)
- Controller tuning and closed-loop behavior checks
- Disturbance testing over time
- Time-step and solver stability troubleshooting
- Sequential construction of large dynamic flowsheets

## When to Activate

Trigger on terms like:
- "dynamic simulation", "transient", "startup", "shutdown"
- "PID", "controller", "disturbance", "setpoint tracking"
- "time step", "integration", "dynamic convergence"

## Mandatory Constraints

1. Never use or suggest DWSIM PRO-only features.
2. For large process plans, build one unit operation at a time.
3. Simulate each new unit operation separately first; connect only after success.
4. After every successful build/modify step, save:
   - Flowsheet snapshot (`.dwxmz`)
   - Excel workbook (`.xlsx`) with streams/equipment properties
   - Python automation script (`.py`) used for that step

## Dynamic Workflow

### Step 1 — Problem framing
- Confirm simulation goal (startup, control, disturbance response)
- Define timeline (e.g., 0–3600 s), sampling/export interval, and key KPIs
- Define manipulated variables, controlled variables, and disturbances

### Step 2 — Build steady-state base case
- Add compounds and property package
- Build minimal steady-state section and converge
- Expand unit operations sequentially with convergence checks

### Step 3 — Transition to dynamic mode
- Enable dynamic behavior and define initial conditions from converged steady state
- Configure controller blocks and key tuning values
- Use conservative initial time step

### Step 4 — Execute dynamic run in increments
- Run short horizon first
- Validate physical behavior and controller directionality
- Extend horizon only after stable results

### Step 5 — Persist artifacts every successful step
- Export `.dwxmz`, `.xlsx`, and `.py` at each successful iteration
- Keep numbered snapshots for rollback and reproducibility

## Python Pattern

```python
from src.core.incremental import IncrementalSimulationWorkflow

workflow = IncrementalSimulationWorkflow.create_new()

# ... build or modify one unit-op section here ...
result = workflow.run_step_and_persist(
    step_name="dynamic_step_01_basecase",
    output_dir="artifacts/dynamic",
    python_code=generated_python_script,
)

if not result["result"]["success"]:
    raise RuntimeError(result["result"]["errors"])
```
