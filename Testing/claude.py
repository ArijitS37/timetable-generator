import pandas as pd
from ortools.sat.python import cp_model
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

# -----------------------------
# Step 1: Read Excel Input
# -----------------------------
df = pd.read_excel("input.xlsx")

# Collect data
teachers = df["Teacher"].unique().tolist()
rooms = df["Room_type"].unique().tolist()
years = df["Year_Sem"].unique().tolist()  # e.g., CSE-1, CSE-3, CSE-5, CSE-7
subjects = df.to_dict("records")

print(f"Years/Semesters found: {years}")
print(f"Teachers: {teachers}")
print(f"Room types: {rooms}")
print(f"Total subjects: {len(subjects)}")

# -----------------------------
# Step 2: Define Time Slots
# -----------------------------
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
slots = [f"{h}:30-{h+1}:30" for h in range(8, 17)]  # 8:30–17:30
time_slots = [(d, s) for d in days for s in slots]

# Find GE slot index (12:30-13:30)
ge_slot_time = "12:30-13:30"
ge_slot_indices = []
for i, (day, slot) in enumerate(time_slots):
    if slot == ge_slot_time:
        ge_slot_indices.append(i)

print(f"GE slots found at indices: {ge_slot_indices}")

# -----------------------------
# Step 3: CP-SAT Model
# -----------------------------
model = cp_model.CpModel()

# Decision variables
timetable = {}
for subj in subjects:
    for t in range(len(time_slots)):
        timetable[(subj["Subject"], t)] = model.NewBoolVar(f"{subj['Subject']}_at_{t}")

# For lab sessions, we need additional variables to track consecutive slots
lab_sessions = {}
for subj in subjects:
    if subj.get("Type", "").lower() == "lab":
        # Lab sessions can start at any slot except the last one of each day
        for day_idx, day in enumerate(days):
            for slot_idx in range(len(slots) - 1):  # Can't start at last slot
                t = day_idx * len(slots) + slot_idx
                lab_sessions[(subj["Subject"], t)] = model.NewBoolVar(f"lab_{subj['Subject']}_starts_at_{t}")

# Variable for earliest completion time objective
max_used_slot = model.NewIntVar(0, len(time_slots) - 1, "max_used_slot")

# -----------------------------
# Step 4: Constraints
# -----------------------------

# 1. Course Hour Requirement
for subj in subjects:
    if subj.get("Type", "").lower() == "lab":
        # For labs, count lab sessions (each taking 2 consecutive slots)
        total_lab_sessions = subj["Hours_per_week"] // 2
        if subj["Subject"] in [key[0] for key in lab_sessions.keys()]:
            model.Add(
                sum(lab_sessions[(subj["Subject"], t)] 
                    for t in range(len(time_slots)) 
                    if (subj["Subject"], t) in lab_sessions) == total_lab_sessions
            )
    else:
        # For theory subjects
        model.Add(
            sum(timetable[(subj["Subject"], t)] for t in range(len(time_slots)))
            == subj["Hours_per_week"]
        )

# 2. Teacher Clash
for t in range(len(time_slots)):
    for teacher in teachers:
        regular_classes = sum(
            timetable[(subj["Subject"], t)]
            for subj in subjects if subj["Teacher"] == teacher
        )
        
        lab_classes_current = sum(
            lab_sessions[(subj["Subject"], t)]
            for subj in subjects 
            if subj["Teacher"] == teacher and subj.get("Type", "").lower() == "lab"
            and (subj["Subject"], t) in lab_sessions
        )
        
        # Lab sessions that started in previous slot
        lab_classes_previous = 0
        if t > 0:
            day_idx = t // len(slots)
            slot_idx = t % len(slots)
            prev_day_idx = (t-1) // len(slots)
            prev_slot_idx = (t-1) % len(slots)
            
            # Check if previous slot is consecutive (same day, consecutive time)
            if day_idx == prev_day_idx and slot_idx == prev_slot_idx + 1:
                lab_classes_previous = sum(
                    lab_sessions[(subj["Subject"], t-1)]
                    for subj in subjects 
                    if subj["Teacher"] == teacher and subj.get("Type", "").lower() == "lab"
                    and (subj["Subject"], t-1) in lab_sessions
                )
        
        model.Add(regular_classes + lab_classes_current + lab_classes_previous <= 1)

