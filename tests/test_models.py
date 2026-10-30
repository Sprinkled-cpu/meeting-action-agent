"""
Unit tests for data schemas and validation.
"""

import unittest
from meeting_action_agent.models.core import (
    Task,
    Decision,
    UnresolvedQuestion,
    FollowUp,
    ContradictionOrAmbiguity,
    MeetingActionPlan,
    MeetingMetadata,
    AlignmentMetrics,
)
from pydantic import ValidationError


class TestModels(unittest.TestCase):

    def test_valid_task_model(self):
        task = Task(
            id="TASK-01",
            title="Database Migration",
            description="Run PostgreSQL migration",
            owner="David Miller",
            owner_status="Assigned",
            deadline="2026-11-05",
            deadline_type="Hard",
            priority="P1 (High)",
        )
        self.assertEqual(task.id, "TASK-01")
        self.assertEqual(task.status, "Not Started")

    def test_invalid_task_priority(self):
        with self.assertRaises(ValidationError):
            Task(
                id="TASK-01",
                title="Test",
                description="Test description",
                owner="Someone",
                owner_status="Assigned",
                deadline_type="Hard",
                priority="Critical",  # Invalid priority literal
            )

    def test_meeting_action_plan_serialization(self):
        plan = MeetingActionPlan(
            metadata=MeetingMetadata(
                title="Test Meeting",
                date="2026-10-30",
                time_window="10:00 - 11:00",
                attendees=["Alice", "Bob"],
                executive_summary="Summary text here.",
            ),
            decisions=[
                Decision(
                    id="DEC-01",
                    decision="Adopt v2 tokens",
                    context="Better security",
                    decided_by="Alice",
                    impact_level="High",
                )
            ],
            tasks=[],
            unresolved_questions=[],
            follow_ups=[],
            contradictions_and_ambiguities=[],
            metrics=AlignmentMetrics(),
        )

        json_str = plan.model_dump_json()
        self.assertIn("Test Meeting", json_str)
        self.assertIn("Adopt v2 tokens", json_str)

        # Re-parse from JSON
        restored = MeetingActionPlan.model_validate_json(json_str)
        self.assertEqual(restored.metadata.title, "Test Meeting")
        self.assertEqual(len(restored.decisions), 1)


if __name__ == "__main__":
    unittest.main()
