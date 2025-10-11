import pandas as pd
import random
from ortools.sat.python import cp_model

# -----------------------------
# Step 1: Generate Dummy Dataset
# -----------------------------
teachers = [f"Teacher_{i}" for i in range(1, 151)]
rooms = [f"Room_{i}" for i in range(1, 51)]
subjects = []

for i in range(1, 101):  # 100 subjects
    subj = {
        "Subject": f"Subject_{i}",
        "Teacher": random.choice(teachers),
        "Hours_per_week": random.randint(2, 4),  # 2–4 hrs/week
        "Room_type": random.choice(rooms),
        # Add dummy course/section so we can slice later
        "Course": f"Course_{random.randint(1, 20)}",
        "Section": random.choice(["A", "B", "C"])
    }
    subjects.append(subj)

df = pd.DataFrame(subjects)
print("Dummy dataset sample:\n", df.head())

# -----------------------------
# Step 2: Define Time Slots
# -----------------------------
days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
slots = [f"{h}:30-{h+1}:30" for h in range(8, 17)]  # 8:30–6:30
time_slots = [(d, s) for d in days for s in slots]  # (day, slot) pairs
slots_per_day = len(slots)

# -----------------------------
# Step 3: CP-SAT Model
# -----------------------------
model = cp_model.CpModel()

# Variable: timetable[(subj, t)] = 1 if scheduled in timeslot t
timetable = {}
for subj in subjects:
    for t in range(len(time_slots)):
        timetable[(subj["Subject"], t)] = model.NewBoolVar(f"{subj['Subject']}_at_{t}")

# -----------------------------
# Step 4: Constraints
# -----------------------------

# (1) Each subject must appear "Hours_per_week" times
for subj in subjects:
    model.Add(
        sum(timetable[(subj["Subject"], t)] for t in range(len(time_slots)))
        == subj["Hours_per_week"]
    )

# (2) Teacher not double booked
for t in range(len(time_slots)):
    for teacher in teachers:
        model.Add(
            sum(
                timetable[(subj["Subject"], t)]
                for subj in subjects if subj["Teacher"] == teacher
            ) <= 1
        )

# (3) Room not double booked
for t in range(len(time_slots)):
    for room in rooms:
        model.Add(
            sum(
                timetable[(subj["Subject"], t)]
                for subj in subjects if subj["Room_type"] == room
            ) <= 1
        )

# (4) Teacher load (max hours per week = 16)
for teacher in teachers:
    model.Add(
        sum(
            timetable[(subj["Subject"], t)]
            for subj in subjects if subj["Teacher"] == teacher
            for t in range(len(time_slots))
        ) <= 16
    )

# -----------------------------
# Step 5: Solve
# -----------------------------
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 15  # time limit
status = solver.Solve(model)

# -----------------------------
# Step 6: Build Master Timetable
# -----------------------------
if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    print("\n✅ Timetable generated!")

    master_records = []
    for subj in subjects:
        subj_name = subj["Subject"]
        for t in range(len(time_slots)):
            if solver.Value(timetable[(subj_name, t)]) == 1:
                day, slot = time_slots[t]
                master_records.append({
                    "Day": day,
                    "Time Slot": slot,
                    "Course": subj["Course"],
                    "Section": subj["Section"],
                    "Subject": subj_name,
                    "Teacher": subj["Teacher"],
                    "Room": subj["Room_type"]
                })

    # Convert to DataFrame
    master_df = pd.DataFrame(master_records)

    # Show a small preview in console
    print("\nMaster Timetable (sample):\n", master_df.head(15))

    # Save to Excel for full inspection
    master_df.to_excel("master_timetable.xlsx", index=False)
    print("\n📂 Full master timetable saved as 'master_timetable.xlsx'")
else:
    print("❌ No feasible solution found.")
