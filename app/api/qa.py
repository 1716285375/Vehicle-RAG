import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.qa.chain import RAGChain

router = APIRouter()


class QARequest(BaseModel):
    question: str = Field(min_length=1)
    filters: dict | None = None
    session_id: str | None = None


@router.post("/qa")
async def qa(request: QARequest) -> dict:
    return await RAGChain().answer(request.question, request.filters)


@router.post("/qa/stream")
async def qa_stream(request: QARequest) -> StreamingResponse:
    async def events():
        async for event in RAGChain().stream_events(request.question, request.filters):
            yield f"event: {event.event}\n"
            yield "data: " + json.dumps(event.data, ensure_ascii=False) + "\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")

