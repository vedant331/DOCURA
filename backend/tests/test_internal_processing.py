"""The serverless processing trigger: POST /internal/process.

The hermetic tests replace the queue-draining unit (:func:`process_one`) with a fake so
authentication, bounding, and dependency wiring are exercised without a database. One
integration test then drives the *real* pipeline end to end to prove the trigger runs
the same claim/execute path — and that the upload route stayed asynchronous.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Environment, Settings
from app.main import create_app
from tests.conftest import (
    INTEGRATION_DSN,
    PNG_BYTES,
    TEST_DSN,
    auth_header,
    register_and_login,
    requires_postgres,
    upload_document,
)

SECRET = "trigger-secret-value"
SECRET_HEADER = "X-Internal-Secret"


def _make_app(secret: str | None) -> FastAPI:
    """A real app (real middleware/routes) with a stub session_factory for the endpoint."""
    settings = Settings(
        environment=Environment.TEST,
        database_url=TEST_DSN,
        worker_trigger_secret=secret,
    )
    app = create_app(settings)
    # The endpoint reads these off app.state; create_app sets the storage/extractor/
    # classifier/field_extractor seams, and the fake process_one ignores the factory.
    app.state.session_factory = object()
    return app


async def _client(app: FastAPI) -> AsyncClient:
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    return AsyncClient(transport=transport, base_url="http://testserver")


class _FakeProcessOne:
    """Records each call and returns True for the first ``successes`` invocations."""

    def __init__(self, successes: int) -> None:
        self.calls: list[dict[str, Any]] = []
        self._successes = successes

    async def __call__(self, session_factory: Any, **kwargs: Any) -> bool:
        self.calls.append({"session_factory": session_factory, **kwargs})
        return len(self.calls) <= self._successes


@pytest.fixture
def _no_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """Skip the real pending-count DB query in hermetic tests."""

    async def _zero(_request: Any) -> int:
        return 0

    monkeypatch.setattr("app.api.internal._count_pending", _zero)


# -- Authentication (fails closed) -----------------------------------------------------


async def test_unconfigured_secret_fails_closed() -> None:
    app = _make_app(secret=None)
    async with await _client(app) as client:
        response = await client.post("/internal/process", headers={SECRET_HEADER: "anything"})
    assert response.status_code == 503


async def test_missing_header_is_rejected() -> None:
    app = _make_app(secret=SECRET)
    async with await _client(app) as client:
        response = await client.post("/internal/process")
    assert response.status_code == 401


async def test_wrong_secret_is_rejected() -> None:
    app = _make_app(secret=SECRET)
    async with await _client(app) as client:
        response = await client.post("/internal/process", headers={SECRET_HEADER: "wrong"})
    assert response.status_code == 401


@pytest.mark.usefixtures("_no_count")
async def test_valid_secret_is_accepted(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("app.api.internal.process_one", _FakeProcessOne(successes=0))
    app = _make_app(secret=SECRET)
    async with await _client(app) as client:
        response = await client.post("/internal/process", headers={SECRET_HEADER: SECRET})
    assert response.status_code == 200
    assert response.json() == {"processed": 0, "remaining": 0, "budget_exhausted": False}


# -- Bounded processing ----------------------------------------------------------------


@pytest.mark.usefixtures("_no_count")
async def test_stops_when_queue_empties(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeProcessOne(successes=3)  # three jobs available, then empty
    monkeypatch.setattr("app.api.internal.process_one", fake)
    app = _make_app(secret=SECRET)
    async with await _client(app) as client:
        response = await client.post("/internal/process", headers={SECRET_HEADER: SECRET})
    body = response.json()
    assert body["processed"] == 3
    assert body["budget_exhausted"] is False
    assert len(fake.calls) == 4  # three successes + one empty poll that ends the loop


@pytest.mark.usefixtures("_no_count")
async def test_respects_max_jobs_ceiling(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = _FakeProcessOne(successes=10_000)  # always work available
    monkeypatch.setattr("app.api.internal.process_one", fake)
    app = _make_app(secret=SECRET)
    async with await _client(app) as client:
        response = await client.post(
            "/internal/process", headers={SECRET_HEADER: SECRET}, params={"max_jobs": 5}
        )
    body = response.json()
    assert body["processed"] == 5
    assert body["budget_exhausted"] is True
    assert len(fake.calls) == 5


# -- process_one dependency wiring -----------------------------------------------------


@pytest.mark.usefixtures("_no_count")
async def test_process_one_receives_app_state_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = _FakeProcessOne(successes=1)
    monkeypatch.setattr("app.api.internal.process_one", fake)
    app = _make_app(secret=SECRET)
    async with await _client(app) as client:
        await client.post("/internal/process", headers={SECRET_HEADER: SECRET})

    assert fake.calls, "process_one was never called"
    call = fake.calls[0]
    assert call["session_factory"] is app.state.session_factory
    assert call["storage"] is app.state.document_storage
    assert call["extractor"] is app.state.document_extractor
    assert call["classifier"] is app.state.document_classifier
    assert call["field_extractor"] is app.state.document_field_extractor
    assert call["settings"] is app.state.settings


# -- The upload path is untouched ------------------------------------------------------


def test_upload_path_does_not_process_inline() -> None:
    """POST /documents must stay asynchronous: the request path never runs the worker."""
    import app.api.documents as documents_module
    import app.services.document_service as document_service_module

    assert "process_one" not in inspect.getsource(documents_module)
    assert "process_one" not in inspect.getsource(document_service_module)


# -- End to end against a real database (skips without TEST_DATABASE_URL) ---------------


@requires_postgres
async def test_trigger_drains_real_queue_and_upload_is_async(
    db_engine: Any, tmp_path: Path
) -> None:
    from app.db.session import create_session_factory

    assert INTEGRATION_DSN is not None
    settings = Settings(
        environment=Environment.TEST,
        database_url=INTEGRATION_DSN,
        worker_trigger_secret=SECRET,
        document_storage_root=tmp_path / "documents",
    )
    app = create_app(settings)
    app.state.engine = db_engine
    app.state.session_factory = create_session_factory(db_engine)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        token, _ = await register_and_login(client, "trigger-e2e@example.test")
        document = await upload_document(
            client, token, content=PNG_BYTES, filename="scan.png", content_type="image/png"
        )

        # Upload is asynchronous: nothing processed it in the request path.
        before = await client.get(f"/documents/{document['id']}", headers=auth_header(token))
        assert before.json()["status"] == "queued"

        # The trigger runs the real process_one/_execute/retry path. With the production
        # unconfigured extractor, the job exhausts its attempts and the document fails
        # honestly (the success path is unreachable until S-6 selects an engine).
        triggered = await client.post("/internal/process", headers={SECRET_HEADER: SECRET})
        assert triggered.status_code == 200, triggered.text
        summary = triggered.json()
        assert summary["processed"] == settings.worker_max_attempts
        assert summary["remaining"] == 0

        after = await client.get(f"/documents/{document['id']}", headers=auth_header(token))
        assert after.json()["status"] == "failed"
