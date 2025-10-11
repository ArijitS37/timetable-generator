import pandas as pd
from ortools.sat.python import cp_model
from reportlab.lib import colors
from reportlab.lib.pagesizes import A3, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

# -----------------------------
# Step 1: Read Excel Input
# -----------------------------
df = pd.read_excel("input.xlsx")

# Collect data
teachers = df["Teacher"].unique().tolist()
rooms = df["Room_type"].unique().tolist()
subjects = df.to_dict("records")

# -----------------------------
# Step 2: Define Time Slots
# -----------------------------
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
slots = [f"{h}:30-{h+1}:30" for h in range(8, 17)]  # 8:30–5:30
time_slots = [(d, s) for d in days for s in slots]

# -----------------------------
# Step 3: CP-SAT Model
# -----------------------------
model = cp_model.CpModel()

timetable = {}
for subj in subjects:
    for t in range(len(time_slots)):
        timetable[(subj["Subject"], t)] = model.NewBoolVar(f"{subj['Subject']}_at_{t}")

# -----------------------------
# Step 4: Constraints
# -----------------------------
for subj in subjects:
    model.Add(
        sum(timetable[(subj["Subject"], t)] for t in range(len(time_slots)))
        == subj["Hours_per_week"]
    )

for t in range(len(time_slots)):
    for teacher in teachers:
        model.Add(
            sum(
                timetable[(subj["Subject"], t)]
                for subj in subjects if subj["Teacher"] == teacher
            ) <= 1
        )

for t in range(len(time_slots)):
    for room in rooms:
        model.Add(
            sum(
                timetable[(subj["Subject"], t)]
                for subj in subjects if subj["Room_type"] == room
            ) <= 1
        )

# -----------------------------
# Step 5: Solve
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 20
status = solver.Solve(model)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    # -----------------------------
    # Step 6: Build Timetable Grid
    # -----------------------------
    grid = {day: [""] * len(slots) for day in days}

    for subj in subjects:
        subj_name = subj["Subject"]
        teacher = subj["Teacher"]
        room = subj["Room_type"]
        for t in range(len(time_slots)):
            if solver.Value(timetable[(subj_name, t)]) == 1:
                day, slot = time_slots[t]
                idx = slots.index(slot)
                grid[day][idx] = f"{subj_name}\n{teacher}\n{room}"

    # Print in console
    print("\n=== Timetable Grid ===")
    print("Time", "\t".join(slots))
    for day in days:
        print(day, "\t".join(grid[day]))

    # -----------------------------
    # Step 7: Export to PDF
    # -----------------------------
    data = [["Day/Time"] + slots]  # Header row
    for day in days:
        data.append([day] + grid[day])

    pdf_file = "timetable.pdf"
    doc = SimpleDocTemplate(pdf_file, pagesize=landscape(A3))
    table = Table(data, repeatRows=1)

    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
    ])
    table.setStyle(style)

    doc.build([table])
    print(f"\n📄 Timetable exported to {pdf_file}")

else:
    print("❌ No feasible solution found.")
