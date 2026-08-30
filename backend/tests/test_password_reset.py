"""Sprint 2 — the verified reset process (FR-ACC-005, UC-001 A2).

UC-001 A2 gives this flow two properties to prove, and every test here belongs to
one of them:

* **verified** — only the address already on the account learns the token, so the
  endpoint must not say whether an address has an account, and the token must not
  come back in a response;
* **must not weaken the vault** — the reset path must not be a cheaper way into an
  account than the password it replaces: single use, short life, and every session
  ended when it succeeds.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_reset_token, verify_password
from app.db.models import PasswordResetToken, Session, User
from tests.conftest import (
    OTHER_PASSWORD,
    PASSWORD,
    RecordingResetDelivery,
    auth_header,
    register_and_login,
    request_reset_token,
    requires_postgres,
)

pytestmark = requires_postgres

NEW_PASSWORD = "a-brand-new-sufficiently-long-password"


async def _fetch_user(engine: Any, email: str) -> User:
    async with AsyncSession(engine) as db:
        user = await db.scalar(select(User).where(User.email == email))
    assert user is not None
    return user


async def _fetch_reset_rows(engine: Any) -> list[PasswordResetToken]:
    async with AsyncSession(engine) as db:
        rows = await db.scalars(select(PasswordResetToken))
        return list(rows)


class TestResetRequest:
    async def test_request_for_a_known_account_delivers_a_token(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T014 — UC-001 A2 step 1."""
        email = "forgetful@docura.example"
        await register_and_login(auth_client, email)

        response = await auth_client.post("/auth/password-reset/request", json={"email": email})

        assert response.status_code == 202
        assert reset_delivery.latest_token_for(email)

    async def test_unknown_address_is_answered_identically(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T015 — the endpoint must not be a register of who holds a vault."""
        known = "member@docura.example"
        await register_and_login(auth_client, known)

        for_known = await auth_client.post("/auth/password-reset/request", json={"email": known})
        for_unknown = await auth_client.post(
            "/auth/password-reset/request", json={"email": "stranger@docura.example"}
        )

        assert for_unknown.status_code == for_known.status_code == 202
        assert for_unknown.json() == for_known.json()
        assert not any(email == "stranger@docura.example" for email, _ in reset_delivery.sent)

    async def test_response_never_carries_the_token(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T016 — a token in the response makes the mailbox check pointless."""
        email = "leak@docura.example"
        await register_and_login(auth_client, email)

        response = await auth_client.post("/auth/password-reset/request", json={"email": email})
        token = reset_delivery.latest_token_for(email)

        assert token not in response.text

    async def test_token_is_stored_only_as_a_digest(
        self,
        auth_client: AsyncClient,
        db_engine: Any,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T017 — a database leak must not yield a usable reset link."""
        email = "digest@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        rows = await _fetch_reset_rows(db_engine)

        assert len(rows) == 1
        assert token not in rows[0].token_hash
        assert rows[0].token_hash == hash_reset_token(token)

    async def test_a_new_request_supersedes_the_previous_link(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T018 — otherwise every forgotten click leaves another live way in."""
        email = "superseded@docura.example"
        await register_and_login(auth_client, email)

        first = await request_reset_token(auth_client, reset_delivery, email)
        second = await request_reset_token(auth_client, reset_delivery, email)
        assert first != second

        stale = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": first, "password": NEW_PASSWORD},
        )

        assert stale.status_code == 400

    async def test_deactivated_account_receives_nothing(
        self,
        auth_client: AsyncClient,
        db_engine: Any,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """A reset must not be a way back into an account that was switched off."""
        email = "disabled@docura.example"
        await register_and_login(auth_client, email)

        async with AsyncSession(db_engine) as db:
            user = await db.scalar(select(User).where(User.email == email))
            assert user is not None
            user.is_active = False
            await db.commit()

        response = await auth_client.post("/auth/password-reset/request", json={"email": email})

        assert response.status_code == 202
        assert reset_delivery.sent == []


class TestResetConfirm:
    async def test_reset_replaces_the_password(
        self,
        auth_client: AsyncClient,
        db_engine: Any,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T019 — UC-001 A2: the user recovers access."""
        email = "recover@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        response = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )

        assert response.status_code == 200
        assert response.json()["status"] == "reset"

        old = await auth_client.post("/auth/login", json={"email": email, "password": PASSWORD})
        new = await auth_client.post("/auth/login", json={"email": email, "password": NEW_PASSWORD})

        assert old.status_code == 401
        assert new.status_code == 200

        user = await _fetch_user(db_engine, email)
        assert verify_password(NEW_PASSWORD, user.password_hash)
        assert NEW_PASSWORD not in user.password_hash

    async def test_reset_does_not_return_a_session(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """Possession of a mailbox is not, on its own, an authenticated session."""
        email = "nosession@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        response = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )

        assert "access_token" not in response.json()

    async def test_token_is_single_use(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T020 — a replayable link is a standing key to the account."""
        email = "once@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        first = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )
        second = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": "yet-another-long-password"},
        )

        assert first.status_code == 200
        assert second.status_code == 400

    async def test_expired_token_is_refused(
        self,
        auth_client: AsyncClient,
        db_engine: Any,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T021 — the link's life is bounded, like a session's."""
        email = "expired@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        async with AsyncSession(db_engine) as db:
            row = await db.scalar(
                select(PasswordResetToken).where(
                    PasswordResetToken.token_hash == hash_reset_token(token)
                )
            )
            assert row is not None
            row.expires_at = datetime.now(UTC) - timedelta(minutes=1)
            await db.commit()

        response = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )

        assert response.status_code == 400

        still_old = await auth_client.post(
            "/auth/login", json={"email": email, "password": PASSWORD}
        )
        assert still_old.status_code == 200

    async def test_unknown_token_is_refused_with_the_same_message(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T022 — invalid, spent, and expired must be indistinguishable."""
        email = "sameerror@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )
        spent = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )
        unknown = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": "not-a-real-reset-token", "password": NEW_PASSWORD},
        )

        assert spent.status_code == unknown.status_code == 400
        assert spent.json()["detail"] == unknown.json()["detail"]
        assert spent.json()["title"] == unknown.json()["title"]

    async def test_error_says_what_to_do_next(self, auth_client: AsyncClient) -> None:
        """NFR-ERR-001 — an error names the remedy, not just the failure."""
        response = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": "no-such-token", "password": NEW_PASSWORD},
        )

        body = response.json()
        assert body["remediation"]
        assert response.headers["content-type"].startswith("application/problem+json")

    async def test_weak_password_is_rejected_without_spending_the_token(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T023 — a rejected password must not burn the user's only link.

        The reset must also not be a way *around* the password policy: the same
        minimum applies here as at registration.
        """
        email = "weak@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        rejected = await auth_client.post(
            "/auth/password-reset/confirm", json={"token": token, "password": "short"}
        )
        retried = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": token, "password": NEW_PASSWORD},
        )

        assert rejected.status_code == 422
        assert retried.status_code == 200


class TestResetAndSessions:
    async def test_reset_revokes_every_existing_session(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T024 — NFR-SEC-005: whoever held the old password is signed out.

        This is the property that keeps a reset from *weakening* the vault: if an
        attacker's session survived the owner's password change, the reset would
        have accomplished nothing.
        """
        email = "evict@docura.example"
        first_token, _ = await register_and_login(auth_client, email)
        second_login = await auth_client.post(
            "/auth/login", json={"email": email, "password": PASSWORD}
        )
        second_token = second_login.json()["access_token"]

        reset_token = await request_reset_token(auth_client, reset_delivery, email)
        response = await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": reset_token, "password": NEW_PASSWORD},
        )

        assert response.json()["sessions_revoked"] == 2

        for token in (first_token, second_token):
            after = await auth_client.get("/users/me", headers=auth_header(token))
            assert after.status_code == 401

    async def test_revoked_sessions_are_marked_in_the_database(
        self,
        auth_client: AsyncClient,
        db_engine: Any,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """Revocation is server-side state, not merely a rejected response."""
        email = "marked@docura.example"
        await register_and_login(auth_client, email)
        reset_token = await request_reset_token(auth_client, reset_delivery, email)

        await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": reset_token, "password": NEW_PASSWORD},
        )

        async with AsyncSession(db_engine) as db:
            sessions = list(await db.scalars(select(Session)))

        assert sessions
        assert all(session.revoked_at is not None for session in sessions)


