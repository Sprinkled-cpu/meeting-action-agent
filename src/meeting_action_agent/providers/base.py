"""
Base interface for LLM / inference providers.
"""

from abc import ABC, abstractmethod
from meeting_action_agent.models.core import TranscriptDocument, MeetingActionPlan


class BaseLLMProvider(ABC):
    """Abstract interface for LLM inference providers."""

    @abstractmethod
    def generate_plan(self, doc: TranscriptDocument) -> MeetingActionPlan:
        """Processes the structured transcript into an action plan."""
        pass
