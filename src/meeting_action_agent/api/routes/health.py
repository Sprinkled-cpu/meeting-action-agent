"""
Health check and diagnostics route.
"""

from fastapi import APIRouter
from meeting_action_agent.models.responses import HealthResponse
from meeting_action_agent.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check():
    settings = get_settings()
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        environment=settings.app_env,
        provider=settings.default_provider,
    )


@router.get("/ready")
def readiness_check():
    return {"ready": True}
