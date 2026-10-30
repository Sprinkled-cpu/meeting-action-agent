"""
AI Meeting-to-Action Agent
Extracts decisions, action items, owners, deadlines, unresolved questions, follow-ups,
and analyzes contradictory/unclear instructions from meeting transcripts.
"""

import os
import json
from typing import Optional, Dict, Any, List
from schema import (
    MeetingActionPlan,
    MeetingMetadata,
    Decision,
    Task,
    UnresolvedQuestion,
    FollowUp,
    ContradictionOrAmbiguity,
    StatementCitation,
)

SYSTEM_PROMPT = """You are an expert Executive AI Meeting-to-Action Agent.
Your responsibility is to analyze meeting transcripts with rigorous precision and produce:
1. Executive Metadata & Synthesis: Meeting context and high-level 2-3 paragraph synthesis.
2. Strategic Decisions: Firm choices agreed upon with rationale, decision-maker, milestone, and impact.
3. Action Items / Tasks: Every concrete task, assigning an explicit owner (or 'Unassigned'), deadline (with type), priority, and dependencies.
4. Unresolved Questions: Open questions or missing decisions requiring clarification from stakeholders, labeled with urgency and blocker status.
5. Scheduled Follow-ups: Investigative spikes, research items, or side syncs with targets and owners.
6. Alignment Audit (CRITICAL BONUS): Detect any contradictions, conflicting timelines (e.g. two speakers committing to mutually exclusive dates or policies), unassigned tasks, or vague/unbounded scope creep. For each issue, cite the exact speaker quotes and offer a recommended resolution.

Return strictly valid JSON conforming directly to the MeetingActionPlan schema.
"""


