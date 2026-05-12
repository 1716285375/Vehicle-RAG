from pathlib import Path

from app.ingestion.loaders.base import BaseLoader
from app.models import Page


class MarkdownLoader(BaseLoader):
    async def load(self, file_path: Path) -> list[Page]:
        text = file_path.read_text(encoding="utf-8")
        return [Page(page_number=1, text=text, metadata={"source": str(file_path)})]

