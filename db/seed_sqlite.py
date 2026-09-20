"""
Phase 1 (SQLite variant): load data/generated/* (and data/raw/resumes_raw.csv) into a local
SQLite database file -- no separate database server needed, just Python's built-in sqlite3.

Run:
    python db/seed_sqlite.py

Creates/updates: db/talent_matching.db
Idempotent: safe to re-run (tables without a natural unique key are cleared and reloaded).
"""
import csv
import json
import os
import sqlite3

HERE = os.path.dirname(__file__)
GEN_DIR = os.path.join(HERE, "..", "data", "generated")
RAW_DIR = os.path.join(HERE, "..", "data", "raw")
DB_PATH = os.path.join(HERE, "talent_matching.db")


def get_or_create_skill(cur, skill_cache, name):
    if name in skill_cache:
        return skill_cache[name]
    cur.execute("INSERT OR IGNORE INTO skills (canonical_name) VALUES (?)", (name,))
    cur.execute("SELECT skill_id FROM skills WHERE canonical_name = ?", (name,))
    skill_id = cur.fetchone()[0]
    skill_cache[name] = skill_id
    return skill_id


def load_employees(cur):
    path = os.path.join(GEN_DIR, "employees.csv")
    if not os.path.exists(path):
        print(f"SKIP employees: {path} not found -- run generate_employee_extensions.py first")
        return
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        cur.execute(
            """
            INSERT INTO employees (eeid, full_name, department, hire_date, salary, availability_status, available_from)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(eeid) DO UPDATE SET
                full_name = excluded.full_name, department = excluded.department,
                hire_date = excluded.hire_date, salary = excluded.salary,
                availability_status = excluded.availability_status, available_from = excluded.available_from
            """,
            (r["eeid"], r["full_name"], r["department"], r["hire_date"] or None,
             float(r["salary"]) if r["salary"] else None, r["availability_status"], r["available_from"] or None),
        )
    print(f"Loaded {len(rows)} employees")


def load_employee_skills(cur, skill_cache):
    path = os.path.join(GEN_DIR, "employee_skills.csv")
    if not os.path.exists(path):
        print(f"SKIP employee_skills: {path} not found")
        return
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        skill_id = get_or_create_skill(cur, skill_cache, r["skill"])
        cur.execute(
            """
            INSERT INTO employee_skills (eeid, skill_id, years_experience)
            VALUES (?, ?, ?)
            ON CONFLICT(eeid, skill_id) DO UPDATE SET years_experience = excluded.years_experience
            """,
            (r["eeid"], skill_id, r["years_experience"] or None),
        )
    print(f"Loaded {len(rows)} employee_skills rows")


def load_projects(cur, skill_cache):
    path = os.path.join(GEN_DIR, "projects.json")
    if not os.path.exists(path):
        print(f"SKIP projects: {path} not found -- run generate_projects_and_training.py first")
        return
    with open(path) as f:
        projects = json.load(f)
    for p in projects:
        cur.execute(
            """
            INSERT INTO projects (project_id, title, domain, duration_months, team_size)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(project_id) DO UPDATE SET
                title = excluded.title, domain = excluded.domain,
                duration_months = excluded.duration_months, team_size = excluded.team_size
            """,
            (p["project_id"], p["title"], p["domain"], p["duration_months"], p["team_size"]),
        )
        for req in p["requirements"]:
            skill_id = get_or_create_skill(cur, skill_cache, req["skill"])
            cur.execute(
                """
                INSERT INTO project_requirements (project_id, skill_id, is_required)
                VALUES (?, ?, ?)
                ON CONFLICT(project_id, skill_id) DO UPDATE SET is_required = excluded.is_required
                """,
                (p["project_id"], skill_id, 1 if req["is_required"] else 0),
            )
    print(f"Loaded {len(projects)} projects")


def load_past_projects(cur):
    path = os.path.join(GEN_DIR, "employee_past_projects.csv")
    if not os.path.exists(path):
        print(f"SKIP employee_past_projects: {path} not found")
        return
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        cur.execute(
            """
            INSERT INTO employee_past_projects (eeid, project_id, role)
            VALUES (?, ?, ?)
            ON CONFLICT(eeid, project_id) DO UPDATE SET role = excluded.role
            """,
            (r["eeid"], r["project_id"], r["role"]),
        )
    print(f"Loaded {len(rows)} employee_past_projects rows")


def load_training_catalog(cur, skill_cache):
    path = os.path.join(GEN_DIR, "training_catalog.json")
    if not os.path.exists(path):
        print(f"SKIP training_catalog: {path} not found")
        return
    with open(path) as f:
        courses = json.load(f)
    for c in courses:
        skill_id = get_or_create_skill(cur, skill_cache, c["skill"])
        cur.execute(
            """
            INSERT INTO training_courses (course_id, title, skill_id, duration_hours, format, enrollment_link)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(course_id) DO UPDATE SET
                title = excluded.title, skill_id = excluded.skill_id,
                duration_hours = excluded.duration_hours, format = excluded.format,
                enrollment_link = excluded.enrollment_link
            """,
            (c["course_id"], c["title"], skill_id, c["duration_hours"], c["format"], c["enrollment_link"]),
        )
    print(f"Loaded {len(courses)} training courses")


def load_candidates(cur):
    path = os.path.join(RAW_DIR, "resumes_raw.csv")
    if not os.path.exists(path):
        print(f"SKIP candidates: {path} not found -- see data/raw/README.md")
        return
    with open(path, newline="", encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        print("SKIP candidates: resumes_raw.csv is empty")
        return
    category_col = next((c for c in ("Category", "category") if c in rows[0]), None)
    text_col = next((c for c in ("Resume_str", "Resume", "resume", "Resume_html") if c in rows[0]), None)
    if not text_col:
        print(f"WARNING: couldn't find a resume-text column. Columns seen: {list(rows[0].keys())}")
        return
    count = 0
    for r in rows:
        cur.execute(
            "INSERT INTO candidates (source_category, raw_resume_text) VALUES (?, ?)",
            (r.get(category_col), r.get(text_col)),
        )
        count += 1
    print(f"Loaded {count} candidates (unparsed -- Phase 3's NLP pipeline fills candidate_skills)")


def load_assignment_outcomes(cur):
    path = os.path.join(GEN_DIR, "assignment_outcomes.csv")
    if not os.path.exists(path):
        print(f"SKIP assignment_outcomes: {path} not found -- run generate_assignment_outcomes.py first")
        return
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        cur.execute(
            """
            INSERT INTO assignment_outcomes
                (eeid, project_id, skill_match, tenure_score, availability_score, weighted_score, outcome_label)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (r["eeid"], r["project_id"], r["skill_match"], r["tenure_score"],
             r["availability_score"], r["weighted_score"], r["outcome_label"]),
        )
    print(f"Loaded {len(rows)} assignment_outcomes rows")


def main():
    schema_path = os.path.join(HERE, "schema_sqlite.sql")
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    with open(schema_path) as f:
        conn.executescript(f.read())

    skill_cache = {}
    cur = conn.cursor()
    try:
        # tables with no natural unique key get cleared before reload, so re-running this
        # script doesn't duplicate rows
        cur.execute("DELETE FROM candidates")
        cur.execute("DELETE FROM assignment_outcomes")

        load_employees(cur)
        load_projects(cur, skill_cache)
        load_employee_skills(cur, skill_cache)
        load_past_projects(cur)
        load_training_catalog(cur, skill_cache)
        load_candidates(cur)
        load_assignment_outcomes(cur)
        conn.commit()
        print(f"Seed complete. Database file: {DB_PATH}")
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    main()