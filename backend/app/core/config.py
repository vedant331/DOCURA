"""Application configuration.

Every value is read from the environment. No credential, key, or connection string
has a default here — a missing secret is a startup failure, never a silent fallback
(NFR-SEC-004 handling posture; Step 3 §2.1).
"""

from __future__ import annotations

import os
from enum import StrEnum
from functools import lru_cache
from pathlib import Path
from typing import Annotated
from urllib.parse import urlsplit, urlunsplit

from dotenv import dotenv_values
from pydantic import Field, PostgresDsn, SecretStr, ValidationError, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PREFIX = "DOCURA_"
ENV_FILE = ".env"

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


class LlmProvider(StrEnum):
    """Which LLM backs the chatbot's language-understanding (intent) layer.

    The default is ``NONE`` — the deterministic keyword provider is used, and no data leaves the
    backend. ``OPENAI_COMPATIBLE`` calls a configured OpenAI-style ``/chat/completions`` endpoint
    (any vendor or gateway via ``DOCURA_LLM_BASE_URL``) for intent classification ONLY, with a
    deterministic fallback on any failure. The LLM never becomes the source of truth and cannot
    override DOCURA's safety rules. An unrecognised value is a startup configuration error.
    """

    NONE = "none"
    OPENAI_COMPATIBLE = "openai_compatible"


class OcrEngine(StrEnum):
    """Which extraction engine :func:`build_document_extractor` constructs.

    The default is ``UNCONFIGURED`` — the production posture (D-01): no engine is selected
    until the S-6 held-out evaluation reports (AR-AST-008). ``TESSERACT`` is a **dev/evaluation
    opt-in only** that runs the M20/M21 candidate through the normal pipeline for local technical
    testing; it does **not** make Tesseract the production engine. An unrecognised value is a
    startup configuration error (an enum member or nothing), never a silent fallback.
    """

    UNCONFIGURED = "unconfigured"
    TESSERACT = "tesseract"


class ConfigurationError(RuntimeError):
    """Raised when the environment does not describe a runnable application.

    The message deliberately names the offending *field*, never the offending
    *value* — values at this layer are credentials (NFR-ERR-004).
    """


