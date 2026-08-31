"""File validation, applied before a byte is accepted into the vault.

FR-UPL-003 and FR-UPL-004 set the shape of this module: check type and size
*before* acceptance, state the limits in advance, and reject with a message naming
both the reason and the accepted alternatives. Table 7.1 adds integrity to that
list, which is why a declared content type is never taken at its word.

The order of checks is deliberate. The filename is sanitised first, because it is
the only field a hostile client fully controls and it is the one that later reaches
a response header. The size ceiling is applied *while* reading rather than
afterwards, so an oversized upload is abandoned part-way instead of being buffered
in full and then rejected. The type is decided last, and by the file's own leading
bytes: an extension and a ``Content-Type`` are both claims made by the sender, and
a vault that accepted them would be trusting the upload to describe itself.
"""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from typing import BinaryIO

from app.core.errors import DocumentTooLargeError, UnsupportedDocumentError
from app.db.models import FILENAME_MAX_LENGTH

# The three types FR-UPL-001 names, and nothing else. Each maps to its magic
# signature and the extensions that may carry it.
PDF_MEDIA_TYPE = "application/pdf"
JPEG_MEDIA_TYPE = "image/jpeg"
PNG_MEDIA_TYPE = "image/png"

_SIGNATURES: tuple[tuple[str, bytes], ...] = (
    # ISO 32000-1 §7.5.2. Some producers emit a short preamble before the header, so
    # it is looked for near the start rather than only at offset zero.
    (PDF_MEDIA_TYPE, b"%PDF-"),
    # SOI marker followed by the first segment's marker byte.
    (JPEG_MEDIA_TYPE, b"\xff\xd8\xff"),
    # RFC 2083 §3.1 — the CR/LF pair is what detects a corrupting text-mode transfer.
    (PNG_MEDIA_TYPE, b"\x89PNG\r\n\x1a\n"),
)

_EXTENSIONS: dict[str, str] = {
    ".pdf": PDF_MEDIA_TYPE,
    ".jpg": JPEG_MEDIA_TYPE,
    ".jpeg": JPEG_MEDIA_TYPE,
    ".png": PNG_MEDIA_TYPE,
}

ACCEPTED_MEDIA_TYPES: tuple[str, ...] = (PDF_MEDIA_TYPE, JPEG_MEDIA_TYPE, PNG_MEDIA_TYPE)
ACCEPTED_EXTENSIONS: tuple[str, ...] = tuple(sorted(_EXTENSIONS))

# Human phrasing for the "accepted alternatives" half of FR-UPL-004.
ACCEPTED_DESCRIPTION = "PDF, JPG, or PNG"

# How much of the file the signature check reads. Generous enough for a PDF
# preamble, small enough that it is one buffer.
_HEADER_BYTES = 1024
_READ_CHUNK_BYTES = 64 * 1024

# Characters that must not survive into a filename: path separators either way, the
# Windows reserved set, and every C0/C1 control including NUL, CR and LF. The last
# group matters twice over — they would corrupt a Content-Disposition header and a
# log line alike.
_UNSAFE_FILENAME = re.compile(r'[\x00-\x1f\x7f-\x9f/\\:*?"<>|]')

_GENERIC_MEDIA_TYPES = frozenset(
    {"", "application/octet-stream", "binary/octet-stream", "application/x-download"}
)


@dataclass(frozen=True, slots=True)
class ValidatedUpload:
    """What validation established about one file. No contents, by construction."""

    filename: str
    content_type: str
    byte_size: int
    checksum_sha256: str


def sanitise_filename(raw: str | None) -> str:
    """Reduce a client-supplied name to something safe to store and to echo back.

    This name is *display metadata only* — the vault finds bytes by an opaque
    storage key, never by this string — so the job here is not to make a safe path.
    It is to make sure that whatever ends up in the database, in a
    ``Content-Disposition`` header, and on the user's own disk after a download
    cannot be a traversal sequence, a header injection, or an invisible mess.
    """
    candidate = (raw or "").strip()

    # Split on both separators regardless of host: a Windows client may well send
    # "C:\\Users\\me\\aadhaar.pdf", and a POSIX-only basename would keep all of it.
    for separator in ("\\", "/"):
        candidate = candidate.rsplit(separator, 1)[-1]

    # NFC first, so that a name which normalises *into* a separator or a control
    # character cannot slip past the substitution below.
    candidate = unicodedata.normalize("NFC", candidate)
    candidate = _UNSAFE_FILENAME.sub("_", candidate)

    # Leading dots hide the file; trailing dots and spaces are silently dropped by
    # Windows, which would make the stored name and the written name disagree.
    candidate = candidate.strip().strip(". ")

    if not candidate or candidate in {".", ".."}:
        raise UnsupportedDocumentError(
            detail="The upload did not carry a usable filename.",
            remediation=(
                f"Send the file with its original name and a "
                f"{'/'.join(ACCEPTED_EXTENSIONS)} extension."
            ),
        )

    if len(candidate) > FILENAME_MAX_LENGTH:
        # Truncate the stem, not the extension: the extension is what the type check
        # and the user's own operating system both read.
        stem, dot, suffix = candidate.rpartition(".")
        if dot and len(suffix) < FILENAME_MAX_LENGTH:
            keep = FILENAME_MAX_LENGTH - len(suffix) - 1
            candidate = f"{stem[:keep]}.{suffix}"
        else:
            candidate = candidate[:FILENAME_MAX_LENGTH]

    return candidate


