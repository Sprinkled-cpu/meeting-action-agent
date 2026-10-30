"""
Base interface for transcript parsers.
"""

from abc import ABC, abstractmethod
from meeting_action_agent.models.core import TranscriptDocument


class BaseTranscriptParser(ABC):
    """Abstract base parser for meeting transcripts."""

    @abstractmethod
    def parse(self, text: str) -> TranscriptDocument:
        """Parses raw transcript string into a structured TranscriptDocument."""
        pass
