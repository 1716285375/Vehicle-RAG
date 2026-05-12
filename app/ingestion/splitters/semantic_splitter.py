from typing import Any

from app.ingestion.splitters.base import BaseSplitter
from app.models import Chunk, Page


class FAQSplitter(BaseSplitter):
    def split(self, pages: list[Page], base_metadata: dict[str, Any]) -> list[Chunk]:
        text = "\n\n".join(page.text for page in pages)
        blocks = [block.strip() for block in text.split("\n\n") if block.strip()]
        chunks: list[Chunk] = []
        pending_question: str | None = None
        for block in blocks:
            lower = block.lower()
            is_question = block.startswith(("Q:", "Q：", "问:", "问：")) or lower.startswith("question:")
            is_answer = block.startswith(("A:", "A：", "答:", "答：")) or lower.startswith("answer:")
            if is_question:
                pending_question = block
                continue
            if is_answer and pending_question:
                chunks.append(
                    Chunk(
                        text=f"{pending_question}\n{block}",
                        metadata={**base_metadata, "section": pending_question[:80]},
                    )
                )
                pending_question = None
                continue
            chunks.append(Chunk(text=block, metadata={**base_metadata, "section": block[:80]}))
        return chunks


class TroubleCodeSplitter(BaseSplitter):
    def split(self, pages: list[Page], base_metadata: dict[str, Any]) -> list[Chunk]:
        chunks: list[Chunk] = []
        for page in pages:
            for line in page.text.splitlines():
                line = line.strip()
                if not line:
                    continue
                code = line.split("|", 1)[0].strip()
                chunks.append(
                    Chunk(
                        text=line,
                        metadata={
                            **base_metadata,
                            "code": code,
                            "section": code,
                            "page": page.page_number,
                        },
                    )
                )
        return chunks

