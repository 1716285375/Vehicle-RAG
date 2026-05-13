import builtins

from app.retrieval.milvus_store import MilvusVectorStore


def test_milvus_store_requires_pymilvus(monkeypatch):
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "pymilvus":
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    try:
        MilvusVectorStore()
    except RuntimeError as exc:
        assert "Install pymilvus" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError")
