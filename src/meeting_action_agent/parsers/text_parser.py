"""
Parser for standard timestamped and speaker-labeled plain text transcripts.
"""

import re
from typing import List, Tuple, Optional
from meeting_action_agent.parsers.base import BaseTranscriptParser
from meeting_action_agent.models.core import TranscriptDocument, DialogueTurn


class PlainTextTranscriptParser(BaseTranscriptParser):
    """
    Parses conversational transcripts formatted with bracketed or inline timestamps,
    e.g.:
      [10:00:15] Sarah Chen: Good morning team...
      Sarah Chen (10:00): Hello everyone...
      Marcus Vance: Next item...
    """

    # Matches [HH:MM:SS] Speaker: text or [HH:MM] Speaker: text
    TIMESTAMP_FIRST_RE = re.compile(
        r"^\[(?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)\]\s*(?P<speaker>[^:\n]+):\s*(?P<text>.*)$",
        re.IGNORECASE,
    )
    # Matches Speaker [HH:MM:SS]: text or Speaker (HH:MM): text
    SPEAKER_FIRST_RE = re.compile(
        r"^(?P<speaker>[^\[\(\:\n]+)\s*[\(\[](?P<timestamp>\d{1,2}:\d{2}(?::\d{2})?(?:\s*[AP]M)?)[\)\]]:\s*(?P<text>.*)$",
        re.IGNORECASE,
    )
    # Matches Speaker: text
    SIMPLE_SPEAKER_RE = re.compile(r"^(?P<speaker>[A-Z][a-zA-Z\s\.\-]{1,35}):\s*(?P<text>.*)$")

    def parse(self, text: str) -> TranscriptDocument:
        turns: List[DialogueTurn] = []
        speakers_set = set()
        index = 1

        lines = text.strip().splitlines()
        current_turn: Optional[DialogueTurn] = None

        for raw_line in lines:
            line = raw_line.strip()
            if not line:
                continue

            # Skip metadata bracket lines like [Meeting: ...] or [Date: ...]
            if line.startswith("[") and ":" in line and not self.TIMESTAMP_FIRST_RE.match(line):
                continue

            # Try matching timestamp-first format: [10:00:15] Sarah Chen: ...
            m1 = self.TIMESTAMP_FIRST_RE.match(line)
            if m1:
                speaker = m1.group("speaker").strip()
                timestamp = m1.group("timestamp").strip()
                utterance = m1.group("text").strip()
                current_turn = DialogueTurn(
                    index=index,
                    speaker=speaker,
                    timestamp=timestamp,
                    text=utterance,
                    detected_intent=self._infer_intent(utterance),
                )
                turns.append(current_turn)
                speakers_set.add(speaker)
                index += 1
                continue

            # Try speaker-first format: Sarah Chen [10:00:15]: ...
            m2 = self.SPEAKER_FIRST_RE.match(line)
            if m2:
                speaker = m2.group("speaker").strip()
                timestamp = m2.group("timestamp").strip()
                utterance = m2.group("text").strip()
                current_turn = DialogueTurn(
                    index=index,
                    speaker=speaker,
                    timestamp=timestamp,
                    text=utterance,
                    detected_intent=self._infer_intent(utterance),
                )
                turns.append(current_turn)
                speakers_set.add(speaker)
                index += 1
                continue

            # Try simple speaker format: Sarah Chen: ...
            m3 = self.SIMPLE_SPEAKER_RE.match(line)
            if m3 and not line.lower().startswith(("http", "note:", "warning:")):
                speaker = m3.group("speaker").strip()
                utterance = m3.group("text").strip()
                current_turn = DialogueTurn(
                    index=index,
                    speaker=speaker,
                    timestamp=None,
                    text=utterance,
                    detected_intent=self._infer_intent(utterance),
                )
                turns.append(current_turn)
                speakers_set.add(speaker)
                index += 1
                continue

            # Multi-line utterance continuation
            if current_turn:
                current_turn.text += f" {line}"
            else:
                # Fallback turn if text begins without explicit speaker
                current_turn = DialogueTurn(
                    index=index,
                    speaker="Speaker",
                    timestamp=None,
                    text=line,
                    detected_intent=self._infer_intent(line),
                )
                turns.append(current_turn)
                speakers_set.add("Speaker")
                index += 1

        return TranscriptDocument(
            format="plaintext",
            raw_text=text,
            turns=turns,
            speakers=sorted(list(speakers_set)),
        )

    def _infer_intent(self, text: str) -> str:
        """Heuristic intent tagger for discourse turns."""
        lower = text.lower()
        if "?" in text:
            return "question"
        if any(w in lower for w in ["decision:", "we decided", "decision is", "agreed"]):
            return "decision"
        if any(w in lower for w in ["i will", "my commitment", "will deliver", "action item"]):
            return "commitment"
        if any(w in lower for w in ["wait a second", "disagree", "cannot", "policy", "freeze", "violate"]):
            return "objection_or_conflict"
        return "statement"
