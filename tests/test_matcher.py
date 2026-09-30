import pytest
from app.ai.matching.matcher import matching_engine
from app.ai.matching.gap_analyzer import gap_analyzer
from app.core.constants import MatchStatus


def test_matching_engine_computation():
    candidate_profile = {
        "full_name": "Test Candidate",
        "summary": "Senior Machine Learning Engineer with PyTorch, Python, and Docker expertise.",
        "total_years_experience": 5.0,
        "skills": [
            {"canonical_name": "Python", "evidence_context": "5 years writing Python."},
            {"canonical_name": "PyTorch", "evidence_context": "Trained vision models in PyTorch."},
            {"canonical_name": "Docker", "evidence_context": "Containerized APIs using Docker."}
        ],
        "educations": [{"degree_level": 4, "degree": "Master of Science"}],
        "projects": [{"title": "Vision System", "technologies_used": ["PyTorch", "Python"]}],
        "experiences": [{"duration_months": 60, "job_title": "Senior ML Engineer"}]
    }

    job_data = {
        "title": "Machine Learning Engineer",
        "company": "AI Labs",
        "raw_text": "We need a Senior ML Engineer with Python and PyTorch.",
        "min_years_experience": 4.0,
        "min_education_level": 3,
        "required_skills": [
            {"canonical_name": "Python"},
            {"canonical_name": "PyTorch"},
            {"canonical_name": "Docker"}
        ],
        "preferred_skills": [
            {"canonical_name": "Kubernetes"}
        ]
    }

    result = matching_engine.match(candidate_profile, job_data)

    assert "overall_score" in result
    assert result["overall_score"] >= 80.0
    assert result["required_skill_score"] == 100.0
    assert len(result["evidences"]) == 4
    assert "AI Labs" in result["synthesis_explanation"]
    assert "Python" in result["synthesis_explanation"]


def test_gap_analyzer_prioritization():
    evidences = [
        {"skill_name": "Python", "is_required": True, "match_status": MatchStatus.DIRECT_MATCH.value, "similarity_score": 1.0},
        {"skill_name": "FastAPI", "is_required": True, "match_status": MatchStatus.TRANSFERABLE_MATCH.value, "matched_candidate_skill": "Flask", "similarity_score": 0.65},
        {"skill_name": "Kubernetes", "is_required": True, "match_status": MatchStatus.MISSING.value, "similarity_score": 0.0}
    ]

    analysis = gap_analyzer.analyze_gaps([], evidences)
    assert len(analysis["strong_skills"]) == 1
    assert len(analysis["transferable_skills"]) == 1
    assert len(analysis["missing_skills"]) == 1

    assert analysis["missing_skills"][0]["skill_name"] == "Kubernetes"
    assert analysis["missing_skills"][0]["priority_level"] == "HIGH"
    assert len(analysis["upskilling_roadmap"]) > 0
