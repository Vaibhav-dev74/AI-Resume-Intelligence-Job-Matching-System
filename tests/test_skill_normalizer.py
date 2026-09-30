import pytest
from app.ai.extraction.skill_normalizer import skill_normalizer
from app.ai.extraction.skill_extractor import skill_extractor
from app.core.constants import MatchStatus


def test_alias_normalization():
    node = skill_normalizer.normalize("postgres")
    assert node is not None
    assert node.canonical_name == "PostgreSQL"

    node = skill_normalizer.normalize("python 3")
    assert node is not None
    assert node.canonical_name == "Python"

    node = skill_normalizer.normalize("reactjs")
    assert node is not None
    assert node.canonical_name == "React"


def test_transferable_skill_matching():
    candidate_skills = ["Flask", "Python", "SQL"]
    status, matched_skill, score, rationale = skill_normalizer.match_skill_against_candidates(
        "FastAPI",
        candidate_skills
    )
    assert status == MatchStatus.TRANSFERABLE_MATCH
    assert matched_skill == "Flask"
    assert 0.50 <= score <= 0.85
    assert "transferable" in rationale.lower()


def test_direct_skill_matching():
    candidate_skills = ["Python", "Docker", "PyTorch"]
    status, matched_skill, score, rationale = skill_normalizer.match_skill_against_candidates(
        "python",
        candidate_skills
    )
    assert status == MatchStatus.DIRECT_MATCH
    assert score == 1.0


def test_missing_skill_matching():
    candidate_skills = ["Python", "SQL"]
    status, matched_skill, score, rationale = skill_normalizer.match_skill_against_candidates(
        "Kubernetes",
        candidate_skills
    )
    assert status == MatchStatus.MISSING
    assert score == 0.0
    assert matched_skill is None


def test_skill_extractor_evidence():
    text = "Engineered real-time object detection models using PyTorch on AWS GPU clusters."
    skills = skill_extractor.extract_skills(text)
    skill_names = [s["canonical_name"] for s in skills]
    assert "PyTorch" in skill_names
    assert "AWS" in skill_names

    pytorch_skill = next(s for s in skills if s["canonical_name"] == "PyTorch")
    assert "Engineered real-time object detection" in pytorch_skill["evidence_context"]
