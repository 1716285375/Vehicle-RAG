from fastapi.testclient import TestClient

from app.main import app


def test_validation_errors_are_structured():
    client = TestClient(app)
    response = client.post("/v1/qa", json={})
    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["details"]
