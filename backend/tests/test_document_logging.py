"""S3-T018 — no document content, filename, or storage location reaches a log sink.

The same shape as ``test_auth_logging.py``, and for the same reason: proving the
redaction processor masks a named key proves that the *mechanism* works, not that
the application uses it. What matters is the property — drive real vault traffic
through the real logging pipeline and find nothing of the document in the output —
because that holds whether or not the next person to add a log line remembers.

Three things are checked separately, because they leak for different reasons.
Contents are the obvious one (BR-017, NFR-PRIV-007). A *filename* is the quiet one:
on a document vault it names a person and a document type before a byte is read.
The storage key is the third: it says where DOCURA keeps the file, and belongs in
no operational log (NFR-ERR-004).
"""

from __future__ import annotations

import io
import logging
from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from tests.conftest import (
    JPEG_BYTES,
    PDF_BYTES,
    RecordingResetDelivery,
    auth_header,
    register_and_login,
    requires_postgres,
    upload_document,
    upload_file,
)

pytestmark = requires_postgres

# Distinctive enough that a substring search cannot match it by accident.
SECRET_CONTENT_MARKER = "AADHAAR-9876-5432-1098-PRIYA-SHARMA"
REVEALING_FILENAME = "aadhaar-priya-sharma-1998.pdf"


@pytest.fixture
def log_sink() -> io.StringIO:
    return io.StringIO()


@pytest.fixture
async def logging_client(
    db_settings: Settings,
    db_engine: Any,
    log_sink: io.StringIO,
    reset_delivery: RecordingResetDelivery,
) -> Any:
    """An app rendering JSON logs into ``log_sink``.

    The handler is attached after ``create_app``, which clears root handlers as it
    configures logging, and it borrows the real formatter so what lands in the sink
    is what would have landed on stdout — redaction included.
    """
    from app.api.auth import reset_rate_limiter
    from app.db.session import create_session_factory
    from app.main import create_app

    reset_rate_limiter()
    app = create_app(db_settings.model_copy(update={"log_json": True, "log_level": "DEBUG"}))
    app.state.engine = db_engine
    app.state.session_factory = create_session_factory(db_engine)
    app.state.reset_delivery = reset_delivery

    root = logging.getLogger()
    handler = logging.StreamHandler(log_sink)
    handler.setFormatter(root.handlers[0].formatter)
    root.addHandler(handler)

    transport = ASGITransport(app=app, raise_app_exceptions=False)
    try:
        async with AsyncClient(transport=transport, base_url="http://testserver") as client:
            yield client
    finally:
        root.removeHandler(handler)
        reset_rate_limiter()


async def _drive_the_whole_vault(client: AsyncClient) -> str:
    """Upload, list, read, download, and delete — every route that touches a document."""
    token, _ = await register_and_login(client, "logging@docura.example")
    headers = auth_header(token)

    content = PDF_BYTES + f"% {SECRET_CONTENT_MARKER}\n".encode()
    document = await upload_document(client, token, content=content, filename=REVEALING_FILENAME)

    await client.get("/documents", headers=headers)
    await client.get(f"/documents/{document['id']}", headers=headers)
    await client.get(f"/documents/{document['id']}/content", headers=headers)
    await client.delete(f"/documents/{document['id']}", headers=headers)
    return token


class TestDocumentLogging:
    async def test_document_contents_never_appear_in_logs(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """S3-T018 — BR-017, NFR-PRIV-007."""
        await _drive_the_whole_vault(logging_client)

        logs = log_sink.getvalue()

        assert logs, "the pipeline emitted nothing, so this test proved nothing"
        assert SECRET_CONTENT_MARKER not in logs
        assert "%PDF" not in logs

    async def test_filenames_never_appear_in_logs(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """A filename on this product names a person and a document type."""
        await _drive_the_whole_vault(logging_client)

        logs = log_sink.getvalue()

        assert REVEALING_FILENAME not in logs
        assert "priya" not in logs.lower()

    async def test_storage_locations_never_appear_in_logs(
        self, logging_client: AsyncClient, log_sink: io.StringIO, db_settings: Settings
    ) -> None:
        """NFR-ERR-004 — where DOCURA keeps a file is not operational context."""
        await _drive_the_whole_vault(logging_client)

        logs = log_sink.getvalue()

        assert str(db_settings.document_storage_root) not in logs
        assert "storage_key" not in logs

    async def test_a_rejected_upload_does_not_log_the_file_it_refused(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """A file DOCURA would not store is a file it certainly must not write to a log."""
        token, _ = await register_and_login(logging_client, "rejected@docura.example")
        rejected_marker = b"REJECTED-PAYLOAD-MARKER-4471"

        await logging_client.post(
            "/documents",
            headers=auth_header(token),
            files=upload_file(rejected_marker, "secret-notes.exe", "application/exe"),
        )

        logs = log_sink.getvalue()

        assert rejected_marker.decode() not in logs
        assert "secret-notes.exe" not in logs

    async def test_the_redaction_still_fires_on_an_explicitly_named_field(
        self, logging_client: AsyncClient, log_sink: io.StringIO
    ) -> None:
        """The processor is the backstop, so it is checked directly as well.

        If some future log call does pass a filename or a storage key by name, the
        pipeline masks it rather than emitting it — this asserts that safety net is
        actually wired, not merely present in the key list.
        """
        from app.core.logging import REDACTED, get_logger

        get_logger(__name__).info(
            "test.event",
            filename=REVEALING_FILENAME,
            storage_key="ab/cd/" + "0" * 32,
            document_content=JPEG_BYTES.hex(),
        )

        logs = log_sink.getvalue()

        assert REDACTED in logs
        assert REVEALING_FILENAME not in logs