# 3. Room Clash
for t in range(len(time_slots)):
    for room in rooms:
        regular_classes = sum(
            timetable[(subj["Subject"], t)]
            for subj in subjects if subj["Room_type"] == room
        )
        
        lab_classes_current = sum(
            lab_sessions[(subj["Subject"], t)]
            for subj in subjects 
            if subj["Room_type"] == room and subj.get("Type", "").lower() == "lab"
            and (subj["Subject"], t) in lab_sessions
        )
        
        lab_classes_previous = 0
        if t > 0:
            day_idx = t // len(slots)
            slot_idx = t % len(slots)
            prev_day_idx = (t-1) // len(slots)
            prev_slot_idx = (t-1) % len(slots)
            
            if day_idx == prev_day_idx and slot_idx == prev_slot_idx + 1:
                lab_classes_previous = sum(
                    lab_sessions[(subj["Subject"], t-1)]
                    for subj in subjects 
                    if subj["Room_type"] == room and subj.get("Type", "").lower() == "lab"
                    and (subj["Subject"], t-1) in lab_sessions
                )
        
        model.Add(regular_classes + lab_classes_current + lab_classes_previous <= 1)

# 4. Year/Semester Clash - a year cannot have two classes at the same slot
for t in range(len(time_slots)):
    for year in years:
        regular_classes = sum(
            timetable[(subj["Subject"], t)]
            for subj in subjects if subj["Year_Sem"] == year
        )
        
        lab_classes_current = sum(
            lab_sessions[(subj["Subject"], t)]
            for subj in subjects 
            if subj["Year_Sem"] == year and subj.get("Type", "").lower() == "lab"
            and (subj["Subject"], t) in lab_sessions
        )
        
        lab_classes_previous = 0
        if t > 0:
            day_idx = t // len(slots)
            slot_idx = t % len(slots)
            prev_day_idx = (t-1) // len(slots)
            prev_slot_idx = (t-1) % len(slots)
            
            if day_idx == prev_day_idx and slot_idx == prev_slot_idx + 1:
                lab_classes_previous = sum(
                    lab_sessions[(subj["Subject"], t-1)]
                    for subj in subjects 
                    if subj["Year_Sem"] == year and subj.get("Type", "").lower() == "lab"
                    and (subj["Subject"], t-1) in lab_sessions
                )
        
        model.Add(regular_classes + lab_classes_current + lab_classes_previous <= 1)

# 5. Teacher Load
max_hours_per_teacher = 16
for teacher in teachers:
    total_theory_hours = sum(
        timetable[(subj["Subject"], t)] 
        for subj in subjects 
        for t in range(len(time_slots))
        if subj["Teacher"] == teacher and subj.get("Type", "").lower() != "lab"
    )
    
    total_lab_hours = sum(
        lab_sessions[(subj["Subject"], t)] * 2
        for subj in subjects 
        for t in range(len(time_slots))
        if subj["Teacher"] == teacher and subj.get("Type", "").lower() == "lab"
        and (subj["Subject"], t) in lab_sessions
    )
    
    model.Add(total_theory_hours + total_lab_hours <= max_hours_per_teacher)

# 6. GE Fixed Slot
for subj in subjects:
    if subj.get("Subject_type", "").upper() == "GE":
        model.Add(
            sum(timetable[(subj["Subject"], t)] 
                for t in range(len(time_slots)) 
                if t not in ge_slot_indices) == 0
        )
    else:
        model.Add(
            sum(timetable[(subj["Subject"], t)] for t in ge_slot_indices) == 0
        )

# 7. Lab Duration - consecutive slots constraint
for subj in subjects:
    if subj.get("Type", "").lower() == "lab":
        for t in range(len(time_slots)):
            if (subj["Subject"], t) in lab_sessions:
                if t < len(time_slots) - 1:
                    day_idx = t // len(slots)
                    slot_idx = t % len(slots)
                    next_day_idx = (t+1) // len(slots)
                    next_slot_idx = (t+1) % len(slots)
                    
                    # Check if next slot is consecutive (same day, next time slot)
                    if day_idx == next_day_idx and next_slot_idx == slot_idx + 1:
                        model.Add(
                            timetable[(subj["Subject"], t+1)] >= lab_sessions[(subj["Subject"], t)]
                        )
                        model.Add(
                            timetable[(subj["Subject"], t)] >= lab_sessions[(subj["Subject"], t)]
                        )

