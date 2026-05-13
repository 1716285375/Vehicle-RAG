import asyncio

from app.infra.mysql_client import MySQLDatabase, NullDatabase, build_database


def test_build_database_returns_null_without_dsn():
    assert isinstance(build_database(None), NullDatabase)


def test_build_database_returns_mysql_with_dsn():
    assert isinstance(build_database("mysql+aiomysql://user:pass@localhost/db"), MySQLDatabase)


def test_null_database_healthcheck_is_true():
    asyncio.run(_run_null_database_healthcheck_is_true())


async def _run_null_database_healthcheck_is_true():
    assert await NullDatabase().healthcheck() is True
