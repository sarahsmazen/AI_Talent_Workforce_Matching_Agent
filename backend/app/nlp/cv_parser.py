"""
Phase 3 (start): CV skill extraction -- scans resume free text for known skill terms
(canonical names + synonyms) and returns the canonical skills mentioned.

This is intentionally a straightforward keyword-spotter, not a full NLP model: it's a
concrete, gradeable baseline (does the resume text literally mention "Python", "machine
learning", "AWS", etc.) that the matching engine can already use, and it's meant to be
swapped out or supplemented with a proper NER/embeddings-based extractor later without
changing what calls it.
"""
import re
from typing import Dict, List

from app.nlp.skill_normalizer import SkillNormalizer

# Surface forms made only of letters/digits/spaces get precise word-boundary regex
# matching. Forms with special characters (C++, C#, CI/CD, ...) fall back to a plain
# substring search, since \b doesn't work reliably around non-word characters.
_ALNUM_SPACE_RE = re.compile(r"^[a-z0-9 ]+$")


def build_surface_forms(normalizer: SkillNormalizer) -> Dict[str, str]:
    """canonical skill name / synonym (lowercased) -> canonical skill name.

    Build this once per batch job (it's the same for every resume) and reuse it --
    don't call this inside a per-candidate loop.
    """
    forms = {}
    for canonical in normalizer.canonical_skills:
        forms[canonical.lower()] = canonical
    for synonym, canonical in normalizer.synonyms.items():
        forms.setdefault(synonym, canonical)
    return forms


def extract_skills(text: str, surface_forms: Dict[str, str]) -> List[str]:
    """Returns the sorted, deduped list of canonical skills mentioned in `text`."""
    if not text:
        return []
    text_lower = text.lower()
    found = set()

    for surface_form, canonical in surface_forms.items():
        if _ALNUM_SPACE_RE.match(surface_form):
            pattern = r"\b" + re.escape(surface_form) + r"\b"
            if re.search(pattern, text_lower):
                found.add(canonical)
        elif surface_form in text_lower:
            found.add(canonical)

    return sorted(found)


def extract_skills_from_text(text: str, normalizer: SkillNormalizer) -> List[str]:
    """Convenience one-off wrapper. Batch code should call build_surface_forms() once
    and reuse it with extract_skills() instead of rebuilding the form list every call."""
    return extract_skills(text, build_surface_forms(normalizer))


if __name__ == "__main__":
    normalizer = SkillNormalizer()
    sample = (
        "Experienced software engineer skilled in Python, ML, and AWS. "
        "Familiar with Docker, K8s, and CI/CD pipelines. Also know C++."
    )
    print(extract_skills_from_text(sample, normalizer))