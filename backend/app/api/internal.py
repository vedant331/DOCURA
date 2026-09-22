"""Internal, secret-authenticated operations for an out-of-band scheduler.

The processing worker (Sprint 4 / decision D-09) is a long-running poll loop,
:mod:`app.worker`, and a serverless host (Vercel) has no process to run it. This
endpoint is the serverless-safe *trigger*: an external periodic caller invokes it, and
it drains a bounded number of already-queued jobs by calling the existing
:func:`app.services.processing.process_one` — the same claim/execute path the poll loop
uses. Only the trigger changes; ``processing_jobs``, :func:`claim_next_job`, and
``_execute`` are untouched, and ``POST /documents`` stays asynchronous (it still only
enqueues).

Authentication is a single shared secret compared in constant time, deliberately
separate from user sessions: the caller is a machine, not an account. It fails closed —
a deployment with no secret configured refuses (503), and a missing or wrong secret is
rejected (401), so no processing ever runs unauthenticated.
"""

from __future__ import annotations

import secrets
import time
from typing import Annotated

from fastapi import APIRouter, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from sqlalchemy import func, select

from app.core.config import Settings
from app.core.logging import get_logger
from app.db.models import JobState, ProcessingJob
from app.services.processing import process_one

logger = get_logger(__name__)

router = APIRouter(prefix="/internal", tags=["internal"])

# The credential travels in a dedicated header rather than the Authorization bearer used
# by user sessions, so the two auth schemes never collide.
_SECRET_HEADER = "X-Internal-Secret"  # noqa: S105 — a header name, not a secret value

# Bounds so one invocation cannot run unbounded on a function with a wall-clock limit:
# it stops after this many jobs or this many seconds, whichever comes first. The caller
# may lower the job count but never raise it past the ceiling.
_DEFAULT_MAX_JOBS = 10
_MAX_JOBS_CEILING = 100
_TIME_BUDGET_SECONDS = 25.0


class ProcessSummary(BaseModel):
    """What one trigger invocation did, safe to return to the scheduler."""

    processed: int = Field(description="Jobs run to completion in this invocation.")
    remaining: int = Field(description="Jobs still pending after this invocation.")
    budget_exhausted: bool = Field(
        description="True if the job or time bound stopped the run before the queue drained.",
    )


def _authenticate(settings: Settings, provided: str | None) -> None:
    """Refuse unless the caller presents the configured secret. Fails closed.

    An unconfigured deployment (no secret) cannot authenticate anyone, so it refuses
    with 503 rather than silently processing. A missing or wrong secret is a 401. The
    comparison is constant-time so a wrong secret leaks nothing through timing.
    """
    configured = settings.worker_trigger_secret
    if configured is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Processing trigger is not configured.",
        )
    expected = configured.get_secret_value()
    if not provided or not secrets.compare_digest(provided, expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing internal credential.",
        )


async def _count_pending(request: Request) -> int:
    """How many jobs are still waiting — a cheap signal for the scheduler to keep calling."""
    session_factory = request.app.state.session_factory
    async with session_factory() as db:
        count = await db.scalar(
            select(func.count())
            .select_from(ProcessingJob)
            .where(ProcessingJob.state == JobState.PENDING)
        )
    return int(count or 0)


@router.post(
    "/process",
    response_model=ProcessSummary,
    summary="Drain a bounded batch of processing jobs (scheduler trigger)",
    responses={
        401: {"description": "Missing or invalid internal credential."},
        503: {"description": "No trigger secret is configured on this deployment."},
    },
)
async def process_jobs(
    request: Request,
    x_internal_secret: Annotated[str | None, Header(alias=_SECRET_HEADER)] = None,
    max_jobs: int = _DEFAULT_MAX_JOBS,
) -> ProcessSummary:
    """Claim and run up to ``max_jobs`` queued jobs, then report progress.

    Each iteration is the existing :func:`process_one`, which opens its own short
    transaction and claims a single job with ``FOR UPDATE SKIP LOCKED`` — so several
    schedulers (or an overlapping call) can run this at once without ever taking the
    same job. The loop stops early when the queue is empty or the time budget is spent.
    """
    settings: Settings = request.app.state.settings
    _authenticate(settings, x_internal_secret)

    limit = max(1, min(max_jobs, _MAX_JOBS_CEILING))
    deadline = time.monotonic() + _TIME_BUDGET_SECONDS
    processed = 0
    budget_exhausted = False

    while processed < limit:
        if time.monotonic() >= deadline:
            budget_exhausted = True
            break
        worked = await process_one(
            request.app.state.session_factory,
            storage=request.app.state.document_storage,
            extractor=request.app.state.document_extractor,
            settings=settings,
            classifier=request.app.state.document_classifier,
            field_extractor=request.app.state.document_field_extractor,
        )
        if not worked:
            break
        processed += 1
    else:
        # Hit the job ceiling with the loop still willing to run — more may remain.
        budget_exhausted = True

    remaining = await _count_pending(request)
    logger.info(
        "internal.process_completed",
        processed=processed,
        remaining=remaining,
        budget_exhausted=budget_exhausted,
    )
    return ProcessSummary(
        processed=processed, remaining=remaining, budget_exhausted=budget_exhausted
    )
