"""
Timetable Generator - Main Entry Point (WITH FEASIBILITY CHECK)
"""
from src.data_loader import DataLoader
from src.constraint_selector import ConstraintSelector
from src.constraint_builder import ConstraintBuilder
from src.solver_engine import SolverEngine
from src.pdf_generator import PDFGenerator
from src.excel_generator import ExcelGenerator
from src.feasibility_checker import FeasibilityChecker
from src.config import Config
import os

def print_banner():
    """Print welcome banner"""
    print("\n" + "=" * 70)
    print(" " * 15 + "🎓 COLLEGE TIMETABLE GENERATOR 🎓")
    print(" " * 20 + "Advanced Constraint-Based System")
    print("=" * 70)
    print()

def main():
    """Main function to run the timetable generator"""
     
    print_banner()
    
    # Step 1: Load and validate input data
    print("📋 STEP 1: DATA LOADING AND VALIDATION")
    print("-" * 70)
    
    data_loader = DataLoader("exceptions_input.xlsx")
    
    if not data_loader.validate_data():
        print("\n❌ Data validation failed. Please fix the issues and try again.")
        return
    
    if not data_loader.validate_config_match():
        print("\n❌ Config validation failed. Please update config.py with correct section counts.")
        return
    
    subjects = data_loader.get_subjects()
    teachers = data_loader.get_teachers()
    rooms = data_loader.get_rooms()
    course_semesters = data_loader.get_course_semesters()
    room_capacities = data_loader.get_room_capacities()
    
    # Print comprehensive data summary
    data_loader.print_data_summary()
    
    # Step 1.5: PRE-SOLVER FEASIBILITY CHECK
    print("\n" + "=" * 70)
    print("📋 STEP 1.5: PRE-SOLVER FEASIBILITY CHECK")
    print("-" * 70)
    
    feasibility_checker = FeasibilityChecker(subjects, room_capacities)
    is_feasible, issues, warnings, stats = feasibility_checker.check_feasibility()
    feasibility_checker.print_summary()
    
    if not is_feasible:
        print("\n" + "=" * 70)
        print("🛑 STOPPING: Critical issues found that prevent solution")
        print("=" * 70)
        print("\n💡 PLEASE FIX THE ISSUES ABOVE BEFORE PROCEEDING")
        print("   The solver will NOT find a solution with these problems.")
        print("\n📧 If you need help, review the specific error messages above.")
        return
    
    # Step 2: Select constraints
    print("\n" + "=" * 70)
    print("📋 STEP 2: CONSTRAINT CONFIGURATION")
    print("-" * 70)
    
    constraint_selector = ConstraintSelector()
    selected_constraints = constraint_selector.select_constraints()
    
    # Step 3: Build model with constraints
    print("\n" + "=" * 70)
    print("📋 STEP 3: MODEL BUILDING")
    print("-" * 70)
    
    constraint_builder = ConstraintBuilder(
        subjects, teachers, rooms, course_semesters, 
        room_capacities, constraint_selector,
        data_loader.teacher_initials
    )
    model, variables = constraint_builder.build_model()
    
    # Step 4: Solve the model
    print("\n" + "=" * 70)
    print("📋 STEP 4: SOLVING OPTIMIZATION PROBLEM")
    print("-" * 70)
    
    solver_engine = SolverEngine(model, variables, subjects, data_loader.teacher_initials)
    # model.ExportToFile("debug_model.proto.txt") # Creates a debug txt file that stores all the solver's logs in it
    solution = solver_engine.solve()
    
    if not solution:
        print("\n" + "=" * 70)
        print("❌ FAILED: No feasible solution found")
        print("=" * 70)
        print("\n💡 TROUBLESHOOTING TIPS:")
        print("   1. Review the pre-solver warnings above")
        print("   2. Try disabling some optional constraints and re-run")
        print("   3. Increase max consecutive/daily hours limits")
        print("   4. Check if practical consecutive constraint is too restrictive")
        print("   5. Review teacher workload distribution")
        print("\n📧 Note: Pre-solver check passed but solver still failed.")
        print("   This might indicate:")
        print("   - Optional constraints are too restrictive")
        print("   - Edge case not caught by pre-solver checks")
        print("   - Early completion objective forcing impossible schedule")
        return
    
    # Step 5: Generate outputs
    print("\n" + "=" * 70)
    print("📋 STEP 5: GENERATING TIMETABLES")
    print("-" * 70)
    
    # Create output directory
    os.makedirs("output", exist_ok=True)
    
    # Generate Excel master timetable
    print("\n   📊 Generating master timetable (Excel)...")
    excel_generator = ExcelGenerator(solution, subjects)
    excel_generator.generate_master_timetable("output/master_timetable.xlsx")
    
    # Generate PDF timetables
    pdf_generator = PDFGenerator(solution, subjects, teachers, rooms, course_semesters)
    
    print("\n   📄 Generating teacher timetables (PDF)...")
    pdf_generator.generate_teacher_timetables("output/teachers/")
    
    print("\n   📄 Generating room timetables (PDF)...")
    pdf_generator.generate_room_timetables("output/rooms/")
    
    print("\n   📄 Generating course-semester timetables (PDF)...")
    pdf_generator.generate_course_semester_timetables("output/courses/")
    
    # Print summary
    solver_engine.print_summary()
    
    # Final success message
    print("\n" + "=" * 70)
    print("✅ SUCCESS: Timetable generation completed!")
    print("=" * 70)
    print("\n📁 OUTPUT FILES LOCATION:")
    print("   📂 output/")
    print("      ├── master_timetable.xlsx        (Complete schedule - Excel)")
    print("      ├── teachers/                    (Individual teacher schedules)")
    print("      ├── rooms/                       (Room utilization schedules)")
    print("      └── courses/                     (Course-semester schedules)")
    print("\n💡 KEY FEATURES:")
    print("   • Room numbers shown (Room-1, Lab-CS-1, etc.)")
    print("   • Reserved slots marked for GE/SEC/VAC/AEC")
    print("   • Continuous classes formatted without separators")
    print("   • Tutorial flexibility: sacrificed when needed")
    print("   • Year-appropriate reserved slot display")
    print("   • Multi-teacher support (co-teaching)")
    print("\n" + "=" * 70 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Operation cancelled by user")
    except Exception as e:
        print(f"\n\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()

