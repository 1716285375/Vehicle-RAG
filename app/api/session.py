from fastapi import APIRouter

from app.infra.session_store import session_store

router = APIRouter()


@router.get("/sessions/{session_id}")
async def get_session(session_id: str) -> dict:
    turns = await session_store.get(session_id)
    return {"session_id": session_id, "turns": [turn.model_dump(mode="json") for turn in turns]}


@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict:
    deleted_turns = await session_store.delete(session_id)
    return {"session_id": session_id, "deleted_turns": deleted_turns}
