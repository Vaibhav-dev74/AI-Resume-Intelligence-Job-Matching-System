import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "service" in data


def test_canonical_skills_endpoint():
    response = client.get("/api/v1/skills/canonical")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 10
    skill_names = [s["canonical_name"] for s in data]
    assert "Python" in skill_names
    assert "FastAPI" in skill_names


def test_evaluation_benchmark_endpoint():
    response = client.get("/api/v1/evaluations")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert data["metrics"]["skill_extraction_f1"] > 0.80
    assert "failure_cases" in data["metrics"]
