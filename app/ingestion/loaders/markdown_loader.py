from pathlib import Path

from app.ingestion.loaders.base import BaseLoader
from app.ingestion.loaders.text_utils import read_text_with_fallback
from app.models import Page


class MarkdownLoader(BaseLoader):
    async def load(self, file_path: Path) -> list[Page]:
        text = read_text_with_fallback(file_path)
        return [Page(page_number=1, text=text, metadata={"source": str(file_path)})]
