"""Sprint 3 — the document vault, exercised over HTTP.

Every test here drives a real request through the real middleware stack, the real
authentication dependency, the real service layer, a real PostgreSQL database, and
real storage on disk. Testing the service functions directly would have proved that
the functions work; it would not have proved that the *route* authorises, that the
authorisation is applied before storage is touched, or that the response omits what
it must omit. The requirement being tested is the behaviour of the API, so that is
what is driven.

Isolation between users is not one test. It is tested at every surface the vault
has — list, metadata, download, delete — because a check that is right in three
places and forgotten in the fourth is exactly the failure mode NFR-SEC-003 exists
to prevent.
"""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.core.errors import DocumentStorageError
from tests.conftest import (
    JPEG_BYTES,
    PDF_BYTES,
    PNG_BYTES,
    RecordingResetDelivery,
    auth_header,
    pdf_bytes,
    register_and_login,
    requires_postgres,
    upload_document,
    upload_file,
)

pytestmark = requires_postgres

OWNER = "owner@docura.example"
INTRUDER = "intruder@docura.example"


@pytest.fixture
async def owner_token(auth_client: AsyncClient) -> str:
    token, _ = await register_and_login(auth_client, OWNER)
    return token


@pytest.fixture
async def intruder_token(auth_client: AsyncClient) -> str:
    token, _ = await register_and_login(auth_client, INTRUDER)
    return token


