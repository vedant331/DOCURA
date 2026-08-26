"""Shared fixtures.

Tests never read the developer's real environment: ``_isolate_env`` strips every
``DOCURA_*`` variable and points the settings loader at an empty directory, so a
passing suite cannot depend on one machine's local configuration.
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator, Iterator
from pathlib import Path
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Environment, Settings, get_settings

TEST_DSN = "postgresql://test_user:test_password@localhost:5432/docura_test"


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> Iterator[None]:
    for key in list(os.environ):
        if key.startswith("DOCURA_"):
            monkeypatch.delenv(key, raising=False)
    # Point the loader at an empty directory so a real .env is never picked up.
    monkeypatch.chdir(tmp_path)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def settings() -> Settings:
    """Valid settings for a test-environment app."""
    return Settings(
        environment=Environment.TEST,
        database_url=TEST_DSN,
    )


class StubEngine:
    """Stands in for an ``AsyncEngine`` so HTTP tests need no live database.

    ``check_health`` is patched per test to decide what this engine "answers"; the
    stub itself only needs to be disposable.
    """

    def __init__(self) -> None:
        self.disposed = False

    async def dispose(self) -> None:
        self.disposed = True


@pytest.fixture
async def client(settings: Settings, monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    """An app with a stubbed database, exercised through the real middleware stack.

    Lifespan is bypassed rather than simulated: startup connectivity is covered
    directly in ``test_startup.py``, and repeating it here would make every HTTP
    test depend on that machinery.
    """
    from app.main import create_app

    app = create_app(settings)
    app.state.engine = StubEngine()

    async def _healthy(_engine: Any) -> bool:
        return True

    monkeypatch.setattr("app.api.health.check_health", _healthy)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client
