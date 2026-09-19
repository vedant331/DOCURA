"""Requirements provider — the authoritative-source seam.

DOCURA must NOT invent government/application requirements. ``RequirementsProvider`` is the
seam through which a configured, identifiable, authoritative source would supply a
:class:`RequirementSet`. The production default is :class:`UnconfiguredRequirementsProvider`,
which honestly reports ``UNAVAILABLE`` — it never fabricates requirements or a source. A real
integration (a configured retrieval mechanism) drops in at :func:`build_requirements_provider`
and must record its source and retrieval time, and mark stale/uncertain data as such.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from app.core.config import Settings


class RequirementStatus(StrEnum):
    VERIFIED = "verified"
    UNAVAILABLE = "unavailable"
    AMBIGUOUS = "ambiguous"
    STALE = "stale"


@dataclass(frozen=True, slots=True)
class RequirementItem:
    """One required item. ``kind`` is "document" or "information"; an information item may name
    the canonical attribute it maps to, so readiness can check it against the record."""

    label: str
    kind: str  # "document" | "information"
    optional: bool = False
    canonical_identifier: str | None = None


@dataclass(frozen=True, slots=True)
class RequirementSet:
    application: str
    status: RequirementStatus
    documents: tuple[RequirementItem, ...] = ()
    information: tuple[RequirementItem, ...] = ()
    source: str | None = None
    retrieved_at: datetime | None = None
    note: str = ""
    entities: dict[str, str] = field(default_factory=dict)


@runtime_checkable
class RequirementsProvider(Protocol):
    @property
    def name(self) -> str: ...

    def requirements_for(self, application: str | None) -> RequirementSet: ...


class UnconfiguredRequirementsProvider:
    """The honest default: no authoritative requirements source is configured, so DOCURA does
    not know an application's requirements and says so. It never invents documents, information,
    or a source (§9/§10)."""

    name = "unconfigured"

    def requirements_for(self, application: str | None) -> RequirementSet:
        return RequirementSet(
            application=(application or "").strip() or "unspecified application",
            status=RequirementStatus.UNAVAILABLE,
            source=None,
            retrieved_at=None,
            note=(
                "DOCURA has no configured authoritative source for application requirements, so "
                "it will not state what is required. Connect a verified requirements source to "
                "enable this."
            ),
        )


def build_requirements_provider(settings: Settings) -> RequirementsProvider:
    """Construct the configured requirements provider — the plug point.

    Returns the unconfigured provider (honest "unavailable") until a verified, identifiable
    external source is configured; that implementation drops in here with no change above it.
    """
    _ = settings
    return UnconfiguredRequirementsProvider()
