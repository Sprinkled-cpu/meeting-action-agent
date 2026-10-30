"""
Core Domain Models for AI Meeting-to-Action Agent using Pydantic v2.
"""

from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, ConfigDict


class DialogueTurn(BaseModel):
    """Represents an individual spoken utterance in the meeting."""
    index: int
    speaker: str
    timestamp: Optional[str] = None
    text: str
    detected_intent: Optional[str] = None


class TranscriptDocument(BaseModel):
    """Normalized structured transcript document representation."""
    format: Literal["plaintext", "vtt", "srt", "json"]
    raw_text: str
    turns: List[DialogueTurn] = Field(default_factory=list)
    speakers: List[str] = Field(default_factory=list)


class Decision(BaseModel):
    id: str = Field(..., description="Unique decision ID, e.g. DEC-01")
    decision: str = Field(..., description="Clear description of the agreed decision")
    context: str = Field(..., description="Rationale, driver, or operational background")
    decided_by: str = Field(..., description="Decision-maker or approving authority")
    effective_milestone: Optional[str] = Field(None, description="When decision takes effect")
    impact_level: Literal["High", "Medium", "Low"] = Field(..., description="Impact severity")


class Task(BaseModel):
    id: str = Field(..., description="Unique task ID, e.g. TASK-01")
    title: str = Field(..., description="Concise task title")
    description: str = Field(..., description="Detailed deliverable specification")
    owner: str = Field(..., description="Assigned individual or 'Unassigned'")
    owner_status: Literal["Assigned", "Unassigned", "Ambiguous"] = Field(
        ..., description="Certainty level of assignment"
    )
    deadline: Optional[str] = Field(None, description="Committed deadline timestamp/date")
    deadline_type: Literal["Hard", "Soft", "Unspecified"] = Field(
        ..., description="Firmness of the committed date"
    )
    priority: Literal["P0 (Urgent)", "P1 (High)", "P2 (Medium)", "P3 (Low)"] = Field(...)
    dependencies: List[str] = Field(default_factory=list, description="IDs of blocking tasks or milestones")
    status: Literal["Not Started", "In Progress", "Blocked", "Done"] = Field("Not Started")


class UnresolvedQuestion(BaseModel):
    id: str = Field(..., description="Unique question ID, e.g. Q-01")
    question: str = Field(..., description="The unanswered question or unknown")
    raised_by: str = Field(..., description="Person who raised the question")
    relevant_stakeholders: str = Field(..., description="Owners or parties required to resolve")
    urgency: Literal["Critical", "High", "Medium", "Low"] = Field(...)
    blocking: bool = Field(False, description="Whether this actively blocks progress")


class FollowUp(BaseModel):
    id: str = Field(..., description="Unique follow-up ID, e.g. FUP-01")
    item: str = Field(..., description="Action or research item")
    owner: str = Field(..., description="Person accountable")
    target_date: Optional[str] = Field(None, description="Expected completion date")
    notes: Optional[str] = Field(None, description="Operational notes")


class StatementCitation(BaseModel):
    speaker: str
    timestamp: Optional[str] = None
    statement: str
    assertion: str


class ContradictionOrAmbiguity(BaseModel):
    id: str = Field(..., description="Unique issue ID, e.g. WARN-01")
    category: Literal[
        "Direct Contradiction",
        "Conflicting Timelines",
        "Unclear Ownership",
        "Ambiguous Scope / Scope Creep",
        "Missing Acceptance Criteria"
    ] = Field(..., description="Category of communication discrepancy")
    severity: Literal["Critical Blocker", "High Risk", "Moderate Ambiguity", "Low Advisory"] = Field(...)
    summary: str = Field(..., description="Short headline of the discrepancy")
    issue_description: str = Field(..., description="Detailed analysis of the conflict")
    conflicting_statements: List[StatementCitation] = Field(
        default_factory=list, description="Direct citations with timestamps"
    )
    recommended_action: str = Field(..., description="Prescribed remediation steps")


class MeetingMetadata(BaseModel):
    title: str = Field(..., description="Title of the meeting")
    date: str = Field(..., description="Date of the meeting")
    time_window: str = Field(..., description="Time duration")
    attendees: List[str] = Field(default_factory=list, description="Attendees list")
    executive_summary: str = Field(..., description="Executive level 2-3 paragraph synthesis")


class AlignmentMetrics(BaseModel):
    total_decisions: int = 0
    total_tasks: int = 0
    assigned_tasks: int = 0
    unassigned_tasks: int = 0
    total_questions: int = 0
    blocking_questions: int = 0
    critical_contradictions: int = 0
    warnings: int = 0
    alignment_score: float = Field(
        100.0, description="Meeting health score out of 100 based on clarity and conflicts"
    )


class MeetingActionPlan(BaseModel):
    metadata: MeetingMetadata
    decisions: List[Decision] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    unresolved_questions: List[UnresolvedQuestion] = Field(default_factory=list)
    follow_ups: List[FollowUp] = Field(default_factory=list)
    contradictions_and_ambiguities: List[ContradictionOrAmbiguity] = Field(default_factory=list)
    metrics: AlignmentMetrics = Field(default_factory=AlignmentMetrics)

    model_config = ConfigDict(populate_by_name=True)
