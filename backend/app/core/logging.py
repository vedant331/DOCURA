"""Structured logging with redaction applied before anything reaches a sink.

NFR-OBS-004 requires failures to carry enough context to diagnose them *and* to
carry no personal values. Those pull against each other, so redaction is a
processor in the pipeline rather than a convention: a caller cannot forget it, and
adding a new log call cannot leak a value that a later sprint introduces.
"""

from __future__ import annotations

import logging
import sys
from collections.abc import MutableMapping
from typing import Any

import structlog
from structlog.typing import EventDict, WrappedLogger

from app.core.config import Environment, LogLevel, Settings

REDACTED = "***REDACTED***"
_MAX_DEPTH = 6

# Exact key names whose values never reach a log sink. Matched case-insensitively
# against the key with separators stripped, so `api_key`, `apiKey`, and `API-KEY`
# all collapse to the same entry.
_SENSITIVE_KEYS: frozenset[str] = frozenset(
    {
        # Credentials and session material
        "password",
        "passwd",
        "pwd",
        "passwordhash",
        "secret",
        "clientsecret",
        "token",
        "accesstoken",
        "refreshtoken",
        "idtoken",
        "apikey",
        "authorization",
        "auth",
        "cookie",
        "setcookie",
        "sessionid",
        "session",
        "credential",
        "credentials",
        "privatekey",
        "signature",
        "otp",
        # Connection strings carry embedded passwords
        "dsn",
        "databaseurl",
        "connectionstring",
        # Document and record content (Step 3 FR-AUD-006, BR-017)
        "documentcontent",
        "documenttext",
        "extractedtext",
        "ocrtext",
        "filecontents",
        "attributevalue",
        "fieldvalue",
        "filledvalue",
    }
)


def _normalise(key: str) -> str:
    return key.replace("_", "").replace("-", "").lower()


def _redact(value: Any, depth: int = 0) -> Any:
    """Recursively mask sensitive entries in mappings and sequences."""
    if depth >= _MAX_DEPTH:
        return value
    if isinstance(value, MutableMapping):
        return {
            key: (
                REDACTED
                if isinstance(key, str) and _normalise(key) in _SENSITIVE_KEYS
                else _redact(item, depth + 1)
            )
            for key, item in value.items()
        }
    if isinstance(value, list | tuple | set):
        rebuilt = [_redact(item, depth + 1) for item in value]
        return type(value)(rebuilt) if isinstance(value, list | tuple) else set(rebuilt)
    return value


def redact_processor(_logger: WrappedLogger, _method: str, event_dict: EventDict) -> EventDict:
    """structlog processor that strips sensitive values from every event."""
    return dict(_redact(event_dict))


def configure_logging(settings: Settings) -> None:
    """Install the logging pipeline. Idempotent — safe to call per process start.

    Application logs and standard-library logs share one handler through
    ``ProcessorFormatter``. That matters more than tidiness: libraries this service
    depends on — uvicorn, SQLAlchemy — log through the stdlib, and a pipeline that
    redacts only structlog events would let a third party's log line carry a value
    the application layer is careful never to emit.
    """
    level = logging.getLevelNamesMapping()[LogLevel(settings.log_level).value]

    renderer: structlog.typing.Processor = (
        structlog.processors.JSONRenderer()
        if settings.render_json_logs
        else structlog.dev.ConsoleRenderer(colors=False)
    )

    # Applied to events from both sources, so they render identically.
    shared: list[structlog.typing.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.StackInfoRenderer(),
    ]

    structlog.configure(
        processors=[
            *shared,
            structlog.processors.format_exc_info,
            redact_processor,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Caching binds a logger to the configuration live at its first call, which
        # makes a later reconfigure a no-op for any module that already logged.
        # That is the right trade in a long-lived process and the wrong one where
        # configuration is rebuilt repeatedly, as it is under test.
        cache_logger_on_first_use=settings.environment not in (Environment.LOCAL, Environment.TEST),
    )

    formatter = structlog.stdlib.ProcessorFormatter(
        # Runs over records that did not originate in structlog.
        foreign_pre_chain=[*shared, structlog.stdlib.ExtraAdder()],
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            # Second pass: foreign records have not been through it yet, and it is
            # idempotent for records that have.
            redact_processor,
            renderer,
        ],
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root = logging.getLogger()
    for existing in root.handlers[:]:
        root.removeHandler(existing)
    root.addHandler(handler)
    root.setLevel(level)

    # Uvicorn installs its own handlers at startup; clearing them and propagating
    # sends its output through the formatter above instead.
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        uvicorn_logger = logging.getLogger(name)
        uvicorn_logger.handlers.clear()
        uvicorn_logger.propagate = True


def get_logger(name: str) -> Any:
    """Return a bound structlog logger."""
    return structlog.stdlib.get_logger(name)
