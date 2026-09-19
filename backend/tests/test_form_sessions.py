"""M1 — the form-session and audit foundation.

These tests exercise the backend the future browser extension calls: opening a session
on a form (explicit activation), ending it (hand back or stop), and reading its
append-only history — scoped to the authenticated user. Filling, detection,
attachment, and approval are later milestones and are not exercised here; the audit
*writer* they will use (:func:`record_action`) is tested directly, as the current
record tests seed observations directly for lack of a creation endpoint.

Needs a real PostgreSQL (native UUID); skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

import uuid
from typing import Any

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.db.models import (
    FormAction,
    FormActionOutcome,
    FormActionType,
    FormSession,
    FormSessionState,
)
from app.services import form_session as svc
from tests.conftest import (
    auth_header,
    register_and_login,
    requires_postgres,
    upload_document,
)

pytestmark = requires_postgres


async def _activate(client: AsyncClient, token: str) -> dict[str, Any]:
    response = await client.post("/form-sessions", headers=auth_header(token))
    assert response.status_code == 201, response.text
    body: dict[str, Any] = response.json()
    return body


class TestActivationAndOwnership:
    async def test_authenticated_user_activates_a_session(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        body = await _activate(auth_client, token)
        # Explicit activation is representable: the session exists and is active.
        assert body["state"] == "active"
        assert body["ended_at"] is None
        assert uuid.UUID(body["id"])

    async def test_session_is_owned_by_its_creator(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)

        fetched = await auth_client.get(
            f"/form-sessions/{created['id']}", headers=auth_header(token)
        )
        assert fetched.status_code == 200, fetched.text
        assert fetched.json()["id"] == created["id"]

    async def test_another_user_cannot_access_the_session(self, auth_client: AsyncClient) -> None:
        token_a, _a = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token_a)

        token_b, _b = await register_and_login(auth_client, "b@example.com")
        # A session owned by A answers 404 for B, exactly as a nonexistent id does.
        other = await auth_client.get(
            f"/form-sessions/{created['id']}", headers=auth_header(token_b)
        )
        assert other.status_code == 404, other.text
        history = await auth_client.get(
            f"/form-sessions/{created['id']}/actions", headers=auth_header(token_b)
        )
        assert history.status_code == 404, history.text

    async def test_authentication_is_enforced(self, auth_client: AsyncClient) -> None:
        assert (await auth_client.post("/form-sessions")).status_code == 401
        assert (await auth_client.get("/form-sessions")).status_code == 401
        assert (await auth_client.get(f"/form-sessions/{uuid.uuid4()}")).status_code == 401


class TestLifecycle:
    async def test_hand_back_transitions_and_is_recorded(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)

        handed = await auth_client.post(
            f"/form-sessions/{created['id']}/hand-back", headers=auth_header(token)
        )
        assert handed.status_code == 200, handed.text
        body = handed.json()
        assert body["state"] == "handed_back"
        assert body["ended_at"] is not None

        # FR-SUB-004: reaching hand-back is recorded in the history.
        history = await auth_client.get(
            f"/form-sessions/{created['id']}/actions", headers=auth_header(token)
        )
        actions = history.json()["actions"]
        assert [a["action_type"] for a in actions] == ["hand_back"]
        assert actions[0]["outcome"] == "succeeded"

    async def test_stop_transitions_and_is_recorded(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)

        stopped = await auth_client.post(
            f"/form-sessions/{created['id']}/stop", headers=auth_header(token)
        )
        assert stopped.status_code == 200, stopped.text
        assert stopped.json()["state"] == "stopped"

        history = await auth_client.get(
            f"/form-sessions/{created['id']}/actions", headers=auth_header(token)
        )
        assert [a["action_type"] for a in history.json()["actions"]] == ["stop"]

    async def test_an_ended_session_refuses_a_second_transition(
        self, auth_client: AsyncClient
    ) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)
        await auth_client.post(f"/form-sessions/{created['id']}/stop", headers=auth_header(token))
        # BR-016: an already-ended session does not end again.
        again = await auth_client.post(
            f"/form-sessions/{created['id']}/hand-back", headers=auth_header(token)
        )
        assert again.status_code == 409, again.text

    async def test_expiry_is_representable(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)
        session_factory: async_sessionmaker[AsyncSession] = auth_app.state.session_factory

        # EC-016: server-driven, so there is no endpoint — the service marks it expired.
        async with session_factory() as db:
            session = await svc.expire_form_session(
                db, user_id=uuid.UUID(user["id"]), session_id=uuid.UUID(created["id"])
            )
            assert session.state is FormSessionState.EXPIRED

        fetched = await auth_client.get(
            f"/form-sessions/{created['id']}", headers=auth_header(token)
        )
        assert fetched.json()["state"] == "expired"


class TestAuditHistory:
    async def _new_active_session(
        self, session_factory: async_sessionmaker[AsyncSession], user_id: uuid.UUID
    ) -> uuid.UUID:
        async with session_factory() as db:
            session = await svc.create_form_session(db, user_id=user_id)
            return session.id

    async def test_failed_action_is_recorded_without_pretending_success(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        _token, user = await register_and_login(auth_client, "a@example.com")
        session_factory = auth_app.state.session_factory
        session_id = await self._new_active_session(session_factory, uuid.UUID(user["id"]))

        # BR-016 / EC-014: a degraded fill is recorded as a failure, never as success.
        async with session_factory() as db:
            session = await svc.get_form_session(
                db, user_id=uuid.UUID(user["id"]), session_id=session_id
            )
            action = await svc.record_action(
                db,
                session=session,
                action_type=FormActionType.FILL,
                outcome=FormActionOutcome.FAILED,
                field_ref="applicant_email",
            )
            await db.commit()
            assert action.outcome is FormActionOutcome.FAILED

    async def test_reversal_is_a_new_append_only_entry(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, user = await register_and_login(auth_client, "a@example.com")
        session_factory = auth_app.state.session_factory
        session_id = await self._new_active_session(session_factory, uuid.UUID(user["id"]))

        async with session_factory() as db:
            session = await svc.get_form_session(
                db, user_id=uuid.UUID(user["id"]), session_id=session_id
            )
            original = await svc.record_action(
                db,
                session=session,
                action_type=FormActionType.FILL,
                outcome=FormActionOutcome.SUCCEEDED,
                field_ref="applicant_name",
                detail="Priya Sharma",
            )
            await db.commit()
            original_id, original_created = original.id, original.created_at

        # FR-AUD-005 / BR-015: the correction is a *new* row pointing back, not an edit.
        async with session_factory() as db:
            session = await svc.get_form_session(
                db, user_id=uuid.UUID(user["id"]), session_id=session_id
            )
            await svc.record_action(
                db,
                session=session,
                action_type=FormActionType.OVERRIDE,
                outcome=FormActionOutcome.SUCCEEDED,
                field_ref="applicant_name",
                reverses_action_id=original_id,
            )
            await db.commit()

        history = await auth_client.get(
            f"/form-sessions/{session_id}/actions", headers=auth_header(token)
        )
        actions = history.json()["actions"]
        assert [a["action_type"] for a in actions] == ["fill", "override"]
        # The original is untouched; the override references it.
        assert actions[1]["reverses_action_id"] == str(original_id)

        async with session_factory() as db:
            reloaded = await db.get(FormAction, original_id)
            assert reloaded is not None
            assert reloaded.created_at == original_created  # unchanged
            assert reloaded.reverses_action_id is None

    async def test_action_belongs_to_its_session(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        _token, user = await register_and_login(auth_client, "a@example.com")
        session_factory = auth_app.state.session_factory
        s1 = await self._new_active_session(session_factory, uuid.UUID(user["id"]))
        s2 = await self._new_active_session(session_factory, uuid.UUID(user["id"]))

        async with session_factory() as db:
            session = await svc.get_form_session(db, user_id=uuid.UUID(user["id"]), session_id=s1)
            await svc.record_action(
                db,
                session=session,
                action_type=FormActionType.ASK,
                outcome=FormActionOutcome.SKIPPED,
            )
            await db.commit()
            just_s2 = await svc.list_actions(
                db,
                session=await svc.get_form_session(
                    db, user_id=uuid.UUID(user["id"]), session_id=s2
                ),
            )
        # The other session's history does not leak the first session's action.
        assert just_s2 == []

    async def test_history_does_not_cross_user_boundaries(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token_a, _user_a = await register_and_login(auth_client, "a@example.com")
        token_b, _user_b = await register_and_login(auth_client, "b@example.com")
        await _activate(auth_client, token_a)
        await _activate(auth_client, token_b)

        # Each listing shows only the caller's own sessions.
        list_a = (await auth_client.get("/form-sessions", headers=auth_header(token_a))).json()
        list_b = (await auth_client.get("/form-sessions", headers=auth_header(token_b))).json()
        assert list_a["count"] == 1
        assert list_b["count"] == 1
        assert {s["id"] for s in list_a["sessions"]} & {
            s["id"] for s in list_b["sessions"]
        } == set()


class TestDataMinimisation:
    async def test_action_references_provenance_by_id_not_content(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, user = await register_and_login(auth_client, "a@example.com")
        document = await upload_document(auth_client, token)
        session_factory = auth_app.state.session_factory

        async with session_factory() as db:
            session = await svc.create_form_session(db, user_id=uuid.UUID(user["id"]))
            await svc.record_action(
                db,
                session=session,
                action_type=FormActionType.ATTACH,
                outcome=FormActionOutcome.SUCCEEDED,
                field_ref="proof_of_identity",
                source_document_id=uuid.UUID(document["id"]),
            )
            await db.commit()
            session_id = session.id

        history = await auth_client.get(
            f"/form-sessions/{session_id}/actions", headers=auth_header(token)
        )
        action = history.json()["actions"][0]
        # The document is referenced by id; no bytes, key, or checksum are copied in.
        assert action["document_id"] == document["id"]
        assert "storage_key" not in history.text
        assert "checksum" not in history.text
        assert "%PDF" not in history.text

    def test_the_audit_model_has_no_content_columns(self) -> None:
        """Structural: there is nowhere on a form action to store form/file content."""
        columns = set(FormAction.__table__.columns.keys())
        assert not (
            columns & {"value", "storage_key", "checksum_sha256", "content", "page_content"}
        )

    async def test_session_and_action_cascade_when_the_account_is_deleted(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        _token, user = await register_and_login(auth_client, "a@example.com")
        session_factory = auth_app.state.session_factory
        async with session_factory() as db:
            session = await svc.create_form_session(db, user_id=uuid.UUID(user["id"]))
            await svc.record_action(
                db,
                session=session,
                action_type=FormActionType.HAND_BACK,
                outcome=FormActionOutcome.SUCCEEDED,
            )
            await db.commit()

        # BR-018 / FR-ACC-007: deleting the account leaves no orphaned session or action.
        from app.db.models import User

        async with session_factory() as db:
            account = await db.get(User, uuid.UUID(user["id"]))
            assert account is not None
            await db.delete(account)
            await db.commit()

        async with session_factory() as db:
            sessions = (await db.scalars(select(FormSession))).all()
            actions = (await db.scalars(select(FormAction))).all()
        assert sessions == []
        assert actions == []


class TestRecordAction:
    """POST /form-sessions/{id}/actions — the extension records its in-session effects.

    Owner-scoped and forgery-resistant: only the caller's own ACTIVE session, only
    in-session action types, only the caller's own referenced ids, no field value stored.
    """

    async def test_records_a_fill_action_and_it_appears_in_history(
        self, auth_client: AsyncClient
    ) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)

        response = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={
                "action_type": "fill",
                "outcome": "succeeded",
                "field_ref": "#full_name",
                "detail": "person.full_name",
            },
        )
        assert response.status_code == 201, response.text
        body = response.json()
        assert body["action_type"] == "fill"
        assert body["outcome"] == "succeeded"
        assert body["field_ref"] == "#full_name"
        assert "value" not in body  # never a field value

        history = await auth_client.get(
            f"/form-sessions/{created['id']}/actions", headers=auth_header(token)
        )
        types = [a["action_type"] for a in history.json()["actions"]]
        assert "fill" in types

    async def test_lifecycle_action_types_are_rejected(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)
        for bad in ("hand_back", "stop"):
            response = await auth_client.post(
                f"/form-sessions/{created['id']}/actions",
                headers=auth_header(token),
                json={"action_type": bad, "outcome": "succeeded"},
            )
            assert response.status_code == 422, f"{bad}: {response.text}"

    async def test_cannot_record_on_an_ended_session(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)
        await auth_client.post(f"/form-sessions/{created['id']}/stop", headers=auth_header(token))

        response = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={"action_type": "fill", "outcome": "succeeded", "field_ref": "#x"},
        )
        assert response.status_code == 409, response.text

    async def test_another_user_cannot_record_to_the_session(
        self, auth_client: AsyncClient
    ) -> None:
        token_a, _a = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token_a)
        token_b, _b = await register_and_login(auth_client, "b@example.com")

        response = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token_b),
            json={"action_type": "fill", "outcome": "succeeded", "field_ref": "#x"},
        )
        assert response.status_code == 404, response.text  # same 404 as a nonexistent session

    async def test_attach_requires_an_owned_document(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)

        # A document owned by someone else must not be referable.
        token_b, _b = await register_and_login(auth_client, "b@example.com")
        other_doc = await upload_document(auth_client, token_b)
        denied = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={"action_type": "attach", "outcome": "succeeded", "document_id": other_doc["id"]},
        )
        assert denied.status_code == 404, denied.text

        # The caller's own document is accepted.
        own_doc = await upload_document(auth_client, token)
        ok = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={"action_type": "attach", "outcome": "succeeded", "document_id": own_doc["id"]},
        )
        assert ok.status_code == 201, ok.text
        assert ok.json()["document_id"] == own_doc["id"]

    async def test_reversal_must_reference_an_action_in_the_same_session(
        self, auth_client: AsyncClient
    ) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)

        # An unknown action id cannot be reversed.
        missing = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={
                "action_type": "override",
                "outcome": "succeeded",
                "reverses_action_id": str(uuid.uuid4()),
            },
        )
        assert missing.status_code == 404, missing.text

        # An action from THIS session can be reversed.
        first = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={"action_type": "fill", "outcome": "succeeded", "field_ref": "#x"},
        )
        reversal = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={
                "action_type": "override",
                "outcome": "succeeded",
                "field_ref": "#x",
                "reverses_action_id": first.json()["id"],
            },
        )
        assert reversal.status_code == 201, reversal.text
        assert reversal.json()["reverses_action_id"] == first.json()["id"]

    async def test_approval_decision_is_auditable(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        created = await _activate(auth_client, token)
        response = await auth_client.post(
            f"/form-sessions/{created['id']}/actions",
            headers=auth_header(token),
            json={
                "action_type": "approval_decision",
                "outcome": "succeeded",
                "field_ref": "#sensitive_full_name",
                "detail": "person.full_name",
            },
        )
        assert response.status_code == 201, response.text
        assert response.json()["action_type"] == "approval_decision"

    async def test_authentication_is_enforced(self, auth_client: AsyncClient) -> None:
        response = await auth_client.post(
            f"/form-sessions/{uuid.uuid4()}/actions",
            json={"action_type": "fill", "outcome": "succeeded"},
        )
        assert response.status_code == 401
