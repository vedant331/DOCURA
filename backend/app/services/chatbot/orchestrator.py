"""Task orchestrator — decides what DOCURA should do for a message and composes the reply.

It runs intent understanding, then calls EXISTING domain services (record, documents) and the
requirements/readiness seams. It never mutates domain data, never fills a field, and never
submits a form: form filling stays in the approved extension/form-session flow, so a FILL_FORM
request returns an ACTION that points the user there (explicit activation, approval, no submit).
Every reply is a structured :class:`AssistantTurn` the API persists and the client renders.
"""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING, Any

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ConversationMessageType
from app.services.chatbot.intent import Intent, IntentProvider, TaskType, select_intent_provider
from app.services.chatbot.readiness import compute_readiness
from app.services.chatbot.requirements import (
    RequirementsProvider,
    RequirementStatus,
    build_requirements_provider,
)
from app.services.document_service import list_documents

if TYPE_CHECKING:
    from app.core.config import Settings


@dataclass(frozen=True, slots=True)
class AssistantTurn:
    message: str
    message_type: ConversationMessageType
    data: dict[str, Any]


def _task_block(intent: Intent) -> dict[str, Any]:
    return {
        "task_type": intent.task_type.value,
        "confidence": intent.confidence,
        "entities": intent.entities,
        "reason": intent.reason,
        "method": intent.method,
    }


