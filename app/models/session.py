from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class SessionTurn(BaseModel):
    id: str = Field(default_factory=lambda: f"turn_{uuid4().hex}")
    session_id: str
    question: str
    answer: str
    citations: list[dict[str, Any]] = Field(default_factory=list)
    filters: dict[str, Any] | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
