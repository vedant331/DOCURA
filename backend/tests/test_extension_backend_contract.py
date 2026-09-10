"""M2 — the backend contract the browser extension depends on.

The extension adds no backend endpoints: it reuses the existing account/session system
and the M1 form-session API. These tests pin the exact sequence it drives — sign in
(account sharing), activate, stop — and the guarantees it relies on: ownership
isolation, that activity cannot continue after stop, that the audit trail is written by
backend-owned logic and holds no page content, and that there is no endpoint a client
could use to forge history.

Needs a real PostgreSQL (native UUID); skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

from fastapi import FastAPI
from httpx import AsyncClient

from tests.conftest import auth_header, register_and_login, requires_postgres

pytestmark = requires_postgres


class TestAccountSharing:
    async def test_extension_signin_shares_the_existing_account(
        self, auth_client: AsyncClient
    ) -> None:
        # The extension signs in through the same /auth/login every client uses; the
        # token then names the same account at /users/me — no second user system.
        token, user = await register_and_login(auth_client, "a@example.com")
        me = await auth_client.get("/users/me", headers=auth_header(token))
        assert me.status_code == 200, me.text
        assert me.json()["id"] == user["id"]

    async def test_an_invalid_token_can_do_nothing(self, auth_client: AsyncClient) -> None:
        # A stale/invalid token is rejected, so the extension "does nothing" by design.
        bad = await auth_client.post("/form-sessions", headers=auth_header("not-a-real-token"))
        assert bad.status_code == 401, bad.text


class TestActivationLifecycle:
    async def test_activation_creates_a_session_owned_by_the_user(
        self, auth_client: AsyncClient
    ) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        activated = await auth_client.post("/form-sessions", headers=auth_header(token))
        assert activated.status_code == 201, activated.text
        session_id = activated.json()["id"]
        assert activated.json()["state"] == "active"

        owned = await auth_client.get(f"/form-sessions/{session_id}", headers=auth_header(token))
        assert owned.status_code == 200

    async def test_stop_ends_the_session_and_records_a_clean_audit_entry(
        self, auth_client: AsyncClient
    ) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        session_id = (
            await auth_client.post("/form-sessions", headers=auth_header(token))
        ).json()["id"]

        stopped = await auth_client.post(
            f"/form-sessions/{session_id}/stop", headers=auth_header(token)
        )
        assert stopped.status_code == 200, stopped.text
        assert stopped.json()["state"] == "stopped"

        history = await auth_client.get(
            f"/form-sessions/{session_id}/actions", headers=auth_header(token)
        )
        actions = history.json()["actions"]
        # Backend-owned logic wrote the stop; it carries no page content.
        assert [a["action_type"] for a in actions] == ["stop"]
        assert actions[0]["field_ref"] is None
        assert actions[0]["detail"] is None
        assert "%PDF" not in history.text
        assert "storage_key" not in history.text

    async def test_activity_cannot_continue_after_stop(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        session_id = (
            await auth_client.post("/form-sessions", headers=auth_header(token))
        ).json()["id"]
        await auth_client.post(f"/form-sessions/{session_id}/stop", headers=auth_header(token))

        # A stopped session accepts no further lifecycle action (BR-016).
        again = await auth_client.post(
            f"/form-sessions/{session_id}/stop", headers=auth_header(token)
        )
        assert again.status_code == 409, again.text


class TestIsolationAndForgery:
    async def test_another_user_cannot_control_or_read_the_session(
        self, auth_client: AsyncClient
    ) -> None:
        token_a, _a = await register_and_login(auth_client, "a@example.com")
        session_id = (
            await auth_client.post("/form-sessions", headers=auth_header(token_a))
        ).json()["id"]

        token_b, _b = await register_and_login(auth_client, "b@example.com")
        assert (
            await auth_client.get(f"/form-sessions/{session_id}", headers=auth_header(token_b))
        ).status_code == 404
        assert (
            await auth_client.post(
                f"/form-sessions/{session_id}/stop", headers=auth_header(token_b)
            )
        ).status_code == 404
        assert (
            await auth_client.get(
                f"/form-sessions/{session_id}/actions", headers=auth_header(token_b)
            )
        ).status_code == 404

    def test_no_endpoint_lets_a_client_forge_history(self, auth_app: FastAPI) -> None:
        """The only writes to a session are activate, stop, and hand-back.

        There is deliberately no route to append an arbitrary FormAction — history is
        written by DOCURA's own logic, never posted by a client. The audit *reader*
        (``GET /form-sessions/{id}/actions``) is read-only.
        """
        paths = auth_app.openapi()["paths"]
        writing = {"post", "put", "patch", "delete"}
        form_writes = {
            (path, method)
            for path, operations in paths.items()
            if path.startswith("/form-sessions")
            for method in operations
            if method in writing
        }
        assert form_writes == {
            ("/form-sessions", "post"),
            ("/form-sessions/{session_id}/hand-back", "post"),
            ("/form-sessions/{session_id}/stop", "post"),
        }
        # The history route exists only as a read.
        actions = paths["/form-sessions/{session_id}/actions"]
        assert set(actions) == {"get"}
