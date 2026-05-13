from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.ingestion.rebuild import rebuild_index
from app.retrieval import build_vector_store

router = APIRouter()


class RebuildRequest(BaseModel):
    directory: str = Field(min_length=1)
    doc_type: str = Field(min_length=1)
    metadata: dict[str, Any] | None = None


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
async def rebuild(request: RebuildRequest) -> dict:
    try:
        result = await rebuild_index(Path(request.directory), request.doc_type, request.metadata)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return {"status": "completed", **result}


def _matches_document(document: dict, filters: dict[str, str | None]) -> bool:
    metadata = document.get("metadata", {})
    for key, expected in filters.items():
        if expected is None:
            continue
        if document.get(key) != expected and metadata.get(key) != expected:
            return False
    return True
