from app.ingestion.splitters.base import count_tokens
from app.models import Citation, ScoredChunk


class ContextBuilder:
    def build(
        self, chunks: list[ScoredChunk], max_tokens: int = 3000
    ) -> tuple[str, list[Citation]]:
        context_parts: list[str] = []
        citations: list[Citation] = []
        used_tokens = 0
        for index, chunk in enumerate(chunks, start=1):
            chunk_tokens = count_tokens(chunk.text)
            if used_tokens and used_tokens + chunk_tokens > max_tokens:
                break
            section = chunk.metadata.get("section") or " / ".join(
                chunk.metadata.get("heading_path", ["未知"])
            )
            doc_title = chunk.metadata.get("doc_title", "")
            context_parts.append(f"[{index}] (来源: {doc_title} / {section})\n{chunk.text}")
            citations.append(
                Citation(
                    id=index,
                    doc_id=str(chunk.metadata.get("doc_id", "")),
                    doc_title=str(doc_title),
                    section=str(section),
                    text=chunk.text,
                    score=float(chunk.rerank_score if chunk.rerank_score is not None else chunk.score),
                )
            )
            used_tokens += chunk_tokens
        return "\n\n".join(context_parts), citations