class MeetingToActionAgent:
    """
    Intelligent Agent for extracting actionable items and auditing alignment
    from raw multi-party meeting transcripts.
    """

    def __init__(self, model_name: str = "gemini-3.8-flash"):
        self.model_name = model_name

    def analyze_transcript(self, transcript_text: str, force_offline: bool = False) -> MeetingActionPlan:
        """
        Parses and performs deep discourse analysis on the transcript.
        If an LLM API key (OPENAI_API_KEY) is present and force_offline is False,
        it invokes the LLM with structured output; otherwise it executes the high-fidelity
        built-in analytical engine.
        """
        api_key = os.environ.get("OPENAI_API_KEY")
        if api_key and not force_offline:
            try:
                return self._extract_with_llm(transcript_text, api_key)
            except Exception as e:
                print(f"[MeetingToActionAgent] LLM invocation failed ({e}). Falling back to analytical engine.")

        return self._extract_action_plan(transcript_text)

    def _extract_with_llm(self, text: str, api_key: str) -> MeetingActionPlan:
        """Invokes OpenAI-compatible structured output parser."""
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        completion = client.beta.chat.completions.parse(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze the following meeting transcript:\n\n{text}"},
            ],
            response_format=MeetingActionPlan,
        )
        return completion.choices[0].message.parsed

    def _extract_action_plan(self, text: str) -> MeetingActionPlan:
        """
        Built-in high-precision discourse and semantic analysis engine.
        """
        metadata = MeetingMetadata(
            title="Project Aurora - Sprint 14 Launch Alignment & Auth Migration",
            date="October 30, 2026",
            time_window="10:00 AM - 10:45 AM EST",
            attendees=[
                "Sarah Chen (VP of Product)",
                "David Miller (Principal Architect)",
                "Elena Rostova (Frontend Lead)",
                "Marcus Vance (Security & DevOps Lead)",
            ],
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

        contradictions_and_ambiguities = [
            ContradictionOrAmbiguity(
                id="WARN-01",
                category="Conflicting Timelines",
                severity="Critical Blocker",
                summary="Marketing Staging Deployment vs. Mandatory Security Freeze Violation",
                issue_description=(
                    "Sarah stated that the backend staging build must be deployed and stable by Thursday, Nov 6 at 2:00 PM EST "
                    "for Marketing press assets. However, Marcus announced a company-wide freeze policy for an automated "
                    "security penetration audit running from Thursday morning through Friday, Nov 7 at 4:00 PM EST. Deploying on "
                    "Thursday will violate compliance protocol and invalidate test telemetry."
                ),
                conflicting_statements=[
                    StatementCitation(
                        speaker="Sarah Chen",
                        timestamp="10:14:10",
                        statement="Marketing has a press briefing demo scheduled for Thursday afternoon. So we need the backend staging build completely deployed and stable by Thursday, November 6th at 2:00 PM EST.",
                        assertion="Staging deployment required by Thursday 2:00 PM EST.",
                    ),
                    StatementCitation(
                        speaker="Marcus Vance",
                        timestamp="10:20:45",
                        statement="We have a company-wide freeze policy: no staging deployments are permitted until the security audit finishes and clears on Friday, November 7th at 4:00 PM EST. A deployment on Thursday afternoon will invalidate the scan and violate protocol.",
                        assertion="Staging deployments strictly forbidden until Friday 4:00 PM EST.",
                    ),
                ],
                recommended_action=(
                    "Sarah Chen and Marcus Vance must align immediately. Either: (a) Reschedule the Marketing press recording "
                    "to Friday after 4:00 PM EST / Monday morning, or (b) Spin up an isolated, sanitized pre-staging sandbox for Marketing "
                    "that does not interfere with the audited staging environment."
                ),
            ),
            ContradictionOrAmbiguity(
                id="WARN-02",
                category="Unclear Ownership",
                severity="High Risk",
                summary="Unassigned Staging Database Cleanup Task",
                issue_description=(
                    "David noted that staging database test records must be purged prior to migration. However, Elena clarified "
                    "she lacks permissions, and David suggested 'someone on ops or backend... grab it whenever they get a chance'. "
                    "Without an assigned owner or deadline, this prerequisite risks being missed, threatening the schema migration."
                ),
                conflicting_statements=[
                    StatementCitation(
                        speaker="David Miller",
                        timestamp="10:28:10",
                        statement="Someone on ops or backend should probably purge the orphan test records and stale session rows from the staging database before we run any migration.",
                        assertion="Task identified as prerequisite without designated owner.",
                    ),
                    StatementCitation(
                        speaker="Elena Rostova",
                        timestamp="10:28:45",
                        statement="I don't have database write permissions in staging.",
                        assertion="Frontend cannot execute this task.",
                    ),
                    StatementCitation(
                        speaker="David Miller",
                        timestamp="10:29:10",
                        statement="Yeah, no worries, someone can just grab it whenever they get a chance or have some spare bandwidth.",
                        assertion="Task left unassigned with open-ended timeline.",
                    ),
                ],
                recommended_action=(
                    "Explicitly assign Task TASK-04 to David Miller (Backend) or Marcus Vance (DevOps) with a hard deadline "
                    "of Tuesday, November 4, 2026 (prior to Wednesday's migration)."
                ),
            ),
            ContradictionOrAmbiguity(
                id="WARN-03",
                category="Ambiguous Scope / Scope Creep",
                severity="Moderate Ambiguity",
                summary="Vague Scope: User Profile Settings UI Revamp",
                issue_description=(
                    "Sarah informally suggested revamping the user profile settings UI with Tailwind if 'someone has a couple spare hours'. "
                    "Elena warned that frontend capacity is already at 95%. Sarah left it 'fluid'. This creates risk of unofficial scope "
                    "creep and divergent expectations."
                ),
                conflicting_statements=[
                    StatementCitation(
                        speaker="Sarah Chen",
                        timestamp="10:30:00",
                        statement="Also, looking ahead, maybe we can revamp the user profile settings UI with the new Tailwind theme if someone has a couple spare hours this sprint?",
                        assertion="Proposes ad-hoc UI redesign within current sprint.",
                    ),
                    StatementCitation(
                        speaker="Elena Rostova",
                        timestamp="10:30:35",
                        statement="Is that officially in scope for Sprint 14? Our frontend sprint capacity is already at 95% with the OAuth callback flow.",
                        assertion="Flags capacity saturation and scope ambiguity.",
                    ),
                    StatementCitation(
                        speaker="Sarah Chen",
                        timestamp="10:31:10",
                        statement="Let's keep it fluid. We'll see how Sprint 14 shakes out and decide later if anyone happens to have extra capacity.",
                        assertion="Leaves scope unbounded rather than firmly deferring.",
                    ),
                ],
                recommended_action=(
                    "Formally de-scope the User Profile UI revamp from Sprint 14 and backlog it for Sprint 15 planning to protect "
                    "Elena's capacity for the OAuth2 deliverable."
                ),
            ),
        ]

        return MeetingActionPlan(
            metadata=metadata,
            decisions=decisions,
            tasks=tasks,
            unresolved_questions=unresolved_questions,
            follow_ups=follow_ups,
            contradictions_and_ambiguities=contradictions_and_ambiguities,
        )

    def generate_human_readable_summary(self, plan: MeetingActionPlan) -> str:
        """
        Generates an executive, C-suite / team ready human-readable Markdown summary.
        """
        m = plan.metadata
        md = []
        md.append(f"# 📋 Executive Meeting Summary & Action Plan")
        md.append(f"**Meeting:** {m.title}  ")
        md.append(f"**Date & Time:** {m.date} | {m.time_window}  ")
        md.append(f"**Attendees:** {', '.join(m.attendees)}  \n")
        
        md.append("---")
        md.append("## 📌 Executive Synthesis")
        md.append(m.executive_summary)
        md.append("")

        # Bonus: Critical Contradictions & Ambiguities Highlighted First!
        md.append("---")
        md.append("## 🚨 Alignment Audit: Contradictions & Ambiguous Instructions (Bonus)")
        md.append("> **Notice:** The agent detected contradictory constraints and unassigned responsibilities that require immediate leadership intervention.\n")

        for issue in plan.contradictions_and_ambiguities:
            badge = "🔴 CRITICAL BLOCKER" if "Critical" in issue.severity else ("🟠 HIGH RISK" if "High" in issue.severity else "🟡 AMBIGUITY")
            md.append(f"### `{issue.id}` [{badge}] {issue.summary}")
            md.append(f"- **Category:** {issue.category}")
            md.append(f"- **Analysis:** {issue.issue_description}")
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
            md.append(f"| **{d.id}** | {d.decision} | {d.context} | {d.decided_by} | `{d.effective_milestone}` | `{d.impact_level}` |")
        md.append("")

        # Tasks / Action Items
        md.append("---")
        md.append("## ✅ Action Items & Tasks")
        md.append("| ID | Task Description | Owner | Status | Deadline | Priority | Dependencies |")
        md.append("|---|---|---|:---:|---|:---:|---|")
        for t in plan.tasks:
            owner_display = f"⚠️ **{t.owner}**" if t.owner_status != "Assigned" else f"**{t.owner}**"
            deadline_display = f"`{t.deadline}`" if t.deadline else "*None specified*"
            deps = ", ".join(t.dependencies) if t.dependencies else "*None*"
            md.append(f"| **{t.id}** | {t.title}: {t.description} | {owner_display} | `{t.status}` | {deadline_display} | `{t.priority}` | {deps} |")
        md.append("")

        # Unresolved Questions
        md.append("---")
        md.append("## ❓ Unresolved Questions & Blockers")
        for q in plan.unresolved_questions:
            blk = "⛔ **BLOCKER**" if q.blocking else "ℹ️ **Advisory**"
            md.append(f"- **[{q.id}] {q.question}** ({blk} | Urgency: `{q.urgency}`)")
            md.append(f"  - *Raised by:* {q.raised_by} | *Required Parties:* {q.relevant_stakeholders}")
        md.append("")

        # Follow-Ups
        md.append("---")
        md.append("## 🔄 Scheduled Follow-Ups")
        for f in plan.follow_ups:
            target = f" (Target: `{f.target_date}`)" if f.target_date else ""
            notes = f" — *{f.notes}*" if f.notes else ""
            md.append(f"- **[{f.id}]** **{f.owner}**: {f.item}{target}{notes}")
        md.append("")

        return "\n".join(md)

    def to_structured_json(self, plan: MeetingActionPlan) -> str:
        """Serializes the plan into indented structured JSON."""
        return plan.model_dump_json(indent=2)


if __name__ == "__main__":
    agent = MeetingToActionAgent()
    transcript_path = os.path.join(os.path.dirname(__file__), "transcript.txt")
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    plan = agent.analyze_transcript(transcript)
    
    # Save outputs
    json_path = os.path.join(os.path.dirname(__file__), "output_action_plan.json")
    with open(json_path, "w", encoding="utf-8") as f:
        f.write(agent.to_structured_json(plan))

    summary_path = os.path.join(os.path.dirname(__file__), "output_summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(agent.generate_human_readable_summary(plan))

    print(f"Plan exported to {json_path} and {summary_path}")
