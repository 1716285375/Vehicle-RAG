import json
import time
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Any

from app.config.settings import settings
from app.embedding import CachedEmbedder, HashEmbedder
from app.infra.redis_client import cache
from app.llm import LLMClient
from app.qa.citation import bind_answer_citations
from app.qa.context_builder import ContextBuilder
from app.qa.filter_extractor import extract_query_filters, merge_filters
from app.qa.query_rewriter import QueryRewriter
from app.retrieval import LightweightReranker, VectorStore, build_vector_store


@dataclass
class Event:
    event: str
    data: Any


class RAGChain:
    def __init__(
        self,
        embedder: HashEmbedder | None = None,
        vector_store: VectorStore | None = None,
        reranker: LightweightReranker | None = None,
        llm: LLMClient | None = None,
    ) -> None:
        self.embedder = embedder or CachedEmbedder(HashEmbedder())
        self.vector_store = vector_store or build_vector_store()
        self.reranker = reranker or LightweightReranker()
        self.llm = llm or LLMClient()
        self.query_rewriter = QueryRewriter(llm=self.llm)
        self.context_builder = ContextBuilder()

    async def answer(self, question: str, filters: dict[str, Any] | None = None) -> dict[str, Any]:
        started = time.perf_counter()
        final: dict[str, Any] | None = None
        async for event in self.stream_events(question, filters):
            if event.event == "final":
                final = event.data
        assert final is not None
        final["latency_ms"] = int((time.perf_counter() - started) * 1000)
        return final

    async def retrieve_debug(
        self, question: str, filters: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        effective_filters = merge_filters(filters, extract_query_filters(question))
        rewritten = await self.query_rewriter.rewrite(question)
        query_vec = await self.embedder.embed(rewritten)
        candidates = await self.vector_store.search(
            query_vec,
            top_k=settings.retrieval_top_k,
            filters=effective_filters,
            query_text=rewritten,
        )
        reranked = await self.reranker.rerank(rewritten, candidates, top_k=settings.rerank_top_k)
        return {
            "question": question,
            "rewritten": rewritten,
            "filters": effective_filters,
            "candidates": [
                {
                    "id": item.id,
                    "text": item.text[:300],
                    "metadata": item.metadata,
                    "score": item.score,
                    "rerank_score": item.rerank_score,
                }
                for item in reranked
            ],
        }

    async def stream_events(
        self, question: str, filters: dict[str, Any] | None = None
    ) -> AsyncIterator[Event]:
        effective_filters = merge_filters(filters, extract_query_filters(question))
        cache_key = self._cache_key(question, effective_filters)
        if cached := await cache.get(cache_key):
            result = json.loads(cached)
            result["cached"] = True
            yield Event("final", result)
            return

        rewritten = await self.query_rewriter.rewrite(question)
        yield Event("query_rewritten", {"original": question, "rewritten": rewritten})
        if effective_filters:
            yield Event("query_filters", effective_filters)

        query_vec = await self.embedder.embed(rewritten)
        candidates = await self.vector_store.search(
            query_vec, top_k=settings.retrieval_top_k, filters=effective_filters, query_text=rewritten
        )
        yield Event("retrieved", {"count": len(candidates)})

        reranked = await self.reranker.rerank(rewritten, candidates, top_k=settings.rerank_top_k)
        relevant = [item for item in reranked if self._relevance_score(item) >= settings.min_relevance_score]
        yield Event(
            "reranked",
            {
                "top": [
                    {"id": item.id, "score": item.rerank_score if item.rerank_score else item.score}
                    for item in reranked
                ],
                "accepted": len(relevant),
            },
        )

        context, citations = self.context_builder.build(
            relevant,
            settings.context_max_tokens,
            settings.context_min_chunk_tokens,
        )
        answer_buffer = ""
        async for token in self.llm.stream(question, context):
            answer_buffer += token
            yield Event("token", {"token": token})

        bound_citations = bind_answer_citations(answer_buffer, citations)
        result = {
            "answer": answer_buffer,
            "citations": [c.model_dump() for c in bound_citations],
            "cached": False,
        }
        await cache.setex(cache_key, ttl=settings.qa_cache_ttl, value=json.dumps(result, ensure_ascii=False))
        yield Event("final", result)

    def _cache_key(self, question: str, filters: dict[str, Any] | None) -> str:
        return "qa:" + json.dumps({"q": question, "filters": filters or {}}, sort_keys=True, ensure_ascii=False)

    def _relevance_score(self, item) -> float:
        return float(item.rerank_score if item.rerank_score is not None else item.score)
