"""Processing worker entrypoint (Sprint 4 decision D-09).

A separate long-running process from the API, so document processing load grows
independently of interactive traffic (NFR-SCL-002). It shares the application's
configuration, database, storage, and extraction seam — it simply drives them from
outside the request path instead of from within it.

Run it alongside the API:

    python -m app.worker

It fails the same way the API does when configuration is missing (exit 78), and it
stops cleanly on SIGINT/SIGTERM so an in-flight claim is the only thing a restart
has to recover — and that recovery is automatic (NFR-REL-002).
"""

from __future__ import annotations

import asyncio
import signal
import sys

from app.core.config import ConfigurationError, Settings, load_settings
from app.core.logging import configure_logging, get_logger
from app.db.session import create_engine, create_session_factory, dispose_engine
from app.services.classification import build_document_classifier
from app.services.extraction import build_document_extractor
from app.services.field_extraction import build_field_extractor
from app.services.processing import run_worker
from app.services.storage import build_document_storage

logger = get_logger(__name__)


async def _serve(settings: Settings) -> None:
    """Build the worker's dependencies, run until signalled, and tear down."""
    engine = create_engine(settings)
    session_factory = create_session_factory(engine)
    storage = build_document_storage(settings)
    # The same builder the API uses (D-01): whatever engine is installed, or the
    # unconfigured extractor that refuses honestly while none is.
    extractor = build_document_extractor(settings)
    # The classification seam (D-02). Abstains until a model is selected, so today it
    # only ever assigns UNCLASSIFIED — and only on the success path, which the
    # unconfigured extractor never reaches.
    classifier = build_document_classifier()
    # The field-extraction seam (blocks → attribute candidates). Engine-neutral, so it
    # is usable whatever OCR engine D-01 selects; today it only runs on the success path,
    # which the unconfigured extractor never reaches.
    field_extractor = build_field_extractor()

    stop = asyncio.Event()
    loop = asyncio.get_running_loop()
    for signame in ("SIGINT", "SIGTERM"):
        sig = getattr(signal, signame, None)
        if sig is not None:
            try:
                loop.add_signal_handler(sig, stop.set)
            except NotImplementedError:  # pragma: no cover - Windows has no add_signal_handler
                signal.signal(sig, lambda *_: stop.set())

    logger.info("worker.starting", environment=settings.environment.value)
    try:
        await run_worker(
            session_factory,
            storage=storage,
            extractor=extractor,
            settings=settings,
            classifier=classifier,
            field_extractor=field_extractor,
            stop=stop,
        )
    finally:
        await dispose_engine(engine)


def main() -> None:
    """Console entrypoint: load config, fail clearly, otherwise process."""
    try:
        settings = load_settings()
    except ConfigurationError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        raise SystemExit(78) from None  # EX_CONFIG

    configure_logging(settings)
    asyncio.run(_serve(settings))


if __name__ == "__main__":
    main()
