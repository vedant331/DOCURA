"""Record export (FR-ACC-006) and search (FR-SRCH) — owner-scoped, read-only.

Both features reuse the existing vault + current-record services, so these tests drive the real
HTTP surface and reuse the record-seeding helper from ``test_record_api``. Needs PostgreSQL;
skips when TEST_DATABASE_URL is unset.
"""

from __future__ import annotations

from datetime import date, timedelta

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


class TestSearchFilters:
    """FR-SRCH-005 — filter search results by document type and date added.

    Uploaded documents are stored as ``unclassified`` (the only released DocumentType until the
    S-6 taxonomy is set), so the type filter is exercised via its valid value and its 422
    rejection; the date filter is exercised for inclusion and exclusion. Dates are relative to
    today, so the tests do not depend on a fixed clock. Every request is owner-scoped.
    """

    async def _setup(self, auth_client: AsyncClient, email: str) -> str:
        token, _user = await register_and_login(auth_client, email)
        await upload_document(auth_client, token, filename="aadhaar-card.pdf")
        return token

    async def _search(self, auth_client: AsyncClient, token: str, **params: object) -> dict:
        resp = await auth_client.get("/search", params=params, headers=auth_header(token))
        assert resp.status_code == 200, resp.text
        return resp.json()

    # 1. baseline: no filters, existing behaviour unchanged
    async def test_search_without_filters(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f1@example.com")
        body = await self._search(auth_client, token, q="aadhaar")
        assert body["document_count"] == 1

    # 2. filter by document type (valid released value)
    async def test_filter_by_document_type(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f2@example.com")
        body = await self._search(auth_client, token, q="aadhaar", document_type="unclassified")
        assert body["document_count"] == 1

    # 3. filter by date (inclusive today; and an exclusion boundary)
    async def test_filter_by_date(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f3@example.com")
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        yesterday = (date.today() - timedelta(days=1)).isoformat()
        assert (await self._search(auth_client, token, q="aadhaar", added_after=today))[
            "document_count"
        ] == 1
        assert (await self._search(auth_client, token, q="aadhaar", added_before=today))[
            "document_count"
        ] == 1
        assert (await self._search(auth_client, token, q="aadhaar", added_after=tomorrow))[
            "document_count"
        ] == 0
        assert (await self._search(auth_client, token, q="aadhaar", added_before=yesterday))[
            "document_count"
        ] == 0

    # 4. combined text + type
    async def test_text_and_type(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f4@example.com")
        assert (
            await self._search(auth_client, token, q="aadhaar", document_type="unclassified")
        )["document_count"] == 1
        # text that does not match the filename → no document, even with a matching type filter
        assert (
            await self._search(auth_client, token, q="zzz", document_type="unclassified")
        )["document_count"] == 0

    # 5. combined text + date
    async def test_text_and_date(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f5@example.com")
        today = date.today().isoformat()
        assert (await self._search(auth_client, token, q="aadhaar", added_after=today))[
            "document_count"
        ] == 1

    # 6. combined type + date
    async def test_type_and_date(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f6@example.com")
        today = date.today().isoformat()
        body = await self._search(
            auth_client, token, q="aadhaar", document_type="unclassified", added_after=today
        )
        assert body["document_count"] == 1

    # 7. all three together
    async def test_text_type_and_date(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f7@example.com")
        today = date.today().isoformat()
        body = await self._search(
            auth_client, token, q="aadhaar", document_type="unclassified", added_after=today
        )
        assert body["document_count"] == 1

    # 8. no-match filters (valid but exclude everything)
    async def test_no_match_filters(self, auth_client: AsyncClient) -> None:
        token = await self._setup(auth_client, "f8@example.com")
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        body = await self._search(auth_client, token, q="aadhaar", added_after=tomorrow)
        assert body["document_count"] == 0

    # 9. invalid date → 422 via request validation
    async def test_invalid_date_is_rejected(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "f9@example.com")
        resp = await auth_client.get(
            "/search", params={"q": "x", "added_after": "not-a-date"}, headers=auth_header(token)
        )
        assert resp.status_code == 422

    # 10. invalid document type → 422 via request validation
    async def test_invalid_document_type_is_rejected(self, auth_client: AsyncClient) -> None:
        token, _user = await register_and_login(auth_client, "f10@example.com")
        resp = await auth_client.get(
            "/search", params={"q": "x", "document_type": "aadhaar"}, headers=auth_header(token)
        )
        assert resp.status_code == 422  # not a released DocumentType

    # 11. owner isolation with filters — B cannot see A's documents even with matching filters
    async def test_filters_are_owner_scoped(self, auth_client: AsyncClient) -> None:
        token_a = await self._setup(auth_client, "fa@example.com")
        a_body = await self._search(
            auth_client, token_a, q="aadhaar", document_type="unclassified"
        )
        assert a_body["document_count"] == 1
        token_b, _user_b = await register_and_login(auth_client, "fb@example.com")
        today = date.today().isoformat()
        body = await self._search(
            auth_client, token_b, q="aadhaar", document_type="unclassified", added_after=today
        )
        assert body["document_count"] == 0  # B sees none of A's documents

    # 12. attribute results are filtered by their supporting document (consistency)
    async def test_attribute_results_respect_document_filters(
        self, auth_app: FastAPI, auth_client: AsyncClient
    ) -> None:
        token, _uid, doc_id = await _register_and_upload(auth_client, "f12@example.com")
        await _persist_run_with_name(auth_app.state.session_factory, doc_id, name="Priya Sharma")
        today = date.today().isoformat()
        tomorrow = (date.today() + timedelta(days=1)).isoformat()
        # supporting document added today → attribute survives an added_after=today filter
        included = await self._search(auth_client, token, q="priya", added_after=today)
        assert included["attribute_count"] == 1
        # a filter excluding the supporting document also drops the attribute match
        excluded = await self._search(auth_client, token, q="priya", added_after=tomorrow)
        assert excluded["attribute_count"] == 0