class TestResetIsolation:
    async def test_a_reset_touches_only_its_own_account(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S2-T025 — FR-ACC-003, NFR-SEC-003: one record, one owner.

        The token names its account; nothing the caller sends does. There is no
        field on the confirm request that could point the reset at someone else.
        """
        owner = "owner@docura.example"
        bystander = "bystander@docura.example"
        await register_and_login(auth_client, owner)
        bystander_token, _ = await register_and_login(auth_client, bystander, OTHER_PASSWORD)

        reset_token = await request_reset_token(auth_client, reset_delivery, owner)
        await auth_client.post(
            "/auth/password-reset/confirm",
            json={"token": reset_token, "password": NEW_PASSWORD},
        )

        bystander_still_in = await auth_client.get(
            "/users/me", headers=auth_header(bystander_token)
        )
        bystander_login = await auth_client.post(
            "/auth/login", json={"email": bystander, "password": OTHER_PASSWORD}
        )

        assert bystander_still_in.status_code == 200
        assert bystander_login.status_code == 200

    async def test_confirm_request_rejects_an_unexpected_user_field(
        self,
        auth_client: AsyncClient,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """Ownership is never taken from the client (NFR-SEC-003)."""
        email = "extra@docura.example"
        await register_and_login(auth_client, email)
        token = await request_reset_token(auth_client, reset_delivery, email)

        response = await auth_client.post(
            "/auth/password-reset/confirm",
            json={
                "token": token,
                "password": NEW_PASSWORD,
                "user_id": "00000000-0000-0000-0000-000000000001",
            },
        )

        assert response.status_code == 422


class TestResetRateLimiting:
    async def test_reset_requests_are_throttled(self, auth_client: AsyncClient) -> None:
        """Unlimited, this endpoint is both a mail bomb and an address enumerator."""
        statuses = [
            (
                await auth_client.post(
                    "/auth/password-reset/request",
                    json={"email": f"flood{index}@docura.example"},
                )
            ).status_code
            for index in range(15)
        ]

        assert 429 in statuses

    async def test_confirm_attempts_are_throttled(self, auth_client: AsyncClient) -> None:
        """A 256-bit token resists guessing; the limit resists trying anyway."""
        statuses = [
            (
                await auth_client.post(
                    "/auth/password-reset/confirm",
                    json={"token": f"guess-{index}", "password": NEW_PASSWORD},
                )
            ).status_code
            for index in range(15)
        ]

        assert 429 in statuses
