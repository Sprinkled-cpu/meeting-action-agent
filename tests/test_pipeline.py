"""
Unit and integration tests for the MeetingToActionPipeline.
"""

import unittest
from meeting_action_agent.core.pipeline import MeetingToActionPipeline


SAMPLE_TRANSCRIPT = """
[10:00:15] Sarah Chen: Good morning team. Let's make an executive decision: deprecate API v1 keys on Nov 15.
[10:01:42] David Miller: I will deliver the complete PostgreSQL schema migration by Wednesday, Nov 5 at 12 PM.
[10:03:05] Elena Rostova: I will implement the OAuth2 login components by Friday, Nov 7 at 5 PM.
[10:14:10] Sarah Chen: We need the staging build deployed by Thursday at 2 PM for marketing press briefing.
[10:20:45] Marcus Vance: We cannot deploy staging builds because security audit freeze runs through Friday at 4 PM.
[10:28:10] David Miller: Someone on ops or backend should purge the orphan records from staging DB.
"""


class TestPipeline(unittest.TestCase):

    def setUp(self):
        self.pipeline = MeetingToActionPipeline(provider_name="mock", enable_audit=True)

    def test_pipeline_execution(self):
        plan, doc, execution_ms = self.pipeline.process(SAMPLE_TRANSCRIPT)

        self.assertIsNotNone(plan)
        self.assertIsNotNone(doc)
        self.assertGreater(execution_ms, 0)
        self.assertGreater(len(plan.decisions), 0)
        self.assertGreater(len(plan.tasks), 0)
        self.assertGreater(len(plan.contradictions_and_ambiguities), 0)

        # Check that conflict between marketing deployment and security freeze was identified
        conflict_types = [c.category for c in plan.contradictions_and_ambiguities]
        self.assertIn("Conflicting Timelines", conflict_types)

    def test_pipeline_exports(self):
        plan, _, _ = self.pipeline.process(SAMPLE_TRANSCRIPT)
        markdown = self.pipeline.export_markdown(plan)
        json_str = self.pipeline.export_json(plan)
        jira_csv = self.pipeline.export_jira_csv(plan)

        self.assertIn("# 📋 Executive Meeting Summary", markdown)
        self.assertIn("DEC-01", json_str)
        self.assertIn("Issue Key,Summary", jira_csv)


if __name__ == "__main__":
    unittest.main()
