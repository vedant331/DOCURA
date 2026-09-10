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


class AuthenticationError(DocuraError):
    """No valid credential or session accompanied the request.

    One message covers every cause — absent, malformed, unknown, expired, revoked.
    Distinguishing them would let an unauthenticated caller probe which tokens once
    existed, and would turn a login form into an account-existence oracle.
    """

    status_code = status.HTTP_401_UNAUTHORIZED
    title = "Not authenticated"
    detail = "The request did not carry a valid DOCURA session."
    remediation = "Sign in and send the returned token as 'Authorization: Bearer <token>'."


class InvalidCredentialsError(AuthenticationError):
    """Login failed. Deliberately indistinguishable from an unknown account."""

    detail = "The email address or password is incorrect."
    remediation = "Check both and try again."


class PermissionDeniedError(DocuraError):
    """Authenticated, but not entitled to the thing requested (BR-018)."""

    status_code = status.HTTP_403_FORBIDDEN
    title = "Not permitted"
    detail = "This account may not access that."
    remediation = "Use an account that owns the requested data."


class EmailAlreadyRegisteredError(DocuraError):
    """Registration collided with an existing account."""

    status_code = status.HTTP_409_CONFLICT
    title = "Email already registered"
    detail = "An account already exists for that email address."
    remediation = "Sign in instead, or reset the password for that account."


class InvalidResetTokenError(DocuraError):
    """The presented password-reset token is unusable.

    One message covers absent, unknown, already-spent, and expired alike. Telling
    them apart would turn the confirm endpoint into an oracle for which reset
    tokens have existed, and UC-001 A2 requires that the reset not weaken the vault.
    """

    status_code = status.HTTP_400_BAD_REQUEST
    title = "Reset link not usable"
    detail = "This password reset link is not valid, has already been used, or has expired."
    remediation = "Request a new password reset and use the most recent link."


class WeakPasswordError(DocuraError):
    """The password does not meet the configured policy."""

    status_code = 422
    title = "Password rejected"
    detail = "The password does not meet DOCURA's requirements."
    remediation = "Choose a longer password and try again."


class DocumentNotFoundError(DocuraError):
    """No document with that id is readable by the requesting account.

    Deliberately 404 rather than 403, and deliberately the same answer whether the
    id names nothing at all or names another user's document. A 403 would confirm
    that the id exists, which on a vault of identity documents is itself a
    disclosure: it would let anyone with a list of ids learn which are real. NFR-
    SEC-003 requires the ownership check; NFR-PRIV-002 requires that the check not
    become an oracle.
    """

    status_code = status.HTTP_404_NOT_FOUND
    title = "Document not found"
    detail = "No document with that identifier is available to this account."
    remediation = "Check the identifier against your document list and try again."


class AttributeNotFoundError(DocuraError):
    """No value for that canonical attribute is available to the requesting account.

    404, and identical whether the identifier names nothing DOCURA has a value for or
    names something this account simply has no observation of — the same oracle-
    avoidance as :class:`DocumentNotFoundError` (NFR-SEC-003, NFR-PRIV-002). It never
    confirms that another account holds the attribute.
    """

    status_code = status.HTTP_404_NOT_FOUND
    title = "Attribute not found"
    detail = "No value for that attribute is available to this account."
    remediation = "Check the attribute identifier, or upload a document that provides it."


class FormSessionNotFoundError(DocuraError):
    """No form session with that id is readable by the requesting account.

    404, and identical whether the id names nothing or names another account's
    session — the same oracle-avoidance as :class:`DocumentNotFoundError`
    (NFR-SEC-003). Ownership is a ``WHERE`` clause, never a post-load check.
    """

    status_code = status.HTTP_404_NOT_FOUND
    title = "Form session not found"
    detail = "No form session with that identifier is available to this account."
    remediation = "Check the identifier against your form sessions and try again."


class FormSessionNotActiveError(DocuraError):
    """A lifecycle transition was requested on a session that has already ended.

    A hand-back or stop applies to a live session; one already handed back, stopped,
    or expired has no further transition (BR-016 — do nothing rather than pretend a
    second ending happened). The history of the original ending is preserved.
    """

    status_code = status.HTTP_409_CONFLICT
    title = "Form session already ended"
    detail = "This form session has already ended and cannot change state again."
    remediation = "Activate DOCURA again on the form to start a new session."


