"""
Data loading and validation module - UPDATED
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
from src.config import Config

class DataLoader:
    def __init__(self, excel_file: str):
        self.excel_file = excel_file
        self.df = None
        self.subjects = []
        self.semester_type = None  # 'odd' or 'even'
        
    def load_data(self) -> bool:
        """Load data from Excel file"""
        try:
            self.df = pd.read_excel(self.excel_file)
            print(f"✅ Loaded {len(self.df)} rows from {self.excel_file}")
            return True
        except Exception as e:
            print(f"❌ Error loading data: {e}")
            return False
    
    def validate_data(self) -> bool:
        """Validate the loaded data"""
        if not self.load_data():
            return False
        
        # Check required columns
        required_columns = [
            "Course", "Semester", "Subject", "Teacher", 
            "Subject Hour Requirements(Le,Tu,Pr)", "Department", "Subject_type"
        ]
        missing_columns = [col for col in required_columns if col not in self.df.columns]
        
        if missing_columns:
            print(f"❌ Missing required columns: {missing_columns}")
            return False
        
        # Validate semester type
        if not self._validate_semester_type():
            return False
        
        # Validate each row
        for idx, row in self.df.iterrows():
            if not self._validate_row(idx, row):
                return False
        
        # Parse hour requirements and expand sections
        self._parse_and_expand_subjects()
        
        print("✅ Data validation passed")
        return True
    
    def _validate_semester_type(self) -> bool:
        """Ask user for semester type and validate"""
        print("\n📅 Semester Type Selection:")
        print("1. Odd Semester (1, 3, 5, 7)")
        print("2. Even Semester (2, 4, 6, 8)")
        
        while True:
            choice = input("Select semester type (1 or 2): ").strip()
            if choice == "1":
                self.semester_type = "odd"
                valid_semesters = Config.ODD_SEMESTERS
                break
            elif choice == "2":
                self.semester_type = "even"
                valid_semesters = Config.EVEN_SEMESTERS
                break
            else:
                print("❌ Invalid choice. Please enter 1 or 2.")
        
        # Check if all semesters in data match the selected type
        unique_semesters = self.df["Semester"].unique()
        invalid_semesters = [s for s in unique_semesters if s not in valid_semesters]
        
        if invalid_semesters:
            print(f"❌ Invalid semesters found: {invalid_semesters}")
            print(f"   Expected: {valid_semesters}")
            return False
        
        print(f"✅ Semester type: {self.semester_type.upper()} - Valid semesters: {list(unique_semesters)}")
        return True
    
    def _validate_row(self, idx: int, row: pd.Series) -> bool:
        """Validate a single row"""
        row_num = idx + 2  # Excel row number (1-indexed + header)
        
        # Get subject type first
        subject_type_raw = row["Subject_type"]
        if pd.isna(subject_type_raw):
            subject_type = ""
        else:
            subject_type = str(subject_type_raw).strip().upper()
        
        # Validate semester
        if not isinstance(row["Semester"], (int, np.integer)):
            print(f"❌ Row {row_num}: Semester must be a number, got '{row['Semester']}'")
            return False
        
        semester = int(row["Semester"])
        
        # Check for empty values (Course can be empty for GE/SEC/VAC/AEC)
        required_cols = ["Semester", "Subject", "Teacher", "Subject Hour Requirements(Le,Tu,Pr)", "Department"]
        for col in required_cols:
            if pd.isna(row[col]) or str(row[col]).strip() == "":
                print(f"❌ Row {row_num}: Empty value in column '{col}'")
                return False
        
        # Course validation - can be empty only for GE/SEC/VAC/AEC
        if pd.isna(row["Course"]) or str(row["Course"]).strip() == "":
            if subject_type not in ["GE", "SEC", "VAC", "AEC"]:
                print(f"❌ Row {row_num}: Course cannot be empty for non-GE/SEC/VAC/AEC subjects")
                print(f"   Subject type: {subject_type if subject_type else 'Not specified (defaults to DSC)'}")
                return False
        
        # Validate hour requirements format
        hour_req = str(row["Subject Hour Requirements(Le,Tu,Pr)"]).strip()
        if not self._validate_hour_format(hour_req):
            print(f"❌ Row {row_num}: Invalid hour format '{hour_req}'. Expected format: 'Le,Tu,Pr' (e.g., '3,1,0' or '3,0,2')")
            return False
        
        # Validate Subject_type
        if not pd.isna(row["Subject_type"]):
            if subject_type not in Config.SUBJECT_TYPES:
                print(f"❌ Row {row_num}: Invalid Subject_type '{subject_type}'. Must be one of: {Config.SUBJECT_TYPES}")
                return False
            
            # Validate subject type is allowed for this semester
            allowed_types = Config.get_allowed_subject_types_for_semester(semester)
            if subject_type not in allowed_types:
                print(f"❌ Row {row_num}: Subject type '{subject_type}' not allowed for Semester {semester}")
                print(f"   Allowed types for Semester {semester}: {allowed_types}")
                return False
        
        # Validate course exists in config (if specified)
        if not pd.isna(row["Course"]) and str(row["Course"]).strip() != "":
            course = str(row["Course"]).strip()
            if course not in Config.COURSE_SECTIONS:
                print(f"❌ Row {row_num}: Course '{course}' not found in system configuration")
                print(f"   Available courses: {list(Config.COURSE_SECTIONS.keys())}")
                return False
            
            # Validate semester for this course
            if semester not in Config.COURSE_SECTIONS[course]:
                print(f"❌ Row {row_num}: Semester {semester} not configured for course '{course}'")
                return False
        
        return True
    
    def _validate_hour_format(self, hour_str: str) -> bool:
        """Validate hour requirement format"""
        try:
            parts = hour_str.split(",")
            if len(parts) != 3:
                return False
            
            for part in parts:
                val = int(part.strip())
                if val < 0:
                    return False
            
            return True
        except:
            return False
    
    def _parse_and_expand_subjects(self):
        """Parse hour requirements and expand subjects into course-section combinations"""
        self.subjects = []
        
        for idx, row in self.df.iterrows():
            hour_req = str(row["Subject Hour Requirements(Le,Tu,Pr)"]).strip()
            le, tu, pr = [int(x.strip()) for x in hour_req.split(",")]
            
            # Practical hours are multiplied by 2
            pr_hours = pr * 2
            
            # Get subject type (handle NaN)
            subject_type_raw = row["Subject_type"]
            if pd.isna(subject_type_raw):
                subject_type = ""
            else:
                subject_type = str(subject_type_raw).strip().upper()
            
            # Normalize names (remove extra spaces, consistent capitalization)
            teacher_name = " ".join(str(row["Teacher"]).strip().split())  # Normalize spaces
            subject_name = " ".join(str(row["Subject"]).strip().split())  # Normalize spaces
            department = str(row["Department"]).strip()
            
            # Determine room type for practicals
            lab_type = Config.DEPARTMENT_LABS.get(department, "Lab-General")
            
            semester = int(row["Semester"])
            
            # Handle GE/SEC/VAC/AEC subjects (no specific course)
            if subject_type in ["GE", "SEC", "VAC", "AEC"]:
                # These are common subjects - create one entry
                subject_data = {
                    "Course": "COMMON",  # Special marker
                    "Semester": semester,
                    "Subject": subject_name,
                    "Teacher": teacher_name,
                    "Department": department,
                    "Subject_type": subject_type,
                    "Lecture_hours": le,
                    "Tutorial_hours": tu,
                    "Practical_hours": pr_hours,
                    "Total_hours": le + tu + pr_hours,
                    "Lab_type": lab_type if pr_hours > 0 else None,
                    "Course_Semester": f"COMMON-Sem{semester}",
                    "Section": "ALL",  # Applies to all sections
                    "Students_count": 0  # Not applicable for common subjects
                }
                self.subjects.append(subject_data)
            else:
                # Regular DSC/DSE subjects - expand by sections
                course = " ".join(str(row["Course"]).strip().split())  # Normalize spaces
                num_sections = Config.COURSE_SECTIONS[course][semester]
                section_letters = Config.get_section_letters(num_sections)
                
                for section in section_letters:
                    subject_data = {
                        "Course": course,
                        "Semester": semester,
                        "Subject": subject_name,
                        "Teacher": teacher_name,
                        "Department": department,
                        "Subject_type": subject_type,
                        "Lecture_hours": le,
                        "Tutorial_hours": tu,
                        "Practical_hours": pr_hours,
                        "Total_hours": le + tu + pr_hours,
                        "Lab_type": lab_type if pr_hours > 0 else None,
                        "Course_Semester": f"{course}-Sem{semester}-{section}",
                        "Section": section,
                        "Students_count": Config.STUDENTS_PER_SECTION
                    }
                    self.subjects.append(subject_data)
        
        print(f"✅ Parsed and expanded to {len(self.subjects)} subject-section combinations")
    
    def get_subjects(self) -> List[Dict[str, Any]]:
        """Get list of subjects"""
        return self.subjects
    
    def get_teachers(self) -> List[str]:
        """Get unique list of teachers"""
        return list(set(subj["Teacher"] for subj in self.subjects))
    
    def get_rooms(self) -> List[str]:
        """Get unique list of room types needed"""
        rooms = {"Classroom"}  # Always need classrooms
        for subj in self.subjects:
            if subj["Lab_type"]:
                rooms.add(subj["Lab_type"])
        return list(rooms)
    
    def get_course_semesters(self) -> List[str]:
        """Get unique list of course-semester combinations"""
        return list(set(subj["Course_Semester"] for subj in self.subjects))
    
    def get_courses(self) -> List[str]:
        """Get unique list of courses"""
        courses = set(subj["Course"] for subj in self.subjects if subj["Course"] != "COMMON")
        return list(courses)
    
    def get_room_capacities(self) -> Dict[str, Dict]:
        """Get predefined room capacities from config"""
        return Config.ROOM_CAPACITIES
    
    def print_data_summary(self):
        """Print summary of loaded data"""
        if not self.subjects:
            print("❌ No data loaded")
            return
        
        print("\n📊 Data Summary:")
        print(f"   Semester Type: {self.semester_type.upper()}")
        print(f"   Total subject-section combinations: {len(self.subjects)}")
        
        # Separate common and course-specific
        common_subjects = [s for s in self.subjects if s["Course"] == "COMMON"]
        course_subjects = [s for s in self.subjects if s["Course"] != "COMMON"]
        
        print(f"   Common subjects (GE/SEC/VAC/AEC): {len(common_subjects)}")
        print(f"   Course-specific subjects: {len(course_subjects)}")
        
        print(f"   Unique courses: {len(self.get_courses())}")
        print(f"   Teachers: {len(self.get_teachers())}")
        print(f"   Room types needed: {self.get_rooms()}")
        
        # Hours breakdown
        total_lecture = sum(s["Lecture_hours"] for s in self.subjects)
        total_tutorial = sum(s["Tutorial_hours"] for s in self.subjects)
        total_practical = sum(s["Practical_hours"] for s in self.subjects)
        
        print(f"\n   📚 Total Hour Requirements:")
        print(f"      Lecture hours: {total_lecture}")
        print(f"      Tutorial hours: {total_tutorial}")
        print(f"      Practical hours: {total_practical}")
        print(f"      Total hours: {total_lecture + total_tutorial + total_practical}")
        
        # Subject type breakdown
        type_counts = {}
        for subj in self.subjects:
            stype = subj["Subject_type"] if subj["Subject_type"] else "DSC/DSE"
            type_counts[stype] = type_counts.get(stype, 0) + 1
        
        print(f"\n   📋 Subject Types:")
        for stype, count in sorted(type_counts.items()):
            print(f"      {stype}: {count} entries")
        
        # Room capacity info
        print(f"\n   🏢 Predefined Room Capacities:")
        for room_type, info in Config.ROOM_CAPACITIES.items():
            print(f"      {room_type}: {info['count']} rooms, {info['capacity']} capacity (+{info['overflow_allowed']} overflow)")