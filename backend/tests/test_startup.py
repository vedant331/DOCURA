"""Application startup and shutdown."""

from __future__ import annotations

from typing import Any

import pytest
from asgi_lifespan import LifespanManager
from fastapi import FastAPI

from app.core.config import Environment, Settings
from app.core.errors import DatabaseUnavailableError
from app.main import create_app
from tests.conftest import TEST_DSN


def _middleware_names(app: FastAPI) -> list[str]:
    """Middleware classes are wrapped, so read the name off the wrapped class."""
    return [getattr(m.cls, "__name__", type(m.cls).__name__) for m in app.user_middleware]


class TestApplicationFactory:
    def test_builds_with_injected_settings(self, settings: Settings) -> None:
        app = create_app(settings)

        assert app.state.settings is settings
        assert app.title == "DOCURA Backend"

    def test_health_routes_are_registered(self, settings: Settings) -> None:
        paths = set(create_app(settings).openapi()["paths"])

        assert "/health" in paths
        assert "/health/ready" in paths

    def test_docs_exposed_outside_production(self, settings: Settings) -> None:
        assert create_app(settings).docs_url == "/docs"

    def test_docs_hidden_in_production(self) -> None:
        """The schema is an unnecessary description of the attack surface in production."""
        production = create_app(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))

        assert production.docs_url is None
        assert production.openapi_url is None

    def test_cors_is_absent_when_no_origins_configured(self, settings: Settings) -> None:
        stack = _middleware_names(create_app(settings))

        assert "CORSMiddleware" not in stack

    def test_cors_added_for_configured_origins(self) -> None:
        configured = create_app(
            Settings(
                environment=Environment.TEST,
                database_url=TEST_DSN,
                cors_allow_origins=("https://app.docura.test",),
            )
        )
        stack = _middleware_names(configured)

        assert "CORSMiddleware" in stack


class TestLifespan:
    async def test_starts_when_the_database_is_reachable(
        self, settings: Settings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        disposed: list[bool] = []

        class _Engine:
            async def dispose(self) -> None:
                disposed.append(True)

        async def _ok(_engine: Any) -> None:
            return None

        monkeypatch.setattr("app.main.create_engine", lambda _settings: _Engine())
        monkeypatch.setattr("app.main.verify_connection", _ok)

        app = create_app(settings)
        async with LifespanManager(app):
            assert app.state.engine is not None

        assert disposed == [True], "the engine must be disposed on shutdown"

    async def test_startup_fails_when_the_database_is_unreachable(
        self, settings: Settings, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A service that boots into a permanently broken state hides the outage."""
        disposed: list[bool] = []

        class _Engine:
            async def dispose(self) -> None:
                disposed.append(True)

        async def _fail(_engine: Any) -> None:
            raise DatabaseUnavailableError

        monkeypatch.setattr("app.main.create_engine", lambda _settings: _Engine())
        monkeypatch.setattr("app.main.verify_connection", _fail)

        app = create_app(settings)
        with pytest.raises(DatabaseUnavailableError):
            async with LifespanManager(app):
                pass

        assert disposed == [True], "a failed startup must still release the pool"

    async def test_startup_logs_no_credentials(
        self,
        settings: Settings,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        class _Engine:
            async def dispose(self) -> None:
                return None

        async def _ok(_engine: Any) -> None:
            return None

        monkeypatch.setattr("app.main.create_engine", lambda _settings: _Engine())
        monkeypatch.setattr("app.main.verify_connection", _ok)

        async with LifespanManager(create_app(settings)):
            pass

        output = capsys.readouterr().out
        assert "test_password" not in output
        assert "test_user" not in output
        assert "docura_test" in output, "the target database should still be identifiable"


class TestEntrypoint:
    def test_invalid_configuration_exits_with_ex_config(
        self, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
    ) -> None:
        """No DOCURA_DATABASE_URL is set, so main() must refuse to serve."""
        from app.main import main

        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 78  # EX_CONFIG
        assert "FATAL" in capsys.readouterr().err

    def test_startup_failure_message_names_the_variable(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        from app.main import main

        with pytest.raises(SystemExit):
            main()

        assert "DOCURA_DATABASE_URL" in capsys.readouterr().err
