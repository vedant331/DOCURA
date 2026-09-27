"""Quick-action routing — the UI cards must start their intended workflow, not a generic reply.

These are the DB-free unit checks: the task-hint coercion, and that an explicit hint overrides
text classification for the two handlers that touch no database (fill_form, ask_requirements).
The database-backed end-to-end checks for all four cards live in ``test_chatbot.py``
(``TestQuickActions``) and run when a test database is configured.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any, cast

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Environment, Settings
from app.services.chatbot.intent import DeterministicIntentProvider, TaskType
from app.services.chatbot.orchestrator import _coerce_task_type, build_orchestrator


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        environment=Environment.TEST,
        database_url="postgresql://u:p@localhost:5432/none",
        document_storage_root=tmp_path / "documents",
    )


class TestClassifierWordBoundaries:
    """Intent matching must respect word boundaries, so an ordinary follow-up that merely
    contains a rule's characters stays UNKNOWN (letting the active task be inherited)."""

    @pytest.mark.parametrize(
        "message",
        [
            "this",  # contains "hi"
            "which",  # contains "hi"
            "while",  # contains "hi"
            "they said so",  # contains "hey"
            "the one on this page",  # "hi" inside "this"
            "helpless",  # contains "help"
            "Passport application",  # the canonical continuation follow-up
            "Show me what you found.",
        ],
    )
    def test_substring_lookalikes_are_unknown(self, message: str) -> None:
        assert DeterministicIntentProvider().classify(message).task_type is TaskType.UNKNOWN

    @pytest.mark.parametrize(
        ("message", "expected"),
        [
            ("hi", TaskType.GENERAL_DOCURA_HELP),
            ("hello", TaskType.GENERAL_DOCURA_HELP),
            ("hey there", TaskType.GENERAL_DOCURA_HELP),
            ("help", TaskType.GENERAL_DOCURA_HELP),
            ("Fill this form", TaskType.FILL_FORM),
            ("What documents do I have?", TaskType.CHECK_DOCUMENTS),
            ("Am I ready?", TaskType.CHECK_READINESS),
            ("Which document should I use?", TaskType.DOCUMENT_MATCH),
            ("I need to apply for a passport. What do I need?", TaskType.ASK_REQUIREMENTS),
            ("Why can't DOCURA fill this?", TaskType.EXPLAIN_BLOCKER),
        ],
    )
    def test_legitimate_phrases_still_classify(self, message: str, expected: TaskType) -> None:
        assert DeterministicIntentProvider().classify(message).task_type is expected


class TestCoerceTaskType:
    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("ask_requirements", TaskType.ASK_REQUIREMENTS),
            ("check_documents", TaskType.CHECK_DOCUMENTS),
            ("check_readiness", TaskType.CHECK_READINESS),
            ("fill_form", TaskType.FILL_FORM),
        ],
    )
    def test_recognised_quick_actions(self, value: str, expected: TaskType) -> None:
        assert _coerce_task_type(value) is expected

    @pytest.mark.parametrize("value", [None, "", "bogus", "not_a_task"])
    def test_unrecognised_hint_defers_to_classification(self, value: str | None) -> None:
        assert _coerce_task_type(value) is None

    @pytest.mark.parametrize(
        "value", ["explain_blocker", "document_match", "general_docura_help", "unknown"]
    )
    def test_internal_tasks_cannot_be_forced_from_the_ui(self, value: str) -> None:
        # A hint may only start a user-initiable workflow; internal tasks fall back to
        # classification rather than being forced by a client.
        assert _coerce_task_type(value) is None


