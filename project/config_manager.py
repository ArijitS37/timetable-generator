"""
Professional Configuration Manager for Timetable Generator
Uses YAML for human-readable configuration with validation
"""
import yaml
import os
from pathlib import Path
from typing import Optional, Dict, Any
from src.config import Config

class ConfigManager:
    """Manages application configuration with YAML storage"""
    
    def __init__(self, config_path: str = "config/timetable_config.yml"):
        self.config_path = config_path
        self.config = None
        self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file or create default"""
        config_file = Path(self.config_path)
        
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    self.config = yaml.safe_load(f)
                print(f"✅ Loaded configuration from: {self.config_path}")
                
                # Validate loaded config
                if not self._validate_config():
                    print("⚠️  Invalid configuration detected, using defaults")
                    self.config = self._create_default_config()
                    self.save_config()
                
                return self.config
                
            except Exception as e:
                print(f"⚠️  Error loading config: {e}")
                print("   Creating default configuration...")
                self.config = self._create_default_config()
                self.save_config()
                return self.config
        else:
            print(f"📝 No configuration found at: {self.config_path}")
            print("   Creating default configuration...")
            self.config = self._create_default_config()
            self.save_config()
            return self.config
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default configuration"""
        return {
            'semester': {
                'type': 'odd',  # 'odd' or 'even'
                'valid_odd': [1, 3, 5, 7],
                'valid_even': [2, 4, 6, 8]
            },
            'constraints': {
                'practical_consecutive': True,
                'max_consecutive_classes': True,
                'max_daily_hours': True,
                'max_daily_teacher_hours': True,
                'early_completion': True
            },
            'limits': {
                'max_consecutive_classes': 3,
                'max_daily_hours': 6,
                'max_daily_teacher_hours': 6
            },
            'solver': {
                'time_limit_seconds': 300,
                'max_teacher_hours_per_week': 16
            }
        }
    
    def _validate_config(self) -> bool:
        """Validate configuration structure and values"""
        if not self.config:
            return False
        
        try:
            # Check required sections
            required_sections = ['semester', 'constraints', 'limits']
            for section in required_sections:
                if section not in self.config:
                    print(f"⚠️  Missing section: {section}")
                    return False
            
            # Validate semester type
            semester_type = self.config['semester'].get('type')
            if semester_type not in ['odd', 'even']:
                print(f"⚠️  Invalid semester type: {semester_type}")
                return False
            
            # Validate constraint booleans
            for key, value in self.config['constraints'].items():
                if not isinstance(value, bool):
                    print(f"⚠️  Constraint '{key}' must be True/False")
                    return False
            
            # Validate limits
            limits = self.config['limits']
            if limits.get('max_consecutive_classes', 0) < 1 or limits.get('max_consecutive_classes', 0) > 9:
                print(f"⚠️  max_consecutive_classes must be between 1-9")
                return False
            
            if limits.get('max_daily_hours', 0) < 1 or limits.get('max_daily_hours', 0) > 9:
                print(f"⚠️  max_daily_hours must be between 1-9")
                return False
            
            if limits.get('max_daily_teacher_hours', 0) < 1 or limits.get('max_daily_teacher_hours', 0) > 9:
                print(f"⚠️  max_daily_teacher_hours must be between 1-9")
                return False
            
            return True
            
        except Exception as e:
            print(f"⚠️  Validation error: {e}")
            return False
    
    def save_config(self):
        """Save current configuration to YAML file"""
        config_file = Path(self.config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(config_file, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
            print(f"✅ Configuration saved to: {self.config_path}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def interactive_configure(self):
        """Interactive configuration wizard"""
        print("\n🔧 CONFIGURATION WIZARD")
        print("=" * 70)
        print("This will create/update your timetable configuration.")
        print("Press Enter to keep current/default values shown in [brackets]")
        print()
        
        # Semester Type
        current_semester = self.config['semester']['type']
        print(f"📅 Semester Type")
        print(f"   Current: {current_semester.upper()}")
        print("   1. Odd Semester (1, 3, 5, 7)")
        print("   2. Even Semester (2, 4, 6, 8)")
        
        while True:
            choice = input(f"   Select (1/2) [{1 if current_semester == 'odd' else 2}]: ").strip()
            if choice == "":
                break
            elif choice == "1":
                self.config['semester']['type'] = 'odd'
                break
            elif choice == "2":
                self.config['semester']['type'] = 'even'
                break
            else:
                print("   ❌ Invalid choice. Enter 1 or 2")
        
        print()
        
        # Constraints
        print("🔒 OPTIONAL CONSTRAINTS")
        print("-" * 70)
        
        constraints_info = {
            'practical_consecutive': {
                'name': 'Practical Consecutive Slots',
                'desc': 'Ensures practical sessions occupy 2 consecutive hours'
            },
            'max_consecutive_classes': {
                'name': 'Maximum Consecutive Classes',
                'desc': 'Limits continuous hours without break'
            },
            'max_daily_hours': {
                'name': 'Maximum Daily Hours (Students)',
                'desc': 'Limits total class hours per day for students'
            },
            'max_daily_teacher_hours': {
                'name': 'Maximum Daily Hours (Teachers)',
                'desc': 'Limits teaching hours per day for teachers'
            },
            'early_completion': {
                'name': 'Early Completion Optimization',
                'desc': 'Tries to schedule classes earlier in the day'
            }
        }
        
        for key, info in constraints_info.items():
            current = self.config['constraints'][key]
            print(f"\n📌 {info['name']}")
            print(f"   {info['desc']}")
            print(f"   Current: {'ENABLED' if current else 'DISABLED'}")
            
            while True:
                choice = input(f"   Enable? (y/n) [{'y' if current else 'n'}]: ").strip().lower()
                if choice == "":
                    break
                elif choice in ['y', 'yes']:
                    self.config['constraints'][key] = True
                    break
                elif choice in ['n', 'no']:
                    self.config['constraints'][key] = False
                    break
                else:
                    print("   ❌ Invalid input. Enter 'y' or 'n'")
            
            # Ask for limits if constraint is enabled
            if key == 'max_consecutive_classes' and self.config['constraints'][key]:
                current_limit = self.config['limits']['max_consecutive_classes']
                while True:
                    try:
                        limit = input(f"   Maximum consecutive hours [1-9] [{current_limit}]: ").strip()
                        if limit == "":
                            break
                        limit = int(limit)
                        if 1 <= limit <= 9:
                            self.config['limits']['max_consecutive_classes'] = limit
                            break
                        else:
                            print("   ❌ Must be between 1 and 9")
                    except ValueError:
                        print("   ❌ Invalid number")
            
            elif key == 'max_daily_hours' and self.config['constraints'][key]:
                current_limit = self.config['limits']['max_daily_hours']
                while True:
                    try:
                        limit = input(f"   Maximum daily hours [1-9] [{current_limit}]: ").strip()
                        if limit == "":
                            break
                        limit = int(limit)
                        if 1 <= limit <= 9:
                            self.config['limits']['max_daily_hours'] = limit
                            break
                        else:
                            print("   ❌ Must be between 1 and 9")
                    except ValueError:
                        print("   ❌ Invalid number")
            
            elif key == 'max_daily_teacher_hours' and self.config['constraints'][key]:
                current_limit = self.config['limits']['max_daily_teacher_hours']
                while True:
                    try:
                        limit = input(f"   Maximum teacher daily hours [1-9] [{current_limit}]: ").strip()
                        if limit == "":
                            break
                        limit = int(limit)
                        if 1 <= limit <= 9:
                            self.config['limits']['max_daily_teacher_hours'] = limit
                            break
                        else:
                            print("   ❌ Must be between 1 and 9")
                    except ValueError:
                        print("   ❌ Invalid number")
        
        # Summary
        print("\n" + "=" * 70)
        print("📋 CONFIGURATION SUMMARY")
        print("=" * 70)
        print(f"\n📅 Semester Type: {self.config['semester']['type'].upper()}")
        print(f"\n🔒 Constraints:")
        for key, info in constraints_info.items():
            status = "✅ ENABLED" if self.config['constraints'][key] else "❌ DISABLED"
            print(f"   {status}: {info['name']}")
            
            if key == 'max_consecutive_classes' and self.config['constraints'][key]:
                print(f"      → Limit: {self.config['limits']['max_consecutive_classes']} hours")
            elif key == 'max_daily_hours' and self.config['constraints'][key]:
                print(f"      → Limit: {self.config['limits']['max_daily_hours']} hours/day")
            elif key == 'max_daily_teacher_hours' and self.config['constraints'][key]:
                print(f"      → Limit: {self.config['limits']['max_daily_teacher_hours']} hours/day")
        
        print("\n" + "=" * 70)
        
        # Confirm
        while True:
            confirm = input("\n💾 Save this configuration? (y/n) [y]: ").strip().lower()
            if confirm == "" or confirm in ['y', 'yes']:
                self.save_config()
                print("✅ Configuration saved successfully!")
                return True
            elif confirm in ['n', 'no']:
                print("❌ Configuration not saved")
                return False
            else:
                print("Invalid input. Enter 'y' or 'n'")
    
    def get(self, key_path: str, default=None):
        """
        Get config value using dot notation
        Example: config.get('semester.type') or config.get('limits.max_daily_hours')
        """
        keys = key_path.split('.')
        value = self.config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def set(self, key_path: str, value):
        """
        Set config value using dot notation
        Example: config.set('semester.type', 'even')
        """
        keys = key_path.split('.')
        target = self.config
        
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        target[keys[-1]] = value
    
    def print_current_config(self):
        """Print current configuration in readable format"""
        print("\n📋 CURRENT CONFIGURATION")
        print("=" * 70)
        print(yaml.dump(self.config, default_flow_style=False, sort_keys=False))
        print("=" * 70)


# Convenience function for backward compatibility
def load_config_from_json_if_exists():
    """
    Migrate old JSON config to new YAML format
    This is for backward compatibility only
    """
    json_path = "src/constraints_config.json"
    yaml_path = "config/timetable_config.yml"
    
    if os.path.exists(json_path) and not os.path.exists(yaml_path):
        print("🔄 Detected old JSON config. Migrating to YAML...")
        try:
            import json
            with open(json_path, 'r') as f:
                old_config = json.load(f)
            
            # Create ConfigManager and update with old values
            config_mgr = ConfigManager(yaml_path)
            config_mgr.set('semester.type', old_config.get('semester_type', 'odd'))
            
            if 'selected_constraints' in old_config:
                for key, value in old_config['selected_constraints'].items():
                    config_mgr.set(f'constraints.{key}', value)
            
            if 'limits' in old_config:
                for key, value in old_config['limits'].items():
                    config_mgr.set(f'limits.{key}', value)
            
            config_mgr.save_config()
            print("✅ Migration complete! Old JSON config preserved for backup.")
            
            return config_mgr
        except Exception as e:
            print(f"⚠️  Migration failed: {e}")
            print("   Starting with default configuration...")
            return ConfigManager(yaml_path)
    
    return ConfigManager(yaml_path)