"""Chatbot orchestration layer — conversations, messages, intent, readiness, safety, privacy.

Drives the real HTTP surface for conversations/messages (auth + ownership), and the service
layer for intent classification, the requirements seam, and the readiness engine. Asserts the
safety invariants hold (no guessing, no conflict auto-resolution, no submission) and that no raw
record value leaks into a message.
"""

from __future__ import annotations

import io
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.db.models import User
from app.db.session import create_session_factory
from app.services.attribute_observation import CandidateObservation, build_attribute_observations
from app.services.chatbot.intent import DeterministicIntentProvider, TaskType
from app.services.chatbot.readiness import ReadinessStatus, compute_readiness
from app.services.chatbot.requirements import (
    RequirementItem,
    RequirementSet,
    RequirementStatus,
    UnconfiguredRequirementsProvider,
    build_requirements_provider,
)
from app.services.document_service import store_document
from app.services.extraction import ExtractedPage, ExtractionResult, TextBlock
from app.services.extraction_store import build_extraction_run
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import (
    PDF_BYTES,
    auth_header,
    register_and_login,
    requires_postgres,
    upload_document,
)

pytestmark = requires_postgres

OWNER = "chat-owner@docura.example"
OTHER = "chat-other@docura.example"


async def _new_conversation(client: AsyncClient, token: str) -> str:
    r = await client.post("/conversations", headers=auth_header(token), json={})
    assert r.status_code == 201, r.text
    return str(r.json()["id"])


# ------------------------------------------------------------------ conversations (API)
class TestConversations:
    async def test_create_list_get_rename_delete(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)

        listed = await auth_client.get("/conversations", headers=auth_header(token))
        assert listed.status_code == 200
        assert listed.json()["count"] == 1

        got = await auth_client.get(f"/conversations/{cid}", headers=auth_header(token))
        assert got.status_code == 200

        renamed = await auth_client.patch(
            f"/conversations/{cid}", headers=auth_header(token), json={"title": "Voter ID"}
        )
        assert renamed.status_code == 200
        assert renamed.json()["title"] == "Voter ID"

        deleted = await auth_client.delete(f"/conversations/{cid}", headers=auth_header(token))
        assert deleted.status_code == 204
        gone = await auth_client.get(f"/conversations/{cid}", headers=auth_header(token))
        assert gone.status_code == 404

    async def test_conversation_ownership_is_enforced(self, auth_client: AsyncClient) -> None:
        owner_token, _ = await register_and_login(auth_client, OWNER)
        other_token, _ = await register_and_login(auth_client, OTHER)
        cid = await _new_conversation(auth_client, owner_token)

        # Method-appropriate bodies so the ownership check (404) is what's exercised, not body
        # validation. Each must be a 404 for a non-owner — never a leak.
        cases: list[tuple[str, str, dict[str, str] | None]] = [
            ("GET", f"/conversations/{cid}", None),
            ("PATCH", f"/conversations/{cid}", {"title": "x"}),
            ("DELETE", f"/conversations/{cid}", None),
            ("GET", f"/conversations/{cid}/messages", None),
            ("POST", f"/conversations/{cid}/messages", {"content": "hi"}),
        ]
        for method, path, body in cases:
            r = await auth_client.request(
                method, path, headers=auth_header(other_token), json=body
            )
            assert r.status_code == 404, f"{method} {path} leaked to another user: {r.status_code}"

    async def test_unauthenticated_is_rejected(self, auth_client: AsyncClient) -> None:
        assert (await auth_client.get("/conversations")).status_code == 401
        assert (await auth_client.post("/conversations", json={})).status_code == 401


