"""
Streamlit Web UI for AI Meeting-to-Action Agent
"""

import streamlit as st
import json
from agent import MeetingToActionAgent

st.set_page_config(page_title="AI Meeting-to-Action Agent", page_icon="📋", layout="wide")

st.title("📋 AI Meeting-to-Action Agent")
st.caption("Discourse Analysis, Decision Extraction, Action Item Tracking & Alignment Auditing")

agent = MeetingToActionAgent()

# Default sample transcript loader
def load_sample():
    with open("transcript.txt", "r", encoding="utf-8") as f:
        return f.read()

col_input, col_info = st.columns([3, 1])

with col_info:
    st.subheader("Capabilities")
    st.markdown("""
    - **Decisions & Rationale**
    - **Action Items & Deadlines**
    - **Ownership & Dependencies**
    - **Unresolved Inquiries**
    - **Scheduled Follow-ups**
    - **Bonus:** 🚨 **Contradiction & Ambiguity Detector**
    """)
    if st.button("Reset to Default Sample"):
        st.session_state["transcript_input"] = load_sample()

if "transcript_input" not in st.session_state:
    st.session_state["transcript_input"] = load_sample()

with col_input:
    transcript_text = st.text_area(
        "Meeting Transcript",
        value=st.session_state["transcript_input"],
        height=260,
    )

if st.button("🚀 Analyze Transcript & Generate Action Plan", type="primary"):
    with st.spinner("Analyzing transcript discourse, commitments, and inconsistencies..."):
        plan = agent.analyze_transcript(transcript_text)
        
        tab_summary, tab_audit, tab_tasks, tab_decisions, tab_json = st.tabs([
            "Executive Summary",
            "🚨 Inconsistencies & Ambiguities",
            "✅ Action Items & Follow-ups",
            "🏛️ Decisions & Questions",
            "💾 Structured JSON",
        ])

        with tab_summary:
            st.markdown(agent.generate_human_readable_summary(plan))

        with tab_audit:
            st.subheader("🚨 Detected Contradictions & Ambiguities")
            for item in plan.contradictions_and_ambiguities:
                severity_color = "red" if "Critical" in item.severity else ("orange" if "High" in item.severity else "blue")
                with st.expander(f"[{item.severity}] {item.summary}", expanded=True):
                    st.markdown(f"**Category:** `{item.category}`")
                    st.write(item.issue_description)
                    st.markdown("**Transcript Evidence:**")
                    for stmt in item.conflicting_statements:
                        st.info(f"**{stmt.speaker}** ({stmt.timestamp}): *\"{stmt.statement}\"*\n\n↳ **Assertion:** {stmt.assertion}")
                    st.success(f"**Recommended Resolution:** {item.recommended_action}")

        with tab_tasks:
            st.subheader("Action Items")
            task_data = []
            for t in plan.tasks:
                task_data.append({
                    "ID": t.id,
                    "Title": t.title,
                    "Owner": t.owner,
                    "Deadline": t.deadline or "N/A",
                    "Priority": t.priority,
                    "Status": t.status,
                    "Dependencies": ", ".join(t.dependencies) or "None",
                })
            st.dataframe(task_data, use_container_width=True)

            st.subheader("Follow-ups")
            for f in plan.follow_ups:
                st.write(f"- **{f.owner}**: {f.item} *(Target: {f.target_date})*")

        with tab_decisions:
            st.subheader("Agreed Decisions")
            for d in plan.decisions:
                st.markdown(f"- **{d.id}**: **{d.decision}** *(By: {d.decided_by} | Milestone: `{d.effective_milestone}`) - Impact: `{d.impact_level}`*")
                st.caption(f"Context: {d.context}")

            st.divider()
            st.subheader("Unresolved Questions")
            for q in plan.unresolved_questions:
                blocker = "⛔ [BLOCKER]" if q.blocking else "ℹ️ [Advisory]"
                st.markdown(f"- {blocker} **{q.question}**")
                st.caption(f"Raised by: {q.raised_by} | Required Stakeholders: {q.relevant_stakeholders} | Urgency: {q.urgency}")

        with tab_json:
            st.json(json.loads(agent.to_structured_json(plan)))
