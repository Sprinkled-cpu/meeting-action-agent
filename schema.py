"""
Data schemas for AI Meeting-to-Action Agent using Pydantic v2.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class Decision(BaseModel):
    id: str = Field(..., description="Unique identifier for the decision, e.g., DEC-01")
    decision: str = Field(..., description="Clear summary of the agreed decision")
    context: str = Field(..., description="Background rationale or motivation behind the decision")
    decided_by: str = Field(..., description="Person or group who approved the decision")
    effective_milestone: Optional[str] = Field(None, description="When the decision takes effect")
    impact_level: Literal["High", "Medium", "Low"] = Field(..., description="Impact of the decision")


class Task(BaseModel):
    id: str = Field(..., description="Unique identifier for the task, e.g., TASK-01")
    title: str = Field(..., description="Short title of the task")
    description: str = Field(..., description="Detailed description of what needs to be delivered")
    owner: str = Field(..., description="Assigned individual, or 'Unassigned' if not designated")
    owner_status: Literal["Assigned", "Unassigned", "Ambiguous"] = Field(
        ..., description="Assignment certainty status"
    )
    deadline: Optional[str] = Field(None, description="Exact deadline with date/time if specified")
    deadline_type: Literal["Hard", "Soft", "Unspecified"] = Field(
        ..., description="Type of deadline commitment"
    )
    priority: Literal["P0 (Urgent)", "P1 (High)", "P2 (Medium)", "P3 (Low)"] = Field(...)
    dependencies: List[str] = Field(default_factory=list, description="IDs or descriptions of blocking dependencies")
    status: Literal["Not Started", "In Progress", "Blocked"] = Field("Not Started")


class UnresolvedQuestion(BaseModel):
    id: str = Field(..., description="Unique identifier for the question, e.g., Q-01")
    question: str = Field(..., description="The exact question or unknown left open")
    raised_by: str = Field(..., description="Person who asked the question")
    relevant_stakeholders: str = Field(..., description="Party or role needed to answer")
    urgency: Literal["Critical", "High", "Medium", "Low"] = Field(...)
    blocking: bool = Field(False, description="Whether this blocks release or engineering progress")


class FollowUp(BaseModel):
    id: str = Field(..., description="Unique identifier for the follow-up, e.g., FUP-01")
    item: str = Field(..., description="Follow-up action or investigation")
    owner: str = Field(..., description="Person responsible for the follow-up")
    target_date: Optional[str] = Field(None, description="Target timeline for the follow-up")
    notes: Optional[str] = Field(None, description="Additional context or expectations")


class StatementCitation(BaseModel):
    speaker: str
    timestamp: Optional[str] = None
    statement: str
    assertion: str


class ContradictionOrAmbiguity(BaseModel):
    id: str = Field(..., description="Unique identifier, e.g., WARN-01")
    category: Literal[
        "Direct Contradiction",
        "Conflicting Timelines",
        "Unclear Ownership",
        "Ambiguous Scope / Scope Creep",
        "Missing Acceptance Criteria"
    ] = Field(..., description="Category of the communication issue")
    severity: Literal["Critical Blocker", "High Risk", "Moderate Ambiguity", "Low Advisory"] = Field(...)
    summary: str = Field(..., description="Concise headline of the conflict or ambiguity")
    issue_description: str = Field(..., description="Explanation of what makes this problematic or unclear")
    conflicting_statements: List[StatementCitation] = Field(
        default_factory=list, description="Direct excerpts from transcript illustrating the conflict"
    )
    recommended_action: str = Field(..., description="Actionable recommendation to resolve the issue")


class MeetingMetadata(BaseModel):
    title: str = Field(..., description="Meeting topic or project title")
    date: str = Field(..., description="Meeting date")
    time_window: str = Field(..., description="Start and end time")
    attendees: List[str] = Field(..., description="List of attendees with roles")
    executive_summary: str = Field(..., description="High-level 2-3 paragraph synthesis of outcomes")


class MeetingActionPlan(BaseModel):
    metadata: MeetingMetadata
    decisions: List[Decision] = Field(default_factory=list)
    tasks: List[Task] = Field(default_factory=list)
    unresolved_questions: List[UnresolvedQuestion] = Field(default_factory=list)
    follow_ups: List[FollowUp] = Field(default_factory=list)
    contradictions_and_ambiguities: List[ContradictionOrAmbiguity] = Field(default_factory=list)
