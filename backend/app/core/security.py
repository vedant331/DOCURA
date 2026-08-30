"""Password hashing and session-token primitives.

Two different secrets are handled here, and they are deliberately treated
differently:

* A **password** is low-entropy and chosen by a human, so it is hashed with
  Argon2id — deliberately slow and memory-hard, so that a stolen database is
  expensive to attack offline (NFR-SEC-004: "never in recoverable form").
* A **session token** is 256 bits from the system CSPRNG. There is nothing to
  guess, so a slow hash buys no security and would add its cost to *every*
  authenticated request. It is stored as a SHA-256 digest, which still means a
  database leak yields no usable token.
"""

from __future__ import annotations

import contextlib
import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError

# OWASP Password Storage Cheat Sheet, Argon2id: 19 MiB, t=2, p=1.
_ARGON2_MEMORY_COST_KIB = 19 * 1024
_ARGON2_TIME_COST = 2
_ARGON2_PARALLELISM = 1

_hasher = PasswordHasher(
    memory_cost=_ARGON2_MEMORY_COST_KIB,
    time_cost=_ARGON2_TIME_COST,
    parallelism=_ARGON2_PARALLELISM,
)

SESSION_TOKEN_BYTES = 32
# A reset token is a single-use bearer credential for the account, so it is drawn
# from the same 256-bit space as a session token.
RESET_TOKEN_BYTES = 32

# Verified against when no account matches, so that a login attempt costs the same
# whether or not the address exists. Without this, response time answers "is this
# person registered with DOCURA?" — which, for a document vault, is itself private.
_DUMMY_HASH = _hasher.hash("docura-timing-equaliser-not-a-credential")


def hash_password(password: str) -> str:
    """Return an Argon2id hash. The encoded form carries its own salt and parameters."""
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Check a password against a stored hash, returning False rather than raising.

    A malformed stored hash is treated as a failed verification: it must never let
    a caller through, and it must not crash the login path either.
    """
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, VerificationError, InvalidHashError):
        return False


def verify_dummy_password(password: str) -> None:
    """Burn the same work as a real verification, for a login with no matching user."""
    with contextlib.suppress(VerifyMismatchError, VerificationError, InvalidHashError):
        _hasher.verify(_DUMMY_HASH, password)


def needs_rehash(password_hash: str) -> bool:
    """True when a stored hash predates the current Argon2 parameters."""
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True


def generate_session_token() -> str:
    """Return a fresh URL-safe session token. This is the only time it exists in clear."""
    return secrets.token_urlsafe(SESSION_TOKEN_BYTES)


def hash_session_token(token: str) -> str:
    """Return the digest stored in the database. Never store the token itself."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def tokens_match(candidate_digest: str, stored_digest: str) -> bool:
    """Constant-time digest comparison."""
    return hmac.compare_digest(candidate_digest, stored_digest)


def generate_reset_token() -> str:
    """Return a fresh password-reset token. This is the only time it exists in clear."""
    return secrets.token_urlsafe(RESET_TOKEN_BYTES)


def hash_reset_token(token: str) -> str:
    """Return the digest stored for a reset token.

    Named separately from :func:`hash_session_token` even though the algorithm is
    the same: the two live in different tables and must never be looked up against
    each other, and a shared helper invites exactly that mistake.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
