import pytest
from app.ai.recommendations.resume_improver import resume_improver


def test_resume_improver_passive_verb_detection():
    candidate_profile = {
        "skills": [{"canonical_name": "Python"}, {"canonical_name": "FastAPI"}],
        "experiences": [
            {
                "company": "Startup Inc",
                "key_achievements": [
                    "Worked on Python microservices for data processing.",
                    "Helped with database migration to PostgreSQL."
                ]
            }
        ],
        "projects": []
    }

    result = resume_improver.improve(candidate_profile)
    assert "strength_score" in result
    assert len(result["suggestions"]) >= 2

    first_sug = result["suggestions"][0]
    assert first_sug["issue_type"] == "PASSIVE_VOICE"
    assert "Engineered" in first_sug["suggested_revision"] or "Architected" in first_sug["suggested_revision"]
    assert "interactive_prompt" in first_sug
    assert "?" in first_sug["interactive_prompt"]
