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


# ------------------------------------------------------------- quick-action cards (API)
class TestQuickActions:
    """The four Ask-page cards must each start their intended workflow via an explicit
    ``task_type`` hint — never fall through to a generic reply — while every grounding and
    safety invariant still holds."""

    async def _send(self, client: AsyncClient, token: str, content: str, task_type: str) -> dict:
        cid = await _new_conversation(client, token)
        r = await client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": content, "task_type": task_type},
        )
        assert r.status_code == 201, r.text
        return r.json()["assistant_message"]

    async def test_find_required_documents_starts_ask_requirements(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        assistant = await self._send(
            auth_client, token, "What documents do I need?", "ask_requirements"
        )
        data = assistant["data"]
        assert data["task"]["task_type"] == "ask_requirements"
        assert data["task"]["method"] == "quick_action_selection"
        # Requirements are never fabricated without a configured authoritative source, and the
        # user is asked for more instead of guessing.
        assert data["requirements"]["status"] == "unavailable"
        assert data["requirements"]["documents"] == []
        assert data["needs_user_input"] is True

    async def test_check_application_starts_check_readiness(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        # This prompt does NOT match any readiness phrase, so without the hint it would misroute;
        # the hint guarantees the readiness workflow.
        assistant = await self._send(
            auth_client,
            token,
            "Which of my details are ready, missing, or need review?",
            "check_readiness",
        )
        data = assistant["data"]
        assert data["task"]["task_type"] == "check_readiness"
        # Never "ready" when requirements are unavailable — it reports it cannot check yet.
        assert data["readiness"]["computable"] is False
        assert data["readiness"]["ready"] is False

    async def test_fill_a_form_starts_fill_form_and_never_submits(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        # "How does DOCURA fill a form…" would classify to general help without the hint.
        assistant = await self._send(
            auth_client, token, "How does DOCURA fill a form using my documents?", "fill_form"
        )
        assert assistant["data"]["task"]["task_type"] == "fill_form"
        assert assistant["message_type"] == "action"
        assert "never submits" in assistant["content"].lower()
        action_types = {a["type"] for a in assistant["data"]["actions"]}
        assert "start_form_session" in action_types  # routes to the extension, does not fill/submit

    async def test_review_my_documents_reflects_real_vault(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        await upload_document(auth_client, token)
        assistant = await self._send(
            auth_client, token, "Summarise what DOCURA has read.", "check_documents"
        )
        data = assistant["data"]
        assert data["task"]["task_type"] == "check_documents"
        assert assistant["message_type"] == "document_status"
        assert data["count"] == 1  # grounded in the real vault, not fabricated

    async def test_review_my_documents_is_honest_when_vault_is_empty(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        assistant = await self._send(
            auth_client, token, "Summarise what DOCURA has read.", "check_documents"
        )
        assert assistant["data"]["count"] == 0
        assert "haven't uploaded" in assistant["content"].lower()

    async def test_hint_overrides_misclassifying_text(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        text = "How does DOCURA fill a form using my documents?"
        # Without the hint this text classifies to general help (the old generic behaviour)…
        without = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": text},
        )
        without_task = without.json()["assistant_message"]["data"]["task"]["task_type"]
        assert without_task == "general_docura_help"
        # …with the fill_form hint it starts the correct workflow.
        with_hint = await auth_client.post(
            f"/conversations/{cid}/messages",
            headers=auth_header(token),
            json={"content": text, "task_type": "fill_form"},
        )
        assert with_hint.json()["assistant_message"]["data"]["task"]["task_type"] == "fill_form"

    async def test_unrecognised_hint_falls_back_to_classification(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        # A client can't force an internal task; the hint is ignored and the text is classified.
        assistant = await self._send(auth_client, token, "hello", "explain_blocker")
        assert assistant["data"]["task"]["task_type"] == "general_docura_help"


# ---------------------------------------------------- quick-action task continuation (API)
class TestTaskContinuation:
    """A selected quick-action task stays active across follow-up turns until it is completed,
    switched to another explicit task, or cancelled — all end to end through the real API."""

    async def _post(
        self, client: AsyncClient, token: str, cid: str, content: str, task_type: str | None = None
    ) -> dict:
        body: dict[str, str] = {"content": content}
        if task_type is not None:
            body["task_type"] = task_type
        r = await client.post(
            f"/conversations/{cid}/messages", headers=auth_header(token), json=body
        )
        assert r.status_code == 201, r.text
        return r.json()["assistant_message"]

    async def test_followup_retains_ask_requirements(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        await self._post(auth_client, token, cid, "What do I need?", "ask_requirements")
        # Plain follow-up with NO task hint must stay with ask_requirements, not re-classify.
        follow = await self._post(auth_client, token, cid, "Passport application")
        assert follow["data"]["task"]["task_type"] == "ask_requirements"
        assert follow["data"]["task"]["method"] == "quick_action_continuation"
        # Still never fabricates requirements.
        assert follow["data"]["requirements"]["status"] == "unavailable"
        assert follow["data"]["requirements"]["documents"] == []

    async def test_multiple_followups_retain_task(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        await self._post(auth_client, token, cid, "Which are ready?", "check_readiness")
        first = await self._post(auth_client, token, cid, "Passport application")
        second = await self._post(auth_client, token, cid, "and the details")
        assert first["data"]["task"]["task_type"] == "check_readiness"
        assert second["data"]["task"]["task_type"] == "check_readiness"
        # Readiness rules still hold: never "ready" without an authoritative requirements source.
        assert second["data"]["readiness"]["computable"] is False
        assert second["data"]["readiness"]["ready"] is False

    async def test_explicit_new_quick_action_switches_task(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        await self._post(auth_client, token, cid, "What do I need?", "ask_requirements")
        switched = await self._post(auth_client, token, cid, "Fill a form", "fill_form")
        assert switched["data"]["task"]["task_type"] == "fill_form"
        assert switched["message_type"] == "action"
        assert "never submits" in switched["content"].lower()

    async def test_no_active_task_classifies_normally(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        # No prior task: the follow-up phrase is classified as before (unknown), not inherited.
        reply = await self._post(auth_client, token, cid, "Passport application")
        assert reply["data"]["task"]["task_type"] == "unknown"

    async def test_cancel_clears_active_task(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        await self._post(auth_client, token, cid, "What do I need?", "ask_requirements")
        cleared = await self._post(auth_client, token, cid, "never mind")
        assert cleared["data"]["task"]["task_type"] == "general_docura_help"
        assert cleared["data"]["task"]["method"] == "task_cleared"
        # After cancelling, a plain follow-up is classified normally again (task truly cleared).
        after = await self._post(auth_client, token, cid, "Passport application")
        assert after["data"]["task"]["task_type"] == "unknown"

    async def test_review_documents_continuation_uses_real_vault(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        await upload_document(auth_client, token)
        cid = await _new_conversation(auth_client, token)
        await self._post(auth_client, token, cid, "Review my documents", "check_documents")
        follow = await self._post(auth_client, token, cid, "Show me what you found.")
        assert follow["data"]["task"]["task_type"] == "check_documents"
        assert follow["message_type"] == "document_status"
        assert follow["data"]["count"] == 1  # real vault, not fabricated

    async def test_fill_form_continuation_never_submits(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        cid = await _new_conversation(auth_client, token)
        await self._post(auth_client, token, cid, "Fill a form", "fill_form")
        follow = await self._post(auth_client, token, cid, "Passport application")
        assert follow["data"]["task"]["task_type"] == "fill_form"
        assert "never submits" in follow["content"].lower()


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
