import pytest
from pydantic import ValidationError

from app.config.settings import Settings


def test_settings_normalizes_vector_store_name():
    settings = Settings(vector_store=" FAISS ")
    assert settings.vector_store == "faiss"


def test_settings_rejects_unknown_vector_store():
    with pytest.raises(ValidationError, match="unsupported vector store"):
        Settings(vector_store="sqlite")


def test_settings_rejects_unknown_embedding_provider():
    with pytest.raises(ValidationError, match="unsupported embedding provider"):
        Settings(embedding_provider="unknown")


def test_settings_rejects_unknown_reranker_provider():
    with pytest.raises(ValidationError, match="unsupported reranker provider"):
        Settings(reranker_provider="unknown")


def test_settings_rejects_non_positive_runtime_values():
    with pytest.raises(ValidationError, match="must be greater than 0"):
        Settings(retrieval_top_k=0)


def test_settings_rejects_invalid_context_budget():
    with pytest.raises(ValidationError, match="context_min_chunk_tokens cannot exceed"):
        Settings(context_max_tokens=100, context_min_chunk_tokens=101)
