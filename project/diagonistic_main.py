"""
Diagnostic version to identify the constraint causing infeasibility
"""
from src.data_loader import DataLoader
from src.constraint_builder import ConstraintBuilder
from src.solver_engine import SolverEngine
from src.config import Config
from ortools.sat.python import cp_model

def test_constraints_incrementally():
    """Test constraints one by one to find the problematic one"""
    
    print("🔍 DIAGNOSTIC MODE - Testing constraints incrementally")
    
    # Load data
    data_loader = DataLoader("input.xlsx")
    if not data_loader.validate_data():
        return
    
    subjects = data_loader.get_subjects()
    teachers = data_loader.get_teachers()
    rooms = data_loader.get_rooms()
    years = data_loader.get_years()
    room_capacities = data_loader.get_room_capacity_config()
    
    print(f"📊 Data: {len(subjects)} subjects, {len(teachers)} teachers, {len(rooms)} rooms, {len(years)} years")
    print(f"📍 Room capacities: {room_capacities}")
    
    # Test 1: Only hour requirements
    print("\n🧪 TEST 1: Only hour requirements")
    model1 = cp_model.CpModel()
    builder = ConstraintBuilder(subjects, teachers, rooms, years, room_capacities)
    variables = builder._create_variables(model1)
    builder._add_hour_requirements(model1, variables)
    
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 30
    status = solver.Solve(model1)
    print(f"Result: {'✅ FEASIBLE' if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else '❌ INFEASIBLE'}")
    
    # Test 2: Hour requirements + Teacher clash
    print("\n🧪 TEST 2: Hour requirements + Teacher clash")
    model2 = cp_model.CpModel()
    variables = builder._create_variables(model2)
    builder._add_hour_requirements(model2, variables)
    
    # Add only teacher clash constraints
    for t in range(len(builder.time_slots)):
        for teacher in teachers:
            teacher_load = builder._calculate_teacher_load_at_time(teacher, t, variables)
            model2.Add(teacher_load <= 1)
    
    status = solver.Solve(model2)
    print(f"Result: {'✅ FEASIBLE' if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else '❌ INFEASIBLE'}")
    
    # Test 3: + Room clash
    print("\n🧪 TEST 3: + Room clash")
    model3 = cp_model.CpModel()
    variables = builder._create_variables(model3)
    builder._add_hour_requirements(model3, variables)
    
    for t in range(len(builder.time_slots)):
        for teacher in teachers:
            teacher_load = builder._calculate_teacher_load_at_time(teacher, t, variables)
            model3.Add(teacher_load <= 1)
        
        for room in rooms:
            room_load = builder._calculate_room_load_at_time(room, t, variables)
            room_capacity = room_capacities.get(room, 1)
            model3.Add(room_load <= room_capacity)
    
    status = solver.Solve(model3)
    print(f"Result: {'✅ FEASIBLE' if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else '❌ INFEASIBLE'}")
    
    # Test 4: + Year clash
    print("\n🧪 TEST 4: + Year clash")
    model4 = cp_model.CpModel()
    variables = builder._create_variables(model4)
    builder._add_hour_requirements(model4, variables)
    
    for t in range(len(builder.time_slots)):
        for teacher in teachers:
            teacher_load = builder._calculate_teacher_load_at_time(teacher, t, variables)
            model4.Add(teacher_load <= 1)
        
        for room in rooms:
            room_load = builder._calculate_room_load_at_time(room, t, variables)
            room_capacity = room_capacities.get(room, 1)
            model4.Add(room_load <= room_capacity)
            
        for year in years:
            year_load = builder._calculate_year_load_at_time(year, t, variables)
            model4.Add(year_load <= 1)
    
    status = solver.Solve(model4)
    print(f"Result: {'✅ FEASIBLE' if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else '❌ INFEASIBLE'}")
    
    # Test 5: + Teacher load constraints
    print("\n🧪 TEST 5: + Teacher load constraints")
    model5 = cp_model.CpModel()
    variables = builder._create_variables(model5)
    builder._add_hour_requirements(model5, variables)
    
    for t in range(len(builder.time_slots)):
        for teacher in teachers:
            teacher_load = builder._calculate_teacher_load_at_time(teacher, t, variables)
            model5.Add(teacher_load <= 1)
        
        for room in rooms:
            room_load = builder._calculate_room_load_at_time(room, t, variables)
            room_capacity = room_capacities.get(room, 1)
            model5.Add(room_load <= room_capacity)
            
        for year in years:
            year_load = builder._calculate_year_load_at_time(year, t, variables)
            model5.Add(year_load <= 1)
    
    # Add teacher load constraints
    for teacher in teachers:
        total_theory_hours = sum(
            variables['timetable'][(subj["Subject"], t)]
            for subj in subjects
            for t in range(len(builder.time_slots))
            if subj["Teacher"] == teacher and subj.get("Type", "").lower() != "lab"
        )
        
        total_lab_hours = sum(
            variables['lab_sessions'][(subj["Subject"], t)] * 2
            for subj in subjects
            for t in range(len(builder.time_slots))
            if (subj["Teacher"] == teacher and 
                subj.get("Type", "").lower() == "lab" and
                (subj["Subject"], t) in variables['lab_sessions'])
        )
        
        model5.Add(total_theory_hours + total_lab_hours <= Config.MAX_HOURS_PER_TEACHER)
    
    status = solver.Solve(model5)
    print(f"Result: {'✅ FEASIBLE' if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else '❌ INFEASIBLE'}")
    
    # Test 6: + Lab duration constraints (THE SUSPECT!)
    print("\n🧪 TEST 6: + Lab duration constraints")
    model6 = cp_model.CpModel()
    variables = builder._create_variables(model6)
    builder._add_hour_requirements(model6, variables)
    
    for t in range(len(builder.time_slots)):
        for teacher in teachers:
            teacher_load = builder._calculate_teacher_load_at_time(teacher, t, variables)
            model6.Add(teacher_load <= 1)
        
        for room in rooms:
            room_load = builder._calculate_room_load_at_time(room, t, variables)
            room_capacity = room_capacities.get(room, 1)
            model6.Add(room_load <= room_capacity)
            
        for year in years:
            year_load = builder._calculate_year_load_at_time(year, t, variables)
            model6.Add(year_load <= 1)
    
    for teacher in teachers:
        total_theory_hours = sum(
            variables['timetable'][(subj["Subject"], t)]
            for subj in subjects
            for t in range(len(builder.time_slots))
            if subj["Teacher"] == teacher and subj.get("Type", "").lower() != "lab"
        )
        
        total_lab_hours = sum(
            variables['lab_sessions'][(subj["Subject"], t)] * 2
            for subj in subjects
            for t in range(len(builder.time_slots))
            if (subj["Teacher"] == teacher and 
                subj.get("Type", "").lower() == "lab" and
                (subj["Subject"], t) in variables['lab_sessions'])
        )
        
        model6.Add(total_theory_hours + total_lab_hours <= Config.MAX_HOURS_PER_TEACHER)
    
    # Add lab duration constraints
    for subj in subjects:
        if subj.get("Type", "").lower() == "lab":
            for t in range(len(builder.time_slots)):
                if ((subj["Subject"], t) in variables['lab_sessions'] and
                    t < len(builder.time_slots) - 1 and
                    builder._is_consecutive_slot(t + 1)):
                    
                    model6.Add(
                        variables['timetable'][(subj["Subject"], t)] >= 
                        variables['lab_sessions'][(subj["Subject"], t)]
                    )
                    model6.Add(
                        variables['timetable'][(subj["Subject"], t+1)] >= 
                        variables['lab_sessions'][(subj["Subject"], t)]
                    )
    
    status = solver.Solve(model6)
    print(f"Result: {'✅ FEASIBLE' if status in [cp_model.OPTIMAL, cp_model.FEASIBLE] else '❌ INFEASIBLE'}")
    
    if status not in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("\n💡 LAB DURATION CONSTRAINTS are causing the infeasibility!")
        print("🔧 Analyzing lab constraints...")
        
        # Check lab session variables
        lab_count = sum(1 for key in variables['lab_sessions'].keys())
        print(f"📊 Total lab session variables created: {lab_count}")
        
        # Check consecutive slots available
        consecutive_pairs = 0
        for day_idx, day in enumerate(Config.DAYS):
            for slot_idx in range(len(builder.slots) - 1):
                consecutive_pairs += 1
        
        print(f"📊 Consecutive slot pairs per day: {len(builder.slots) - 1}")
        print(f"📊 Total consecutive pairs available: {consecutive_pairs * len(Config.DAYS)}")
        print(f"📊 Lab sessions needed: {len([s for s in subjects if s.get('Type', '').lower() == 'lab'])}")

if __name__ == "__main__":
    test_constraints_incrementally()