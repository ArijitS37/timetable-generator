"""
Interactive constraint selection module
"""
from src.config import Config
from typing import Dict

class ConstraintSelector:
    def __init__(self):
        self.selected_constraints = {}
        self.max_consecutive_hours = 3
        self.max_daily_hours_students = 6
        self.max_daily_hours_teachers = 6
        
    def select_constraints(self) -> Dict[str, bool]:
        """Interactive constraint selection"""
        print("\n🔧 CONSTRAINT CONFIGURATION")
        print("=" * 70)
        print("\n✅ CORE CONSTRAINTS (Always Enabled):")
        print("   • Teacher Clash Prevention")
        print("   • Room Clash Prevention")
        print("   • Course-Semester Clash Prevention")
        print("   • Teacher Weekly Load Limit (16 hours/week)")
        print("   • Subject Hour Requirements")
        print("   • Fixed Time Slots for GE/SEC/VAC/AEC")
        
        print("\n" + "=" * 70)
        print("📋 OPTIONAL CONSTRAINTS")
        print("=" * 70)
        print("Configure the following optional constraints:")
        print()
        
        # 1. Practical Consecutive
        print("📌 1. Practical Consecutive Slots")
        print("   Ensures practical sessions occupy 2 consecutive hours")
        while True:
            choice = input("   Enable? (y/n) [y]: ").strip().lower()
            if choice == "" or choice == "y":
                self.selected_constraints["practical_consecutive"] = True
                print("   ✅ ENABLED\n")
                break
            elif choice == "n":
                self.selected_constraints["practical_consecutive"] = False
                print("   ❌ DISABLED\n")
                break
            else:
                print("   Invalid input. Please enter 'y' or 'n'")
        
        # 2. Max Consecutive Classes
        print("📌 2. Maximum Consecutive Classes")
        print("   Limits how many hours students/teachers can have without break")
        while True:
            choice = input("   Enable? (y/n) [y]: ").strip().lower()
            if choice == "" or choice == "y":
                self.selected_constraints["max_consecutive_classes"] = True
                print("   ✅ ENABLED")
                
                # Ask for the limit
                while True:
                    try:
                        max_hours = input("   Enter maximum consecutive hours [3]: ").strip()
                        if max_hours == "":
                            self.max_consecutive_hours = 3
                            break
                        else:
                            val = int(max_hours)
                            if 1 <= val <= 6:
                                self.max_consecutive_hours = val
                                break
                            else:
                                print("   ❌ Must be between 1 and 6")
                    except ValueError:
                        print("   ❌ Invalid number")
                
                print(f"   → Max consecutive hours set to: {self.max_consecutive_hours}\n")
                break
            elif choice == "n":
                self.selected_constraints["max_consecutive_classes"] = False
                print("   ❌ DISABLED\n")
                break
            else:
                print("   Invalid input. Please enter 'y' or 'n'")
        
        # 3. Max Daily Hours for Students
        print("📌 3. Maximum Daily Hours for Students")
        print("   Limits total class hours per day for students")
        while True:
            choice = input("   Enable? (y/n) [y]: ").strip().lower()
            if choice == "" or choice == "y":
                self.selected_constraints["max_daily_hours"] = True
                print("   ✅ ENABLED")
                
                # Ask for the limit
                while True:
                    try:
                        max_hours = input("   Enter maximum hours per day [6]: ").strip()
                        if max_hours == "":
                            self.max_daily_hours_students = 6
                            break
                        else:
                            val = int(max_hours)
                            if 1 <= val <= 9:
                                self.max_daily_hours_students = val
                                break
                            else:
                                print("   ❌ Must be between 1 and 9")
                    except ValueError:
                        print("   ❌ Invalid number")
                
                print(f"   → Max daily hours for students: {self.max_daily_hours_students}\n")
                break
            elif choice == "n":
                self.selected_constraints["max_daily_hours"] = False
                print("   ❌ DISABLED\n")
                break
            else:
                print("   Invalid input. Please enter 'y' or 'n'")
        
        # 4. Max Daily Hours for Teachers
        print("📌 4. Maximum Daily Teaching Hours for Teachers")
        print("   Limits total teaching hours per day for teachers")
        while True:
            choice = input("   Enable? (y/n) [y]: ").strip().lower()
            if choice == "" or choice == "y":
                self.selected_constraints["max_daily_teacher_hours"] = True
                print("   ✅ ENABLED")
                
                # Ask for the limit
                while True:
                    try:
                        max_hours = input("   Enter maximum hours per day [6]: ").strip()
                        if max_hours == "":
                            self.max_daily_hours_teachers = 6
                            break
                        else:
                            val = int(max_hours)
                            if 1 <= val <= 9:
                                self.max_daily_hours_teachers = val
                                break
                            else:
                                print("   ❌ Must be between 1 and 9")
                    except ValueError:
                        print("   ❌ Invalid number")
                
                print(f"   → Max daily hours for teachers: {self.max_daily_hours_teachers}\n")
                break
            elif choice == "n":
                self.selected_constraints["max_daily_teacher_hours"] = False
                print("   ❌ DISABLED\n")
                break
            else:
                print("   Invalid input. Please enter 'y' or 'n'")
        
        # 5. Early Completion
        print("📌 5. Early Completion Optimization")
        print("   Tries to schedule classes earlier in the day")
        while True:
            choice = input("   Enable? (y/n) [y]: ").strip().lower()
            if choice == "" or choice == "y":
                self.selected_constraints["early_completion"] = True
                print("   ✅ ENABLED\n")
                break
            elif choice == "n":
                self.selected_constraints["early_completion"] = False
                print("   ❌ DISABLED\n")
                break
            else:
                print("   Invalid input. Please enter 'y' or 'n'")
        
        # Summary
        print("=" * 70)
        print("📋 CONFIGURATION SUMMARY:")
        print("=" * 70)
        
        print("\n✅ Core Constraints: Always Enabled")
        
        print("\n📊 Optional Constraints:")
        for key, enabled in self.selected_constraints.items():
            status = "✅ ENABLED" if enabled else "❌ DISABLED"
            constraint_name = key.replace('_', ' ').title()
            print(f"   {status}: {constraint_name}")
            
            if enabled:
                if key == "max_consecutive_classes":
                    print(f"      → Limit: {self.max_consecutive_hours} hours")
                elif key == "max_daily_hours":
                    print(f"      → Limit: {self.max_daily_hours_students} hours/day")
                elif key == "max_daily_teacher_hours":
                    print(f"      → Limit: {self.max_daily_hours_teachers} hours/day")
        
        print("\n" + "=" * 70)
        
        # Confirmation
        while True:
            confirm = input("\nProceed with this configuration? (y/n) [y]: ").strip().lower()
            if confirm == "" or confirm == "y":
                return self.selected_constraints
            elif confirm == "n":
                print("\n🔄 Restarting constraint configuration...\n")
                return self.select_constraints()
            else:
                print("Invalid input. Please enter 'y' or 'n'")
    
    def is_enabled(self, constraint_key: str) -> bool:
        """Check if a constraint is enabled"""
        # Core constraints are always enabled
        if constraint_key in Config.CORE_CONSTRAINTS:
            return True
        return self.selected_constraints.get(constraint_key, True)
    
    def get_max_consecutive_hours(self) -> int:
        """Get maximum consecutive hours setting"""
        return self.max_consecutive_hours
    
    def get_max_daily_hours_students(self) -> int:
        """Get maximum daily hours for students"""
        return self.max_daily_hours_students
    
    def get_max_daily_hours_teachers(self) -> int:
        """Get maximum daily hours for teachers"""
        return self.max_daily_hours_teachers