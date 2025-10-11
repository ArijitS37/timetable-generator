"""
Constraint building module - COMPLETELY UPDATED with new constraints
"""
from ortools.sat.python import cp_model
from src.config import Config
from src.constraint_selector import ConstraintSelector
from typing import List, Dict, Any, Tuple
import pandas as pd

class ConstraintBuilder:
    def __init__(self, subjects: List[Dict], teachers: List[str], rooms: List[str], 
                 course_semesters: List[str], room_capacities: Dict[str, Dict],
                 constraint_selector: ConstraintSelector):
        self.subjects = subjects
        self.teachers = teachers
        self.rooms = rooms
        self.course_semesters = course_semesters
        self.room_capacities = room_capacities
        self.constraint_selector = constraint_selector
        self.time_slots = Config.get_time_slots()
        self.slots = Config.get_slots_list()
        
    def build_model(self) -> Tuple[cp_model.CpModel, Dict]:
        """Build the complete CP-SAT model with selected constraints"""
        model = cp_model.CpModel()
        
        print("\n🔧 Building optimization model...")
        
        # Create decision variables
        variables = self._create_variables(model)
        
        # CORE CONSTRAINTS (always enabled)
        print("   ✅ Adding core constraints...")
        self._add_hour_requirements(model, variables)
        self._add_teacher_clash(model, variables)
        self._add_room_clash(model, variables)
        self._add_course_semester_clash(model, variables)
        self._add_teacher_load(model, variables)
        self._add_fixed_slots(model, variables)
        
        # OPTIONAL CONSTRAINTS (user-configured)
        if self.constraint_selector.is_enabled("practical_consecutive"):
            print("   ✅ Adding practical consecutive slot constraints")
            self._add_practical_consecutive(model, variables)
        
        if self.constraint_selector.is_enabled("max_consecutive_classes"):
            print(f"   ✅ Adding max consecutive classes constraint ({self.constraint_selector.get_max_consecutive_hours()}h)")
            self._add_max_consecutive_classes(model, variables)
        
        if self.constraint_selector.is_enabled("max_daily_hours"):
            print(f"   ✅ Adding max daily hours for students ({self.constraint_selector.get_max_daily_hours_students()}h)")
            self._add_max_daily_hours_students(model, variables)
        
        if self.constraint_selector.is_enabled("max_daily_teacher_hours"):
            print(f"   ✅ Adding max daily hours for teachers ({self.constraint_selector.get_max_daily_hours_teachers()}h)")
            self._add_max_daily_hours_teachers(model, variables)
        
        if self.constraint_selector.is_enabled("early_completion"):
            print("   ✅ Adding early completion objective")
            self._add_early_completion_objective(model, variables)
        
        print("✅ Model built successfully")
        return model, variables
    
    def _create_variables(self, model: cp_model.CpModel) -> Dict:
        """Create all decision variables"""
        variables = {
            'lecture': {},
            'tutorial': {},
            'practical': {},
            'tutorial_used': {},  # Track if tutorial is used (for flexibility)
            'max_used_slot': model.NewIntVar(0, len(self.time_slots) - 1, "max_used_slot")
        }
        
        for subj in self.subjects:
            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
            
            # Lecture variables
            if subj["Lecture_hours"] > 0:
                for t in range(len(self.time_slots)):
                    variables['lecture'][(subject_id, t)] = model.NewBoolVar(f"lec_{subject_id}_{t}")
            
            # Tutorial variables (with flexibility tracking)
            if subj["Tutorial_hours"] > 0:
                for t in range(len(self.time_slots)):
                    variables['tutorial'][(subject_id, t)] = model.NewBoolVar(f"tut_{subject_id}_{t}")
                
                # Track if tutorials are actually scheduled (can be sacrificed)
                variables['tutorial_used'][subject_id] = model.NewBoolVar(f"tut_used_{subject_id}")
            
            # Practical variables
            if subj["Practical_hours"] > 0:
                for day_idx in range(len(Config.DAYS)):
                    for slot_idx in range(len(self.slots) - 1):
                        t = day_idx * len(self.slots) + slot_idx
                        variables['practical'][(subject_id, t)] = model.NewBoolVar(f"prac_{subject_id}_{t}")
        
        print(f"   📊 Variables: {len(variables['lecture'])} lec, {len(variables['tutorial'])} tut, {len(variables['practical'])} prac")
        return variables
    
    def _add_hour_requirements(self, model: cp_model.CpModel, variables: Dict):
        """Each subject must get required hours (tutorials are flexible)"""
        for subj in self.subjects:
            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
            
            # Lectures (mandatory)
            if subj["Lecture_hours"] > 0:
                model.Add(
                    sum(variables['lecture'][(subject_id, t)] for t in range(len(self.time_slots))) 
                    == subj["Lecture_hours"]
                )
            
            # Tutorials (flexible - can be 0 or full requirement)
            if subj["Tutorial_hours"] > 0:
                tutorial_count = sum(variables['tutorial'][(subject_id, t)] for t in range(len(self.time_slots)))
                
                # If tutorial_used is True, must meet full requirement
                model.Add(tutorial_count == subj["Tutorial_hours"]).OnlyEnforceIf(variables['tutorial_used'][subject_id])
                # If tutorial_used is False, must be 0
                model.Add(tutorial_count == 0).OnlyEnforceIf(variables['tutorial_used'][subject_id].Not())
            
            # Practicals (mandatory)
            if subj["Practical_hours"] > 0:
                num_practical_sessions = subj["Practical_hours"] // 2
                practical_vars = [
                    variables['practical'][(subject_id, t)] 
                    for t in range(len(self.time_slots))
                    if (subject_id, t) in variables['practical']
                ]
                if practical_vars:
                    model.Add(sum(practical_vars) == num_practical_sessions)
    
    def _add_teacher_clash(self, model: cp_model.CpModel, variables: Dict):
        """Teacher cannot teach multiple classes at same time"""
        for t in range(len(self.time_slots)):
            for teacher in self.teachers:
                classes_at_t = []
                
                for subj in self.subjects:
                    if subj["Teacher"] == teacher:
                        subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                        
                        if (subject_id, t) in variables['lecture']:
                            classes_at_t.append(variables['lecture'][(subject_id, t)])
                        
                        if (subject_id, t) in variables['tutorial']:
                            classes_at_t.append(variables['tutorial'][(subject_id, t)])
                        
                        if (subject_id, t) in variables['practical']:
                            classes_at_t.append(variables['practical'][(subject_id, t)])
                        
                        if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                            classes_at_t.append(variables['practical'][(subject_id, t-1)])
                
                if classes_at_t:
                    model.Add(sum(classes_at_t) <= 1)
    
    def _add_room_clash(self, model: cp_model.CpModel, variables: Dict):
        """Room cannot host more classes than capacity (with overflow)"""
        for t in range(len(self.time_slots)):
            # Classroom usage
            classroom_usage = []
            for subj in self.subjects:
                subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                if (subject_id, t) in variables['lecture']:
                    classroom_usage.append(variables['lecture'][(subject_id, t)])
                if (subject_id, t) in variables['tutorial']:
                    classroom_usage.append(variables['tutorial'][(subject_id, t)])
            
            if classroom_usage:
                classroom_capacity = self.room_capacities['Classroom']['count']
                model.Add(sum(classroom_usage) <= classroom_capacity)
            
            # Lab usage (per lab type)
            for room_type, room_info in self.room_capacities.items():
                if room_type != "Classroom":
                    lab_usage = []
                    for subj in self.subjects:
                        if subj["Lab_type"] == room_type:
                            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                            
                            if (subject_id, t) in variables['practical']:
                                lab_usage.append(variables['practical'][(subject_id, t)])
                            
                            if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                                lab_usage.append(variables['practical'][(subject_id, t-1)])
                    
                    if lab_usage:
                        model.Add(sum(lab_usage) <= room_info['count'])
    
    def _add_course_semester_clash(self, model: cp_model.CpModel, variables: Dict):
        """Course-semester cannot have multiple classes at same time"""
        for t in range(len(self.time_slots)):
            for course_sem in self.course_semesters:
                classes_at_t = []
                
                for subj in self.subjects:
                    if subj["Course_Semester"] == course_sem:
                        subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                        
                        if (subject_id, t) in variables['lecture']:
                            classes_at_t.append(variables['lecture'][(subject_id, t)])
                        
                        if (subject_id, t) in variables['tutorial']:
                            classes_at_t.append(variables['tutorial'][(subject_id, t)])
                        
                        if (subject_id, t) in variables['practical']:
                            classes_at_t.append(variables['practical'][(subject_id, t)])
                        
                        if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                            classes_at_t.append(variables['practical'][(subject_id, t-1)])
                
                if classes_at_t:
                    model.Add(sum(classes_at_t) <= 1)
    
    def _add_teacher_load(self, model: cp_model.CpModel, variables: Dict):
        """Limit total hours per teacher per week"""
        for teacher in self.teachers:
            total_hours = []
            
            for subj in self.subjects:
                if subj["Teacher"] == teacher:
                    subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                    
                    for t in range(len(self.time_slots)):
                        if (subject_id, t) in variables['lecture']:
                            total_hours.append(variables['lecture'][(subject_id, t)])
                        
                        if (subject_id, t) in variables['tutorial']:
                            total_hours.append(variables['tutorial'][(subject_id, t)])
                        
                        if (subject_id, t) in variables['practical']:
                            total_hours.append(variables['practical'][(subject_id, t)] * 2)
            
            if total_hours:
                model.Add(sum(total_hours) <= Config.MAX_HOURS_PER_TEACHER)
    
    def _add_fixed_slots(self, model: cp_model.CpModel, variables: Dict):
        """Enforce fixed time slots for GE/SEC/VAC/AEC and STRICTLY block others"""
        # Get all fixed slot indices
        all_fixed_indices = set(Config.get_all_fixed_slot_indices())
        
        print(f"      → Total fixed slot indices: {len(all_fixed_indices)}")
        
        for subj in self.subjects:
            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
            subject_type = subj["Subject_type"]
            semester = subj["Semester"]
            
            # Get which fixed slot types apply to this semester
            semester_fixed_types = Config.get_fixed_slot_types_for_semester(semester)
            
            if subject_type in Config.FIXED_SLOT_TYPES:
                # This is a GE/SEC/VAC/AEC subject
                # It can ONLY be scheduled in its specific fixed slots
                allowed_slots = set(Config.get_fixed_slot_indices(subject_type))
                
                print(f"      → {subject_type} subject '{subj['Subject']}' limited to {len(allowed_slots)} slots")
                
                # Block all other slots
                for t in range(len(self.time_slots)):
                    if t not in allowed_slots:
                        if (subject_id, t) in variables['lecture']:
                            model.Add(variables['lecture'][(subject_id, t)] == 0)
                        if (subject_id, t) in variables['tutorial']:
                            model.Add(variables['tutorial'][(subject_id, t)] == 0)
                        # Practicals for GE/SEC/VAC/AEC are rare but handle them
                        if (subject_id, t) in variables['practical']:
                            model.Add(variables['practical'][(subject_id, t)] == 0)
            else:
                # This is a regular DSC/DSE subject
                # STRICTLY block ALL fixed slots that apply to this semester
                
                # Get slots that are fixed for THIS semester's allowed types
                blocked_slots = set()
                for fixed_type in semester_fixed_types:
                    blocked_slots.update(Config.get_fixed_slot_indices(fixed_type))
                
                # Block lectures and tutorials from ALL blocked slots
                for t in blocked_slots:
                    if (subject_id, t) in variables['lecture']:
                        model.Add(variables['lecture'][(subject_id, t)] == 0)
                    if (subject_id, t) in variables['tutorial']:
                        model.Add(variables['tutorial'][(subject_id, t)] == 0)
                
                # For practicals, block if EITHER slot (t or t+1) is in fixed slots
                for t in range(len(self.time_slots)):
                    if (subject_id, t) in variables['practical']:
                        # Check if practical starting at t would occupy any fixed slot
                        if t in blocked_slots or (t + 1) in blocked_slots:
                            model.Add(variables['practical'][(subject_id, t)] == 0)
    
    def _add_practical_consecutive(self, model: cp_model.CpModel, variables: Dict):
        """Practical sessions must occupy 2 consecutive slots"""
        for subj in self.subjects:
            if subj["Practical_hours"] > 0:
                subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                
                for t in range(len(self.time_slots)):
                    if (subject_id, t) in variables['practical']:
                        if t >= len(self.time_slots) - 1 or not self._is_consecutive_slot(t + 1):
                            model.Add(variables['practical'][(subject_id, t)] == 0)
    
    def _add_max_consecutive_classes(self, model: cp_model.CpModel, variables: Dict):
        """Limit maximum consecutive classes for students and teachers"""
        max_consecutive = self.constraint_selector.get_max_consecutive_hours()
        
        # For each course-semester (students)
        for course_sem in self.course_semesters:
            for day_idx in range(len(Config.DAYS)):
                for start_slot in range(len(self.slots) - max_consecutive):
                    consecutive_classes = []
                    
                    for offset in range(max_consecutive + 1):
                        t = day_idx * len(self.slots) + start_slot + offset
                        
                        for subj in self.subjects:
                            if subj["Course_Semester"] == course_sem:
                                subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                                
                                if (subject_id, t) in variables['lecture']:
                                    consecutive_classes.append(variables['lecture'][(subject_id, t)])
                                if (subject_id, t) in variables['tutorial']:
                                    consecutive_classes.append(variables['tutorial'][(subject_id, t)])
                                if (subject_id, t) in variables['practical']:
                                    consecutive_classes.append(variables['practical'][(subject_id, t)])
                                if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                                    consecutive_classes.append(variables['practical'][(subject_id, t-1)])
                    
                    if consecutive_classes:
                        model.Add(sum(consecutive_classes) <= max_consecutive)
        
        # For each teacher
        for teacher in self.teachers:
            for day_idx in range(len(Config.DAYS)):
                for start_slot in range(len(self.slots) - max_consecutive):
                    consecutive_classes = []
                    
                    for offset in range(max_consecutive + 1):
                        t = day_idx * len(self.slots) + start_slot + offset
                        
                        for subj in self.subjects:
                            if subj["Teacher"] == teacher:
                                subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                                
                                if (subject_id, t) in variables['lecture']:
                                    consecutive_classes.append(variables['lecture'][(subject_id, t)])
                                if (subject_id, t) in variables['tutorial']:
                                    consecutive_classes.append(variables['tutorial'][(subject_id, t)])
                                if (subject_id, t) in variables['practical']:
                                    consecutive_classes.append(variables['practical'][(subject_id, t)])
                                if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                                    consecutive_classes.append(variables['practical'][(subject_id, t-1)])
                    
                    if consecutive_classes:
                        model.Add(sum(consecutive_classes) <= max_consecutive)
    
    def _add_max_daily_hours_students(self, model: cp_model.CpModel, variables: Dict):
        """Limit maximum hours per day for students"""
        max_hours = self.constraint_selector.get_max_daily_hours_students()
        
        for course_sem in self.course_semesters:
            for day_idx in range(len(Config.DAYS)):
                daily_hours = []
                
                for slot_idx in range(len(self.slots)):
                    t = day_idx * len(self.slots) + slot_idx
                    
                    for subj in self.subjects:
                        if subj["Course_Semester"] == course_sem:
                            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                            
                            if (subject_id, t) in variables['lecture']:
                                daily_hours.append(variables['lecture'][(subject_id, t)])
                            if (subject_id, t) in variables['tutorial']:
                                daily_hours.append(variables['tutorial'][(subject_id, t)])
                            if (subject_id, t) in variables['practical']:
                                daily_hours.append(variables['practical'][(subject_id, t)])
                            if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                                daily_hours.append(variables['practical'][(subject_id, t-1)])
                
                if daily_hours:
                    model.Add(sum(daily_hours) <= max_hours)
    
    def _add_max_daily_hours_teachers(self, model: cp_model.CpModel, variables: Dict):
        """Limit maximum teaching hours per day for teachers"""
        max_hours = self.constraint_selector.get_max_daily_hours_teachers()
        
        for teacher in self.teachers:
            for day_idx in range(len(Config.DAYS)):
                daily_hours = []
                
                for slot_idx in range(len(self.slots)):
                    t = day_idx * len(self.slots) + slot_idx
                    
                    for subj in self.subjects:
                        if subj["Teacher"] == teacher:
                            subject_id = f"{subj['Course_Semester']}_{subj['Subject']}"
                            
                            if (subject_id, t) in variables['lecture']:
                                daily_hours.append(variables['lecture'][(subject_id, t)])
                            if (subject_id, t) in variables['tutorial']:
                                daily_hours.append(variables['tutorial'][(subject_id, t)])
                            if (subject_id, t) in variables['practical']:
                                daily_hours.append(variables['practical'][(subject_id, t)])
                            if self._is_consecutive_slot(t) and (subject_id, t-1) in variables['practical']:
                                daily_hours.append(variables['practical'][(subject_id, t-1)])
                
                if daily_hours:
                    model.Add(sum(daily_hours) <= max_hours)
    
    def _add_early_completion_objective(self, model: cp_model.CpModel, variables: Dict):
        """Minimize latest time slot AND prefer earlier days in week (excluding fixed slots)"""
        fixed_indices = set(Config.get_all_fixed_slot_indices())
        
        # Create variables for tracking usage
        day_used = {}  # Track if each day is used
        for day_idx in range(len(Config.DAYS)):
            day_used[day_idx] = model.NewBoolVar(f"day_{day_idx}_used")
        
        # Track latest slot per day
        for t in range(len(self.time_slots)):
            if t not in fixed_indices:
                classes_at_t = []
                
                for subject_id, time in variables['lecture'].keys():
                    if time == t:
                        classes_at_t.append(variables['lecture'][(subject_id, time)])
                
                for subject_id, time in variables['tutorial'].keys():
                    if time == t:
                        classes_at_t.append(variables['tutorial'][(subject_id, time)])
                
                for subject_id, start_time in variables['practical'].keys():
                    if start_time == t or (start_time == t - 1 and self._is_consecutive_slot(t)):
                        classes_at_t.append(variables['practical'][(subject_id, start_time)])
                
                if classes_at_t:
                    has_class = model.NewBoolVar(f"has_class_at_{t}")
                    model.Add(sum(classes_at_t) >= 1).OnlyEnforceIf(has_class)
                    model.Add(sum(classes_at_t) == 0).OnlyEnforceIf(has_class.Not())
                    
                    # If there's a class at t, max_used_slot >= t
                    model.Add(variables['max_used_slot'] >= t).OnlyEnforceIf(has_class)
                    
                    # Track which day is used
                    day_idx = t // len(self.slots)
                    model.Add(day_used[day_idx] == 1).OnlyEnforceIf(has_class)
        
        # Create weighted objective: prefer earlier days + earlier slots
        # Day weights: Mon=0, Tue=1, Wed=2, Thu=3, Fri=4, Sat=5 (multiplied by slots per day)
        day_penalty = sum(
            day_used[day_idx] * day_idx * len(self.slots) * 2  # Higher weight for later days
            for day_idx in range(len(Config.DAYS))
        )
        
        # Slot penalty: prefer ending earlier in the day
        slot_penalty = variables['max_used_slot']
        
        # Combined objective: minimize both day usage and latest slot
        model.Minimize(day_penalty + slot_penalty)
    
    def _is_consecutive_slot(self, t: int) -> bool:
        """Check if time slot t is consecutive to t-1 (same day)"""
        if t <= 0:
            return False
        
        day_idx_current = t // len(self.slots)
        slot_idx_current = t % len(self.slots)
        day_idx_prev = (t - 1) // len(self.slots)
        slot_idx_prev = (t - 1) % len(self.slots)
        
        return day_idx_current == day_idx_prev and slot_idx_current == slot_idx_prev + 1