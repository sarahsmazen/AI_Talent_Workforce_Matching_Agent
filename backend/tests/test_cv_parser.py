from app.nlp.cv_parser import build_surface_forms, extract_skills
from app.nlp.skill_normalizer import SkillNormalizer

normalizer = SkillNormalizer()
surface_forms = build_surface_forms(normalizer)


def test_extracts_plain_skill_mentions():
    text = "Skilled in Python and SQL with 5 years of experience."
    assert extract_skills(text, surface_forms) == ["Python", "SQL"]


def test_extracts_synonyms_and_normalizes_them():
    text = "Strong background in ML and k8s."
    assert extract_skills(text, surface_forms) == ["Kubernetes", "Machine Learning"]


def test_extracts_symbol_containing_skills():
    text = "Backend in C++ with CI/CD pipelines."
    result = extract_skills(text, surface_forms)
    assert "C++" in result
    assert "CI/CD" in result


def test_no_false_positive_on_substring():
    # "Java" should not fire "JavaScript", and "React" alone shouldn't imply "ReactJS"-style
    # false matches -- word-boundary matching should keep these separate.
    text = "5 years of Java backend development."
    result = extract_skills(text, surface_forms)
    assert "Java" in result
    assert "JavaScript" not in result


def test_empty_text_returns_empty_list():
    assert extract_skills("", surface_forms) == []
    assert extract_skills(None, surface_forms) == []


def test_unrelated_text_returns_empty_list():
    text = "Passionate chef with 10 years in fine dining and menu design."
    assert extract_skills(text, surface_forms) == []