"""Request-scoped middleware: correlation ID, access logging, headers, body cap."""

from __future__ import annotations

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from starlette.datastructures import MutableHeaders
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.config import Environment, Settings
from app.core.errors import problem_response
from app.core.logging import get_logger

HTTP_413_CONTENT_TOO_LARGE = 413

REQUEST_ID_HEADER = "X-Request-ID"
_MAX_INBOUND_REQUEST_ID = 128

logger = get_logger(__name__)

Handler = Callable[[Request], Awaitable[Response]]


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Assign a request ID, bind it to the log context, and log the outcome.

    An inbound ``X-Request-ID`` is honoured so a correlation ID survives a proxy,
    but it is length-capped and only accepted when it looks like an identifier —
    the value is echoed in responses and written to logs, and an unbounded client
    string in either place is a log-injection surface.
    """

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        request_id = self._resolve_request_id(request)
        request.state.request_id = request_id

        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=request_id)

        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            # Logged with a traceback by the exception handler; recorded here so a
            # failed request still produces one access line with its duration.
            logger.warning(
                "request.completed",
                method=request.method,
                path=request.url.path,
                status_code=500,
                duration_ms=round((time.perf_counter() - started) * 1000, 2),
            )
            raise

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        response.headers[REQUEST_ID_HEADER] = request_id
        logger.info(
            "request.completed",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        return response

    @staticmethod
    def _resolve_request_id(request: Request) -> str:
        inbound = request.headers.get(REQUEST_ID_HEADER, "").strip()
        if (
            inbound
            and len(inbound) <= _MAX_INBOUND_REQUEST_ID
            and all(char.isalnum() or char in "-_" for char in inbound)
        ):
            return inbound
        return str(uuid.uuid4())


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply the response headers appropriate to a JSON API.

    The CSP is deliberately a lockdown rather than a page policy: this service
    returns JSON, so nothing should ever be loaded or framed from a response.
    HSTS is set only outside local/test, where TLS is not in play.
    """

    def __init__(self, app: Callable[..., Awaitable[None]], *, settings: Settings) -> None:
        super().__init__(app)
        self._send_hsts = settings.environment not in (Environment.LOCAL, Environment.TEST)

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        response = await call_next(request)
        headers = MutableHeaders(scope=None, raw=response.raw_headers)
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Referrer-Policy", "no-referrer")
        headers.setdefault(
            "Content-Security-Policy",
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'",
        )
        headers.setdefault("Cross-Origin-Opener-Policy", "same-origin")
        headers.setdefault("Cross-Origin-Resource-Policy", "same-origin")
        headers.setdefault("Cache-Control", "no-store")
        headers.setdefault("Permissions-Policy", "geolocation=(), camera=(), microphone=()")
        if self._send_hsts:
            headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response


class BodySizeLimitMiddleware(BaseHTTPMiddleware):
    """Reject oversized bodies on the declared length, before reading them.

    This is the cheap half of the defence. A chunked request can lie about or omit
    ``Content-Length``; the real ceiling for uploads belongs with the upload
    endpoint in a later sprint, and this guard exists so no endpoint added before
    then is unbounded by default.
    """

    def __init__(self, app: Callable[..., Awaitable[None]], *, max_bytes: int) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        declared = request.headers.get("content-length")
        if declared is not None:
            try:
                length = int(declared)
            except ValueError:
                length = -1
            if length > self._max_bytes:
                logger.info(
                    "request.body_too_large",
                    path=request.url.path,
                    method=request.method,
                    limit_bytes=self._max_bytes,
                )
                return problem_response(
                    status_code=HTTP_413_CONTENT_TOO_LARGE,
                    title="Request too large",
                    detail=(
                        f"The request body exceeds the {self._max_bytes} byte limit "
                        "for this endpoint."
                    ),
                    remediation="Send a smaller request body.",
                    request_id=getattr(request.state, "request_id", None),
                )
        return await call_next(request)
