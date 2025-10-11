"""
PDF generation module - UPDATED with room numbers and formatting
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from src.config import Config
import os
from typing import Dict, List, Any

class PDFGenerator:
    def __init__(self, solution: Dict, subjects: List[Dict], teachers: List[str], rooms: List[str], course_semesters: List[str]):
        self.solution = solution
        self.subjects = subjects
        self.teachers = teachers
        self.rooms = rooms
        self.course_semesters = course_semesters
        self.master_schedule = solution['master_schedule']
        self.slots = Config.get_slots_list()
        self.days = Config.DAYS
        
    def generate_teacher_timetables(self, output_dir: str):
        """Generate individual timetables for each teacher"""
        os.makedirs(output_dir, exist_ok=True)
        
        for teacher in self.teachers:
            filename = os.path.join(output_dir, f"{teacher.replace(' ', '_')}_timetable.pdf")
            print(f"      → {filename}")
            self._generate_filtered_timetable(
                filename,
                f"Timetable for {teacher}",
                lambda class_info: class_info['teacher'] == teacher,
                show_fields=['subject', 'course_semester', 'type', 'room', 'section'],
                show_reserved_slots=False
            )
    
    def generate_room_timetables(self, output_dir: str):
        """Generate individual timetables for each specific room"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all unique rooms from schedule
        rooms_used = set()
        for day_schedule in self.master_schedule.values():
            for slot_classes in day_schedule.values():
                for class_info in slot_classes:
                    rooms_used.add(class_info['room'])
        
        for room in sorted(rooms_used, key=lambda x: (x.split('-')[0], int(x.split('-')[1]) if '-' in x and x.split('-')[1].isdigit() else 0)):
            filename = os.path.join(output_dir, f"{room.replace(' ', '_')}_timetable.pdf")
            print(f"      → {filename}")
            self._generate_filtered_timetable(
                filename,
                f"Room Utilization: {room}",
                lambda class_info: class_info['room'] == room,
                show_fields=['subject', 'teacher', 'course_semester', 'type', 'section'],
                show_reserved_slots=False
            )
    
    def generate_course_semester_timetables(self, output_dir: str):
        """Generate individual timetables for each course-semester"""
        os.makedirs(output_dir, exist_ok=True)
        
        for course_sem in self.course_semesters:
            filename = os.path.join(output_dir, f"{course_sem.replace(' ', '_').replace('/', '_')}_timetable.pdf")
            print(f"      → {filename}")
            self._generate_filtered_timetable(
                filename,
                f"Timetable for {course_sem}",
                lambda class_info: class_info['course_semester'] == course_sem,
                show_fields=['subject', 'teacher', 'type', 'room'],
                show_reserved_slots=True  # Students need to see reserved slots
            )
    
    def _generate_filtered_timetable(self, filename: str, title_text: str, filter_func, 
                                     show_fields: List[str], show_reserved_slots: bool):
        """Generate a filtered timetable"""
        doc = SimpleDocTemplate(filename, pagesize=landscape(A3))
        styles = getSampleStyleSheet()
        
        title = Paragraph(f"<b>{title_text}</b>", styles['Title'])
        
        # Determine semester for year-specific reserved slots
        semester = None
        for course_sem in self.course_semesters:
            if course_sem in title_text:
                # Extract semester from course_sem
                for subj in self.subjects:
                    if subj["Course_Semester"] == course_sem:
                        semester = subj["Semester"]
                        break
                break
        
        # Get fixed slot info based on semester
        fixed_slots_info = self._get_fixed_slots_info(semester) if show_reserved_slots else {}
        
        # Create filtered grid
        data = [["Day/Time"] + self.slots]
        
        for day in self.days:
            row = [day]
            for slot in self.slots:
                cell_content = ""
                
                # Check for reserved slots (semester-specific)
                slot_type = fixed_slots_info.get((day, slot), "")
                
                if day in self.master_schedule and slot in self.master_schedule[day]:
                    filtered_classes = [
                        class_info for class_info in self.master_schedule[day][slot]
                        if filter_func(class_info)
                    ]
                    
                    if filtered_classes:
                        cell_parts = []
                        
                        # Group continuous practical sessions
                        processed_subjects = set()
                        
                        for class_info in filtered_classes:
                            subject_key = f"{class_info['subject']}_{class_info.get('teacher', '')}"
                            
                            # Skip if this is a continuation of an already processed practical
                            if class_info.get('is_continuation', False) and subject_key in processed_subjects:
                                continue
                            
                            parts = []
                            if 'subject' in show_fields:
                                subject_display = class_info['subject']
                                if class_info['type'] == 'Practical':
                                    subject_display += " (2-hour)"
                                parts.append(subject_display)
                            
                            if 'teacher' in show_fields:
                                parts.append(class_info['teacher'])
                            if 'course_semester' in show_fields:
                                parts.append(f"[{class_info['course_semester']}]")
                            if 'section' in show_fields and class_info['section'] != "ALL":
                                parts.append(f"Sec-{class_info['section']}")
                            if 'room' in show_fields:
                                parts.append(class_info['room'])
                            if class_info['subject_type']:
                                parts.append(f"({class_info['subject_type']})")
                            
                            cell_parts.append("\n".join(parts))
                            
                            # Mark practical as processed
                            if class_info['type'] == 'Practical':
                                processed_subjects.add(subject_key)
                        
                        cell_content = "\n\n".join(cell_parts)
                    else:
                        # Show reserved slot even if no matching classes
                        if slot_type:
                            cell_content = f"[{slot_type}]\nRESERVED"
                else:
                    # Show reserved slot
                    if slot_type:
                        cell_content = f"[{slot_type}]\nRESERVED"
                
                row.append(cell_content)
            data.append(row)
        
        # Summary
        total_classes = sum(
            1 for day_schedule in self.master_schedule.values()
            for slot_classes in day_schedule.values()
            for class_info in slot_classes
            if filter_func(class_info) and not class_info.get('is_continuation', False)
        )
        
        summary_text = f"<b>Total Classes:</b> {total_classes}"
        summary = Paragraph(summary_text, styles['Normal'])
        
        table = Table(data, repeatRows=1)
        table.setStyle(self._get_table_style())
        
        doc.build([title, Spacer(1, 12), summary, Spacer(1, 12), table])
    
    def _get_fixed_slots_info(self, semester=None) -> Dict:
        """Get information about which slots are reserved (semester-specific if provided)"""
        fixed_info = {}
        time_slots = Config.get_time_slots()
        
        # If semester specified, only show slots relevant to that semester
        if semester is not None:
            relevant_types = Config.get_fixed_slot_types_for_semester(semester)
        else:
            relevant_types = Config.FIXED_SLOT_TYPES
        
        # Add slots for each relevant type
        for slot_type in relevant_types:
            for idx in Config.get_fixed_slot_indices(slot_type):
                day, slot = time_slots[idx]
                if (day, slot) not in fixed_info:
                    fixed_info[(day, slot)] = slot_type
                else:
                    if slot_type not in fixed_info[(day, slot)]:
                        fixed_info[(day, slot)] += f"/{slot_type}"
        
        return fixed_info
    
    def _get_table_style(self) -> TableStyle:
        """Get consistent table styling"""
        return TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.Color(*Config.PDF_HEADER_COLOR)),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), Config.PDF_FONT_SIZE),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(*Config.PDF_ALT_ROW_COLOR)]),
        ])