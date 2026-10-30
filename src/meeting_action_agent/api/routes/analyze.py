"""
Transcript analysis API routes.
"""

from fastapi import APIRouter, HTTPException, Request
from typing import Optional
from meeting_action_agent.models.requests import AnalyzeTranscriptRequest
from meeting_action_agent.models.responses import AnalysisResponse
from meeting_action_agent.core.pipeline import MeetingToActionPipeline
from meeting_action_agent.exceptions import MeetingActionAgentError
from meeting_action_agent.logging_config import logger

router = APIRouter(prefix="/api/v1", tags=["Analysis"])


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_transcript(request: AnalyzeTranscriptRequest):
    """
    Parses a meeting transcript, extracts decisions, tasks, questions, and follow-ups,
    and runs the contradiction & ambiguity detection audit.
    """
    try:
        pipeline = MeetingToActionPipeline(
            provider_name=request.provider,
            enable_audit=request.detect_contradictions,
        )
        plan, doc, execution_ms = pipeline.process(
            raw_text=request.transcript,
            format_hint=request.format,
            meeting_title_override=request.meeting_title,
        )
        return AnalysisResponse(
            success=True,
            plan=plan,
            format_detected=doc.format,
            turns_parsed=len(doc.turns),
            speakers_identified=doc.speakers,
            execution_time_ms=execution_ms,
        )
    except MeetingActionAgentError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.exception(f"Unexpected server error during analysis: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server processing error.")


@router.post("/analyze/raw", response_model=AnalysisResponse)
async def analyze_raw_stream(
    request: Request,
    format: str = "auto",
    title: Optional[str] = None,
    detect_contradictions: bool = True,
):
    """
    Accepts raw transcript text stream directly in request body (e.g. text/plain or octet-stream).
    Does not require python-multipart.
    """
    try:
        body = await request.body()
        raw_text = body.decode("utf-8", errors="replace")
        if not raw_text.strip():
            raise HTTPException(status_code=400, detail="Request body cannot be empty.")

        pipeline = MeetingToActionPipeline(enable_audit=detect_contradictions)
        plan, doc, execution_ms = pipeline.process(
            raw_text=raw_text,
            format_hint=format,
            meeting_title_override=title,
        )
        return AnalysisResponse(
            success=True,
            plan=plan,
            format_detected=doc.format,
            turns_parsed=len(doc.turns),
            speakers_identified=doc.speakers,
            execution_time_ms=execution_ms,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Raw analysis failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Check if python-multipart is available before registering multipart file-upload route
try:
    import multipart
    from fastapi import UploadFile, File, Form

    @router.post("/analyze/upload", response_model=AnalysisResponse)
    async def analyze_file_upload(
        file: UploadFile = File(...),
        detect_contradictions: bool = Form(True),
        meeting_title: Optional[str] = Form(None),
    ):
        """Uploads and analyzes a transcript file (.txt, .vtt, .srt)."""
        content_bytes = await file.read()
        raw_text = content_bytes.decode("utf-8", errors="replace")

        filename = file.filename or ""
        format_hint = "auto"
        if filename.endswith(".vtt"):
            format_hint = "vtt"
        elif filename.endswith(".srt"):
            format_hint = "srt"

        pipeline = MeetingToActionPipeline(enable_audit=detect_contradictions)
        plan, doc, execution_ms = pipeline.process(
            raw_text=raw_text,
            format_hint=format_hint,
            meeting_title_override=meeting_title,
        )
        return AnalysisResponse(
            success=True,
            plan=plan,
            format_detected=doc.format,
            turns_parsed=len(doc.turns),
            speakers_identified=doc.speakers,
            execution_time_ms=execution_ms,
        )
except (ImportError, RuntimeError):
    # python-multipart not installed; /analyze/raw is the high-performance alternative
    pass
