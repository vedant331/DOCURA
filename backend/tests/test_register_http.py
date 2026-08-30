"""Registration over a real socket, not an in-process ASGI transport.

Every other suite drives the app through ``httpx.ASGITransport``. That exercises
the real routing, middleware, and handlers, but it hands the app a Python object
rather than bytes off a TCP connection — so it could not distinguish "the endpoint
is broken" from "the client never sent what you thought it sent".

That distinction cost real debugging time: a 422 with ``{"field": "1", "reason":
"JSON decode error"}`` was read as a backend defect when the body on the wire was
``{email:...}``, Windows PowerShell 5.1 having stripped the double quotes out of
the argument before ``curl.exe`` ever saw it. These tests pin both halves down —
what a correct request does, and what that specific malformed body does — so the
next person sees immediately which side is at fault.
"""

from __future__ import annotations

import asyncio
import socket
from collections.abc import AsyncIterator
from typing import Any

import pytest
import uvicorn
from httpx import AsyncClient

from app.core.config import Settings
from tests.conftest import PASSWORD, RecordingResetDelivery, requires_postgres

pytestmark = requires_postgres

_STARTUP_TIMEOUT_SECONDS = 10.0

# Byte-for-byte what PowerShell 5.1 passes to curl.exe when the JSON is written
# inline: the quotes are gone, so this is no longer JSON. Kept as an explicit
# literal — the point of the test is the exact bytes, not a construction of them.
POWERSHELL_MANGLED_BODY = b"{email:smoke2@docura.example,password:a-sufficiently-long-password}"

VALID_BODY = b'{"email":"smoke2@docura.example","password":"a-sufficiently-long-password"}'
JSON_HEADERS = {"Content-Type": "application/json"}


@pytest.fixture
async def live_server(
    db_settings: Settings,
    db_engine: Any,
    reset_delivery: RecordingResetDelivery,
) -> AsyncIterator[str]:
    """A uvicorn server on an ephemeral port, serving the real application.

    Lifespan is off and the engine injected, matching ``auth_client``: startup
    connectivity has its own coverage in ``test_startup.py``, and the fixture's
    per-test engine must be the one the requests use — a second engine built by the
    lifespan would belong to the same loop but not to the schema this test prepared.
    """
    from app.api.auth import reset_rate_limiter
    from app.db.session import create_session_factory
    from app.main import create_app

    reset_rate_limiter()

    app = create_app(db_settings)
    app.state.engine = db_engine
    app.state.session_factory = create_session_factory(db_engine)
    app.state.reset_delivery = reset_delivery

    # Port 0 lets the OS pick a free port, so a developer already running the
    # service on 8001 does not collide with the suite.
    bound = socket.socket()
    bound.bind(("127.0.0.1", 0))
    port = bound.getsockname()[1]

    server = uvicorn.Server(uvicorn.Config(app, log_config=None, access_log=False, lifespan="off"))
    serving = asyncio.create_task(server.serve(sockets=[bound]))

    loop = asyncio.get_running_loop()
    deadline = loop.time() + _STARTUP_TIMEOUT_SECONDS
    while not server.started:
        if serving.done() or loop.time() > deadline:
            server.should_exit = True
            await serving
            pytest.fail("the test server did not start")
        await asyncio.sleep(0.01)

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        await serving
        bound.close()
        reset_rate_limiter()


@pytest.fixture
async def http_client(live_server: str) -> AsyncIterator[AsyncClient]:
    """A client that opens a genuine TCP connection to the running server."""
    async with AsyncClient(base_url=live_server, timeout=10.0) as client:
        yield client


class TestRegistrationOverRealHttp:
    async def test_valid_json_registers_the_account(self, http_client: AsyncClient) -> None:
        """S2-T027 — the endpoint works when the bytes on the wire are actually JSON."""
        response = await http_client.post(
            "/auth/register", content=VALID_BODY, headers=JSON_HEADERS
        )

        assert response.status_code == 201, response.text
        assert response.json()["email"] == "smoke2@docura.example"

    async def test_duplicate_registration_conflicts(self, http_client: AsyncClient) -> None:
        """S2-T028 — uniqueness holds across two real connections, not one process call."""
        first = await http_client.post("/auth/register", content=VALID_BODY, headers=JSON_HEADERS)
        second = await http_client.post("/auth/register", content=VALID_BODY, headers=JSON_HEADERS)

        assert first.status_code == 201
        assert second.status_code == 409

    async def test_login_and_protected_route(self, http_client: AsyncClient) -> None:
        """S2-T029 — register, sign in, and use the token, all over the socket."""
        await http_client.post("/auth/register", content=VALID_BODY, headers=JSON_HEADERS)

        login = await http_client.post(
            "/auth/login",
            json={"email": "smoke2@docura.example", "password": "a-sufficiently-long-password"},
        )
        assert login.status_code == 200
        token = login.json()["access_token"]

        with_token = await http_client.get(
            "/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        without_token = await http_client.get("/users/me")

        assert with_token.status_code == 200
        assert with_token.json()["email"] == "smoke2@docura.example"
        assert without_token.status_code == 401


class TestMalformedBodyIsReportedHonestly:
    """These lock in a *correct* rejection, so it is not later "fixed" by loosening.

    Accepting unquoted keys would mean parsing something that is not JSON on the
    endpoint that creates accounts. The 422 is the right answer; what was missing
    was a way to see that the client, not the server, was at fault.
    """

    async def test_body_with_stripped_quotes_is_rejected(self, http_client: AsyncClient) -> None:
        """S2-T030 — the exact bytes PowerShell 5.1 sends, and the exact 422 seen."""
        response = await http_client.post(
            "/auth/register", content=POWERSHELL_MANGLED_BODY, headers=JSON_HEADERS
        )

        assert response.status_code == 422
        body = response.json()
        assert body["errors"] == [{"field": "1", "reason": "JSON decode error"}]

    async def test_no_account_is_created_by_a_malformed_body(
        self, http_client: AsyncClient
    ) -> None:
        """NFR-ERR-002 — failure means inaction, not a partially applied request."""
        await http_client.post(
            "/auth/register", content=POWERSHELL_MANGLED_BODY, headers=JSON_HEADERS
        )

        login = await http_client.post(
            "/auth/login",
            json={"email": "smoke2@docura.example", "password": "a-sufficiently-long-password"},
        )

        assert login.status_code == 401

    async def test_rejection_names_the_remedy_without_echoing_the_body(
        self, http_client: AsyncClient
    ) -> None:
        """NFR-ERR-001 and NFR-ERR-004 — say what to do; reflect nothing back."""
        response = await http_client.post(
            "/auth/register",
            content=b'{"email":"echo@docura.example","password":"' + PASSWORD.encode() + b'"',
            headers=JSON_HEADERS,
        )

        body = response.json()
        assert response.status_code == 422
        assert body["remediation"]
        assert PASSWORD not in response.text

    async def test_json_body_requires_the_json_content_type(self, http_client: AsyncClient) -> None:
        """A JSON API should not read a body a browser could post cross-origin.

        Without the declared type the request is a CORS "simple request"; requiring
        ``application/json`` keeps this endpoint out of that category.
        """
        response = await http_client.post(
            "/auth/register", content=VALID_BODY, headers={"Content-Type": "text/plain"}
        )

        assert response.status_code == 422
