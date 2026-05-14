from typing import Any
import re

from app.ingestion.splitters.base import BaseSplitter
from app.models import Chunk, Page


TROUBLE_CODE_RE = re.compile(r"^[PBCU][0-9A-Fa-f]{4}$")


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
                if not line or self._is_table_separator(line):
                    continue
                parts = self._split_row(line)
                if not parts:
                    continue
                code = parts[0].strip().upper()
                if code.lower() in {"code", "故障码", "dtc"}:
                    continue
                metadata = {
                    **base_metadata,
                    "code": code,
                    "section": code,
                    "page": page.page_number,
                }
                if len(parts) > 1:
                    metadata["description"] = parts[1]
                if len(parts) > 2:
                    metadata["action"] = parts[2]
                chunks.append(
                    Chunk(
                        text=" | ".join(parts),
                        metadata=metadata,
                    )
                )
        return chunks

    def _split_row(self, line: str) -> list[str]:
        if "|" in line:
            return [part.strip() for part in line.strip("|").split("|") if part.strip()]
        parts = [part.strip() for part in re.split(r"\s{2,}|\t", line) if part.strip()]
        if parts and TROUBLE_CODE_RE.match(parts[0]):
            return parts
        return [line]

    def _is_table_separator(self, line: str) -> bool:
        stripped = line.replace("|", "").replace(":", "").replace(" ", "").strip()
        return bool(stripped) and all(char == "-" for char in stripped)
