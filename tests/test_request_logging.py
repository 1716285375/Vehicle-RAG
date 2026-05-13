from fastapi.testclient import TestClient

from app.main import app


def test_request_logging_adds_request_id_header():
    client = TestClient(app)
    response = client.get("/health", headers={"X-Request-ID": "req-1"})
    assert response.headers["X-Request-ID"] == "req-1"
