import numpy as np
import pytest
from app.ai.embeddings.embedding_engine import embedding_engine, EmbeddingEngine
from app.ai.extraction.skill_extractor import skill_extractor
from app.ai.matching.matcher import matching_engine
from app.ai.recommendations.resume_improver import evidence_grounding_validator, EvidenceGroundingValidator
from app.core.constants import MatchStatus
from app.core.security import anonymize_text, anonymize_profile


def test_cosine_similarity_monotonicity():
    """Verify cosine similarity is monotonic and has no discontinuous jumps at 0."""
    engine = EmbeddingEngine()
    v_base = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    v_positive = np.array([0.9, 0.1, 0.0], dtype=np.float32)
    v_orthogonal = np.array([0.0, 1.0, 0.0], dtype=np.float32)
    v_opposite = np.array([-1.0, 0.0, 0.0], dtype=np.float32)

    sim_pos = engine.cosine_similarity(v_base, v_positive)
    sim_orth = engine.cosine_similarity(v_base, v_orthogonal)
    sim_opp = engine.cosine_similarity(v_base, v_opposite)

    assert sim_pos > sim_orth
    assert sim_orth >= sim_opp
    assert sim_opp == 0.0
    assert 0.0 <= sim_orth <= 0.05


def test_embedding_cache_bounded_lru():
    """Verify embedding cache caps capacity to prevent memory leaks."""
    engine = EmbeddingEngine()
    engine.MAX_CACHE_SIZE = 5

    for i in range(10):
        engine.encode(f"test unique text string {i}")

    assert len(engine._cache) <= 5


def test_sentence_splitter_abbreviation_preservation():
    """Verify sentence splitter does not break on versions, tech suffixes, or decimals."""
    text = "Architected high-throughput microservices using Node.js and Python 3.11 with 99.9% uptime SLA. Deployed on AWS."
    sentences = skill_extractor.split_sentences(text)
    assert len(sentences) == 2
    assert "Node.js and Python 3.11 with 99.9% uptime SLA" in sentences[0]
    assert "Deployed on AWS" in sentences[1]


def test_short_alias_case_guard():
    """Verify short aliases like 'go' or 'py' do not trigger false positives on regular words."""
    false_pos_text = "We go to client meetings every week and did some py work."
    skills = skill_extractor.extract_skills(false_pos_text)
    skill_names = [s["canonical_name"] for s in skills]

    # 'go' as lowercase common English verb must not match Golang/Go
    assert "Go" not in skill_names


def test_dynamic_weight_redistribution():
    """Verify jobs with 0 preferred skills renormalize weights instead of awarding free points."""
    candidate = {
        "full_name": "Test Candidate",
        "summary": "Software Engineer",
        "total_years_experience": 3.0,
        "skills": [{"canonical_name": "Python", "evidence_context": "Python backend"}],
        "educations": [{"degree_level": 3}],
        "projects": [],
        "experiences": [{"duration_months": 36, "job_title": "Backend Dev"}]
    }

    job_with_pref = {
        "title": "Backend Dev",
        "company": "Tech Corp",
        "raw_text": "Python engineer",
        "min_years_experience": 3.0,
        "min_education_level": 3,
        "required_skills": [{"canonical_name": "Python"}],
        "preferred_skills": [{"canonical_name": "Kubernetes"}]
    }

    job_no_pref = {
        "title": "Backend Dev",
        "company": "Tech Corp",
        "raw_text": "Python engineer",
        "min_years_experience": 3.0,
        "min_education_level": 3,
        "required_skills": [{"canonical_name": "Python"}],
        "preferred_skills": []
    }

    res_with = matching_engine.match(candidate, job_with_pref)
    res_without = matching_engine.match(candidate, job_no_pref)

    # In the job without preferred skills, preferred_skills weight should be 0.0
    assert res_without["scoring_weights"]["preferred_skills"] == 0.0
    # And the weights should still sum to 1.0
    assert pytest.approx(sum(res_without["scoring_weights"].values()), 0.01) == 1.0


def test_evidence_grounding_validator():
    """Verify hallucination detection on unanchored skills and fabricated numbers."""
    orig = "Responsible for managing team and helping with deployment."
    
    # Valid grounded revision: only action verbs changed
    safe_rev = "Led engineering team and orchestrated deployment."
    audit_safe = EvidenceGroundingValidator.validate_revision(orig, safe_rev, ["Python"])
    assert audit_safe["is_grounded"] is True
    assert audit_safe["audit_verdict"] == "VERIFIED_GROUNDED"

    # Hallucinated revision: injects Kubernetes and 45% improvement
    hallucinated_rev = "Engineered distributed Kubernetes cluster improving latency by 45%."
    audit_hallucinated = EvidenceGroundingValidator.validate_revision(orig, hallucinated_rev, ["Python"])
    assert audit_hallucinated["is_grounded"] is False
    assert audit_hallucinated["audit_verdict"] == "HALLUCINATION_DETECTED"
    assert "kubernetes" in [s.lower() for s in audit_hallucinated["unanchored_skills"]]
    assert len(audit_hallucinated["fabricated_numbers"]) > 0


def test_blind_screening_pii_anonymization():
    """Verify PII redaction for candidate name, email, phone, and URLs."""
    raw = "Jane Doe. Contact: jane.doe@ai-company.com, +1 (555) 234-5678, https://linkedin.com/in/janedoe"
    anonymized = anonymize_text(raw, candidate_name="Jane Doe")
    assert "[REDACTED EMAIL]" in anonymized
    assert "[REDACTED PHONE]" in anonymized
    assert "[REDACTED URL]" in anonymized
    assert "[REDACTED CANDIDATE NAME]" in anonymized or "[REDACTED NAME]" in anonymized
    assert "janedoe" not in anonymized.lower()
