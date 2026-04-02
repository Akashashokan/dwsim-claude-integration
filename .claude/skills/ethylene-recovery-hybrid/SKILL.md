---
name: ethylene-recovery-hybrid
description: Implement a hybrid dynamic ethylene recovery simulation in DWSIM by combining dynamic envelope units with quasi-steady cryogenic columns, event-driven disturbances, and automation-friendly tagging.
---

# Ethylene Recovery (Hybrid Dynamic) Skill

Use this skill when the user asks for **dynamic/transient behavior** of an ethylene cracker recovery section where rigorous cryogenic columns are retained as steady-state blocks.

## Scope

- Dynamic envelope around compression, KO drums, valves, coolers, surge/storage vessels
- Quasi-steady cryogenic core (demethanizer/deethanizer/C2 splitter)
- Event-driven disturbances and controller studies
- Automation-ready variable/tag structure for scenario generation

Use open-source DWSIM capabilities only.

## Required references

Read these files before implementation:
1. `Ethylene Cracker Engineering Data.md` (hybrid strategy + operating ranges)
2. `.claude/skills/dwsim-dynamic/SKILL.md` (dynamic workflow constraints)
3. `.claude/skills/dwsim/SKILL.md` (incremental artifact persistence rules)

## Hybrid architecture policy

1. Keep rigorous distillation columns in steady-state mode.
2. Place dynamic holdup and controls in surrounding envelope:
   - Suction/interstage KO vessels
   - Compressor recycle and pressure-control valves
   - Chiller/cooler duty disturbances
   - Product/storage vessel with pressure and level control
3. Exchange boundary conditions between dynamic envelope and steady-state core each simulation step.

## Mandatory workflow

1. Converge full steady-state base first.
2. Clone/wrap into dynamic envelope model.
3. Add one dynamic control loop at a time (validate directionality and limits).
4. Run short horizon tests before full-duration campaigns.
5. Persist artifacts after each successful modification:
   - `.dwxmz`
   - `.xlsx`
   - `.py`

## Recommended disturbance scenarios

- Feed composition step (ethylene/ethane split drift)
- Compressor efficiency degradation
- Refrigeration utility temperature increase
- Valve stiction or deadband injection
- Dryer bed switch timing offset

## KPIs to monitor

- Ethylene product purity and recovery trend
- Tail-gas methane/hydrogen slip
- Recycle flow stability and oscillation amplitude
- KO drum levels and pressure constraints
- Compressor anti-surge margin proxy

## Output contract

When responding with results:
- Separate what is dynamic vs quasi-steady.
- State the simulation horizon, sample interval, and disturbance schedule.
- Report which loops are stable, oscillatory, or saturated.
- Identify any assumptions that could invalidate control conclusions.
