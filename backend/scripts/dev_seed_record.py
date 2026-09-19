"""ONE-OFF LOCAL DEV SEED — manual autofill testing only. NOT a production path.

Populates ONE local/test user's structured record with exactly two RELEASED canonical
attributes, so the already-implemented M10/M13/M16 autofill flow can be tested manually
while real OCR/S-6 is unavailable. It does this the honest way — through the EXISTING
record architecture (Document -> ExtractionRun -> ExtractionPage/Block ->
AttributeObservation) using the EXISTING service helpers — so the values surface through
the normal GET /record/attributes derivation, not a faked API response.

It does NOT implement OCR, add an API, add attributes, or change any architecture. The
run is clearly marked engine="dev-manual-seed" (not a fabricated OCR engine). Run from
backend/ with the dev .env in place:

    .venv/Scripts/python.exe -m scripts.dev_seed_record

Re-running is idempotent: it reuses its own seed document and adds a newer run (newest run
wins), so the record shows the same two values without piling up documents.
"""

from __future__ import annotations

import asyncio
import hashlib
import io

from sqlalchemy import select

from app.core.config import Settings
from app.core.errors import DuplicateDocumentError
from app.db.models import Document, User
from app.db.session import create_engine, create_session_factory
from app.services.attribute_observation import CandidateObservation, build_attribute_observations
from app.services.current_record import build_current_record
from app.services.document_service import store_document
from app.services.extraction import ExtractedPage, ExtractionResult, TextBlock
from app.services.extraction_store import build_extraction_run
from app.services.storage import build_document_storage

# The single local test user to target. No other user's data is touched.
TARGET_EMAIL = "vedantskadam24@gmail.com"

# Exactly the two RELEASED controlled attributes (v0.2-draft). Nothing else.
SEED_VALUES: list[tuple[str, str]] = [
    ("person.full_name", "Vedant Santosh Kadam"),
    ("person.date_of_birth", "2007-03-24"),
]

# Clearly a development seed, never a real OCR result (marks ExtractionRun.engine).
SEED_FILENAME = "DEV-MANUAL-SEED.pdf"
SEED_ENGINE = "dev-manual-seed"
SEED_ENGINE_VERSION = "manual-test"
# Smallest bytes that pass upload validation (magic `%PDF-`), so the seed document is a
# real vault document created through the normal store_document path.
MIN_PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"


async def _seed() -> int:
    settings = Settings()
    engine = create_engine(settings)
    factory = create_session_factory(engine)
    storage = build_document_storage(settings)
    try:
        async with factory() as db:
            user = await db.scalar(select(User).where(User.email == TARGET_EMAIL))
            if user is None:
                print(f"ABORT: no user {TARGET_EMAIL!r} exists. Register via the frontend first.")
                print("No data was changed.")
                return 2

            # Find-or-create THIS script's own seed document (so re-runs don't duplicate it
            # and no other document is disturbed).
            doc = await db.scalar(
                select(Document).where(
                    Document.user_id == user.id,
                    Document.original_filename == SEED_FILENAME,
                )
            )
            if doc is None:
                try:
                    doc = await store_document(
                        db,
                        owner=user,
                        source=io.BytesIO(MIN_PDF),
                        filename=SEED_FILENAME,
                        declared_content_type="application/pdf",
                        storage=storage,
                        settings=settings,
                    )
                except DuplicateDocumentError:
                    doc = await db.scalar(
                        select(Document).where(
                            Document.user_id == user.id,
                            Document.checksum_sha256 == hashlib.sha256(MIN_PDF).hexdigest(),
                        )
                    )
            if doc is None:
                print("ABORT: could not create or find the seed document. No data changed.")
                return 1

            # Build one run (clearly a dev seed) carrying one block per attribute, then the
            # observations that name each block AS its canonical attribute — reusing the
            # exact service helpers the pipeline and tests use.
            result = ExtractionResult(
                pages=(
                    ExtractedPage(
                        number=1,
                        text="dev seed page",
                        confidence=None,
                        blocks=tuple(
                            TextBlock(text=value, confidence=None) for _, value in SEED_VALUES
                        ),
                    ),
                ),
                engine=SEED_ENGINE,
                engine_version=SEED_ENGINE_VERSION,
                metadata={"source": "dev-manual-seed", "note": "not an OCR result"},
            )
            run = build_extraction_run(document_id=doc.id, result=result)
            db.add(run)
            await db.flush()
            blocks = run.pages[0].blocks
            candidates = [
                CandidateObservation(
                    canonical_identifier=identifier,
                    value=blocks[i].text,
                    source_block=blocks[i],
                    confidence=blocks[i].confidence,
                )
                for i, (identifier, _value) in enumerate(SEED_VALUES)
            ]
            db.add_all(build_attribute_observations(run=run, candidates=candidates))
            await db.commit()

            # Verify through the SAME derivation the API uses.
            record = await build_current_record(db, user_id=user.id)
            print(f"Seeded record for {TARGET_EMAIL} (user {user.id})")
            print(f"  document {doc.id}, run {run.id}:")
            for value in record:
                print(
                    f"  {value.canonical_identifier} = {value.value!r} "
                    f"(ambiguous={value.is_ambiguous})"
                )
            return 0
    finally:
        await engine.dispose()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_seed()))