def _extension_media_type(filename: str) -> str | None:
    _, dot, suffix = filename.rpartition(".")
    if not dot:
        return None
    return _EXTENSIONS.get(f".{suffix.lower()}")


def _sniff_media_type(header: bytes) -> str | None:
    """Identify the file from its own leading bytes, or return None."""
    for media_type, signature in _SIGNATURES:
        if media_type == PDF_MEDIA_TYPE:
            if header.startswith(signature) or signature in header[:_HEADER_BYTES]:
                return media_type
        elif header.startswith(signature):
            return media_type
    return None


def _reject_type(reason: str) -> UnsupportedDocumentError:
    """Build a rejection that names the reason *and* the alternatives (FR-UPL-004)."""
    return UnsupportedDocumentError(
        detail=reason,
        remediation=f"Upload a {ACCEPTED_DESCRIPTION} file instead.",
    )


def resolve_media_type(filename: str, declared: str | None, header: bytes) -> str:
    """Decide the file's type, or refuse it.

    Three claims are compared: the extension, the ``Content-Type`` the client sent,
    and the signature in the bytes. The signature decides — it is the only one the
    sender cannot get wrong by accident or change by choice — and the other two must
    not contradict it. A ``.png`` holding a PDF is rejected rather than silently
    re-typed, because the name the user will later download it under would then
    describe something it is not.
    """
    if not header:
        raise _reject_type("The file is empty, so there is nothing to store.")

    extension_type = _extension_media_type(filename)
    if extension_type is None:
        raise _reject_type(
            f"That file does not have an accepted extension ({', '.join(ACCEPTED_EXTENSIONS)})."
        )

    sniffed = _sniff_media_type(header)
    if sniffed is None:
        # Covers both "not one of ours" and "one of ours but damaged at the front",
        # which from the outside are the same observation.
        raise _reject_type(
            "The file's contents are not a readable PDF, JPG, or PNG. "
            "It may be of another type, or damaged."
        )

    if sniffed != extension_type:
        raise _reject_type(f"The file is named as {extension_type} but its contents are {sniffed}.")

    normalised_declared = (declared or "").split(";", 1)[0].strip().lower()
    if normalised_declared not in _GENERIC_MEDIA_TYPES and normalised_declared != sniffed:
        raise _reject_type(
            f"The upload declared {normalised_declared} but the file's contents are {sniffed}."
        )

    return sniffed


def measure_and_validate(source: BinaryIO, *, filename: str, max_bytes: int) -> tuple[int, str]:
    """Read the whole stream once, enforcing the size ceiling and hashing as it goes.

    Returns the byte count and the SHA-256 digest. Reading in chunks and stopping at
    the ceiling is the point: an oversized file is refused after ``max_bytes`` have
    been seen, not after all of it has been.

    The stream is left at its end; the caller rewinds it before storing.
    """
    digest = hashlib.sha256()
    total = 0

    while chunk := source.read(_READ_CHUNK_BYTES):
        total += len(chunk)
        if total > max_bytes:
            raise DocumentTooLargeError(
                detail=(
                    f"'{filename}' is larger than the {max_bytes} byte limit for a single document."
                ),
                remediation=(f"Upload a file of {max_bytes} bytes or less, or split the document."),
            )
        digest.update(chunk)

    if total == 0:
        raise _reject_type(f"'{filename}' is empty, so there is nothing to store.")

    return total, digest.hexdigest()


def validate_upload(
    source: BinaryIO,
    *,
    filename: str | None,
    declared: str | None,
    max_bytes: int,
) -> ValidatedUpload:
    """Run every check against one uploaded file and describe what passed.

    Nothing here writes, and nothing here touches the database. A caller that gets a
    :class:`ValidatedUpload` back knows the file is an accepted type, within the
    limit, non-empty, and safely named — and a caller that gets an exception knows
    the vault was not modified (BR-016).
    """
    safe_name = sanitise_filename(filename)

    source.seek(0)
    header = source.read(_HEADER_BYTES)
    content_type = resolve_media_type(safe_name, declared, header)

    source.seek(0)
    byte_size, checksum = measure_and_validate(source, filename=safe_name, max_bytes=max_bytes)
    source.seek(0)

    return ValidatedUpload(
        filename=safe_name,
        content_type=content_type,
        byte_size=byte_size,
        checksum_sha256=checksum,
    )
