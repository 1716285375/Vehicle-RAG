from app.config.settings import settings
from app.embedding.bge_m3 import BGEM3Embedder, HashEmbedder
from app.embedding.cache import CachedEmbedder


def build_embedder(provider: str | None = None, cached: bool = True):
    backend = (provider or settings.embedding_provider).strip().lower()
    if backend == "hash":
        embedder = HashEmbedder(dim=settings.embedding_dim)
    elif backend == "bge-m3":
        embedder = BGEM3Embedder(model_path=settings.embed_model_path, device=settings.embed_device)
    else:
        raise ValueError(f"Unsupported embedding provider: {backend}")
    return CachedEmbedder(embedder) if cached else embedder
