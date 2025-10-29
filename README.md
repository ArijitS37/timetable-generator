# College Timetable Generator

Professional constraint-based timetable generation system using OR-Tools CP-SAT solver.

## 📁 Repository Structure
```
Timetable_Generator/
├── project/              ← Current working version (use this!)
├── older_versions/       ← Previous iterations (reference only)
└── requirements.txt      ← Python dependencies
```

## 🚀 Quick Start

### 1. Setup Virtual Environment (Recommended)
```bash
# One-time setup
python setup_venv.py

# Activate (do this every time you work)
source venv/bin/activate     # Mac/Linux
venv\Scripts\activate        # Windows
```

### 2. Configure & Generate
```bash
cd project
python main.py --configure  # First time
python main.py              # Generate timetable
```

### 3. Deactivate When Done
```bash
deactivate
```

---

## 🔄 Alternative: Manual Setup

If you prefer not to use virtual environment:
```bash
pip install -r requirements.txt
cd project
python main.py --configure
python main.py
```

## 📖 Usage
```bash
cd project

# Normal usage
python main.py              # Generate with saved settings

# Configuration
python main.py --configure  # Update settings
python main.py --show-config # View current settings

# Override semester temporarily
python main.py --semester odd
python main.py --semester even

# Help
python main.py --help
```

## 📂 Output

Generated timetables saved in `project/output/`:
- `master_timetable.xlsx` - Complete schedule (Excel)
- `teachers/` - Individual teacher PDFs
- `rooms/` - Room utilization PDFs  
- `courses/` - Course-semester PDFs

## 🔧 Configuration

Settings stored in `project/config/timetable_config.yml` (auto-generated).

Example config in `project/timetable_config.example.yml`.

## 📦 Dependencies

- Python 3.7+
- OR-Tools (constraint solver)
- pandas, openpyxl (data processing)
- PyYAML (configuration)
- reportlab (PDF generation)

See `requirements.txt` for full list.

## 🗂️ Version History

Previous iterations available in `older_versions/` for reference.
Always use `project/` for latest version.