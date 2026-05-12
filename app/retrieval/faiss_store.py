from app.retrieval.json_store import JsonVectorStore


class FaissVectorStore(JsonVectorStore):
    """Placeholder-compatible store.

    The MVP persists JSON for portability. This class keeps the public module
    boundary expected by dev.md so FAISS can replace internals later.
    """

