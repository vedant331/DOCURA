"""Account deletion — FR-ACC-006/007/008, NFR-PRIV-003.

Deletion is irreversible and must remove the account, every document, all extracted
information, and every derived copy. It requires the explicit confirmation FR-ACC-007 asks
for, acts only on the authenticated account (never a client-supplied id), and cascades in the
database. These tests drive the real HTTP surface (auth, ownership, confirmation) and, at the
service level, prove the cascade actually removes extracted information and derived rows.
"""

from __future__ import annotations

import io
from typing import Any

import pytest
from httpx import AsyncClient
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.core.config import Settings
from app.db.models import (
    AttributeObservation,
    Document,
    ExtractionRun,
    ProcessingJob,
    Session,
    User,
)
from app.db.session import create_session_factory
from app.services.attribute_observation import CandidateObservation, build_attribute_observations
from app.services.auth_service import delete_account
from app.services.document_service import store_document
from app.services.extraction import ExtractedPage, ExtractionResult, TextBlock
from app.services.extraction_store import build_extraction_run
from app.services.storage import DocumentStorage, build_document_storage
from tests.conftest import (
    PDF_BYTES,
    auth_header,
    register_and_login,
    requires_postgres,
    upload_document,
)

pytestmark = requires_postgres

OWNER = "delete-owner@docura.example"
OTHER = "delete-other@docura.example"


# ----------------------------------------------------------------------- HTTP surface
class TestAccountDeletionApi:
    async def test_deletes_account_documents_and_revokes_the_session(
        self, auth_client: AsyncClient
    ) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        await upload_document(auth_client, token)

        response = await auth_client.request(
            "DELETE", "/users/me", headers=auth_header(token),
            json={"confirm_email": OWNER},
        )
        assert response.status_code == 200, response.text
        body = response.json()
        assert body["status"] == "deleted"
        assert body["documents_removed"] == 1
        assert body["objects_removed"] == 1  # the stored original was removed from storage

        # The session is gone with the account — the token no longer authenticates.
        after = await auth_client.get("/users/me", headers=auth_header(token))
        assert after.status_code == 401
        # The account itself is gone — the credentials no longer work.
        relogin = await auth_client.post(
            "/auth/login", json={"email": OWNER, "password": "correct horse battery"}
        )
        assert relogin.status_code in (401, 422)

    async def test_wrong_confirmation_deletes_nothing(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        await upload_document(auth_client, token)

        response = await auth_client.request(
            "DELETE", "/users/me", headers=auth_header(token),
            json={"confirm_email": "someone-else@docura.example"},
        )
        assert response.status_code == 400  # DeletionNotConfirmedError

        # Nothing was destroyed: the account and its document remain.
        me = await auth_client.get("/users/me", headers=auth_header(token))
        assert me.status_code == 200
        docs = await auth_client.get("/documents", headers=auth_header(token))
        assert docs.status_code == 200
        assert docs.json()["count"] == 1

    async def test_missing_confirmation_is_rejected(self, auth_client: AsyncClient) -> None:
        token, _ = await register_and_login(auth_client, OWNER)
        response = await auth_client.request(
            "DELETE", "/users/me", headers=auth_header(token), json={}
        )
        assert response.status_code == 422  # confirm_email is required

    async def test_unauthenticated_deletion_is_rejected(self, auth_client: AsyncClient) -> None:
        response = await auth_client.request("DELETE", "/users/me", json={"confirm_email": OWNER})
        assert response.status_code == 401

    async def test_deletion_is_isolated_to_the_caller(self, auth_client: AsyncClient) -> None:
        owner_token, _ = await register_and_login(auth_client, OWNER)
        other_token, _ = await register_and_login(auth_client, OTHER)
        await upload_document(auth_client, owner_token)
        await upload_document(auth_client, other_token)

        deleted = await auth_client.request(
            "DELETE", "/users/me", headers=auth_header(owner_token),
            json={"confirm_email": OWNER},
        )
        assert deleted.status_code == 200

        # The other account and its document are untouched.
        me = await auth_client.get("/users/me", headers=auth_header(other_token))
        assert me.status_code == 200
        docs = await auth_client.get("/documents", headers=auth_header(other_token))
        assert docs.json()["count"] == 1


# ----------------------------------------------------------- cascade (service level)
@requires_postgres
class TestAccountDeletionCascade:
    @pytest.fixture
    def session_factory(self, db_engine: Any) -> async_sessionmaker[AsyncSession]:
        return create_session_factory(db_engine)

    @pytest.fixture
    def storage(self, db_settings: Settings) -> DocumentStorage:
        return build_document_storage(db_settings)

    async def test_deleting_the_account_removes_extracted_information_and_derived_rows(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        storage: DocumentStorage,
        db_settings: Settings,
    ) -> None:
        # Seed a user with a document, a real extraction run, and an attribute observation.
        async with session_factory() as db:
            user = User(email="cascade@docura.example", password_hash="argon2-unused")
            db.add(user)
            await db.commit()
            document = await store_document(
                db, owner=user, source=io.BytesIO(PDF_BYTES), filename="d.pdf",
                declared_content_type="application/pdf", storage=storage, settings=db_settings,
            )
            run = build_extraction_run(
                document_id=document.id,
                result=ExtractionResult(
                    pages=(ExtractedPage(number=1, text="x", blocks=(TextBlock(text="x"),)),),
                    engine="test-double", engine_version="1",
                ),
            )
            db.add(run)
            await db.flush()
            observations = build_attribute_observations(
                run=run,
                candidates=[CandidateObservation(
                    canonical_identifier="person.full_name", value="X",
                    source_block=run.pages[0].blocks[0], confidence=0.9,
                )],
            )
            db.add_all(observations)
            await db.commit()
            user_id = user.id

        async def count(db: AsyncSession, model: Any, where: Any) -> int:
            return (await db.scalar(select(func.count()).select_from(model).where(where))) or 0

        async with session_factory() as db:
            # Preconditions: the derived rows exist.
            assert await count(db, Document, Document.user_id == user_id) == 1
            run_ids = (
                await db.scalars(
                    select(ExtractionRun.id)
                    .join(Document, ExtractionRun.document_id == Document.id)
                    .where(Document.user_id == user_id)
                )
            ).all()
            assert len(run_ids) == 1
            seeded = await count(
                db, AttributeObservation, AttributeObservation.run_id.in_(run_ids)
            )
            assert seeded == 1

        # Delete the account.
        async with session_factory() as db:
            account = await db.get(User, user_id)
            assert account is not None
            docs_removed, _ = await delete_account(
                db, user=account, confirm_email="cascade@docura.example", storage=storage
            )
            assert docs_removed == 1

        # Everything derived from the account is gone (DB ON DELETE CASCADE).
        async with session_factory() as db:
            assert await db.get(User, user_id) is None
            owned_docs = select(Document.id).where(Document.user_id == user_id)
            assert await count(db, Document, Document.user_id == user_id) == 0
            assert await count(db, ProcessingJob, ProcessingJob.document_id.in_(owned_docs)) == 0
            assert await count(db, ExtractionRun, ExtractionRun.id.in_(run_ids)) == 0
            assert await count(db, Session, Session.user_id == user_id) == 0
            observed = await count(
                db, AttributeObservation, AttributeObservation.run_id.in_(run_ids)
            )
            assert observed == 0
