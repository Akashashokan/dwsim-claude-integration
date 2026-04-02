# /dwsim-dynamic - Dynamic DWSIM Simulation

Activates dynamic/transient simulation workflow for DWSIM using the
`dwsim-dynamic-expert` agent.

## Usage

```text
/dwsim-dynamic <dynamic simulation request>
```

## Examples

```text
/dwsim-dynamic build startup simulation for a flash drum with level and pressure control
```

```text
/dwsim-dynamic test a +10% feed flow disturbance and show 0-1800 s response
```

## Required Behavior

1. Build flowsheets one unit operation at a time for large plans.
2. Simulate each added unit operation separately and connect only after success.
3. Save `.dwxmz`, `.xlsx`, and `.py` outputs after every successful modification.
4. Never use PRO-only features.
