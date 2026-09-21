"""Sprint 3 — the storage boundary, and the filename handling in front of it.

These are unit tests on purpose. The HTTP suite proves the vault behaves; this
proves the two properties that a request cannot easily reach: that a key which
tries to leave the storage root is refused rather than followed, and that a
filename is reduced to something inert before anything is done with it.

S3-T016 is tested from both ends. The API end shows that a hostile filename does
not escape the configured location; this file shows *why* — the name never becomes
a path in the first place, and the key that does become a path is checked twice.
"""

from __future__ import annotations

import io
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

if TYPE_CHECKING:
    from app.core.config import Settings

from app.core.errors import DocumentStorageError, UnsupportedDocumentError
from app.services.document_validation import sanitise_filename
from app.services.storage import (
    LocalFileStorage,
    StorageKeyError,
    SupabaseStorage,
    build_document_storage,
    generate_storage_key,
    stream_object,
)


@pytest.fixture
def storage(tmp_path: Path) -> LocalFileStorage:
    return LocalFileStorage(tmp_path / "vault")


class TestStorageKeys:
    def test_a_minted_key_has_the_expected_shape(self) -> None:
        key = generate_storage_key()

        prefix_a, prefix_b, name = key.split("/")
        assert len(prefix_a) == len(prefix_b) == 2
        assert len(name) == 32
        assert name.startswith(prefix_a + prefix_b)

    def test_keys_are_unguessable(self) -> None:
        """128 bits from the CSPRNG: a thousand draws must not collide or repeat."""
        keys = {generate_storage_key() for _ in range(1000)}
        assert len(keys) == 1000

    @pytest.mark.parametrize(
        "key",
        [
            "../../../etc/passwd",
            "ab/cd/../../../../etc/passwd",
            "ab/cd/" + "a" * 32 + "/../../../secret",
            "/etc/passwd",
            "C:/Windows/System32/config/SAM",
            "ab\\cd\\" + "f" * 32,
            "ab/cd/" + "g" * 32,  # 'g' is not hex
            "ab/cd/" + "a" * 31,
            "",
            "ab/cd/" + "a" * 32 + "\x00.png",
        ],
    )
    def test_a_key_that_is_not_a_minted_key_is_refused(
        self, storage: LocalFileStorage, key: str
    ) -> None:
        """S3-T016 — nothing outside the minted format ever becomes a path."""
        with pytest.raises(StorageKeyError):
            storage.save(key, io.BytesIO(b"payload"))

    def test_a_traversing_key_writes_nothing_anywhere(
        self, storage: LocalFileStorage, tmp_path: Path
    ) -> None:
        """S3-T016 — the refusal is not merely an error; no file appears outside the root."""
        outside = tmp_path / "outside.txt"

        with pytest.raises(StorageKeyError):
            storage.save("../outside.txt", io.BytesIO(b"escaped"))

        assert not outside.exists()
        assert list(storage.root.rglob("*")) == []

    def test_exists_answers_false_for_a_malformed_key(self, storage: LocalFileStorage) -> None:
        """A probe with a hostile key is a plain 'no', not an exception to handle."""
        assert storage.exists("../../etc/passwd") is False


