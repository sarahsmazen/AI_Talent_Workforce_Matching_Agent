"""
Phase 1 data authoring: synthetic Assignment Outcomes for ML training (Phase 5).

Generates (employee, project) pairs with a weighted score from skill match + tenure +
availability, plus noise, then samples a binary outcome label from that score. This gives
the Phase 5 classifier a real, learnable pattern to beat the weighted-score baseline on --
not random labels, which no classifier could learn from.

Input:
    data/generated/employees.csv
    data/generated/employee_skills.csv
    data/generated/projects.json
Output:
    data/generated/assignment_outcomes.csv

Run:
    python data/scripts/generate_assignment_outcomes.py
"""
import csv
import json
import os
import random

random.seed(7)

HERE = os.path.dirname(__file__)
GEN_DIR = os.path.join(HERE, "..", "generated")

# Weights here intentionally mirror the *shape* of the weighted-score baseline
# (skill match dominant, then experience, then availability) without needing every
# field the full baseline uses (education/certifications aren't in this dataset).
W_SKILL, W_TENURE, W_AVAILABILITY = 0.5, 0.3, 0.2
NOISE_STDDEV = 0.15
PAIRS_PER_EMPLOYEE = 4  # how many (employee, project) pairs to synthesize per employee


def load_employees():
    with open(os.path.join(GEN_DIR, "employees.csv")) as f:
        return list(csv.DictReader(f))


def load_employee_skills():
    skills_by_eeid = {}
    with open(os.path.join(GEN_DIR, "employee_skills.csv")) as f:
        for row in csv.DictReader(f):
            skills_by_eeid.setdefault(row["eeid"], set()).add(row["skill"])
    return skills_by_eeid


def load_projects():
    with open(os.path.join(GEN_DIR, "projects.json")) as f:
        return json.load(f)


def availability_score(status):
    return {"Available": 1.0, "Partially Allocated": 0.5, "Fully Allocated": 0.0}.get(status, 0.0)


def tenure_score(hire_date_str):
    # crude: just use presence of a 4-digit year; the extension script already computed
    # tenure once, so this is a light re-derivation good enough for synthetic labels.
    import re
    m = re.search(r"(19|20)\d{2}", hire_date_str or "")
    if not m:
        return random.uniform(0.2, 0.8)
    year = int(m.group(0))
    from datetime import date
    years = max(0, date.today().year - year)
    return min(years / 10.0, 1.0)


def main():
    employees = load_employees()
    skills_by_eeid = load_employee_skills()
    projects = load_projects()

    rows = []
    for emp in employees:
        eeid = emp["eeid"]
        emp_skills = skills_by_eeid.get(eeid, set())
        avail = availability_score(emp["availability_status"])
        tenure = tenure_score(emp["hire_date"])

        sampled_projects = random.sample(projects, min(PAIRS_PER_EMPLOYEE, len(projects)))
        for proj in sampled_projects:
            required = [r["skill"] for r in proj["requirements"] if r["is_required"]]
            optional = [r["skill"] for r in proj["requirements"] if not r["is_required"]]
            all_req = required + optional
            skill_match = len(emp_skills.intersection(all_req)) / len(all_req) if all_req else 0.0

            weighted_score = W_SKILL * skill_match + W_TENURE * tenure + W_AVAILABILITY * avail
            noisy_prob = min(1.0, max(0.0, weighted_score + random.gauss(0, NOISE_STDDEV)))
            outcome_label = 1 if random.random() < noisy_prob else 0

            rows.append({
                "eeid": eeid,
                "project_id": proj["project_id"],
                "skill_match": round(skill_match, 4),
                "tenure_score": round(tenure, 4),
                "availability_score": round(avail, 4),
                "weighted_score": round(weighted_score, 4),
                "outcome_label": outcome_label,
            })

    out_path = os.path.join(GEN_DIR, "assignment_outcomes.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "eeid", "project_id", "skill_match", "tenure_score",
            "availability_score", "weighted_score", "outcome_label"])
        writer.writeheader()
        writer.writerows(rows)

    positive_rate = sum(r["outcome_label"] for r in rows) / len(rows) if rows else 0
    print(f"Wrote {len(rows)} assignment-outcome rows -> {out_path}")
    print(f"Positive outcome rate: {positive_rate:.1%} "
          f"(watch for this being too close to 0%/100% -- adjust NOISE_STDDEV if so)")


if __name__ == "__main__":
    main()
