"""
JIRA and Linear task ticket exporter.
Generates standard CSV and JSON issue tracking schemas.
"""

import io
import csv
import json
from typing import List, Dict, Any
from meeting_action_agent.models.core import MeetingActionPlan


class JiraExporter:
    """Exports tasks into JIRA-compatible CSV and JSON representations."""

    def to_csv(self, plan: MeetingActionPlan) -> str:
        output = io.StringIO()
        fieldnames = [
            "Issue Key",
            "Summary",
            "Description",
            "Assignee",
            "Issue Type",
            "Priority",
            "Due Date",
            "Status",
            "Labels",
        ]
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for t in plan.tasks:
            priority_map = {
                "P0 (Urgent)": "Highest",
                "P1 (High)": "High",
                "P2 (Medium)": "Medium",
                "P3 (Low)": "Low",
            }
            writer.writerow({
                "Issue Key": t.id,
                "Summary": t.title,
                "Description": t.description + (f" (Dependencies: {', '.join(t.dependencies)})" if t.dependencies else ""),
                "Assignee": t.owner if t.owner_status == "Assigned" else "",
                "Issue Type": "Task",
                "Priority": priority_map.get(t.priority, "Medium"),
                "Due Date": t.deadline or "",
                "Status": "To Do" if t.status == "Not Started" else t.status,
                "Labels": "meeting-action-item",
            })

        return output.getvalue()

    def to_json(self, plan: MeetingActionPlan) -> List[Dict[str, Any]]:
        tickets = []
        for t in plan.tasks:
            tickets.append({
                "external_id": t.id,
                "title": t.title,
                "body": t.description,
                "assignee": t.owner if t.owner_status == "Assigned" else None,
                "due_date": t.deadline,
                "priority": t.priority,
                "dependencies": t.dependencies,
                "status": t.status,
            })
        return tickets
