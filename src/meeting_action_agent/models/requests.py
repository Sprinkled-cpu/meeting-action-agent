"""
API Request schemas.
"""

from typing import Optional, Literal
from pydantic import BaseModel, Field


class AnalyzeTranscriptRequest(BaseModel):
    """Request payload for /api/v1/analyze."""
    transcript: str = Field(..., description="Raw meeting transcript text", min_length=10)
    format: Literal["auto", "plaintext", "vtt", "srt"] = Field(
        "auto", description="Transcript format; auto-detected if auto"
    )
    meeting_title: Optional[str] = Field(None, description="Optional override title")
    provider: Optional[Literal["mock", "openai", "gemini"]] = Field(
        None, description="Inference provider override"
    )
    detect_contradictions: bool = Field(True, description="Enable conflict and ambiguity analysis")


class ExportRequest(BaseModel):
    """Request payload for exporting action plans."""
    format: Literal["json", "markdown", "jira_csv", "jira_json"] = Field("markdown")
