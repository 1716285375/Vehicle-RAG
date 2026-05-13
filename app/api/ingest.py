import json
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.config.settings import settings
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter()


def parse_metadata(metadata: str) -> dict:
    if not metadata:
        return {}
    try:
        parsed = json.loads(metadata)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=422, detail=f"Invalid metadata JSON: {exc.msg}") from exc
    if not isinstance(parsed, dict):
        raise HTTPException(status_code=422, detail="metadata must be a JSON object")
    return parsed


@router.post("/ingest")
async def ingest(
    file: UploadFile = File(...),
    doc_type: str = Form(...),
    metadata: str = Form(default="{}"),
) -> dict:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    target = settings.upload_dir / Path(file.filename or "upload.bin").name
    with target.open("wb") as output:
        shutil.copyfileobj(file.file, output)
    parsed_metadata = parse_metadata(metadata)
    try:
        return await IngestionPipeline().ingest(target, doc_type=doc_type, metadata=parsed_metadata)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
