-- AI Talent & Workforce Matching Agent -- SQLite schema (local-dev stand-in for schema.sql)
-- No server needed: python db/seed_sqlite.py creates/updates db/talent_matching.db from this file.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS employees (
    eeid                TEXT PRIMARY KEY,
    full_name           TEXT NOT NULL,
    department          TEXT NOT NULL,
    hire_date           TEXT,
    salary              REAL,
    availability_status TEXT NOT NULL CHECK (availability_status IN ('Available', 'Partially Allocated', 'Fully Allocated')),
    available_from      TEXT
);

CREATE TABLE IF NOT EXISTS candidates (
    candidate_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    source_category  TEXT,
    raw_resume_text  TEXT NOT NULL,
    parsed_at        TEXT
);

CREATE TABLE IF NOT EXISTS skills (
    skill_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    canonical_name  TEXT UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS employee_skills (
    eeid              TEXT REFERENCES employees(eeid) ON DELETE CASCADE,
    skill_id          INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    proficiency       TEXT,
    years_experience  INTEGER,
    PRIMARY KEY (eeid, skill_id)
);

CREATE TABLE IF NOT EXISTS candidate_skills (
    candidate_id      INTEGER REFERENCES candidates(candidate_id) ON DELETE CASCADE,
    skill_id          INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    years_experience  INTEGER,
    PRIMARY KEY (candidate_id, skill_id)
);

CREATE TABLE IF NOT EXISTS projects (
    project_id       TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    domain           TEXT,
    description      TEXT,
    duration_months  INTEGER,
    team_size        INTEGER
);

CREATE TABLE IF NOT EXISTS project_requirements (
    project_id   TEXT REFERENCES projects(project_id) ON DELETE CASCADE,
    skill_id     INTEGER REFERENCES skills(skill_id) ON DELETE CASCADE,
    is_required  INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (project_id, skill_id)
);

CREATE TABLE IF NOT EXISTS employee_past_projects (
    eeid        TEXT REFERENCES employees(eeid) ON DELETE CASCADE,
    project_id  TEXT REFERENCES projects(project_id) ON DELETE CASCADE,
    role        TEXT,
    PRIMARY KEY (eeid, project_id)
);

CREATE TABLE IF NOT EXISTS training_courses (
    course_id        TEXT PRIMARY KEY,
    title            TEXT NOT NULL,
    skill_id         INTEGER REFERENCES skills(skill_id),
    duration_hours   INTEGER,
    format           TEXT,
    enrollment_link  TEXT
);

CREATE TABLE IF NOT EXISTS assignment_outcomes (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    eeid                TEXT REFERENCES employees(eeid) ON DELETE CASCADE,
    project_id          TEXT REFERENCES projects(project_id) ON DELETE CASCADE,
    skill_match         REAL,
    tenure_score        REAL,
    availability_score  REAL,
    weighted_score      REAL,
    outcome_label       INTEGER NOT NULL CHECK (outcome_label IN (0, 1))
);

CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tool_name   TEXT NOT NULL,
    inputs      TEXT,
    result      TEXT,
    cited_ids   TEXT
);

CREATE INDEX IF NOT EXISTS idx_employee_skills_skill ON employee_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_candidate_skills_skill ON candidate_skills(skill_id);
CREATE INDEX IF NOT EXISTS idx_employees_department ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_availability ON employees(availability_status);
CREATE INDEX IF NOT EXISTS idx_audit_log_tool ON audit_log(tool_name);