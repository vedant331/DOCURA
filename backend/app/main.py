"""Application factory and process entrypoint."""

from __future__ import annotations

import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.health import router as health_router
from app.api.users import router as users_router
from app.core.config import ConfigurationError, Environment, Settings, load_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging, get_logger
from app.core.middleware import (
    BodySizeLimitMiddleware,
    RequestContextMiddleware,
    SecurityHeadersMiddleware,
)
from app.db.session import (
    create_engine,
    create_session_factory,
    dispose_engine,
    verify_connection,
)
from app.services.reset_delivery import build_delivery_channel
from app.services.storage import build_document_storage

logger = get_logger(__name__)

# The one path prefix whose bodies are files rather than JSON. Named here because
# both the router and the body-size middleware have to agree on it.
DOCUMENTS_PREFIX = "/documents"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Start dependencies, verify them, and tear them down.

    Startup fails loudly if the database is unreachable. A service that boots into a
    permanently broken state is harder to notice than one that refuses to boot, and
    every endpoint past Sprint 1 needs the database anyway.
    """
    settings: Settings = app.state.settings

    logger.info(
        "service.starting",
        service=settings.service_name,
        version=settings.version,
        environment=settings.environment.value,
        database=settings.database_display_url,
    )

    engine = create_engine(settings)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)

    try:
        await verify_connection(engine)
    except Exception:
        logger.critical("service.startup_failed", reason="database_unreachable")
        await dispose_engine(engine)
        raise

    logger.info("database.connected", database=settings.database_display_url)
    logger.info("service.started", host=settings.host, port=settings.port)

    try:
        yield
    finally:
        logger.info("service.stopping")
        await dispose_engine(engine)
        logger.info("service.stopped")


def create_app(settings: Settings | None = None) -> FastAPI:
    """Build the application. Accepts injected settings so tests need no environment."""
    settings = settings or load_settings()
    configure_logging(settings)

    is_production = settings.environment is Environment.PRODUCTION
    app = FastAPI(
        title="DOCURA Backend",
        version=settings.version,
        summary="Personal document intelligence layer — backend foundation.",
        lifespan=lifespan,
        # Interactive docs are useful in development and are an unnecessary
        # description of the attack surface in production.
        docs_url=None if is_production else "/docs",
        redoc_url=None,
        openapi_url=None if is_production else "/openapi.json",
    )
    app.state.settings = settings
    # One place decides how a reset token leaves the process; tests and a future
    # mailer replace this attribute rather than the service that mints the token.
    app.state.reset_delivery = build_delivery_channel(settings)
    # Likewise for document bytes: one place decides where they live, so swapping
    # local disk for object storage is a change to build_document_storage alone.
    app.state.document_storage = build_document_storage(settings)

    # Middleware runs bottom-up: the request context is outermost so that a
    # request ID exists before any other layer can log or reject.
    app.add_middleware(
        BodySizeLimitMiddleware,
        max_bytes=settings.max_request_bytes,
        upload_paths=(DOCUMENTS_PREFIX,),
        upload_max_bytes=settings.max_upload_request_bytes,
    )
    app.add_middleware(SecurityHeadersMiddleware, settings=settings)
    if settings.cors_allow_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=list(settings.cors_allow_origins),
            allow_credentials=True,
            allow_methods=["GET", "POST", "PATCH", "DELETE"],
            allow_headers=["Authorization", "Content-Type", "X-Request-ID"],
        )
    app.add_middleware(RequestContextMiddleware)

    register_exception_handlers(app)
    app.include_router(health_router)
    app.include_router(auth_router)
    app.include_router(users_router)
    app.include_router(documents_router)

    return app


def main() -> None:
    """Console entrypoint: load config, fail clearly, otherwise serve."""
    import uvicorn

    try:
        settings = load_settings()
    except ConfigurationError as exc:
        # Logging is not configured yet, and this must be readable regardless.
        print(f"FATAL: {exc}", file=sys.stderr)
        raise SystemExit(78) from None  # EX_CONFIG

    uvicorn.run(
        create_app(settings),
        host=settings.host,
        port=settings.port,
        log_config=None,  # structlog owns logging; uvicorn's dictConfig would undo it
        # The middleware already logs every request with a duration and request ID;
        # uvicorn's access log would duplicate it with less detail.
        access_log=False,
        # Naming the server and its version tells a scanner which exploits to try.
        server_header=False,
    )


if __name__ == "__main__":
    main()