class TestUpload:
    async def test_authenticated_user_can_upload_a_supported_document(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T001 — FR-UPL-001, AC-US-002-1."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(PDF_BYTES, "12th-marksheet.pdf"),
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert body["rejected"] == []
        [document] = body["accepted"]

        assert document["original_filename"] == "12th-marksheet.pdf"
        assert document["content_type"] == "application/pdf"
        assert document["byte_size"] == len(PDF_BYTES)
        # FR-UPL-005: a status is present from the moment of acceptance.
        assert document["status"] == "queued"
        assert document["document_type"] == "unclassified"
        uuid.UUID(document["id"])

    @pytest.mark.parametrize(
        ("content", "filename", "declared", "expected_type"),
        [
            (PDF_BYTES, "aadhaar.pdf", "application/pdf", "application/pdf"),
            (JPEG_BYTES, "photograph.jpg", "image/jpeg", "image/jpeg"),
            (JPEG_BYTES, "photograph.jpeg", "image/jpeg", "image/jpeg"),
            (PNG_BYTES, "signature.png", "image/png", "image/png"),
        ],
    )
    async def test_every_accepted_type_is_accepted(
        self,
        auth_client: AsyncClient,
        owner_token: str,
        content: bytes,
        filename: str,
        declared: str,
        expected_type: str,
    ) -> None:
        """FR-UPL-001 names PDF, JPG and PNG; all three must actually work."""
        document = await upload_document(
            auth_client, owner_token, content=content, filename=filename, content_type=declared
        )
        assert document["content_type"] == expected_type

    async def test_unauthenticated_upload_is_rejected(self, auth_client: AsyncClient) -> None:
        """S3-T002 — FR-ACC-002."""
        response = await auth_client.post("/documents", files=upload_file(PDF_BYTES))

        assert response.status_code == 401
        assert response.headers["WWW-Authenticate"].startswith("Bearer")
        assert response.headers["content-type"].startswith("application/problem+json")

    async def test_upload_with_an_unknown_token_is_rejected(self, auth_client: AsyncClient) -> None:
        """A token that was never issued must not differ from no token at all."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header("not-a-real-session-token"),
            files=upload_file(PDF_BYTES),
        )
        assert response.status_code == 401

    async def test_unsupported_file_type_is_rejected(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T003 — FR-UPL-004, AC-US-002-3: the reason *and* the alternatives."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(b"MZ\x90\x00 not a document", "payload.exe", "application/exe"),
        )

        assert response.status_code == 415
        body = response.json()
        assert "extension" in body["detail"].lower()
        assert "PDF, JPG, or PNG" in body["remediation"]

    async def test_a_file_lying_about_its_type_is_rejected(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """A ``.pdf`` name over non-PDF bytes must not be stored as a PDF.

        This is the check that makes the extension untrustworthy on purpose: the
        signature decides, and a contradiction is refused rather than silently
        re-typed under a name that would then describe the wrong thing.
        """
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(b"<html><body>not a pdf</body></html>", "cv.pdf", "application/pdf"),
        )

        assert response.status_code == 415
        assert "not a readable" in response.json()["detail"]

    async def test_a_pdf_named_as_a_png_is_rejected(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """The mismatch is reported specifically, not as a generic refusal."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(PDF_BYTES, "scan.png", "image/png"),
        )

        assert response.status_code == 415
        detail = response.json()["detail"]
        assert "image/png" in detail
        assert "application/pdf" in detail

    async def test_empty_file_is_rejected(self, auth_client: AsyncClient, owner_token: str) -> None:
        """S3-T004 — Table 7.1 integrity check; there is nothing to store."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(b"", "empty.pdf"),
        )

        assert response.status_code == 415
        assert "empty" in response.json()["detail"].lower()

    async def test_truncated_file_is_rejected_as_unreadable(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """A PDF whose header did not survive the transfer is corrupt, and says so."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(b"DF-1.7\ntrailer\n%%EOF\n", "truncated.pdf"),
        )

        assert response.status_code == 415
        assert "damaged" in response.json()["detail"]

    async def test_file_size_limit_is_enforced(
        self,
        db_settings: Settings,
        db_engine: Any,
        reset_delivery: RecordingResetDelivery,
    ) -> None:
        """S3-T005 — FR-UPL-003.

        The app is rebuilt with a small ceiling rather than sending ten megabytes
        through the test suite: what is being tested is that the configured limit is
        the one enforced, and a real-sized file would prove that no better.
        """
        from app.api.auth import reset_rate_limiter
        from app.db.session import create_session_factory
        from app.main import create_app

        reset_rate_limiter()
        small = db_settings.model_copy(update={"max_document_bytes": 2048})
        app = create_app(small)
        app.state.engine = db_engine
        app.state.session_factory = create_session_factory(db_engine)
        app.state.reset_delivery = reset_delivery

        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            token, _ = await register_and_login(client, OWNER)

            oversized = PDF_BYTES + b"%" + b"x" * 4096
            response = await client.post(
                "/documents",
                headers=auth_header(token),
                files=upload_file(oversized, "huge.pdf"),
            )

            assert response.status_code == 413
            assert "2048" in response.json()["detail"]

            # And nothing was admitted: a refused upload leaves no row (BR-016).
            listing = await client.get("/documents", headers=auth_header(token))
            assert listing.json()["count"] == 0

        reset_rate_limiter()

    async def test_limits_are_stated_in_advance(
        self, auth_client: AsyncClient, owner_token: str, db_settings: Settings
    ) -> None:
        """FR-UPL-003 — the limits are readable before a file is chosen."""
        response = await auth_client.get("/documents/limits", headers=auth_header(owner_token))

        assert response.status_code == 200
        body = response.json()
        assert body["max_document_bytes"] == db_settings.max_document_bytes
        assert body["max_documents_per_upload"] == db_settings.max_documents_per_upload
        assert set(body["accepted_media_types"]) == {
            "application/pdf",
            "image/jpeg",
            "image/png",
        }
        assert set(body["accepted_extensions"]) == {".pdf", ".jpg", ".jpeg", ".png"}

    async def test_metadata_is_persisted_correctly(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T006 — what was uploaded is what a later request reads back."""
        content = pdf_bytes(b"semester-4")
        created = await upload_document(
            auth_client, owner_token, content=content, filename="semester-4-result.pdf"
        )

        fetched = await auth_client.get(
            f"/documents/{created['id']}", headers=auth_header(owner_token)
        )
        assert fetched.status_code == 200
        stored = fetched.json()

        assert stored == created
        assert stored["byte_size"] == len(content)
        assert stored["original_filename"] == "semester-4-result.pdf"

        import hashlib

        assert stored["checksum_sha256"] == hashlib.sha256(content).hexdigest()

    async def test_several_files_upload_in_one_action(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """FR-UPL-002, AC-US-002-2 — each accepted file is its own document."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=[
                ("files", ("marksheet.pdf", pdf_bytes(b"one"), "application/pdf")),
                ("files", ("photo.jpg", JPEG_BYTES, "image/jpeg")),
                ("files", ("sign.png", PNG_BYTES, "image/png")),
            ],
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert len(body["accepted"]) == 3
        assert body["rejected"] == []
        assert len({item["id"] for item in body["accepted"]}) == 3

    async def test_a_partly_invalid_batch_reports_both_halves(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """NFR-ERR-003 — partial success is reported as partial, and itemised."""
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=[
                ("files", ("good.pdf", pdf_bytes(b"good"), "application/pdf")),
                ("files", ("bad.exe", b"MZ\x90\x00", "application/exe")),
            ],
        )

        assert response.status_code == 201, response.text
        body = response.json()
        assert [item["original_filename"] for item in body["accepted"]] == ["good.pdf"]
        [rejection] = body["rejected"]
        assert rejection["filename"] == "bad.exe"
        assert rejection["reason"]
        assert rejection["remediation"]

    async def test_too_many_files_in_one_request_is_refused(
        self, auth_client: AsyncClient, owner_token: str, db_settings: Settings
    ) -> None:
        """The per-request count is bounded, so one request cannot be a whole batch job."""
        over = db_settings.max_documents_per_upload + 1
        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=[
                ("files", (f"scan-{index}.pdf", pdf_bytes(str(index).encode()), "application/pdf"))
                for index in range(over)
            ],
        )

        assert response.status_code == 415
        assert str(db_settings.max_documents_per_upload) in response.json()["detail"]

    async def test_identical_file_is_not_silently_duplicated(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """FR-UPL-007, AC-US-002-4 — no silent duplicate; the existing one is named."""
        await upload_document(auth_client, owner_token, filename="aadhaar.pdf")

        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(PDF_BYTES, "aadhaar-copy.pdf"),
        )

        assert response.status_code == 409
        assert "aadhaar.pdf" in response.json()["detail"]

        listing = await auth_client.get("/documents", headers=auth_header(owner_token))
        assert listing.json()["count"] == 1

    async def test_two_users_may_store_the_same_file(
        self, auth_client: AsyncClient, owner_token: str, intruder_token: str
    ) -> None:
        """Duplicate detection is per account. Two people holding one public form is normal."""
        await upload_document(auth_client, owner_token)
        await upload_document(auth_client, intruder_token)

        for token in (owner_token, intruder_token):
            listing = await auth_client.get("/documents", headers=auth_header(token))
            assert listing.json()["count"] == 1


