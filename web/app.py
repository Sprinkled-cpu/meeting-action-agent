"""
Production Streamlit Web Dashboard for AI Meeting-to-Action Agent.
"""

import os
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import streamlit as st
import json
from meeting_action_agent.core.pipeline import MeetingToActionPipeline

st.set_page_config(
    page_title="AI Meeting-to-Action Agent | Enterprise Intelligence",
    page_icon="📋",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling
st.markdown("""
<style>
    .metric-card {
        background-color: #1E232F;
        border-radius: 8px;
        padding: 16px;
        border: 1px solid #2B3245;
        text-align: center;
    }
    .badge-critical {
        background-color: #FF4D4F;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
    .badge-warning {
        background-color: #FA8C16;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 12px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar Configuration
with st.sidebar:
    st.title("⚙️ Engine Settings")
    provider = st.selectbox(
        "Inference Provider",
        ["mock (Deterministic Offline)", "openai (GPT-4o)", "gemini (2.0 Flash)"],
        index=0,
    )
    provider_name = provider.split()[0]
    
    st.divider()
    enable_audit = st.toggle("Contradiction & Ambiguity Audit", value=True)
    st.caption("Detects schedule clashes, unassigned work, and scope creep.")
    
    st.divider()
    st.subheader("Sample Presets")
    sample_choice = st.radio(
        "Load Transcript Preset:",
        ["Sprint 14 Launch Alignment (.txt)", "WebVTT Meeting Recording (.vtt)"],
    )
    
    samples_dir = Path(__file__).parent.parent / "samples"
    if sample_choice == "Sprint 14 Launch Alignment (.txt)":
        sample_path = samples_dir / "sample_sprint_meeting.txt"
    else:
        sample_path = samples_dir / "sample_meeting.vtt"

    default_text = ""
    if sample_path.exists():
        default_text = sample_path.read_text(encoding="utf-8")


# Main Dashboard Header
st.title("📋 AI Meeting-to-Action Agent")
st.markdown(
    "Enterprise discourse analysis engine for turning unstructured conversation into **validated decisions, tasks, deadlines, and alignment audits**."
)

col_input, col_upload = st.columns([3, 1])

with col_upload:
    st.subheader("Transcript Upload")
    uploaded_file = st.file_uploader("Upload .txt, .vtt, .srt", type=["txt", "vtt", "srt"])
    if uploaded_file:
        default_text = uploaded_file.read().decode("utf-8", errors="replace")

with col_input:
    transcript_text = st.text_area(
        "Meeting Transcript Editor",
        value=default_text,
        height=220,
        placeholder="Paste your meeting transcript here...",
    )

analyze_btn = st.button("🚀 Analyze Transcript & Audit Alignment", type="primary", use_container_width=True)

if analyze_btn or "last_plan" in st.session_state:
    if analyze_btn:
        with st.spinner("Processing transcript discourse, commitments, and conflict signals..."):
            pipeline = MeetingToActionPipeline(
                provider_name=provider_name,
                enable_audit=enable_audit,
            )
            plan, doc, duration_ms = pipeline.process(transcript_text)
            st.session_state["last_plan"] = plan
            st.session_state["last_doc"] = doc
            st.session_state["last_duration"] = duration_ms

    plan = st.session_state["last_plan"]
    doc = st.session_state["last_doc"]
    duration_ms = st.session_state["last_duration"]

    st.divider()

    # KPI Summary Row
    k1, k2, k3, k4, k5 = st.columns(5)
    with k1:
        st.metric("Meeting Health Score", f"{plan.metrics.alignment_score}/100")
    with k2:
        st.metric("Agreed Decisions", len(plan.decisions))
    with k3:
        st.metric("Action Items", f"{plan.metrics.assigned_tasks}/{len(plan.tasks)} assigned")
    with k4:
        st.metric("Open Inquiries", len(plan.unresolved_questions), f"{plan.metrics.blocking_questions} blocking")
    with k5:
        st.metric("Detected Inconsistencies", len(plan.contradictions_and_ambiguities))

    # Main Tabs
    tab_audit, tab_tasks, tab_decisions, tab_summary, tab_exports = st.tabs([
        "🚨 Inconsistency & Alignment Audit",
        "✅ Action Items & Tasks",
        "🏛️ Decisions & Questions",
        "📄 Executive Summary",
        "💾 Structured Data Exports",
    ])

    with tab_audit:
        st.subheader("🚨 Alignment & Contradiction Audit (Bonus Feature)")
        if not plan.contradictions_and_ambiguities:
            st.success("🎉 No contradictions, unassigned tasks, or scope creep detected in this meeting!")
        else:
            for idx, issue in enumerate(plan.contradictions_and_ambiguities, start=1):
                badge_type = (
                    "🔴 [CRITICAL BLOCKER]"
                    if "Critical" in issue.severity
                    else ("🟠 [HIGH RISK]" if "High" in issue.severity else "🟡 [AMBIGUITY]")
                )
                with st.expander(f"{badge_type} {issue.summary}", expanded=True):
                    st.markdown(f"**Category:** `{issue.category}` | **Severity:** `{issue.severity}`")
                    st.write(issue.issue_description)
                    if issue.conflicting_statements:
                        st.markdown("**Transcript Evidence:**")
                        for stmt in issue.conflicting_statements:
                            st.info(f"**{stmt.speaker}** ({stmt.timestamp or 'N/A'}): *\"{stmt.statement}\"*\n\n↳ **Assertion:** {stmt.assertion}")
                    st.success(f"**💡 Recommended Remediation:** {issue.recommended_action}")

    with tab_tasks:
        st.subheader("Assigned Deliverables & Action Items")
        task_rows = []
        for t in plan.tasks:
            task_rows.append({
                "ID": t.id,
                "Task Title": t.title,
                "Owner": f"⚠️ {t.owner}" if t.owner_status != "Assigned" else t.owner,
                "Status": t.status,
                "Deadline": t.deadline or "None specified",
                "Priority": t.priority,
                "Dependencies": ", ".join(t.dependencies) if t.dependencies else "None",
            })
        st.dataframe(task_rows, use_container_width=True)

        st.subheader("Scheduled Follow-ups")
        for f in plan.follow_ups:
            st.markdown(f"- **{f.owner}**: {f.item} *(Target: `{f.target_date}`) — {f.notes or ''}*")

    with tab_decisions:
        st.subheader("Strategic Decisions Agreed")
        for d in plan.decisions:
            st.markdown(f"### `{d.id}` {d.decision}")
            st.markdown(f"- **Decided By:** {d.decided_by} | **Milestone:** `{d.effective_milestone}` | **Impact:** `{d.impact_level}`")
            st.caption(f"Context: {d.context}")

        st.divider()
        st.subheader("Unresolved Questions & Blockers")
        for q in plan.unresolved_questions:
            blocker_tag = "⛔ **BLOCKER**" if q.blocking else "ℹ️ **Advisory**"
            st.markdown(f"- {blocker_tag} **{q.question}** *(Urgency: `{q.urgency}`)*")
            st.caption(f"Raised by: {q.raised_by} | Required Parties: {q.relevant_stakeholders}")

    with tab_summary:
        pipeline = MeetingToActionPipeline(provider_name=provider_name)
        st.markdown(pipeline.export_markdown(plan))

    with tab_exports:
        pipeline = MeetingToActionPipeline(provider_name=provider_name)
        json_str = pipeline.export_json(plan)
        csv_str = pipeline.export_jira_csv(plan)
        md_str = pipeline.export_markdown(plan)

        st.subheader("Direct File Downloads")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.download_button(
                "📥 Download Structured JSON",
                data=json_str,
                file_name="action_plan.json",
                mime="application/json",
            )
        with d2:
            st.download_button(
                "📥 Download JIRA CSV",
                data=csv_str,
                file_name="jira_tasks.csv",
                mime="text/csv",
            )
        with d3:
            st.download_button(
                "📥 Download Executive Markdown",
                data=md_str,
                file_name="executive_summary.md",
                mime="text/markdown",
            )

        st.divider()
        st.subheader("Raw JSON Contract")
        st.json(json.loads(json_str))
