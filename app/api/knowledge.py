from fastapi import APIRouter, Query

from app.retrieval import build_vector_store

router = APIRouter()


@router.get("/knowledge/documents")
async def list_documents(
    doc_id: str | None = Query(default=None),
    doc_type: str | None = Query(default=None),
    vehicle_model: str | None = Query(default=None),
) -> dict:
    documents = await build_vector_store().list_documents()
    filters = {
        "doc_id": doc_id,
        "doc_type": doc_type,
        "vehicle_model": vehicle_model,
    }
    return {"documents": [_doc for _doc in documents if _matches_document(_doc, filters)]}


@router.delete("/knowledge/documents/{doc_id}")
async def delete_document(doc_id: str) -> dict:
    deleted_chunks = await build_vector_store().delete(doc_id)
    return {"doc_id": doc_id, "deleted_chunks": deleted_chunks}


@router.post("/knowledge/rebuild")
async def rebuild() -> dict:
    return {"status": "not_implemented", "message": "Use scripts/rebuild_index.py for local rebuilds."}


def _matches_document(document: dict, filters: dict[str, str | None]) -> bool:
    metadata = document.get("metadata", {})
    for key, expected in filters.items():
        if expected is None:
            continue
        if document.get(key) != expected and metadata.get(key) != expected:
            return False
    return True
