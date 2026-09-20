"""
Phase 3 (start): run the CV skill-extractor over every candidate's raw_resume_text already
sitting in the database, and fill in candidate_skills.

Run (from the backend/ directory, so `app` is importable):
    python -m app.nlp.populate_candidate_skills

Idempotent: clears and reloads candidate_skills each run.
"""
import os
import sqlite3
from datetime import datetime, timezone

from app.nlp.cv_parser import build_surface_forms, extract_skills
from app.nlp.skill_normalizer import SkillNormalizer

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "..", "db", "talent_matching.db")


def get_or_create_skill(cur, skill_cache, name):
    if name in skill_cache:
        return skill_cache[name]
    cur.execute("INSERT OR IGNORE INTO skills (canonical_name) VALUES (?)", (name,))
    cur.execute("SELECT skill_id FROM skills WHERE canonical_name = ?", (name,))
    skill_id = cur.fetchone()[0]
    skill_cache[name] = skill_id
    return skill_id


def main():
    if not os.path.exists(DB_PATH):
        raise SystemExit(f"{DB_PATH} not found -- run db/seed_sqlite.py first.")

    normalizer = SkillNormalizer()
    surface_forms = build_surface_forms(normalizer)  # built once, reused for every candidate

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    skill_cache = {}

    cur.execute("DELETE FROM candidate_skills")  # idempotent re-run

    cur.execute("SELECT candidate_id, raw_resume_text FROM candidates")
    candidates = cur.fetchall()
    if not candidates:
        print("No candidates found -- run db/seed_sqlite.py (or seed.py) first.")
        return

    total_links = 0
    zero_skill_candidates = 0
    now = datetime.now(timezone.utc).isoformat()

    for candidate_id, raw_text in candidates:
        skills = extract_skills(raw_text or "", surface_forms)
        if not skills:
            zero_skill_candidates += 1
        for skill in skills:
            skill_id = get_or_create_skill(cur, skill_cache, skill)
            cur.execute(
                "INSERT OR IGNORE INTO candidate_skills (candidate_id, skill_id, years_experience) "
                "VALUES (?, ?, NULL)",
                (candidate_id, skill_id),
            )
            total_links += 1
        cur.execute("UPDATE candidates SET parsed_at = ? WHERE candidate_id = ?", (now, candidate_id))

    conn.commit()
    conn.close()

    zero_pct = zero_skill_candidates / len(candidates)
    print(f"Parsed {len(candidates)} candidates -> {total_links} candidate_skills rows")
    print(f"Candidates with zero recognized skills: {zero_skill_candidates} ({zero_pct:.1%})")
    if zero_pct > 0.15:
        print("That's a meaningful chunk -- expected for resume categories outside the current "
              "tech/business-leaning taxonomy (Aviation, Chef, Fitness, etc.). Extend "
              "data/scripts/skill_taxonomy.json with more categories/skills if you want better "
              "coverage there; this keyword-spotter only ever reports what it's told to look for.")


if __name__ == "__main__":
    main()