# 8. Earliest completion time constraint (soft constraint via objective)
for t in range(len(time_slots)):
    has_any_class = sum(
        timetable[(subj["Subject"], t)] 
        for subj in subjects if subj.get("Type", "").lower() != "lab"
    ) + sum(
        lab_sessions[(subj["Subject"], start_t)]
        for subj in subjects 
        for start_t in range(len(time_slots))
        if subj.get("Type", "").lower() == "lab" 
        and (subj["Subject"], start_t) in lab_sessions
        and (start_t == t or (start_t < len(time_slots) - 1 and start_t + 1 == t and 
             (start_t // len(slots)) == (t // len(slots)) and 
             (t % len(slots)) == ((start_t % len(slots)) + 1)))
    )
    
    # If there's any class at time t, then max_used_slot >= t
    model.Add(max_used_slot >= t).OnlyEnforceIf(has_any_class >= 1)

# -----------------------------
# Step 5: Objective - Minimize latest used slot
# -----------------------------
model.Minimize(max_used_slot)

# -----------------------------
# Step 6: Solve
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 120
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print(f"Solution status: {'OPTIMAL' if status == cp_model.OPTIMAL else 'FEASIBLE'}")
    print(f"Latest used time slot: {solver.Value(max_used_slot)} ({time_slots[solver.Value(max_used_slot)]})")
    
    # Create output directory
    os.makedirs("timetables", exist_ok=True)
    
    # Generate separate timetable for each year/semester
    for year in years:
        print(f"\nGenerating timetable for {year}...")
        
        # Build timetable grid for this year
        grid = {day: [""] * len(slots) for day in days}
        
        # Process regular classes for this year
        for subj in subjects:
            if subj["Year_Sem"] == year:
                subj_name = subj["Subject"]
                teacher = subj["Teacher"]
                room = subj["Room_type"]
                subj_type = subj.get("Type", "Theory")
                
                if subj.get("Type", "").lower() != "lab":
                    for t in range(len(time_slots)):
                        if solver.Value(timetable[(subj_name, t)]) == 1:
                            day_idx = t // len(slots)
                            slot_idx = t % len(slots)
                            day = days[day_idx]
                            
                            display_text = f"{subj_name}\n{teacher}\n{room}"
                            if subj.get("Subject_type", "").upper() == "GE":
                                display_text += "\n(GE)"
                            
                            grid[day][slot_idx] = display_text
        
        # Process lab sessions for this year
        for subj in subjects:
            if subj["Year_Sem"] == year and subj.get("Type", "").lower() == "lab":
                subj_name = subj["Subject"]
                teacher = subj["Teacher"]
                room = subj["Room_type"]
                
                for t in range(len(time_slots)):
                    if (subj_name, t) in lab_sessions and solver.Value(lab_sessions[(subj_name, t)]) == 1:
                        day_idx = t // len(slots)
                        slot_idx = t % len(slots)
                        day = days[day_idx]
                        
                        # Mark both consecutive slots
                        lab_info = f"{subj_name} (LAB)\n{teacher}\n{room}"
                        grid[day][slot_idx] = lab_info
                        if slot_idx + 1 < len(slots):
                            grid[day][slot_idx + 1] = lab_info
        
        # Print in console for this year
        print(f"\n=== {year} Timetable ===")
        header = "Day\\Time\t" + "\t".join(slots[:6])  # First 6 slots
        print(header)
        for day in days:
            row_data = [cell if cell else "-" for cell in grid[day][:6]]
            print(f"{day}\t" + "\t".join([cell.replace('\n', ' | ') for cell in row_data]))
        
        if len(slots) > 6:  # If there are more slots
            print(f"\nDay\\Time\t" + "\t".join(slots[6:]))
            for day in days:
                row_data = [cell if cell else "-" for cell in grid[day][6:]]
                print(f"{day}\t" + "\t".join([cell.replace('\n', ' | ') for cell in row_data]))
        
        # Generate PDF for this year
        data = [["Day/Time"] + slots]
        for day in days:
            data.append([day] + grid[day])
        
        pdf_file = f"timetables/{year}_timetable.pdf"
        doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A3))
        
        # Create title
        styles = getSampleStyleSheet()
        title = Paragraph(f"<b>Timetable for {year} - Computer Science Department</b>", 
                         styles['Title'])
        
        table = Table(data, repeatRows=1)
        
        style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
        ])
        table.setStyle(style)
        
        # Build PDF
        doc.build([title, Spacer(1, 12), table])
        print(f"📄 {year} timetable exported to {pdf_file}")
    
    # Print overall summary
    print(f"\n=== Overall Summary ===")
    total_theory_classes = sum(
        solver.Value(timetable[(subj["Subject"], t)])
        for subj in subjects
        for t in range(len(time_slots))
        if subj.get("Type", "").lower() != "lab"
    )
    
    total_lab_sessions = sum(
        solver.Value(lab_sessions[(subj["Subject"], t)])
        for subj in subjects
        for t in range(len(time_slots))
        if subj.get("Type", "").lower() == "lab" and (subj["Subject"], t) in lab_sessions
    )
    
    print(f"Total theory classes scheduled: {total_theory_classes}")
    print(f"Total lab sessions scheduled: {total_lab_sessions}")
    print(f"Total teaching hours: {total_theory_classes + (total_lab_sessions * 2)}")
    print(f"All timetables saved in 'timetables/' directory")

else:
    print("❌ No feasible solution found.")
    print("Try:")
    print("- Reducing subject hours or teacher loads")
    print("- Adding more rooms or teachers") 
    print("- Checking for conflicting constraints")
    print("- Increasing solver time limit")