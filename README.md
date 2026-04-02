<p align="center">
  <h1 align="center">DWSIM Automation</h1>
  <p align="center">
    <strong>AI-powered chemical process simulation for everyone.</strong>
  </p>
  <p align="center">
    A Python library + Claude Code agent for automating
    <a href="https://dwsim.org">DWSIM</a> simulations
    with natural language.
  </p>
  <p align="center">
    <a href="#quick-start">Quick Start</a> &middot;
    <a href="#let-ai-set-it-up-for-you">AI Setup</a> &middot;
    <a href="#claude-code-commands">Commands</a> &middot;
    <a href="#property-packages-reference">Property Packages</a> &middot;
    <a href="SETUP.md">Full Setup Guide</a>
  </p>
</p>

---

> **Disclaimer:** This is an **unofficial** community project. It is **not** affiliated with,
> endorsed by, or maintained by the DWSIM development team. This library simply wraps the
> public automation interface of [DWSIM](https://dwsim.org), which is an independent
> open-source chemical process simulator created by Daniel Medeiros.

---

## What This Is

**DWSIM Automation** bridges the gap between AI and chemical engineering. It gives you two things:

**1. Python Library (`src/`)** -- A clean, Pythonic API over DWSIM's .NET automation interface. Build flowsheets, run flash calculations, configure unit operations, access the compound database, and generate reports -- all from Python, no GUI needed.

**2. Claude Code Integration (`.claude/`)** -- A specialized AI agent (`dwsim-expert`), slash commands (`/dwsim`, `/dwsim-flash`, `/dwsim-props`), and a skill that let Claude Code act as your virtual chemical engineer. Describe what you want in plain language, and the AI writes and runs the simulation for you.

> **Tip:** You can use each part independently. Want just the AI agent without the Python library? Copy only the `.claude/` folder. Want just the Python API without AI? Use `src/` directly.

---

## Why This Exists

Process simulation software has traditionally been locked behind expensive licenses and steep learning curves. DWSIM changed that by being free and open source. This project takes it one step further: **what if you could describe a simulation in plain English and have AI build it for you?**

Whether you are a student learning thermodynamics, a researcher prototyping a process, or an engineer automating repetitive calculations -- this toolkit is for you.

---

## Quick Start

### 5-Minute Setup

```bash
# 1. Clone
git clone https://github.com/fdias78git/dwsim-claude-integration.git
cd dwsim-automation

# 2. Virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux / macOS

# 3. Install
pip install -r requirements.txt

# 4. Point to your DWSIM installation (pick one)
$env:DWSIM_PATH = "C:\Program Files\DWSIM"      # Windows PowerShell
export DWSIM_PATH=/opt/dwsim                      # Linux / macOS

# 5. Verify
python run.py --check
```

> Need help? See the [Full Setup Guide](SETUP.md) with step-by-step instructions for every platform.

### Your First Simulation

```python
from src.core.automation import DWSIMAutomation
from src.core.flowsheet import FlowsheetManager

dwsim = DWSIMAutomation()
dwsim.initialize()

fs = dwsim.create_flowsheet()
mgr = FlowsheetManager(fs, dwsim)

mgr.add_compounds(["Methane", "Ethane", "Propane"])
mgr.set_property_package("Peng-Robinson")

feed = mgr.add_object("material_stream", "Feed", 100, 100)
feed.set_conditions(
    temperature_K=250.0,
    pressure_Pa=5_000_000,
    molar_flow_mol_s=1.0,
    composition={"Methane": 0.85, "Ethane": 0.10, "Propane": 0.05}
)

result = dwsim.calculate(fs)
print(f"Converged: {result['success']}")
```

Or just run the built-in example:

```bash
python run.py --example
```

---

## Let AI Set It Up for You

If you have [Claude Code](https://github.com/anthropics/claude-code) installed, you can skip reading documentation entirely. Just open this project folder in Claude Code and type:

```
Set up this DWSIM project for me. My DWSIM is installed at C:\Program Files\DWSIM
```

Claude will:
1. Check your Python environment
2. Create your `config.json`
3. Verify the DWSIM DLLs are found
4. Run a test calculation to confirm everything works

You can also ask it to **build simulations from a description**:

```
Create a simulation of a natural gas demethanizer column.
Feed: 70% methane, 20% ethane, 10% propane at 30 bar, -30C.
I want to recover 95% of the ethane in the bottoms.
```

```
Run a PT flash for a water-ethanol mixture (50/50 mol%) at 80C and 1 atm.
Show me the vapor and liquid compositions.
```

```
What property package should I use for a CO2-methane system at high pressure?
```

The AI agent knows DWSIM's internals, property package selection rules, experiment design, convergence troubleshooting, and the entire Python API in this repository.

---

## Claude Code Commands

Once the `.claude/` folder is in place, these commands are available:

| Command | What it does |
|---------|-------------|
| `/dwsim <request>` | Natural language DWSIM request -- describe what you want |
| `/dwsim-dynamic <request>` | Dynamic/transient simulation workflow (startup, control, disturbances) |
| `/dwsim-flash PT 300 1e5 Water:0.5,Ethanol:0.5` | Run a PT flash calculation |
| `/dwsim-props Water` | Query compound properties from the database |
| `/dwsim-props search ethyl` | Search compounds by partial name |

### Install Commands Globally

To use the commands in any project (not just this one):

```bash
# Windows (PowerShell)
Copy-Item -Recurse .claude\agents\dwsim-expert.md "$env:USERPROFILE\.claude\agents\"
Copy-Item -Recurse .claude\commands\dwsim*.md "$env:USERPROFILE\.claude\commands\"
Copy-Item -Recurse .claude\skills\dwsim "$env:USERPROFILE\.claude\skills\"
```

```bash
# Linux / macOS
mkdir -p ~/.claude/agents ~/.claude/commands ~/.claude/skills/dwsim
cp .claude/agents/dwsim-expert.md ~/.claude/agents/
cp .claude/commands/dwsim*.md ~/.claude/commands/
cp -r .claude/skills/dwsim ~/.claude/skills/
```

---

## Using With Other AI Tools

The agent and commands are plain Markdown -- they work as system prompts for **any** LLM:

| AI Tool | How to use |
|---------|-----------|
| **ChatGPT / GPT-4** | Paste `dwsim-expert.md` contents as a system prompt |
| **Gemini** | Use as context in Google AI Studio system instruction |
| **Codex CLI** | Include as context in your prompt |
| **LM Studio / Ollama** | Inject via the system message |

The Python library (`src/`) is completely framework-agnostic and works with any LLM that can generate Python code.

---

## What You Can Simulate

| Category | Unit Operations |
|----------|----------------|
| **Thermodynamics** | 31+ property packages, PT/PH/PS/PV/TV/TH flash, compound database |
| **Streams** | Material streams, energy streams, composition setup |
| **Separators** | Flash vessels, component separators, filters |
| **Columns** | Rigorous distillation, absorption, shortcut (FUG) |
| **Heat Transfer** | Shell-and-tube exchangers, heaters, coolers |
| **Pressure** | Pumps, compressors, expanders, valves |
| **Reactors** | CSTR, PFR, Gibbs minimization, equilibrium |
| **Flow** | Mixers, splitters, recycle convergence blocks |
| **Reporting** | Excel export, CSV, HTML reports with Jinja2 |

---

## Property Packages Reference

| System | Recommended Package |
|--------|-------------------|
| Light hydrocarbons (C1-C6) | Peng-Robinson |
| Heavy hydrocarbons (C7+) | PR78, Lee-Kesler-Plocker |
| Alcohol-water | NRTL, UNIQUAC |
| No experimental data | UNIFAC |
| Water / steam only | IAPWS-IF97 |
| Refrigerants | CoolProp |
| Electrolytes | Extended NRTL |
| Sour gas (H2S/CO2/water) | Sour Water |

Not sure which one to pick? Just ask the AI agent -- it has a built-in decision tree.

---

## Project Structure

```
dwsim-automation/
├── .claude/                    # Claude Code integration
│   ├── agents/
│   │   └── dwsim-expert.md    # DWSIM specialist agent
│   ├── commands/
│   │   ├── dwsim.md           # Generic command
│   │   ├── dwsim-flash.md     # Flash calculations
│   │   └── dwsim-props.md     # Compound properties
│   └── skills/
│       └── dwsim/
│           └── SKILL.md       # Claude Code skill
├── src/
│   ├── core/
│   │   ├── automation.py      # Main DWSIM interface
│   │   └── flowsheet.py       # Flowsheet manager
│   ├── thermo/
│   │   ├── property_packages.py    # 31+ property packages
│   │   ├── flash_calculations.py   # PT/PH/PS/PV/TV/TH flash
│   │   └── compound_properties.py  # Compound database
│   ├── streams/
│   │   ├── material.py        # Material streams
│   │   └── energy.py          # Energy streams
│   ├── unitops/
│   │   ├── columns.py         # Distillation, absorption
│   │   ├── exchangers.py      # Heat exchangers
│   │   ├── reactors.py        # CSTR, PFR, Gibbs
│   │   ├── pumps_compressors.py
│   │   ├── separators.py
│   │   └── mixers_splitters.py
│   └── visualization/
│       ├── plotters.py        # Phase diagrams, charts
│       └── reports.py         # Report generation
├── config.example.json        # Configuration template
├── requirements.txt
├── run.py                     # CLI entry point
└── LICENSE
```

---

## Requirements

| Dependency | Version | Required |
|-----------|---------|----------|
| [DWSIM](https://dwsim.org/index.php/download/) | >= 8.0 | Yes |
| Python | >= 3.8 | Yes |
| [pythonnet](https://pypi.org/project/pythonnet/) | >= 3.0.3 | Yes |
| [Claude Code](https://github.com/anthropics/claude-code) | latest | Only for AI features |
| pandas | any | Only for Excel/CSV export |
| jinja2 | any | Only for HTML reports |

---

## Contributing

Contributions are welcome! Areas of interest:

- Additional unit operation wrappers (`src/unitops/`)
- Example scripts for specific industries (refining, gas processing, petrochemicals)
- Test coverage improvements
- Documentation and tutorials

Please open an issue before submitting large pull requests.

---

## License

MIT License. See [LICENSE](LICENSE).

---

## Author

**Felipe Dias** -- Process engineer, Python developer, and AI enthusiast from Brazil.

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Felipe_Dias-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/felipe-dias-926bb126)

---

## Acknowledgments

This project exists because of **Daniel Medeiros** and his extraordinary work on
[DWSIM](https://dwsim.org). His dedication to building and maintaining a world-class,
open-source chemical process simulator is an inspiration to engineers everywhere.
By sharing DWSIM with the world, Daniel has given students, researchers, and professionals
a powerful tool that was once accessible only through expensive commercial licenses.
As a fellow Brazilian, I am proud that our country is home to someone so committed to
advancing process engineering globally. The community owes him a great deal of gratitude.

- **[DWSIM](https://dwsim.org)** by Daniel Medeiros -- the open-source process simulator this library wraps.
- **[pythonnet](https://github.com/pythonnet/pythonnet)** -- Python-.NET interop that makes this possible.
- **[Claude Code](https://github.com/anthropics/claude-code)** by Anthropic -- the AI coding tool that powers the agent integration.
