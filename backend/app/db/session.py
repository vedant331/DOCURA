"""Database engine lifecycle and connectivity checks.

Sprint 1 owns the *connection*, not the schema. There are no models and no
migrations here; the DOCURA data model is later-sprint work. What this module
guarantees is that the service knows whether Postgres is reachable, says so
clearly when it is not, and never puts a credential in a log line while doing it.
"""

from __future__ import annotations

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from app.core.config import Settings
from app.core.errors import DatabaseUnavailableError
from app.core.logging import get_logger

logger = get_logger(__name__)

_LIVENESS_QUERY = text("SELECT 1")


def create_engine(settings: Settings) -> AsyncEngine:
    """Build the async engine.

    ``pool_pre_ping`` is on because the failure it prevents — handing out a
    connection the server closed while idle — surfaces as an unexplained 500 on a
    user's request rather than as a connection error at the pool.
    """
    return create_async_engine(
        settings.async_database_url,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
        connect_args={"timeout": settings.db_connect_timeout_seconds},
        echo=False,  # SQLAlchemy echo prints bound parameters — never enable here
    )


async def verify_connection(engine: AsyncEngine) -> None:
    """Run a trivial query, raising ``DatabaseUnavailableError`` if it fails.

    The driver's own message can carry the host, user, and occasionally the DSN, so
    it is attached to the log record's exception info and deliberately kept out of
    the raised error's user-facing text.
    """
    try:
        async with engine.connect() as connection:
            await connection.execute(_LIVENESS_QUERY)
    except (SQLAlchemyError, OSError) as exc:
        logger.error(
            "database.unreachable",
            error_class=type(exc).__name__,
            exc_info=exc,
        )
        raise DatabaseUnavailableError from exc


async def check_health(engine: AsyncEngine) -> bool:
    """Non-raising probe for the readiness endpoint."""
    try:
        await verify_connection(engine)
    except DatabaseUnavailableError:
        return False
    return True


async def dispose_engine(engine: AsyncEngine) -> None:
    """Close pooled connections on shutdown."""
    await engine.dispose()
    logger.info("database.disconnected")
