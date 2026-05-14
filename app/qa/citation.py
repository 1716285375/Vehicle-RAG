import re

from app.config.settings import settings
from app.ingestion.splitters.base import count_tokens
from app.models import Citation, ScoredChunk


class ContextBuilder:
    def build(
        self,
        chunks: list[ScoredChunk],
        max_tokens: int = 3000,
        min_chunk_tokens: int | None = None,
    ) -> tuple[str, list[Citation]]:
        context_parts: list[str] = []
        citations: list[Citation] = []
        used_tokens = 0
        min_chunk_tokens = min_chunk_tokens or settings.context_min_chunk_tokens
        for index, chunk in enumerate(chunks, start=1):
            remaining_tokens = max_tokens - used_tokens
            if remaining_tokens <= 0:
                break
            chunk_text = chunk.text
            chunk_tokens = count_tokens(chunk_text)
            if chunk_tokens > remaining_tokens:
                if remaining_tokens < min_chunk_tokens:
                    break
                chunk_text = truncate_to_token_budget(chunk_text, remaining_tokens)
                chunk_tokens = count_tokens(chunk_text)
            section = chunk.metadata.get("section") or " / ".join(
                chunk.metadata.get("heading_path", ["未知"])
            )
            doc_title = chunk.metadata.get("doc_title", "")
            context_parts.append(f"[{index}] (来源: {doc_title} / {section})\n{chunk_text}")
            citations.append(
                Citation(
                    id=index,
                    doc_id=str(chunk.metadata.get("doc_id", "")),
                    doc_title=str(doc_title),
                    section=str(section),
                    text=chunk_text,
                    score=float(chunk.rerank_score if chunk.rerank_score is not None else chunk.score),
                )
            )
            used_tokens += chunk_tokens
        return "\n\n".join(context_parts), citations


def truncate_to_token_budget(text: str, max_tokens: int) -> str:
    if count_tokens(text) <= max_tokens:
        return text
    max_chars = max(1, max_tokens * 2)
    if len(text) <= max_chars:
        return text
    return text[: max(1, max_chars - 1)].rstrip() + "…"


def extract_citation_ids(answer: str) -> set[int]:
    return {int(match) for match in re.findall(r"\[(\d+)\]", answer)}


def bind_answer_citations(answer: str, citations: list[Citation]) -> list[Citation]:
    cited_ids = extract_citation_ids(answer)
    if not cited_ids:
        return []
    return [citation for citation in citations if citation.id in cited_ids]
