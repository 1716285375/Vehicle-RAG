import asyncio
from pathlib import Path

from app.infra.session_store import JsonSessionStore
from app.models import SessionTurn


def test_json_session_store_append_get_delete(tmp_path: Path):
    asyncio.run(_run_json_session_store_append_get_delete(tmp_path))


async def _run_json_session_store_append_get_delete(tmp_path: Path):
    store = JsonSessionStore(tmp_path / "sessions.json")
    await store.append(SessionTurn(session_id="s1", question="AUTOHOLD?", answer="Use the switch."))
    await store.append(SessionTurn(session_id="s2", question="P0301?", answer="Fault code."))

    turns = await store.get("s1")
    assert len(turns) == 1
    assert turns[0].question == "AUTOHOLD?"

    deleted = await store.delete("s1")
    assert deleted == 1
    assert await store.get("s1") == []
