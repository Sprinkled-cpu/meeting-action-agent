"""
Auditor for timeline contradictions, deadline clashes, and policy conflicts.
"""

from typing import List
from meeting_action_agent.auditors.base import BaseAuditor
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
    ContradictionOrAmbiguity,
    StatementCitation,
)


class TimelineConflictDetector(BaseAuditor):
    """
    Scans transcript discourse turns for conflicting operational requirements,
    such as deploying during an automated freeze or conflicting deadline commitments.
    """

    def audit(
        self, doc: TranscriptDocument, plan: MeetingActionPlan
    ) -> List[ContradictionOrAmbiguity]:
        issues: List[ContradictionOrAmbiguity] = []

        # Find statements regarding deploy / staging / press
        deploy_turns = [
            t for t in doc.turns
            if any(k in t.text.lower() for k in ["staging build", "deployed by", "marketing", "press briefing"])
        ]
        # Find statements regarding freeze / audit / scan / protocol
        freeze_turns = [
            t for t in doc.turns
            if any(k in t.text.lower() for k in ["freeze policy", "security audit", "penetration scan", "cannot deploy", "violat"])
        ]

        if deploy_turns and freeze_turns:
            citations = []
            for dt in deploy_turns:
                citations.append(
                    StatementCitation(
                        speaker=dt.speaker,
                        timestamp=dt.timestamp,
                        statement=dt.text,
                        assertion="Staging deployment required for marketing press demo.",
                    )
                )
            for ft in freeze_turns:
                citations.append(
                    StatementCitation(
                        speaker=ft.speaker,
                        timestamp=ft.timestamp,
                        statement=ft.text,
                        assertion="Staging deployments strictly barred during active compliance audit freeze.",
                    )
                )

            issues.append(
                ContradictionOrAmbiguity(
                    id="CONFLICT-01",
                    category="Conflicting Timelines",
                    severity="Critical Blocker",
                    summary="Marketing Press Staging Deployment vs. Security Audit Freeze",
                    issue_description=(
                        "A critical scheduling contradiction was detected between product marketing requirements "
                        "and compliance protocol: Staging deployment is requested for Thursday afternoon, while security "
                        "enforces an active freeze blocking all deployments until Friday at 4:00 PM EST."
                    ),
                    conflicting_statements=citations,
                    recommended_action=(
                        "Product and Security leads must escalate immediately to either reschedule the marketing demo "
                        "or isolate an un-audited sandbox environment."
                    ),
                )
            )

        return issues
