"""Intent / task understanding — a controlled, replaceable seam.

The chatbot is task-oriented, not an open text generator: a message maps to one of a small,
controlled set of :class:`TaskType`s. ``IntentProvider`` is the seam; the only provider enabled
today is the transparent :class:`DeterministicIntentProvider` (keyword/phrase matching, no LLM,
no network, no guessing beyond what it can see). A future approved LLM provider drops in at
:func:`select_intent_provider` with no change to the orchestrator. Nothing here fabricates an
answer — an unrecognised message is honestly ``UNKNOWN``.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.core.config import Settings

INTENT_METHOD = "deterministic-keyword-v1"


class TaskType(StrEnum):
    ASK_REQUIREMENTS = "ask_requirements"
    CHECK_DOCUMENTS = "check_documents"
    CHECK_READINESS = "check_readiness"
    FILL_FORM = "fill_form"
    DOCUMENT_MATCH = "document_match"
    EXPLAIN_BLOCKER = "explain_blocker"
    GENERAL_DOCURA_HELP = "general_docura_help"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Intent:
    task_type: TaskType
    confidence: float
    entities: dict[str, str]
    reason: str
    method: str


@runtime_checkable
class IntentProvider(Protocol):
    @property
    def name(self) -> str: ...

    def classify(self, message: str, *, history: list[str] | None = None) -> Intent: ...


# Ordered rules: the FIRST task whose any phrase appears wins. Order encodes precedence
# (an explicit "fill" beats a generic "documents"). Data-driven — extend the phrase lists,
# not the control flow. Matching is on normalised, word-boundaried text; never fuzzy.
_RULES: list[tuple[TaskType, tuple[str, ...]]] = [
    (
        TaskType.FILL_FORM,
        ("fill this form", "fill the form", "fill it", "autofill", "fill in this", "fill form"),
    ),
    (
        TaskType.CHECK_READINESS,
        (
            "am i ready",
            "ready to fill",
            "do i have everything",
            "am i missing",
            "what is missing",
            "what's missing",
            "what am i missing",
            "ready to apply",
        ),
    ),
    (
        TaskType.EXPLAIN_BLOCKER,
        (
            "why can't docura",
            "why cant docura",
            "why did docura not",
            "why was this not filled",
            "why not filled",
            "explain why",
        ),
    ),
    (
        TaskType.DOCUMENT_MATCH,
        (
            "which document should i use",
            "which document should i",
            "which document do i use",
            "best document for",
        ),
    ),
    (
        TaskType.CHECK_DOCUMENTS,
        (
            "what documents do i have",
            "what documents do i already have",
            "which documents do i have",
            "my documents",
            "documents i have",
            "what do i already have",
            "what do i have",
        ),
    ),
    (
        TaskType.ASK_REQUIREMENTS,
        (
            "what documents do i need",
            "what do i need",
            "documents required",
            "requirements for",
            "what is required",
            "i need to create",
            "i need to apply",
            "apply for",
            "how do i get",
            "how to get",
        ),
    ),
    (
        TaskType.GENERAL_DOCURA_HELP,
        ("what can you do", "help", "how does docura", "what is docura", "hi", "hello", "hey"),
    ),
]

# Extract a coarse application name for ASK_REQUIREMENTS: the phrase after a lead-in verb.
_APPLICATION = re.compile(
    r"\b(?:need(?:\s+to\s+(?:create|make|get|apply\s+for))?|apply\s+for|create|make|get|requirements?\s+for)\b\s+(?:an?\s+|the\s+)?(?P<app>[a-z0-9][a-z0-9 /-]{1,60}?)(?:\?|\.|,|$|\s+what|\s+which|\s+do\b|\s+application\b)",  # noqa: E501
    re.IGNORECASE,
)


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


class DeterministicIntentProvider:
    """Transparent keyword/phrase classifier. No LLM, no network. It reports which phrase it
    matched (``reason``) so its decision is always inspectable, and returns ``UNKNOWN`` when it
    recognises nothing rather than guessing."""

    name = INTENT_METHOD

    def classify(self, message: str, *, history: list[str] | None = None) -> Intent:
        text = _normalize(message)
        for task, phrases in _RULES:
            hit = next((p for p in phrases if p in text), None)
            if hit is None:
                continue
            entities: dict[str, str] = {}
            if task is TaskType.ASK_REQUIREMENTS:
                match = _APPLICATION.search(message)
                if match:
                    app = _normalize(match.group("app"))
                    if app and app not in {"documents", "document", "form", "it"}:
                        entities["application"] = app
            return Intent(
                task_type=task,
                confidence=1.0,  # exact phrase match: certain about the MEANING, not the answer
                entities=entities,
                reason=f'Matched phrase "{hit}".',
                method=self.name,
            )
        return Intent(
            task_type=TaskType.UNKNOWN,
            confidence=0.0,
            entities={},
            reason="No known DOCURA task matched this message.",
            method=self.name,
        )


def select_intent_provider(settings: Settings) -> IntentProvider:
    """The active intent provider. When an LLM is configured (``settings.llm_configured``) the
    LLM provider is used *with the deterministic provider as its fallback*, so a failed or
    unavailable LLM degrades to deterministic understanding instead of fabricating. When no LLM
    is configured, the deterministic provider is used directly."""
    deterministic = DeterministicIntentProvider()
    if not settings.llm_configured:
        return deterministic
    from app.services.chatbot.llm import build_llm_intent_provider  # lazy: avoid import cycle

    return build_llm_intent_provider(settings, fallback=deterministic)
