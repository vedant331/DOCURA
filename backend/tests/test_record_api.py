"""Sprint 4 (fifth milestone) — the current-record retrieval API.

These tests exercise the retrieval boundary the future chatbot/voice and browser-extension
clients call *after* translating a request into a canonical identifier: the current value
of an attribute, its ambiguity state, its supporting provenance and confidence — scoped to
the authenticated user, and reusing the existing document vault for the files themselves.

Observations have no creation endpoint yet (the block→attribute mapping is G-12, unbuilt),
so they are seeded directly against a document that was uploaded through the real API.
``person.full_name`` is the only vocabulary-dependent fixture, read from configuration.

Needs a real PostgreSQL (native UUID); skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

try:  # stdlib on the project's Python 3.12
    import tomllib
except ModuleNotFoundError:  # pragma: no cover
    import tomli as tomllib  # type: ignore[no-redef]

from app.core.config import Settings
from app.services import processing
from app.services.attribute_observation import (
    CandidateObservation,
    build_attribute_observations,
    list_attribute_observations,
)
from app.services.extraction import (
    ExtractedPage,
    ExtractionResult,
    TextBlock,
    TextRegion,
    UnconfiguredExtractor,
)
from app.services.extraction_store import build_extraction_run
from tests.conftest import (
    PDF_BYTES,
    auth_header,
    pdf_bytes,
    register_and_login,
    requires_postgres,
    upload_document,
)

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


def _result(
    name: str, *, version: str, confidence: float | None, with_region: bool
) -> ExtractionResult:
    region = TextRegion(page=1, x=0.1, y=0.2, width=0.3, height=0.05) if with_region else None
    return ExtractionResult(
        pages=(
            ExtractedPage(
                number=1,
                text="page one",
                confidence=None,
                blocks=(TextBlock(text=name, region=region, confidence=confidence),),
            ),
        ),
        engine="deterministic-test-double",
        engine_version=version,
        metadata={},
    )


async def _persist_run_with_name(
    session_factory: async_sessionmaker[AsyncSession],
    document_id: Any,
    *,
    name: str,
    version: str = "1.0",
    confidence: float | None = 0.9,
    with_region: bool = True,
) -> None:
    """Persist a run and one person.full_name observation (run + observation atomic)."""
    async with session_factory() as db:
        run = build_extraction_run(
            document_id=document_id,
            result=_result(name, version=version, confidence=confidence, with_region=with_region),
        )
        db.add(run)
        await db.flush()
        block = run.pages[0].blocks[0]
        db.add_all(
            build_attribute_observations(
                run=run,
                candidates=[
                    CandidateObservation(
                        canonical_identifier=PERSON_FULL_NAME,
                        value=block.text,
                        source_block=block,
                        confidence=block.confidence,
                    )
                ],
            )
        )
        await db.commit()


async def _register_and_upload(
    auth_client: AsyncClient, email: str, *, content: bytes = PDF_BYTES
) -> tuple[str, str, str]:
    """Register a user, upload one document, and return (token, user_id, document_id)."""
    token, user = await register_and_login(auth_client, email)
    document = await upload_document(auth_client, token, content=content)
    return token, str(user["id"]), str(document["id"])


class TestAttributeRetrieval:
    async def test_authenticated_user_retrieves_full_name_with_provenance(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _user_id, document_id = await _register_and_upload(auth_client, "a@example.com")
        await _persist_run_with_name(
            auth_app.state.session_factory, document_id, name="Priya Sharma"
        )

        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token)
        )
        assert response.status_code == 200, response.text
        body = response.json()
        # Correct value, no ambiguity.
        assert body["canonical_identifier"] == PERSON_FULL_NAME == "person.full_name"
        assert body["value"] == "Priya Sharma"
        assert body["is_ambiguous"] is False
        # Confidence and provenance travel with the observation.
        assert len(body["observations"]) == 1
        obs = body["observations"][0]
        assert obs["confidence"] == pytest.approx(0.9)
        assert obs["document_id"] == document_id
        assert obs["page_number"] == 1
        assert obs["region"] == {"x": 0.1, "y": 0.2, "width": 0.3, "height": 0.05}

    async def test_missing_region_is_null_not_invented(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _user_id, document_id = await _register_and_upload(auth_client, "a@example.com")
        await _persist_run_with_name(
            auth_app.state.session_factory, document_id, name="Priya Sharma", with_region=False
        )

        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token)
        )
        assert response.status_code == 200, response.text
        assert response.json()["observations"][0]["region"] is None

    async def test_ambiguous_attribute_returns_no_selected_value(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _user_id, doc_a = await _register_and_upload(
            auth_client, "a@example.com", content=pdf_bytes(b"A")
        )
        # A second document for the same user, disagreeing on the name.
        doc_b = str((await upload_document(auth_client, token, content=pdf_bytes(b"B")))["id"])
        await _persist_run_with_name(auth_app.state.session_factory, doc_a, name="Priya Sharma")
        await _persist_run_with_name(auth_app.state.session_factory, doc_b, name="Riya Verma")

        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token)
        )
        assert response.status_code == 200, response.text
        body = response.json()
        # No value is selected; both candidates remain visible.
        assert body["is_ambiguous"] is True
        assert body["value"] is None
        assert {o["value"] for o in body["observations"]} == {"Priya Sharma", "Riya Verma"}

    async def test_unknown_attribute_is_not_found(
        self, auth_client: AsyncClient
    ) -> None:
        token, _user = await register_and_login(auth_client, "a@example.com")
        response = await auth_client.get(
            "/record/attributes/person.date_of_birth", headers=auth_header(token)
        )
        assert response.status_code == 404, response.text

    async def test_record_listing_is_scoped_to_the_user(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _user_id, document_id = await _register_and_upload(auth_client, "a@example.com")
        await _persist_run_with_name(
            auth_app.state.session_factory, document_id, name="Priya Sharma"
        )

        response = await auth_client.get("/record/attributes", headers=auth_header(token))
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["count"] == 1
        assert body["attributes"][0]["canonical_identifier"] == PERSON_FULL_NAME
        assert body["attributes"][0]["value"] == "Priya Sharma"


class TestUserIsolation:
    async def test_another_users_attribute_cannot_be_retrieved(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        # User A has a value.
        _token_a, _a_id, doc_a = await _register_and_upload(auth_client, "a@example.com")
        await _persist_run_with_name(
            auth_app.state.session_factory, doc_a, name="Priya Sharma"
        )

        # User B has none — the same request answers 404, never A's value.
        token_b, _b = await register_and_login(auth_client, "b@example.com")
        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token_b)
        )
        assert response.status_code == 404, response.text

        listing = await auth_client.get("/record/attributes", headers=auth_header(token_b))
        assert listing.status_code == 200
        assert listing.json() == {"attributes": [], "count": 0}

    async def test_another_users_document_cannot_be_retrieved(
        self, auth_client: AsyncClient
    ) -> None:
        # Document retrieval reuses the vault; ownership is enforced there.
        token_a, _a_id, doc_a = await _register_and_upload(auth_client, "a@example.com")
        owner = await auth_client.get(f"/documents/{doc_a}", headers=auth_header(token_a))
        assert owner.status_code == 200, owner.text

        token_b, _b = await register_and_login(auth_client, "b@example.com")
        other = await auth_client.get(f"/documents/{doc_a}", headers=auth_header(token_b))
        assert other.status_code == 404, other.text

    async def test_authentication_is_enforced(self, auth_client: AsyncClient) -> None:
        assert (await auth_client.get(f"/record/attributes/{PERSON_FULL_NAME}")).status_code == 401
        assert (await auth_client.get("/record/attributes")).status_code == 401


class TestFreshnessAndHistory:
    async def test_retrieval_reflects_the_newest_successful_run(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _user_id, document_id = await _register_and_upload(auth_client, "a@example.com")
        session_factory = auth_app.state.session_factory
        await _persist_run_with_name(
            session_factory, document_id, name="Priya Sharma", version="1.0"
        )
        await _persist_run_with_name(
            session_factory, document_id, name="Priya Verma", version="2.0"
        )

        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token)
        )
        body = response.json()
        # The newest run supersedes; not an ambiguity within one document.
        assert body["value"] == "Priya Verma"
        assert body["is_ambiguous"] is False
        assert len(body["observations"]) == 1

        # History is intact: both runs' observations still exist underneath.
        async with session_factory() as db:
            everything = await list_attribute_observations(
                db, document_id=uuid.UUID(document_id)
            )
        assert {o.value for o in everything} == {"Priya Sharma", "Priya Verma"}

    async def test_failed_extraction_does_not_become_retrievable(
        self, auth_app: FastAPI, auth_client: AsyncClient, db_settings: Settings
    ) -> None:
        token, _user_id, document_id = await _register_and_upload(auth_client, "a@example.com")
        session_factory = auth_app.state.session_factory
        await _persist_run_with_name(session_factory, document_id, name="Priya Sharma")

        # A failed extraction persists no run, so it adds no retrievable value.
        await processing.process_one(
            session_factory,
            storage=auth_app.state.document_storage,
            extractor=UnconfiguredExtractor(),
            settings=db_settings,
        )

        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token)
        )
        body = response.json()
        assert body["value"] == "Priya Sharma"
        assert len(body["observations"]) == 1


class TestNoFileBytes:
    async def test_no_document_bytes_are_duplicated_into_the_response(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _user_id, document_id = await _register_and_upload(auth_client, "a@example.com")
        await _persist_run_with_name(
            auth_app.state.session_factory, document_id, name="Priya Sharma"
        )

        response = await auth_client.get(
            f"/record/attributes/{PERSON_FULL_NAME}", headers=auth_header(token)
        )
        # The response references the document by id and carries no file content.
        assert response.json()["observations"][0]["document_id"] == document_id
        assert "%PDF" not in response.text
        assert "storage_key" not in response.text
