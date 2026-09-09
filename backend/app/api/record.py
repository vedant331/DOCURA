"""Current-record retrieval endpoints (Sprint 4, fifth milestone).

The retrieval boundary between the derived structured-record layer
(:mod:`app.services.current_record`) and the future chatbot/voice and browser-extension
clients. It answers, for the authenticated user only: *what is the current value of this
canonical attribute, with what support?* — after a client has already translated a
natural-language request into a canonical identifier. There is no natural-language
parsing, no retrieval ranking, and no AI here.

Documents are **not** re-exposed: a value's provenance carries ``document_id``, and the
client fetches the file through the existing vault (``GET /documents/{id}`` / ``/content``),
which already enforces the same per-user ownership. Identity comes from the session, never
from the path — a caller has no way to name another account, exactly as in the vault.
"""

from __future__ import annotations

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.core.errors import AttributeNotFoundError
from app.db.models import AttributeObservation
from app.schemas.record import (
    AttributeRecordResponse,
    AttributeValueResponse,
    SourceRegionResponse,
    SupportingObservationResponse,
)
from app.services.current_record import (
    CurrentAttributeValue,
    build_current_record,
    get_current_value,
)

router = APIRouter(prefix="/record", tags=["record"])


def _region(observation: AttributeObservation) -> SourceRegionResponse | None:
    block = observation.source_block
    x, y, w, h = block.region_x, block.region_y, block.region_width, block.region_height
    # All four are present together or all NULL; checking each narrows the type too.
    if x is None or y is None or w is None or h is None:
        return None
    return SourceRegionResponse(x=x, y=y, width=w, height=h)


def _observation(observation: AttributeObservation) -> SupportingObservationResponse:
    """Project one observation onto its public shape — provenance, never file content.

    The chain (block → page → run) is eager-loaded by the service, so this only reads
    already-loaded attributes.
    """
    run = observation.source_block.page.run
    return SupportingObservationResponse(
        value=observation.value,
        confidence=observation.confidence,
        document_id=run.document_id,
        extraction_run_id=run.id,
        page_number=observation.source_block.page.number,
        region=_region(observation),
    )


def _to_response(value: CurrentAttributeValue) -> AttributeValueResponse:
    return AttributeValueResponse(
        canonical_identifier=value.canonical_identifier,
        value=value.value,
        is_ambiguous=value.is_ambiguous,
        observations=[_observation(o) for o in value.observations],
    )


@router.get(
    "/attributes",
    response_model=AttributeRecordResponse,
    summary="This account's current structured record",
)
async def read_record(user: CurrentUser, db: DbSession) -> AttributeRecordResponse:
    """Every canonical attribute the account has a value for, scoped to the session.

    Derived on read from observation history; disagreement is surfaced as ambiguity,
    never resolved. A client prefetching what DOCURA knows reads one shape here.
    """
    record = await build_current_record(db, user_id=user.id)
    return AttributeRecordResponse(
        attributes=[_to_response(value) for value in record],
        count=len(record),
    )


@router.get(
    "/attributes/{canonical_identifier}",
    response_model=AttributeValueResponse,
    summary="The current value of one canonical attribute",
)
async def read_attribute(
    canonical_identifier: str, user: CurrentUser, db: DbSession
) -> AttributeValueResponse:
    """One attribute's current value for the account, or 404.

    Scoped to ``user.id`` from the session, so another account's value is unreachable and
    answers the same 404 as an identifier DOCURA has no value for — neither confirms the
    other account holds it (NFR-SEC-003, NFR-PRIV-002).
    """
    value = await get_current_value(
        db, user_id=user.id, canonical_identifier=canonical_identifier
    )
    if value is None:
        raise AttributeNotFoundError
    return _to_response(value)
