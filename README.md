# College Timetable Generator

Professional constraint-based timetable generation system using OR-Tools.

## 🚀 Quick Start

### First Time Users (Recommended)
```bash
# 1. Setup virtual environment
python setup_venv.py

# 2. Activate it
venv\Scripts\activate        # Windows
source venv/bin/activate     # Mac/Linux

# 3. Navigate to project
cd project

# 4. Run in interactive mode (walks you through everything)
python main.py --interactive
```

### Regular Users
```bash
cd project
python main.py  # Automatic mode with saved configuration
```

---

## 📖 Usage
```bash
cd project

# Interactive mode (step-by-step with confirmations)
python main.py --interactive
python main.py -i              # Short form

# Normal usage (automatic)
python main.py

# Configuration
python main.py --configure     # Update constraint settings
python main.py --show-config   # View current settings

# Override semester temporarily
python main.py --semester odd
python main.py --semester even

# Combinations
python main.py -i --semester odd  # Interactive with semester override

# Help
python main.py --help
```

---

## 🎯 Usage Modes Explained

| Mode | Command | Best For |
|------|---------|----------|
| **Interactive** | `python main.py --interactive` | First-time users, reviewing data before generation |
| **Automatic** | `python main.py` | Regular use once configured |
| **Configure** | `python main.py --configure` | Changing constraint settings only |
| **Show Config** | `python main.py --show-config` | Checking current configuration |

### Interactive Mode Features:
- ✅ Review/change configuration before running
- ✅ Pause after data validation summary
- ✅ Confirm before starting solver
- ✅ Full control at each step

---

## ✨ Features

- ✅ Constraint-based optimization (OR-Tools CP-SAT)
- ✅ Support for multiple subject types (DSC, DSE, GE, SEC, VAC, AEC)
- ✅ Teacher workload balancing (max 16h/week)
- ✅ Room assignment with capacity matching
- ✅ Split teaching and course merging support
- ✅ Configurable constraints (max consecutive hours, daily limits)
- ✅ Professional YAML-based configuration
- ✅ Interactive and automatic modes
- ✅ Command-line interface

---

## 📂 Output

Generated timetables are saved in `output/`:
- `master_timetable.xlsx` - Complete schedule (Excel)
- `teachers/` - Individual teacher schedules (PDF)
- `rooms/` - Room utilization schedules (PDF)
- `courses/` - Course-semester schedules (PDF)

---

## 🔧 Configuration

Settings stored in `config/timetable_config.yml` (auto-generated).

See `timetable_config.example.yml` for reference.

### Configuration Options:
- Semester type (odd/even)
- Practical consecutive slots
- Max consecutive classes
- Max daily hours (students/teachers)
- Early completion optimization

---

## 📦 Requirements

- Python 3.7+
- OR-Tools
- pandas, openpyxl
- PyYAML
- reportlab

See `requirements.txt` for full list.

---

## 🗂️ Repository Structure
```
Timetable_Generator/
├── project/              ← Current working version (use this!)
├── older_versions/       ← Previous iterations (reference only)
└── requirements.txt      ← Python dependencies
```

---

## 💡 Tips

**For first-time users:** Use `--interactive` mode to understand the workflow.

**For regular use:** Just run `python main.py` - it remembers your settings.

**To change settings:** Run `python main.py --configure` anytime.

**Testing different semesters:** Use `--semester odd` or `--semester even` without changing saved config.