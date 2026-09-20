"""Dynamic, grounded chatbot responses — narrator composition + multi-turn wiring.

The narrator turns the orchestrator's already-owner-scoped, value-free structured context into a
natural reply, grounded strictly in that context, with the deterministic message as a guaranteed
fallback. These tests use fake completion/narrator seams — never a live LLM — and assert:
grounded composition, deterministic fallback on failure, data minimisation in the payload,
multi-turn history wiring, and that narration never alters the structured contract or the
no-submit boundary. The DB-backed test proves the deterministic fallback is context-aware.
"""

from __future__ import annotations

import json
import uuid
from typing import Any, cast

from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Environment, LlmProvider, Settings
from app.db.models import ConversationMessageType
from app.services.chatbot.intent import Intent, TaskType
from app.services.chatbot.narrator import DeterministicComposer, LlmComposer, build_composer
from app.services.chatbot.orchestrator import TaskOrchestrator
from tests.conftest import auth_header, register_and_login, requires_postgres, upload_document

_NO_DB = cast(AsyncSession, None)  # the fill_form path never touches the DB


# --------------------------------------------------------------------------- narrator (pure)
def test_llm_composer_uses_grounded_reply() -> None:
    composer = LlmComposer(provider_label="x", model="m", complete=lambda _m: "Grounded reply.")
    out = composer.compose(deterministic_message="fallback", grounding={"count": 1})
    assert out == "Grounded reply."


def test_llm_composer_falls_back_on_provider_error() -> None:
    def boom(_messages: list[dict[str, str]]) -> str:
        raise RuntimeError("timeout")

    composer = LlmComposer(provider_label="x", model="m", complete=boom)
    out = composer.compose(deterministic_message="the deterministic answer", grounding={})
    assert out == "the deterministic answer"  # never fabricated; deterministic message kept


def test_llm_composer_falls_back_on_empty_reply() -> None:
    composer = LlmComposer(provider_label="x", model="m", complete=lambda _m: "   ")
    out = composer.compose(deterministic_message="fb", grounding={})
    assert out == "fb"


def test_deterministic_composer_is_identity() -> None:
    composer = DeterministicComposer()
    assert composer.compose(deterministic_message="unchanged", grounding={"a": 1}) == "unchanged"


def test_composer_payload_carries_context_and_history_only() -> None:
    captured: dict[str, Any] = {}

    def capture(messages: list[dict[str, str]]) -> str:
        captured["messages"] = messages
        return "ok"

    composer = LlmComposer(provider_label="x", model="m", complete=capture)
    composer.compose(
        deterministic_message="You have 1 document.",
        grounding={"documents": [{"filename": "marksheet.pdf", "status": "ready"}], "count": 1},
        history=["earlier turn", "what documents do i have?"],
    )
    joined = json.dumps(captured["messages"])
    assert "marksheet.pdf" in joined  # grounding reached the model
    assert "documents" in joined
    assert "earlier turn" in joined  # history reached the model
    assert "what documents do i have?" in joined
    # Only what we passed is present — no secret/record value was smuggled in.
    assert "SECRET" not in joined
    assert "person.full_name" not in joined


def test_build_composer_selects_by_config(tmp_path: Any) -> None:
    off = Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "d",
        llm_provider=LlmProvider.NONE,
    )
    assert isinstance(build_composer(off), DeterministicComposer)
    on = Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "d",
        llm_provider=LlmProvider.OPENAI_COMPATIBLE,
        llm_model="test-model",
        llm_api_key="test-key",
    )
    assert isinstance(build_composer(on), LlmComposer)


# ------------------------------------------------------------------- orchestrator wiring (pure)
class _FixedIntent:
    name = "fixed"

    def __init__(self, task: TaskType) -> None:
        self._task = task

    def classify(self, message: str, *, history: list[str] | None = None) -> Intent:
        return Intent(
            task_type=self._task, confidence=1.0, entities={}, reason="test", method="fixed"
        )


class _RecordingNarrator:
    name = "recording"

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def compose(
        self,
        *,
        deterministic_message: str,
        grounding: dict[str, Any],
        history: list[str] | None = None,
    ) -> str:
        self.calls.append(
            {"message": deterministic_message, "grounding": grounding, "history": history}
        )
        return f"COMPOSED: {deterministic_message}"


class _StubRequirements:
    name = "stub"

    def requirements_for(self, application: str | None) -> Any:  # pragma: no cover - unused here
        raise AssertionError("fill_form must not consult the requirements provider")


async def test_narrator_receives_grounding_and_full_history() -> None:
    narrator = _RecordingNarrator()
    orch = TaskOrchestrator(
        intent_provider=_FixedIntent(TaskType.FILL_FORM),
        requirements_provider=_StubRequirements(),
        narrator=narrator,
    )
    turn = await orch.handle(
        _NO_DB, user_id=uuid.uuid4(), message="fill it for me", history=["hi", "hello"]
    )
    assert turn.message.startswith("COMPOSED: ")
    call = narrator.calls[0]
    assert call["grounding"] == turn.data  # grounded on the handler's structured context
    assert call["history"] == ["hi", "hello", "fill it for me"]  # prior turns + current message


async def test_narration_preserves_contract_and_no_submit_boundary() -> None:
    # Even a narrator that returns an (untrue) submission claim cannot change the structured
    # contract or cause a submission: message_type and data are preserved, and no submit action
    # is ever produced. The backend, not the text, is the safety boundary.
    class _RogueNarrator:
        name = "rogue"

        def compose(
            self,
            *,
            deterministic_message: str,
            grounding: dict[str, Any],
            history: list[str] | None = None,
        ) -> str:
            return "I submitted the form for you."

    orch = TaskOrchestrator(
        intent_provider=_FixedIntent(TaskType.FILL_FORM),
        requirements_provider=_StubRequirements(),
        narrator=_RogueNarrator(),
    )
    turn = await orch.handle(_NO_DB, user_id=uuid.uuid4(), message="fill it", history=None)
    assert turn.message_type is ConversationMessageType.ACTION  # unchanged
    action_types = {a["type"] for a in turn.data["actions"]}
    assert "submit" not in action_types
    assert "submit_form" not in action_types
    assert turn.data["needs_user_input"] is True  # still hands control to the user


# ------------------------------------------------------------------ context-aware fallback (HTTP)
@requires_postgres
class TestContextAwareFallback:
    async def test_documents_fallback_names_documents(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        # With no LLM configured (test env), the deterministic fallback must still be informative:
        # it names the user's actual documents rather than a generic line.
        token, _ = await register_and_login(auth_client, "dyn-owner@docura.example")
        await upload_document(auth_client, token, filename="my-marksheet.pdf")
        created = await auth_client.post("/conversations", headers=auth_header(token), json={})
        conv_id = created.json()["id"]
        r = await auth_client.post(
            f"/conversations/{conv_id}/messages",
            headers=auth_header(token),
            json={"content": "What documents do I have?"},
        )
        assert r.status_code == 201, r.text
        msg = r.json()["assistant_message"]
        assert "my-marksheet.pdf" in msg["content"]  # context-aware fallback, not generic
        assert msg["data"]["count"] == 1
