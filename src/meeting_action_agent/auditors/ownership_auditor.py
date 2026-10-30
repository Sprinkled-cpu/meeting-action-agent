"""
Auditor for unassigned action items and ambiguous task allocations.
"""

from typing import List
from meeting_action_agent.auditors.base import BaseAuditor
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
    ContradictionOrAmbiguity,
    StatementCitation,
)


class OwnershipAmbiguityAuditor(BaseAuditor):
    """
    Detects tasks or verbal commitments where:
    1. An action item was explicitly created with owner 'Unassigned' or 'Ambiguous'.
    2. Utterances show bystander diffusion (e.g. 'someone should', 'whoever has bandwidth').
    """

    def audit(
        self, doc: TranscriptDocument, plan: MeetingActionPlan
    ) -> List[ContradictionOrAmbiguity]:
        issues: List[ContradictionOrAmbiguity] = []

        # 1. Audit explicit plan tasks
        unassigned_tasks = [t for t in plan.tasks if t.owner_status != "Assigned" or t.owner.lower() in ["unassigned", "tbd", "someone"]]
        for t in unassigned_tasks:
            issues.append(
                ContradictionOrAmbiguity(
                    id=f"OWNER-{t.id}",
                    category="Unclear Ownership",
                    severity="High Risk",
                    summary=f"Unassigned Action Item: {t.title}",
                    issue_description=(
                        f"Task '{t.title}' is documented as actionable work but lacks a dedicated accountable owner. "
                        f"Tasks without assigned owners have a high abandonment probability."
                    ),
                    conflicting_statements=[],
                    recommended_action=f"Assign an explicit DRI (Directly Responsible Individual) for {t.id} with a committed deadline.",
                )
            )

        # 2. Audit transcript discourse for diffused phrasing
        vague_assignment_turns = [
            t for t in doc.turns
            if any(p in t.text.lower() for p in ["someone on ops", "someone should", "whoever has spare", "grab it whenever"])
        ]
        if vague_assignment_turns and not any(i.id.startswith("OWNER-") for i in issues):
            citations = [
                StatementCitation(
                    speaker=t.speaker,
                    timestamp=t.timestamp,
                    statement=t.text,
                    assertion="Task mentioned without assigning specific responsibility.",
                )
                for t in vague_assignment_turns
            ]
            issues.append(
                ContradictionOrAmbiguity(
                    id="OWNER-DISC-01",
                    category="Unclear Ownership",
                    severity="High Risk",
                    summary="Diffused Task Ownership in Discussion",
                    issue_description="Discussion references work to be done but uses vague phrasing like 'someone should grab it whenever'.",
                    conflicting_statements=citations,
                    recommended_action="Designate a single accountable team member and record in sprint tracker.",
                )
            )

        return issues
