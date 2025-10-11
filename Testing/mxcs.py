# dynamic_timetable_generator.py
import os
import random
import pandas as pd

# ---------------------------
# CONFIG: courses & semesters
# ---------------------------
COURSES = {
    "BSc_Hons_CS": {
        1: ["Python Programming", "Digital Logic", "Mathematics-I"],
        3: ["Data Structures", "Operating Systems", "Discrete Maths"],
        5: ["DBMS", "Computer Networks", "Theory of Computation"],
        7: ["Machine Learning", "Cloud Computing", "Compiler Design"]
    },
    "BSc_Physical_CS": {
        1: ["C Programming", "Physics-I", "Mathematics-I"],
        3: ["Data Structures", "Electronics", "Linear Algebra"],
        5: ["DBMS", "Numerical Methods", "Operating Systems"],
        7: ["AI", "Parallel Computing", "Computer Graphics"]
    },
    "BA_CA": {
        1: ["Python Basics", "Web Development-I", "Mathematics-I"],
        3: ["Data Structures", "Web Development-II", "Statistics"],
        5: ["DBMS", "Software Engineering", "Operating Systems"],
        7: ["AI", "Big Data Analytics", "Project Work"]
    }
}

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
SLOTS = [
    "8:30-9:30", "9:30-10:30", "10:30-11:30",
    "11:30-12:30", "12:30-13:30",  # GE
    "13:30-14:30", "14:30-15:30", "15:30-16:30", "16:30-17:30"
]
GE_SLOT = "12:30-13:30"
LUNCH_SLOT = "13:30-14:30"

OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ---------------------------
# Helpers
# ---------------------------
def make_empty_table():
    table = {}
    for d in DAYS:
        table[d] = {}
        for s in SLOTS:
            if s == GE_SLOT:
                table[d][s] = "GE"
            elif s == LUNCH_SLOT:
                table[d][s] = "LUNCH"
            else:
                table[d][s] = "FREE"
    return table

def find_two_consecutive_free(table, avoid_slots=None):
    avoid = set(avoid_slots or [])
    for day in random.sample(DAYS, len(DAYS)):
        for i in range(len(SLOTS)-1):
            s1, s2 = SLOTS[i], SLOTS[i+1]
            if s1 in avoid or s2 in avoid: continue
            if table[day][s1] == "FREE" and table[day][s2] == "FREE":
                return day, i
    return None, None

def place_two_consecutive(table, day, start_idx, label):
    s1, s2 = SLOTS[start_idx], SLOTS[start_idx+1]
    table[day][s1] = label
    table[day][s2] = label
    # 1 hr break after 2-hr class
    if start_idx+2 < len(SLOTS) and table[day][SLOTS[start_idx+2]] == "FREE":
        table[day][SLOTS[start_idx+2]] = "BREAK"

def find_single_free_slots(table, count, prefer_times=None, avoid_slots=None):
    res, avoid = [], set(avoid_slots or [])
    prefs = prefer_times or []
    ordered_slots = prefs + [s for s in SLOTS if s not in prefs]
    for day in random.sample(DAYS, len(DAYS)):
        for s in ordered_slots:
            if s in avoid: continue
            if table[day][s] == "FREE":
                res.append((day, s))
                if len(res) >= count: return res
    return res

# ---------------------------
# Timetable generator for 1 batch
# ---------------------------
def schedule_batch(subject_list):
    table = make_empty_table()
    warnings = []

    # Labs first
    for subj in subject_list:
        lab_label = f"{subj} (Lab)"
        day, start_idx = find_two_consecutive_free(table, avoid_slots=[GE_SLOT, LUNCH_SLOT])
        if day:
            place_two_consecutive(table, day, start_idx, lab_label)
        else:
            warnings.append(f"Lab for {subj} could not be placed!")

    # Theory 2x1hr preferred
    for subj in subject_list:
        th_label = f"{subj} (Th)"
        pref_slots = ["8:30-9:30","9:30-10:30","10:30-11:30","11:30-12:30","14:30-15:30","15:30-16:30","16:30-17:30"]
        singles = find_single_free_slots(table, 2, prefer_times=pref_slots, avoid_slots=[GE_SLOT,LUNCH_SLOT])
        if len(singles) >= 2 and singles[0][0] != singles[1][0]:
            for day, s in singles[:2]: table[day][s] = th_label
        else:
            day, idx = find_two_consecutive_free(table, avoid_slots=[GE_SLOT,LUNCH_SLOT])
            if day: place_two_consecutive(table, day, idx, th_label)
            else:
                warnings.append(f"Theory for {subj} could not be placed!")

    # remaining FREE -> '-'
    for d in DAYS:
        for s in SLOTS:
            if table[d][s] == "FREE": table[d][s] = "-"

    return table, warnings

# ---------------------------
# MAIN
# ---------------------------
course_input = input("Enter course (BSc_Hons_CS / BSc_Physical_CS / BA_CA): ")
semester_input = int(input("Enter semester (1/3/5/7): "))

subjects = COURSES.get(course_input, {}).get(semester_input)
if not subjects:
    print("❌ Invalid course or semester!")
    exit()

table, warns = schedule_batch(subjects)
df = pd.DataFrame([{ "Day": d, **table[d]} for d in DAYS])

out_file = os.path.join(OUTPUT_DIR, f"{course_input}_Sem{semester_input}.csv")
df.to_csv(out_file, index=False)
print(f"✅ Timetable saved as '{out_file}'")
if warns:
    print("\n⚠️ Warnings:")
    for w in warns: print(" -", w)
