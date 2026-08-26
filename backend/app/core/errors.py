"""Consistent error responses.

Three requirements shape every response in this module:

* **NFR-ERR-001** — an error states what went wrong *and* what the user can do next.
  A body with only a title is not an acceptable error here, so ``remediation`` is a
  required field of the problem document, not an optional extra.
* **NFR-ERR-004** — no stack trace, internal identifier, or infrastructure detail
  reaches the client. Detail is logged; a generic document is returned.
* **NFR-ERR-002** — failure means inaction. Handlers report and stop; none retries,
  substitutes a default, or partially applies a request.

The wire format is RFC 9457 ``application/problem+json``.
"""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.logging import get_logger

PROBLEM_CONTENT_TYPE = "application/problem+json"

logger = get_logger(__name__)


class DocuraError(Exception):
    """Base class for failures this service reports deliberately."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    title: str = "Internal server error"
    detail: str = "The request could not be completed."
    remediation: str = "Try again. If the problem continues, contact support."

    def __init__(
        self,
        detail: str | None = None,
        *,
        remediation: str | None = None,
    ) -> None:
        self.detail = detail or self.detail
        self.remediation = remediation or self.remediation
        super().__init__(self.detail)


class ServiceUnavailableError(DocuraError):
    """A dependency this request needed was not reachable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    title = "Service temporarily unavailable"
    detail = "A service DOCURA depends on is not responding."
    remediation = "Wait a moment and try again. Nothing was changed."


class DatabaseUnavailableError(ServiceUnavailableError):
    """The database could not be reached or did not answer in time."""

    detail = "DOCURA cannot reach its database."
    remediation = "Wait a moment and try again. No data was read or written."


def problem_response(
    *,
    status_code: int,
    title: str,
    detail: str,
    remediation: str,
    request_id: str | None = None,
    extra: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build an RFC 9457 problem document."""
    body: dict[str, Any] = {
        "type": "about:blank",
        "title": title,
        "status": status_code,
        "detail": detail,
        "remediation": remediation,
    }
    if request_id:
        body["request_id"] = request_id
    if extra:
        body.update(extra)
    return JSONResponse(status_code=status_code, content=body, media_type=PROBLEM_CONTENT_TYPE)


def _request_id(request: Request) -> str | None:
    value = getattr(request.state, "request_id", None)
    return str(value) if value else None


def _sanitise_validation_errors(exc: RequestValidationError) -> list[dict[str, str]]:
    """Reduce pydantic errors to location and reason.

    Pydantic includes the rejected input in every error. Echoing it back would
    reflect attacker-supplied content and, on a credential field, the credential
    itself — so ``input`` and ``ctx`` are dropped rather than forwarded.
    """
    sanitised: list[dict[str, str]] = []
    for error in exc.errors():
        location = ".".join(str(part) for part in error.get("loc", ()) if part != "body")
        sanitised.append(
            {
                "field": location or "body",
                "reason": str(error.get("msg", "is invalid")),
            }
        )
    return sanitised


async def docura_error_handler(request: Request, exc: DocuraError) -> JSONResponse:
    logger.warning(
        "request.failed",
        error_class=type(exc).__name__,
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        request_id=_request_id(request),
    )
    return problem_response(
        status_code=exc.status_code,
        title=exc.title,
        detail=exc.detail,
        remediation=exc.remediation,
        request_id=_request_id(request),
    )


async def validation_error_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = _sanitise_validation_errors(exc)
    logger.info(
        "request.invalid",
        path=request.url.path,
        method=request.method,
        error_count=len(errors),
        request_id=_request_id(request),
    )
    return problem_response(
        status_code=422,
        title="Invalid request",
        detail="The request did not match what this endpoint expects.",
        remediation="Correct the fields listed in 'errors' and send the request again.",
        request_id=_request_id(request),
        extra={"errors": errors},
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    remediation = {
        status.HTTP_404_NOT_FOUND: "Check the URL and try again.",
        status.HTTP_405_METHOD_NOT_ALLOWED: "Use one of the methods this endpoint allows.",
        413: "Send a smaller request body.",
    }.get(exc.status_code, "Check the request and try again.")

    logger.info(
        "request.rejected",
        status_code=exc.status_code,
        path=request.url.path,
        method=request.method,
        request_id=_request_id(request),
    )
    return problem_response(
        status_code=exc.status_code,
        title=str(exc.detail) if exc.detail else "Request rejected",
        detail=str(exc.detail) if exc.detail else "The request was rejected.",
        remediation=remediation,
        request_id=_request_id(request),
    )


async def unhandled_error_handler(request: Request, exc: Exception) -> JSONResponse:
    """Last resort. The traceback is logged; the client gets none of it."""
    logger.exception(
        "request.unhandled_error",
        error_class=type(exc).__name__,
        path=request.url.path,
        method=request.method,
        request_id=_request_id(request),
    )
    return problem_response(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        title="Internal server error",
        detail="Something went wrong inside DOCURA. Your request was not completed.",
        remediation="Try again. If the problem continues, contact support with the request ID.",
        request_id=_request_id(request),
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Attach every handler. Order is irrelevant; FastAPI dispatches by type."""
    app.add_exception_handler(DocuraError, docura_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(RequestValidationError, validation_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(StarletteHTTPException, http_error_handler)  # type: ignore[arg-type]
    app.add_exception_handler(Exception, unhandled_error_handler)
