from pathlib import Path

from app.ingestion.loaders.base import BaseLoader
from app.ingestion.loaders.docx_loader import DocxLoader
from app.ingestion.loaders.html_loader import HTMLLoader
from app.ingestion.loaders.markdown_loader import MarkdownLoader
from app.ingestion.loaders.pdf_loader import PDFLoader


class LoaderFactory:
    def get(self, file_path: str | Path) -> BaseLoader:
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return PDFLoader()
        if suffix == ".docx":
            return DocxLoader()
        if suffix in {".md", ".markdown", ".txt"}:
            return MarkdownLoader()
        if suffix in {".html", ".htm"}:
            return HTMLLoader()
        raise ValueError(f"Unsupported file type: {suffix}")

