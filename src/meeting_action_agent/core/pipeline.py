"""
Meeting-to-Action Core Processing Pipeline.
Orchestrates ingestion, parsing, LLM inference, discrepancy auditing, metrics, and multi-format exports.
"""

import time
from typing import Optional, Tuple
from meeting_action_agent.models.core import (
    TranscriptDocument,
    MeetingActionPlan,
)
from meeting_action_agent.parsers.factory import get_parser
from meeting_action_agent.providers.factory import get_llm_provider
from meeting_action_agent.auditors.engine import DiscourseAuditingEngine
from meeting_action_agent.exporters.markdown_exporter import MarkdownExporter
from meeting_action_agent.exporters.jira_exporter import JiraExporter
from meeting_action_agent.logging_config import logger


class MeetingToActionPipeline:
    """
    End-to-end production pipeline:
      Raw Transcript -> Parse & Normalize -> LLM Extraction ->
      Contradiction & Ambiguity Auditing -> Metric Computation -> Plan & Exports.
    """

    def __init__(
        self,
        provider_name: Optional[str] = None,
        enable_audit: bool = True,
    ):
        self.provider = get_llm_provider(provider_name)
        self.enable_audit = enable_audit
        self.auditing_engine = DiscourseAuditingEngine()
        self.markdown_exporter = MarkdownExporter()
        self.jira_exporter = JiraExporter()

    def process(
        self,
        raw_text: str,
        format_hint: str = "auto",
        meeting_title_override: Optional[str] = None,
    ) -> Tuple[MeetingActionPlan, TranscriptDocument, float]:
        """
        Executes the full pipeline and returns (MeetingActionPlan, TranscriptDocument, execution_time_ms).
        """
        start_time = time.perf_counter()
        logger.info(f"Starting pipeline execution on transcript ({len(raw_text)} chars)...")

        # 1. Parse raw transcript into structured turns
        parser = get_parser(format_hint, raw_text)
        doc: TranscriptDocument = parser.parse(raw_text)
        logger.info(f"Parsed {len(doc.turns)} turns across {len(doc.speakers)} speakers using {parser.__class__.__name__}.")

        # 2. Extract deliverables via Provider
        plan: MeetingActionPlan = self.provider.generate_plan(doc)

        if meeting_title_override:
            plan.metadata.title = meeting_title_override

        # 3. Discourse & Inconsistency Audit (Bonus)
        if self.enable_audit:
            logger.info("Executing discourse and contradiction auditing passes...")
            audited_issues = self.auditing_engine.run_audit(doc, plan)
            plan.contradictions_and_ambiguities = audited_issues

        # 4. Compute Health & Alignment Metrics
        plan.metrics = self.auditing_engine.calculate_metrics(plan)
        logger.info(f"Alignment audit complete: Score = {plan.metrics.alignment_score}/100.")

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
        logger.info(f"Pipeline finished successfully in {duration_ms}ms.")
        return plan, doc, duration_ms

    def export_markdown(self, plan: MeetingActionPlan) -> str:
        return self.markdown_exporter.export(plan)

    def export_json(self, plan: MeetingActionPlan) -> str:
        return plan.model_dump_json(indent=2)

    def export_jira_csv(self, plan: MeetingActionPlan) -> str:
        return self.jira_exporter.to_csv(plan)

    def export_jira_json(self, plan: MeetingActionPlan) -> list:
        return self.jira_exporter.to_json(plan)
