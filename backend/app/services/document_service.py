"""Document vault logic: store, list, read, and destroy an owner's documents.

Every function here takes ``user_id`` as a keyword argument and puts it in the
``WHERE`` clause. That is not a stylistic preference. NFR-SEC-003 says ownership
"shall never be inferred from an identifier supplied by the client", and the way to
guarantee that is to make the owner part of the *query* rather than a condition
checked against a row that has already been loaded: a filter that is missing makes
the query return nothing, whereas a post-hoc check that is missing makes it return
someone else's document.

The endpoints never call storage directly. They call these functions, which own the
one ordering decision that matters — see :func:`delete_document`.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import BinaryIO

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import DocumentNotFoundError, DocumentStorageError, DuplicateDocumentError
from app.core.logging import get_logger
from app.db.models import Document, DocumentStatus, DocumentType, User
from app.services.document_validation import ValidatedUpload, validate_upload
from app.services.storage import DocumentStorage, generate_storage_key

logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class DeletedDocument:
    """What a deleted document was, captured before the row was removed.

    FR-DOC-007 requires the user to be told what is lost, so the response has to
    name the document after it no longer exists. A plain value object is used rather
    than the detached ORM row, because a detached row invites a lazy load against a
    session that has already forgotten it.
    """

    id: uuid.UUID
    original_filename: str
    content_type: str
    byte_size: int
    created_at: datetime
    object_removed: bool


async def _existing_by_checksum(
    db: AsyncSession, *, user_id: uuid.UUID, checksum: str
) -> Document | None:
    existing: Document | None = await db.scalar(
        select(Document).where(
            Document.user_id == user_id,
            Document.checksum_sha256 == checksum,
        )
    )
    return existing


async def store_document(
    db: AsyncSession,
    *,
    owner: User,
    source: BinaryIO,
    filename: str | None,
    declared_content_type: str | None,
    storage: DocumentStorage,
    settings: Settings,
) -> Document:
    """Validate one uploaded file and admit it to the vault.

    The sequence is validate, then write bytes, then write the row, and it is in
    that order for a reason: validation can refuse without having touched anything,
    and if the metadata insert fails the orphaned object is removed before the error
    propagates. What must never happen is the reverse — a row the user can see whose
    bytes were never written (NFR-REL-002, BR-016).
    """
    validated: ValidatedUpload = validate_upload(
        source,
        filename=filename,
        declared=declared_content_type,
        max_bytes=settings.max_document_bytes,
    )

    # Checked before the write so that an obvious duplicate does not cost a copy of
    # the file. The unique index is what actually guarantees it; this is the polite
    # path, and the IntegrityError below is the correct one.
    duplicate = await _existing_by_checksum(
        db, user_id=owner.id, checksum=validated.checksum_sha256
    )
    if duplicate is not None:
        raise DuplicateDocumentError(
            detail=(f"An identical file is already stored as '{duplicate.original_filename}'."),
            remediation=(
                "Open the document you already have, or upload a different file. "
                "Replacing or versioning a document is not available yet."
            ),
        )

    storage_key = generate_storage_key()
    source.seek(0)
    written = storage.save(storage_key, source)

    document = Document(
        user_id=owner.id,
        original_filename=validated.filename,
        storage_key=storage_key,
        content_type=validated.content_type,
        byte_size=written,
        checksum_sha256=validated.checksum_sha256,
        document_type=DocumentType.UNCLASSIFIED,
        # Nothing moves it out of `queued` in this sprint; the extraction pipeline
        # that does is FR-OCR work.
        status=DocumentStatus.QUEUED,
    )
    db.add(document)

    try:
        await db.flush()
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        # Two uploads of the same bytes raced past the check above. Undo this one's
        # write so the loser leaves nothing behind.
        _discard_object(storage, storage_key)
        raise DuplicateDocumentError from exc
    except Exception:
        await db.rollback()
        _discard_object(storage, storage_key)
        raise

    # Deliberately narrow: an identifier, a size, and a type. No filename, no
    # checksum, no storage key — a filename alone can name a person and a document
    # type, and BR-017/NFR-PRIV-007 keep that out of a log sink.
    logger.info(
        "document.stored",
        user_id=str(owner.id),
        document_ref=str(document.id),
        content_type=document.content_type,
        byte_size=document.byte_size,
        status=document.status.value,
    )
    return document


def _discard_object(storage: DocumentStorage, key: str) -> None:
    """Best-effort cleanup of bytes whose row did not survive.

    Swallows storage failure on purpose: the caller is already raising the error the
    user needs to see, and replacing it with a cleanup failure would report the
    wrong problem. The leftover is logged so it can be swept.
    """
    try:
        storage.delete(key)
    except DocumentStorageError:
        logger.error("document.orphaned_object", reason="rollback_cleanup_failed")


async def list_documents(db: AsyncSession, *, user_id: uuid.UUID) -> list[Document]:
    """The vault listing for one account, newest first (FR-DOC-001).

    No pagination. The approved requirements do not ask for it — NFR-SCL-003 leaves
    per-user record size limits TBD — and an unused paging contract would be harder
    to remove later than to add.
    """
    result = await db.scalars(
        select(Document)
        .where(Document.user_id == user_id)
        .order_by(Document.created_at.desc(), Document.id.desc())
    )
    return list(result)


async def get_document(db: AsyncSession, *, user_id: uuid.UUID, document_id: uuid.UUID) -> Document:
    """One document belonging to this account, or a 404.

    A document owned by somebody else and a document that does not exist produce the
    identical answer. Distinguishing them would let a caller confirm which ids are
    real, and on a vault of identity documents that alone is a disclosure.
    """
    document = await db.scalar(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == user_id,
        )
    )
    if document is None:
        logger.info("document.access_denied", user_id=str(user_id))
        raise DocumentNotFoundError
    return document


def open_document_content(document: Document, *, storage: DocumentStorage) -> BinaryIO:
    """Open the stored original exactly as uploaded (FR-DOC-004, BR-013).

    The handle is returned rather than the bytes so the response can stream it. The
    caller has already been through :func:`get_document`, so ownership is settled
    before a single byte is read.
    """
    return storage.open(document.storage_key)


async def delete_document(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    document_id: uuid.UUID,
    storage: DocumentStorage,
) -> DeletedDocument:
    """Destroy one document — its row first, then its bytes (FR-DOC-007).

    The ordering is the whole design of this function.

    Removing the row and committing *before* touching storage means the only state
    that can survive a partial failure is bytes with no row: unreachable, because
    the key that named them is gone with the row, and sweepable. The other order
    risks the state that is actually harmful — a row the user can see whose file no
    longer exists, so that the vault lists a document it cannot serve.

    A missing storage object is not an error. It is the outcome the caller asked
    for, and a delete that failed because the file was already gone would leave the
    user unable to remove the record at all.

    FR-DOC-008's recovery grace period is deliberately *not* implemented. Its length
    is marked TBD in the approved requirements, and a soft delete with no configured
    period would keep a user's identity documents indefinitely while telling them
    the documents were deleted — which is the opposite of what BR-018 promises.
    """
    document = await get_document(db, user_id=user_id, document_id=document_id)

    # Read off what the response has to name before the row goes away.
    storage_key = document.storage_key
    document_id_removed = document.id
    original_filename = document.original_filename
    content_type = document.content_type
    byte_size = document.byte_size
    created_at = document.created_at

    await db.delete(document)
    await db.commit()

    try:
        object_removed = storage.delete(storage_key)
    except DocumentStorageError:
        # The user's record is already gone, which is what they asked for, so this
        # does not become their error. It is logged as an operational leftover.
        logger.error("document.orphaned_object", reason="delete_failed", user_id=str(user_id))
        object_removed = False

    logger.info(
        "document.deleted",
        user_id=str(user_id),
        document_ref=str(document_id_removed),
        object_removed=object_removed,
    )
    return DeletedDocument(
        id=document_id_removed,
        original_filename=original_filename,
        content_type=content_type,
        byte_size=byte_size,
        created_at=created_at,
        object_removed=object_removed,
    )
