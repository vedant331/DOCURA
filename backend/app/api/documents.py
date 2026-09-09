"""Document vault endpoints (FR-UPL-001…005/007, FR-DOC-001/004/007, NFR-SEC-003/007).

Five routes, and no more. There is deliberately no ``/users/{id}/documents`` and no
way to name an owner: identity comes from the session, exactly as it does in Sprint
2's ``/users/me``, so one account has no vocabulary for addressing another's vault.
The isolation is structural rather than a check that a future endpoint could forget.

NFR-SEC-007 asks that document access be time-limited and single-purpose, and that
no link grant standing access. This sprint satisfies it by not issuing links at
all: the only way to read bytes is an authenticated request carrying a session that
expires on inactivity and can be revoked (NFR-SEC-005). A pre-signed URL would
introduce a second, weaker credential with its own expiry to get wrong.
"""

from __future__ import annotations

import uuid
from urllib.parse import quote

from fastapi import APIRouter, File, UploadFile, status
from fastapi.responses import StreamingResponse

from app.api.deps import AppSettings, CurrentUser, DbSession, DocumentStore
from app.core.errors import DocuraError, UnsupportedDocumentError
from app.core.logging import get_logger
from app.db.models import Document
from app.schemas.documents import (
    DocumentDeletionResponse,
    DocumentListResponse,
    DocumentResponse,
    RejectedUpload,
    UploadLimits,
    UploadResponse,
)
from app.services.document_service import (
    delete_document,
    get_document,
    list_documents,
    open_document_content,
    request_reprocess,
    store_document,
)
from app.services.document_validation import (
    ACCEPTED_EXTENSIONS,
    ACCEPTED_MEDIA_TYPES,
    sanitise_filename,
)
from app.services.storage import stream_object

logger = get_logger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


def _to_response(document: Document) -> DocumentResponse:
    """Project a row onto its public shape.

    Field by field, for the same reason ``_to_user_response`` is: an ORM-wide
    conversion would start returning ``storage_key`` the day the model gains a
    field, and the storage key is the one thing on this row the owner must not see.
    """
    return DocumentResponse(
        id=document.id,
        original_filename=document.original_filename,
        content_type=document.content_type,
        byte_size=document.byte_size,
        checksum_sha256=document.checksum_sha256,
        document_type=document.document_type,
        status=document.status,
        failure_reason=document.failure_reason,
        created_at=document.created_at,
        updated_at=document.updated_at,
    )


def _content_disposition(filename: str) -> str:
    """Build an RFC 6266 header that preserves the user's own filename.

    Both forms are sent: ``filename*`` carries the real name for anything built this
    century, and the quoted ASCII form is the fallback. The name has already been
    stripped of quotes, separators, and control characters by
    :func:`sanitise_filename`, so this cannot inject a header — the transliteration
    below is the second layer, not the first.
    """
    ascii_fallback = filename.encode("ascii", "replace").decode("ascii")
    ascii_fallback = ascii_fallback.replace('"', "_").replace("\\", "_")
    return f"attachment; filename=\"{ascii_fallback}\"; filename*=UTF-8''{quote(filename, safe='')}"


@router.get(
    "/limits",
    response_model=UploadLimits,
    summary="What this vault accepts",
)
async def read_limits(user: CurrentUser, settings: AppSettings) -> UploadLimits:
    """State the limits before a file is chosen (FR-UPL-003).

    Authenticated like everything else in the vault: FR-ACC-002 requires
    authentication before any document surface is readable, and there is no reason
    for an anonymous caller to learn how this deployment is configured.
    """
    return UploadLimits(
        accepted_media_types=list(ACCEPTED_MEDIA_TYPES),
        accepted_extensions=list(ACCEPTED_EXTENSIONS),
        max_document_bytes=settings.max_document_bytes,
        max_documents_per_upload=settings.max_documents_per_upload,
    )


@router.post(
    "",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload one or more documents",
)
async def upload_documents(
    user: CurrentUser,
    db: DbSession,
    settings: AppSettings,
    storage: DocumentStore,
    files: list[UploadFile] = File(  # noqa: B008 — FastAPI resolves this per request
        ...,
        description="One or more PDF, JPG, or PNG files.",
    ),
) -> UploadResponse:
    """Accept a batch of files into the caller's vault (FR-UPL-001, FR-UPL-002).

    Each file is judged on its own. One unsupported file in a batch of five does not
    discard the other four — NFR-ERR-003 requires partial success to be reported as
    partial and itemised, and AC-US-002-2 expects every *accepted* file to appear as
    its own document. When nothing at all was accepted there is no partial success
    to report, so the request fails with the error the file itself caused: a
    rejected single upload returns 415, 413, or 409 rather than a 201 with an empty
    list, which would read as success.
    """
    if len(files) > settings.max_documents_per_upload:
        raise UnsupportedDocumentError(
            detail=(
                f"This request carries {len(files)} files; the limit is "
                f"{settings.max_documents_per_upload} per upload."
            ),
            remediation=(f"Upload at most {settings.max_documents_per_upload} files at a time."),
        )

    accepted: list[DocumentResponse] = []
    rejected: list[RejectedUpload] = []
    first_error: DocuraError | None = None

    for upload in files:
        try:
            document = await store_document(
                db,
                owner=user,
                source=upload.file,
                filename=upload.filename,
                declared_content_type=upload.content_type,
                storage=storage,
                settings=settings,
            )
        except DocuraError as exc:
            first_error = first_error or exc
            rejected.append(
                RejectedUpload(
                    filename=_safe_label(upload.filename),
                    reason=exc.detail,
                    remediation=exc.remediation,
                )
            )
            continue
        finally:
            await upload.close()

        accepted.append(_to_response(document))

    if not accepted and first_error is not None:
        raise first_error

    logger.info(
        "document.upload_completed",
        user_id=str(user.id),
        accepted=len(accepted),
        rejected=len(rejected),
    )
    return UploadResponse(accepted=accepted, rejected=rejected)


