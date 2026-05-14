import json

from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.infra.session_store import session_store
from app.models import SessionTurn
from app.qa.chain import RAGChain

router = APIRouter()


class QARequest(BaseModel):
    question: str = Field(min_length=1)
    filters: dict | None = None
    session_id: str | None = None


@router.post("/qa")
async def qa(request: QARequest) -> dict:
    result = await RAGChain().answer(request.question, request.filters)
    if request.session_id:
        await session_store.append(
            SessionTurn(
                session_id=request.session_id,
                question=request.question,
                answer=result["answer"],
                citations=result.get("citations", []),
                filters=request.filters,
            )
        )
    return result


@router.post("/qa/retrieve")
async def retrieve(request: QARequest) -> dict:
    return await RAGChain().retrieve_debug(request.question, request.filters)


@router.post("/qa/stream")
async def qa_stream(request: QARequest) -> StreamingResponse:
    async def events():
        async for event in RAGChain().stream_events(request.question, request.filters):
            if event.event == "final" and request.session_id:
                await session_store.append(
                    SessionTurn(
                        session_id=request.session_id,
                        question=request.question,
                        answer=event.data["answer"],
                        citations=event.data.get("citations", []),
                        filters=request.filters,
                    )
                )
            yield f"event: {event.event}\n"
            yield "data: " + json.dumps(event.data, ensure_ascii=False) + "\n\n"
        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream")