class UnsupportedDocumentError(DocuraError):
    """The file is not one of the accepted types, or is not readable as one.

    FR-UPL-004 requires the message to name both the reason *and* the accepted
    alternatives, so the accepted list is part of the remediation rather than
    something the caller is expected to already know.
    """

    status_code = 415
    title = "File type not accepted"
    detail = "That file is not a document type DOCURA accepts."
    remediation = "Upload a PDF, JPG, or PNG."


class DocumentTooLargeError(DocuraError):
    """The file exceeds the configured per-document ceiling (FR-UPL-003)."""

    status_code = 413
    title = "File too large"
    detail = "That file is larger than DOCURA accepts for a single document."
    remediation = "Upload a smaller file, or split the document."


class DuplicateDocumentError(DocuraError):
    """The exact same bytes are already stored for this account.

    FR-UPL-007 and AC-US-002-4 forbid a *silent* duplicate. Choosing between keep,
    replace, and version needs document versioning (FR-DOC-005), which is not built
    yet, so this sprint reports the collision and names the document already held
    rather than deciding on the user's behalf (BR-003).
    """

    status_code = status.HTTP_409_CONFLICT
    title = "Document already stored"
    detail = "An identical file is already in this account's vault."
    remediation = "Open the document you already have, or upload a different file."


class DocumentNotReprocessableError(DocuraError):
    """Reprocessing was requested for a document that is still being processed.

    FR-OCR-010 lets a user re-run a document, but only one that has come to rest —
    ``ready``, ``needs_review``, or ``failed``. Re-queuing one that is still
    ``queued`` or ``processing`` would let a second run race the first, which
    NFR-REL-005 (no duplicate work) weighs against; the request is refused rather
    than silently ignored.
    """

    status_code = status.HTTP_409_CONFLICT
    title = "Document is still processing"
    detail = "This document cannot be reprocessed because it is still being processed."
    remediation = "Wait until it is ready or has failed, then request reprocessing again."


class DocumentStorageError(ServiceUnavailableError):
    """The bytes could not be written, read, or removed.

    A 503 rather than a 500 because BR-016 applies: the operation did not happen,
    nothing was partially applied, and retrying is the right next step. The
    underlying path and OS error are logged and never described to the client
    (NFR-ERR-004).
    """

    detail = "DOCURA could not reach the store that holds your documents."
    remediation = "Wait a moment and try again. Nothing was changed."


class DocumentExtractionError(ServiceUnavailableError):
    """A document could not be read by the extraction engine.

    FR-OCR-009 fixes the shape of this failure: the original file is retained, what
    failed is stated, and a retry and a manual-entry path are offered. The remediation
    below says the first two of those; the retry and manual-entry paths are part of
    the processing pipeline and are not built yet, so nothing here promises them.

    BR-016 is why this is a failure at all rather than an empty result: a component
    that cannot do its work does nothing and says so.
    """

    detail = "DOCURA could not read this document."
    remediation = "Your file is unchanged and still stored. Try again in a moment."


class ExtractionNotConfiguredError(DocumentExtractionError):
    """No extraction engine is configured (Sprint 4 decision D-01).

    The engine remains TBD until the held-out evaluation required by AR-AST-008
    reports. Reaching this is an honest statement that document understanding is not
    available yet — never an empty or invented extraction result.
    """

    detail = "DOCURA cannot read documents yet: no extraction engine is configured."
    remediation = "Your file is stored and unchanged. Document reading is not available yet."


class RateLimitedError(DocuraError):
    """Too many authentication attempts from one source."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    title = "Too many attempts"
    detail = "Too many authentication attempts have been made recently."
    remediation = "Wait a few minutes before trying again."


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
    response = problem_response(
        status_code=exc.status_code,
        title=exc.title,
        detail=exc.detail,
        remediation=exc.remediation,
        request_id=_request_id(request),
    )
    if isinstance(exc, AuthenticationError):
        # RFC 9110 §11.6.1 requires a challenge on a 401. The realm is a constant;
        # it must not describe why this particular attempt failed.
        response.headers["WWW-Authenticate"] = 'Bearer realm="docura"'
    return response


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
