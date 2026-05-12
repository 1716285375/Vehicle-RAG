import json
import shutil
from pathlib import Path

from fastapi import APIRouter, File, Form, UploadFile

from app.config.settings import settings
from app.ingestion.pipeline import IngestionPipeline

router = APIRouter()


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
    parsed_metadata = json.loads(metadata) if metadata else {}
    return await IngestionPipeline().ingest(target, doc_type=doc_type, metadata=parsed_metadata)