class TestLocalFileStorage:
    def test_save_then_open_returns_the_same_bytes(self, storage: LocalFileStorage) -> None:
        key = generate_storage_key()
        payload = b"%PDF-1.7 the original, unmodified"

        written = storage.save(key, io.BytesIO(payload))

        assert written == len(payload)
        with storage.open(key) as handle:
            assert handle.read() == payload

    def test_save_is_atomic_and_leaves_no_partial_file(self, storage: LocalFileStorage) -> None:
        """A completed write leaves exactly one object, with no ``.part`` beside it."""
        key = generate_storage_key()
        storage.save(key, io.BytesIO(b"x" * 200_000))

        files = [path.name for path in storage.root.rglob("*") if path.is_file()]
        assert len(files) == 1
        assert not any(name.endswith(".part") for name in files)

    def test_a_failed_write_leaves_nothing_behind(self, storage: LocalFileStorage) -> None:
        """NFR-REL-002 — an interrupted upload must not leave a readable half-object."""

        class ExplodingStream(io.RawIOBase):
            def __init__(self) -> None:
                self._served = False

            def read(self, size: int = -1) -> bytes:
                if self._served:
                    raise OSError("the connection dropped")
                self._served = True
                return b"first chunk"

        key = generate_storage_key()
        with pytest.raises(DocumentStorageError):
            storage.save(key, ExplodingStream())  # type: ignore[arg-type]

        assert [path for path in storage.root.rglob("*") if path.is_file()] == []
        assert storage.exists(key) is False

    def test_open_on_a_missing_object_is_a_storage_error(self, storage: LocalFileStorage) -> None:
        with pytest.raises(DocumentStorageError):
            storage.open(generate_storage_key())

    def test_delete_is_idempotent(self, storage: LocalFileStorage) -> None:
        key = generate_storage_key()
        storage.save(key, io.BytesIO(b"payload"))

        assert storage.delete(key) is True
        assert storage.delete(key) is False
        assert storage.exists(key) is False

    def test_the_root_is_created_on_construction(self, tmp_path: Path) -> None:
        root = tmp_path / "nested" / "vault"
        assert not root.exists()

        LocalFileStorage(root)

        assert root.is_dir()

    def test_build_uses_the_configured_root(self, tmp_path: Path) -> None:
        """The location is configuration, never a path compiled into the code."""
        from app.core.config import Environment, Settings

        settings = Settings(
            environment=Environment.TEST,
            database_url="postgresql://u:p@localhost:5432/d",
            document_storage_root=tmp_path / "configured",
        )

        built = build_document_storage(settings)

        assert isinstance(built, LocalFileStorage)
        assert built.root == (tmp_path / "configured").resolve()

    def test_stream_object_closes_the_handle(self, storage: LocalFileStorage) -> None:
        key = generate_storage_key()
        storage.save(key, io.BytesIO(b"abcdef"))
        handle = storage.open(key)

        assert b"".join(stream_object(handle, chunk_size=2)) == b"abcdef"
        assert handle.closed


class TestBackendSelection:
    """build_document_storage picks the backend from configuration alone."""

    def _settings(self, **overrides: object) -> Settings:
        from app.core.config import Environment, Settings

        base: dict[str, object] = {
            "environment": Environment.PRODUCTION,
            "database_url": "postgresql://u:p@localhost:5432/d",
        }
        base.update(overrides)
        return Settings(**base)  # type: ignore[arg-type]

    def test_production_config_selects_supabase(self) -> None:
        settings = self._settings(
            supabase_url="https://proj.supabase.co",
            supabase_service_role_key="service-role-secret",
        )
        assert settings.supabase_storage_configured is True
        assert isinstance(build_document_storage(settings), SupabaseStorage)

    def test_local_config_selects_local_file_storage(self, tmp_path: Path) -> None:
        from app.core.config import Environment, Settings

        settings = Settings(
            environment=Environment.LOCAL,
            database_url="postgresql://u:p@localhost:5432/d",
            document_storage_root=tmp_path / "vault",
        )
        assert settings.supabase_storage_configured is False
        assert isinstance(build_document_storage(settings), LocalFileStorage)

    def test_url_without_key_stays_local(self, tmp_path: Path) -> None:
        settings = self._settings(
            document_storage_root=tmp_path / "vault",
            supabase_url="https://proj.supabase.co",
        )
        assert isinstance(build_document_storage(settings), LocalFileStorage)