# --------------------------------------------------------------------- messages (API)
class TestMessagesAndOrchestration:
    async def test_check_documents_reflects_real_vault(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        await upload_document(auth_client, token)
        cid = await _new_conversation(auth_client, token)

        r = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "What documents do I have?"},
        )
        assert r.status_code == 201, r.text
        assistant = r.json()["assistant_message"]
        assert assistant["message_type"] == "document_status"
        assert assistant["data"]["count"] == 1
        assert assistant["data"]["task"]["task_type"] == "check_documents"

    async def test_requirements_are_never_fabricated(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)

        r = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "I need to create voter ID. What documents do I need?"},
        )
        data = r.json()["assistant_message"]["data"]
        assert data["task"]["task_type"] == "ask_requirements"
        assert data["requirements"]["status"] == "unavailable"  # no fabricated requirements
        assert data["requirements"]["documents"] == []
        assert data["requirements"]["source"] is None
        assert data["needs_user_input"] is True

    async def test_readiness_unavailable_when_requirements_unavailable(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        r = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "Am I ready to apply?"},
        )
        data = r.json()["assistant_message"]["data"]
        assert data["task"]["task_type"] == "check_readiness"
        assert data["readiness"]["computable"] is False

    async def test_fill_form_orchestrates_never_fills_or_submits(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        r = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "Fill this form"},
        )
        assistant = r.json()["assistant_message"]
        assert assistant["message_type"] == "action"
        assert "never submits" in assistant["content"].lower()
        action_types = {a["type"] for a in assistant["data"]["actions"]}
        assert "start_form_session" in action_types  # points to the extension flow, does not fill

    async def test_help_and_unknown(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        helped = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "hello"},
        )
        assert (
            helped.json()["assistant_message"]["data"]["task"]["task_type"] == "general_docura_help"
        )
        unknown = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "xyzzy plugh 1234"},
        )
        assert unknown.json()["assistant_message"]["data"]["task"]["task_type"] == "unknown"

    async def test_messages_persist_in_order(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        await auth_client.post(
            f"/conversations/{cid}/messages", headers=auth_header(token), json={"content": "help"}
        )
        listed = await auth_client.get(f"/conversations/{cid}/messages", headers=auth_header(token))
        msgs = listed.json()["messages"]
        assert [m["role"] for m in msgs] == ["user", "assistant"]

    async def test_message_validation(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        empty = await auth_client.post(
            f"/conversations/{cid}/messages", headers=auth_header(token), json={"content": ""}
        )
        assert empty.status_code == 422
        oversized = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "x" * 5000},
        )
        assert oversized.status_code == 422

    async def test_no_record_value_leaks_into_a_message(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        r = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": "What documents do I have?"},
        )
        # Document status carries filenames + statuses, never extracted personal values.
        assert "person.full_name" not in r.text  # no canonical values echoed


# --------------------------------------------------------------------- intent (unit)
class TestIntent:
    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("Fill this form", TaskType.FILL_FORM),
            ("What documents do I have?", TaskType.CHECK_DOCUMENTS),
            ("Am I ready?", TaskType.CHECK_READINESS),
            ("I need to apply for passport. What do I need?", TaskType.ASK_REQUIREMENTS),
            ("Why can't DOCURA fill this?", TaskType.EXPLAIN_BLOCKER),
            ("Which document should I use?", TaskType.DOCUMENT_MATCH),
            ("hello", TaskType.GENERAL_DOCURA_HELP),
            ("blah blah nonsense", TaskType.UNKNOWN),
        ],
    )
    def test_classifies_known_tasks(self, message: str, expected: TaskType) -> None:
        assert DeterministicIntentProvider().classify(message).task_type is expected

    def test_extracts_application_entity(self) -> None:
        intent = DeterministicIntentProvider().classify("I need to apply for a passport")
        assert intent.task_type is TaskType.ASK_REQUIREMENTS
        assert "passport" in intent.entities.get("application", "")


# ------------------------------------------------------- requirements provider (unit)
class TestRequirementsProvider:
    def test_unconfigured_never_fabricates(self) -> None:
        rs = UnconfiguredRequirementsProvider().requirements_for("voter id")
        assert rs.status is RequirementStatus.UNAVAILABLE
        assert rs.documents == ()
        assert rs.information == ()
        assert rs.source is None

    def test_build_returns_unconfigured_by_default(self, tmp_path: Any) -> None:
        settings = Settings(
            environment="test",
            database_url="postgresql://u:p@localhost:5432/none",
            document_storage_root=tmp_path / "d",
        )
        assert build_requirements_provider(settings).name == "unconfigured"


