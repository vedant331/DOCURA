"""S2-T012 — no credential or token reaches a log sink.

Sprint 1 proved the redaction processor masks named keys. This proves the property
that actually matters: driving real authentication traffic through the real logging
pipeline emits no password and no session token, whether or not anyone remembered
to name a field carefully.
"""

from __future__ import annotations

import io
import json
import logging
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from tests.conftest import (
    PASSWORD,
    RecordingResetDelivery,
    auth_header,
    request_reset_token,
    requires_postgres,
)

pytestmark = requires_postgres


@pytest.fixture
def log_sink() -> io.StringIO:
    """Buffer that receives everything the logging pipeline emits.

    Not ``capsys``: pytest swaps ``sys.stdout`` between the setup and call phases,
    and ``configure_logging`` binds whichever stream it sees when the app is built,
    so a fixture-built app would keep writing to the stream from setup. Attaching a
    handler after configuration captures the real pipeline regardless of phase.
    """
    return io.StringIO()


@pytest.fixture
async def logging_client(
    db_settings: Settings,
    db_engine: Any,
    log_sink: io.StringIO,
    reset_delivery: RecordingResetDelivery,
) -> Any:
    """An app rendering JSON logs into ``log_sink``."""
    from app.api.auth import reset_rate_limiter
    from app.db.session import create_session_factory
    from app.main import create_app

    reset_rate_limiter()
    app = create_app(db_settings.model_copy(update={"log_json": True}))
    app.state.engine = db_engine
    app.state.session_factory = create_session_factory(db_engine)
    app.state.reset_delivery = reset_delivery

    # Added after create_app, which clears root handlers as it configures logging.
    root = logging.getLogger()
    handler = logging.StreamHandler(log_sink)
    handler.setFormatter(root.handlers[0].formatter)
    root.addHandler(handler)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client
    finally:
        root.removeHandler(handler)
        reset_rate_limiter()


class TestAuthenticationLogging:
    async def test_password_never_appears_in_logs(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """S2-T012 — registration, successful login, and failed login."""
        email = "logged@docura.example"

        await logging_client.post("/auth/register", json={"email": email, "password": PASSWORD})
        await logging_client.post("/auth/login", json={"email": email, "password": PASSWORD})
        await logging_client.post(
            "/auth/login", json={"email": email, "password": "wrong-password-entirely"}
        )

        output = log_sink.getvalue()

        assert PASSWORD not in output
        assert "wrong-password-entirely" not in output

    async def test_session_token_never_appears_in_logs(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """S2-T012 — a token in a log file is a credential in a log file."""
        email = "token@docura.example"

        await logging_client.post("/auth/register", json={"email": email, "password": PASSWORD})
        login = await logging_client.post(
            "/auth/login", json={"email": email, "password": PASSWORD}
        )
        token = login.json()["access_token"]

        log_sink.truncate(0)  # discard everything logged up to this point
        log_sink.seek(0)

        await logging_client.get("/users/me", headers=auth_header(token))
        await logging_client.post("/auth/logout", headers=auth_header(token))

        output = log_sink.getvalue()

        assert token not in output
        assert "Bearer" not in output

    async def test_password_hash_never_appears_in_logs(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        await logging_client.post(
            "/auth/register", json={"email": "hashlog@docura.example", "password": PASSWORD}
        )

        assert "$argon2id$" not in log_sink.getvalue()

    async def test_failed_login_is_logged_without_the_attempted_password(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """NFR-OBS-004: diagnosable, and free of personal values.

        A failed sign-in must leave enough behind to investigate a break-in attempt,
        which means the event and its reason — and nothing that was typed.
        """
        await logging_client.post(
            "/auth/login",
            json={"email": "ghost@docura.example", "password": "attempted-secret-value"},
        )

        output = log_sink.getvalue()
        events = [json.loads(line) for line in output.splitlines() if line.startswith("{")]
        failures = [e for e in events if e.get("event") == "auth.login_failed"]

        assert failures, "a failed authentication must be observable"
        assert failures[0]["reason"] == "unknown_account"
        assert "attempted-secret-value" not in output

    async def test_request_id_correlates_authentication_events(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """Without a correlation id, a 401 in a log cannot be tied to its request."""
        await logging_client.post(
            "/auth/login",
            json={"email": "corr@docura.example", "password": PASSWORD},
            headers={"X-Request-ID": "auth-corr-1"},
        )

        events = [
            json.loads(line) for line in log_sink.getvalue().splitlines() if line.startswith("{")
        ]

        assert any(e.get("request_id") == "auth-corr-1" for e in events)


class TestSessionReferenceLogging:
    """`session_id` is redacted by default; DOCURA logs a primary key instead."""

    async def test_session_reference_is_recorded_and_readable(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """A revocation that cannot be traced to a session is not diagnosable."""
        await logging_client.post(
            "/auth/register", json={"email": "ref@docura.example", "password": PASSWORD}
        )
        login = await logging_client.post(
            "/auth/login", json={"email": "ref@docura.example", "password": PASSWORD}
        )
        token = login.json()["access_token"]
        await logging_client.post("/auth/logout", headers=auth_header(token))

        events = [
            json.loads(line) for line in log_sink.getvalue().splitlines() if line.startswith("{")
        ]
        created = next(e for e in events if e["event"] == "auth.session_created")
        revoked = next(e for e in events if e["event"] == "auth.session_revoked")

        assert created["session_ref"] not in ("", "***REDACTED***")
        assert created["session_ref"] == revoked["session_ref"]
        assert token not in log_sink.getvalue()

    def test_session_id_remains_redacted_for_future_callers(self) -> None:
        """The conservative default must stay in place for code written later."""
        from app.core.logging import REDACTED, redact_processor

        event = redact_processor(None, "info", {"session_id": "a-session-credential"})

        assert event["session_id"] == REDACTED


class TestPasswordResetLogging:
    """A reset token is a credential for the account until it is spent."""

    async def test_reset_token_never_appears_in_logs(
        self,
        logging_client: AsyncClient,
        log_sink: io.StringIO,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T026 — the whole flow, from request through to a spent token."""
        email = "resetlog@docura.example"
        await logging_client.post("/auth/register", json={"email": email, "password": PASSWORD})

        token = await request_reset_token(logging_client, reset_delivery, email)
        await logging_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": "a-replacement-password-value"},
        )

        output = log_sink.getvalue()

        assert token not in output
        assert "a-replacement-password-value" not in output

    async def test_reset_is_observable_without_the_credential(
        self,
        logging_client: AsyncClient,
        log_sink: io.StringIO,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """NFR-OBS-004 — a reset must be investigable after the fact.

        The row's primary key is logged, which ties the issued link to the completed
        reset without recording anything that could be presented to the endpoint.
        """
        email = "resettrace@docura.example"
        await logging_client.post("/auth/register", json={"email": email, "password": PASSWORD})
        token = await request_reset_token(logging_client, reset_delivery, email)
        await logging_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": "another-replacement-password"},
        )

        events = [
            json.loads(line) for line in log_sink.getvalue().splitlines() if line.startswith("{")
        ]
        issued = next(e for e in events if e["event"] == "auth.password_reset_issued")
        completed = next(e for e in events if e["event"] == "auth.password_reset_completed")

        assert issued["reset_ref"] not in ("", "***REDACTED***")
        assert issued["reset_ref"] == completed["reset_ref"]
