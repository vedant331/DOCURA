"""Error handling.

Each test names the requirement it holds: NFR-ERR-001 (say what to do next),
NFR-ERR-004 (leak nothing internal), NFR-ERR-002 (fail towards inaction).
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic import BaseModel

from app.core.config import Settings
from app.core.errors import PROBLEM_CONTENT_TYPE, DatabaseUnavailableError, DocuraError
from app.main import create_app
from tests.conftest import StubEngine

SECRET_MARKER = "s3cr3t-internal-token"


class _Payload(BaseModel):
    name: str
    count: int


@pytest.fixture
def failing_app(settings: Settings) -> FastAPI:
    """An app with routes that raise, so real handlers are exercised end to end."""
    app = create_app(settings)
    app.state.engine = StubEngine()

    @app.get("/boom/unhandled")
    async def _unhandled() -> None:
        raise RuntimeError(f"internal failure at 0xdeadbeef with {SECRET_MARKER}")

    @app.get("/boom/dependency")
    async def _dependency() -> None:
        raise DatabaseUnavailableError

    @app.post("/boom/validate")
    async def _validate(payload: _Payload) -> dict[str, str]:
        return {"name": payload.name}

    return app


@pytest.fixture
async def failing_client(failing_app: FastAPI) -> AsyncIterator[AsyncClient]:
    transport = ASGITransport(app=failing_app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://testserver") as http_client:
        yield http_client


class TestProblemDocumentShape:
    async def test_not_found_is_a_problem_document(self, client: AsyncClient) -> None:
        response = await client.get("/does-not-exist")

        assert response.status_code == 404
        assert response.headers["content-type"].startswith(PROBLEM_CONTENT_TYPE)
        body = response.json()
        assert set(body) >= {"type", "title", "status", "detail", "remediation"}

    async def test_every_error_says_what_to_do_next(self, client: AsyncClient) -> None:
        """NFR-ERR-001 — a message that only restates failure is not acceptable."""
        body = (await client.get("/does-not-exist")).json()

        assert body["remediation"]
        assert len(body["remediation"]) > 10

    async def test_method_not_allowed(self, client: AsyncClient) -> None:
        response = await client.post("/health")

        assert response.status_code == 405
        assert response.json()["remediation"]

    async def test_request_id_is_included(self, client: AsyncClient) -> None:
        body = (await client.get("/does-not-exist")).json()

        assert body["request_id"]


class TestUnhandledExceptions:
    async def test_returns_a_generic_500(self, failing_client: AsyncClient) -> None:
        response = await failing_client.get("/boom/unhandled")

        assert response.status_code == 500
        assert response.json()["title"] == "Internal server error"

    async def test_leaks_no_internal_detail(self, failing_client: AsyncClient) -> None:
        """NFR-ERR-004 — no stack trace, identifier, or infrastructure detail."""
        body = (await failing_client.get("/boom/unhandled")).text

        assert SECRET_MARKER not in body
        assert "0xdeadbeef" not in body
        assert "RuntimeError" not in body
        assert "Traceback" not in body
        assert "app/main.py" not in body

    async def test_still_carries_a_request_id_for_correlation(
        self, failing_client: AsyncClient
    ) -> None:
        """The client gets nothing internal, so the ID is how support finds the log."""
        body = (await failing_client.get("/boom/unhandled")).json()

        assert body["request_id"]


class TestDependencyFailures:
    async def test_dependency_failure_is_503(self, failing_client: AsyncClient) -> None:
        response = await failing_client.get("/boom/dependency")

        assert response.status_code == 503

    async def test_states_that_nothing_changed(self, failing_client: AsyncClient) -> None:
        """NFR-ERR-002 — DOCURA fails towards inaction, and says so."""
        body = (await failing_client.get("/boom/dependency")).json()

        assert "No data was read or written" in body["remediation"]

    async def test_does_not_name_the_database_host(self, failing_client: AsyncClient) -> None:
        body = (await failing_client.get("/boom/dependency")).text

        assert "localhost" not in body
        assert "5432" not in body


class TestValidationErrors:
    async def test_invalid_body_is_422(self, failing_client: AsyncClient) -> None:
        response = await failing_client.post("/boom/validate", json={"name": 5})

        assert response.status_code == 422
        assert response.json()["title"] == "Invalid request"

    async def test_lists_the_offending_fields(self, failing_client: AsyncClient) -> None:
        body = (await failing_client.post("/boom/validate", json={})).json()

        fields = {error["field"] for error in body["errors"]}
        assert {"name", "count"} <= fields

    async def test_does_not_echo_submitted_input(self, failing_client: AsyncClient) -> None:
        """Echoing input reflects attacker content and, on a credential field, the credential."""
        response = await failing_client.post(
            "/boom/validate",
            json={"name": SECRET_MARKER, "count": "<script>alert(1)</script>"},
        )

        assert SECRET_MARKER not in response.text
        assert "<script>" not in response.text


class TestBodySizeLimit:
    async def test_oversized_body_is_rejected(
        self, failing_app: FastAPI, settings: Settings
    ) -> None:
        transport = ASGITransport(app=failing_app, raise_app_exceptions=False)
        oversized = "x" * (settings.max_request_bytes + 1)

        async with AsyncClient(transport=transport, base_url="http://testserver") as http:
            response = await http.post("/boom/validate", content=oversized)

        assert response.status_code == 413
        assert response.json()["remediation"]


class TestErrorClasses:
    def test_custom_detail_overrides_the_default(self) -> None:
        error = DocuraError("a specific failure", remediation="do this instead")

        assert error.detail == "a specific failure"
        assert error.remediation == "do this instead"

    def test_defaults_are_populated(self) -> None:
        error = DatabaseUnavailableError()

        assert error.status_code == 503
        assert error.detail
        assert error.remediation
