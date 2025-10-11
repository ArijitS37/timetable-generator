"""
Configuration settings for the timetable generator
"""
from typing import List

class Config:
    # Time slots configuration
    DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    START_HOUR = 8
    END_HOUR = 17
    
    # Generate time slots
    @classmethod
    def get_time_slots(cls):
        slots = [f"{h}:30-{h+1}:30" for h in range(cls.START_HOUR, cls.END_HOUR)]
        return [(d, s) for d in cls.DAYS for s in slots]
    
    @classmethod
    def get_slots_list(cls):
        return [f"{h}:30-{h+1}:30" for h in range(cls.START_HOUR, cls.END_HOUR)]
    
    # Valid semester types
    ODD_SEMESTERS = [1, 3, 5, 7]
    EVEN_SEMESTERS = [2, 4, 6, 8]
    
    # Valid subject types
    SUBJECT_TYPES = ["DSC", "DSE", "GE", "SEC", "VAC", "AEC"]
    
    # Subject types with fixed slots
    FIXED_SLOT_TYPES = ["GE", "SEC", "VAC", "AEC"]
    
    # Subject types by year (CORRECTED)
    YEAR1_SUBJECTS = ["DSC", "GE", "SEC", "VAC", "AEC"]  # Sem 1,2
    YEAR2_SUBJECTS = ["DSC", "DSE", "GE", "SEC", "VAC", "AEC"]  # Sem 3,4
    YEAR3_SUBJECTS = ["DSC", "DSE", "GE", "SEC"]  # Sem 5,6 - NO VAC, AEC
    YEAR4_SUBJECTS = ["DSC", "DSE", "GE"]  # Sem 7,8 - NO SEC, VAC, AEC
    
    @classmethod
    def get_allowed_subject_types_for_semester(cls, semester: int) -> List[str]:
        """Get allowed subject types for a given semester"""
        if semester in [1, 2]:
            return cls.YEAR1_SUBJECTS
        elif semester in [3, 4]:
            return cls.YEAR2_SUBJECTS
        elif semester in [5, 6]:
            return cls.YEAR3_SUBJECTS
        elif semester in [7, 8]:
            return cls.YEAR4_SUBJECTS
        return []
    
    @classmethod
    def get_fixed_slot_types_for_semester(cls, semester: int) -> List[str]:
        """Get which fixed slot types apply to a given semester"""
        allowed_types = cls.get_allowed_subject_types_for_semester(semester)
        return [t for t in cls.FIXED_SLOT_TYPES if t in allowed_types]
    
    # Fixed slot configurations (UPDATED WITH AEC SATURDAY)
    FIXED_SLOTS = {
        "GE": {
            "slots": ["12:30-13:30"],
            "days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            "description": "Generic Electives (12:30-1:30 all days)"
        },
        "SEC": {
            "slots": ["13:30-14:30", "14:30-15:30"],
            "days": ["Fri"],
            "description": "Skill Enhancement Courses (Friday 1:30-3:30)"
        },
        "SEC_SAT": {
            "slots": ["8:30-9:30", "9:30-10:30"],
            "days": ["Sat"], 
            "description": "Skill Enhancement Courses (Saturday 8:30-10:30)"
        },
        "VAC": {
            "slots": ["15:30-16:30", "16:30-17:30"],
            "days": ["Fri"],
            "description": "Value Addition Courses (Friday 3:30-5:30)"
        },
        "VAC_SAT": {
            "slots": ["10:30-11:30", "11:30-12:30"],
            "days": ["Sat"],
            "description": "Value Addition Courses (Saturday 10:30-12:30)"
        },
        "AEC": {
            "slots": ["12:30-13:30"],
            "days": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "description": "Ability Enhancement Courses (Mon-Fri 12:30-1:30)"
        },
        "AEC_SAT": {
            "slots": ["13:30-14:30", "14:30-15:30"],
            "days": ["Sat"],
            "description": "Ability Enhancement Courses (Saturday 1:30-3:30)"
        }
    }
    
    # Course sections configuration (predefined)
    COURSE_SECTIONS = {
        # B.Sc. Courses
        "B.Sc. (Hons.) Chemistry": {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 1, 8: 1},
        "B.Sc. (Hons) Computer Science": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.Sc. (Hons) Electronics": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.Sc. (Hons.) Mathematics": {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2},
        "B.Sc. (Hons.) Physics": {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2},
        "B.Sc. Physical science Industrial Chemistry": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.Sc. Physical Science Chemistry": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.Sc. Physical Science Electronics": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.Sc. Physical Science Computer Science": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        
        # B.A. Courses
        "B.A. (Hons.) Economics": {1: 2, 2: 2, 3: 2, 4: 2, 5: 2, 6: 2, 7: 2, 8: 2},
        "B.A. (Hons.) English": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.A. (Hons.) Hindi": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.A. (Hons.) History": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.A. (Hons.) Political Science": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        "B.A. Program": {1: 1, 2: 1, 3: 1, 4: 1, 5: 1, 6: 1, 7: 1, 8: 1},
        
        # B.Com Courses
        "B.Com (Hons)": {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3},
        "B.Com": {1: 3, 2: 3, 3: 3, 4: 3, 5: 3, 6: 3, 7: 3, 8: 3},
    }
    
    @classmethod
    def get_section_letters(cls, num_sections):
        """Get section letters (A, B, C, etc.) based on number"""
        return [chr(65 + i) for i in range(num_sections)]  # 65 is ASCII for 'A'
    
    # Department-to-Lab mapping
    DEPARTMENT_LABS = {
        "Physics": "Lab-Physics",
        "Chemistry": "Lab-Chemistry",
        "Biology": "Lab-Biology",
        "Electronics": "Lab-Electronics",
        "Computer Science": "Lab-CS",
        "CS": "Lab-CS",
    }
    
    # Room capacities (predefined)
    ROOM_CAPACITIES = {
        "Classroom": {
            "count": 15,
            "capacity": 60,
            "overflow_allowed": 10  # Can exceed by 10 students
        },
        "Lab-Physics": {
            "count": 2,
            "capacity": 30,
            "overflow_allowed": 10
        },
        "Lab-Chemistry": {
            "count": 2,
            "capacity": 30,
            "overflow_allowed": 10
        },
        "Lab-Biology": {
            "count": 1,
            "capacity": 30,
            "overflow_allowed": 10
        },
        "Lab-Electronics": {
            "count": 2,
            "capacity": 30,
            "overflow_allowed": 10
        },
        "Lab-CS": {
            "count": 3,
            "capacity": 30,
            "overflow_allowed": 10
        },
    }
    
    # Students per course-section (predefined - approximate)
    STUDENTS_PER_SECTION = 50  # Default, can be overridden
    
    @classmethod
    def get_fixed_slot_indices(cls, course_type):
        """Get time slot indices for a specific course type"""
        time_slots = cls.get_time_slots()
        indices = []
        
        # Handle SEC, VAC, AEC which have multiple entries (including Saturday)
        if course_type == "SEC":
            for config_key in ["SEC", "SEC_SAT"]:
                if config_key in cls.FIXED_SLOTS:
                    config = cls.FIXED_SLOTS[config_key]
                    for i, (day, slot) in enumerate(time_slots):
                        if day in config["days"] and slot in config["slots"]:
                            indices.append(i)
        elif course_type == "VAC":
            for config_key in ["VAC", "VAC_SAT"]:
                if config_key in cls.FIXED_SLOTS:
                    config = cls.FIXED_SLOTS[config_key]
                    for i, (day, slot) in enumerate(time_slots):
                        if day in config["days"] and slot in config["slots"]:
                            indices.append(i)
        elif course_type == "AEC":
            for config_key in ["AEC", "AEC_SAT"]:
                if config_key in cls.FIXED_SLOTS:
                    config = cls.FIXED_SLOTS[config_key]
                    for i, (day, slot) in enumerate(time_slots):
                        if day in config["days"] and slot in config["slots"]:
                            indices.append(i)
        elif course_type in cls.FIXED_SLOTS:
            config = cls.FIXED_SLOTS[course_type]
            for i, (day, slot) in enumerate(time_slots):
                if day in config["days"] and slot in config["slots"]:
                    indices.append(i)
        
        return indices
    
    @classmethod
    def get_all_fixed_slot_indices(cls):
        """Get all fixed slot indices"""
        all_indices = set()
        for course_type in ["GE", "SEC", "VAC", "AEC"]:
            all_indices.update(cls.get_fixed_slot_indices(course_type))
        return list(all_indices)
    
    # Constraint settings
    MAX_HOURS_PER_TEACHER = 16
    SOLVER_TIME_LIMIT = 300  # Increased to 5 minutes
    
    # PDF settings
    PDF_FONT_SIZE = 6
    PDF_HEADER_COLOR = (0.4, 0.4, 0.4)
    PDF_ALT_ROW_COLOR = (0.9, 0.9, 0.9)
    
    # Available constraints (user-configurable)
    USER_CONFIGURABLE_CONSTRAINTS = {
        "practical_consecutive": "Ensure practical sessions occupy consecutive 2-hour slots",
        "max_consecutive_classes": "Limit maximum consecutive classes for students and teachers",
        "max_daily_hours": "Limit maximum hours per day for students (default: 6 hours)",
        "max_daily_teacher_hours": "Limit maximum teaching hours per day for teachers (default: 5-6 hours)",
        "early_completion": "Soft constraint to end classes as early as possible"
    }
    
    # Core constraints (always enabled, not asked to user)
    CORE_CONSTRAINTS = [
        "teacher_clash",
        "room_clash", 
        "course_semester_clash",
        "teacher_load",
        "hour_requirements",
        "fixed_slots"
    ]