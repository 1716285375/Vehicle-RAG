from fastapi import APIRouter

from app.retrieval import build_vector_store

router = APIRouter()


@router.get("/knowledge/documents")
async def list_documents() -> dict:
    return {"documents": await build_vector_store().list_documents()}


@router.delete("/knowledge/documents/{doc_id}")
async def delete_document(doc_id: str) -> dict:
    deleted_chunks = await build_vector_store().delete(doc_id)
    return {"doc_id": doc_id, "deleted_chunks": deleted_chunks}


@router.post("/knowledge/rebuild")
async def rebuild() -> dict:
    return {"status": "not_implemented", "message": "Use scripts/rebuild_index.py for local rebuilds."}
