from app.config.settings import settings
from app.retrieval.reranker import BGEReranker, LightweightReranker


def build_reranker(provider: str | None = None):
    backend = (provider or settings.reranker_provider).strip().lower()
    if backend == "lightweight":
        return LightweightReranker()
    if backend == "bge":
        return BGEReranker(model_path=settings.rerank_model_path, use_fp16=settings.rerank_use_fp16)
    raise ValueError(f"Unsupported reranker provider: {backend}")