class TestListing:
    async def test_user_can_list_their_own_documents(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T007 — FR-DOC-001."""
        await upload_document(auth_client, owner_token, content=pdf_bytes(b"a"), filename="a.pdf")
        await upload_document(auth_client, owner_token, content=pdf_bytes(b"b"), filename="b.pdf")

        response = await auth_client.get("/documents", headers=auth_header(owner_token))

        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 2
        names = {item["original_filename"] for item in body["documents"]}
        assert names == {"a.pdf", "b.pdf"}
        # FR-DOC-001 asks the listing to show type, date added, and status.
        for item in body["documents"]:
            assert item["document_type"] == "unclassified"
            assert item["status"] == "queued"
            assert item["created_at"]

    async def test_listing_never_contains_file_contents(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """A vault listing answers 'what do I have', not 'give me my documents'."""
        await upload_document(auth_client, owner_token)

        raw = (await auth_client.get("/documents", headers=auth_header(owner_token))).text

        assert "%PDF" not in raw

    async def test_user_cannot_see_another_users_documents(
        self, auth_client: AsyncClient, owner_token: str, intruder_token: str
    ) -> None:
        """S3-T008 — NFR-SEC-003, NFR-PRIV-002."""
        await upload_document(auth_client, owner_token, filename="owner-only.pdf")

        response = await auth_client.get("/documents", headers=auth_header(intruder_token))

        assert response.status_code == 200
        assert response.json() == {"documents": [], "count": 0}

    async def test_unauthenticated_listing_is_rejected(self, auth_client: AsyncClient) -> None:
        """FR-ACC-002 — nothing about a vault is readable without a session."""
        assert (await auth_client.get("/documents")).status_code == 401


class TestMetadata:
    async def test_user_can_read_their_own_document_metadata(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T009."""
        created = await upload_document(auth_client, owner_token)

        response = await auth_client.get(
            f"/documents/{created['id']}", headers=auth_header(owner_token)
        )

        assert response.status_code == 200
        assert response.json()["id"] == created["id"]

    async def test_user_cannot_read_another_users_document_metadata(
        self, auth_client: AsyncClient, owner_token: str, intruder_token: str
    ) -> None:
        """S3-T010 — and the answer is 404, not 403.

        A 403 would confirm the identifier names a real document. On a vault of
        identity papers, that confirmation is itself the disclosure.
        """
        created = await upload_document(auth_client, owner_token)

        response = await auth_client.get(
            f"/documents/{created['id']}", headers=auth_header(intruder_token)
        )

        assert response.status_code == 404
        assert created["original_filename"] not in response.text

    async def test_an_unknown_id_answers_exactly_as_a_forbidden_one_does(
        self, auth_client: AsyncClient, owner_token: str, intruder_token: str
    ) -> None:
        """The two cases must be indistinguishable, or the endpoint is an oracle."""
        created = await upload_document(auth_client, owner_token)

        forbidden = await auth_client.get(
            f"/documents/{created['id']}", headers=auth_header(intruder_token)
        )
        unknown = await auth_client.get(
            f"/documents/{uuid.uuid4()}", headers=auth_header(intruder_token)
        )

        assert forbidden.status_code == unknown.status_code == 404
        assert forbidden.json()["detail"] == unknown.json()["detail"]
        assert forbidden.json()["title"] == unknown.json()["title"]

    async def test_a_malformed_id_is_a_validation_error_not_a_lookup(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """A non-UUID never reaches the database."""
        response = await auth_client.get("/documents/not-a-uuid", headers=auth_header(owner_token))
        assert response.status_code == 422


class TestDownload:
    async def test_user_can_download_their_own_document(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T011 — FR-DOC-004, BR-013: the original, exactly as uploaded."""
        content = pdf_bytes(b"downloadable")
        created = await upload_document(
            auth_client, owner_token, content=content, filename="10th-marksheet.pdf"
        )

        response = await auth_client.get(
            f"/documents/{created['id']}/content", headers=auth_header(owner_token)
        )

        assert response.status_code == 200
        assert response.content == content
        assert response.headers["content-type"].startswith("application/pdf")
        disposition = response.headers["content-disposition"]
        assert disposition.startswith("attachment")
        assert "10th-marksheet.pdf" in disposition

    async def test_download_preserves_a_non_ascii_filename(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """RFC 6266 — the user's own name for the file survives the round trip."""
        created = await upload_document(auth_client, owner_token, filename="स्नातक-प्रमाणपत्र.pdf")

        response = await auth_client.get(
            f"/documents/{created['id']}/content", headers=auth_header(owner_token)
        )

        assert response.status_code == 200
        assert "filename*=UTF-8''" in response.headers["content-disposition"]

    async def test_user_cannot_download_another_users_document(
        self, auth_client: AsyncClient, owner_token: str, intruder_token: str
    ) -> None:
        """S3-T012 — the ownership check runs before storage is opened."""
        created = await upload_document(auth_client, owner_token, content=pdf_bytes(b"private"))

        response = await auth_client.get(
            f"/documents/{created['id']}/content", headers=auth_header(intruder_token)
        )

        assert response.status_code == 404
        assert b"%PDF" not in response.content

    async def test_unauthenticated_download_is_rejected(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """NFR-SEC-007 — there is no standing link; the session is the credential."""
        created = await upload_document(auth_client, owner_token)

        response = await auth_client.get(f"/documents/{created['id']}/content")

        assert response.status_code == 401
        assert b"%PDF" not in response.content

    async def test_a_revoked_session_can_no_longer_download(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """NFR-SEC-005, EC-016 — access ends when the session does, not when a link expires."""
        created = await upload_document(auth_client, owner_token)
        await auth_client.post("/auth/logout", headers=auth_header(owner_token))

        response = await auth_client.get(
            f"/documents/{created['id']}/content", headers=auth_header(owner_token)
        )

        assert response.status_code == 401


class TestDeletion:
    async def test_user_can_delete_their_own_document(
        self, auth_client: AsyncClient, owner_token: str, db_settings: Settings
    ) -> None:
        """S3-T013 — FR-DOC-007: the row goes, the bytes go, and the user is told what went."""
        created = await upload_document(auth_client, owner_token, filename="obsolete.pdf")
        root = db_settings.document_storage_root
        assert _stored_object_count(root) == 1

        response = await auth_client.delete(
            f"/documents/{created['id']}", headers=auth_header(owner_token)
        )

        assert response.status_code == 200
        body = response.json()
        assert body["deleted"] is True
        assert body["id"] == created["id"]
        # FR-DOC-007: the confirmation names what was lost.
        assert "obsolete.pdf" in body["detail"]
        assert _stored_object_count(root) == 0

    async def test_user_cannot_delete_another_users_document(
        self, auth_client: AsyncClient, owner_token: str, intruder_token: str, db_settings: Settings
    ) -> None:
        """S3-T014 — and the owner's file is untouched by the attempt."""
        created = await upload_document(auth_client, owner_token)

        response = await auth_client.delete(
            f"/documents/{created['id']}", headers=auth_header(intruder_token)
        )

        assert response.status_code == 404
        assert _stored_object_count(db_settings.document_storage_root) == 1

        still_there = await auth_client.get(
            f"/documents/{created['id']}", headers=auth_header(owner_token)
        )
        assert still_there.status_code == 200

    async def test_deleted_document_is_no_longer_retrievable(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T015 — every surface agrees the document is gone."""
        created = await upload_document(auth_client, owner_token)
        await auth_client.delete(f"/documents/{created['id']}", headers=auth_header(owner_token))

        headers = auth_header(owner_token)
        assert (
            await auth_client.get(f"/documents/{created['id']}", headers=headers)
        ).status_code == 404
        assert (
            await auth_client.get(f"/documents/{created['id']}/content", headers=headers)
        ).status_code == 404
        assert (await auth_client.get("/documents", headers=headers)).json()["count"] == 0

    async def test_deleting_twice_reports_it_is_already_gone(
        self, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """Repeated deletion answers 404 rather than pretending to delete again."""
        created = await upload_document(auth_client, owner_token)
        headers = auth_header(owner_token)

        first = await auth_client.delete(f"/documents/{created['id']}", headers=headers)
        second = await auth_client.delete(f"/documents/{created['id']}", headers=headers)

        assert first.status_code == 200
        assert second.status_code == 404

    async def test_deletion_succeeds_when_the_stored_object_is_already_missing(
        self, auth_client: AsyncClient, owner_token: str, db_settings: Settings
    ) -> None:
        """A file removed underneath DOCURA must not trap the user with an undeletable row.

        BR-018 says the record is the user's to delete. If a missing object made
        deletion fail, the one state the user could never escape would be the one
        where their document is half gone.
        """
        created = await upload_document(auth_client, owner_token)
        for path in db_settings.document_storage_root.rglob("*"):
            if path.is_file():
                path.unlink()

        response = await auth_client.delete(
            f"/documents/{created['id']}", headers=auth_header(owner_token)
        )

        assert response.status_code == 200
        listing = await auth_client.get("/documents", headers=auth_header(owner_token))
        assert listing.json()["count"] == 0

    async def test_unauthenticated_deletion_is_rejected(
        self, auth_client: AsyncClient, owner_token: str, db_settings: Settings
    ) -> None:
        created = await upload_document(auth_client, owner_token)

        response = await auth_client.delete(f"/documents/{created['id']}")

        assert response.status_code == 401
        assert _stored_object_count(db_settings.document_storage_root) == 1


class TestInformationLeakage:
    async def test_internal_storage_paths_are_never_in_a_response(
        self, auth_client: AsyncClient, owner_token: str, db_settings: Settings
    ) -> None:
        """S3-T017 — NFR-ERR-004, NFR-PRIV-007.

        Every response the vault produces is checked against the storage root and
        against the field name that would carry it, so a future model change that
        starts serialising the whole row fails here.
        """
        created = await upload_document(auth_client, owner_token)
        root = str(db_settings.document_storage_root)
        headers = auth_header(owner_token)
        document_id = created["id"]

        bodies = [
            (await auth_client.get("/documents", headers=headers)).text,
            (await auth_client.get(f"/documents/{document_id}", headers=headers)).text,
            (await auth_client.get("/documents/limits", headers=headers)).text,
            (await auth_client.delete(f"/documents/{document_id}", headers=headers)).text,
        ]

        for body in bodies:
            assert root not in body
            assert "storage_key" not in body
            assert "var/documents" not in body
            assert "\\documents\\" not in body

    async def test_a_storage_failure_produces_the_projects_standard_error(
        self, auth_app: FastAPI, auth_client: AsyncClient, owner_token: str
    ) -> None:
        """S3-T019 — NFR-ERR-001/004, BR-016.

        The failing backend is substituted through the same application state the
        real one is installed into, which is the point of the storage protocol: a
        failure can be induced without reaching inside the service.
        """

        class FailingStorage:
            def save(self, key: str, source: Any) -> int:
                raise DocumentStorageError

            def open(self, key: str) -> Any:
                raise DocumentStorageError

            def delete(self, key: str) -> bool:
                raise DocumentStorageError

            def exists(self, key: str) -> bool:
                return False

        auth_app.state.document_storage = FailingStorage()

        response = await auth_client.post(
            "/documents",
            headers=auth_header(owner_token),
            files=upload_file(PDF_BYTES),
        )

        assert response.status_code == 503
        assert response.headers["content-type"].startswith("application/problem+json")
        body = response.json()
        # NFR-ERR-001: every error states what went wrong and what to do next.
        assert body["title"]
        assert body["detail"]
        assert body["remediation"]
        # NFR-ERR-004: no internal detail escapes.
        assert "Traceback" not in response.text
        assert "OSError" not in response.text

        # And nothing was recorded for a write that did not happen (BR-016).
        listing = await auth_client.get("/documents", headers=auth_header(owner_token))
        assert listing.json()["count"] == 0


def _stored_object_count(root: Path) -> int:
    """How many objects the local storage backend is holding."""
    if not root.exists():
        return 0
    return sum(1 for path in root.rglob("*") if path.is_file())
