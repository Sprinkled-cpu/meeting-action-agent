"""
Unit tests for contradiction, ownership, and scope auditors.
"""

import unittest
from meeting_action_agent.models.core import (
    TranscriptDocument,
    DialogueTurn,
    MeetingActionPlan,
    MeetingMetadata,
    Task,
)
from meeting_action_agent.auditors.conflict_detector import TimelineConflictDetector
from meeting_action_agent.auditors.ownership_auditor import OwnershipAmbiguityAuditor
from meeting_action_agent.auditors.scope_creep_auditor import ScopeCreepAuditor
from meeting_action_agent.auditors.engine import DiscourseAuditingEngine


class TestAuditors(unittest.TestCase):

    def setUp(self):
        self.metadata = MeetingMetadata(
            title="Sprint Sync",
            date="2026-10-30",
            time_window="10:00 - 10:30",
            attendees=["Sarah", "Marcus"],
            executive_summary="Summary",
        )

    def test_timeline_conflict_detector(self):
        doc = TranscriptDocument(
            format="plaintext",
            raw_text="...",
            turns=[
                DialogueTurn(
                    index=1,
                    speaker="Sarah",
                    timestamp="10:14",
                    text="We need the staging build deployed by Thursday for marketing press briefing.",
                ),
                DialogueTurn(
                    index=2,
                    speaker="Marcus",
                    timestamp="10:20",
                    text="We have a freeze policy: no staging deployments are permitted until the security audit finishes.",
                ),
            ],
            speakers=["Sarah", "Marcus"],
        )
        plan = MeetingActionPlan(metadata=self.metadata)
        detector = TimelineConflictDetector()
        issues = detector.audit(doc, plan)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].category, "Conflicting Timelines")
        self.assertIn("Marketing Press Staging Deployment", issues[0].summary)

    def test_ownership_ambiguity_auditor(self):
        doc = TranscriptDocument(format="plaintext", raw_text="...", turns=[], speakers=[])
        plan = MeetingActionPlan(
            metadata=self.metadata,
            tasks=[
                Task(
                    id="TASK-99",
                    title="Orphan record cleanup",
                    description="Purge test records",
                    owner="Unassigned",
                    owner_status="Unassigned",
                    deadline=None,
                    deadline_type="Unspecified",
                    priority="P2 (Medium)",
                )
            ],
        )
        auditor = OwnershipAmbiguityAuditor()
        issues = auditor.audit(doc, plan)

        self.assertGreaterEqual(len(issues), 1)
        self.assertEqual(issues[0].category, "Unclear Ownership")

    def test_scope_creep_auditor(self):
        doc = TranscriptDocument(
            format="plaintext",
            raw_text="...",
            turns=[
                DialogueTurn(
                    index=1,
                    speaker="Sarah",
                    text="Let's keep it fluid and see how sprint shakes out if someone has spare hours.",
                )
            ],
            speakers=["Sarah"],
        )
        plan = MeetingActionPlan(metadata=self.metadata)
        auditor = ScopeCreepAuditor()
        issues = auditor.audit(doc, plan)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].category, "Ambiguous Scope / Scope Creep")

    def test_auditing_engine_metrics_calculation(self):
        engine = DiscourseAuditingEngine()
        doc = TranscriptDocument(format="plaintext", raw_text="...", turns=[], speakers=[])
        plan = MeetingActionPlan(
            metadata=self.metadata,
            tasks=[
                Task(
                    id="TASK-01",
                    title="Task 1",
                    description="Desc",
                    owner="Alice",
                    owner_status="Assigned",
                    deadline="2026-11-01",
                    deadline_type="Hard",
                    priority="P1 (High)",
                )
            ],
        )
        metrics = engine.calculate_metrics(plan)
        self.assertEqual(metrics.alignment_score, 100.0)


if __name__ == "__main__":
    unittest.main()
