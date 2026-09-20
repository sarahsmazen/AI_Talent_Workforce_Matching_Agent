from app.nlp.skill_normalizer import SkillNormalizer

normalizer = SkillNormalizer()


def test_synonym_lookup():
    assert normalizer.normalize("ml") == "Machine Learning"
    assert normalizer.normalize("Python 3") == "Python"
    assert normalizer.normalize("k8s") == "Kubernetes"


def test_exact_canonical_match_case_insensitive():
    assert normalizer.normalize("python") == "Python"
    assert normalizer.normalize("AWS") == "AWS"


def test_fuzzy_typo_match():
    assert normalizer.normalize("Kubernetees") == "Kubernetes"


def test_unmapped_skill_returns_none():
    assert normalizer.normalize("Underwater Basket Weaving") is None
    assert normalizer.normalize("") is None
    assert normalizer.normalize("   ") is None


def test_normalize_list_dedupes_and_splits_unmapped():
    result = normalizer.normalize_list(["ml", "Machine Learning", "python 3", "Bagpipes"])
    assert result["matched"] == ["Machine Learning", "Python"]
    assert result["unmapped"] == ["Bagpipes"]