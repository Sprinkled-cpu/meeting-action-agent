"""
Export format conversion endpoints.
"""

from fastapi import APIRouter, Response
from meeting_action_agent.models.core import MeetingActionPlan
from meeting_action_agent.exporters.markdown_exporter import MarkdownExporter
from meeting_action_agent.exporters.jira_exporter import JiraExporter

router = APIRouter(prefix="/api/v1/export", tags=["Export"])

md_exporter = MarkdownExporter()
jira_exporter = JiraExporter()


@router.post("/markdown")
def export_markdown(plan: MeetingActionPlan):
    """Exports an action plan into formatted executive Markdown."""
    markdown_content = md_exporter.export(plan)
    return Response(content=markdown_content, media_type="text/markdown")


@router.post("/jira-csv")
def export_jira_csv(plan: MeetingActionPlan):
    """Exports tasks into JIRA-compatible CSV format."""
    csv_content = jira_exporter.to_csv(plan)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": 'attachment; filename="jira_tasks.csv"'},
    )


@router.post("/jira-json")
def export_jira_json(plan: MeetingActionPlan):
    """Exports tasks into structured tickets for JIRA/Linear API integration."""
    return jira_exporter.to_json(plan)