# ----------------------------------------------------------- readiness engine (service)
@requires_postgres
class TestReadiness:
    @pytest.fixture
    def session_factory(self, db_engine: Any) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(db_engine)

    @pytest.fixture
    def storage(self, db_settings: Settings) -> DocumentStorage:
        return build_document_storage(db_settings)

    async def test_readiness_reflects_record_without_guessing(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        # Seed: full_name available (one value); date_of_birth ambiguous (two values, one doc).
        async with session_factory() as db:
            user = User(email="ready@docura.example", password_hash="x")
            db.add(user)
            await db.commit()
            document = await store_document(
                db,
                owner=user,
                source=io.BytesIO(PDF_BYTES),
                filename="d.pdf",
                declared_content_type="application/pdf",
                storage=storage,
                settings=db_settings,
            )
            run = build_extraction_run(
                document_id=document.id,
                result=ExtractionResult(
                    pages=(
                        ExtractedPage(
                            number=1,
                            text="x",
                            blocks=(
                                TextBlock(text="a"),
                                TextBlock(text="b"),
                                TextBlock(text="c"),
                            ),
                        ),
                    ),
                    engine="t",
                    engine_version="1",
                ),
            )
            db.add(run)
            await db.flush()
            blocks = run.pages[0].blocks
            db.add_all(
                build_attribute_observations(
                    run=run,
                    candidates=[
                        CandidateObservation("person.full_name", "Neha Kulkarni", blocks[0], 0.9),
                        CandidateObservation("person.date_of_birth", "2007-03-24", blocks[1], 0.9),
                        CandidateObservation("person.date_of_birth", "2007-03-25", blocks[2], 0.9),
                    ],
                )
            )
            await db.commit()
            user_id = user.id

        rs = RequirementSet(
            application="voter id",
            status=RequirementStatus.VERIFIED,
            information=(
                RequirementItem(
                    "Full name", "information", canonical_identifier="person.full_name"
                ),
                RequirementItem(
                    "Date of birth", "information", canonical_identifier="person.date_of_birth"
                ),
                RequirementItem("Email", "information", canonical_identifier="person.email"),
                RequirementItem("Something", "information"),  # no mapping - unknown
            ),
            documents=(RequirementItem("Identity proof", "document"),),
            source="test",
        )
        async with session_factory() as db:
            readiness = await compute_readiness(db, user_id=user_id, requirement_set=rs)

        status_by = {i.requirement: i.status for i in readiness.items}
        assert status_by["Full name"] is ReadinessStatus.AVAILABLE
        assert status_by["Date of birth"] is ReadinessStatus.NEEDS_REVIEW  # conflict, not resolved
        assert status_by["Email"] is ReadinessStatus.MISSING
        assert status_by["Something"] is ReadinessStatus.UNKNOWN  # never guessed
        assert status_by["Identity proof"] is ReadinessStatus.UNKNOWN  # type unverifiable
        assert readiness.ready is False
        # No raw value is exposed — references are canonical ids, not values.
        assert all("Neha" not in (i.reference or "") for i in readiness.items)

    async def test_unverified_requirements_are_not_computed(
        self, session_factory: async_sessionmaker[AsyncSession]
    ) -> None:
        async with session_factory() as db:
            user = User(email="ready2@docura.example", password_hash="x")
            db.add(user)
            await db.commit()
            user_id = user.id
            rs = RequirementSet(application="x", status=RequirementStatus.UNAVAILABLE)
            readiness = await compute_readiness(db, user_id=user_id, requirement_set=rs)
        assert readiness.computable is False
        assert readiness.ready is False


# ---------------------------------------------------------------- safety (structural)
def test_no_submission_route_exists(auth_app: FastAPI) -> None:
    """DOCURA never submits: no route path suggests a form-submission capability."""
    paths = {getattr(r, "path", "") for r in auth_app.routes}
    assert not any("submit" in p.lower() for p in paths)
