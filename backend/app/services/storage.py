"""Object storage for uploaded originals.

The vault keeps two separate things: *metadata*, which lives in PostgreSQL and is
queried, and *bytes*, which live here and are only ever streamed in and out by an
opaque key. Nothing above this module knows whether those bytes are on a local
disk, in object storage, or behind a KMS-backed envelope — that is the whole point
of :class:`DocumentStorage`, and it is what lets NFR-SEC-002 (encryption at rest)
be satisfied by substituting a backend rather than by rewriting the vault.

Three properties are load-bearing and are enforced here rather than trusted to the
callers:

* **A key is never derived from user input.** Keys are minted from the system
  CSPRNG, so a filename — however hostile — can never name a storage location.
* **A key is validated before it touches the filesystem**, and the resolved path is
  re-checked against the root. Path traversal therefore has to defeat a whitelist
  regex *and* a containment check, not just one of them.
* **A write is atomic.** Bytes land in a temporary file and are renamed into place,
  so a failed or interrupted upload leaves no half-written object that a later read
  could serve as if it were whole (NFR-REL-002).
"""

from __future__ import annotations

import os
import re
import secrets
from collections.abc import Iterator
from pathlib import Path
from typing import BinaryIO, Protocol

from app.core.config import Settings
from app.core.errors import DocumentStorageError
from app.core.logging import get_logger

logger = get_logger(__name__)

# Two levels of two hex characters, then the object itself. Sharding keeps any one
# directory small; the shape is fixed so that the pattern below can be exact.
_KEY_PATTERN = re.compile(r"^[0-9a-f]{2}/[0-9a-f]{2}/[0-9a-f]{32}$")

_STORAGE_KEY_BYTES = 16
STORAGE_KEY_MAX_LENGTH = 40  # "ab/cd/" + 32 hex characters

# Owner-only. On POSIX this is the difference between "another account on this host
# can read the vault" and "it cannot"; on Windows the mode bits are largely
# advisory, and the real control is the directory's ACL, set by the deployment.
_DIR_MODE = 0o700
_FILE_MODE = 0o600

_COPY_CHUNK_BYTES = 64 * 1024


class StorageKeyError(ValueError):
    """A key did not match the minted format.

    Deliberately not a :class:`~app.core.errors.DocuraError`: reaching this means a
    key that the service itself minted has been corrupted or forged, which is a bug
    or an attack, not a condition a user should be given a remediation for.
    """


def generate_storage_key() -> str:
    """Mint a fresh, unguessable object key.

    128 bits from the CSPRNG. It is not the document's primary key, and not a hash
    of its contents: either would make one identifier predictable from the other,
    and a content hash would additionally let anyone holding a copy of a file
    confirm whether some user had stored it.
    """
    token = secrets.token_hex(_STORAGE_KEY_BYTES)
    return f"{token[0:2]}/{token[2:4]}/{token}"


class DocumentStorage(Protocol):
    """What the vault needs from a place to keep bytes."""

    def save(self, key: str, source: BinaryIO) -> int:
        """Write ``source`` under ``key``, returning the number of bytes stored."""
        ...

    def open(self, key: str) -> BinaryIO:
        """Open the stored object for reading. The caller closes it."""
        ...

    def delete(self, key: str) -> bool:
        """Remove the object. Returns False if it was already absent."""
        ...

    def exists(self, key: str) -> bool:
        """True when an object is stored under ``key``."""
        ...


class LocalFileStorage:
    """A :class:`DocumentStorage` backed by a directory on this host.

    Intended for development and for the automated suite. It is deliberately not
    presented as production storage: it provides no encryption at rest, so a
    deployment that must satisfy NFR-SEC-002 either mounts an encrypted volume
    underneath it or substitutes a backend that encrypts.
    """

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._ensure_root()

    @property
    def root(self) -> Path:
        """The configured base directory. Never exposed through the API."""
        return self._root

    def _ensure_root(self) -> None:
        try:
            self._root.mkdir(mode=_DIR_MODE, parents=True, exist_ok=True)
        except OSError as exc:
            # The path is in the message because it is operator-facing configuration,
            # and this is raised at startup, not into a response.
            logger.error("storage.root_unusable", error_class=type(exc).__name__)
            msg = f"document storage root is not usable: {self._root}"
            raise DocumentStorageError(msg) from exc

    def _path_for(self, key: str) -> Path:
        """Resolve a key to a path, refusing anything that escapes the root.

        Both checks are kept even though either alone would stop the classic
        ``../../etc/passwd``: the pattern rejects the input, and the containment
        check catches a symlinked shard or a normalisation quirk that the pattern
        could not see.
        """
        if not _KEY_PATTERN.fullmatch(key):
            raise StorageKeyError("storage key is not in the minted format")

        candidate = (self._root / key).resolve()
        if candidate != self._root and self._root not in candidate.parents:
            raise StorageKeyError("storage key resolves outside the storage root")
        return candidate

    def save(self, key: str, source: BinaryIO) -> int:
        """Stream ``source`` into place atomically."""
        target = self._path_for(key)
        try:
            target.parent.mkdir(mode=_DIR_MODE, parents=True, exist_ok=True)
        except OSError as exc:
            logger.error("storage.write_failed", stage="mkdir", error_class=type(exc).__name__)
            raise DocumentStorageError from exc

        # Same directory as the target, so the rename below is on one filesystem and
        # is therefore atomic rather than a copy that can be observed half-done.
        temporary = target.with_name(f".{target.name}.{secrets.token_hex(4)}.part")
        written = 0
        try:
            with temporary.open("wb") as handle:
                while chunk := source.read(_COPY_CHUNK_BYTES):
                    handle.write(chunk)
                    written += len(chunk)
                handle.flush()
                os.fsync(handle.fileno())
            temporary.chmod(_FILE_MODE)
            # os.replace rather than Path.rename: it is the atomic overwrite, and
            # Path has no equivalent that is atomic on every platform.
            os.replace(temporary, target)
        except OSError as exc:
            temporary.unlink(missing_ok=True)
            logger.error("storage.write_failed", stage="write", error_class=type(exc).__name__)
            raise DocumentStorageError from exc
        return written

    def open(self, key: str) -> BinaryIO:
        path = self._path_for(key)
        try:
            return path.open("rb")
        except FileNotFoundError as exc:
            logger.warning("storage.object_missing", operation="open")
            raise DocumentStorageError from exc
        except OSError as exc:
            logger.error("storage.read_failed", error_class=type(exc).__name__)
            raise DocumentStorageError from exc

    def delete(self, key: str) -> bool:
        path = self._path_for(key)
        try:
            path.unlink()
        except FileNotFoundError:
            # Already gone is the outcome the caller wanted, so deletion is
            # idempotent rather than an error the user has to understand.
            return False
        except OSError as exc:
            logger.error("storage.delete_failed", error_class=type(exc).__name__)
            raise DocumentStorageError from exc
        return True

    def exists(self, key: str) -> bool:
        try:
            return self._path_for(key).is_file()
        except StorageKeyError:
            return False


