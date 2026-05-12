import re
import unicodedata

from app.ingestion.cleaners.dedupe import DedupeCleaner
from app.ingestion.cleaners.header_footer import HeaderFooterCleaner
from app.ingestion.cleaners.table_repair import TableRepairCleaner
from app.models import Page


CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


class TextNormalizer:
    def clean(self, pages: list[Page]) -> list[Page]:
        cleaned: list[Page] = []
        for page in pages:
            text = unicodedata.normalize("NFKC", page.text)
            text = CONTROL_RE.sub("", text)
            text = re.sub(r"[ \t]+", " ", text)
            text = re.sub(r"\n{3,}", "\n\n", text)
            cleaned.append(page.with_text(text.strip()))
        return cleaned


class DocumentCleaner:
    def __init__(self) -> None:
        self.steps = [
            HeaderFooterCleaner(),
            TableRepairCleaner(),
            TextNormalizer(),
            DedupeCleaner(),
        ]

    def clean(self, pages: list[Page]) -> list[Page]:
        for step in self.steps:
            pages = step.clean(pages)
        return pages

