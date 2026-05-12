from abc import ABC, abstractmethod
from typing import Any

from app.models import Chunk, Page


def count_tokens(text: str) -> int:
    # Cheap mixed Chinese/English approximation; replace with tokenizer later if needed.
    return max(1, len(text) // 2)


class BaseSplitter(ABC):
    @abstractmethod
    def split(self, pages: list[Page], base_metadata: dict[str, Any]) -> list[Chunk]:
        raise NotImplementedError