class Settings(BaseSettings):
    """Validated application settings.

    This application owns the ``DOCURA_`` namespace and validates it strictly: an
    unrecognised ``DOCURA_*`` name fails startup rather than leaving a default
    quietly in place. That check lives in :func:`_unknown_docura_variables`, not in
    ``extra``.

    ``extra`` must be ``"ignore"``. ``DotEnvSettingsSource`` forwards *every* key in
    the ``.env`` file into the model, prefixed or not, and this file is shared with
    ``docker-compose.yml``, which owns ``POSTGRES_*``. Under ``extra="forbid"`` those
    foreign keys are rejected as unknown fields and the service refuses to start.
    Policing another tool's variables is not this model's job.
    """

    model_config = SettingsConfigDict(
        env_prefix=ENV_PREFIX,
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
        frozen=True,
        validate_default=True,
    )

    # -- Application ----------------------------------------------------------
    environment: Environment = Environment.LOCAL
    service_name: str = "docura-backend"
    version: str = "0.1.0"

    host: str = "127.0.0.1"
    port: Annotated[int, Field(ge=1, le=65535)] = 8000

    # -- Extraction engine (D-01 / M23) ---------------------------------------
    # Which engine build_document_extractor constructs. Defaults to the unconfigured
    # extractor — the production posture until S-6 selects an engine. `tesseract` is a
    # DEV/EVALUATION opt-in (DOCURA_OCR_ENGINE=tesseract) for local technical testing of the
    # candidate through the normal pipeline; it does NOT select Tesseract for production.
    ocr_engine: OcrEngine = OcrEngine.UNCONFIGURED

    # -- Dynamic demo mode (DEV/EVALUATION only) ------------------------------
    # When true (DOCURA_DEMO_MODE=true), the field extractor uses the DEMO synonym vocabulary
    # (canonical_attributes.demo.toml) to discover common labelled key/value fields for the
    # end-to-end dynamic-autofill demo. It does NOT release those attributes for production and
    # does NOT change extraction/observation architecture. Default false = production posture
    # (only the two authored controlled attributes).
    demo_mode: bool = False

    # -- Chatbot LLM (intent understanding only) ------------------------------
    # DOCURA_LLM_PROVIDER=none (default) uses the deterministic intent provider; no data leaves
    # the backend. `openai_compatible` calls DOCURA_LLM_BASE_URL's /chat/completions with
    # DOCURA_LLM_MODEL + DOCURA_LLM_API_KEY for intent classification ONLY (bounded, value-free),
    # falling back to deterministic on any failure. Secrets come from the environment, never
    # source. If the provider is set but the key/model is missing, the deterministic provider is
    # used (treated as unconfigured), never a crash.
    llm_provider: LlmProvider = LlmProvider.NONE
    llm_model: str = ""
    llm_base_url: str = "https://api.openai.com/v1"
    llm_api_key: SecretStr | None = None
    llm_timeout_seconds: Annotated[float, Field(gt=0, le=60)] = 12.0

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

    # -- Authentication -------------------------------------------------------
    # No signing key appears here. Sessions are opaque server-side records
    # (NFR-SEC-005 requires revocation, which a self-contained token cannot honour),
    # so there is no authentication secret to configure, rotate, or leak.
    session_idle_timeout_minutes: Annotated[int, Field(ge=1, le=10_080)] = 60
    session_absolute_timeout_hours: Annotated[int, Field(ge=1, le=8_760)] = 24
    password_min_length: Annotated[int, Field(ge=12, le=1_024)] = 12
    # A reset token is a bearer credential for the account, so its life is measured
    # in minutes, not days (UC-001 A2: "the reset must not weaken the vault").
    password_reset_token_ttl_minutes: Annotated[int, Field(ge=5, le=1_440)] = 30
    auth_rate_limit_attempts: Annotated[int, Field(ge=1, le=1_000)] = 10
    auth_rate_limit_window_seconds: Annotated[int, Field(ge=1, le=3_600)] = 300

    # -- Document vault -------------------------------------------------------
    # Where uploaded originals live. Relative paths resolve against the process
    # working directory, so no machine-specific absolute path is baked in; a
    # deployment points this at its own volume via DOCURA_DOCUMENT_STORAGE_ROOT.
    document_storage_root: Path = Path("var/documents")
    # Production object storage. When both a URL and a service-role key are present,
    # build_document_storage selects the Supabase backend instead of LocalFileStorage,
    # so a read-only serverless filesystem (Vercel) is never touched. All three are
    # backend-only secrets and MUST NOT carry a VITE_ prefix — the service-role key
    # bypasses row-level security and must never reach the browser. The bucket must be
    # created (private) in the Supabase project before first upload.
    supabase_url: str = ""
    supabase_service_role_key: SecretStr | None = None
    supabase_storage_bucket: str = "documents"
    # FR-UPL-003 requires the limits be stated in advance, but no approved document
    # fixes a number. Both figures below are assumptions (Sprint 3 ASM-S3-1) chosen
    # to cover the MVP document set — a scanned multi-page marksheet, a photograph,
    # a signature — and are configurable precisely because they are not derived.
    max_document_bytes: Annotated[int, Field(ge=1024, le=100 * 1024 * 1024)] = 10 * 1024 * 1024
    max_documents_per_upload: Annotated[int, Field(ge=1, le=50)] = 5

    # -- Processing worker (Sprint 4 decision D-09) ---------------------------
    # None of these is a requirement value: the specification fixes no poll cadence,
    # retry ceiling, or claim timeout. They are operational knobs (NFR-MNT-004
    # posture), defaulted here and overridable per deployment.
    # How long an idle worker waits before polling for the next job.
    worker_poll_interval_seconds: Annotated[float, Field(gt=0, le=60)] = 1.0
    # The bounded automatic-retry ceiling (D-09.3 note 2). After this many attempts a
    # document becomes `failed` rather than retrying forever on a poison input.
    worker_max_attempts: Annotated[int, Field(ge=1, le=10)] = 3
    # A claim older than this is treated as abandoned and may be reclaimed, so a
    # worker that died mid-job does not strand its document (NFR-REL-002).
    worker_claim_timeout_seconds: Annotated[int, Field(ge=1, le=3_600)] = 300

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

    @field_validator("supabase_url")
    @classmethod
    def _normalise_supabase_url(cls, value: str) -> str:
        """Clean paste artifacts and reject a URL httpx cannot use.

        This value is pasted into a deployment's env field by hand, so it can arrive
        wrapped in quotes or padded with whitespace or a trailing newline. Left as-is
        it becomes the httpx ``base_url`` in :class:`SupabaseStorage` with no usable
        scheme, and the failure surfaces only on the first upload as
        ``httpx.UnsupportedProtocol`` — swallowed into an opaque 503 with a request id
        rather than raised here. Stripping heals the common artifacts; a genuinely
        scheme-less value fails loudly at startup, naming the variable instead.

        Empty stays empty: an unset URL selects LocalFileStorage for local and test
        runs, and must not be forced to carry a scheme it will never use.
        """
        cleaned = value.strip().strip("\"'").strip()
        if cleaned and not cleaned.startswith(("http://", "https://")):
            msg = "supabase_url must start with http:// or https://"
            raise ValueError(msg)
        return cleaned

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
    def max_upload_request_bytes(self) -> int:
        """Ceiling for a multipart upload request.

        ``max_request_bytes`` sizes a JSON body and is far too small for a scanned
        PDF, so the upload route needs its own limit. It is derived rather than
        configured separately: a fourth number that could disagree with the two
        real limits would only ever be wrong. The slack covers multipart boundaries,
        part headers, and the filenames themselves.
        """
        multipart_overhead = 1024 * 1024
        return self.max_documents_per_upload * self.max_document_bytes + multipart_overhead

    @property
    def render_json_logs(self) -> bool:
        if self.log_json is not None:
            return self.log_json
        return self.environment not in (Environment.LOCAL, Environment.TEST)

    @property
    def expose_error_detail(self) -> bool:
        """Only non-production environments may see internal failure detail."""
        return self.environment is not Environment.PRODUCTION

    @property
    def supabase_storage_configured(self) -> bool:
        """True when the Supabase object-storage backend should be used.

        Reveals no secret — only whether both the URL and a key are present. When
        false, the vault falls back to LocalFileStorage for development and tests.

        A present-but-blank key is treated as *unconfigured*: Vercel (and any env
        source) can hold a variable whose value is empty or whitespace, and building
        SupabaseStorage with an empty service-role key would only fail later, on the
        first request, as an opaque 401 instead of here as a clear selection outcome.
        """
        key = self.supabase_service_role_key
        return (
            bool(self.supabase_url.strip())
            and key is not None
            and bool(key.get_secret_value().strip())
        )

    @property
    def llm_configured(self) -> bool:
        """True when a live LLM intent provider is usable. A provider set without a key/model is
        treated as unconfigured (deterministic fallback), never a crash. Reveals no secret."""
        return (
            self.llm_provider is not LlmProvider.NONE
            and self.llm_api_key is not None
            and bool(self.llm_model.strip())
        )


