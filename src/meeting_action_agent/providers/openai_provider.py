"""
OpenAI LLM provider supporting structured output and Pydantic validation.
"""

import os
from meeting_action_agent.providers.base import BaseLLMProvider
from meeting_action_agent.models.core import TranscriptDocument, MeetingActionPlan
from meeting_action_agent.exceptions import LLMProviderError


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


class OpenAIProvider(BaseLLMProvider):
    """Integrates with OpenAI GPT-4o / GPT-4.5 with structured outputs."""

    def __init__(self, api_key: str, model_name: str = "gpt-4o"):
        self.api_key = api_key
        self.model_name = model_name

    def generate_plan(self, doc: TranscriptDocument) -> MeetingActionPlan:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            completion = client.beta.chat.completions.parse(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Analyze the following transcript:\n\n{doc.raw_text}"},
                ],
                response_format=MeetingActionPlan,
            )
            parsed = completion.choices[0].message.parsed
            if not parsed:
                raise LLMProviderError("Empty response returned from OpenAI structured completion.")
            return parsed
        except Exception as e:
            raise LLMProviderError(f"OpenAI completion failed: {str(e)}") from e
