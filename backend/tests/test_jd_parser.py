from app.nlp.jd_parser import extract_job_requirements


def test_acceptance_question_senior_data_engineer():
    # Straight from the proposal's acceptance test list.
    text = "Find the top 3 candidates for a Senior Data Engineer role requiring Python, AWS, and SQL."
    result = extract_job_requirements(text)
    assert result["required_skills"] == ["AWS", "Python", "SQL"]
    assert result["seniority"] == "Senior"


def test_acceptance_question_team_builder():
    # Straight from the proposal's acceptance test list.
    text = "Build a 4-person team for a 6-month NLP project requiring Python, NLP, and RAG."
    result = extract_job_requirements(text)
    assert result["required_skills"] == ["NLP", "Python", "RAG"]
    assert result["team_size"] == 4
    assert result["duration_months"] == 6


def test_optional_marker_splits_required_from_optional():
    text = "Requires Python and SQL. Experience with Docker is nice to have."
    result = extract_job_requirements(text)
    assert result["required_skills"] == ["Python", "SQL"]
    assert result["optional_skills"] == ["Docker"]


def test_skill_required_elsewhere_overrides_optional_mention():
    text = "Requires Python and Docker. Docker experience is preferred but not required."
    result = extract_job_requirements(text)
    assert "Docker" in result["required_skills"]
    assert "Docker" not in result["optional_skills"]


def test_missing_team_size_and_duration_return_none():
    text = "Looking for someone skilled in Python and SQL."
    result = extract_job_requirements(text)
    assert result["team_size"] is None
    assert result["duration_months"] is None
    assert result["seniority"] is None


def test_duration_in_weeks_converts_to_months():
    text = "A 12-week project requiring Python."
    result = extract_job_requirements(text)
    assert result["duration_months"] == 3