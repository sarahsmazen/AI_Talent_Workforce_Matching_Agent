"""
Phase 3: job/project requirement extraction -- parses a natural-language request (a job
posting, or a project manager's free-text ask like "Build a 4-person team for a 6-month
NLP project requiring Python, NLP, and RAG") into a structured requirement set the
matching engine can use.

Reuses the same skill vocabulary as cv_parser.py, plus lightweight regex/keyword rules for
team size, duration, seniority, and required-vs-optional skill splitting.
"""
import re
from typing import Dict, List, Optional

from app.nlp.cv_parser import build_surface_forms, extract_skills
from app.nlp.skill_normalizer import SkillNormalizer

_TEAM_SIZE_RE = re.compile(
    r"\b(\d+)[\s-]*(?:person|people|employees?|engineers?|developers?|members?)\b", re.IGNORECASE
)
_DURATION_MONTHS_RE = re.compile(r"\b(\d+)[\s-]*month", re.IGNORECASE)
_DURATION_WEEKS_RE = re.compile(r"\b(\d+)[\s-]*week", re.IGNORECASE)
_DURATION_YEARS_RE = re.compile(r"\b(\d+)[\s-]*year", re.IGNORECASE)

_SENIORITY_LEVELS = ["intern", "junior", "mid-level", "senior", "lead", "principal", "staff"]

# Phrases that mark whatever skill(s) appear in the same sentence as optional rather than
# required -- a simple, transparent rule rather than a guess about intent.
_OPTIONAL_MARKERS = [
    "nice to have", "nice-to-have", "preferred", "a plus", "bonus",
    "optional", "would be a plus", "ideally", "good to have",
]


def extract_team_size(text: str) -> Optional[int]:
    match = _TEAM_SIZE_RE.search(text)
    return int(match.group(1)) if match else None


def extract_duration_months(text: str) -> Optional[int]:
    m = _DURATION_MONTHS_RE.search(text)
    if m:
        return int(m.group(1))
    m = _DURATION_YEARS_RE.search(text)
    if m:
        return int(m.group(1)) * 12
    m = _DURATION_WEEKS_RE.search(text)
    if m:
        return max(1, round(int(m.group(1)) / 4.33))  # nearest month, minimum 1
    return None


def extract_seniority(text: str) -> Optional[str]:
    text_lower = text.lower()
    for level in _SENIORITY_LEVELS:
        if re.search(r"\b" + re.escape(level) + r"\b", text_lower):
            return level.title()
    return None


def _sentence_mentions_optional_marker(sentence: str) -> bool:
    sentence_lower = sentence.lower()
    return any(marker in sentence_lower for marker in _OPTIONAL_MARKERS)


def extract_job_requirements(text: str, normalizer: Optional[SkillNormalizer] = None) -> Dict:
    """Returns a structured requirement set:
    {
        "required_skills": [...canonical, sorted...],
        "optional_skills": [...canonical, sorted...],
        "team_size": int | None,
        "duration_months": int | None,
        "seniority": str | None,
    }

    Required-vs-optional split works at the sentence level: any skill mentioned in a
    sentence containing an "optional" marker phrase ("nice to have", "preferred", ...) is
    optional; everything else mentioned is required. A skill appearing in both an
    optional-marked sentence and elsewhere is treated as required (the stronger claim wins).
    """
    normalizer = normalizer or SkillNormalizer()
    surface_forms = build_surface_forms(normalizer)

    text = text or ""
    sentences = re.split(r"(?<=[.!?])\s+", text.strip()) if text.strip() else [text]

    required, optional = set(), set()
    for sentence in sentences:
        skills_in_sentence = extract_skills(sentence, surface_forms)
        if _sentence_mentions_optional_marker(sentence):
            optional.update(skills_in_sentence)
        else:
            required.update(skills_in_sentence)

    optional -= required  # required wins if a skill shows up both ways

    return {
        "required_skills": sorted(required),
        "optional_skills": sorted(optional),
        "team_size": extract_team_size(text),
        "duration_months": extract_duration_months(text),
        "seniority": extract_seniority(text),
    }


if __name__ == "__main__":
    import json

    sample = (
        "Build a 4-person team for a 6-month NLP project requiring Python, NLP, and RAG. "
        "Experience with Docker is nice to have. Looking for senior-level candidates."
    )
    print(json.dumps(extract_job_requirements(sample), indent=2))
    