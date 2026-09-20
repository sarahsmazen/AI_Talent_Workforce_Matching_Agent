"""
Phase 1 data authoring: Projects & Training Catalog.

No public dataset fits internal staffing requests or course catalogs, so these ~20 project
briefs and ~25 training courses are hand-authored here. Edit the PROJECTS / COURSES lists
directly to add more variety — this script just validates and writes them to JSON.

Run:
    python data/scripts/generate_projects_and_training.py
Writes:
    data/generated/projects.json
    data/generated/training_catalog.json
"""
import json
import os

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "generated")

# Each project: id, title, domain, duration (months), team_size, and a list of
# (skill, is_required) requirement pairs. Required skills are the hard filter;
# optional skills add to the match score without being a hard blocker.
PROJECTS = [
    {"project_id": "PRJ-001", "title": "Customer Churn Prediction Platform", "domain": "Data Science",
     "duration_months": 4, "team_size": 3,
     "requirements": [("Python", True), ("Machine Learning", True), ("SQL", True), ("Tableau", False)]},
    {"project_id": "PRJ-002", "title": "NLP-Powered Support Ticket Router", "domain": "AI/NLP",
     "duration_months": 6, "team_size": 4,
     "requirements": [("Python", True), ("NLP", True), ("RAG", False), ("FastAPI", True)]},
    {"project_id": "PRJ-003", "title": "Cloud Migration — Legacy ERP to AWS", "domain": "Cloud/Infra",
     "duration_months": 5, "team_size": 5,
     "requirements": [("AWS", True), ("DevOps", True), ("Linux", True), ("Cybersecurity", False)]},
    {"project_id": "PRJ-004", "title": "Real-Time Analytics Dashboard", "domain": "Data Engineering",
     "duration_months": 3, "team_size": 3,
     "requirements": [("Data Engineering", True), ("Spark", True), ("Power BI", False), ("SQL", True)]},
    {"project_id": "PRJ-005", "title": "Internal RAG Knowledge Assistant", "domain": "AI/NLP",
     "duration_months": 4, "team_size": 3,
     "requirements": [("RAG", True), ("LangChain", True), ("Python", True), ("NLP", False)]},
    {"project_id": "PRJ-006", "title": "Mobile-First Customer Portal Rebuild", "domain": "Frontend",
     "duration_months": 5, "team_size": 4,
     "requirements": [("React", True), ("JavaScript", True), ("TypeScript", False), ("Frontend Development", True)]},
    {"project_id": "PRJ-007", "title": "Kubernetes Platform Standardization", "domain": "Cloud/Infra",
     "duration_months": 6, "team_size": 4,
     "requirements": [("Kubernetes", True), ("Docker", True), ("DevOps", True), ("CI/CD", False)]},
    {"project_id": "PRJ-008", "title": "Sales Pipeline CRM Overhaul", "domain": "Sales Ops",
     "duration_months": 3, "team_size": 3,
     "requirements": [("CRM", True), ("Sales", True), ("Data Analysis", False)]},
    {"project_id": "PRJ-009", "title": "Computer Vision QA Inspection Line", "domain": "AI/CV",
     "duration_months": 6, "team_size": 4,
     "requirements": [("Computer Vision", True), ("Deep Learning", True), ("Python", True), ("PyTorch", False)]},
    {"project_id": "PRJ-010", "title": "HR Workforce Analytics Rollout", "domain": "HR Tech",
     "duration_months": 3, "team_size": 2,
     "requirements": [("HR Management", True), ("Data Analysis", True), ("Power BI", False)]},
    {"project_id": "PRJ-011", "title": "Financial Forecasting Model Refresh", "domain": "Finance",
     "duration_months": 4, "team_size": 2,
     "requirements": [("Financial Modeling", True), ("Excel", True), ("Python", False)]},
    {"project_id": "PRJ-012", "title": "API Gateway & Backend Consolidation", "domain": "Backend",
     "duration_months": 5, "team_size": 4,
     "requirements": [("Backend Development", True), ("FastAPI", True), ("REST API Design", True), ("SQL", False)]},
    {"project_id": "PRJ-013", "title": "Marketing Attribution & SEO Overhaul", "domain": "Marketing",
     "duration_months": 3, "team_size": 2,
     "requirements": [("SEO", True), ("Marketing", True), ("Data Analysis", False)]},
    {"project_id": "PRJ-014", "title": "Enterprise Cybersecurity Audit", "domain": "Security",
     "duration_months": 4, "team_size": 3,
     "requirements": [("Cybersecurity", True), ("Network Administration", True), ("Linux", False)]},
    {"project_id": "PRJ-015", "title": "6-Month NLP Contract Analysis Engine", "domain": "AI/NLP",
     "duration_months": 6, "team_size": 4,
     "requirements": [("Python", True), ("NLP", True), ("RAG", True), ("Backend Development", False)]},
    {"project_id": "PRJ-016", "title": "Data Warehouse ETL Modernization", "domain": "Data Engineering",
     "duration_months": 5, "team_size": 3,
     "requirements": [("ETL", True), ("Data Engineering", True), ("SQL", True), ("Spark", False)]},
    {"project_id": "PRJ-017", "title": "Agile Transformation — PMO Standup", "domain": "Program Mgmt",
     "duration_months": 2, "team_size": 2,
     "requirements": [("Agile", True), ("Scrum", True), ("Stakeholder Management", False)]},
    {"project_id": "PRJ-018", "title": "Multi-Cloud Cost Optimization", "domain": "Cloud/Infra",
     "duration_months": 3, "team_size": 3,
     "requirements": [("AWS", True), ("Azure", False), ("GCP", False), ("Cloud Architecture", True)]},
    {"project_id": "PRJ-019", "title": "Employee Self-Service HR Portal", "domain": "HR Tech",
     "duration_months": 4, "team_size": 3,
     "requirements": [("React", True), ("FastAPI", True), ("HR Management", False)]},
    {"project_id": "PRJ-020", "title": "Senior Data Engineer Hiring Sprint Support", "domain": "Data Engineering",
     "duration_months": 2, "team_size": 1,
     "requirements": [("Python", True), ("AWS", True), ("SQL", True)]},
]

