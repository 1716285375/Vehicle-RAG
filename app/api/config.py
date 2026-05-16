from fastapi import APIRouter

from app.config.settings import settings

router = APIRouter()

PUBLIC_SETTINGS = (
    "app_name",
    "app_host",
    "app_port",
    "embedding_provider",
    "embedding_dim",
    "retrieval_top_k",
    "rerank_top_k",
    "reranker_provider",
    "min_relevance_score",
    "context_max_tokens",
    "context_min_chunk_tokens",
    "vector_store",
    "milvus_host",
    "milvus_port",
    "milvus_collection",
    "enable_llm_query_rewrite",
)


@router.get("/config")
async def get_public_config() -> dict:
    return {"config": {name: getattr(settings, name) for name in PUBLIC_SETTINGS}}
