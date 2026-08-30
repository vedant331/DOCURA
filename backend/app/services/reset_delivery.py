"""Out-of-band delivery of password-reset tokens.

The reset process is *verified* (FR-ACC-005) because the token only ever reaches
the address already registered to the account. Sending that message is a separate
concern from minting the token, so it sits behind a channel rather than inside the
service: no mail transport is in this sprint's scope, and adding one later must not
mean editing security-relevant code.

The token is **never** returned in an HTTP response. Returning it would let anyone
who can call the request endpoint reset any account — precisely the weakening
UC-001 A2 forbids.
"""

from __future__ import annotations

import sys
from typing import Protocol

from app.core.config import Environment, Settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class ResetDeliveryChannel(Protocol):
    """How a reset token reaches the account's verified address."""

    async def send(self, *, email: str, token: str) -> None: ...


class ConsoleResetDeliveryChannel:
    """The Sprint 2 stand-in for a mailer.

    In ``local`` and ``test`` the token is written straight to this process's
    stderr so a developer can complete the flow end to end. That deliberately
    bypasses ``app.core.logging``, which redacts anything named ``token`` before it
    reaches a sink — the point is not to defeat that redaction but to keep the
    development transport out of the log pipeline entirely, so no reset credential
    can ever be shipped to a log aggregator.

    In every other environment nothing is printed. The missing mail transport is
    reported at ERROR instead — without the token and without the address — so the
    gap is loud rather than silent if this reaches an environment with real users.
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    async def send(self, *, email: str, token: str) -> None:
        if self._settings.environment in (Environment.LOCAL, Environment.TEST):
            print(
                f"[docura] password reset for {email}: token={token}",
                file=sys.stderr,
                flush=True,
            )
            return

        logger.error(
            "auth.password_reset_delivery_unconfigured",
            note="No mail transport is configured; the reset token was discarded unsent.",
        )


def build_delivery_channel(settings: Settings) -> ResetDeliveryChannel:
    """The channel this application runs with. One place to swap in a real mailer."""
    return ConsoleResetDeliveryChannel(settings)