class TaskOrchestrator:
    def __init__(
        self,
        *,
        intent_provider: IntentProvider,
        requirements_provider: RequirementsProvider,
    ) -> None:
        self._intent = intent_provider
        self._requirements = requirements_provider

    async def handle(self, db: AsyncSession, *, user_id: uuid.UUID, message: str) -> AssistantTurn:
        # classify may do blocking network I/O (LLM provider); keep the event loop free.
        intent = await asyncio.to_thread(self._intent.classify, message)
        task = intent.task_type
        if task is TaskType.ASK_REQUIREMENTS:
            return self._ask_requirements(intent)
        if task is TaskType.CHECK_DOCUMENTS:
            return await self._check_documents(db, user_id, intent)
        if task is TaskType.CHECK_READINESS:
            return await self._check_readiness(db, user_id, intent)
        if task is TaskType.FILL_FORM:
            return self._fill_form(intent)
        if task is TaskType.DOCUMENT_MATCH:
            return self._document_match(intent)
        if task is TaskType.EXPLAIN_BLOCKER:
            return self._explain_blocker(intent)
        if task is TaskType.GENERAL_DOCURA_HELP:
            return self._general_help(intent)
        return self._unknown(intent)

    # ---- handlers ----------------------------------------------------------------------
    def _ask_requirements(self, intent: Intent) -> AssistantTurn:
        rs = self._requirements.requirements_for(intent.entities.get("application"))
        block = {
            "application": rs.application,
            "status": rs.status.value,
            "source": rs.source,
            "retrieved_at": rs.retrieved_at.isoformat() if rs.retrieved_at else None,
            "note": rs.note,
            "documents": [asdict(i) for i in rs.documents],
            "information": [asdict(i) for i in rs.information],
        }
        if rs.status is RequirementStatus.VERIFIED:
            message = f"For {rs.application}, here is what is required."
        else:
            message = f"I can't list the requirements for {rs.application}: {rs.note}"
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.REQUIREMENTS,
            data={
                "task": _task_block(intent),
                "requirements": block,
                "actions": [{"type": "open_documents", "label": "Open documents"}],
                "needs_user_input": rs.status is not RequirementStatus.VERIFIED,
            },
        )

    async def _check_documents(
        self, db: AsyncSession, user_id: uuid.UUID, intent: Intent
    ) -> AssistantTurn:
        docs = await list_documents(db, user_id=user_id)
        listed = [{"filename": d.original_filename, "status": d.status.value} for d in docs]
        message = (
            "You haven't uploaded any documents yet."
            if not docs
            else f"You have {len(docs)} document{'s' if len(docs) != 1 else ''} in your vault."
        )
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.DOCUMENT_STATUS,
            data={
                "task": _task_block(intent),
                "documents": listed,
                "count": len(docs),
                "actions": [{"type": "view_documents", "label": "View documents"}],
                "needs_user_input": False,
            },
        )

    async def _check_readiness(
        self, db: AsyncSession, user_id: uuid.UUID, intent: Intent
    ) -> AssistantTurn:
        rs = self._requirements.requirements_for(intent.entities.get("application"))
        readiness = await compute_readiness(db, user_id=user_id, requirement_set=rs)
        block = {
            "application": readiness.application,
            "computable": readiness.computable,
            "ready": readiness.ready,
            "summary": readiness.summary,
            "items": [asdict(i) | {"status": i.status.value} for i in readiness.items],
            "note": readiness.note,
        }
        if not readiness.computable:
            message = "I can't check readiness yet: " + (
                readiness.note or "the application's requirements are unavailable."
            )
        elif readiness.ready:
            message = "You appear to have everything required — review before you submit."
        else:
            message = "You're not ready yet — some required items are missing or need review."
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.READINESS,
            data={
                "task": _task_block(intent),
                "readiness": block,
                "actions": [{"type": "view_documents", "label": "View documents"}],
                "needs_user_input": not readiness.computable or not readiness.ready,
            },
        )

    def _fill_form(self, intent: Intent) -> AssistantTurn:
        message = (
            "DOCURA fills forms through the browser extension on the page you activate — I can't "
            "fill from chat. Open the form, activate DOCURA, and it will fill only what it can do "
            "safely; sensitive fields still need your one-time approval, and DOCURA never submits "
            "the form for you."
        )
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.ACTION,
            data={
                "task": _task_block(intent),
                "actions": [
                    {"type": "open_form", "label": "Open the form"},
                    {"type": "start_form_session", "label": "Activate DOCURA on the form"},
                ],
                "needs_user_input": True,
            },
        )

    def _document_match(self, intent: Intent) -> AssistantTurn:
        message = (
            "Matching a document to a specific upload field isn't available yet: it needs "
            "document-type classification, which is blocked until the OCR evaluation (S-6) "
            "completes. You can still open your documents and choose one yourself."
        )
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.TEXT,
            data={
                "task": _task_block(intent),
                "actions": [{"type": "view_documents", "label": "View documents"}],
                "needs_user_input": False,
            },
        )

    def _explain_blocker(self, intent: Intent) -> AssistantTurn:
        message = (
            "DOCURA only automates what it is certain of. It leaves a field untouched when the "
            "information is unknown, asks you when more than one value is reasonable, surfaces a "
            "conflict when your documents disagree (it never picks one for you), and requires "
            "your explicit approval before disclosing a sensitive value. It never accepts "
            "declarations or consent for you, and never submits the form."
        )
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.TEXT,
            data={"task": _task_block(intent), "needs_user_input": False},
        )

    def _general_help(self, intent: Intent) -> AssistantTurn:
        message = (
            "I can help you work with your own documents: tell me what an application needs, "
            "what documents you already have, whether you're ready, or ask me to help fill a "
            "form. I use only information you've authorized, and DOCURA never submits a form."
        )
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.TEXT,
            data={"task": _task_block(intent), "needs_user_input": False},
        )

    def _unknown(self, intent: Intent) -> AssistantTurn:
        message = (
            "I didn't recognise that as a task I can help with. I understand a limited set of "
            "requests: what documents you need, what you already have, whether you're ready, or "
            "filling a form. Could you rephrase what you'd like to do?"
        )
        return AssistantTurn(
            message=message,
            message_type=ConversationMessageType.TEXT,
            data={"task": _task_block(intent), "needs_user_input": True},
        )


def build_orchestrator(settings: Settings) -> TaskOrchestrator:
    """Construct the orchestrator with the configured (today: deterministic) providers."""
    return TaskOrchestrator(
        intent_provider=select_intent_provider(settings),
        requirements_provider=build_requirements_provider(settings),
    )
