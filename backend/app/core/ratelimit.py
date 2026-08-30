"""In-process rate limiting for authentication endpoints.

**Known limitation, stated rather than hidden:** counters live in this process's
memory, so the effective limit multiplies by the number of running instances and
resets on restart. That is honest for the single-instance MVP and must be replaced
with a shared store before DOCURA runs more than one process. It is here because
the alternative — no brute-force resistance at all on the login path — is worse
than an imperfect limit.

It is a supplement to Argon2, never a substitute: the hash is what makes a stolen
database expensive, and this is what makes an online guessing run slow.
"""

from __future__ import annotations

import time
from collections import defaultdict, deque


class SlidingWindowRateLimiter:
    """Allow N attempts per key within a rolling window."""

    def __init__(self, *, max_attempts: int, window_seconds: float) -> None:
        self._max_attempts = max_attempts
        self._window_seconds = window_seconds
        self._hits: defaultdict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> bool:
        """Record an attempt. Returns False when the caller is over the limit.

        Expired timestamps are dropped on read, so an idle key costs nothing until
        it is touched again.
        """
        now = time.monotonic()
        cutoff = now - self._window_seconds
        hits = self._hits[key]

        while hits and hits[0] <= cutoff:
            hits.popleft()

        if len(hits) >= self._max_attempts:
            return False

        hits.append(now)
        return True

    def reset(self, key: str) -> None:
        """Clear a key's history — called after a successful authentication.

        Without this, a user who mistypes a password several times and then signs in
        correctly would stay near the limit for the rest of the window.
        """
        self._hits.pop(key, None)

    def prune(self) -> None:
        """Drop keys with no live attempts, so the map cannot grow without bound."""
        cutoff = time.monotonic() - self._window_seconds
        for key in list(self._hits):
            hits = self._hits[key]
            while hits and hits[0] <= cutoff:
                hits.popleft()
            if not hits:
                del self._hits[key]
