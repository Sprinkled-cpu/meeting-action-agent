"""
Parser for SubRip (.srt) caption files.
"""

import re
from typing import List
from meeting_action_agent.parsers.base import BaseTranscriptParser
from meeting_action_agent.models.core import TranscriptDocument, DialogueTurn


class SRTTranscriptParser(BaseTranscriptParser):
    """
    Parses SubRip (.srt) transcript subtitle blocks.
    Example:
      1
      00:00:10,500 --> 00:00:13,200
      David Miller: We need to deliver the schema migration.
    """

    TIME_CUE_RE = re.compile(
        r"^(?P<start>\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2},\d{3})"
    )
    SPEAKER_COLON_RE = re.compile(r"^(?P<speaker>[A-Za-z\s]+):\s*(?P<text>.*)$")

    def parse(self, text: str) -> TranscriptDocument:
        turns: List[DialogueTurn] = []
        speakers_set = set()
        index = 1

        blocks = re.split(r"\n\s*\n", text.strip())
        for block in blocks:
            lines = [l.strip() for l in block.splitlines() if l.strip()]
            if len(lines) < 2:
                continue

            time_line = ""
            text_lines = []
            for line in lines:
                if self.TIME_CUE_RE.match(line):
                    time_line = line
                elif not line.isdigit():
                    text_lines.append(line)

            if time_line and text_lines:
                start_time = self.TIME_CUE_RE.match(time_line).group("start")
                combined_text = " ".join(text_lines)
                speaker = "Speaker"
                utterance = combined_text

                s_match = self.SPEAKER_COLON_RE.match(combined_text)
                if s_match:
                    speaker = s_match.group("speaker").strip()
                    utterance = s_match.group("text").strip()

                turns.append(
                    DialogueTurn(
                        index=index,
                        speaker=speaker,
                        timestamp=start_time,
                        text=utterance,
                        detected_intent="question" if "?" in utterance else "statement",
                    )
                )
                speakers_set.add(speaker)
                index += 1

        return TranscriptDocument(
            format="srt",
            raw_text=text,
            turns=turns,
            speakers=sorted(list(speakers_set)),
        )