def _safe_label(filename: str | None) -> str:
    """A name safe to put in a response body, even for a file that was refused.

    A rejected upload still has to be identifiable to the user, and its name is
    still attacker-controlled, so it goes through the same sanitiser. A name so
    broken that even the sanitiser refuses it is reported as unnamed rather than
    echoed raw.
    """
    try:
        return sanitise_filename(filename)
    except DocuraError:
        return "(unnamed file)"


@router.get(
    "",
    response_model=DocumentListResponse,
    summary="List this account's documents",
)
async def list_own_documents(user: CurrentUser, db: DbSession) -> DocumentListResponse:
    """The vault listing (FR-DOC-001).

    Scoped to ``user.id`` taken from the authenticated session. No filter, sort, or
    identifier the caller supplies can widen it, and file contents never appear
    here — this endpoint answers "what do I have", not "give me my documents".
    """
    documents = await list_documents(db, user_id=user.id)
    items = [_to_response(document) for document in documents]
    return DocumentListResponse(documents=items, count=len(items))


@router.get(
    "/{document_id}",
    response_model=DocumentResponse,
    summary="One document's metadata",
)
async def read_document(
    document_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> DocumentResponse:
    """Metadata for a single document, if this account owns it (NFR-SEC-003).

    ``document_id`` narrows a set already restricted to the caller; it never
    identifies the owner. A document belonging to somebody else answers 404, exactly
    as a nonexistent one does.
    """
    document = await get_document(db, user_id=user.id, document_id=document_id)
    return _to_response(document)


@router.get(
    "/{document_id}/content",
    response_class=StreamingResponse,
    summary="Download the original file",
    responses={200: {"content": {"application/octet-stream": {}}, "description": "The file."}},
)
async def download_document(
    document_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    storage: DocumentStore,
) -> StreamingResponse:
    """Serve the original exactly as uploaded (FR-DOC-004, BR-013).

    Ownership is settled before the object is opened, the response is streamed so a
    large scan is never held in memory, and the body is the stored bytes unchanged —
    no transcoding, no resizing. Preparing a constraint-compliant *copy* is
    FR-MATCH-006 and belongs to the form-filling sprint; it will never be done here,
    because BR-013 makes the original immutable.
    """
    document = await get_document(db, user_id=user.id, document_id=document_id)
    handle = open_document_content(document, storage=storage)

    logger.info(
        "document.downloaded",
        user_id=str(user.id),
        document_ref=str(document.id),
        content_type=document.content_type,
    )
    return StreamingResponse(
        stream_object(handle),
        media_type=document.content_type,
        headers={
            "Content-Disposition": _content_disposition(document.original_filename),
            "Content-Length": str(document.byte_size),
        },
    )


@router.post(
    "/{document_id}/reprocess",
    response_model=DocumentResponse,
    summary="Reprocess a document",
)
async def reprocess_document(
    document_id: uuid.UUID, user: CurrentUser, db: DbSession
) -> DocumentResponse:
    """Queue a document to be read again (FR-OCR-010).

    Owner-scoped like everything else: a document another account owns answers 404.
    The document returns to 'queued' and the worker picks it up; a document still in
    flight is refused with 409 rather than run twice. Nothing about the stored
    original changes (BR-013).
    """
    document = await request_reprocess(db, user_id=user.id, document_id=document_id)
    return _to_response(document)


@router.delete(
    "/{document_id}",
    response_model=DocumentDeletionResponse,
    summary="Delete a document",
)
async def remove_document(
    document_id: uuid.UUID,
    user: CurrentUser,
    db: DbSession,
    storage: DocumentStore,
) -> DocumentDeletionResponse:
    """Destroy one document and its stored file (FR-DOC-007, BR-018).

    The response names what went, because FR-DOC-007 requires the user to be told
    what is lost. Deleting the same document twice answers 404 the second time: it
    is gone, and the vault says so rather than pretending to delete it again.
    """
    removed = await delete_document(db, user_id=user.id, document_id=document_id, storage=storage)
    return DocumentDeletionResponse(
        id=removed.id,
        original_filename=removed.original_filename,
        content_type=removed.content_type,
        byte_size=removed.byte_size,
        detail=(
            f"'{removed.original_filename}' and its stored file were removed. "
            "This cannot be undone."
        ),
    )
