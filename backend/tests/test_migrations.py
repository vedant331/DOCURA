"""S2-T013 — the Alembic migrations build the schema the models expect.

The application fixtures build tables from model metadata, which is fast but would
not notice a migration that drifted from the models. This runs the migration itself
against a scratch database and compares the result.
"""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

import pytest
from sqlalchemy import create_engine as create_sync_engine
from sqlalchemy import inspect, text
from sqlalchemy.engine import Engine

from tests.conftest import INTEGRATION_DSN, requires_postgres

pytestmark = requires_postgres

BACKEND_ROOT = Path(__file__).resolve().parent.parent
MIGRATION_TEST_DB = "docura_migration_check"


def _plain_dsn(dsn: str, database: str) -> str:
    """A driverless DSN, which is what ``DOCURA_DATABASE_URL`` accepts.

    The application's config validator deliberately allows only ``postgresql``,
    ``postgres``, and ``postgresql+asyncpg``, and applies the async driver itself.
    """
    parts = urlsplit(dsn)
    return urlunsplit(("postgresql", parts.netloc, f"/{database}", "", ""))


def _inspection_engine(dsn: str) -> Engine:
    """A synchronous engine for schema inspection.

    SQLAlchemy's bare ``postgresql://`` resolves to psycopg2, which this project
    does not install, so psycopg3 is named explicitly.
    """
    parts = urlsplit(dsn)
    psycopg_dsn = urlunsplit(("postgresql+psycopg", parts.netloc, parts.path, "", ""))
    return create_sync_engine(psycopg_dsn)


@pytest.fixture
def scratch_database() -> Iterator[str]:
    """A database created and dropped around the test, so the run leaves no trace."""
    assert INTEGRATION_DSN is not None
    admin_dsn = _plain_dsn(INTEGRATION_DSN, "postgres")

    admin = _inspection_engine(admin_dsn).execution_options(isolation_level="AUTOCOMMIT")
    with admin.connect() as connection:
        connection.execute(text(f'DROP DATABASE IF EXISTS "{MIGRATION_TEST_DB}"'))
        connection.execute(text(f'CREATE DATABASE "{MIGRATION_TEST_DB}"'))
    admin.dispose()

    try:
        yield _plain_dsn(INTEGRATION_DSN, MIGRATION_TEST_DB)
    finally:
        admin = _inspection_engine(admin_dsn).execution_options(isolation_level="AUTOCOMMIT")
        with admin.connect() as connection:
            connection.execute(text(f'DROP DATABASE IF EXISTS "{MIGRATION_TEST_DB}"'))
        admin.dispose()


