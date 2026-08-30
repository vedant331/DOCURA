"""Sprint 2 — registration, login, sessions, and isolation.

Test IDs from the sprint brief are cited on each test so the exit checklist can be
read off the results.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_session_token, verify_password
from app.db.models import Session, User
from tests.conftest import (
    OTHER_PASSWORD,
    PASSWORD,
    auth_header,
    register_and_login,
    requires_postgres,
)

pytestmark = requires_postgres


async def _fetch_user(engine: Any, email: str) -> User:
    async with AsyncSession(engine) as db:
        user = await db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


class TestRegistration:
    async def test_valid_registration_succeeds(self, auth_client: AsyncClient) -> None:
        """S2-T001."""
        response = await auth_client.post(
            "/auth/register", json={"email": "ada@docura.example", "password": PASSWORD}
        )

        assert response.status_code == 201
        body = response.json()
        assert body["email"] == "ada@docura.example"
        assert body["is_active"] is True
        assert body["id"]

    async def test_password_is_stored_hashed(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        """S2-T002 — the stored value must be an Argon2id hash, not the password."""
        await auth_client.post(
            "/auth/register", json={"email": "hash@docura.example", "password": PASSWORD}
        )

        user = await _fetch_user(db_engine, "hash@docura.example")

        assert PASSWORD not in user.password_hash
        assert user.password_hash.startswith("$argon2id$")
        assert verify_password(PASSWORD, user.password_hash)

    async def test_plaintext_password_appears_nowhere_in_the_database(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        """S2-T002 — scan every text column, not just the one we expect."""
        await auth_client.post(
            "/auth/register", json={"email": "scan@docura.example", "password": PASSWORD}
        )

        async with AsyncSession(db_engine) as db:
            rows = await db.execute(text("SELECT * FROM users"))
            dumped = str(rows.mappings().all())

        assert PASSWORD not in dumped

    async def test_duplicate_registration_is_rejected(self, auth_client: AsyncClient) -> None:
        """S2-T003."""
        payload = {"email": "dupe@docura.example", "password": PASSWORD}
        assert (await auth_client.post("/auth/register", json=payload)).status_code == 201

        second = await auth_client.post("/auth/register", json=payload)

        assert second.status_code == 409
        assert second.json()["remediation"]

    async def test_duplicate_is_detected_case_insensitively(self, auth_client: AsyncClient) -> None:
        """Uniqueness must not be defeated by capitalisation."""
        await auth_client.post(
            "/auth/register", json={"email": "Case@docura.example", "password": PASSWORD}
        )

        second = await auth_client.post(
            "/auth/register", json={"email": "CASE@DOCURA.EXAMPLE", "password": PASSWORD}
        )

        assert second.status_code == 409

    @pytest.mark.parametrize(
        ("payload", "reason"),
        [
            ({"email": "not-an-email", "password": PASSWORD}, "malformed address"),
            ({"email": "a@b.example", "password": "short"}, "password below minimum"),
            ({"email": "a@b.example"}, "missing password"),
            ({"password": PASSWORD}, "missing email"),
            ({"email": "", "password": PASSWORD}, "empty address"),
            (
                {"email": "a@b.example", "password": PASSWORD, "is_active": True},
                "attempt to set a field the client does not own",
            ),
        ],
    )
    async def test_invalid_registration_is_rejected(
        self, auth_client: AsyncClient, payload: dict[str, Any], reason: str
    ) -> None:
        """S2-T004."""
        response = await auth_client.post("/auth/register", json=payload)

        assert response.status_code in (400, 409, 422), f"{reason}: {response.text}"

    async def test_registration_never_returns_the_password(self, auth_client: AsyncClient) -> None:
        """S2-T011."""
        response = await auth_client.post(
            "/auth/register", json={"email": "quiet@docura.example", "password": PASSWORD}
        )

        assert PASSWORD not in response.text
        assert "password" not in response.json()
        assert "password_hash" not in response.json()


class TestLogin:
    async def test_valid_login_succeeds(self, auth_client: AsyncClient) -> None:
        """S2-T005."""
        await auth_client.post(
            "/auth/register", json={"email": "in@docura.example", "password": PASSWORD}
        )

        response = await auth_client.post(
            "/auth/login", json={"email": "in@docura.example", "password": PASSWORD}
        )

        assert response.status_code == 200
        body = response.json()
        assert body["access_token"]
        assert body["token_type"] == "bearer"
        assert body["user"]["email"] == "in@docura.example"

    async def test_invalid_password_is_rejected(self, auth_client: AsyncClient) -> None:
        """S2-T006."""
        await auth_client.post(
            "/auth/register", json={"email": "wrong@docura.example", "password": PASSWORD}
        )

        response = await auth_client.post(
            "/auth/login", json={"email": "wrong@docura.example", "password": OTHER_PASSWORD}
        )

        assert response.status_code == 401

    async def test_unknown_account_and_wrong_password_are_indistinguishable(
        self, auth_client: AsyncClient
    ) -> None:
        """A different message would turn login into an account-existence oracle."""
        await auth_client.post(
            "/auth/register", json={"email": "known@docura.example", "password": PASSWORD}
        )

        wrong_password = await auth_client.post(
            "/auth/login", json={"email": "known@docura.example", "password": OTHER_PASSWORD}
        )
        unknown_account = await auth_client.post(
            "/auth/login", json={"email": "nobody@docura.example", "password": OTHER_PASSWORD}
        )

        assert wrong_password.status_code == unknown_account.status_code == 401
        assert wrong_password.json()["detail"] == unknown_account.json()["detail"]
        assert wrong_password.json()["title"] == unknown_account.json()["title"]

    async def test_login_response_carries_no_hash(self, auth_client: AsyncClient) -> None:
        """S2-T011."""
        _token, user = await register_and_login(auth_client, "clean@docura.example")

        assert "password" not in user
        assert "password_hash" not in user

    async def test_token_is_not_stored_in_clear(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        """A database leak must not yield a replayable token."""
        token, _user = await register_and_login(auth_client, "opaque@docura.example")

        async with AsyncSession(db_engine) as db:
            stored = await db.scalar(select(Session.token_hash))

        assert stored is not None
        assert stored != token
        assert stored == hash_session_token(token)

    async def test_login_is_case_insensitive_on_email(self, auth_client: AsyncClient) -> None:
        await auth_client.post(
            "/auth/register", json={"email": "mixed@docura.example", "password": PASSWORD}
        )

        response = await auth_client.post(
            "/auth/login", json={"email": "MiXeD@Docura.Example", "password": PASSWORD}
        )

        assert response.status_code == 200

    async def test_each_login_issues_a_distinct_token(self, auth_client: AsyncClient) -> None:
        first, _ = await register_and_login(auth_client, "twice@docura.example")
        second = await auth_client.post(
            "/auth/login", json={"email": "twice@docura.example", "password": PASSWORD}
        )

        assert second.json()["access_token"] != first


class TestProtectedEndpoint:
    async def test_unauthenticated_request_is_rejected(self, auth_client: AsyncClient) -> None:
        """S2-T008."""
        response = await auth_client.get("/users/me")

        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"].startswith("Bearer")

    @pytest.mark.parametrize(
        "header",
        [
            {"Authorization": "Bearer not-a-real-token"},
            {"Authorization": "Bearer "},
            {"Authorization": "Basic dXNlcjpwYXNz"},
            {"Authorization": "token abc"},
            {"Authorization": ""},
        ],
    )
    async def test_invalid_authentication_is_rejected(
        self, auth_client: AsyncClient, header: dict[str, str]
    ) -> None:
        """S2-T007."""
        response = await auth_client.get("/users/me", headers=header)

        assert response.status_code == 401

    async def test_authenticated_request_succeeds(self, auth_client: AsyncClient) -> None:
        """S2-T009."""
        token, user = await register_and_login(auth_client, "me@docura.example")

        response = await auth_client.get("/users/me", headers=auth_header(token))

        assert response.status_code == 200
        body = response.json()
        assert body["email"] == "me@docura.example"
        assert body["id"] == user["id"]

    async def test_protected_response_exposes_no_credential(self, auth_client: AsyncClient) -> None:
        """S2-T011."""
        token, _user = await register_and_login(auth_client, "safe@docura.example")

        response = await auth_client.get("/users/me", headers=auth_header(token))

        assert PASSWORD not in response.text
        assert "argon2" not in response.text
        assert token not in response.text


class TestUserIsolation:
    async def test_one_account_never_sees_another(self, auth_client: AsyncClient) -> None:
        """S2-T010 — /users/me must reflect the token, not any client-supplied id."""
        token_a, user_a = await register_and_login(auth_client, "alice@docura.example")
        token_b, user_b = await register_and_login(
            auth_client, "bob@docura.example", OTHER_PASSWORD
        )

        assert user_a["id"] != user_b["id"]

        seen_by_a = await auth_client.get("/users/me", headers=auth_header(token_a))
        seen_by_b = await auth_client.get("/users/me", headers=auth_header(token_b))

        assert seen_by_a.json()["id"] == user_a["id"]
        assert seen_by_b.json()["id"] == user_b["id"]

    async def test_client_supplied_identifiers_are_ignored(self, auth_client: AsyncClient) -> None:
        """S2-T010 — NFR-SEC-003: ownership is never inferred from client input."""
        token_a, user_a = await register_and_login(auth_client, "carol@docura.example")
        _token_b, user_b = await register_and_login(
            auth_client, "dave@docura.example", OTHER_PASSWORD
        )

        response = await auth_client.get(
            "/users/me",
            headers={**auth_header(token_a), "X-User-Id": user_b["id"]},
            params={"user_id": user_b["id"], "id": user_b["id"]},
        )

        assert response.status_code == 200
        assert response.json()["id"] == user_a["id"]

    async def test_sessions_list_is_scoped_to_the_caller(self, auth_client: AsyncClient) -> None:
        """S2-T010 — Bob's sessions must be invisible to Alice."""
        token_a, _user_a = await register_and_login(auth_client, "erin@docura.example")
        token_b, _user_b = await register_and_login(
            auth_client, "frank@docura.example", OTHER_PASSWORD
        )

        a_sessions = (await auth_client.get("/auth/sessions", headers=auth_header(token_a))).json()[
            "sessions"
        ]
        b_sessions = (await auth_client.get("/auth/sessions", headers=auth_header(token_b))).json()[
            "sessions"
        ]

        assert len(a_sessions) == 1
        assert len(b_sessions) == 1
        assert {item["id"] for item in a_sessions} & {item["id"] for item in b_sessions} == set()

    async def test_one_account_cannot_revoke_anothers_sessions(
        self, auth_client: AsyncClient
    ) -> None:
        """S2-T010 — revoke-all must not reach across accounts."""
        token_a, _ = await register_and_login(auth_client, "gina@docura.example")
        token_b, _ = await register_and_login(auth_client, "hugo@docura.example", OTHER_PASSWORD)

        await auth_client.post("/auth/sessions/revoke-all", headers=auth_header(token_a))

        still_valid = await auth_client.get("/users/me", headers=auth_header(token_b))
        assert still_valid.status_code == 200


