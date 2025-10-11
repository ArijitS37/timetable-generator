"""
Excel generation module for master timetable
"""
import pandas as pd
from src.config import Config
from typing import Dict, List
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

class ExcelGenerator:
    def __init__(self, solution: Dict, subjects: List[Dict]):
        self.solution = solution
        self.subjects = subjects
        self.master_schedule = solution['master_schedule']
        self.slots = Config.get_slots_list()
        self.days = Config.DAYS
        
    def generate_master_timetable(self, filename: str):
        """Generate master timetable as Excel file"""
        print(f"      → {filename}")
        
        # Create DataFrame
        data = []
        
        # Add fixed slot indicators to know which slots are reserved
        fixed_slots_info = self._get_fixed_slots_info()
        
        for day in self.days:
            row = [day]
            for slot in self.slots:
                cell_content = ""
                
                # Check if this is a fixed slot
                slot_type = fixed_slots_info.get((day, slot), "")
                
                if day in self.master_schedule and slot in self.master_schedule[day]:
                    classes = self.master_schedule[day][slot]
                    if classes:
                        parts = []
                        for class_info in classes:
                            part = f"{class_info['subject']}"
                            if class_info['section'] != "ALL":
                                part += f" ({class_info['section']})"
                            part += f" | {class_info['teacher']}"
                            part += f" | {class_info['room']}"
                            part += f" | {class_info['type']}"
                            if class_info['subject_type']:
                                part += f" [{class_info['subject_type']}]"
                            parts.append(part)
                        cell_content = "\n---\n".join(parts)
                    else:
                        # Show fixed slot even if empty
                        if slot_type:
                            cell_content = f"[{slot_type} SLOT - RESERVED]"
                else:
                    # Show fixed slot even if no classes scheduled
                    if slot_type:
                        cell_content = f"[{slot_type} SLOT - RESERVED]"
                
                row.append(cell_content)
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data, columns=["Day/Time"] + self.slots)
        
        # Write to Excel with formatting
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Master Timetable', index=False)
            
            # Get worksheet
            worksheet = writer.sheets['Master Timetable']
            
            # Format header row
            header_fill = PatternFill(start_color="808080", end_color="808080", fill_type="solid")
            header_font = Font(bold=True, color="FFFFFF")
            
            for cell in worksheet[1]:
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center')
            
            # Format data cells
            thin_border = Border(
                left=Side(style='thin'),
                right=Side(style='thin'),
                top=Side(style='thin'),
                bottom=Side(style='thin')
            )
            
            for row in worksheet.iter_rows(min_row=2, max_row=len(data)+1):
                for cell in row:
                    cell.alignment = Alignment(horizontal='center', vertical='top', wrap_text=True)
                    cell.border = thin_border
            
            # Adjust column widths
            worksheet.column_dimensions['A'].width = 12  # Day column
            for col_idx in range(2, len(self.slots) + 2):
                worksheet.column_dimensions[openpyxl.utils.get_column_letter(col_idx)].width = 30
            
            # Adjust row heights
            for row_idx in range(2, len(data) + 2):
                worksheet.row_dimensions[row_idx].height = 100
        
        print(f"      ✅ Master timetable Excel generated")
    
    def _get_fixed_slots_info(self) -> Dict:
        """Get information about which slots are reserved for GE/SEC/VAC/AEC"""
        fixed_info = {}
        time_slots = Config.get_time_slots()
        
        # GE slots
        for idx in Config.get_fixed_slot_indices("GE"):
            day, slot = time_slots[idx]
            if (day, slot) not in fixed_info:
                fixed_info[(day, slot)] = "GE"
        
        # SEC slots
        for idx in Config.get_fixed_slot_indices("SEC"):
            day, slot = time_slots[idx]
            if (day, slot) not in fixed_info:
                fixed_info[(day, slot)] = "SEC"
            else:
                fixed_info[(day, slot)] += "/SEC"
        
        # VAC slots
        for idx in Config.get_fixed_slot_indices("VAC"):
            day, slot = time_slots[idx]
            if (day, slot) not in fixed_info:
                fixed_info[(day, slot)] = "VAC"
            else:
                fixed_info[(day, slot)] += "/VAC"
        
        # AEC slots
        for idx in Config.get_fixed_slot_indices("AEC"):
            day, slot = time_slots[idx]
            if (day, slot) not in fixed_info:
                fixed_info[(day, slot)] = "AEC"
            elif "GE" not in fixed_info[(day, slot)] and "AEC" not in fixed_info[(day, slot)]:
                fixed_info[(day, slot)] += "/AEC"
        
        return fixed_info