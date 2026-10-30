"""
Markdown Executive Report Exporter.
"""

from meeting_action_agent.models.core import MeetingActionPlan


class MarkdownExporter:
    """Formats a MeetingActionPlan into an executive Markdown report."""

    def export(self, plan: MeetingActionPlan) -> str:
        m = plan.metadata
        md = []
        md.append(f"# 📋 Executive Meeting Summary & Action Plan")
        md.append(f"**Meeting:** {m.title}  ")
        md.append(f"**Date & Time:** {m.date} | {m.time_window}  ")
        md.append(f"**Attendees:** {', '.join(m.attendees)}  ")
        md.append(f"**Meeting Alignment Score:** `{plan.metrics.alignment_score}/100`  \n")

        md.append("---")
        md.append("## 📌 Executive Synthesis")
        md.append(m.executive_summary)
        md.append("")

        # Contradictions & Ambiguities Alert (Bonus)
        if plan.contradictions_and_ambiguities:
            md.append("---")
            md.append("## 🚨 Alignment Audit: Contradictions & Ambiguous Instructions (Bonus)")
            md.append("> **Automated Notice:** The agent detected contradictory constraints and unassigned responsibilities requiring intervention.\n")

            for issue in plan.contradictions_and_ambiguities:
                badge = (
                    "🔴 CRITICAL BLOCKER"
                    if "Critical" in issue.severity
                    else ("🟠 HIGH RISK" if "High" in issue.severity else "🟡 AMBIGUITY")
                )
                md.append(f"### `{issue.id}` [{badge}] {issue.summary}")
                md.append(f"- **Category:** `{issue.category}`")
                md.append(f"- **Analysis:** {issue.issue_description}")
                if issue.conflicting_statements:
                    md.append(f"- **Direct Transcript Citations:**")
                    for c in issue.conflicting_statements:
                        ts = f" at `{c.timestamp}`" if c.timestamp else ""
                        md.append(f"  - **{c.speaker}**{ts}: *\"{c.statement}\"*  \n    ↳ **Assertion:** {c.assertion}")
                md.append(f"- **💡 Recommended Resolution:** {issue.recommended_action}\n")

        # Decisions
        md.append("---")
        md.append("## 🏛️ Strategic Decisions Agreed")
        md.append("| ID | Decision | Rationale & Context | Decided By | Milestone / Effective | Impact |")
        md.append("|---|---|---|---|---|:---:|")
        for d in plan.decisions:
            md.append(
                f"| **{d.id}** | {d.decision} | {d.context} | {d.decided_by} | `{d.effective_milestone}` | `{d.impact_level}` |"
            )
        md.append("")

        # Tasks
        md.append("---")
        md.append("## ✅ Action Items & Tasks")
        md.append("| ID | Task Description | Owner | Status | Deadline | Priority | Dependencies |")
        md.append("|---|---|---|:---:|---|:---:|---|")
        for t in plan.tasks:
            owner_display = f"⚠️ **{t.owner}**" if t.owner_status != "Assigned" else f"**{t.owner}**"
            deadline_display = f"`{t.deadline}`" if t.deadline else "*None specified*"
            deps = ", ".join(t.dependencies) if t.dependencies else "*None*"
            md.append(
                f"| **{t.id}** | {t.title}: {t.description} | {owner_display} | `{t.status}` | {deadline_display} | `{t.priority}` | {deps} |"
            )
        md.append("")

        # Unresolved Questions
        if plan.unresolved_questions:
            md.append("---")
            md.append("## ❓ Unresolved Questions & Blockers")
            for q in plan.unresolved_questions:
                blk = "⛔ **BLOCKER**" if q.blocking else "ℹ️ **Advisory**"
                md.append(f"- **[{q.id}] {q.question}** ({blk} | Urgency: `{q.urgency}`)")
                md.append(f"  - *Raised by:* {q.raised_by} | *Required Parties:* {q.relevant_stakeholders}")
            md.append("")

        # Follow-Ups
        if plan.follow_ups:
            md.append("---")
            md.append("## 🔄 Scheduled Follow-Ups")
            for f in plan.follow_ups:
                target = f" (Target: `{f.target_date}`)" if f.target_date else ""
                notes = f" — *{f.notes}*" if f.notes else ""
                md.append(f"- **[{f.id}]** **{f.owner}**: {f.item}{target}{notes}")
            md.append("")

        return "\n".join(md)
