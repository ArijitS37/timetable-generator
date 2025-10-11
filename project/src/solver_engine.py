"""
Solver engine module - UPDATED with room numbering
"""
from ortools.sat.python import cp_model
from src.config import Config
from typing import Dict, List, Any, Optional

class SolverEngine:
    def __init__(self, model: cp_model.CpModel, variables: Dict, subjects: List[Dict]):
        self.model = model
        self.variables = variables
        self.subjects = subjects
        self.solver = cp_model.CpSolver()
        self.solution = None
        self.room_assignments = {}  # Track specific room assignments
        
    def solve(self) -> Optional[Dict]:
        """Solve the timetable optimization problem"""
        print(f"\n🔍 Starting solver (max {Config.SOLVER_TIME_LIMIT}s)...")
        
        self.solver.parameters.max_time_in_seconds = Config.SOLVER_TIME_LIMIT
        self.solver.parameters.log_search_progress = True
        
        status = self.solver.Solve(self.model)
        
        if status == cp_model.OPTIMAL:
            print("✅ OPTIMAL solution found!")
            self.solution = self._extract_solution()
            return self.solution
        elif status == cp_model.FEASIBLE:
            print("✅ FEASIBLE solution found!")
            self.solution = self._extract_solution()
            return self.solution
        else:
            print("❌ No solution found")
            self._diagnose_failure(status)
            return None
    
    def _extract_solution(self) -> Dict:
        """Extract solution from solver and assign specific room numbers"""
        time_slots = Config.get_time_slots()
        slots = Config.get_slots_list()
        
        # Build master schedule with room assignments
        master_schedule = {}
        
        # Track room usage per time slot for assignment
        room_usage = {}  # {time_slot: {room_type: [list of assigned room numbers]}}
        
        # Process lectures
        for (subject_id, t), var in self.variables['lecture'].items():
            if self.solver.Value(var) == 1:
                day, slot = time_slots[t]
                subj_details = self._get_subject_details(subject_id)
                
                # Assign specific classroom
                room_number = self._assign_room(t, "Classroom", room_usage)
                
                if day not in master_schedule:
                    master_schedule[day] = {}
                if slot not in master_schedule[day]:
                    master_schedule[day][slot] = []
                
                class_info = {
                    'subject': subj_details['Subject'],
                    'teacher': subj_details['Teacher'],
                    'course_semester': subj_details['Course_Semester'],
                    'type': 'Lecture',
                    'room': f"Room-{room_number}",
                    'room_type': 'Classroom',
                    'subject_type': subj_details['Subject_type'],
                    'section': subj_details['Section']
                }
                master_schedule[day][slot].append(class_info)
        
        # Process tutorials
        for (subject_id, t), var in self.variables['tutorial'].items():
            if self.solver.Value(var) == 1:
                day, slot = time_slots[t]
                subj_details = self._get_subject_details(subject_id)
                
                # Assign specific classroom
                room_number = self._assign_room(t, "Classroom", room_usage)
                
                if day not in master_schedule:
                    master_schedule[day] = {}
                if slot not in master_schedule[day]:
                    master_schedule[day][slot] = []
                
                class_info = {
                    'subject': subj_details['Subject'],
                    'teacher': subj_details['Teacher'],
                    'course_semester': subj_details['Course_Semester'],
                    'type': 'Tutorial',
                    'room': f"Room-{room_number}",
                    'room_type': 'Classroom',
                    'subject_type': subj_details['Subject_type'],
                    'section': subj_details['Section']
                }
                master_schedule[day][slot].append(class_info)
        
        # Process practicals (2-hour sessions)
        for (subject_id, t), var in self.variables['practical'].items():
            if self.solver.Value(var) == 1:
                day, slot = time_slots[t]
                subj_details = self._get_subject_details(subject_id)
                lab_type = subj_details['Lab_type']
                
                # Assign specific lab room (same lab for both hours)
                lab_number = self._assign_room(t, lab_type, room_usage)
                
                # Add to both consecutive slots
                for offset in [0, 1]:
                    if t + offset < len(time_slots):
                        day_offset, slot_offset = time_slots[t + offset]
                        
                        if day_offset not in master_schedule:
                            master_schedule[day_offset] = {}
                        if slot_offset not in master_schedule[day_offset]:
                            master_schedule[day_offset][slot_offset] = []
                        
                        # Use same lab number for both slots
                        if offset == 1:
                            # Reuse the same lab number from first slot
                            pass
                        
                        class_info = {
                            'subject': subj_details['Subject'],
                            'teacher': subj_details['Teacher'],
                            'course_semester': subj_details['Course_Semester'],
                            'type': 'Practical',
                            'room': f"{lab_type}-{lab_number}",
                            'room_type': lab_type,
                            'subject_type': subj_details['Subject_type'],
                            'section': subj_details['Section'],
                            'is_continuation': offset == 1  # Mark second hour
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
            total_rooms = Config.ROOM_CAPACITIES["Classroom"]["count"]
        else:
            total_rooms = Config.ROOM_CAPACITIES[room_type]["count"]
        
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
            if f"{subj['Course_Semester']}_{subj['Subject']}" == subject_id:
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
        """Print solution summary statistics"""
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
        
        # Teacher workload analysis
        print(f"\n   👨‍🏫 Teacher Workload:")
        teacher_loads = {}
        for subj in self.subjects:
            teacher = subj["Teacher"]
            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
            
            if teacher not in teacher_loads:
                teacher_loads[teacher] = 0
            
            for t in range(len(self.solution['time_slots'])):
                if (subject_id, t) in self.variables['lecture']:
                    if self.solver.Value(self.variables['lecture'][(subject_id, t)]) == 1:
                        teacher_loads[teacher] += 1
                
                if (subject_id, t) in self.variables['tutorial']:
                    if self.solver.Value(self.variables['tutorial'][(subject_id, t)]) == 1:
                        teacher_loads[teacher] += 1
                
                if (subject_id, t) in self.variables['practical']:
                    if self.solver.Value(self.variables['practical'][(subject_id, t)]) == 1:
                        teacher_loads[teacher] += 2
        
        for teacher, hours in sorted(teacher_loads.items()):
            status_icon = "✅" if hours <= Config.MAX_HOURS_PER_TEACHER else "⚠️"
            print(f"      {status_icon} {teacher}: {hours}/{Config.MAX_HOURS_PER_TEACHER} hours")
        
        # Room utilization
        print(f"\n   🏢 Room Utilization:")
        room_usage = {}
        for day_schedule in self.solution['master_schedule'].values():
            for slot_classes in day_schedule.values():
                for class_info in slot_classes:
                    room = class_info['room']
                    room_usage[room] = room_usage.get(room, 0) + 1
        
        for room in sorted(room_usage.keys(), key=lambda x: (x.split('-')[0], int(x.split('-')[1]) if len(x.split('-')) > 1 else 0)):
            print(f"      {room}: {room_usage[room]} slot-hours used")
        
        print("=" * 70)