"""Sprint 4 (fourth milestone) — the user's current structured record.

These tests prove the smallest derived view over attribute-observation history: for a
user, the current known value of a canonical attribute, its supporting observation(s),
user isolation, and — crucially — that genuine disagreement is exposed as ambiguity
rather than silently resolved (G-20 is unresolved). Values that agree under the approved
N-TEXT normalisation are one value, not a conflict.

The one approved ``v0.1-draft`` identifier ``person.full_name`` is the fixture, read from
configuration. Using it is not approval of the G-12 field set — it is the only approved
entry, used solely to exercise the model.

Needs a real PostgreSQL (native UUID); skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

try:  # stdlib on the project's Python 3.12
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

from app.core.config import Settings
from app.db.models import User
from app.db.session import create_session_factory
from app.services import processing
from app.services.attribute_observation import (
    CandidateObservation,
    build_attribute_observations,
    list_attribute_observations,
)
from app.services.current_record import (
    CurrentAttributeValue,
    build_current_record,
    get_current_value,
)
from app.services.document_service import store_document
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    UnconfiguredExtractor,
)
from app.services.extraction_store import build_extraction_run
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import PDF_BYTES, pdf_bytes, requires_postgres

pytestmark = requires_postgres

_VOCAB_PATH = (
    Path(__file__).resolve().parents[1]
    / "config"
    / "vocabulary"
    / "canonical_attributes.v0.2-draft.toml"
)


def _person_full_name_identifier() -> str:
    with _VOCAB_PATH.open("rb") as handle:
        data = tomllib.load(handle)
    return str(data["attribute"][0]["canonical_identifier"])


PERSON_FULL_NAME = _person_full_name_identifier()


def _result(name: str, *, version: str, confidence: float | None) -> ExtractionResult:
    """A one-page, one-block synthetic result carrying ``name`` (the bytes are ignored)."""
    return ExtractionResult(
        pages=(
            ExtractedPage(
                number=1,
                text="page one",
                confidence=None,
                blocks=(TextBlock(text=name, confidence=confidence),),
            ),
        ),
        engine="deterministic-test-double",
        engine_version=version,
        metadata={},
    )


@pytest.fixture
def session_factory(db_engine: Any) -> async_sessionmaker[AsyncSession]:
    return create_session_factory(db_engine)


@pytest.fixture
def storage(db_settings: Settings) -> DocumentStorage:
    return build_document_storage(db_settings)


async def _seed_document(
    session_factory: async_sessionmaker[AsyncSession],
    storage: DocumentStorage,
    settings: Settings,
    *,
    email: str = "record@example.com",
    content: bytes = PDF_BYTES,
) -> Any:
    from sqlalchemy import select

    async with session_factory() as db:
        # Look up or create: a test may seed two documents for the same owner, and the
        # unique index on users.email forbids a second insert.
        user = await db.scalar(select(User).where(User.email == email))
        if user is None:
            user = User(email=email, password_hash="argon2-hash-unused")
            db.add(user)
            await db.commit()
        return await store_document(
            db,
            owner=user,
            source=io.BytesIO(content),
            filename="marksheet.pdf",
            declared_content_type="application/pdf",
            storage=storage,
            settings=settings,
        )


async def _persist_run_with_name(
    session_factory: async_sessionmaker[AsyncSession],
    document_id: Any,
    *,
    name: str,
    version: str = "1.0",
    confidence: float | None = 0.9,
    identifier: str = PERSON_FULL_NAME,
) -> Any:
    """Persist a run and one observation (run + observation atomic in one commit)."""
    async with session_factory() as db:
        run = build_extraction_run(
            document_id=document_id, result=_result(name, version=version, confidence=confidence)
        )
        db.add(run)
        await db.flush()
        block = run.pages[0].blocks[0]
        db.add_all(
            build_attribute_observations(
                run=run,
                candidates=[
                    CandidateObservation(
                        canonical_identifier=identifier,
                        value=block.text,
                        source_block=block,
                        confidence=block.confidence,
                    )
                ],
            )
        )
        await db.commit()
        return run.id


class TestSingleValue:
    async def test_one_observation_produces_a_current_value(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_name(session_factory, document.id, name="Priya Sharma")

        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        assert value.canonical_identifier == PERSON_FULL_NAME == "person.full_name"
        assert value.value == "Priya Sharma"
        assert value.is_ambiguous is False
        assert len(value.observations) == 1
        # Confidence is retained on the supporting observation, not synthesised.
        assert value.observations[0].confidence == pytest.approx(0.9)

    async def test_unknown_attribute_returns_none(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_name(session_factory, document.id, name="Priya Sharma")

        async with session_factory() as db:
            assert (
                await get_current_value(
                    db, user_id=document.user_id, canonical_identifier="person.date_of_birth"
                )
                is None
            )


class TestAgreementUnderApprovedNormalisation:
    async def test_values_agreeing_under_n_text_are_one_value_not_a_conflict(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """Two documents, the name differing only in casing/whitespace — N-TEXT: one value."""
        doc_a = await _seed_document(
            session_factory, storage, db_settings, content=pdf_bytes(b"A")
        )
        doc_b = await _seed_document(
            session_factory, storage, db_settings, content=pdf_bytes(b"B")
        )
        await _persist_run_with_name(session_factory, doc_a.id, name="Priya Sharma")
        await _persist_run_with_name(session_factory, doc_b.id, name="priya   sharma")

        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=doc_a.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        assert value.is_ambiguous is False
        # Both observations support it; the raw form of the first is shown (N-TEXT rule 4).
        assert len(value.observations) == 2
        assert value.value == "Priya Sharma"


class TestAmbiguity:
    async def test_genuinely_conflicting_values_are_exposed_not_resolved(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """Two documents disagree on the name — no approved precedence, so ambiguity."""
        doc_a = await _seed_document(
            session_factory, storage, db_settings, content=pdf_bytes(b"A")
        )
        doc_b = await _seed_document(
            session_factory, storage, db_settings, content=pdf_bytes(b"B")
        )
        await _persist_run_with_name(session_factory, doc_a.id, name="Priya Sharma")
        await _persist_run_with_name(session_factory, doc_b.id, name="Riya Verma")

        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=doc_a.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        # No winner is chosen; both candidates stay visible for the caller to resolve.
        assert value.is_ambiguous is True
        assert value.value is None
        assert {o.value for o in value.observations} == {"Priya Sharma", "Riya Verma"}


class TestWholeRecordAndUserIsolation:
    async def test_build_current_record_is_scoped_to_the_user(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        mine = await _seed_document(
            session_factory, storage, db_settings, email="mine@example.com"
        )
        theirs = await _seed_document(
            session_factory, storage, db_settings, email="theirs@example.com"
        )
        await _persist_run_with_name(session_factory, mine.id, name="Priya Sharma")
        # Another user's document disagrees — it must not leak in, and must not create
        # a false ambiguity for me.
        await _persist_run_with_name(session_factory, theirs.id, name="Someone Else")

        async with session_factory() as db:
            record = await build_current_record(db, user_id=mine.user_id)
        assert len(record) == 1
        entry = record[0]
        assert entry.canonical_identifier == PERSON_FULL_NAME
        # Isolation: the other user's differing value neither leaks in nor forces a
        # false ambiguity — the record is my single value alone.
        assert entry.value == "Priya Sharma"
        assert entry.is_ambiguous is False
        assert len(entry.observations) == 1

    async def test_other_users_observations_never_appear(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        mine = await _seed_document(
            session_factory, storage, db_settings, email="a@example.com"
        )
        theirs = await _seed_document(
            session_factory, storage, db_settings, email="b@example.com"
        )
        await _persist_run_with_name(session_factory, theirs.id, name="Someone Else")

        async with session_factory() as db:
            # I have no observations of my own.
            assert await build_current_record(db, user_id=mine.user_id) == []
            assert (
                await get_current_value(
                    db, user_id=mine.user_id, canonical_identifier=PERSON_FULL_NAME
                )
                is None
            )


class TestSupersessionAndRebuild:
    async def test_a_newer_run_supersedes_the_view_while_history_survives(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        """A newer run of the SAME document is current; the older run's value is history."""
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_name(
            session_factory, document.id, name="Priya Sharma", version="1.0"
        )

        async with session_factory() as db:
            before = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert before is not None
        assert before.value == "Priya Sharma"

        # Reprocess: a newer run reads a corrected name.
        await _persist_run_with_name(
            session_factory, document.id, name="Priya Verma", version="2.0"
        )

        async with session_factory() as db:
            after = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
            everything = await list_attribute_observations(db, document_id=document.id)
        # The derived view rebuilds on read: current is the newest run, not ambiguous.
        assert after is not None
        assert after.value == "Priya Verma"
        assert after.is_ambiguous is False
        assert len(after.observations) == 1
        # History is intact: both runs' observations still exist.
        assert {o.value for o in everything} == {"Priya Sharma", "Priya Verma"}

    async def test_failed_extraction_adds_no_current_value(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        settings = db_settings.model_copy(update={"worker_max_attempts": 1})
        document = await _seed_document(session_factory, storage, settings)
        await _persist_run_with_name(session_factory, document.id, name="Priya Sharma")

        # A failed extraction persists no run, so it can add no observation and cannot
        # change the derived view.
        await processing.process_one(
            session_factory, storage=storage, extractor=UnconfiguredExtractor(), settings=settings
        )

        async with session_factory() as db:
            value = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
        assert value is not None
        assert value.value == "Priya Sharma"
        assert len(value.observations) == 1


class TestNoFileMetadata:
    async def test_current_value_carries_no_file_metadata(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        document = await _seed_document(session_factory, storage, db_settings)
        await _persist_run_with_name(session_factory, document.id, name="Priya Sharma")

        # Structural: the derived value has no file-metadata fields of its own.
        assert set(CurrentAttributeValue.__dataclass_fields__) == {
            "canonical_identifier",
            "value",
            "is_ambiguous",
            "observations",
        }

        async with session_factory() as db:
            reloaded_value = await get_current_value(
                db, user_id=document.user_id, canonical_identifier=PERSON_FULL_NAME
            )
            reloaded_doc = await db.get(type(document), document.id)
        assert reloaded_value is not None
        assert reloaded_doc is not None
        blob = (reloaded_value.value or "") + reloaded_value.canonical_identifier
        assert reloaded_doc.storage_key not in blob
        assert reloaded_doc.original_filename not in blob
        assert reloaded_doc.checksum_sha256 not in blob
