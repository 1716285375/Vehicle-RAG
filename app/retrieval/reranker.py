import asyncio
import re

from app.models import ScoredChunk


class LightweightReranker:
    async def rerank(
        self, query: str, candidates: list[ScoredChunk], top_k: int = 5
    ) -> list[ScoredChunk]:
        query_terms = set(self._terms(query))
        for candidate in candidates:
            terms = set(self._terms(candidate.text))
            lexical = len(query_terms & terms) / max(1, len(query_terms))
            candidate.rerank_score = candidate.score * 0.7 + lexical * 0.3
        return sorted(candidates, key=lambda item: item.rerank_score or 0.0, reverse=True)[:top_k]

    def _terms(self, text: str) -> list[str]:
        ascii_terms = re.findall(r"[a-zA-Z0-9]+", text.lower())
        chinese_chars = [char for char in text if "\u4e00" <= char <= "\u9fff"]
        return ascii_terms + chinese_chars


class BGEReranker:
    def __init__(self, model_path: str = "BAAI/bge-reranker-v2-m3", use_fp16: bool = False) -> None:
        from FlagEmbedding import FlagReranker

        self.model = FlagReranker(model_path, use_fp16=use_fp16)

    async def rerank(
        self, query: str, candidates: list[ScoredChunk], top_k: int = 5
    ) -> list[ScoredChunk]:
        pairs = [[query, candidate.text] for candidate in candidates]
        scores = await asyncio.to_thread(self.model.compute_score, pairs)
        if not isinstance(scores, list):
            scores = [scores]
        for candidate, score in zip(candidates, scores):
            candidate.rerank_score = float(score)
        return sorted(candidates, key=lambda item: item.rerank_score or 0.0, reverse=True)[:top_k]