class TestQuickActionOverridesClassification:
    """A hint wins over the message text, so a card never lands on a generic reply."""

    async def test_fill_form_hint_overrides_generic_text(self, tmp_path: Path) -> None:
        orch = build_orchestrator(_settings(tmp_path))
        # "hello" alone classifies to general help; the fill_form hint must win.
        turn = await orch.handle(
            cast("AsyncSession", None),
            user_id=uuid.uuid4(),
            message="hello",
            task_type="fill_form",
        )
        assert turn.data["task"]["task_type"] == "fill_form"
        assert turn.data["task"]["method"] == "quick_action_selection"
        # Never claims to fill or submit the form from chat.
        assert "never submits" in turn.message.lower()

    async def test_ask_requirements_hint_never_fabricates(self, tmp_path: Path) -> None:
        orch = build_orchestrator(_settings(tmp_path))
        turn = await orch.handle(
            cast("AsyncSession", None),
            user_id=uuid.uuid4(),
            message="hello",
            task_type="ask_requirements",
        )
        assert turn.data["task"]["task_type"] == "ask_requirements"
        # No configured authoritative source → requirements are reported unavailable, never
        # invented, and the user is asked for more (needs_user_input).
        assert turn.data["requirements"]["status"] == "unavailable"
        assert turn.data["requirements"]["documents"] == []
        assert turn.data["needs_user_input"] is True

    async def test_unrecognised_hint_falls_back_to_text(self, tmp_path: Path) -> None:
        orch = build_orchestrator(_settings(tmp_path))
        turn = await orch.handle(
            cast("AsyncSession", None),
            user_id=uuid.uuid4(),
            message="hello",
            task_type="totally-made-up",
        )
        # Falls back to classifying the text ("hello" → general help), not an error.
        assert turn.data["task"]["task_type"] == "general_docura_help"


class TestTaskContinuation:
    """An active task carries across turns until completed, switched, or cancelled (DB-free
    cases: fill_form / ask_requirements). Database-backed continuation is in test_chatbot.py."""

    async def _handle(
        self,
        tmp_path: Path,
        message: str,
        *,
        task_type: str | None = None,
        active_task_type: str | None = None,
    ) -> dict[str, Any]:
        orch = build_orchestrator(_settings(tmp_path))
        turn = await orch.handle(
            cast("AsyncSession", None),
            user_id=uuid.uuid4(),
            message=message,
            task_type=task_type,
            active_task_type=active_task_type,
        )
        return turn.data

    async def test_followup_inherits_active_task(self, tmp_path: Path) -> None:
        # "Passport application" classifies to UNKNOWN on its own; with an active ask_requirements
        # task it must stay with that task, not fall to unknown/general.
        data = await self._handle(
            tmp_path, "Passport application", active_task_type="ask_requirements"
        )
        assert data["task"]["task_type"] == "ask_requirements"
        assert data["task"]["method"] == "quick_action_continuation"
        # Still never fabricates requirements.
        assert data["requirements"]["status"] == "unavailable"
        assert data["requirements"]["documents"] == []

    async def test_followup_inherits_fill_form_and_never_submits(self, tmp_path: Path) -> None:
        data = await self._handle(
            tmp_path, "Passport application", active_task_type="fill_form"
        )
        assert data["task"]["task_type"] == "fill_form"
        assert data["task"]["method"] == "quick_action_continuation"

    async def test_explicit_task_overrides_active(self, tmp_path: Path) -> None:
        # A new quick-action hint wins over the active task (priority).
        data = await self._handle(
            tmp_path, "anything", task_type="fill_form", active_task_type="ask_requirements"
        )
        assert data["task"]["task_type"] == "fill_form"
        assert data["task"]["method"] == "quick_action_selection"

    async def test_explicit_different_task_switches(self, tmp_path: Path) -> None:
        # A clearly-worded different task switches away from the active one (classifier wins).
        data = await self._handle(
            tmp_path, "Fill this form", active_task_type="ask_requirements"
        )
        assert data["task"]["task_type"] == "fill_form"

    async def test_cancel_clears_active_task(self, tmp_path: Path) -> None:
        data = await self._handle(
            tmp_path, "never mind", active_task_type="ask_requirements"
        )
        assert data["task"]["task_type"] == "general_docura_help"
        assert data["task"]["method"] == "task_cleared"

    async def test_no_active_task_uses_normal_classification(self, tmp_path: Path) -> None:
        # Without an active task, a plain follow-up is classified as before (unchanged behaviour).
        data = await self._handle(tmp_path, "Passport application")
        assert data["task"]["task_type"] == "unknown"
