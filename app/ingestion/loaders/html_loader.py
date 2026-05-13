from html.parser import HTMLParser
from pathlib import Path

from app.ingestion.loaders.base import BaseLoader
from app.ingestion.loaders.text_utils import read_text_with_fallback
from app.models import Page


class _TextHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.parts: list[str] = []

    def handle_data(self, data: str) -> None:
        text = data.strip()
        if text:
            self.parts.append(text)


class HTMLLoader(BaseLoader):
    async def load(self, file_path: Path) -> list[Page]:
        parser = _TextHTMLParser()
        parser.feed(read_text_with_fallback(file_path))
        return [
            Page(
                page_number=1,
                text="\n\n".join(parser.parts),
                metadata={"source": str(file_path)},
            )
        ]
