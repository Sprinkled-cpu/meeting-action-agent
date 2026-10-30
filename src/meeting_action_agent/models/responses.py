"""
API Response schemas.
"""

from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field
from meeting_action_agent.models.core import MeetingActionPlan


class ApiResponse(BaseModel):
    """Standard unified response wrapper."""
    success: bool = True
    message: str = "Success"
    data: Optional[Any] = None
    execution_time_ms: float = 0.0


class AnalysisResponse(BaseModel):
    """Analysis result response with plan and execution metadata."""
    success: bool = True
    plan: MeetingActionPlan
    format_detected: str
    turns_parsed: int
    speakers_identified: List[str]
    execution_time_ms: float


class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
    environment: str
    provider: str