def _declared_names() -> set[str]:
    """The full ``DOCURA_*`` names this application recognises."""
    return {f"{ENV_PREFIX}{name.upper()}" for name in Settings.model_fields}


def _unknown_docura_variables() -> list[str]:
    """Find ``DOCURA_*`` names, from either source, that match no field.

    This is the whole of the application's strictness about its own namespace, and
    it covers both the process environment and the ``.env`` file:

    * pydantic-settings silently ignores an unrecognised *environment* variable, so
      ``DOCURA_DATABSE_URL`` would otherwise leave the real setting on its default;
    * ``extra`` is ``"ignore"`` for the reason given on :class:`Settings`, so the
      dotenv source will no longer reject it either.

    Names outside the ``DOCURA_`` prefix belong to other tools sharing the file and
    are deliberately not inspected.
    """
    known = _declared_names()
    candidates = {key.upper() for key in os.environ}

    env_path = Path(ENV_FILE)
    if env_path.is_file():
        # Keys only — a value here is a credential and must not be read into memory
        # for a check that does not need it.
        candidates |= {key.upper() for key in dotenv_values(env_path)}

    return sorted(key for key in candidates if key.startswith(ENV_PREFIX) and key not in known)


def _env_name(loc: tuple[object, ...]) -> str:
    """Render a pydantic error location as the variable a reader can go and fix."""
    name = ".".join(str(part) for part in loc).upper()
    return name if name.startswith(ENV_PREFIX) else f"{ENV_PREFIX}{name}"


def load_settings() -> Settings:
    """Build settings from the environment, converting pydantic errors into ours.

    The re-raised message lists field names and reasons only. Raw values are dropped
    so an invalid-configuration crash cannot print a password into a terminal or a
    container log.
    """
    unknown = _unknown_docura_variables()
    if unknown:
        msg = (
            "Invalid configuration - unrecognised variable(s): "
            f"{', '.join(unknown)}. Check for a typo; no default was applied."
        )
        raise ConfigurationError(msg)

    try:
        return Settings()  # values come from the environment
    except ValidationError as exc:
        problems = "; ".join(f"{_env_name(err['loc'])}: {err['msg']}" for err in exc.errors())
        msg = f"Invalid configuration - {problems}"
        raise ConfigurationError(msg) from None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Process-wide settings singleton. Call ``get_settings.cache_clear()`` in tests."""
    return load_settings()
