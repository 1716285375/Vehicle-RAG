from fastapi.testclient import TestClient

from app.main import app


def test_config_api_exposes_public_settings_only():
    client = TestClient(app)
    response = client.get("/v1/config")
    assert response.status_code == 200
    data = response.json()["config"]
    assert data["vector_store"] in {"json", "faiss", "milvus"}
    assert "llm_api_key" not in data
    assert "mysql_dsn" not in data