class TestSupabaseStorage:
    """The REST request logic, driven against an in-memory bucket."""

    def _storage(self) -> SupabaseStorage:
        import httpx

        bucket: dict[str, bytes] = {}

        def handler(request: httpx.Request) -> httpx.Response:
            # Path shape: /storage/v1/object[/info]/{bucket}/{key...}
            parts = request.url.path.split("/storage/v1/object", 1)[1].lstrip("/")
            if parts.startswith("info/"):
                key = parts.split("/", 2)[2]
                return httpx.Response(200 if key in bucket else 404)
            key = parts.split("/", 1)[1]
            if request.method == "POST":
                bucket[key] = request.content
                return httpx.Response(200, json={"Key": key})
            if request.method == "GET":
                if key not in bucket:
                    return httpx.Response(404, json={"error": "not found"})
                return httpx.Response(200, content=bucket[key])
            if request.method == "DELETE":
                removed = [{"name": key}] if bucket.pop(key, None) is not None else []
                return httpx.Response(200, json=removed)
            return httpx.Response(405)  # pragma: no cover

        storage = SupabaseStorage(
            base_url="https://proj.supabase.co",
            service_key="service-role-secret",
            bucket="documents",
        )
        storage._client = httpx.Client(
            base_url="https://proj.supabase.co/storage/v1",
            transport=httpx.MockTransport(handler),
        )
        return storage

    def test_save_then_open_returns_the_same_bytes(self) -> None:
        storage = self._storage()
        key = generate_storage_key()
        payload = b"%PDF-1.7 the original, unmodified"

        assert storage.save(key, io.BytesIO(payload)) == len(payload)
        with storage.open(key) as handle:
            assert handle.read() == payload

    def test_open_on_a_missing_object_is_a_storage_error(self) -> None:
        with pytest.raises(DocumentStorageError):
            self._storage().open(generate_storage_key())

    def test_delete_is_idempotent(self) -> None:
        storage = self._storage()
        key = generate_storage_key()
        storage.save(key, io.BytesIO(b"payload"))

        assert storage.delete(key) is True
        assert storage.delete(key) is False
        assert storage.exists(key) is False

    def test_exists_tracks_the_stored_object(self) -> None:
        storage = self._storage()
        key = generate_storage_key()
        assert storage.exists(key) is False
        storage.save(key, io.BytesIO(b"x"))
        assert storage.exists(key) is True

    @pytest.mark.parametrize("key", ["../../etc/passwd", "ab/cd/" + "g" * 32, ""])
    def test_a_malformed_key_never_reaches_the_api(self, key: str) -> None:
        storage = self._storage()
        with pytest.raises(StorageKeyError):
            storage.save(key, io.BytesIO(b"payload"))
        assert storage.exists(key) is False


class TestFilenameSanitisation:
    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("marksheet.pdf", "marksheet.pdf"),
            ("../../../etc/passwd.pdf", "passwd.pdf"),
            (r"..\..\Windows\System32\evil.pdf", "evil.pdf"),
            ("/absolute/path/scan.png", "scan.png"),
            (r"C:\Users\me\Desktop\aadhaar.jpg", "aadhaar.jpg"),
            ("  spaced.pdf  ", "spaced.pdf"),
            ("trailing.pdf...", "trailing.pdf"),
            ("....hidden.pdf", "hidden.pdf"),
            ("with:colon.pdf", "with_colon.pdf"),
            ('quote".pdf', "quote_.pdf"),
            ("pipe|star*.pdf", "pipe_star_.pdf"),
        ],
    )
    def test_a_hostile_name_is_reduced_to_a_plain_one(self, raw: str, expected: str) -> None:
        """S3-T016 — the name is display metadata, and is made inert before it is stored."""
        assert sanitise_filename(raw) == expected

    def test_control_characters_cannot_reach_a_header_or_a_log(self) -> None:
        """CR and LF in a filename would split a Content-Disposition header."""
        cleaned = sanitise_filename("report\r\nX-Injected: yes.pdf")

        assert "\r" not in cleaned
        assert "\n" not in cleaned
        assert "\x00" not in sanitise_filename("nul\x00byte.pdf")

    @pytest.mark.parametrize("raw", ["", "   ", ".", "..", "../", "/", "...", None])
    def test_a_name_with_nothing_left_is_refused(self, raw: str | None) -> None:
        """Rejected rather than replaced by a generated name: the user chose nothing."""
        with pytest.raises(UnsupportedDocumentError):
            sanitise_filename(raw)

    def test_an_overlong_name_is_truncated_but_keeps_its_extension(self) -> None:
        """The extension is what the type check and the user's own OS both read."""
        cleaned = sanitise_filename("a" * 400 + ".pdf")

        assert len(cleaned) == 255
        assert cleaned.endswith(".pdf")
