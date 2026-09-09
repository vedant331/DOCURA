"""The extraction processing pipeline (Sprint 4 decision D-09, Option B).

A worker outside the request path (NFR-PERF-002) drives one document at a time
through its :class:`~app.db.models.DocumentStatus` states by executing the durable
:class:`~app.db.models.ProcessingJob` that was created with it. The design notes
that matter are recorded at D-09.4; the code here is their consequence:

* **Recoverable (NFR-REL-002).** A job is claimed with ``SELECT … FOR UPDATE SKIP
  LOCKED`` so two workers never take the same one, and a claim older than the
  configured timeout is treated as abandoned and reclaimed — a worker that dies
  mid-job strands nothing.
* **Bounded (D-09.4 note 2).** A failed attempt is retried until ``max_attempts``,
  after which the document becomes ``failed`` with a user-facing reason (FR-OCR-009).
* **Behind the D-01 seam.** The only extraction dependency is
  :class:`~app.services.extraction.DocumentExtractor`. No engine, field set,
  threshold, or tier is known here; with the unconfigured extractor in place the
  failure path is exercisable end to end and the success path is unreachable.

Claiming and executing are separate steps on purpose: the claim is a short write
that releases its row lock immediately, and the (real, future) engine work then runs
without holding a lock. Reprocessing (FR-OCR-010) lives with the owner-scoped
document logic in :mod:`app.services.document_service`, because it is gated on
ownership, not on worker state.
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.core.errors import DocuraError
from app.core.logging import get_logger
from app.db.models import (
    FAILURE_REASON_MAX_LENGTH,
    JOB_ERROR_MAX_LENGTH,
    Document,
    DocumentStatus,
    JobState,
    ProcessingJob,
)
from app.services.classification import DocumentClassifier
from app.services.extraction import DocumentExtractor
from app.services.extraction_store import build_extraction_run
from app.services.field_extraction import FieldExtractor, apply_field_extraction
from app.services.storage import DocumentStorage

logger = get_logger(__name__)


async def claim_next_job(
    db: AsyncSession, *, claim_timeout_seconds: int, now: datetime
) -> ProcessingJob | None:
    """Atomically take the next runnable job, or return ``None`` when there is none.

    Runnable means ``pending``, or ``claimed`` with a stale claim (a worker that
    never finished). ``SKIP LOCKED`` is what makes concurrent workers safe without a
    broker: a row another worker holds is skipped rather than waited on, so this
    returns the *next* free job or nothing, never a duplicate of one in flight.

    On success the job moves to ``claimed``, its attempt count rises, and the
    document moves to ``processing`` with any previous failure reason cleared — all
    in one committed transaction, so the claim is durable before execution begins.
    """
    stale_before = now - timedelta(seconds=claim_timeout_seconds)
    stmt = (
        select(ProcessingJob)
        .where(
            or_(
                ProcessingJob.state == JobState.PENDING,
                and_(
                    ProcessingJob.state == JobState.CLAIMED,
                    ProcessingJob.claimed_at < stale_before,
                ),
            )
        )
        .order_by(ProcessingJob.created_at)
        .limit(1)
        .with_for_update(skip_locked=True)
    )
    job = await db.scalar(stmt)
    if job is None:
        # Nothing to do. Let the session close and release the empty transaction.
        return None

    job.state = JobState.CLAIMED
    job.claimed_at = now
    job.attempts += 1

    document = await db.get(Document, job.document_id)
    if document is None:  # pragma: no cover - FK + delete-orphan make this impossible
        # The job cannot outlive its document (ON DELETE CASCADE). If it somehow has,
        # the job is meaningless: drop it rather than loop on a phantom.
        await db.delete(job)
        await db.commit()
        return None
    document.status = DocumentStatus.PROCESSING
    document.failure_reason = None

    await db.commit()
    logger.info("processing.claimed", document_ref=str(job.document_id), attempt=job.attempts)
    return job


def _record_failure(job: ProcessingJob, document: Document, exc: DocuraError) -> None:
    """Apply the outcome of a failed attempt: retry if attempts remain, else fail.

    The document carries only the safe ``detail`` (FR-OCR-009's "state what failed");
    the internal class-and-message stays on the job (NFR-ERR-004).
    """
    job.last_error = f"{type(exc).__name__}: {exc.detail}"[:JOB_ERROR_MAX_LENGTH]
    if job.attempts >= job.max_attempts:
        job.state = JobState.FAILED
        document.status = DocumentStatus.FAILED
        document.failure_reason = exc.detail[:FAILURE_REASON_MAX_LENGTH]
    else:
        # Return it to the queue for another worker (or this one) to pick up.
        job.state = JobState.PENDING
        job.claimed_at = None
        document.status = DocumentStatus.QUEUED


async def _execute(
    db: AsyncSession,
    job: ProcessingJob,
    *,
    storage: DocumentStorage,
    extractor: DocumentExtractor,
    classifier: DocumentClassifier | None,
    field_extractor: FieldExtractor | None,
) -> None:
    """Run one claimed job: read the original, extract, and record the outcome.

    Only :class:`DocuraError` is caught — that is the honest-failure surface the
    extractor and storage promise (FR-OCR-009, BR-016). Anything else is a bug and is
    left to propagate to the worker loop, which logs it and moves on; the job stays
    ``claimed`` and is reclaimed once its claim goes stale, so nothing is lost.
    """
    document = await db.get(Document, job.document_id)
    if document is None:  # pragma: no cover - see claim_next_job
        return

    try:
        handle = storage.open(document.storage_key)
        try:
            # The port is synchronous (extraction is CPU-bound). With a real engine
            # this call would belong in a thread; the unconfigured extractor returns
            # immediately, so that is deferred until an engine is chosen (D-01).
            result = extractor.extract(handle, content_type=document.content_type)
        finally:
            handle.close()
    except DocuraError as exc:
        _record_failure(job, document, exc)
        await db.commit()
        logger.info(
            "processing.failed",
            document_ref=str(document.id),
            attempt=job.attempts,
            terminal=job.state == JobState.FAILED,
        )
        return

    # Persist the result and mark the document ready in one commit: the document is
    # `ready` if and only if its extraction run is stored. A reprocess adds a new run
    # rather than replacing an old one, so history is retained.
    run = build_extraction_run(document_id=document.id, result=result)
    db.add(run)
    if classifier is not None:
        # Classify before field extraction, so a future document-type-aware field
        # extractor can read the assigned type off the document. The type is written to
        # the existing column (no new state); today the model abstains, so it stays
        # UNCLASSIFIED. Classification confidence is not persisted — nothing consumes it
        # yet, and inventing a column for it would be speculative.
        document.document_type = classifier.classify(run).document_type
    if field_extractor is not None:
        # Field extraction (blocks → attribute candidates) runs in the same commit as
        # its run, so a run and its observations are true together or not at all. It is
        # flushed first so candidates can point at real block ids. When no field
        # extractor is configured this is skipped and the run persists exactly as before.
        await db.flush()
        await apply_field_extraction(db, run=run, extractor=field_extractor)
    job.state = JobState.SUCCEEDED
    document.status = DocumentStatus.READY
    document.failure_reason = None
    await db.commit()
    logger.info(
        "processing.succeeded",
        document_ref=str(document.id),
        engine=result.engine,
        pages=result.page_count,
    )


async def process_one(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    storage: DocumentStorage,
    extractor: DocumentExtractor,
    settings: Settings,
    classifier: DocumentClassifier | None = None,
    field_extractor: FieldExtractor | None = None,
) -> bool:
    """Claim and run at most one job. Returns whether one was processed.

    The unit the worker loop repeats, and the unit the tests drive directly. A fresh
    session is opened so the claim's transaction is short and self-contained.
    ``classifier`` and ``field_extractor`` are both optional: without either the pipeline
    persists the run and nothing more, exactly as before, so the extraction infrastructure
    is testable on its own.
    """
    now = datetime.now(UTC)
    async with session_factory() as db:
        job = await claim_next_job(
            db, claim_timeout_seconds=settings.worker_claim_timeout_seconds, now=now
        )
        if job is None:
            return False
        await _execute(
            db,
            job,
            storage=storage,
            extractor=extractor,
            classifier=classifier,
            field_extractor=field_extractor,
        )
    return True


async def run_worker(
    session_factory: async_sessionmaker[AsyncSession],
    *,
    storage: DocumentStorage,
    extractor: DocumentExtractor,
    settings: Settings,
    classifier: DocumentClassifier | None = None,
    field_extractor: FieldExtractor | None = None,
    stop: asyncio.Event | None = None,
) -> None:
    """Poll for work until asked to stop.

    Polling is the correctness floor (a `LISTEN/NOTIFY` wake-up would only be an
    optimisation, D-09.2). ``stop`` lets a test — or a signal handler — end the loop
    cleanly; without one it runs until the process is killed.
    """
    logger.info("worker.started", poll_interval_seconds=settings.worker_poll_interval_seconds)
    while stop is None or not stop.is_set():
        try:
            worked = await process_one(
                session_factory,
                storage=storage,
                extractor=extractor,
                settings=settings,
                classifier=classifier,
                field_extractor=field_extractor,
            )
        except Exception:
            # One bad job must not kill the worker. The job stays claimed and is
            # reclaimed once its claim goes stale, so nothing is lost.
            logger.exception("worker.iteration_failed")
            worked = False
        if not worked:
            await asyncio.sleep(settings.worker_poll_interval_seconds)
    logger.info("worker.stopped")
