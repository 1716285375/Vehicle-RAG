from abc import ABC, abstractmethod
from pathlib import Path

from app.models import Page


class BaseLoader(ABC):
    @abstractmethod
    async def load(self, file_path: Path) -> list[Page]:
        raise NotImplementedError

