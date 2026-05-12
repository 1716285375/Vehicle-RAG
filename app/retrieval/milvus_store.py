from app.retrieval.vector_store import VectorStore


class MilvusVectorStore(VectorStore):
    def __init__(self, *args, **kwargs) -> None:
        raise NotImplementedError("MilvusVectorStore is reserved for the production backend.")

