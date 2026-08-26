"""Logging pipeline and redaction.

NFR-OBS-004 requires diagnosable failures that carry no personal values. These
tests hold the second half of that sentence.
"""

from __future__ import annotations

import json
import logging
from typing import Any

import pytest

from app.core.config import Environment, Settings
from app.core.logging import REDACTED, configure_logging, get_logger, redact_processor
from tests.conftest import TEST_DSN


def _redact(event: dict[str, Any]) -> dict[str, Any]:
    """Run one event through the redaction processor."""
    return dict(redact_processor(None, "info", event))


class TestRedaction:
    @pytest.mark.parametrize(
        "key",
        [
            "password",
            "passwd",
            "secret",
            "token",
            "access_token",
            "refresh_token",
            "api_key",
            "authorization",
            "cookie",
            "session_id",
            "private_key",
            "database_url",
            "dsn",
        ],
    )
    def test_credential_keys_are_masked(self, key: str) -> None:
        assert _redact({key: "sensitive-value"})[key] == REDACTED

    @pytest.mark.parametrize(
        "key",
        [
            "document_content",
            "extracted_text",
            "ocr_text",
            "attribute_value",
            "field_value",
            "filled_value",
        ],
    )
    def test_record_content_keys_are_masked(self, key: str) -> None:
        """BR-017 and FR-AUD-006: document content does not belong in an ops log."""
        assert _redact({key: "Aadhaar 1234 5678 9012"})[key] == REDACTED

    @pytest.mark.parametrize("key", ["API_KEY", "apiKey", "Api-Key", "api_key"])
    def test_key_matching_ignores_case_and_separators(self, key: str) -> None:
        assert _redact({key: "abc"})[key] == REDACTED

    def test_ordinary_keys_survive(self) -> None:
        event = _redact({"path": "/health", "status_code": 200, "duration_ms": 1.2})

        assert event["path"] == "/health"
        assert event["status_code"] == 200

    def test_nested_dictionaries_are_redacted(self) -> None:
        event = _redact({"context": {"user": {"email": "a@b.test", "password": "hunter2"}}})

        context = event["context"]["user"]
        assert context["password"] == REDACTED
        assert context["email"] == "a@b.test"

    def test_lists_of_dictionaries_are_redacted(self) -> None:
        event = _redact({"attempts": [{"token": "one"}, {"token": "two"}]})

        attempts: list[dict[str, Any]] = event["attempts"]
        assert all(item["token"] == REDACTED for item in attempts)

    def test_deep_nesting_terminates(self) -> None:
        """Redaction must not recurse without bound on a hostile or cyclic structure."""
        deep: dict[str, object] = {"password": "leaf"}
        for _ in range(20):
            deep = {"nested": deep}

        _redact(deep)  # must return rather than hit the recursion limit

    def test_tuple_type_is_preserved(self) -> None:
        event = _redact({"values": ({"token": "x"},)})

        assert isinstance(event["values"], tuple)


class TestPipeline:
    def test_json_rendering_in_production(self, capsys: pytest.CaptureFixture[str]) -> None:
        configure_logging(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))
        get_logger("test").info("service.started", port=8000)

        line = capsys.readouterr().out.strip().splitlines()[-1]
        payload = json.loads(line)

        assert payload["event"] == "service.started"
        assert payload["port"] == 8000
        assert payload["level"] == "info"
        assert "timestamp" in payload

    def test_console_rendering_locally(self, capsys: pytest.CaptureFixture[str]) -> None:
        configure_logging(Settings(environment=Environment.LOCAL, database_url=TEST_DSN))
        get_logger("test").info("service.started")

        assert "service.started" in capsys.readouterr().out

    def test_secret_never_reaches_the_stream(self, capsys: pytest.CaptureFixture[str]) -> None:
        configure_logging(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))
        get_logger("test").info("database.connected", password="hunter2", dsn=TEST_DSN)

        output = capsys.readouterr().out
        assert "hunter2" not in output
        assert "test_password" not in output
        assert REDACTED in output

    def test_log_level_is_honoured(self, capsys: pytest.CaptureFixture[str]) -> None:
        configure_logging(
            Settings(
                environment=Environment.PRODUCTION,
                database_url=TEST_DSN,
                log_level="ERROR",
            )
        )
        logger = get_logger("test")
        logger.info("should.not.appear")
        logger.error("should.appear")

        output = capsys.readouterr().out
        assert "should.not.appear" not in output
        assert "should.appear" in output

    def test_uvicorn_loggers_are_routed_through_the_pipeline(self) -> None:
        """Otherwise uvicorn's own handlers would emit unredacted access lines."""
        configure_logging(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))

        for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            uvicorn_logger = logging.getLogger(name)
            assert uvicorn_logger.handlers == []
            assert uvicorn_logger.propagate is True


