from fastapi.testclient import TestClient

from app.main import app


def test_readiness_health_checks_dependencies():
    client = TestClient(app)
    response = client.get("/health/ready")
    assert response.status_code == 200
    payload = response.json()
    assert payload["ok"] is True
    assert payload["database"] is True
    assert payload["vector_store"] is True
