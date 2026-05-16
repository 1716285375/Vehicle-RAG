from app.embedding import CachedEmbedder, HashEmbedder, build_embedder


def test_build_embedder_returns_cached_hash_embedder():
    embedder = build_embedder("hash")
    assert isinstance(embedder, CachedEmbedder)
    assert isinstance(embedder.inner, HashEmbedder)


def test_build_embedder_can_disable_cache():
    embedder = build_embedder("hash", cached=False)
    assert isinstance(embedder, HashEmbedder)


def test_build_embedder_rejects_unknown_provider():
    try:
        build_embedder("unknown")
    except ValueError as exc:
        assert "Unsupported embedding provider" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
