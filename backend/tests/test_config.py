"""Configuration loading, validation, and secret handling."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import pytest
from pydantic import SecretStr, ValidationError

from app.core.config import (
    ConfigurationError,
    Environment,
    LogLevel,
    Settings,
    get_settings,
    load_settings,
)
from tests.conftest import TEST_DSN


class TestRequiredValues:
    def test_loads_from_environment(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DOCURA_DATABASE_URL", TEST_DSN)
        monkeypatch.setenv("DOCURA_ENVIRONMENT", "staging")
        monkeypatch.setenv("DOCURA_LOG_LEVEL", "WARNING")

        loaded = load_settings()

        assert loaded.environment is Environment.STAGING
        assert loaded.log_level is LogLevel.WARNING
        assert loaded.database_url.get_secret_value() == TEST_DSN

    def test_missing_database_url_is_a_configuration_error(self) -> None:
        with pytest.raises(ConfigurationError) as exc_info:
            load_settings()

        message = str(exc_info.value)
        assert "DOCURA_DATABASE_URL" in message
        assert "Invalid configuration" in message

    def test_no_secret_has_a_default(self) -> None:
        """A credential with a default is a credential in source control."""
        assert Settings.model_fields["database_url"].is_required()


class TestValidation:
    @pytest.mark.parametrize(
        "dsn",
        [
            "not-a-url",
            "mysql://user:pass@localhost:3306/docura",
            "postgresql://user:pass@localhost:5432/",
            "",
        ],
    )
    def test_rejects_unusable_dsn(self, dsn: str) -> None:
        with pytest.raises(ValidationError):
            Settings(environment=Environment.TEST, database_url=dsn)

    def test_rejects_wildcard_cors_origin(self) -> None:
        with pytest.raises(ValidationError, match="explicit allowlist"):
            Settings(
                environment=Environment.TEST,
                database_url=TEST_DSN,
                cors_allow_origins=("https://app.docura.test", "*"),
            )

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [
            ("  https://ref.supabase.co  ", "https://ref.supabase.co"),
            ('"https://ref.supabase.co"', "https://ref.supabase.co"),
            ("'https://ref.supabase.co'", "https://ref.supabase.co"),
            ("https://ref.supabase.co\n", "https://ref.supabase.co"),
            ("", ""),
        ],
    )
    def test_supabase_url_paste_artifacts_are_cleaned(self, raw: str, expected: str) -> None:
        """Quotes/whitespace/newline that would yield a scheme-less httpx base_url
        (httpx.UnsupportedProtocol on upload) are stripped so the URL stays usable."""
        loaded = Settings(
            environment=Environment.TEST, database_url=TEST_DSN, supabase_url=raw
        )
        assert loaded.supabase_url == expected

    @pytest.mark.parametrize("bad", ["ref.supabase.co", "ftp://ref.supabase.co"])
    def test_supabase_url_without_http_scheme_is_rejected(self, bad: str) -> None:
        """A scheme-less URL fails loudly at startup, not as an opaque per-request 503."""
        with pytest.raises(ValidationError, match="http"):
            Settings(
                environment=Environment.TEST, database_url=TEST_DSN, supabase_url=bad
            )

    def test_rejects_unknown_docura_variable(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A typo must fail startup, not silently leave a default in place."""
        monkeypatch.setenv("DOCURA_DATABASE_URL", TEST_DSN)
        monkeypatch.setenv("DOCURA_DATABSE_POOL_SIZE", "20")

        with pytest.raises(ConfigurationError):
            load_settings()

    @pytest.mark.parametrize("port", [0, 70000])
    def test_rejects_out_of_range_port(self, port: int) -> None:
        with pytest.raises(ValidationError):
            Settings(
                environment=Environment.TEST,
                database_url=TEST_DSN,
                port=port,
            )


