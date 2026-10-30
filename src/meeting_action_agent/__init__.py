"""
AI Meeting-to-Action Agent
Enterprise-grade discourse analysis, decision extraction, action item tracking & contradiction auditing.
"""

__version__ = "1.0.0"
__author__ = "Production AI Engineering Team"

from meeting_action_agent.models.core import (
    MeetingActionPlan,
    MeetingMetadata,
    Decision,
    Task,
    UnresolvedQuestion,
    FollowUp,
    ContradictionOrAmbiguity,
    StatementCitation,
    DialogueTurn,
    TranscriptDocument,
)
from meeting_action_agent.core.pipeline import MeetingToActionPipeline

__all__ = [
    "MeetingActionPlan",
    "MeetingMetadata",
    "Decision",
    "Task",
    "UnresolvedQuestion",
    "FollowUp",
    "ContradictionOrAmbiguity",
    "StatementCitation",
    "DialogueTurn",
    "TranscriptDocument",
    "MeetingToActionPipeline",
]
