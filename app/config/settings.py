from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SUPPORTED_VECTOR_STORES = {"json", "faiss", "milvus"}


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Vehicle-RAG"
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    data_dir: Path = Path("data")
    upload_dir: Path = Path("data/raw/uploads")
    processed_dir: Path = Path("data/processed")
    index_path: Path = Path("data/processed/vector_index.json")
    faiss_index_path: Path = Path("data/processed/faiss.index")
    session_store_path: Path = Path("data/processed/sessions.json")

    embedding_provider: str = "hash"
    embed_model_path: str = "BAAI/bge-m3"
    embed_device: str = "cpu"
    embed_batch_size: int = 32
    embedding_dim: int = 384
    retrieval_top_k: int = 20
    rerank_top_k: int = 5
    min_relevance_score: float = 0.05
    context_max_tokens: int = 3000
    context_min_chunk_tokens: int = 80
    qa_cache_ttl: int = 3600
    embedding_cache_ttl: int = 86400
    redis_url: str | None = None
    mysql_dsn: str | None = None

    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str = "qwen-max"
    llm_timeout: float = 60.0
    enable_llm_query_rewrite: bool = False

    vector_store: str = Field(default="json", description="json | faiss | milvus")
    milvus_host: str = "localhost"
    milvus_port: int = 19530
    milvus_collection: str = "vehicle_kb"

    @field_validator(
        "app_port",
        "embed_batch_size",
        "embedding_dim",
        "retrieval_top_k",
        "rerank_top_k",
        "context_max_tokens",
        "context_min_chunk_tokens",
        "qa_cache_ttl",
        "embedding_cache_ttl",
        "milvus_port",
    )
    @classmethod
    def _must_be_positive(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("must be greater than 0")
        return value

    @field_validator("llm_timeout")
    @classmethod
    def _timeout_must_be_positive(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("must be greater than 0")
        return value

    @field_validator("min_relevance_score")
    @classmethod
    def _score_must_be_non_negative(cls, value: float) -> float:
        if value < 0:
            raise ValueError("must be greater than or equal to 0")
        return value

    @field_validator("vector_store")
    @classmethod
    def _normalize_vector_store(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_VECTOR_STORES:
            allowed = ", ".join(sorted(SUPPORTED_VECTOR_STORES))
            raise ValueError(f"unsupported vector store '{value}', expected one of: {allowed}")
        return normalized

    @field_validator("embedding_provider")
    @classmethod
    def _normalize_embedding_provider(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in {"hash", "bge-m3"}:
            raise ValueError("unsupported embedding provider, expected one of: hash, bge-m3")
        return normalized

    @model_validator(mode="after")
    def _validate_context_budget(self) -> "Settings":
        if self.context_min_chunk_tokens > self.context_max_tokens:
            raise ValueError("context_min_chunk_tokens cannot exceed context_max_tokens")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
