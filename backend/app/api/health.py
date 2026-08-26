"""Liveness and readiness endpoints.

The two are kept apart on purpose. ``/health`` answers "is this process alive",
touches no dependency, and must never fail because Postgres is down — an
orchestrator that restarts the service on a database blip turns a recoverable
outage into a crash loop. ``/health/ready`` answers "can this process serve
traffic", and that one does check the database.
"""

from __future__ import annotations

from typing import Literal

from fastapi import APIRouter, Request, Response, status
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.db.session import check_health

router = APIRouter(tags=["health"])


class LivenessResponse(BaseModel):
    status: Literal["ok"] = "ok"
    service: str
    version: str
    environment: str


class ReadinessResponse(BaseModel):
    status: Literal["ready", "not_ready"]
    service: str
    version: str
    checks: dict[str, str] = Field(
        description="Dependency name to 'ok' or 'unavailable'.",
    )


@router.get(
    "/health",
    response_model=LivenessResponse,
    summary="Liveness probe",
    status_code=status.HTTP_200_OK,
)
async def liveness(request: Request) -> LivenessResponse:
    """Return 200 whenever the process is running and can route a request."""
    settings: Settings = request.app.state.settings
    return LivenessResponse(
        service=settings.service_name,
        version=settings.version,
        environment=settings.environment.value,
    )


@router.get(
    "/health/ready",
    response_model=ReadinessResponse,
    summary="Readiness probe",
    responses={503: {"description": "A dependency is unavailable."}},
)
async def readiness(request: Request, response: Response) -> ReadinessResponse:
    """Check every dependency needed to serve traffic.

    Returns 503 rather than raising, so the body always itemises which dependency
    failed — a probe that only reports a status code makes an outage take longer
    to diagnose than it needs to.
    """
    settings: Settings = request.app.state.settings
    database_ok = await check_health(request.app.state.engine)

    checks = {"database": "ok" if database_ok else "unavailable"}
    all_ok = all(value == "ok" for value in checks.values())

    if not all_ok:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

    return ReadinessResponse(
        status="ready" if all_ok else "not_ready",
        service=settings.service_name,
        version=settings.version,
        checks=checks,
    )
