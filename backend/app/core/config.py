"""Application configuration.

Every value is read from the environment. No credential, key, or connection string
has a default here — a missing secret is a startup failure, never a silent fallback
(NFR-SEC-004 handling posture; Step 3 §2.1).
"""

from __future__ import annotations

import os
from enum import StrEnum
from functools import lru_cache
from typing import Annotated
from urllib.parse import urlsplit, urlunsplit

from pydantic import Field, PostgresDsn, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PREFIX = "DOCURA_"

_ASYNC_DRIVER = "postgresql+asyncpg"
_ACCEPTED_SCHEMES = frozenset({"postgresql", "postgres", _ASYNC_DRIVER})


class Environment(StrEnum):
    """Deployment environment. Controls log rendering and error verbosity."""

    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ConfigurationError(RuntimeError):
    """Raised when the environment does not describe a runnable application.

    The message deliberately names the offending *field*, never the offending
    *value* — values at this layer are credentials (NFR-ERR-004).
    """


class Settings(BaseSettings):
    """Validated application settings.

    ``extra="forbid"`` means a mistyped ``DOCURA_*`` variable fails startup rather
    than being silently ignored, which is how a production service ends up running
    on a default it was never meant to use.
    """

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="forbid",
        frozen=True,
        validate_default=True,
    )

    # -- Application ----------------------------------------------------------
    environment: Environment = Environment.LOCAL
    service_name: str = "docura-backend"
    version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: Annotated[int, Field(ge=1, le=65535)] = 8000

    # -- Logging --------------------------------------------------------------
    log_level: LogLevel = LogLevel.INFO
    log_json: bool | None = Field(
        default=None,
        description="Force JSON log rendering. Defaults to on outside local/test.",
    )

    # -- Database -------------------------------------------------------------
    database_url: SecretStr = Field(
        ...,
        description="PostgreSQL DSN. Required; never defaulted.",
    )
    db_pool_size: Annotated[int, Field(ge=1, le=100)] = 5
    db_max_overflow: Annotated[int, Field(ge=0, le=100)] = 5
    db_connect_timeout_seconds: Annotated[float, Field(gt=0, le=60)] = 5.0

    # -- HTTP -----------------------------------------------------------------
    cors_allow_origins: tuple[str, ...] = ()
    max_request_bytes: Annotated[int, Field(ge=1024, le=100 * 1024 * 1024)] = 1024 * 1024

    @field_validator("database_url")
    @classmethod
    def _validate_database_url(cls, value: SecretStr) -> SecretStr:
        """Confirm the DSN is a usable PostgreSQL URL without ever echoing it.

        Pydantic renders the offending input in its error output; because the field
        is a ``SecretStr`` that rendering is masked, so validation failures here stay
        free of credentials.
        """
        raw = value.get_secret_value().strip()
        if not raw:
            msg = "database_url must not be empty"
            raise ValueError(msg)
        try:
            parsed = PostgresDsn(raw)
        except ValidationError as exc:
            msg = "database_url is not a valid PostgreSQL DSN"
            raise ValueError(msg) from exc
        if parsed.scheme not in _ACCEPTED_SCHEMES:
            msg = f"database_url scheme must be one of {sorted(_ACCEPTED_SCHEMES)}"
            raise ValueError(msg)
        if not parsed.path or parsed.path == "/":
            msg = "database_url must name a database"
            raise ValueError(msg)
        return SecretStr(raw)

    @field_validator("cors_allow_origins")
    @classmethod
    def _validate_cors(cls, value: tuple[str, ...]) -> tuple[str, ...]:
        """Reject the wildcard origin outright — an allowlist or nothing."""
        if "*" in value:
            msg = "cors_allow_origins must be an explicit allowlist, not '*'"
            raise ValueError(msg)
        return value

    # -- Derived --------------------------------------------------------------
    @property
    def async_database_url(self) -> str:
        """The DSN rewritten onto the asyncpg driver SQLAlchemy needs."""
        raw = self.database_url.get_secret_value()
        scheme, _, remainder = raw.partition("://")
        if scheme == _ASYNC_DRIVER:
            return raw
        return f"{_ASYNC_DRIVER}://{remainder}"

    @property
    def database_display_url(self) -> str:
        """Host and database only — safe to log, print, or return in a response.

        Userinfo (``user:password@``) is stripped rather than masked so that no part
        of the credential survives into a log sink (NFR-OBS-004).
        """
        parts = urlsplit(self.async_database_url)
        netloc = parts.hostname or ""
        if parts.port:
            netloc = f"{netloc}:{parts.port}"
        return urlunsplit((parts.scheme, netloc, parts.path, "", ""))

    @property
    def render_json_logs(self) -> bool:
        if self.log_json is not None:
            return self.log_json
        return self.environment not in (Environment.LOCAL, Environment.TEST)

    @property
    def expose_error_detail(self) -> bool:
        """Only non-production environments may see internal failure detail."""
        return self.environment is not Environment.PRODUCTION


def _unknown_environment_variables() -> list[str]:
    """Find ``DOCURA_*`` variables that match no field.

    ``extra="forbid"`` only governs values read from a dotenv file; pydantic-settings
    silently ignores unrecognised *environment* variables. That silence is how a
    service ends up running on a default because someone wrote ``DOCURA_DATABSE_URL``,
    so the check is made explicit here.
    """
    known = {f"{ENV_PREFIX}{name.upper()}" for name in Settings.model_fields}
    return sorted(
        key for key in os.environ if key.upper().startswith(ENV_PREFIX) and key.upper() not in known
    )


def load_settings() -> Settings:
    """Build settings from the environment, converting pydantic errors into ours.

    The re-raised message lists field names and reasons only. Raw values are dropped
    so an invalid-configuration crash cannot print a password into a terminal or a
    container log.
    """
    unknown = _unknown_environment_variables()
    if unknown:
        msg = (
            "Invalid configuration - unrecognised variable(s): "
            f"{', '.join(unknown)}. Check for a typo; no default was applied."
        )
        raise ConfigurationError(msg)

    try:
        return Settings()  # values come from the environment
    except ValidationError as exc:
        problems = "; ".join(
            f"{ENV_PREFIX}{'.'.join(str(p) for p in err['loc']).upper()}: {err['msg']}"
            for err in exc.errors()
        )
        msg = f"Invalid configuration - {problems}"
        raise ConfigurationError(msg) from None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings singleton. Call ``get_settings.cache_clear()`` in tests."""
    return load_settings()
