"""
PDF generation module - UPGRADED VERSION
Features:
- Teacher timetables with main + assistant hours
- Course-semester timetables with merged course info and assistants
- Room timetables with (TH) indicator for theory classes
- Free rooms availability PDF
- Color coding with legend on each PDF
- 2-hour block visual merging
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from src.config import Config
import os
from typing import Dict, List, Any, Set, Tuple
from collections import defaultdict

class PDFGenerator:
    def __init__(self, solution: Dict, subjects: List[Dict], teachers: List[str], 
                 rooms: List[str], course_semesters: List[str]):
        self.solution = solution
        self.subjects = subjects
        self.teachers = teachers
        self.rooms = rooms
        self.course_semesters = course_semesters
        self.master_schedule = solution['master_schedule']
        self.slots = Config.get_slots_list()
        self.days = Config.DAYS
        self.assistant_assignments = solution.get('assistant_assignments', {})
        
        # Color scheme (matching Excel)
        self.color_scheme = {
            'DSC': colors.Color(184/255, 230/255, 245/255),    # Light blue
            'DSE': colors.Color(212/255, 230/255, 241/255),    # Lighter blue
            'GE': colors.Color(197/255, 225/255, 165/255),     # Light green
            'SEC': colors.Color(255/255, 249/255, 196/255),    # Light yellow
            'VAC': colors.Color(255/255, 204/255, 188/255),    # Light orange
            'AEC': colors.Color(225/255, 190/255, 231/255),    # Light purple
            'default': colors.white
        }
    
    def generate_teacher_timetables(self, output_dir: str):
        """Generate individual timetables for each teacher (main + assistant hours)"""
        os.makedirs(output_dir, exist_ok=True)
        
        for teacher in self.teachers:
            filename = os.path.join(output_dir, f"{teacher.replace(' ', '_')}_timetable.pdf")
            print(f"      → {filename}")
            
            # Calculate total hours for this teacher
            total_hours = self._calculate_teacher_hours(teacher)
            
            self._generate_teacher_pdf(
                filename,
                teacher,
                total_hours
            )
    
    def generate_room_timetables(self, output_dir: str):
        """Generate individual timetables for each specific room"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Get all unique rooms from schedule
        rooms_used = set()
        for day_schedule in self.master_schedule.values():
            for slot_classes in day_schedule.values():
                for class_info in slot_classes:
                    room = class_info['room']
                    # Handle multiple labs
                    if ',' in room:
                        rooms_used.update([r.strip() for r in room.split(',')])
                    else:
                        rooms_used.add(room)
        
        for room in sorted(rooms_used, key=self._sort_room_key):
            filename = os.path.join(output_dir, f"{room.replace(' ', '_').replace('/', '_')}_timetable.pdf")
            print(f"      → {filename}")
            self._generate_room_pdf(filename, room)
    
    def generate_course_semester_timetables(self, output_dir: str):
        """Generate individual timetables for each course-semester"""
        os.makedirs(output_dir, exist_ok=True)
        
        for course_sem in self.course_semesters:
            filename = os.path.join(output_dir, 
                                  f"{course_sem.replace(' ', '_').replace('/', '_')}_timetable.pdf")
            print(f"      → {filename}")
            self._generate_course_semester_pdf(filename, course_sem)
    
    def generate_free_rooms_pdf(self, output_dir: str):
        """Generate PDF showing free rooms for each time slot"""
        filename = os.path.join(output_dir, "free_rooms_availability.pdf")
        print(f"\n   📄 Generating free rooms availability PDF...")
        print(f"      → {filename}")
        
        doc = SimpleDocTemplate(filename, pagesize=landscape(A3),
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Title'],
            fontSize=18,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=20,
            alignment=TA_CENTER
        )
        title = Paragraph("<b>Free Rooms Availability - Weekly Schedule</b>", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Subtitle
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#7F8C8D'),
            alignment=TA_CENTER,
            spaceAfter=15
        )
        subtitle = Paragraph(
            "Available rooms for self-study, breaks, and social activities",
            subtitle_style
        )
        elements.append(subtitle)
        elements.append(Spacer(1, 0.2*inch))
        
        # Build free rooms grid
        data = self._build_free_rooms_grid()
        
        # Create table
        table = Table(data, repeatRows=1)
        table.setStyle(self._get_free_rooms_table_style(len(data)))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add legend
        legend = self._create_free_rooms_legend(styles)
        elements.extend(legend)
        
        doc.build(elements)
        print(f"      ✅ Free rooms PDF generated")
    
    def _generate_teacher_pdf(self, filename: str, teacher: str, total_hours: float):
        """Generate PDF for a specific teacher"""
        doc = SimpleDocTemplate(filename, pagesize=landscape(A3),
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title with teacher name and hours
        title_text = f"<b>Timetable for {teacher}</b>"
        if total_hours > 0:
            title_text += f"<br/><font size=12>Total Weekly Hours: {total_hours:.1f}/{Config.MAX_HOURS_PER_TEACHER}</font>"
        
        title = Paragraph(title_text, styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Build filtered grid
        data = self._build_teacher_grid(teacher)
        
        # Create table
        table = Table(data, repeatRows=1)
        table.setStyle(self._get_table_style(len(data)))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add legend
        legend = self._create_legend(styles)
        elements.extend(legend)
        
        doc.build(elements)
    
    def _generate_room_pdf(self, filename: str, room: str):
        """Generate PDF for a specific room"""
        doc = SimpleDocTemplate(filename, pagesize=landscape(A3),
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title = Paragraph(f"<b>Room Utilization: {room}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Build filtered grid
        data = self._build_room_grid(room)
        
        # Create table
        table = Table(data, repeatRows=1)
        table.setStyle(self._get_table_style(len(data)))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add legend
        legend = self._create_legend(styles)
        elements.extend(legend)
        
        doc.build(elements)
    
    def _generate_course_semester_pdf(self, filename: str, course_sem: str):
        """Generate PDF for a specific course-semester"""
        doc = SimpleDocTemplate(filename, pagesize=landscape(A3),
                              topMargin=0.5*inch, bottomMargin=0.5*inch)
        styles = getSampleStyleSheet()
        elements = []
        
        # Title
        title = Paragraph(f"<b>Timetable for {course_sem}</b>", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.2*inch))
        
        # Determine semester for reserved slots
        semester = self._get_semester_from_course_sem(course_sem)
        
        # Build filtered grid
        data = self._build_course_semester_grid(course_sem, semester)
        
        # Create table
        table = Table(data, repeatRows=1)
        table.setStyle(self._get_table_style(len(data)))
        
        elements.append(table)
        elements.append(Spacer(1, 0.3*inch))
        
        # Add legend
        legend = self._create_legend(styles)
        elements.extend(legend)
        
        doc.build(elements)
    
    def _build_teacher_grid(self, teacher: str) -> List[List]:
        """Build timetable grid for a teacher"""
        data = [["Day/Time"] + self.slots]
        
        for day in self.days:
            row = [day]
            
            for slot in self.slots:
                cell_content = ""
                
                if day in self.master_schedule and slot in self.master_schedule[day]:
                    classes = self.master_schedule[day][slot]
                    
                    # Filter classes where this teacher is involved
                    teacher_classes = [
                        c for c in classes 
                        if teacher in c.get('teachers_list', [c['teacher']])
                    ]
                    
                    if teacher_classes:
                        parts = []
                        for class_info in teacher_classes:
                            # Skip continuation markers for display
                            if class_info.get('is_continuation', False):
                                continue
                            
                            # Determine role
                            teachers_list = class_info.get('teachers_list', [class_info['teacher']])
                            role = "Main" if teachers_list[0] == teacher else "Assistant"
                            
                            part_lines = [
                                f"{class_info['subject']}",
                                f"{class_info['course_semester']}",
                            ]
                            
                            if class_info['section'] != "ALL" and class_info['section']:
                                part_lines.append(f"Sec-{class_info['section']}")
                            
                            part_lines.append(f"{class_info['room']}")
                            part_lines.append(f"{class_info['type']}")
                            
                            if role == "Assistant":
                                part_lines.append(f"(Assistant)")
                            
                            if class_info['type'] == 'Practical':
                                part_lines.append("(2-hour)")
                            
                            parts.append("\n".join(part_lines))
                        
                        cell_content = "\n---\n".join(parts)
                
                row.append(cell_content)
            
            data.append(row)
        
        return data
    
    def _build_room_grid(self, room: str) -> List[List]:
        """Build timetable grid for a room"""
        data = [["Day/Time"] + self.slots]
        
        for day in self.days:
            row = [day]
            
            for slot in self.slots:
                cell_content = ""
                
                if day in self.master_schedule and slot in self.master_schedule[day]:
                    classes = self.master_schedule[day][slot]
                    
                    # Filter classes in this room
                    room_classes = []
                    for c in classes:
                        class_room = c['room']
                        # Handle multiple rooms
                        if ',' in class_room:
                            rooms_list = [r.strip() for r in class_room.split(',')]
                            if room in rooms_list:
                                room_classes.append(c)
                        elif class_room == room:
                            room_classes.append(c)
                    
                    if room_classes:
                        parts = []
                        for class_info in room_classes:
                            # Skip continuation markers for display
                            if class_info.get('is_continuation', False):
                                continue
                            
                            # Check if lab is being used for theory
                            room_display = class_info['room']
                            if class_info['type'] in ['Lecture', 'Tutorial'] and 'Lab' in room_display:
                                # Add (TH) indicator
                                if ',' in room_display:
                                    # Multiple labs - add (TH) to this specific one
                                    room_display = room.replace(room, f"{room} (TH)")
                                else:
                                    room_display = f"{room_display} (TH)"
                            
                            teachers_str = " + ".join(class_info.get('teachers_list', [class_info['teacher']]))
                            
                            part_lines = [
                                f"{class_info['subject']}",
                                f"{teachers_str}",
                                f"{class_info['course_semester']}",
                            ]
                            
                            if class_info['section'] != "ALL" and class_info['section']:
                                part_lines.append(f"Sec-{class_info['section']}")
                            
                            part_lines.append(f"{class_info['type']}")
                            
                            if class_info['type'] == 'Practical':
                                part_lines.append("(2-hour)")
                            
                            parts.append("\n".join(part_lines))
                        
                        cell_content = "\n---\n".join(parts)
                
                row.append(cell_content)
            
            data.append(row)
        
        return data
    
    def _build_course_semester_grid(self, course_sem: str, semester: int) -> List[List]:
        """Build timetable grid for a course-semester"""
        data = [["Day/Time"] + self.slots]
        
        # Get fixed slots info for this semester
        fixed_slots_info = self._get_fixed_slots_info(semester)
        
        for day in self.days:
            row = [day]
            
            for slot in self.slots:
                cell_content = ""
                
                # Check for reserved slots
                slot_type = fixed_slots_info.get((day, slot), "")
                
                if day in self.master_schedule and slot in self.master_schedule[day]:
                    classes = self.master_schedule[day][slot]
                    
                    # Filter classes for this course-semester
                    cs_classes = [c for c in classes if c['course_semester'] == course_sem]
                    
                    if cs_classes:
                        parts = []
                        for class_info in cs_classes:
                            # Skip continuation markers for display
                            if class_info.get('is_continuation', False):
                                continue
                            
                            # Check if merged course
                            merged_info = self._get_merged_courses_info(class_info)
                            subject_display = class_info['subject']
                            if merged_info:
                                subject_display += f" [{merged_info}]"
                            
                            # Format teachers with assistants
                            teachers_str = " + ".join(class_info.get('teachers_list', [class_info['teacher']]))
                            
                            part_lines = [
                                f"{subject_display}",
                                f"{teachers_str}",
                            ]
                            
                            if class_info['section'] != "ALL" and class_info['section']:
                                part_lines.append(f"Sec-{class_info['section']}")
                            
                            part_lines.append(f"{class_info['room']}")
                            part_lines.append(f"{class_info['type']}")
                            
                            if class_info['type'] == 'Practical':
                                part_lines.append("(2-hour)")
                            
                            if class_info['subject_type']:
                                part_lines.append(f"({class_info['subject_type']})")
                            
                            parts.append("\n".join(part_lines))
                        
                        cell_content = "\n---\n".join(parts)
                    else:
                        # Show reserved slot
                        if slot_type:
                            cell_content = f"[{slot_type}]\nRESERVED"
                else:
                    # Show reserved slot
                    if slot_type:
                        cell_content = f"[{slot_type}]\nRESERVED"
                
                row.append(cell_content)
            
            data.append(row)
        
        return data
    
    def _build_free_rooms_grid(self) -> List[List]:
        """Build grid showing free rooms for each time slot"""
        # Get all rooms with capacities
        all_rooms = []
        for room_name, room_info in Config.ROOMS.items():
            capacity = room_info.get('capacity_max', room_info.get('capacity_min', 0))
            all_rooms.append((room_name, capacity))
        
        # Sort rooms
        all_rooms.sort(key=lambda x: self._sort_room_key(x[0]))
        
        # Track room usage
        room_usage = defaultdict(set)  # {(day, slot): set of rooms in use}
        
        for day in self.days:
            if day not in self.master_schedule:
                continue
            
            for slot in self.slots:
                if slot not in self.master_schedule[day]:
                    continue
                
                for class_info in self.master_schedule[day][slot]:
                    room = class_info['room']
                    
                    # Handle multiple rooms
                    if ',' in room:
                        rooms_list = [r.strip() for r in room.split(',')]
                        for r in rooms_list:
                            # Remove (TH) indicator if present
                            r_clean = r.replace(' (TH)', '').replace('(TH)', '').strip()
                            room_usage[(day, slot)].add(r_clean)
                    else:
                        # Remove (TH) indicator if present
                        room_clean = room.replace(' (TH)', '').replace('(TH)', '').strip()
                        room_usage[(day, slot)].add(room_clean)
        
        # Build grid
        data = [["Day/Time"] + self.slots]
        
        for day in self.days:
            row = [day]
            
            for slot in self.slots:
                used_rooms = room_usage.get((day, slot), set())
                free_rooms = [
                    f"{room} ({capacity})" 
                    for room, capacity in all_rooms 
                    if room not in used_rooms
                ]
                
                if free_rooms:
                    # Limit to avoid overcrowding
                    if len(free_rooms) > 15:
                        cell_content = "\n".join(free_rooms[:15]) + f"\n... +{len(free_rooms)-15} more"
                    else:
                        cell_content = "\n".join(free_rooms)
                else:
                    cell_content = "All rooms\noccupied"
                
                row.append(cell_content)
            
            data.append(row)
        
        return data
    
    def _calculate_teacher_hours(self, teacher: str) -> float:
        """Calculate total hours for a teacher (main + assistant)"""
        total = 0
        
        for day_schedule in self.master_schedule.values():
            for slot_classes in day_schedule.values():
                for class_info in slot_classes:
                    teachers_list = class_info.get('teachers_list', [class_info['teacher']])
                    
                    if teacher in teachers_list:
                        # Don't double count 2-hour practicals
                        if class_info.get('is_continuation', False):
                            continue
                        
                        # Count hours
                        if class_info['type'] == 'Practical':
                            total += 2  # 2-hour block
                        else:
                            total += 1
        
        return total
    
    def _get_merged_courses_info(self, class_info: Dict) -> str:
        """Get merged course information for display"""
        for subj in self.subjects:
            if (subj['Subject'] == class_info['subject'] and 
                subj['Course_Semester'] == class_info['course_semester']):
                if subj.get('Is_Merged', False):
                    merge_group_id = subj.get('Merge_Group_ID')
                    merged_courses = []
                    
                    for s in self.subjects:
                        if s.get('Merge_Group_ID') == merge_group_id:
                            course_short = Config.get_short_course_name(s['Course'])
                            if course_short not in merged_courses:
                                merged_courses.append(course_short)
                    
                    return " + ".join(sorted(merged_courses))
        
        return ""
    
    def _get_semester_from_course_sem(self, course_sem: str) -> int:
        """Extract semester number from course_semester string"""
        for subj in self.subjects:
            if subj['Course_Semester'] == course_sem:
                return subj['Semester']
        return 1  # Default
    
    def _get_fixed_slots_info(self, semester: int) -> Dict:
        """Get information about which slots are reserved (semester-specific)"""
        fixed_info = {}
        time_slots = Config.get_time_slots()
        
        relevant_types = Config.get_fixed_slot_types_for_semester(semester)
        
        for slot_type in relevant_types:
            for idx in Config.get_fixed_slot_indices(slot_type, semester):
                day, slot = time_slots[idx]
                if (day, slot) not in fixed_info:
                    fixed_info[(day, slot)] = slot_type
                else:
                    if slot_type not in fixed_info[(day, slot)]:
                        fixed_info[(day, slot)] += f"/{slot_type}"
        
        return fixed_info
    
    def _sort_room_key(self, room_name: str) -> Tuple:
        """Sort key for room names"""
        parts = room_name.split('-')
        if len(parts) < 2:
            return (room_name, "", 0)
        
        room_type = parts[0]
        try:
            room_num = int(parts[-1].split()[0])
            middle = parts[1] if len(parts) > 2 else ""
            return (room_type, middle, room_num)
        except (ValueError, IndexError):
            return (room_type, parts[1] if len(parts) > 1 else "", 0)
    
    def _get_table_style(self, num_rows: int) -> TableStyle:
        """Get table styling for timetables"""
        style_commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#34495E')),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            
            # Day column
            ("BACKGROUND", (0, 1), (0, -1), colors.HexColor('#ECF0F1')),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ]
        
        # Alternating row colors for better readability
        for row in range(1, num_rows):
            if row % 2 == 0:
                style_commands.append(
                    ("BACKGROUND", (1, row), (-1, row), colors.HexColor('#F8F9FA'))
                )
        
        return TableStyle(style_commands)
    
    def _get_free_rooms_table_style(self, num_rows: int) -> TableStyle:
        """Get table styling for free rooms grid"""
        style_commands = [
            # Header row
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#27AE60')),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            
            # Day column
            ("BACKGROUND", (0, 1), (0, -1), colors.HexColor('#D5F4E6')),
            ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
        ]
        
        # Alternating row colors
        for row in range(1, num_rows):
            if row % 2 == 0:
                style_commands.append(
                    ("BACKGROUND", (1, row), (-1, row), colors.HexColor('#EAFAF1'))
                )
        
        return TableStyle(style_commands)
    
    def _create_legend(self, styles) -> List:
        """Create color legend for PDFs"""
        elements = []
        
        # Legend title
        legend_title_style = ParagraphStyle(
            'LegendTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#2C3E50'),
            spaceAfter=10
        )
        elements.append(Paragraph("<b>Subject Type Color Legend</b>", legend_title_style))
        
        # Legend content
        legend_data = [
            ["Type", "Description", "Color"],
            ["DSC", "Discipline Specific Core", "Light Blue"],
            ["DSE", "Discipline Specific Elective", "Lighter Blue"],
            ["GE", "Generic Elective", "Light Green"],
            ["SEC", "Skill Enhancement Course", "Light Yellow"],
            ["VAC", "Value Added Course", "Light Orange"],
            ["AEC", "Ability Enhancement Course", "Light Purple"],
        ]
        
        legend_table = Table(legend_data, colWidths=[0.8*inch, 2.5*inch, 1.2*inch])
        
        legend_style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor('#95A5A6')),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            
            # Apply colors to legend rows
            ("BACKGROUND", (0, 1), (-1, 1), self.color_scheme['DSC']),
            ("BACKGROUND", (0, 2), (-1, 2), self.color_scheme['DSE']),
            ("BACKGROUND", (0, 3), (-1, 3), self.color_scheme['GE']),
            ("BACKGROUND", (0, 4), (-1, 4), self.color_scheme['SEC']),
            ("BACKGROUND", (0, 5), (-1, 5), self.color_scheme['VAC']),
            ("BACKGROUND", (0, 6), (-1, 6), self.color_scheme['AEC']),
        ])
        
        legend_table.setStyle(legend_style)
        elements.append(legend_table)
        elements.append(Spacer(1, 0.2*inch))
        
        # Notes
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.HexColor('#7F8C8D'),
            leftIndent=10
        )
        
        notes = [
            "<b>Notes:</b>",
            "• Merged courses shown as: Subject [Course1 + Course2]",
            "• Assistant teachers shown as: Main + Asst1 + Asst2",
            "• 2-hour practical blocks span consecutive time slots",
            "• (TH) indicates lab room used for theory class",
            "• Reserved slots marked for GE/SEC/VAC/AEC subjects"
        ]
        
        for note in notes:
            elements.append(Paragraph(note, notes_style))
        
        return elements
    
    def _create_free_rooms_legend(self, styles) -> List:
        """Create legend for free rooms PDF"""
        elements = []
        
        # Legend title
        legend_title_style = ParagraphStyle(
            'LegendTitle',
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#27AE60'),
            spaceAfter=10
        )
        elements.append(Paragraph("<b>Understanding This Schedule</b>", legend_title_style))
        
        # Notes
        notes_style = ParagraphStyle(
            'Notes',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#2C3E50'),
            leftIndent=15,
            spaceAfter=6
        )
        
        notes = [
            "<b>Room Format:</b> RoomName (Capacity)",
            "<b>R-X:</b> Regular classroom (X = room number)",
            "<b>CL-X:</b> Computer Science Lab",
            "<b>PL-X:</b> Physics Lab",
            "<b>ChemL-X:</b> Chemistry Lab",
            "<b>EL-X:</b> Electronics Lab",
            "<b>BioL-X:</b> Biology Lab",
            "",
            "<b>Usage Guidelines:</b>",
            "• Available rooms are free for self-study, breaks, or group discussions",
            "• Please maintain silence for studying students",
            "• Keep rooms clean and tidy",
            "• Labs may have equipment - handle with care",
        ]
        
        for note in notes:
            elements.append(Paragraph(note, notes_style))
        
        return elements