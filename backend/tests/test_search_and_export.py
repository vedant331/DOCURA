"""Record export (FR-ACC-006) and search (FR-SRCH) — owner-scoped, read-only.

Both features reuse the existing vault + current-record services, so these tests drive the real
HTTP surface and reuse the record-seeding helper from ``test_record_api``. Needs PostgreSQL;
skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

from fastapi import FastAPI
from httpx import AsyncClient

from tests.conftest import (
    auth_header,
    register_and_login,
    requires_postgres,
    upload_document,
)
from tests.test_record_api import (
    PERSON_FULL_NAME,
    _persist_run_with_name,
    _register_and_upload,
)

pytestmark = requires_postgres


class TestRecordExport:
    async def test_export_includes_documents_and_extracted_information(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _uid, doc_id = await _register_and_upload(auth_client, "exp1@example.com")
        await _persist_run_with_name(auth_app.state.session_factory, doc_id, name="Priya Sharma")

        response = await auth_client.get("/record/export", headers=auth_header(token))
        assert response.status_code == 200, response.text
        assert (
            response.headers["content-disposition"]
            == 'attachment; filename="docura-record-export.json"'
        )
        body = response.json()
        assert body["account_email"] == "exp1@example.com"
        assert body["document_count"] == 1
        assert body["documents"][0]["id"] == doc_id
        # No storage key / file bytes leak into the export.
        assert "storage_key" not in body["documents"][0]
        assert body["attribute_count"] == 1
        assert body["attributes"][0]["canonical_identifier"] == PERSON_FULL_NAME
        assert body["attributes"][0]["value"] == "Priya Sharma"

    async def test_export_of_an_empty_record(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "exp2@example.com")
        body = (await auth_client.get("/record/export", headers=auth_header(token))).json()
        assert body["documents"] == []
        assert body["attributes"] == []
        assert body["document_count"] == 0
        assert body["attribute_count"] == 0

    async def test_export_requires_authentication(self, auth_client: AsyncClient) -> None:
        assert (await auth_client.get("/record/export")).status_code == 401

    async def test_export_is_owner_scoped(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        _token_a, _uid, doc_a = await _register_and_upload(auth_client, "owner-a@example.com")
        await _persist_run_with_name(auth_app.state.session_factory, doc_a, name="Alice Owner")
        token_b, _user_b = await register_and_login(auth_client, "owner-b@example.com")

        body = (await auth_client.get("/record/export", headers=auth_header(token_b))).json()
        # B's export is B's own — never A's documents or attributes.
        assert body["account_email"] == "owner-b@example.com"
        assert body["documents"] == []
        assert body["attributes"] == []


class TestSearch:
    async def test_finds_own_document_by_filename(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "s1@example.com")
        await upload_document(auth_client, token, filename="aadhaar-card.pdf")

        body = (
            await auth_client.get("/search", params={"q": "aadhaar"}, headers=auth_header(token))
        ).json()
        assert body["document_count"] == 1
        assert body["documents"][0]["original_filename"] == "aadhaar-card.pdf"

    async def test_finds_attribute_value_with_supporting_document_and_location(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _uid, doc_id = await _register_and_upload(auth_client, "s2@example.com")
        await _persist_run_with_name(auth_app.state.session_factory, doc_id, name="Priya Sharma")

        body = (
            await auth_client.get("/search", params={"q": "priya"}, headers=auth_header(token))
        ).json()
        assert body["attribute_count"] == 1
        match = body["attributes"][0]
        assert match["canonical_identifier"] == PERSON_FULL_NAME
        assert match["value"] == "Priya Sharma"
        assert match["document_id"] == doc_id  # supporting document (FR-SRCH-003)
        assert match["page_number"] == 1  # location within it (FR-SRCH-004)

    async def test_no_match_returns_empty(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "s3@example.com")
        await upload_document(auth_client, token, filename="marksheet.pdf")

        body = (
            await auth_client.get(
                "/search", params={"q": "zzz-nothing-here"}, headers=auth_header(token)
            )
        ).json()
        assert body["document_count"] == 0
        assert body["attribute_count"] == 0

    async def test_search_is_owner_scoped(self, auth_client: AsyncClient) -> None:
        token_a, _user_a = await register_and_login(auth_client, "sa@example.com")
        await upload_document(auth_client, token_a, filename="alice-secret.pdf")
        token_b, _user_b = await register_and_login(auth_client, "sb@example.com")

        body = (
            await auth_client.get(
                "/search", params={"q": "alice-secret"}, headers=auth_header(token_b)
            )
        ).json()
        assert body["document_count"] == 0  # B cannot see A's document

    async def test_search_requires_authentication(self, auth_client: AsyncClient) -> None:
        assert (await auth_client.get("/search", params={"q": "anything"})).status_code == 401

    async def test_search_rejects_an_empty_query(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "s4@example.com")
        response = await auth_client.get("/search", params={"q": ""}, headers=auth_header(token))
        assert response.status_code == 422  # q has min_length=1
