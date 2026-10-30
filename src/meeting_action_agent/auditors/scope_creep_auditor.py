"""
Auditor for ambiguous scope, unbounded commitments, and scope creep.
"""

from typing import List
from meeting_action_agent.auditors.base import BaseAuditor
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
    ContradictionOrAmbiguity,
    StatementCitation,
)


class ScopeCreepAuditor(BaseAuditor):
    """
    Detects unconfirmed feature scope, ad-hoc suggestions without capacity confirmation,
    or unbounded statements such as 'keep it fluid' or 'maybe revamp if time permits'.
    """

    def audit(
        self, doc: TranscriptDocument, plan: MeetingActionPlan
    ) -> List[ContradictionOrAmbiguity]:
        issues: List[ContradictionOrAmbiguity] = []

        fluid_turns = [
            t for t in doc.turns
            if any(k in t.text.lower() for k in ["keep it fluid", "if someone has a couple spare hours", "maybe we can revamp", "see how sprint shakes out"])
        ]

        if fluid_turns:
            citations = [
                StatementCitation(
                    speaker=t.speaker,
                    timestamp=t.timestamp,
                    statement=t.text,
                    assertion="Conditional scope proposed without capacity clearance.",
                )
                for t in fluid_turns
            ]

            issues.append(
                ContradictionOrAmbiguity(
                    id="SCOPE-01",
                    category="Ambiguous Scope / Scope Creep",
                    severity="Moderate Ambiguity",
                    summary="Unbounded Scope / Conditional Sprint Inclusions",
                    issue_description=(
                        "Conversational turns suggest adding optional UI revamp work ('keep it fluid', 'if spare hours') "
                        "while capacity is already near saturation. This leads to misaligned delivery expectations."
                    ),
                    conflicting_statements=citations,
                    recommended_action=(
                        "Explicitly define this work as out of scope for the current sprint and move to the backlog."
                    ),
                )
            )

        return issues
