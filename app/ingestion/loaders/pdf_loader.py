from pathlib import Path

from app.ingestion.loaders.base import BaseLoader
from app.models import Page


class PDFLoader(BaseLoader):
    async def load(self, file_path: Path) -> list[Page]:
        import fitz

        pages: list[Page] = []
        with fitz.open(file_path) as doc:
            for index, page in enumerate(doc, start=1):
                pages.append(
                    Page(
                        page_number=index,
                        text=page.get_text("text"),
                        metadata={"source": str(file_path), "page": index},
                    )
                )
        return pages

