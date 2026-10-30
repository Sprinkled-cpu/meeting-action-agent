"""
Production Command Line Interface for Meeting-to-Action Agent.
Usage:
  meeting-action -i transcript.txt -m summary.md -j plan.json
"""

import sys
import argparse
from pathlib import Path

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

from meeting_action_agent.core.pipeline import MeetingToActionPipeline
from meeting_action_agent.logging_config import setup_logging


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meeting-action",
        description="Extract decisions, tasks, questions, follow-ups, and audit alignment from meeting transcripts.",
    )
    parser.add_argument(
        "-i", "--input",
        type=str,
        required=True,
        help="Path to raw transcript file (.txt, .vtt, .srt)",
    )
    parser.add_argument(
        "-j", "--output-json",
        type=str,
        default=None,
        help="Optional path to write structured JSON output",
    )
    parser.add_argument(
        "-m", "--output-md",
        type=str,
        default=None,
        help="Optional path to write executive Markdown report",
    )
    parser.add_argument(
        "-c", "--output-jira",
        type=str,
        default=None,
        help="Optional path to write JIRA-compatible tasks CSV",
    )
    parser.add_argument(
        "-p", "--provider",
        type=str,
        default=None,
        choices=["mock", "openai", "gemini"],
        help="Inference provider to employ (default: settings value)",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Optional title override for the meeting",
    )
    parser.add_argument(
        "--no-audit",
        action="store_true",
        help="Disable automated contradiction & ambiguity auditing",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable detailed diagnostic logging",
    )
    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    setup_logging(level="DEBUG" if args.verbose else "INFO")

    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Transcript file not found at '{args.input}'", file=sys.stderr)
        sys.exit(1)

    raw_text = input_path.read_text(encoding="utf-8", errors="replace")

    pipeline = MeetingToActionPipeline(
        provider_name=args.provider,
        enable_audit=not args.no_audit,
    )

    plan, doc, execution_ms = pipeline.process(
        raw_text=raw_text,
        format_hint="auto",
        meeting_title_override=args.title,
    )

    # Console Summary Banner
    print("\n" + "=" * 65)
    print("  [AI MEETING-TO-ACTION AGENT: ANALYSIS COMPLETE]")
    print("=" * 65)
    print(f"Meeting:         {plan.metadata.title}")
    print(f"Duration:        {plan.metadata.time_window}")
    print(f"Parsed Turns:    {len(doc.turns)} across {len(doc.speakers)} speakers")
    print(f"Alignment Score: {plan.metrics.alignment_score}/100")
    print(f"Execution Time:  {execution_ms} ms")
    print("-" * 65)
    print(f"* Decisions:     {len(plan.decisions)}")
    print(f"* Action Items:  {len(plan.tasks)} ({plan.metrics.assigned_tasks} assigned, {plan.metrics.unassigned_tasks} unassigned)")
    print(f"* Questions:     {len(plan.unresolved_questions)} ({plan.metrics.blocking_questions} blockers)")
    print(f"* Follow-Ups:    {len(plan.follow_ups)}")
    print(f"* Discrepancies: {len(plan.contradictions_and_ambiguities)}")
    print("=" * 65 + "\n")

    if plan.contradictions_and_ambiguities:
        print("[!] CRITICAL CONFLICTS & AMBIGUITIES AUDIT:")
        for idx, issue in enumerate(plan.contradictions_and_ambiguities, start=1):
            print(f"  [{idx}] [{issue.severity}] {issue.summary}")
            print(f"      Issue:  {issue.issue_description}")
            print(f"      Action: {issue.recommended_action}\n")

    # File Exports
    if args.output_json:
        out_j = Path(args.output_json)
        out_j.parent.mkdir(parents=True, exist_ok=True)
        out_j.write_text(pipeline.export_json(plan), encoding="utf-8")
        print(f"[OK] JSON saved to: {out_j.resolve()}")

    if args.output_md:
        out_m = Path(args.output_md)
        out_m.parent.mkdir(parents=True, exist_ok=True)
        out_m.write_text(pipeline.export_markdown(plan), encoding="utf-8")
        print(f"[OK] Markdown report saved to: {out_m.resolve()}")

    if args.output_jira:
        out_c = Path(args.output_jira)
        out_c.parent.mkdir(parents=True, exist_ok=True)
        out_c.write_text(pipeline.export_jira_csv(plan), encoding="utf-8")
        print(f"[OK] JIRA CSV saved to: {out_c.resolve()}")


if __name__ == "__main__":
    main()
