"""The out-of-band channel that carries a reset token (FR-ACC-005).

No database is needed here: the question is only what the channel does with a
credential in each environment, and the answer must be different outside local
development.
"""

from __future__ import annotations

import pytest

from app.core.config import Environment, Settings
from app.services.reset_delivery import ConsoleResetDeliveryChannel, build_delivery_channel
from tests.conftest import TEST_DSN

TOKEN = "a-reset-token-value-for-this-test"


def _settings(environment: Environment) -> Settings:
    return Settings(environment=environment, database_url=TEST_DSN)


@pytest.mark.parametrize("environment", [Environment.LOCAL, Environment.TEST])
async def test_development_delivery_prints_the_token(
    environment: Environment, capsys: pytest.CaptureFixture[str]
) -> None:
    """A developer has to be able to finish the flow on their own machine."""
    channel = ConsoleResetDeliveryChannel(_settings(environment))

    await channel.send(email="dev@docura.example", token=TOKEN)

    assert TOKEN in capsys.readouterr().err


@pytest.mark.parametrize("environment", [Environment.STAGING, Environment.PRODUCTION])
async def test_no_token_is_emitted_outside_development(
    environment: Environment, capsys: pytest.CaptureFixture[str]
) -> None:
    """A reset credential must never reach a shared console or log sink."""
    channel = ConsoleResetDeliveryChannel(_settings(environment))

    await channel.send(email="user@docura.example", token=TOKEN)

    captured = capsys.readouterr()
    assert TOKEN not in captured.out
    assert TOKEN not in captured.err


async def test_missing_transport_is_reported_rather_than_ignored(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """The absent mailer must be loud, not a silently dropped reset."""
    channel = ConsoleResetDeliveryChannel(_settings(Environment.PRODUCTION))

    with caplog.at_level("ERROR"):
        await channel.send(email="user@docura.example", token=TOKEN)

    assert "auth.password_reset_delivery_unconfigured" in caplog.text
    assert TOKEN not in caplog.text


def test_the_application_builds_a_channel_for_every_environment() -> None:
    """``create_app`` depends on this never returning None."""
    for environment in Environment:
        assert build_delivery_channel(_settings(environment)) is not None