class SupabaseStorage:
    """A :class:`DocumentStorage` backed by a private Supabase Storage bucket.

    The production backend for Vercel and any other read-only serverless filesystem:
    nothing is written to local disk, so startup never tries to create a document
    root. Bytes live in the configured bucket and are addressed by the same minted
    key as the local backend, so nothing above this module changes.

    Authorization is unchanged. The service-role key bypasses row-level security, and
    that is correct here: ownership is enforced one layer up by ``document_service``'s
    ``user_id`` ``WHERE`` clauses, and keys are unguessable, so the bucket is a dumb
    byte store. The key must stay server-side (never a ``VITE_`` variable).

    ponytail: calls the Supabase Storage REST API directly with httpx (already a
    dependency) rather than pulling in the ``supabase`` SDK for four HTTP calls. The
    client is synchronous, matching LocalFileStorage's blocking disk I/O; switch to
    an async client only if these blocking calls measurably starve the event loop.
    """

    def __init__(self, *, base_url: str, service_key: str, bucket: str) -> None:
        import httpx  # lazy: only imported when the production backend is selected

        self._bucket = bucket
        self._client = httpx.Client(
            base_url=f"{base_url.rstrip('/')}/storage/v1",
            headers={
                "Authorization": f"Bearer {service_key}",
                "apikey": service_key,
            },
            timeout=30.0,
        )

    @staticmethod
    def _check_key(key: str) -> None:
        # Defence in depth: the key is always minted and stored server-side, but it
        # goes into a URL path here, so it is validated exactly as the local backend
        # validates before touching the filesystem.
        if not _KEY_PATTERN.fullmatch(key):
            raise StorageKeyError("storage key is not in the minted format")

    def _object_path(self, key: str) -> str:
        return f"/object/{self._bucket}/{key}"

    def save(self, key: str, source: BinaryIO) -> int:
        self._check_key(key)
        # Documents are capped at max_document_bytes (10 MiB default), so reading the
        # original into memory to POST it is bounded and simple.
        data = source.read()
        try:
            response = self._client.post(
                self._object_path(key),
                content=data,
                headers={"Content-Type": "application/octet-stream"},
            )
            response.raise_for_status()
        except Exception as exc:
            logger.error("storage.write_failed", stage="upload", error_class=type(exc).__name__)
            raise DocumentStorageError from exc
        return len(data)

    def open(self, key: str) -> BinaryIO:
        self._check_key(key)
        try:
            response = self._client.get(self._object_path(key))
            response.raise_for_status()
        except Exception as exc:
            logger.warning("storage.object_missing", operation="open")
            raise DocumentStorageError from exc
        import io

        return io.BytesIO(response.content)

    def delete(self, key: str) -> bool:
        self._check_key(key)
        try:
            response = self._client.delete(self._object_path(key))
            response.raise_for_status()
        except Exception as exc:
            logger.error("storage.delete_failed", error_class=type(exc).__name__)
            raise DocumentStorageError from exc
        # Supabase returns the list of objects it removed; an empty list means the
        # object was already gone, which is the idempotent "already absent" outcome.
        try:
            removed = response.json()
        except ValueError:
            return True
        return bool(removed)

    def exists(self, key: str) -> bool:
        if not _KEY_PATTERN.fullmatch(key):
            return False
        response = self._client.get(f"/object/info/{self._bucket}/{key}")
        return response.status_code == 200


def stream_object(handle: BinaryIO, chunk_size: int = _COPY_CHUNK_BYTES) -> Iterator[bytes]:
    """Yield an open object in chunks and close it, for a streaming response.

    Written as a generator so a large PDF is never held in memory in full, and
    wrapped in ``finally`` so the handle closes even if the client disconnects
    part-way through the download.
    """
    try:
        while chunk := handle.read(chunk_size):
            yield chunk
    finally:
        handle.close()


def build_document_storage(settings: Settings) -> DocumentStorage:
    """Construct the configured backend.

    One function decides what the vault writes to. Production (Vercel) sets the
    Supabase variables and gets object storage that never touches local disk; local
    development and tests leave them unset and get LocalFileStorage.
    """
    key = settings.supabase_service_role_key
    if settings.supabase_storage_configured and key is not None:
        return SupabaseStorage(
            base_url=settings.supabase_url,
            service_key=key.get_secret_value(),
            bucket=settings.supabase_storage_bucket,
        )
    return LocalFileStorage(settings.document_storage_root)
