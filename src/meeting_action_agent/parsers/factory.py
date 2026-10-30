"""
Factory and auto-detector for transcript formats.
"""

from meeting_action_agent.parsers.base import BaseTranscriptParser
from meeting_action_agent.parsers.text_parser import PlainTextTranscriptParser
from meeting_action_agent.parsers.vtt_parser import WebVTTTranscriptParser
from meeting_action_agent.parsers.srt_parser import SRTTranscriptParser


def get_parser(format_hint: str = "auto", raw_text: str = "") -> BaseTranscriptParser:
    """
    Returns the appropriate parser based on explicit format hint or auto-detection.
    """
    hint = format_hint.lower()
    if hint == "vtt" or (hint == "auto" and "WEBVTT" in raw_text[:200]):
        return WebVTTTranscriptParser()
    if hint == "srt" or (hint == "auto" and "-->" in raw_text and "," in raw_text[:200]):
        return SRTTranscriptParser()
    
    return PlainTextTranscriptParser()
