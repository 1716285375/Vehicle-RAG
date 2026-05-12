from typing import Any

from app.ingestion.splitters.base import BaseSplitter
from app.models import Chunk, Page


class FixedWindowSplitter(BaseSplitter):
    def __init__(self, window: int = 800, overlap: int = 100) -> None:
        self.window = window
        self.overlap = overlap

    def split(self, pages: list[Page], base_metadata: dict[str, Any]) -> list[Chunk]:
        text = "\n\n".join(page.text for page in pages if page.text.strip())
        chunks: list[Chunk] = []
        step = max(1, self.window - self.overlap)
        for index, start in enumerate(range(0, len(text), step)):
            part = text[start : start + self.window].strip()
            if not part:
                continue
            chunks.append(
                Chunk(
                    text=part,
                    metadata={**base_metadata, "section": "fixed_window", "sub_idx": index},
                )
            )
        return chunks