# Each course: id, title, the ONE skill it primarily addresses (matches the taxonomy),
# duration in hours, format, and a placeholder enrollment link.
COURSES = [
    {"course_id": "CRS-001", "title": "Python for Data Professionals", "skill": "Python", "duration_hours": 20, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/python-data"},
    {"course_id": "CRS-002", "title": "Applied Machine Learning Fundamentals", "skill": "Machine Learning", "duration_hours": 30, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/ml-fundamentals"},
    {"course_id": "CRS-003", "title": "Deep Learning with PyTorch", "skill": "Deep Learning", "duration_hours": 25, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/dl-pytorch"},
    {"course_id": "CRS-004", "title": "TensorFlow in Production", "skill": "TensorFlow", "duration_hours": 18, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/tf-production"},
    {"course_id": "CRS-005", "title": "NLP: From Tokens to Transformers", "skill": "NLP", "duration_hours": 22, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/nlp-transformers"},
    {"course_id": "CRS-006", "title": "Computer Vision Bootcamp", "skill": "Computer Vision", "duration_hours": 28, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/cv-bootcamp"},
    {"course_id": "CRS-007", "title": "Building RAG Systems", "skill": "RAG", "duration_hours": 15, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/rag-systems"},
    {"course_id": "CRS-008", "title": "LangChain for Agent Workflows", "skill": "LangChain", "duration_hours": 12, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/langchain-agents"},
    {"course_id": "CRS-009", "title": "AWS Solutions Architect Prep", "skill": "AWS", "duration_hours": 35, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/aws-architect"},
    {"course_id": "CRS-010", "title": "Azure Fundamentals", "skill": "Azure", "duration_hours": 16, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/azure-fundamentals"},
    {"course_id": "CRS-011", "title": "Google Cloud Essentials", "skill": "GCP", "duration_hours": 16, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/gcp-essentials"},
    {"course_id": "CRS-012", "title": "Docker & Containerization", "skill": "Docker", "duration_hours": 10, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/docker-basics"},
    {"course_id": "CRS-013", "title": "Kubernetes for Platform Teams", "skill": "Kubernetes", "duration_hours": 24, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/k8s-platform"},
    {"course_id": "CRS-014", "title": "DevOps & CI/CD Pipelines", "skill": "DevOps", "duration_hours": 20, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/devops-cicd"},
    {"course_id": "CRS-015", "title": "Linux Systems Administration", "skill": "Linux", "duration_hours": 18, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/linux-sysadmin"},
    {"course_id": "CRS-016", "title": "SQL for Analytics", "skill": "SQL", "duration_hours": 14, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/sql-analytics"},
    {"course_id": "CRS-017", "title": "Data Engineering with Spark", "skill": "Spark", "duration_hours": 26, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/spark-data-eng"},
    {"course_id": "CRS-018", "title": "Modern ETL Pipeline Design", "skill": "ETL", "duration_hours": 15, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/etl-design"},
    {"course_id": "CRS-019", "title": "React for Production Apps", "skill": "React", "duration_hours": 20, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/react-production"},
    {"course_id": "CRS-020", "title": "FastAPI Backend Development", "skill": "FastAPI", "duration_hours": 12, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/fastapi-backend"},
    {"course_id": "CRS-021", "title": "System Design for Scale", "skill": "System Design", "duration_hours": 22, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/system-design"},
    {"course_id": "CRS-022", "title": "Cybersecurity Fundamentals", "skill": "Cybersecurity", "duration_hours": 20, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/cybersecurity-fundamentals"},
    {"course_id": "CRS-023", "title": "Power BI for Business Analysts", "skill": "Power BI", "duration_hours": 14, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/powerbi-analysts"},
    {"course_id": "CRS-024", "title": "Agile & Scrum Certification Prep", "skill": "Scrum", "duration_hours": 16, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/agile-scrum"},
    {"course_id": "CRS-025", "title": "Financial Modeling in Excel", "skill": "Financial Modeling", "duration_hours": 18, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/financial-modeling"},
    # CRS-026+: added to guarantee every project-required skill has at least one remedy
    # (the sanity check below will flag any that still slip through). This pushes the
    # catalog past the ~25-course estimate in the proposal -- trim freely if you'd rather
    # keep it tighter and accept a couple of ungrounded skill gaps.
    {"course_id": "CRS-026", "title": "Agile Foundations", "skill": "Agile", "duration_hours": 8, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/agile-foundations"},
    {"course_id": "CRS-027", "title": "Backend Development with Python", "skill": "Backend Development", "duration_hours": 20, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/backend-python"},
    {"course_id": "CRS-028", "title": "CI/CD Pipelines in Practice", "skill": "CI/CD", "duration_hours": 10, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/cicd-practice"},
    {"course_id": "CRS-029", "title": "CRM Platform Administration", "skill": "CRM", "duration_hours": 10, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/crm-admin"},
    {"course_id": "CRS-030", "title": "Cloud Architecture Patterns", "skill": "Cloud Architecture", "duration_hours": 20, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/cloud-architecture"},
    {"course_id": "CRS-031", "title": "Data Analysis with Python & Excel", "skill": "Data Analysis", "duration_hours": 16, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/data-analysis"},
    {"course_id": "CRS-032", "title": "Data Engineering Foundations", "skill": "Data Engineering", "duration_hours": 22, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/data-engineering-foundations"},
    {"course_id": "CRS-033", "title": "Excel for Business Analysis", "skill": "Excel", "duration_hours": 8, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/excel-business"},
    {"course_id": "CRS-034", "title": "Frontend Development Essentials", "skill": "Frontend Development", "duration_hours": 18, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/frontend-essentials"},
    {"course_id": "CRS-035", "title": "HR Management Certificate", "skill": "HR Management", "duration_hours": 20, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/hr-management"},
    {"course_id": "CRS-036", "title": "Modern JavaScript", "skill": "JavaScript", "duration_hours": 16, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/modern-javascript"},
    {"course_id": "CRS-037", "title": "Marketing Analytics Fundamentals", "skill": "Marketing", "duration_hours": 14, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/marketing-analytics"},
    {"course_id": "CRS-038", "title": "Network Administration Basics", "skill": "Network Administration", "duration_hours": 18, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/network-admin"},
    {"course_id": "CRS-039", "title": "Deep Learning with PyTorch (Applied)", "skill": "PyTorch", "duration_hours": 20, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/pytorch-applied"},
    {"course_id": "CRS-040", "title": "REST API Design Principles", "skill": "REST API Design", "duration_hours": 10, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/rest-api-design"},
    {"course_id": "CRS-041", "title": "SEO Strategy & Execution", "skill": "SEO", "duration_hours": 10, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/seo-strategy"},
    {"course_id": "CRS-042", "title": "Consultative Sales Skills", "skill": "Sales", "duration_hours": 12, "format": "Cohort", "enrollment_link": "https://learning.internal/courses/consultative-sales"},
    {"course_id": "CRS-043", "title": "Stakeholder Management for Leads", "skill": "Stakeholder Management", "duration_hours": 8, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/stakeholder-management"},
    {"course_id": "CRS-044", "title": "Tableau for Business Intelligence", "skill": "Tableau", "duration_hours": 16, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/tableau-bi"},
    {"course_id": "CRS-045", "title": "TypeScript for React Developers", "skill": "TypeScript", "duration_hours": 12, "format": "Self-paced", "enrollment_link": "https://learning.internal/courses/typescript-react"},
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)

    projects_out = []
    for p in PROJECTS:
        projects_out.append({
            "project_id": p["project_id"],
            "title": p["title"],
            "domain": p["domain"],
            "duration_months": p["duration_months"],
            "team_size": p["team_size"],
            "requirements": [{"skill": s, "is_required": req} for s, req in p["requirements"]],
        })

    with open(os.path.join(OUT_DIR, "projects.json"), "w") as f:
        json.dump(projects_out, f, indent=2)

    with open(os.path.join(OUT_DIR, "training_catalog.json"), "w") as f:
        json.dump(COURSES, f, indent=2)

    print(f"Wrote {len(projects_out)} projects -> data/generated/projects.json")
    print(f"Wrote {len(COURSES)} courses -> data/generated/training_catalog.json")

    # Sanity check: every skill referenced by a project requirement should have at least
    # one course that remedies it, otherwise identify_skill_gaps() can surface a gap with
    # no possible training recommendation.
    covered = {c["skill"] for c in COURSES}
    required_skills = {req["skill"] for p in projects_out for req in p["requirements"]}
    uncovered = sorted(required_skills - covered)
    if uncovered:
        print(f"WARNING: no course covers these project-required skills: {uncovered}")


if __name__ == "__main__":
    main()
