"""
Base interface for transcript and action-plan auditors.
"""

from abc import ABC, abstractmethod
from typing import List
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
    ContradictionOrAmbiguity,
)


class BaseAuditor(ABC):
    """Abstract interface for auditing discrepancies and risks in meeting transcripts."""

    @abstractmethod
    def audit(
        self, doc: TranscriptDocument, plan: MeetingActionPlan
    ) -> List[ContradictionOrAmbiguity]:
        """Inspects transcript discourse and action plan to discover issues."""
        pass
