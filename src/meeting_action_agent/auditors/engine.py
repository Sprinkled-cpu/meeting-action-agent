"""
Auditing Engine that aggregates all specialized auditors and calculates alignment metrics.
"""

from typing import List
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
    ContradictionOrAmbiguity,
    AlignmentMetrics,
)
from meeting_action_agent.auditors.conflict_detector import TimelineConflictDetector
from meeting_action_agent.auditors.ownership_auditor import OwnershipAmbiguityAuditor
from meeting_action_agent.auditors.scope_creep_auditor import ScopeCreepAuditor


class DiscourseAuditingEngine:
    """
    Runs multi-pass auditing across dialogue turns and extracted deliverables.
    Calculates an objective Alignment & Clarity Score.
    """

    def __init__(self):
        self.auditors = [
            TimelineConflictDetector(),
            OwnershipAmbiguityAuditor(),
            ScopeCreepAuditor(),
        ]

    def run_audit(
        self, doc: TranscriptDocument, plan: MeetingActionPlan
    ) -> List[ContradictionOrAmbiguity]:
        detected_issues: List[ContradictionOrAmbiguity] = []
        for auditor in self.auditors:
            issues = auditor.audit(doc, plan)
            detected_issues.extend(issues)

        # Merge with any existing issues already in the plan without duplicates
        existing_summaries = {i.summary.lower() for i in plan.contradictions_and_ambiguities}
        merged_issues = list(plan.contradictions_and_ambiguities)
        for issue in detected_issues:
            if issue.summary.lower() not in existing_summaries:
                merged_issues.append(issue)
                existing_summaries.add(issue.summary.lower())

        return merged_issues

    def calculate_metrics(self, plan: MeetingActionPlan) -> AlignmentMetrics:
        """
        Calculates health metrics and an overall alignment score (0 - 100).
        Deductions:
          - Critical Blocker: -25 pts
          - High Risk / Unassigned Task: -15 pts
          - Moderate Ambiguity: -10 pts
          - Blocking Question: -10 pts
        """
        assigned = sum(1 for t in plan.tasks if t.owner_status == "Assigned")
        unassigned = len(plan.tasks) - assigned
        blocking_q = sum(1 for q in plan.unresolved_questions if q.blocking)

        crit_count = sum(1 for i in plan.contradictions_and_ambiguities if "Critical" in i.severity)
        warn_count = len(plan.contradictions_and_ambiguities) - crit_count

        score = 100.0
        score -= crit_count * 25.0
        score -= unassigned * 15.0
        score -= blocking_q * 10.0
        score -= warn_count * 5.0
        score = max(0.0, min(100.0, score))

        return AlignmentMetrics(
            total_decisions=len(plan.decisions),
            total_tasks=len(plan.tasks),
            assigned_tasks=assigned,
            unassigned_tasks=unassigned,
            total_questions=len(plan.unresolved_questions),
            blocking_questions=blocking_q,
            critical_contradictions=crit_count,
            warnings=warn_count,
            alignment_score=round(score, 1),
        )