class TestSessionLifecycle:
    async def test_logout_revokes_the_current_session(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "out@docura.example")

        assert (await auth_client.get("/users/me", headers=auth_header(token))).status_code == 200

        logout = await auth_client.post("/auth/logout", headers=auth_header(token))
        assert logout.status_code == 200

        after = await auth_client.get("/users/me", headers=auth_header(token))
        assert after.status_code == 401, "a revoked token must stop working immediately"

    async def test_logout_requires_authentication(self, auth_client: AsyncClient) -> None:
        assert (await auth_client.post("/auth/logout")).status_code == 401

    async def test_revoke_all_ends_every_session(self, auth_client: AsyncClient) -> None:
        """UC-003 steps 4-5."""
        first, _ = await register_and_login(auth_client, "many@docura.example")
        second = (
            await auth_client.post(
                "/auth/login", json={"email": "many@docura.example", "password": PASSWORD}
            )
        ).json()["access_token"]

        response = await auth_client.post("/auth/sessions/revoke-all", headers=auth_header(first))

        assert response.status_code == 200
        assert response.json()["revoked"] == 2
        assert (await auth_client.get("/users/me", headers=auth_header(first))).status_code == 401
        assert (await auth_client.get("/users/me", headers=auth_header(second))).status_code == 401

    async def test_expired_session_is_rejected(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        """NFR-SEC-005 — a session must expire after inactivity."""
        token, _user = await register_and_login(auth_client, "stale@docura.example")

        async with AsyncSession(db_engine) as db:
            session = await db.scalar(
                select(Session).where(Session.token_hash == hash_session_token(token))
            )
            assert session is not None
            session.expires_at = datetime.now(UTC) - timedelta(seconds=1)
            await db.commit()

        assert (await auth_client.get("/users/me", headers=auth_header(token))).status_code == 401

    async def test_absolute_deadline_cannot_be_extended_by_activity(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        """Sliding the idle window must not let a session live forever."""
        token, _user = await register_and_login(auth_client, "forever@docura.example")

        async with AsyncSession(db_engine) as db:
            session = await db.scalar(
                select(Session).where(Session.token_hash == hash_session_token(token))
            )
            assert session is not None
            session.absolute_expires_at = datetime.now(UTC) - timedelta(seconds=1)
            await db.commit()

        assert (await auth_client.get("/users/me", headers=auth_header(token))).status_code == 401

    async def test_activity_slides_the_idle_deadline(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        token, _user = await register_and_login(auth_client, "active@docura.example")

        async with AsyncSession(db_engine) as db:
            before = await db.scalar(
                select(Session.expires_at).where(Session.token_hash == hash_session_token(token))
            )
            assert before is not None
            await db.execute(
                text("UPDATE sessions SET expires_at = expires_at - interval '5 minutes'")
            )
            await db.commit()

        await auth_client.get("/users/me", headers=auth_header(token))

        async with AsyncSession(db_engine) as db:
            after = await db.scalar(
                select(Session.expires_at).where(Session.token_hash == hash_session_token(token))
            )

        assert after is not None
        assert after > before - timedelta(minutes=5)

    async def test_deactivated_account_loses_access_immediately(
        self, auth_client: AsyncClient, db_engine: Any
    ) -> None:
        token, user = await register_and_login(auth_client, "off@docura.example")

        async with AsyncSession(db_engine) as db:
            await db.execute(text("UPDATE users SET is_active = false"))
            await db.commit()

        assert (await auth_client.get("/users/me", headers=auth_header(token))).status_code == 401
        assert user["is_active"] is True


class TestRateLimiting:
    async def test_repeated_failures_are_throttled(self, auth_client: AsyncClient) -> None:
        """Argon2 resists an offline attack; this resists an online one."""
        await auth_client.post(
            "/auth/register", json={"email": "brute@docura.example", "password": PASSWORD}
        )

        statuses = [
            (
                await auth_client.post(
                    "/auth/login",
                    json={"email": "brute@docura.example", "password": "wrong-password-x"},
                )
            ).status_code
            for _ in range(15)
        ]

        assert 429 in statuses, "an unlimited login endpoint invites credential stuffing"

    async def test_rate_limit_response_says_what_to_do(self, auth_client: AsyncClient) -> None:
        for _ in range(15):
            response = await auth_client.post(
                "/auth/login", json={"email": "x@docura.example", "password": "nope-nope-nope"}
            )
            if response.status_code == 429:
                assert response.json()["remediation"]
                return

        pytest.fail("rate limit never triggered")
