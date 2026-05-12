from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Page(BaseModel):
    page_number: int
    text: str
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def lines(self) -> list[str]:
        return self.text.splitlines()

    def with_text(self, text: str) -> "Page":
        return self.model_copy(update={"text": text})


class Document(BaseModel):
    doc_id: str
    title: str
    path: Path
    doc_type: str
    metadata: dict[str, Any] = Field(default_factory=dict)

