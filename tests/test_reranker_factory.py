from app.retrieval import LightweightReranker, build_reranker


def test_build_reranker_returns_lightweight_default():
    assert isinstance(build_reranker("lightweight"), LightweightReranker)


def test_build_reranker_rejects_unknown_provider():
    try:
        build_reranker("unknown")
    except ValueError as exc:
        assert "Unsupported reranker provider" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