class TestSecretHandling:
    def test_password_absent_from_repr_and_str(self, settings: Settings) -> None:
        assert "test_password" not in repr(settings)
        assert "test_password" not in str(settings)
        assert "test_password" not in repr(settings.database_url)

    def test_password_absent_from_model_dump(self, settings: Settings) -> None:
        assert "test_password" not in str(settings.model_dump())

    def test_display_url_drops_credentials(self, settings: Settings) -> None:
        display = settings.database_display_url

        assert "test_password" not in display
        assert "test_user" not in display
        assert "localhost:5432" in display
        assert "docura_test" in display

    def test_configuration_error_never_echoes_the_secret(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setenv("DOCURA_DATABASE_URL", "mysql://real_user:hunter2@db.internal:3306/prod")

        with pytest.raises(ConfigurationError) as exc_info:
            load_settings()

        assert "hunter2" not in str(exc_info.value)
        assert "real_user" not in str(exc_info.value)


class TestDerivedValues:
    def test_async_driver_is_applied(self, settings: Settings) -> None:
        assert settings.async_database_url.startswith("postgresql+asyncpg://")

    def test_async_driver_is_not_doubled(self) -> None:
        already_async = Settings(
            environment=Environment.TEST,
            database_url=SecretStr(TEST_DSN.replace("postgresql://", "postgresql+asyncpg://")),
        )
        assert already_async.async_database_url.count("asyncpg") == 1

    @pytest.mark.parametrize(
        ("environment", "expected"),
        [
            (Environment.LOCAL, False),
            (Environment.TEST, False),
            (Environment.STAGING, True),
            (Environment.PRODUCTION, True),
        ],
    )
    def test_json_logs_default_by_environment(
        self, environment: Environment, expected: bool
    ) -> None:
        loaded = Settings(environment=environment, database_url=TEST_DSN)
        assert loaded.render_json_logs is expected

    def test_log_json_override_wins(self) -> None:
        loaded = Settings(
            environment=Environment.PRODUCTION,
            database_url=TEST_DSN,
            log_json=False,
        )
        assert loaded.render_json_logs is False

    def test_production_hides_error_detail(self) -> None:
        production = Settings(
            environment=Environment.PRODUCTION,
            database_url=TEST_DSN,
        )
        assert production.expose_error_detail is False


class TestSingleton:
    def test_get_settings_is_cached(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("DOCURA_DATABASE_URL", TEST_DSN)
        assert get_settings() is get_settings()


class TestDotEnvFile:
    """The .env file is shared with docker-compose, which owns POSTGRES_*.

    ``DotEnvSettingsSource`` forwards *every* key in the file into the model, not
    just the ``DOCURA_``-prefixed ones, so the application has to be explicit about
    which namespace it owns.
    """

    @staticmethod
    def _write_env(tmp_path: Path, body: str) -> None:
        (tmp_path / ".env").write_text(dedent(body).strip() + "\n", encoding="utf-8")

    def test_loads_alongside_compose_variables(self, tmp_path: Path) -> None:
        """POSTGRES_* belong to docker-compose and must not break app startup."""
        self._write_env(
            tmp_path,
            """
            DOCURA_ENVIRONMENT=local
            DOCURA_DATABASE_URL=postgresql://u:p@localhost:5433/docura
            POSTGRES_USER=u
            POSTGRES_PASSWORD=p
            POSTGRES_DB=docura
            POSTGRES_HOST_PORT=5433
            """,
        )

        loaded = load_settings()

        assert loaded.environment is Environment.LOCAL
        assert loaded.database_url.get_secret_value().endswith("/docura")

    def test_compose_credentials_are_not_absorbed_as_settings(self, tmp_path: Path) -> None:
        """Ignoring a foreign key must mean ignoring it, not stashing it on the model."""
        self._write_env(
            tmp_path,
            """
            DOCURA_DATABASE_URL=postgresql://u:p@localhost:5433/docura
            POSTGRES_PASSWORD=compose_only_secret
            """,
        )

        loaded = load_settings()

        assert "compose_only_secret" not in str(loaded.model_dump())
        assert not hasattr(loaded, "postgres_password")

    def test_typo_in_the_env_file_still_fails(self, tmp_path: Path) -> None:
        """Strictness is preserved: an unknown DOCURA_* key is a configuration error."""
        self._write_env(
            tmp_path,
            """
            DOCURA_DATABASE_URL=postgresql://u:p@localhost:5433/docura
            DOCURA_DATABSE_POOL_SIZE=20
            """,
        )

        with pytest.raises(ConfigurationError, match="DOCURA_DATABSE_POOL_SIZE"):
            load_settings()

    def test_env_file_values_are_applied(self, tmp_path: Path) -> None:
        self._write_env(
            tmp_path,
            """
            DOCURA_DATABASE_URL=postgresql://u:p@localhost:5433/docura
            DOCURA_PORT=8123
            POSTGRES_USER=u
            """,
        )

        assert load_settings().port == 8123

    def test_unknown_docura_key_is_named_without_double_prefix(self, tmp_path: Path) -> None:
        """The old message read DOCURA_DOCURA_PG_HOST_PORT — the prefix was applied twice."""
        self._write_env(
            tmp_path,
            """
            DOCURA_DATABASE_URL=postgresql://u:p@localhost:5433/docura
            DOCURA_PG_HOST_PORT=5433
            """,
        )

        with pytest.raises(ConfigurationError) as exc_info:
            load_settings()

        assert "DOCURA_DOCURA_" not in str(exc_info.value)
        assert "DOCURA_PG_HOST_PORT" in str(exc_info.value)
