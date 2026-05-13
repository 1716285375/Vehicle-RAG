from typing import Protocol

from app.config.settings import settings


class DatabaseBackend(Protocol):
    async def connect(self) -> None:
        raise NotImplementedError

    async def close(self) -> None:
        raise NotImplementedError

    async def healthcheck(self) -> bool:
        raise NotImplementedError


class NullDatabase:
    async def connect(self) -> None:
        return None

    async def close(self) -> None:
        return None

    async def healthcheck(self) -> bool:
        return True


class MySQLDatabase:
    def __init__(self, dsn: str) -> None:
        self.dsn = dsn
        self._engine = None
        self._text = None

    async def connect(self) -> None:
        if self._engine is not None:
            return
        try:
            from sqlalchemy import text
            from sqlalchemy.ext.asyncio import create_async_engine
        except ImportError as exc:
            raise RuntimeError("Install the mysql extra to use MySQLDatabase.") from exc
        self._text = text
        self._engine = create_async_engine(self.dsn, pool_pre_ping=True)

    async def close(self) -> None:
        if self._engine is None:
            return
        await self._engine.dispose()
        self._engine = None

    async def healthcheck(self) -> bool:
        await self.connect()
        assert self._engine is not None
        assert self._text is not None
        async with self._engine.connect() as conn:
            await conn.execute(self._text("SELECT 1"))
        return True


def build_database(mysql_dsn: str | None = None) -> DatabaseBackend:
    if mysql_dsn:
        return MySQLDatabase(mysql_dsn)
    return NullDatabase()


database = build_database(settings.mysql_dsn)
