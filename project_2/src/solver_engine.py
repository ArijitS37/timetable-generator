"""
Solver engine module - UPDATED with room numbering
"""
from ortools.sat.python import cp_model
from src.config import Config
from typing import Dict, List, Any, Optional

class SolverEngine:
    def __init__(self, model: cp_model.CpModel, variables: Dict, subjects: List[Dict], teacher_initials: Dict[str, str]):
        self.model = model
        self.variables = variables
        self.subjects = subjects
        self.teacher_initials = teacher_initials
        self.solver = cp_model.CpSolver()
        self.solution = None
        self.room_assignments = {}  # Track specific room assignments
    
    def _build_subject_id(self, subj: Dict) -> str:
        """
        Build consistent subject_id, handling split teaching with teacher initials.
        Must match the ID format used in constraint_builder.py
        """
        if subj.get("Is_Split_Teaching", False):
            teacher_initials = self.teacher_initials.get(subj["Teacher"], "UNK")
            return f"{subj['Course_Semester']}_{subj['Subject']}_{teacher_initials}"
        else:
            return f"{subj['Course_Semester']}_{subj['Subject']}"
        
    def solve(self) -> Optional[Dict]:
        """Solve the timetable optimization problem"""
        print(f"\n🔍 Starting solver (max {Config.SOLVER_TIME_LIMIT}s)...")
        
        self.solver.parameters.max_time_in_seconds = Config.SOLVER_TIME_LIMIT
        self.solver.parameters.log_search_progress = True
        
        status = self.solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL:
            print("✅ OPTIMAL solution found!")
            self.solution = self._extract_solution()
            self.solution = self._assign_assistants(self.solution)  # NEW
            return self.solution
        elif status == cp_model.FEASIBLE:
            print("✅ FEASIBLE solution found!")
            self.solution = self._extract_solution()
            self.solution = self._assign_assistants(self.solution)  # NEW
            return self.solution
        else:
            print("❌ No solution found")
            self._diagnose_failure(status)
            return None

    def _assign_assistants(self, solution: Dict) -> Dict:
        """Post-processing: Assign assistant teachers to labs based on 1:20 ratio"""
        print("\n🔧 Assigning assistant teachers to lab classes...")
        
        # Track teacher availability and workload
        teacher_availability = {}  # {teacher: {time_slot: is_free}}
        teacher_workload = {}  # {teacher: hours_assigned}
        
        # Initialize teacher data
        all_teachers = set()
        for subj in self.subjects:
            all_teachers.add(subj["Teacher"])
            for co_teacher in subj.get("Co_Teachers", []):
                all_teachers.add(co_teacher)
        
        for teacher in all_teachers:
            teacher_workload[teacher] = 0
            teacher_availability[teacher] = {t: True for t in range(len(solution['time_slots']))}
        
        # Mark times when teachers are busy (from main teaching)
        for day, day_schedule in solution['master_schedule'].items():
            for slot, classes in day_schedule.items():
                # Find time slot index
                time_idx = None
                for idx, (d, s) in enumerate(solution['time_slots']):
                    if d == day and s == slot:
                        time_idx = idx
                        break
                
                if time_idx is None:
                    continue
                
                for class_info in classes:
                    # Mark all teachers in this class as busy
                    for teacher in class_info['teachers_list']:
                        teacher_availability[teacher][time_idx] = False
                        
                        # Count workload for taught hours
                        teacher_workload[teacher] += 1
        
        # Now assign assistants to labs that need them
        assistant_assignments = {}  # {(subject_id, time): [list of assistant teachers]}
        
        for subj in self.subjects:
            if subj["Practical_hours"] == 0:
                continue
            
            subject_id = self._build_subject_id(subj)
            student_count = subj["Students_count"]
            main_teacher = subj["Teacher"]
            department = subj["Department"]
            
            # Calculate teachers needed (1:20 ratio)
            teachers_needed = (student_count + Config.LAB_TEACHER_RATIO - 1) // Config.LAB_TEACHER_RATIO
            
            # Main teacher counts as 1
            assistants_needed = teachers_needed - 1
            
            if assistants_needed <= 0:
                continue
            
            # Find when this lab is scheduled
            for day, day_schedule in solution['master_schedule'].items():
                for slot, classes in day_schedule.items():
                    for class_info in classes:
                        if (class_info['subject'] == subj['Subject'] and 
                            class_info['course_semester'] == subj['Course_Semester'] and
                            class_info['type'] == 'Practical' and
                            not class_info.get('is_continuation', False)):
                            
                            # This is the start of a practical session
                            # Find time indices for both hours
                            start_time_idx = None
                            for idx, (d, s) in enumerate(solution['time_slots']):
                                if d == day and s == slot:
                                    start_time_idx = idx
                                    break
                            
                            if start_time_idx is None:
                                continue
                            
                            practical_hours = [start_time_idx, start_time_idx + 1]
                            
                            # Find available teachers from same department
                            available_teachers = []
                            for teacher in all_teachers:
                                if teacher == main_teacher:
                                    continue  # Main teacher already assigned
                                
                                # Check if teacher is from same department
                                teacher_dept = None
                                for s in self.subjects:
                                    if s["Teacher"] == teacher:
                                        teacher_dept = s["Department"]
                                        break
                                
                                if teacher_dept != department:
                                    continue
                                
                                # Check if under 16 hours
                                if teacher_workload.get(teacher, 0) >= Config.MAX_HOURS_PER_TEACHER:
                                    continue
                                
                                # Check availability for practical hours
                                is_available = all(
                                    teacher_availability[teacher].get(h, False)
                                    for h in practical_hours
                                )
                                
                                if is_available:
                                    available_teachers.append(teacher)
                            
                            # Sort by current workload (assign to those with fewer hours first)
                            available_teachers.sort(key=lambda t: teacher_workload.get(t, 0))
                            
                            # Assign assistants
                            assigned_assistants = []
                            for i in range(min(assistants_needed, len(available_teachers))):
                                asst_teacher = available_teachers[i]
                                assigned_assistants.append(asst_teacher)
                                
                                # Mark as busy for these hours
                                for h in practical_hours:
                                    teacher_availability[asst_teacher][h] = False
                                
                                # Add to workload (2 hours for lab)
                                teacher_workload[asst_teacher] += 2
                            
                            # Store assignment
                            key = (subject_id, start_time_idx)
                            assistant_assignments[key] = assigned_assistants
                            
                            # Check if we couldn't fill all positions
                            if len(assigned_assistants) < assistants_needed:
                                shortage = assistants_needed - len(assigned_assistants)
                                print(f"   ⚠️  {subj['Subject']} [{subj['Course_Semester']}]: "
                                    f"Needs {teachers_needed} teachers, assigned {len(assigned_assistants) + 1}, "
                                    f"short {shortage} assistant(s)")
        
        # Update solution with assistant info
        solution['assistant_assignments'] = assistant_assignments
        solution['teacher_workload_after_assistants'] = teacher_workload
        
        return solution
    
    def _extract_solution(self) -> Dict:
        time_slots = Config.get_time_slots()
        slots = Config.get_slots_list()
        
        # Build master schedule with room assignments
        master_schedule = {}
        
        # Track room usage per time slot for assignment
        room_usage = {}
        
        # Track which teachers are present at each time slot for each subject
        # Format: {(subject_id, time_slot): [list of teachers]}
        teachers_at_slot = {}
        
        # First pass: Determine which teachers are present at which times
        for subj in self.subjects:
            subject_id = self._build_subject_id(subj)
            main_teacher = subj["Teacher"]
            
            # Check all time slots
            for t in range(len(time_slots)):
                teachers_present = []
                
                # Main teacher always present if any class at this time
                is_class_at_t = False
                
                # Check lectures
                if (subject_id, t) in self.variables['lecture']:
                    if self.solver.Value(self.variables['lecture'][(subject_id, t)]) == 1:
                        is_class_at_t = True
                
                # Check tutorials
                if (subject_id, t) in self.variables['tutorial']:
                    if self.solver.Value(self.variables['tutorial'][(subject_id, t)]) == 1:
                        is_class_at_t = True
                
                # Check practicals - main teacher present for all hours
                if (subject_id, t) in self.variables['practical']:
                    if self.solver.Value(self.variables['practical'][(subject_id, t)]) == 1:
                        is_class_at_t = True
                
                if is_class_at_t:
                    teachers_present.append(main_teacher)
                    
                    # Check co-teachers
                    for co_teacher in subj.get("Co_Teachers", []):
                        teachers_present.append(co_teacher)
                    
                    if teachers_present:
                        teachers_at_slot[(subject_id, t)] = teachers_present
        
        # Second pass: Build schedule with proper teacher lists
        
        # Process lectures
        for (subject_id, t), var in self.variables['lecture'].items():
            if self.solver.Value(var) == 1:
                day, slot = time_slots[t]
                subj_details = self._get_subject_details(subject_id)
                
                # Get teachers for this slot
                teachers = teachers_at_slot.get((subject_id, t), [subj_details['Teacher']])
                teacher_str = ", ".join(teachers)
                
                # Assign specific classroom
                room_number = self._assign_room(t, "Classroom", room_usage)
                
                if day not in master_schedule:
                    master_schedule[day] = {}
                if slot not in master_schedule[day]:
                    master_schedule[day][slot] = []
                
                # Find which room was assigned
                assigned_room = "Room-TBD"
                for room in Config.get_rooms_by_type("classroom"):
                    if (subject_id, t, room, 'lecture') in self.variables['room_assignment']:
                        if self.solver.Value(self.variables['room_assignment'][(subject_id, t, room, 'lecture')]) == 1:
                            assigned_room = room
                            break

                # Check if using lab instead
                if assigned_room == "Room-TBD":
                    for lab in [name for name, info in Config.ROOMS.items() if info["type"] == "lab"]:
                        if (subject_id, t, lab, 'lecture') in self.variables['room_assignment']:
                            if self.solver.Value(self.variables['room_assignment'][(subject_id, t, lab, 'lecture')]) == 1:
                                assigned_room = f"{lab} (Theory)"
                                break

                class_info = {
                    'subject': subj_details['Subject'],
                    'teacher': teacher_str,
                    'teachers_list': teachers,
                    'course_semester': subj_details['Course_Semester'],
                    'type': 'Lecture',
                    'room': assigned_room,
                    'room_type': 'Classroom' if 'R-' in assigned_room else 'Lab',
                    'subject_type': subj_details['Subject_type'],
                    'section': subj_details['Section']
                }
                
                # ✅ FIX: Actually append to master_schedule!
                master_schedule[day][slot].append(class_info)
        
        # Process tutorials
        for (subject_id, t), var in self.variables['tutorial'].items():
            if self.solver.Value(var) == 1:
                day, slot = time_slots[t]
                subj_details = self._get_subject_details(subject_id)
                
                # Get teachers for this slot
                teachers = teachers_at_slot.get((subject_id, t), [subj_details['Teacher']])
                teacher_str = ", ".join(teachers)
                
                # Assign specific classroom
                room_number = self._assign_room(t, "Classroom", room_usage)
                
                if day not in master_schedule:
                    master_schedule[day] = {}
                if slot not in master_schedule[day]:
                    master_schedule[day][slot] = []
                
                # Find which room was assigned
                assigned_room = "Room-TBD"
                for room in Config.get_rooms_by_type("classroom"):
                    if (subject_id, t, room, 'tutorial') in self.variables['room_assignment']:
                        if self.solver.Value(self.variables['room_assignment'][(subject_id, t, room, 'tutorial')]) == 1:
                            assigned_room = room
                            break

                # Check if using lab instead
                if assigned_room == "Room-TBD":
                    for lab in [name for name, info in Config.ROOMS.items() if info["type"] == "lab"]:
                        if (subject_id, t, lab, 'tutorial') in self.variables['room_assignment']:
                            if self.solver.Value(self.variables['room_assignment'][(subject_id, t, lab, 'tutorial')]) == 1:
                                assigned_room = f"{lab} (Theory)"
                                break

                class_info = {
                    'subject': subj_details['Subject'],
                    'teacher': teacher_str,
                    'teachers_list': teachers,
                    'course_semester': subj_details['Course_Semester'],
                    'type': 'Tutorial',
                    'room': assigned_room,
                    'room_type': 'Classroom' if 'R-' in assigned_room else 'Lab',
                    'subject_type': subj_details['Subject_type'],
                    'section': subj_details['Section']
                }
                
                # ✅ FIX: Actually append to master_schedule!
                master_schedule[day][slot].append(class_info)
        
        # Process practicals (2-hour sessions) - this part was already correct
        for (subject_id, t), var in self.variables['practical'].items():
            if self.solver.Value(var) == 1:
                day, slot = time_slots[t]
                subj_details = self._get_subject_details(subject_id)
                lab_type = subj_details['Lab_type']
                
                # Find which lab(s) were assigned
                assigned_labs = []
                available_labs = Config.get_labs_by_department(subj_details["Department"])

                for lab in available_labs:
                    if (subject_id, t, lab, 'practical') in self.variables['room_assignment']:
                        if self.solver.Value(self.variables['room_assignment'][(subject_id, t, lab, 'practical')]) == 1:
                            assigned_labs.append(lab)

                # Format room names
                if len(assigned_labs) == 1:
                    room_name = assigned_labs[0]
                elif len(assigned_labs) > 1:
                    room_name = ", ".join(assigned_labs)
                else:
                    room_name = f"{lab_type}-TBD"

                # Add to both consecutive slots
                for offset in [0, 1]:
                    if t + offset < len(time_slots):
                        day_offset, slot_offset = time_slots[t + offset]
                        
                        # Get teachers for THIS specific hour
                        teachers = teachers_at_slot.get((subject_id, t + offset), [subj_details['Teacher']])
                        teacher_str = ", ".join(teachers)
                        
                        if day_offset not in master_schedule:
                            master_schedule[day_offset] = {}
                        if slot_offset not in master_schedule[day_offset]:
                            master_schedule[day_offset][slot_offset] = []
                        
                        class_info = {
                            'subject': subj_details['Subject'],
                            'teacher': teacher_str,
                            'teachers_list': teachers,
                            'course_semester': subj_details['Course_Semester'],
                            'type': 'Practical',
                            'room': room_name,
                            'room_type': lab_type,
                            'subject_type': subj_details['Subject_type'],
                            'section': subj_details['Section'],
                            'is_continuation': offset == 1
                        }
                        master_schedule[day_offset][slot_offset].append(class_info)
        
        # Check which tutorials were scheduled
        tutorials_scheduled = {}
        for subject_id, var in self.variables.get('tutorial_used', {}).items():
            tutorials_scheduled[subject_id] = self.solver.Value(var) == 1
        
        solution = {
            'master_schedule': master_schedule,
            'solver': self.solver,
            'variables': self.variables,
            'max_used_slot': self.solver.Value(self.variables['max_used_slot']) if 'max_used_slot' in self.variables else -1,
            'time_slots': time_slots,
            'slots': slots,
            'tutorials_scheduled': tutorials_scheduled,
            'room_assignments': room_usage
        }
        
        return solution
    
    def _assign_room(self, time_slot: int, room_type: str, room_usage: Dict) -> int:
        """Assign a specific room number for a class"""
        if time_slot not in room_usage:
            room_usage[time_slot] = {}
        if room_type not in room_usage[time_slot]:
            room_usage[time_slot][room_type] = []
        
        # Get total rooms of this type
        if room_type == "Classroom":
            total_rooms = len(Config.get_rooms_by_type("classroom"))  # ✅ CORRECT
        else:
            # For labs, get count by department
            total_rooms = len([name for name, info in Config.ROOMS.items() 
                            if info["type"] == "lab"])  # ✅ CORRECT
        
        # Find next available room
        used_rooms = room_usage[time_slot][room_type]
        for room_num in range(1, total_rooms + 1):
            if room_num not in used_rooms:
                room_usage[time_slot][room_type].append(room_num)
                return room_num
        
        # If all rooms used, assign overflow (shouldn't happen with proper constraints)
        return total_rooms
    
    def _get_subject_details(self, subject_id: str) -> Dict:
        """Get subject details from subject_id"""
        for subj in self.subjects:
            if self._build_subject_id(subj) == subject_id:
                return subj
        return {}
    
    def _diagnose_failure(self, status: int):
        """Provide diagnostic information for failed solutions"""
        if status == cp_model.INFEASIBLE:
            print("\n💡 The problem is INFEASIBLE. Possible causes:")
            print("   - Too many hour requirements for available time slots")
            print("   - Teacher overload (>16 hours/week per teacher)")
            print("   - Insufficient rooms for concurrent classes")
            print("   - Fixed slot constraints too restrictive")
            print("   - Max consecutive/daily constraints too tight")
            print("   - Practical consecutive slot requirements cannot be met")
        elif status == cp_model.MODEL_INVALID:
            print("\n💡 The model is INVALID. Check constraint definitions.")
        elif status == cp_model.UNKNOWN:
            print("\n💡 Solver timed out or ran out of resources. Try:")
            print("   - Increasing solver time limit in config.py")
            print("   - Disabling some optional constraints")
            print("   - Reducing problem complexity")
    
    def print_summary(self):
        """Print solution summary statistics with before/after workload"""
        if not self.solution:
            print("\n❌ No solution available for summary")
            return
        
        print(f"\n📊 SOLUTION SUMMARY:")
        print("=" * 70)
        
        if self.solution['max_used_slot'] >= 0:
            latest_slot = self.solution['time_slots'][self.solution['max_used_slot']]
            print(f"   ⏰ Latest used time slot: {latest_slot}")
        
        # Count scheduled classes
        total_lectures = sum(
            self.solver.Value(var) for var in self.variables['lecture'].values()
        )
        total_tutorials = sum(
            self.solver.Value(var) for var in self.variables['tutorial'].values()
        )
        total_practicals = sum(
            self.solver.Value(var) for var in self.variables['practical'].values()
        )
        
        # Check tutorial sacrifices
        tutorials_total = len([s for s in self.subjects if s['Tutorial_hours'] > 0])
        tutorials_scheduled = sum(1 for v in self.solution['tutorials_scheduled'].values() if v)
        tutorials_sacrificed = tutorials_total - tutorials_scheduled
        
        print(f"\n   📚 Classes Scheduled:")
        print(f"      Lectures: {total_lectures}")
        print(f"      Tutorials: {total_tutorials} ({tutorials_scheduled}/{tutorials_total} subjects)")
        if tutorials_sacrificed > 0:
            print(f"         ⚠️  {tutorials_sacrificed} tutorial(s) sacrificed to meet constraints")
        print(f"      Practicals: {total_practicals} sessions (×2 hours each)")
        print(f"      Total hours: {total_lectures + total_tutorials + (total_practicals * 2)}")
        
        # BEFORE/AFTER Teacher workload analysis
        print(f"\n   👨‍🏫 TEACHER WORKLOAD ANALYSIS:")
        print(f"   {'='*66}")
        
        # Calculate BEFORE workload (from input - what they're assigned to teach)
        teacher_hours_before = {}
        for subj in self.subjects:
            main_teacher = subj["Teacher"]
            taught_hours = subj.get("Total_taught_hours", subj["Total_hours"])
            
            if main_teacher not in teacher_hours_before:
                teacher_hours_before[main_teacher] = 0
            
            # For split teaching, divide hours
            if subj.get("Is_Split_Teaching", False) and subj.get("Co_Teachers"):
                num_teachers = 1 + len(subj["Co_Teachers"])
                teacher_hours_before[main_teacher] += taught_hours / num_teachers
                
                for co_teacher in subj["Co_Teachers"]:
                    if co_teacher not in teacher_hours_before:
                        teacher_hours_before[co_teacher] = 0
                    teacher_hours_before[co_teacher] += taught_hours / num_teachers
            else:
                teacher_hours_before[main_teacher] += taught_hours
                
                # Co-teaching: full hours for all
                for co_teacher in subj.get("Co_Teachers", []):
                    if co_teacher not in teacher_hours_before:
                        teacher_hours_before[co_teacher] = 0
                    teacher_hours_before[co_teacher] += taught_hours
        
        # Get AFTER workload (with assistant assignments)
        teacher_hours_after = self.solution.get('teacher_workload_after_assistants', {})
        
        # Display comparison
        print(f"\n   {'Teacher':<30} {'Before':<12} {'After':<12} {'Change':<10} {'Status'}")
        print(f"   {'-'*66}")
        
        all_teachers = sorted(set(list(teacher_hours_before.keys()) + list(teacher_hours_after.keys())))
        
        for teacher in all_teachers:
            before = teacher_hours_before.get(teacher, 0)
            after = teacher_hours_after.get(teacher, 0)
            change = after - before
            
            # Status icon
            if after > Config.MAX_HOURS_PER_TEACHER:
                status = "❌ OVER"
            elif after == Config.MAX_HOURS_PER_TEACHER:
                status = "✅ FULL"
            elif after >= Config.MAX_HOURS_PER_TEACHER * 0.9:
                status = "✅ NEAR"
            elif change > 0:
                status = "✅ +ASST"
            else:
                status = "✅ OK"
            
            change_str = f"+{change:.1f}h" if change > 0 else f"{change:.1f}h" if change < 0 else "—"
            
            print(f"   {teacher:<30} {before:>5.1f}/{Config.MAX_HOURS_PER_TEACHER:<4}h  "
                f"{after:>5.1f}/{Config.MAX_HOURS_PER_TEACHER:<4}h  {change_str:<10} {status}")
        
        print(f"   {'-'*66}")
        
        # Summary stats
        before_count = len([t for t, h in teacher_hours_before.items() if h > 0])
        after_full = len([t for t, h in teacher_hours_after.items() if h == Config.MAX_HOURS_PER_TEACHER])
        after_over = len([t for t, h in teacher_hours_after.items() if h > Config.MAX_HOURS_PER_TEACHER])
        after_under = len([t for t, h in teacher_hours_after.items() if h < Config.MAX_HOURS_PER_TEACHER and h > 0])
        assistants_added = len([t for t in all_teachers if teacher_hours_after.get(t, 0) > teacher_hours_before.get(t, 0)])
        
        print(f"\n   📈 Summary:")
        print(f"      Teachers with assignments: {before_count}")
        print(f"      At full capacity (16h): {after_full}")
        print(f"      Over capacity: {after_over} {'❌' if after_over > 0 else ''}")
        print(f"      Under capacity: {after_under}")
        print(f"      Assigned as assistants: {assistants_added}")
        
        # Room utilization
        print(f"\n   🏢 Room Utilization:")
        room_usage = {}
        for day_schedule in self.solution['master_schedule'].values():
            for slot_classes in day_schedule.values():
                for class_info in slot_classes:
                    room = class_info['room']
                    room_usage[room] = room_usage.get(room, 0) + 1

        # Sort rooms properly
        def sort_room_key(room_name):
            parts = room_name.split('-')
            if len(parts) < 2:
                return (room_name, "", 0)
            
            room_type = parts[0]
            try:
                room_num = int(parts[-1].split()[0])  # Handle "Lab (Theory)"
                middle = parts[1] if len(parts) > 2 else ""
                return (room_type, middle, room_num)
            except (ValueError, IndexError):
                return (room_type, parts[1] if len(parts) > 1 else "", 0)

        for room in sorted(room_usage.keys(), key=sort_room_key):
            theory_marker = " (includes theory)" if "(Theory)" in room else ""
            print(f"      {room}: {room_usage[room]} slot-hours{theory_marker}")

        print("=" * 70)