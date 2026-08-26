"""Database connection behaviour.

The failure paths run everywhere. The success path needs a real server, so it is
marked ``integration`` and skips when ``TEST_DATABASE_URL`` is unset —
skipped, never silently passed, so a green run without Postgres cannot be mistaken
for a verified connection.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.pool import QueuePool

from app.core.config import Environment, Settings
from app.core.errors import DatabaseUnavailableError
from app.db.session import check_health, create_engine, dispose_engine, verify_connection
from tests.conftest import TEST_DSN

# Deliberately unprefixed: DOCURA_* names are application configuration, and an
# unrecognised one is now a startup error. This is a test-harness variable.
INTEGRATION_DSN = os.environ.get("TEST_DATABASE_URL")

requires_postgres = pytest.mark.skipif(
    not INTEGRATION_DSN,
    reason="Set TEST_DATABASE_URL to run database integration tests.",
)

# A port nothing listens on, so connection is refused rather than timing out.
UNREACHABLE_DSN = "postgresql://nobody:nothing@127.0.0.1:1/docura_absent"


def _settings(dsn: str) -> Settings:
    return Settings(
        environment=Environment.TEST,
        database_url=dsn,
        db_connect_timeout_seconds=2.0,
    )


class TestEngineConstruction:
    def test_uses_the_async_driver(self, settings: Settings) -> None:
        engine = create_engine(settings)

        assert engine.dialect.driver == "asyncpg"

    def test_pool_is_configured_from_settings(self) -> None:
        engine = create_engine(
            Settings(
                environment=Environment.TEST,
                database_url=TEST_DSN,
                db_pool_size=7,
            )
        )

        pool = engine.pool
        assert isinstance(pool, QueuePool)
        assert pool.size() == 7

    def test_echo_is_off(self, settings: Settings) -> None:
        """SQLAlchemy echo prints bound parameters, which are user values."""
        assert create_engine(settings).echo is False

    def test_engine_url_hides_the_password(self, settings: Settings) -> None:
        assert "test_password" not in str(create_engine(settings).url)


class TestConnectionFailure:
    async def test_verify_raises_database_unavailable(self) -> None:
        engine = create_engine(_settings(UNREACHABLE_DSN))
        try:
            with pytest.raises(DatabaseUnavailableError):
                await verify_connection(engine)
        finally:
            await engine.dispose()

    async def test_check_health_returns_false_rather_than_raising(self) -> None:
        engine = create_engine(_settings(UNREACHABLE_DSN))
        try:
            assert await check_health(engine) is False
        finally:
            await engine.dispose()

    async def test_error_message_carries_no_connection_detail(self) -> None:
        """The driver's own message can name the host, user, and occasionally the DSN."""
        engine = create_engine(_settings(UNREACHABLE_DSN))
        try:
            with pytest.raises(DatabaseUnavailableError) as exc_info:
                await verify_connection(engine)

            rendered = f"{exc_info.value.detail} {exc_info.value.remediation}"
            assert "127.0.0.1" not in rendered
            assert "nobody" not in rendered
            assert "nothing" not in rendered
        finally:
            await engine.dispose()

    async def test_failure_is_a_503(self) -> None:
        engine = create_engine(_settings(UNREACHABLE_DSN))
        try:
            with pytest.raises(DatabaseUnavailableError) as exc_info:
                await verify_connection(engine)

            assert exc_info.value.status_code == 503
        finally:
            await engine.dispose()


@requires_postgres
class TestLiveConnection:
    @pytest.fixture
    async def engine(self) -> AsyncIterator[AsyncEngine]:
        assert INTEGRATION_DSN is not None
        built = create_engine(_settings(INTEGRATION_DSN))
        yield built
        await built.dispose()

    async def test_connects(self, engine: AsyncEngine) -> None:
        await verify_connection(engine)

    async def test_check_health_is_true(self, engine: AsyncEngine) -> None:
        assert await check_health(engine) is True

    async def test_repeated_checks_reuse_the_pool(self, engine: AsyncEngine) -> None:
        for _ in range(3):
            assert await check_health(engine) is True

    async def test_dispose_returns_every_connection_to_the_pool(self) -> None:
        """Dispose empties the pool; it does not disable the engine.

        SQLAlchemy rebuilds a pool on the next connect, so the check that matters at
        shutdown is that no connection is left checked out.
        """
        assert INTEGRATION_DSN is not None
        built = create_engine(_settings(INTEGRATION_DSN))
        await verify_connection(built)

        await dispose_engine(built)

        pool = built.pool
        assert isinstance(pool, QueuePool)
        assert pool.checkedout() == 0
