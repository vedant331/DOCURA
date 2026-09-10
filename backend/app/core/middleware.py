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


# The lockdown policy for every JSON response: nothing loads or frames.
_STRICT_CSP = "default-src 'none'; frame-ancestors 'none'; base-uri 'none'; form-action 'none'"

# The pages FastAPI's built-in interactive docs are served on. Only these get the
# relaxed policy below, and only in local development.
_DOCS_PATHS = frozenset({"/docs", "/docs/oauth2-redirect"})

# Just enough to let Swagger UI's CDN assets, its inline init script, and its fetch of
# /openapi.json load. Development only — production disables /docs entirely (see
# app.main.create_app), so this policy is never emitted there.
_DOCS_CSP = (
    "default-src 'none'; "
    "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
    "img-src 'self' data: https://cdn.jsdelivr.net https://fastapi.tiangolo.com; "
    "font-src 'self' https://cdn.jsdelivr.net; "
    "connect-src 'self'; "
    "frame-ancestors 'none'; base-uri 'none'; form-action 'none'"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Apply the response headers appropriate to a JSON API.

    The CSP is deliberately a lockdown rather than a page policy: this service
    returns JSON, so nothing should ever be loaded or framed from a response. The one
    exception is FastAPI's interactive docs in *local development*, whose Swagger UI
    loads assets from a CDN — those pages get a narrowly relaxed CSP, and nothing
    else does. HSTS is set only outside local/test, where TLS is not in play.
    """

    def __init__(self, app: Callable[..., Awaitable[None]], *, settings: Settings) -> None:
        super().__init__(app)
        self._send_hsts = settings.environment not in (Environment.LOCAL, Environment.TEST)
        # Only local development serves /docs (production disables it) and only there
        # is the CDN allowance acceptable; every other environment stays locked down.
        self._relax_docs = settings.environment is Environment.LOCAL

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        response = await call_next(request)
        headers = MutableHeaders(scope=None, raw=response.raw_headers)
        headers.setdefault("X-Content-Type-Options", "nosniff")
        headers.setdefault("X-Frame-Options", "DENY")
        headers.setdefault("Referrer-Policy", "no-referrer")
        docs_page = self._relax_docs and request.url.path in _DOCS_PATHS
        headers.setdefault(
            "Content-Security-Policy",
            _DOCS_CSP if docs_page else _STRICT_CSP,
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
    ``Content-Length``, so the per-file ceiling is also enforced while the upload is
    read (``app.services.document_validation.measure_and_validate``); this guard
    exists so that no endpoint is unbounded by default and so an obviously oversized
    request is refused before a byte of it is parsed.

    The vault needs a second, larger limit. ``max_bytes`` sizes a JSON body — a
    scanned marksheet is orders of magnitude bigger — so paths under
    ``upload_paths`` are measured against ``upload_max_bytes`` instead. The
    exemption is a prefix list rather than a per-route setting because this
    middleware runs long before routing has decided which endpoint will answer.
    """

    def __init__(
        self,
        app: Callable[..., Awaitable[None]],
        *,
        max_bytes: int,
        upload_paths: tuple[str, ...] = (),
        upload_max_bytes: int | None = None,
    ) -> None:
        super().__init__(app)
        self._max_bytes = max_bytes
        self._upload_paths = upload_paths
        self._upload_max_bytes = upload_max_bytes if upload_max_bytes is not None else max_bytes

    def _limit_for(self, path: str) -> int:
        if any(path == prefix or path.startswith(f"{prefix}/") for prefix in self._upload_paths):
            return self._upload_max_bytes
        return self._max_bytes

    async def dispatch(self, request: Request, call_next: Handler) -> Response:
        declared = request.headers.get("content-length")
        if declared is not None:
            limit = self._limit_for(request.url.path)
            try:
                length = int(declared)
            except ValueError:
                length = -1
            if length > limit:
                logger.info(
                    "request.body_too_large",
                    path=request.url.path,
                    method=request.method,
                    limit_bytes=limit,
                )
                return problem_response(
                    status_code=HTTP_413_CONTENT_TOO_LARGE,
                    title="Request too large",
                    detail=(f"The request body exceeds the {limit} byte limit for this endpoint."),
                    remediation="Send a smaller request body.",
                    request_id=getattr(request.state, "request_id", None),
                )
        return await call_next(request)
