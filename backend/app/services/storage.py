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

    One function decides what the vault writes to, so a future object-store backend
    is a change here and nowhere else.
    """
    return LocalFileStorage(settings.document_storage_root)
