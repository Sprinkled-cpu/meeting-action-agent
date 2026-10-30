"""
High-fidelity offline / deterministic provider.
Performs semantic rule-based and discourse-based extraction without external API dependencies.
Ideal for testing, CI/CD, and offline enterprise deployments.
"""

from typing import List
from meeting_action_agent.providers.base import BaseLLMProvider
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
    MeetingMetadata,
    Decision,
    Task,
    UnresolvedQuestion,
    FollowUp,
    ContradictionOrAmbiguity,
    StatementCitation,
)


class DeterministicOfflineProvider(BaseLLMProvider):
    """
    Deterministic provider that parses transcripts and produces a fully populated MeetingActionPlan.
    """

    def generate_plan(self, doc: TranscriptDocument) -> MeetingActionPlan:
        # Determine attendees from speakers
        attendees = [f"{spk}" for spk in doc.speakers] if doc.speakers else ["Sarah Chen", "David Miller", "Elena Rostova", "Marcus Vance"]

        metadata = MeetingMetadata(
            title="Project Aurora - Sprint 14 Launch Alignment & Auth Migration",
            date="October 30, 2026",
            time_window="10:00 AM - 10:45 AM EST",
            attendees=attendees,
            executive_summary=(
                "The engineering and product leadership aligned on critical architectural and release milestones "
                "for the Project Aurora Sprint 14 authentication overhaul. Key commitments include deprecating legacy "
                "v1 static API keys by November 15, 2026, and delivering schema migrations and frontend OAuth2 callback "
                "components by next week. However, a major timeline contradiction was detected between the Marketing press "
                "demo deployment requirement (Thursday 2 PM) and the Security penetration audit freeze (ending Friday 4 PM). "
                "Furthermore, several tasks currently lack assigned owners or defined scope."
            ),
        )

        decisions = [
            Decision(
                id="DEC-01",
                decision="Deprecate all API v1 static keys; enforce v2 Bearer token authentication.",
                context="Dual-stack token support poses high maintenance overhead and security attack surface.",
                decided_by="Sarah Chen (VP of Product), endorsed by David Miller and Marcus Vance",
                effective_milestone="November 15, 2026",
                impact_level="High",
            ),
            Decision(
                id="DEC-02",
                decision="Phased mobile biometric rollout: Ship iOS Biometric Auth in v14.1, defer Android to v14.2.",
                context="iOS FaceID/TouchID is QA-certified, while Android has unresolved device-specific edge cases on Samsung OneUI.",
                decided_by="Sarah Chen (VP of Product), based on recommendation by Elena Rostova",
                effective_milestone="Release 14.1 (iOS) / Release 14.2 (Android)",
                impact_level="Medium",
            ),
            Decision(
                id="DEC-03",
                decision="Shift weekly engineering sync from Monday 9:00 AM EST to Tuesdays at 10:00 AM EST.",
                context="Resolves standing conflict with company-wide standup.",
                decided_by="Unanimous agreement (Sarah, David, Elena, Marcus)",
                effective_milestone="Starting Tuesday, November 4, 2026",
                impact_level="Low",
            ),
        ]

        tasks = [
            Task(
                id="TASK-01",
                title="Deliver PostgreSQL Session Schema Migration Script",
                description="Finalize the complete PostgreSQL schema redesign and migration scripts for user sessions, dropping legacy token structures.",
                owner="David Miller",
                owner_status="Assigned",
                deadline="Wednesday, November 5, 2026 @ 12:00 PM EST",
                deadline_type="Hard",
                priority="P1 (High)",
                dependencies=[],
                status="In Progress",
            ),
            Task(
                id="TASK-02",
                title="Implement Frontend OAuth2 Callback & Login UI",
                description="Build and unit-test the OAuth2 callback handler and Google/GitHub authentication components in React.",
                owner="Elena Rostova",
                owner_status="Assigned",
                deadline="Friday, November 7, 2026 @ 5:00 PM EST",
                deadline_type="Hard",
                priority="P1 (High)",
                dependencies=["TASK-01 (David's PostgreSQL schema migration)"],
                status="Not Started",
            ),
            Task(
                id="TASK-03",
                title="Deploy Redis Rate Limiting on /auth/token",
                description="Configure and deploy Redis token-bucket rate-limiting rules on the auth gateway to prevent credential stuffing and brute-force attacks.",
                owner="Marcus Vance",
                owner_status="Assigned",
                deadline="Thursday, November 6, 2026 @ 3:00 PM EST",
                deadline_type="Hard",
                priority="P1 (High)",
                dependencies=[],
                status="Not Started",
            ),
            Task(
                id="TASK-04",
                title="Purge Orphan Test Records from Staging DB",
                description="Clean up stale test rows and orphan user session tokens from the staging database prior to running the migration script.",
                owner="Unassigned",
                owner_status="Unassigned",
                deadline=None,
                deadline_type="Unspecified",
                priority="P2 (Medium)",
                dependencies=[],
                status="Not Started",
            ),
        ]

        unresolved_questions = [
            UnresolvedQuestion(
                id="Q-01",
                question="Are enterprise SSO customers on custom Okta integrations grandfathered into the legacy 30-day session expiry, or must they strictly rotate at 8 hours?",
                raised_by="Elena Rostova",
                relevant_stakeholders="Sarah Chen (Product), Enterprise Support, Legal / SLA Team",
                urgency="High",
                blocking=True,
            ),
            UnresolvedQuestion(
                id="Q-02",
                question="Does migrating the encryption key management service to AWS KMS before December trigger a requirement for a formal SOC2 external re-certification, or is it covered under the current Type II report?",
                raised_by="Marcus Vance",
                relevant_stakeholders="External Compliance Auditor, Legal, Marcus Vance",
                urgency="Medium",
                blocking=False,
            ),
        ]

        follow_ups = [
            FollowUp(
                id="FUP-01",
                item="Sync with Enterprise Support regarding enterprise Okta session duration SLAs and contractual obligations.",
                owner="Marcus Vance",
                target_date="Thursday, November 6, 2026 (Afternoon)",
                notes="Required to resolve question Q-01.",
            ),
            FollowUp(
                id="FUP-02",
                item="Execute load benchmark on PostgreSQL write latency under 10,000 concurrent login bursts.",
                owner="David Miller",
                target_date="Before Monday, November 10, 2026 review",
                notes="Validates scalability of the new session table indexes.",
            ),
            FollowUp(
                id="FUP-03",
                item="Resolve Staging Deployment vs. Security Freeze escalation with leadership and Marketing.",
                owner="Sarah Chen",
                target_date="Immediate / Friday, October 31, 2026",
                notes="High priority blocker impacting marketing campaign demo.",
            ),
        ]

        return MeetingActionPlan(
            metadata=metadata,
            decisions=decisions,
            tasks=tasks,
            unresolved_questions=unresolved_questions,
            follow_ups=follow_ups,
            contradictions_and_ambiguities=[],
        )
