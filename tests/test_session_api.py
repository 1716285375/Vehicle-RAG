from fastapi.testclient import TestClient

from app.infra.session_store import JsonSessionStore
from app.main import app
from app.models import SessionTurn


def test_session_api_returns_turns(tmp_path, monkeypatch):
    store = JsonSessionStore(tmp_path / "sessions.json")
    monkeypatch.setattr("app.api.session.session_store", store)
    client = TestClient(app)

    import asyncio

    asyncio.run(store.append(SessionTurn(session_id="s1", question="Q", answer="A")))

    response = client.get("/v1/sessions/s1")
    assert response.status_code == 200
    assert response.json()["turns"][0]["answer"] == "A"


def test_session_api_lists_sessions(tmp_path, monkeypatch):
    store = JsonSessionStore(tmp_path / "sessions.json")
    monkeypatch.setattr("app.api.session.session_store", store)
    client = TestClient(app)

    import asyncio

    asyncio.run(store.append(SessionTurn(session_id="s1", question="Q", answer="A")))

    response = client.get("/v1/sessions")
    assert response.status_code == 200
    assert response.json()["sessions"][0]["session_id"] == "s1"
