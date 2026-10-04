import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_api_health():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_api_presets():
    res = client.get("/api/presets")
    assert res.status_code == 200
    data = res.json()
    assert "resumes" in data
    assert "jobs" in data
    assert len(data["resumes"]) >= 3
    assert len(data["jobs"]) >= 3


def test_api_canonical_skills():
    res = client.get("/api/skills/canonical")
    assert res.status_code == 200
    skills = res.json()
    assert isinstance(skills, list)
    assert len(skills) >= 30
    skill_names = [s["canonical_name"] for s in skills]
    assert "Python" in skill_names
    assert "FastAPI" in skill_names
    assert "PyTorch" in skill_names


def test_api_job_analyze():
    sample_jd = """Senior Machine Learning Engineer
Apex Robotics
Required: Python, PyTorch, Computer Vision.
Preferred: Docker, Kubernetes.
Min 3 years experience. Bachelor's degree required.
"""
    res = client.post("/api/job/analyze", json={"job_description": sample_jd})
    assert res.status_code == 200
    data = res.json()
    assert "required_skills" in data
    req_names = [s["canonical_name"] for s in data["required_skills"]]
    assert "Python" in req_names


def test_api_resume_analyze_json():
    sample_resume = """Alice Chen
alice@example.com | 555-1234
Senior Machine Learning Engineer with 5 years experience in Python, PyTorch, Computer Vision.
"""
    res = client.post("/api/resume/analyze-json", json={"resume_text": sample_resume})
    assert res.status_code == 200
    data = res.json()
    assert data["full_name"] == "Alice Chen"
    assert "skills" in data
    extracted_names = [s["canonical_name"] for s in data["skills"]]
    assert "Python" in extracted_names


def test_api_match():
    sample_resume = """Alice Chen
alice@example.com | 555-1234
Senior Machine Learning Engineer with 5 years experience in Python, PyTorch, Computer Vision.
"""
    sample_jd = """Senior Machine Learning Engineer
Apex Robotics
Required: Python, PyTorch, Computer Vision.
Preferred: Docker, Kubernetes.
Min 3 years experience. Bachelor's degree required.
"""
    # First analyze resume and job
    r_cand = client.post("/api/resume/analyze-json", json={"resume_text": sample_resume}).json()
    r_job = client.post("/api/job/analyze", json={"job_description": sample_jd}).json()

    # Match request
    res = client.post("/api/match", json={"candidate": r_cand, "job": r_job})
    assert res.status_code == 200
    data = res.json()
    assert "overall_score" in data
    assert 0 <= data["overall_score"] <= 100
    assert "breakdown" in data
    assert "evidence_matrix" in data
    assert len(data["breakdown"]) >= 5


def test_api_skill_gaps():
    sample_resume = """Alice Chen
Senior Machine Learning Engineer with experience in Python and PyTorch.
"""
    sample_jd = """Required: Python, PyTorch, Kubernetes, Docker."""
    r_cand = client.post("/api/resume/analyze-json", json={"resume_text": sample_resume}).json()
    r_job = client.post("/api/job/analyze", json={"job_description": sample_jd}).json()

    res = client.post("/api/skill-gaps", json={"candidate": r_cand, "job": r_job})
    assert res.status_code == 200
    data = res.json()
    assert "missing_required_skills" in data
    assert "learning_roadmap" in data
    assert "coverage_ratio" in data


def test_api_resume_improve():
    sample_resume = """Alice Chen
Experience:
Worked on ML models and did some python coding. Responsible for database.
"""
    r_cand = client.post("/api/resume/analyze-json", json={"resume_text": sample_resume}).json()
    res = client.post("/api/resume/improve", json={"candidate": r_cand})
    assert res.status_code == 200
    data = res.json()
    assert "strength_index" in data
    assert "bullet_improvements" in data
    assert "critique_notes" in data


def test_api_recommendations():
    sample_resume = """Alice Chen
Senior Machine Learning Engineer with 5 years experience in Python, PyTorch, Computer Vision.
"""
    r_cand = client.post("/api/resume/analyze-json", json={"resume_text": sample_resume}).json()
    res = client.post("/api/recommendations", json={"candidate": r_cand})
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert "fit_score" in data[0]


def test_api_evaluation():
    res = client.get("/api/evaluation")
    assert res.status_code == 200
    data = res.json()
    assert "extraction_metrics" in data
    assert "matching_metrics" in data
    assert "overall_f1" in data["extraction_metrics"]
    assert "semantic_mrr" in data["matching_metrics"]