def _run_alembic(*args: str, dsn: str) -> subprocess.CompletedProcess[str]:
    environment = {
        **os.environ,
        "DOCURA_DATABASE_URL": dsn,
        "DOCURA_ENVIRONMENT": "test",
    }
    return subprocess.run(  # noqa: S603 — fixed argv, no shell, no user input
        [sys.executable, "-m", "alembic", *args],
        cwd=BACKEND_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


class TestMigration:
    def test_upgrade_head_creates_the_expected_schema(self, scratch_database: str) -> None:
        """S2-T013."""
        result = _run_alembic("upgrade", "head", dsn=scratch_database)
        assert result.returncode == 0, result.stderr

        engine = _inspection_engine(scratch_database)
        try:
            inspector = inspect(engine)
            tables = set(inspector.get_table_names())

            assert {
                "users",
                "sessions",
                "password_reset_tokens",
                "documents",
                "alembic_version",
            } <= tables

            user_columns = {c["name"] for c in inspector.get_columns("users")}
            assert user_columns == {
                "id",
                "email",
                "password_hash",
                "is_active",
                "created_at",
                "updated_at",
            }

            session_columns = {c["name"] for c in inspector.get_columns("sessions")}
            assert session_columns == {
                "id",
                "user_id",
                "token_hash",
                "created_at",
                "expires_at",
                "absolute_expires_at",
                "last_used_at",
                "revoked_at",
            }

            reset_columns = {c["name"] for c in inspector.get_columns("password_reset_tokens")}
            assert reset_columns == {
                "id",
                "user_id",
                "token_hash",
                "created_at",
                "expires_at",
                "used_at",
            }

            document_columns = {c["name"] for c in inspector.get_columns("documents")}
            assert document_columns == {
                "id",
                "user_id",
                "original_filename",
                "storage_key",
                "content_type",
                "byte_size",
                "checksum_sha256",
                "document_type",
                "status",
                "created_at",
                "updated_at",
            }
        finally:
            engine.dispose()

    def test_no_later_sprint_tables_are_created(self, scratch_database: str) -> None:
        """Sprint 3 owns accounts, sessions, reset tokens, and documents — nothing later.

        This is the check that keeps OCR, extracted attributes, and form sessions
        out of the schema until the sprint that actually implements them. A table
        added early is a shape committed to before the requirement that would have
        defined it.
        """
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            tables = set(inspect(engine).get_table_names())
        finally:
            engine.dispose()

        assert tables == {
            "users",
            "sessions",
            "password_reset_tokens",
            "documents",
            "alembic_version",
        }

    def test_documents_carry_no_extraction_columns_yet(self, scratch_database: str) -> None:
        """Sprint 3 is the vault. OCR output has no column to land in.

        Named explicitly rather than left to the column-set assertion above, because
        this is the boundary most likely to be crossed by accident.
        """
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            columns = {c["name"] for c in inspect(engine).get_columns("documents")}
        finally:
            engine.dispose()

        forbidden = {
            "extracted_text",
            "ocr_text",
            "classification_confidence",
            "confidence",
            "extracted_fields",
        }
        assert not (columns & forbidden)

    def test_a_users_documents_are_unique_by_checksum(self, scratch_database: str) -> None:
        """AC-US-002-4 — 'no silent duplicate' is held by the database, not by a check."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            indexes = inspect(engine).get_indexes("documents")
            checksum_indexes = [
                index
                for index in indexes
                if index["column_names"] == ["user_id", "checksum_sha256"]
            ]

            assert checksum_indexes, "no index on (user_id, checksum_sha256)"
            assert any(index["unique"] for index in checksum_indexes)
        finally:
            engine.dispose()

    def test_documents_cascade_when_an_account_is_deleted(self, scratch_database: str) -> None:
        """FR-ACC-007, NFR-PRIV-003 — a deleted account leaves no orphaned document rows."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            foreign_keys = inspect(engine).get_foreign_keys("documents")
            user_fk = next(fk for fk in foreign_keys if fk["referred_table"] == "users")

            assert user_fk["options"].get("ondelete") == "CASCADE"
        finally:
            engine.dispose()

    def test_email_uniqueness_is_enforced_by_the_database(self, scratch_database: str) -> None:
        """Application-level checks race; the constraint is what actually holds."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            indexes = inspect(engine).get_indexes("users")
            email_indexes = [i for i in indexes if i["column_names"] == ["email"]]

            assert email_indexes, "no index on users.email"
            assert any(i["unique"] for i in email_indexes)
        finally:
            engine.dispose()

    def test_downgrade_reverses_cleanly(self, scratch_database: str) -> None:
        """A migration that cannot be rolled back is a one-way door in production."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        result = _run_alembic("downgrade", "base", dsn=scratch_database)
        assert result.returncode == 0, result.stderr

        engine = _inspection_engine(scratch_database)
        try:
            tables = set(inspect(engine).get_table_names())
        finally:
            engine.dispose()

        assert "users" not in tables
        assert "sessions" not in tables
        assert "password_reset_tokens" not in tables
        assert "documents" not in tables

    def test_upgrade_after_a_downgrade_still_works(self, scratch_database: str) -> None:
        """The enum types have to go on the way down, or the next upgrade collides.

        ``op.drop_table`` leaves a PostgreSQL enum type in place. Without the
        explicit drops in the Sprint 3 downgrade this passes once and fails the
        second time, which is the worst way for a migration to be wrong.
        """
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0
        assert _run_alembic("downgrade", "base", dsn=scratch_database).returncode == 0

        result = _run_alembic("upgrade", "head", dsn=scratch_database)
        assert result.returncode == 0, result.stderr

        engine = _inspection_engine(scratch_database)
        try:
            assert "documents" in set(inspect(engine).get_table_names())
        finally:
            engine.dispose()

    def test_sessions_cascade_when_an_account_is_deleted(self, scratch_database: str) -> None:
        """FR-ACC-007 will delete accounts; sessions must not outlive their owner."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            foreign_keys = inspect(engine).get_foreign_keys("sessions")
            user_fk = next(fk for fk in foreign_keys if fk["referred_table"] == "users")

            assert user_fk["options"].get("ondelete") == "CASCADE"
        finally:
            engine.dispose()

    def test_reset_tokens_cascade_when_an_account_is_deleted(self, scratch_database: str) -> None:
        """An outstanding reset link must not survive the account it opens."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            foreign_keys = inspect(engine).get_foreign_keys("password_reset_tokens")
            user_fk = next(fk for fk in foreign_keys if fk["referred_table"] == "users")

            assert user_fk["options"].get("ondelete") == "CASCADE"
        finally:
            engine.dispose()

    def test_reset_token_digest_is_unique(self, scratch_database: str) -> None:
        """Two rows sharing a digest would make the confirm lookup ambiguous."""
        assert _run_alembic("upgrade", "head", dsn=scratch_database).returncode == 0

        engine = _inspection_engine(scratch_database)
        try:
            indexes = inspect(engine).get_indexes("password_reset_tokens")
            digest_indexes = [i for i in indexes if i["column_names"] == ["token_hash"]]

            assert digest_indexes, "no index on password_reset_tokens.token_hash"
            assert any(i["unique"] for i in digest_indexes)
        finally:
            engine.dispose()

    def test_alembic_ini_holds_no_credential(self) -> None:
        """The DSN comes from settings; a URL committed here would be a leaked secret."""
        ini = (BACKEND_ROOT / "alembic.ini").read_text(encoding="utf-8")

        for line in ini.splitlines():
            if line.strip().startswith("sqlalchemy.url"):
                assert line.split("=", 1)[1].strip() == ""
