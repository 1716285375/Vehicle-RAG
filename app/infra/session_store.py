import json
from pathlib import Path

from app.config.settings import settings
from app.models import SessionTurn


class JsonSessionStore:
    def __init__(self, path: Path | None = None) -> None:
        self.path = path or settings.session_store_path
        self._turns: list[SessionTurn] | None = None

    async def append(self, turn: SessionTurn) -> None:
        turns = await self._load()
        turns.append(turn)
        self._turns = turns
        self._save(turns)

    async def get(self, session_id: str) -> list[SessionTurn]:
        return [turn for turn in await self._load() if turn.session_id == session_id]

    async def delete(self, session_id: str) -> int:
        turns = await self._load()
        kept = [turn for turn in turns if turn.session_id != session_id]
        deleted = len(turns) - len(kept)
        self._turns = kept
        self._save(kept)
        return deleted

    async def _load(self) -> list[SessionTurn]:
        if self._turns is not None:
            return self._turns
        if not self.path.exists():
            self._turns = []
            return self._turns
        data = json.loads(self.path.read_text(encoding="utf-8"))
        self._turns = [SessionTurn(**item) for item in data.get("turns", [])]
        return self._turns

    def _save(self, turns: list[SessionTurn]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"turns": [turn.model_dump(mode="json") for turn in turns]}
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


session_store = JsonSessionStore()