class TestRequestContext:
    async def test_request_id_is_bound_to_log_events(
        self,
        settings: Settings,
        monkeypatch: pytest.MonkeyPatch,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Every line emitted while serving a request carries its correlation ID.

        The app is built with JSON rendering forced on so the assertion reads the
        real pipeline's output rather than a substituted processor — ``configure_logging``
        caches bound loggers, so swapping processors after the fact would not affect
        the loggers the middleware already holds.
        """
        from httpx import ASGITransport, AsyncClient

        from app.main import create_app
        from tests.conftest import StubEngine

        json_settings = settings.model_copy(update={"log_json": True})
        app = create_app(json_settings)
        app.state.engine = StubEngine()

        async def _healthy(_engine: object) -> bool:
            return True

        monkeypatch.setattr("app.api.health.check_health", _healthy)

        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as http:
            await http.get("/health", headers={"X-Request-ID": "corr-1"})

        events = [
            json.loads(line)
            for line in capsys.readouterr().out.splitlines()
            if line.startswith("{")
        ]

        completed = [event for event in events if event.get("event") == "request.completed"]
        assert completed, "the access log line was not emitted"
        assert completed[0]["request_id"] == "corr-1"
        assert completed[0]["status_code"] == 200
        assert completed[0]["path"] == "/health"


class TestStandardLibraryLogs:
    """Third-party libraries log through the stdlib, and must be redacted too."""

    def test_foreign_records_are_rendered_by_the_same_pipeline(
        self, capsys: pytest.CaptureFixture[str]
    ) -> None:
        configure_logging(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))

        logging.getLogger("uvicorn.error").warning("started on port %s", 8001)

        line = capsys.readouterr().out.strip().splitlines()[-1]
        payload = json.loads(line)

        assert payload["event"] == "started on port 8001"
        assert payload["logger"] == "uvicorn.error"
        assert payload["level"] == "warning"

    def test_foreign_record_extras_are_redacted(self, capsys: pytest.CaptureFixture[str]) -> None:
        """A library that logs a credential in `extra` must not defeat redaction."""
        configure_logging(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))

        logging.getLogger("sqlalchemy.engine").warning(
            "connect failed", extra={"password": "hunter2", "host": "db.internal"}
        )

        output = capsys.readouterr().out
        assert "hunter2" not in output
        assert REDACTED in output
        assert "db.internal" in output

    def test_uvicorn_loggers_have_no_handlers_of_their_own(self) -> None:
        configure_logging(Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN))

        for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
            uvicorn_logger = logging.getLogger(name)
            assert uvicorn_logger.handlers == []
            assert uvicorn_logger.propagate is True

    def test_root_has_exactly_one_handler_after_repeated_configuration(self) -> None:
        """Re-configuring must replace the handler, not stack duplicates onto root."""
        settings = Settings(environment=Environment.PRODUCTION, database_url=TEST_DSN)

        configure_logging(settings)
        configure_logging(settings)
        configure_logging(settings)

        assert len(logging.getLogger().handlers) == 1
