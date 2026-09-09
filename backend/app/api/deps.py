"""Request dependencies: database session, authenticated identity, rate limiting."""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings
from app.core.errors import AuthenticationError, RateLimitedError
from app.core.logging import get_logger
from app.core.ratelimit import SlidingWindowRateLimiter
from app.db.models import Session, User
from app.services.auth_service import resolve_session
from app.services.extraction import DocumentExtractor
from app.services.reset_delivery import ResetDeliveryChannel
from app.services.storage import DocumentStorage

logger = get_logger(__name__)

# auto_error=False so a missing header raises DOCURA's own AuthenticationError and
# gets the same problem+json body as every other failure, rather than Starlette's.
_bearer = HTTPBearer(auto_error=False, scheme_name="DOCURA session token")


async def get_settings_dep(request: Request) -> Settings:
    settings: Settings = request.app.state.settings
    return settings


async def get_db(request: Request) -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped database session, rolling back on an unhandled error."""
    factory = request.app.state.session_factory
    async with factory() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


async def get_reset_delivery(request: Request) -> ResetDeliveryChannel:
    """The configured out-of-band channel for password-reset tokens.

    Resolved from application state rather than constructed here, so a test — or a
    real mailer — can substitute one without the endpoint knowing.
    """
    channel: ResetDeliveryChannel = request.app.state.reset_delivery
    return channel


async def get_document_storage(request: Request) -> DocumentStorage:
    """The configured place where document bytes live.

    Resolved from application state rather than constructed per request, for the
    same reason as the reset channel: the vault's endpoints must not know which
    backend they are talking to, and a test needs to substitute a failing one.
    """
    storage: DocumentStorage = request.app.state.document_storage
    return storage


async def get_document_extractor(request: Request) -> DocumentExtractor:
    """The configured extraction engine (Sprint 4 decision D-01).

    Resolved from application state for the same reason as the storage backend: the
    engine is replaceable, and nothing above ``app.services.extraction`` may know
    which one is installed. No endpoint depends on this yet — the boundary exists
    before the pipeline that will use it, so that the pipeline can be built against
    an interface rather than against a library.
    """
    extractor: DocumentExtractor = request.app.state.document_extractor
    return extractor


async def get_current_session(
    request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
    db: Annotated[AsyncSession, Depends(get_db)],
    settings: Annotated[Settings, Depends(get_settings_dep)],
) -> Session:
    """Resolve the bearer token to a live session, or reject the request.

    This is the only place a request's identity is established. Nothing downstream
    reads a user id from the path, query, or body — NFR-SEC-003 requires that
    ownership is never inferred from an identifier the client supplied.
    """
    if credentials is None or not credentials.credentials:
        raise AuthenticationError

    session = await resolve_session(db, token=credentials.credentials, settings=settings)
    if session is None:
        # Deliberately not logging which token was presented, nor why it failed.
        logger.info("auth.session_rejected", path=request.url.path)
        raise AuthenticationError

    return session


async def get_current_user(
    session: Annotated[Session, Depends(get_current_session)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """The authenticated account. An account deactivated mid-session loses access now."""
    user = await db.get(User, session.user_id)
    if user is None or not user.is_active:
        raise AuthenticationError
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
CurrentSession = Annotated[Session, Depends(get_current_session)]
DbSession = Annotated[AsyncSession, Depends(get_db)]
AppSettings = Annotated[Settings, Depends(get_settings_dep)]
ResetDelivery = Annotated[ResetDeliveryChannel, Depends(get_reset_delivery)]
DocumentStore = Annotated[DocumentStorage, Depends(get_document_storage)]
DocumentExtraction = Annotated[DocumentExtractor, Depends(get_document_extractor)]


def client_key(request: Request) -> str:
    """Rate-limit key for an unauthenticated caller.

    The direct peer address is used, not ``X-Forwarded-For``: that header is
    client-controlled unless a trusted proxy overwrites it, and trusting it here
    would let an attacker rotate the header to bypass the limit entirely. Wiring a
    real proxy configuration belongs with the deployment, not with this sprint.
    """
    return request.client.host if request.client else "unknown"


def enforce_auth_rate_limit(request: Request, limiter: SlidingWindowRateLimiter) -> None:
    """Raise if this caller has made too many recent authentication attempts."""
    key = client_key(request)
    if not limiter.check(key):
        logger.warning("auth.rate_limited", path=request.url.path)
        raise RateLimitedError
