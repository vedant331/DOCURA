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
from fastapi import FastAPI
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


# --------------------------------------------------------------------------
# Sprint 2: fixtures backed by a real database.
#
# The ORM uses PostgreSQL's native UUID type, so these cannot run against a
# stand-in. They skip — never silently pass — when TEST_DATABASE_URL is unset, so a
# green run without Postgres cannot be mistaken for verified authentication.
# --------------------------------------------------------------------------

INTEGRATION_DSN = os.environ.get("TEST_DATABASE_URL")

requires_postgres = pytest.mark.skipif(
    not INTEGRATION_DSN,
    reason="Set TEST_DATABASE_URL to run database-backed tests.",
)

PASSWORD = "correct-horse-battery-staple"
OTHER_PASSWORD = "a-different-sufficiently-long-password"


@pytest.fixture
def db_settings(tmp_path: Path) -> Settings:
    """Settings pointed at the test database, with a fast idle timeout.

    ``document_storage_root`` is a per-test temporary directory. Nothing in the
    suite may write to a developer's real vault, and a test that asserts a file was
    removed must not be able to remove someone's actual document.
    """
    assert INTEGRATION_DSN is not None
    return Settings(
        environment=Environment.TEST,
        database_url=INTEGRATION_DSN,
        session_idle_timeout_minutes=60,
        session_absolute_timeout_hours=24,
        document_storage_root=tmp_path / "documents",
    )


@pytest.fixture
async def db_engine(db_settings: Settings) -> AsyncIterator[Any]:
    """Engine with the Sprint 2 schema present and every table emptied.

    Built per test and disposed after: pytest-asyncio runs each test in its own
    event loop, and an asyncpg connection belongs to the loop that opened it, so a
    cached engine hands the next test connections tied to a closed loop.

    Tables come from the model metadata rather than from Alembic, so a broken
    migration cannot let the suite silently test nothing. The migration itself is
    exercised separately in ``test_migrations.py``.
    """
    from sqlalchemy import text

    from app.db.models import Base
    from app.db.session import create_engine

    engine = create_engine(db_settings)
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)
        await connection.execute(
            text(
                "TRUNCATE TABLE documents, password_reset_tokens, sessions, users "
                "RESTART IDENTITY CASCADE"
            )
        )

    try:
        yield engine
    finally:
        await engine.dispose()


class RecordingResetDelivery:
    """Stands in for the out-of-band channel, capturing what it was asked to send.

    A password-reset token is never returned by the API — only the account's
    verified address receives it — so a test that needs one must take it from the
    delivery channel, exactly as a mailbox would.
    """

    def __init__(self) -> None:
        self.sent: list[tuple[str, str]] = []

    async def send(self, *, email: str, token: str) -> None:
        self.sent.append((email, token))

    def latest_token_for(self, email: str) -> str:
        for sent_email, token in reversed(self.sent):
            if sent_email == email:
                return token
        raise AssertionError(f"no reset token was delivered to {email}")


@pytest.fixture
def reset_delivery() -> RecordingResetDelivery:
    return RecordingResetDelivery()


@pytest.fixture
async def auth_app(
    db_settings: Settings, db_engine: Any, reset_delivery: RecordingResetDelivery
) -> AsyncIterator[FastAPI]:
    """The application itself, wired to the real database.

    Split out from ``auth_client`` so a test can reach ``app.state`` — which is how
    a substitute storage backend or delivery channel is installed, and the only
    honest way to test what the application does when a dependency fails.
    """
    from app.api.auth import reset_rate_limiter
    from app.db.session import create_session_factory
    from app.main import create_app

    reset_rate_limiter()

    app = create_app(db_settings)
    app.state.engine = db_engine
    app.state.session_factory = create_session_factory(db_engine)
    app.state.reset_delivery = reset_delivery

    yield app

    reset_rate_limiter()


@pytest.fixture
async def auth_client(auth_app: FastAPI) -> AsyncIterator[AsyncClient]:
    """A client wired to the real database, through the real middleware stack."""
    transport = ASGITransport(app=auth_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client


async def register_and_login(
    client: AsyncClient, email: str, password: str = PASSWORD
) -> tuple[str, dict[str, Any]]:
    """Create an account and sign in. Returns the token and the user body."""
    registered = await client.post("/auth/register", json={"email": email, "password": password})
    assert registered.status_code == 201, registered.text

    logged_in = await client.post("/auth/login", json={"email": email, "password": password})
    assert logged_in.status_code == 200, logged_in.text
    body = logged_in.json()
    return body["access_token"], body["user"]


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


async def request_reset_token(
    client: AsyncClient, delivery: RecordingResetDelivery, email: str
) -> str:
    """Run the request half of the reset flow and read the token off the channel."""
    response = await client.post("/auth/password-reset/request", json={"email": email})
    assert response.status_code == 202, response.text
    return delivery.latest_token_for(email)


# --------------------------------------------------------------------------
# Sprint 3: document vault fixtures.
#
# The sample files are real enough to pass validation — each carries the leading
# bytes its format is identified by — and small enough to be built inline. A test
# that needs a *rejected* file builds one that deliberately does not.
# --------------------------------------------------------------------------

# %PDF-1.7 header, one object, and a trailer. Not a rich document; it is a file
# whose type is unambiguous, which is what the vault checks.
PDF_BYTES = b"%PDF-1.7\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF\n"
# SOI, an APP0/JFIF segment, and EOI.
JPEG_BYTES = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + b"\xff\xd9"
# The 8-byte PNG signature followed by a minimal IHDR chunk.
PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00"
    b"\x1f\x15\xc4\x89"
)


def pdf_bytes(marker: bytes = b"") -> bytes:
    """A distinct PDF. The marker changes the checksum, so two calls are not duplicates."""
    return PDF_BYTES + b"% " + marker + b"\n" if marker else PDF_BYTES


def upload_file(
    content: bytes, filename: str = "marksheet.pdf", content_type: str = "application/pdf"
) -> dict[str, Any]:
    """A single-file multipart payload in the shape httpx expects."""
    return {"files": (filename, content, content_type)}


async def upload_document(
    client: AsyncClient,
    token: str,
    *,
    content: bytes = PDF_BYTES,
    filename: str = "marksheet.pdf",
    content_type: str = "application/pdf",
) -> dict[str, Any]:
    """Upload one file and return the accepted document's metadata."""
    response = await client.post(
        "/documents",
        headers=auth_header(token),
        files=upload_file(content, filename, content_type),
    )
    assert response.status_code == 201, response.text
    accepted = response.json()["accepted"]
    assert len(accepted) == 1, response.text
    document: dict[str, Any] = accepted[0]
    return document
