import io
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.ai.extraction.skill_extractor import skill_extractor
from app.ai.extraction.skill_normalizer import skill_normalizer
from app.ai.matching.matcher import matching_engine
from app.services.evaluation_service import evaluation_service

client = TestClient(app)


def test_empty_resume_text_rejection():
    """Verify empty or whitespace resume text triggers a 400 Bad Request with structured envelope."""
    res = client.post("/api/resume/analyze-json", json={"resume_text": "   \n\t   "})
    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert "error" in data
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "empty" in data["error"]["message"].lower() or "no extractable" in data["error"]["message"].lower()


def test_corrupt_pdf_upload_rejection():
    """Verify corrupted PDF bytes without valid %PDF signature are rejected safely."""
    corrupt_bytes = b"This is not a real PDF file, just arbitrary junk."
    files = {"file": ("fake_resume.pdf", io.BytesIO(corrupt_bytes), "application/pdf")}
    res = client.post("/api/resume/analyze", files=files)
    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "signature" in data["error"]["message"].lower() or "failed" in data["error"]["message"].lower()


def test_unsupported_file_extension_rejection():
    """Verify unsupported file extensions (.exe, .sh) are rejected by security validation."""
    payload_bytes = b"#!/bin/bash\necho 'malicious'"
    files = {"file": ("exploit.sh", io.BytesIO(payload_bytes), "application/x-sh")}
    res = client.post("/api/resume/analyze", files=files)
    assert res.status_code == 400
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "BAD_REQUEST"
    assert "unsupported" in data["error"]["message"].lower()


def test_oversized_payload_rejection():
    """Verify payload exceeding MAX_UPLOAD_SIZE_MB triggers 413 Payload Too Large."""
    # 11 MB payload
    oversized_bytes = b"0" * (11 * 1024 * 1024)
    files = {"file": ("oversized.pdf", io.BytesIO(oversized_bytes), "application/pdf")}
    res = client.post("/api/resume/analyze", files=files)
    assert res.status_code == 413
    data = res.json()
    assert data["success"] is False
    assert data["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "exceeds maximum allowed size" in data["error"]["message"].lower()


def test_short_token_boundary_protection():
    """Verify single/short-letter skill names (Go, SQL) do not false-positive on common English words."""
    # "Going", "Canadian", "companies" should NOT extract "Go" or "SQL"
    benign_text = "Going forward, our team adopted React and Docker across multiple Canadian companies."
    skills = skill_extractor.extract_skills(benign_text)
    extracted_names = [s["canonical_name"] for s in skills]

    assert "Go" not in extracted_names
    assert "SQL" not in extracted_names

    # But genuine mentions SHOULD extract properly
    technical_text = "Proficient in Go (Golang), SQL, and React programming for distributed systems."
    tech_skills = skill_extractor.extract_skills(technical_text)
    tech_names = [s["canonical_name"] for s in tech_skills]

    assert "Go" in tech_names
    assert "SQL" in tech_names
    assert "React" in tech_names


def test_skill_alias_normalization_precision():
    """Verify industry shorthand aliases correctly resolve to canonical taxonomy entities."""
    test_cases = [
        ("k8s", "Kubernetes"),
        ("psql", "PostgreSQL"),
        ("postgres", "PostgreSQL"),
        ("tf", "TensorFlow"),
        ("ts", "TypeScript"),
        ("gcp", "Google Cloud Platform"),
        ("aws", "AWS"),
        ("amazon web services", "AWS"),
        ("react.js", "React"),
        ("torch", "PyTorch"),
        ("js", "JavaScript"),
    ]
    for alias, expected_canonical in test_cases:
        resolved = skill_normalizer.normalize(alias)
        assert resolved is not None, f"Failed to normalize alias '{alias}'"
        assert resolved.canonical_name == expected_canonical, f"Alias '{alias}' mapped to '{resolved.canonical_name}' instead of '{expected_canonical}'"


def test_dynamic_weights_redistribution_contract():
    """Verify weight redistribution when a job has 0 preferred requirements and candidate has no projects."""
    candidate = {
        "full_name": "Test Candidate",
        "summary": "Full Stack Engineer",
        "total_years_experience": 4.0,
        "skills": [{"canonical_name": "Python"}, {"canonical_name": "FastAPI"}],
        "educations": [{"degree_level": 3}],
        "projects": [],
        "experiences": [{"duration_months": 48, "job_title": "Full Stack Engineer"}]
    }

    job_minimal = {
        "title": "Full Stack Engineer",
        "company": "Startup Inc",
        "raw_text": "Looking for a Python & FastAPI engineer.",
        "min_years_experience": 2.0,
        "min_education_level": 3,
        "required_skills": [{"canonical_name": "Python"}, {"canonical_name": "FastAPI"}],
        "preferred_skills": []     # No preferred skills
    }

    result = matching_engine.match(candidate, job_minimal)
    weights = result["scoring_weights"]

    # Preferred skill and project weights should both be 0.0
    assert weights["preferred_skills"] == 0.0
    assert weights["project_relevance"] == 0.0

    # Total redistributed weight must equal 1.0 exactly
    total_weight = sum(weights.values())
    assert pytest.approx(total_weight, 0.001) == 1.0

    # Required skills and experience relevance should have absorbed redistributed weight proportionally
    assert weights["required_skills"] > 0.40
    assert weights["experience_relevance"] > 0.15


def test_evaluation_mrr_range_and_contract():
    """Verify offline benchmark metrics conform to expected probabilistic ranges [0.0, 1.0]."""
    result = evaluation_service.run_benchmark()
    assert "metrics" in result
    metrics = result["metrics"]

    assert 0.0 <= metrics["skill_extraction_f1"] <= 1.0
    assert 0.0 <= metrics["skill_extraction_precision"] <= 1.0
    assert 0.0 <= metrics["skill_extraction_recall"] <= 1.0
    assert 0.0 <= metrics["job_requirement_accuracy"] <= 1.0
    assert 0.0 <= metrics["semantic_similarity_mrr"] <= 1.0

    # Verify structured failure case report
    assert "failure_cases" in metrics
    assert isinstance(metrics["failure_cases"], list)
    for fc in metrics["failure_cases"]:
        assert "sample_id" in fc
        assert "component" in fc
        assert "error_analysis" in fc


def test_structured_error_envelope_format():
    """Verify 404 and 422 HTTP responses adhere to the standard error envelope."""
    # 404 test
    res_404 = client.get("/api/nonexistent-route-404")
    assert res_404.status_code == 404
    data_404 = res_404.json()
    assert data_404["success"] is False
    assert data_404["error"]["code"] == "NOT_FOUND"

    # 422 test (invalid JSON body for analyze-json)
    res_422 = client.post("/api/resume/analyze-json", json={"wrong_key": 123})
    assert res_422.status_code == 422
    data_422 = res_422.json()
    assert data_422["success"] is False
    assert data_422["error"]["code"] == "VALIDATION_ERROR"
