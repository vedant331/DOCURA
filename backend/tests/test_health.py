"""Health and readiness endpoints."""

from __future__ import annotations

from typing import Any

import pytest
from httpx import AsyncClient

from app.core.config import Settings
from tests.conftest import TEST_DSN


class TestLiveness:
    async def test_returns_ok(self, client: AsyncClient, settings: Settings) -> None:
        response = await client.get("/health")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["service"] == settings.service_name
        assert body["version"] == settings.version
        assert body["environment"] == "test"

    async def test_succeeds_while_the_database_is_down(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Liveness must not depend on Postgres.

        If it did, a database blip would make an orchestrator restart a perfectly
        healthy process, turning a recoverable outage into a crash loop.
        """

        async def _unhealthy(_engine: Any) -> bool:
            return False

        monkeypatch.setattr("app.api.health.check_health", _unhealthy)

        assert (await client.get("/health")).status_code == 200

    async def test_carries_a_request_id(self, client: AsyncClient) -> None:
        response = await client.get("/health")

        assert response.headers["X-Request-ID"]

    async def test_echoes_a_supplied_request_id(self, client: AsyncClient) -> None:
        response = await client.get("/health", headers={"X-Request-ID": "trace-abc-123"})

        assert response.headers["X-Request-ID"] == "trace-abc-123"

    async def test_rejects_a_malformed_request_id(self, client: AsyncClient) -> None:
        """An unbounded client string reaches logs and responses — it is not trusted."""
        response = await client.get("/health", headers={"X-Request-ID": "bad id\nwith injection"})

        assert response.headers["X-Request-ID"] != "bad id\nwith injection"


class TestReadiness:
    async def test_ready_when_the_database_answers(self, client: AsyncClient) -> None:
        response = await client.get("/health/ready")

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ready"
        assert body["checks"]["database"] == "ok"

    async def test_not_ready_when_the_database_fails(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        async def _unhealthy(_engine: Any) -> bool:
            return False

        monkeypatch.setattr("app.api.health.check_health", _unhealthy)

        response = await client.get("/health/ready")

        assert response.status_code == 503
        body = response.json()
        assert body["status"] == "not_ready"
        assert body["checks"]["database"] == "unavailable"

    async def test_names_the_failing_dependency(
        self, client: AsyncClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """A probe that returns only a status code makes an outage slower to diagnose."""

        async def _unhealthy(_engine: Any) -> bool:
            return False

        monkeypatch.setattr("app.api.health.check_health", _unhealthy)

        body = (await client.get("/health/ready")).json()

        assert "database" in body["checks"]


class TestSecurityHeaders:
    @pytest.mark.parametrize(
        ("header", "expected"),
        [
            ("X-Content-Type-Options", "nosniff"),
            ("X-Frame-Options", "DENY"),
            ("Referrer-Policy", "no-referrer"),
            ("Cache-Control", "no-store"),
        ],
    )
    async def test_headers_present(self, client: AsyncClient, header: str, expected: str) -> None:
        response = await client.get("/health")

        assert response.headers[header] == expected

    async def test_content_security_policy_locks_everything_down(self, client: AsyncClient) -> None:
        csp = (await client.get("/health")).headers["Content-Security-Policy"]

        assert "default-src 'none'" in csp
        assert "frame-ancestors 'none'" in csp

    async def test_docs_csp_is_not_relaxed_outside_local(self, client: AsyncClient) -> None:
        """The Swagger CDN allowance is local-only; in every other env /docs stays locked.

        The ``client`` fixture runs in the TEST environment, where /docs is served but
        must still carry the strict policy — the CDN is never allowed here or in prod.
        """
        csp = (await client.get("/docs")).headers["Content-Security-Policy"]

        assert csp.startswith("default-src 'none'")
        assert "cdn.jsdelivr.net" not in csp

    async def test_local_docs_csp_allows_only_swagger_assets(self) -> None:
        """In local development, /docs may load Swagger UI's CDN + inline init script.

        Nothing else is relaxed: a non-docs path in the very same app stays locked
        down, so the allowance is scoped to the docs pages, not the environment.
        """
        from httpx import ASGITransport

        from app.core.config import Environment
        from app.main import create_app

        app = create_app(Settings(environment=Environment.LOCAL, database_url=TEST_DSN))
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://testserver") as local:
            docs_csp = (await local.get("/docs")).headers["Content-Security-Policy"]
            other_csp = (await local.get("/openapi.json")).headers["Content-Security-Policy"]

        # /docs: Swagger's CDN and inline script are permitted, base policy still 'none'.
        assert "default-src 'none'" in docs_csp
        assert "https://cdn.jsdelivr.net" in docs_csp
        assert "'unsafe-inline'" in docs_csp
        assert "connect-src 'self'" in docs_csp
        # A non-docs response in the same local app keeps the strict lockdown.
        assert other_csp.startswith("default-src 'none'")
        assert "cdn.jsdelivr.net" not in other_csp

    async def test_no_hsts_outside_production(self, client: AsyncClient) -> None:
        """HSTS on a plain-HTTP local service would pin a scheme that is not served."""
        response = await client.get("/health")

        assert "Strict-Transport-Security" not in response.headers


class TestResponseHygiene:
    async def test_no_credentials_in_any_health_response(self, client: AsyncClient) -> None:
        for path in ("/health", "/health/ready"):
            body = (await client.get(path)).text
            assert "test_password" not in body
            assert "test_user" not in body
            assert "postgresql" not in body

    async def test_no_server_version_banner(self, client: AsyncClient) -> None:
        response = await client.get("/health")

        assert "uvicorn" not in response.headers.get("server", "").lower()
