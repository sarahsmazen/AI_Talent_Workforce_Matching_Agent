"""
Phase 2: skill normalization -- maps raw skill mentions (from resumes, job descriptions,
free-text agent input) onto the canonical taxonomy in data/scripts/skill_taxonomy.json.

Three-tier match, in order:
    1. Exact synonym lookup ("ml" -> "Machine Learning")
    2. Exact canonical name match, case-insensitive ("python" -> "Python")
    3. Fuzzy match against canonical names, for near-miss typos ("Kubernetees" -> "Kubernetes")
Anything that clears none of these returns None -- per the project's grounding rule, an
unmapped skill is surfaced for review rather than silently guessed at or dropped.
"""
import difflib
import json
import os
from typing import List, Optional

TAXONOMY_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "..", "data", "scripts", "skill_taxonomy.json"
)

_FUZZY_CUTOFF = 0.85  # difflib similarity ratio; below this we'd rather say "no match" than guess


class SkillNormalizer:
    def __init__(self, taxonomy_path: str = TAXONOMY_PATH):
        with open(taxonomy_path) as f:
            taxonomy = json.load(f)
        self.canonical_skills = taxonomy["canonical_skills"]
        self.synonyms = {k.lower(): v for k, v in taxonomy["synonyms"].items()}
        self._canonical_lower = {s.lower(): s for s in self.canonical_skills}

    def normalize(self, raw_skill: str) -> Optional[str]:
        if not raw_skill or not raw_skill.strip():
            return None
        cleaned = raw_skill.strip().lower()

        # tier 1: synonym dictionary
        if cleaned in self.synonyms:
            return self.synonyms[cleaned]

        # tier 2: exact canonical match (case-insensitive)
        if cleaned in self._canonical_lower:
            return self._canonical_lower[cleaned]

        # tier 3: fuzzy match against canonical names (catches typos, not synonyms)
        close = difflib.get_close_matches(cleaned, self._canonical_lower.keys(), n=1, cutoff=_FUZZY_CUTOFF)
        if close:
            return self._canonical_lower[close[0]]

        return None  # unmapped -- surface this, never guess

    def normalize_list(self, raw_skills: List[str]) -> dict:
        """Returns {"matched": [...canonical, deduped...], "unmapped": [...raw, deduped...]}."""
        matched, unmapped = set(), set()
        for raw in raw_skills:
            result = self.normalize(raw)
            if result:
                matched.add(result)
            else:
                unmapped.add(raw.strip())
        return {"matched": sorted(matched), "unmapped": sorted(unmapped)}


if __name__ == "__main__":
    # quick manual smoke test
    normalizer = SkillNormalizer()
    samples = ["ml", "Python 3", "K8s", "AWS", "Kubernetees", "Underwater Basket Weaving"]
    for s in samples:
        print(f"{s!r:35} -> {normalizer.normalize(s)}")