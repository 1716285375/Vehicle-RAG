from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Vehicle-RAG"
    app_host: str = "0.0.0.0"
    app_port: int = 8001

    data_dir: Path = Path("data")
    upload_dir: Path = Path("data/raw/uploads")
    index_path: Path = Path("data/processed/vector_index.json")

    embedding_dim: int = 384
    retrieval_top_k: int = 20
    rerank_top_k: int = 5
    context_max_tokens: int = 3000
    qa_cache_ttl: int = 3600
    redis_url: str | None = None

    llm_base_url: str | None = None
    llm_api_key: str | None = None
    llm_model: str = "qwen-max"
    llm_timeout: float = 60.0

    vector_store: str = Field(default="json", description="json | faiss | milvus")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
