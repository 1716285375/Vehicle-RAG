from fastapi import FastAPI

from app.api.config import router as config_router
from app.api.ingest import router as ingest_router
from app.api.knowledge import router as knowledge_router
from app.api.qa import router as qa_router
from app.api.session import router as session_router
from app.config.settings import settings
from app.infra.logger import configure_logging
from app.infra.mysql_client import database
from app.infra.request_logging import RequestLoggingMiddleware
from app.retrieval import build_vector_store


def create_app() -> FastAPI:
    configure_logging()
    app = FastAPI(title=settings.app_name, version="0.1.0")
    app.add_middleware(RequestLoggingMiddleware)
    app.include_router(config_router, prefix="/v1", tags=["config"])
    app.include_router(qa_router, prefix="/v1", tags=["qa"])
    app.include_router(ingest_router, prefix="/v1", tags=["ingest"])
    app.include_router(knowledge_router, prefix="/v1", tags=["knowledge"])
    app.include_router(session_router, prefix="/v1", tags=["session"])

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/health/db")
    async def database_health() -> dict[str, bool]:
        return {"ok": await database.healthcheck()}

    @app.get("/health/ready")
    async def readiness() -> dict:
        db_ok = await database.healthcheck()
        vector_ok = await build_vector_store().healthcheck()
        return {"ok": db_ok and vector_ok, "database": db_ok, "vector_store": vector_ok}

    return app


app = create_app()
