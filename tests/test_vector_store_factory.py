from app.retrieval import JsonVectorStore, build_vector_store


def test_build_vector_store_returns_json_backend():
    assert isinstance(build_vector_store("json"), JsonVectorStore)


def test_build_vector_store_rejects_unknown_backend():
    try:
        build_vector_store("unknown")
    except ValueError as exc:
        assert "Unsupported vector store backend" in str(exc)
    else:
        raise AssertionError("Expected ValueError")
