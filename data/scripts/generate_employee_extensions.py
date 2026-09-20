"""
Phase 1 data authoring: extend the real Employee Sample Data (Kaggle, Leen Hussein) with
Skills, Availability, and PastProjects, none of which exist in the source file.

Input:
    data/raw/employees_raw.csv   (download first -- see data/raw/README.md)
    data/generated/projects.json (run generate_projects_and_training.py first)
Output:
    data/generated/employees.csv             one row per employee, base fields + availability
    data/generated/employee_skills.csv        (eeid, skill, years_experience) -- many-to-many
    data/generated/employee_past_projects.csv (eeid, project_id, role)        -- many-to-many

Run:
    python data/scripts/generate_employee_extensions.py
"""
import csv
import json
import os
import random
from datetime import date, timedelta

random.seed(42)  # reproducible synthetic output

HERE = os.path.dirname(__file__)
RAW_PATH = os.path.join(HERE, "..", "raw", "employees_raw.csv")
PROJECTS_PATH = os.path.join(HERE, "..", "generated", "projects.json")
TAXONOMY_PATH = os.path.join(HERE, "skill_taxonomy.json")
OUT_DIR = os.path.join(HERE, "..", "generated")

# The public "Employee Sample Data" dataset commonly ships these columns. If your download
# uses different headers, edit this map (target_field -> tuple of acceptable source names)
# rather than the logic below.
COLUMN_CANDIDATES = {
    "eeid": ("EEID", "EmpID", "Employee ID", "employee_id"),
    "full_name": ("Full Name", "Employee_Name", "Name"),
    "department": ("Department", "Dept", "Business Unit"),
    "hire_date": ("Hire Date", "DateofHire", "hire_date"),
    "salary": ("Annual Salary", "Salary", "salary"),
}

AVAILABILITY_STATUSES = ["Available", "Partially Allocated", "Fully Allocated"]
AVAILABILITY_WEIGHTS = [0.35, 0.30, 0.35]


def resolve_columns(fieldnames):
    resolved = {}
    lower_map = {fn.lower().strip(): fn for fn in fieldnames}
    for target, candidates in COLUMN_CANDIDATES.items():
        for cand in candidates:
            if cand.lower() in lower_map:
                resolved[target] = lower_map[cand.lower()]
                break
        else:
            resolved[target] = None
    missing = [k for k, v in resolved.items() if v is None]
    if missing:
        print(f"WARNING: could not find source columns for {missing}. "
              f"Available columns: {fieldnames}. Edit COLUMN_CANDIDATES in this script.")
    return resolved


def parse_hire_year(raw_value):
    if not raw_value:
        return None
    for fmt_sep in ("/", "-"):
        parts = raw_value.split(fmt_sep)
        for p in parts:
            if len(p) == 4 and p.isdigit():
                return int(p)
    return None


def clean_salary(raw_value):
    """Strip currency formatting ('$141,604 ' -> '141604') so it parses as a number later."""
    if not raw_value:
        return ""
    return raw_value.replace("$", "").replace(",", "").strip()


def pick_skills(department, taxonomy):
    bias = taxonomy["department_skill_bias"].get(department, taxonomy["department_skill_bias"]["_default"])
    all_skills = taxonomy["canonical_skills"]
    n_biased = random.randint(2, min(5, len(bias)))
    chosen = set(random.sample(bias, n_biased))
    # sprinkle 1-3 skills from outside the department's usual set, so profiles aren't uniform
    n_extra = random.randint(1, 3)
    remaining = [s for s in all_skills if s not in chosen]
    chosen.update(random.sample(remaining, min(n_extra, len(remaining))))
    return list(chosen)


def main():
    with open(TAXONOMY_PATH) as f:
        taxonomy = json.load(f)

    if not os.path.exists(PROJECTS_PATH):
        raise SystemExit("Run generate_projects_and_training.py first -- projects.json not found.")
    with open(PROJECTS_PATH) as f:
        projects = json.load(f)
    project_ids = [p["project_id"] for p in projects]

    if not os.path.exists(RAW_PATH):
        raise SystemExit(f"{RAW_PATH} not found. See data/raw/README.md to download it first.")

    os.makedirs(OUT_DIR, exist_ok=True)
    today = date.today()

    with open(RAW_PATH, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        cols = resolve_columns(reader.fieldnames)
        rows = list(reader)

    employees_out, skills_out, past_projects_out = [], [], []

    for row in rows:
        eeid = row.get(cols["eeid"], "").strip() if cols["eeid"] else None
        if not eeid:
            continue
        department = row.get(cols["department"], "").strip() if cols["department"] else "_default"
        hire_year = parse_hire_year(row.get(cols["hire_date"], "")) if cols["hire_date"] else None
        tenure_years = max(0, today.year - hire_year) if hire_year else random.randint(0, 8)

        status = random.choices(AVAILABILITY_STATUSES, weights=AVAILABILITY_WEIGHTS, k=1)[0]
        if status == "Available":
            available_from = today.isoformat()
        else:
            available_from = (today + timedelta(days=random.randint(14, 180))).isoformat()

        employees_out.append({
            "eeid": eeid,
            "full_name": row.get(cols["full_name"], "") if cols["full_name"] else "",
            "department": department,
            "hire_date": row.get(cols["hire_date"], "") if cols["hire_date"] else "",
            "salary": clean_salary(row.get(cols["salary"], "")) if cols["salary"] else "",
            "availability_status": status,
            "available_from": available_from,
        })

        for skill in pick_skills(department, taxonomy):
            skills_out.append({
                "eeid": eeid,
                "skill": skill,
                "years_experience": random.randint(1, max(1, min(tenure_years, 10))),
            })

        # correlate past projects loosely with the employee's own skills: if a project's
        # required skills overlap with what this employee has, they're a plausible alum
        employee_skillset = {s["skill"] for s in skills_out if s["eeid"] == eeid}
        candidate_projects = [
            p for p in projects
            if employee_skillset.intersection({r["skill"] for r in p["requirements"]})
        ]
        n_past = random.randint(0, min(3, len(candidate_projects))) if candidate_projects else 0
        for proj in random.sample(candidate_projects, n_past) if n_past else []:
            past_projects_out.append({
                "eeid": eeid,
                "project_id": proj["project_id"],
                "role": random.choice(["Contributor", "Lead", "Reviewer"]),
            })

    def write_csv(path, rows, fieldnames):
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    write_csv(os.path.join(OUT_DIR, "employees.csv"), employees_out,
              ["eeid", "full_name", "department", "hire_date", "salary", "availability_status", "available_from"])
    write_csv(os.path.join(OUT_DIR, "employee_skills.csv"), skills_out, ["eeid", "skill", "years_experience"])
    write_csv(os.path.join(OUT_DIR, "employee_past_projects.csv"), past_projects_out, ["eeid", "project_id", "role"])

    print(f"Wrote {len(employees_out)} employees, {len(skills_out)} skill rows, "
          f"{len(past_projects_out)} past-project rows -> data/generated/")


if __name__ == "__main__":
    main()