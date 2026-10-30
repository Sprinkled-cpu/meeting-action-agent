"""
API route tests testing handlers and contract schemas directly.
"""

import unittest
from meeting_action_agent.api.routes.health import health_check, readiness_check
from meeting_action_agent.api.routes.analyze import analyze_transcript
from meeting_action_agent.api.routes.export import export_markdown, export_jira_csv, export_jira_json
from meeting_action_agent.models.requests import AnalyzeTranscriptRequest
from meeting_action_agent.models.core import MeetingActionPlan, MeetingMetadata


class TestApi(unittest.TestCase):

    def test_health_endpoint(self):
        resp = health_check()
        self.assertEqual(resp.status, "healthy")
        self.assertIsNotNone(resp.version)

    def test_readiness_endpoint(self):
        resp = readiness_check()
        self.assertTrue(resp["ready"])

    def test_analyze_endpoint(self):
        request = AnalyzeTranscriptRequest(
            transcript="[10:00:00] Alice: Let's agree to deprecate v1.\n[10:01:00] Bob: I will test by Thursday.",
            format="plaintext",
            detect_contradictions=True,
        )
        resp = analyze_transcript(request)
        self.assertTrue(resp.success)
        self.assertGreater(len(resp.plan.decisions), 0)
        self.assertGreater(len(resp.plan.tasks), 0)
        self.assertEqual(resp.format_detected, "plaintext")

    def test_export_markdown_endpoint(self):
        plan = MeetingActionPlan(
            metadata=MeetingMetadata(
                title="Test Meeting",
                date="2026-10-30",
                time_window="10:00 - 10:30",
                attendees=["Alice"],
                executive_summary="Summary here.",
            )
        )
        resp = export_markdown(plan)
        self.assertEqual(resp.media_type, "text/markdown")
        self.assertIn("# 📋 Executive Meeting Summary", resp.body.decode("utf-8"))

    def test_export_jira_endpoints(self):
        plan = MeetingActionPlan(
            metadata=MeetingMetadata(
                title="Test Meeting",
                date="2026-10-30",
                time_window="10:00 - 10:30",
                attendees=["Alice"],
                executive_summary="Summary here.",
            )
        )
        csv_resp = export_jira_csv(plan)
        self.assertEqual(csv_resp.media_type, "text/csv")
        self.assertIn("Issue Key,Summary", csv_resp.body.decode("utf-8"))

        json_resp = export_jira_json(plan)
        self.assertIsInstance(json_resp, list)


if __name__ == "__main__":
    unittest.main()
