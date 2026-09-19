"""Readiness engine — requirements x the user's own record/documents.

Deterministic and honest. Given a VERIFIED requirement set, it computes per-item status against
the user's structured record (reusing :func:`build_current_record`) and document vault (reusing
:func:`list_documents`). It reuses DOCURA's safety semantics directly: a value the record marks
ambiguous/conflicting becomes NEEDS_REVIEW (never auto-resolved), an item with no way to verify
stays UNKNOWN (never guessed), and no raw value is exposed — a satisfied item references the
canonical attribute id, not its value.
"""

from __future__ import annotations

import uuid
from collections import Counter
from dataclasses import dataclass
from enum import StrEnum

from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chatbot.requirements import RequirementSet, RequirementStatus
from app.services.current_record import build_current_record
from app.services.document_service import list_documents


class ReadinessStatus(StrEnum):
    AVAILABLE = "available"
    MISSING = "missing"
    NEEDS_REVIEW = "needs_review"
    NEEDS_APPROVAL = "needs_approval"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ReadinessItem:
    requirement: str
    kind: str  # "document" | "information"
    status: ReadinessStatus
    optional: bool
    reference: str | None  # canonical id or a document reference — never a value
    note: str


@dataclass(frozen=True, slots=True)
class Readiness:
    application: str
    computable: bool  # False when requirements are not VERIFIED
    items: tuple[ReadinessItem, ...]
    summary: dict[str, int]
    ready: bool
    note: str


async def compute_readiness(
    db: AsyncSession, *, user_id: uuid.UUID, requirement_set: RequirementSet
) -> Readiness:
    if requirement_set.status is not RequirementStatus.VERIFIED:
        return Readiness(
            application=requirement_set.application,
            computable=False,
            items=(),
            summary={},
            ready=False,
            note=(
                "Readiness cannot be computed: the application's requirements are "
                f"{requirement_set.status.value} (DOCURA will not guess them)."
            ),
        )

    record = {c.canonical_identifier: c for c in await build_current_record(db, user_id=user_id)}
    documents = await list_documents(db, user_id=user_id)
    have_documents = len(documents) > 0

    items: list[ReadinessItem] = []

    for info in requirement_set.information:
        if info.canonical_identifier is None:
            items.append(
                ReadinessItem(
                    info.label,
                    "information",
                    ReadinessStatus.UNKNOWN,
                    info.optional,
                    None,
                    "No canonical mapping for this item — DOCURA cannot verify it.",
                )
            )
            continue
        current = record.get(info.canonical_identifier)
        if current is None:
            items.append(
                ReadinessItem(
                    info.label,
                    "information",
                    ReadinessStatus.MISSING,
                    info.optional,
                    info.canonical_identifier,
                    "Not on record yet.",
                )
            )
        elif current.is_ambiguous:
            items.append(
                ReadinessItem(
                    info.label,
                    "information",
                    ReadinessStatus.NEEDS_REVIEW,
                    info.optional,
                    info.canonical_identifier,
                    "More than one value on record — needs your review.",
                )
            )
        elif current.value is not None:
            items.append(
                ReadinessItem(
                    info.label,
                    "information",
                    ReadinessStatus.AVAILABLE,
                    info.optional,
                    info.canonical_identifier,
                    "",
                )
            )
        else:
            items.append(
                ReadinessItem(
                    info.label,
                    "information",
                    ReadinessStatus.MISSING,
                    info.optional,
                    info.canonical_identifier,
                    "Not on record yet.",
                )
            )

    for doc in requirement_set.documents:
        if not have_documents:
            items.append(
                ReadinessItem(
                    doc.label,
                    "document",
                    ReadinessStatus.MISSING,
                    doc.optional,
                    None,
                    "No documents uploaded yet.",
                )
            )
        else:
            # Document-type classification is not available (S-6/OCR blocked), so DOCURA cannot
            # assert that a specific required type is present — it stays UNKNOWN, never guessed.
            items.append(
                ReadinessItem(
                    doc.label,
                    "document",
                    ReadinessStatus.UNKNOWN,
                    doc.optional,
                    None,
                    "DOCURA cannot yet verify document types; check your vault.",
                )
            )

    summary = dict(Counter(item.status.value for item in items))
    required = [i for i in items if not i.optional]
    ready = bool(required) and all(i.status is ReadinessStatus.AVAILABLE for i in required)
    return Readiness(
        application=requirement_set.application,
        computable=True,
        items=tuple(items),
        summary=summary,
        ready=ready,
        note="",
    )
