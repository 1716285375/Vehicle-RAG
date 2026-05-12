from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class Chunk(BaseModel):
    id: str = Field(default_factory=lambda: f"chunk_{uuid4().hex}")
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)
    embedding: list[float] | None = None


class ScoredChunk(Chunk):
    score: float = 0.0
    rerank_score: float | None = None

