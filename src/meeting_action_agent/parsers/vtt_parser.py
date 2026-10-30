"""
Parser for WebVTT (.vtt) meeting transcripts.
"""

import re
from typing import List
from meeting_action_agent.parsers.base import BaseTranscriptParser
from meeting_action_agent.models.core import TranscriptDocument, DialogueTurn


class WebVTTTranscriptParser(BaseTranscriptParser):
    """
    Parses standard WebVTT meeting captions, such as Zoom, Teams, or Meet exports.
    Example:
      00:01:05.120 --> 00:01:08.500
      <v Sarah Chen>Good morning team, let's start the meeting.</v>
    """

    TIME_CUE_RE = re.compile(
        r"^(?P<start>\d{2}:\d{2}:\d{2}\.\d{3})\s*-->\s*(?P<end>\d{2}:\d{2}:\d{2}\.\d{3})"
    )
    VOICE_TAG_RE = re.compile(r"<v\s+(?P<speaker>[^>]+)>(?P<text>.*?)((?:</v>)|$)", re.IGNORECASE)
    SPEAKER_COLON_RE = re.compile(r"^(?P<speaker>[A-Za-z\s]+):\s*(?P<text>.*)$")

    def parse(self, text: str) -> TranscriptDocument:
        turns: List[DialogueTurn] = []
        speakers_set = set()
        index = 1

        lines = text.strip().splitlines()
        current_time: str = ""

        i = 0
        while i < len(lines):
            line = lines[i].strip()
            if not line or line.startswith("WEBVTT") or line.startswith("NOTE"):
                i += 1
                continue

            time_match = self.TIME_CUE_RE.match(line)
            if time_match:
                current_time = time_match.group("start")
                i += 1
                if i < len(lines):
                    cue_text = lines[i].strip()
                    speaker = "Speaker"
                    text_content = cue_text

                    # Check for voice tag: <v Speaker>text
                    v_match = self.VOICE_TAG_RE.search(cue_text)
                    if v_match:
                        speaker = v_match.group("speaker").strip()
                        text_content = v_match.group("text").strip()
                    else:
                        # Check for Speaker: text
                        s_match = self.SPEAKER_COLON_RE.match(cue_text)
                        if s_match:
                            speaker = s_match.group("speaker").strip()
                            text_content = s_match.group("text").strip()

                    turn = DialogueTurn(
                        index=index,
                        speaker=speaker,
                        timestamp=current_time,
                        text=text_content,
                        detected_intent="question" if "?" in text_content else "statement",
                    )
                    turns.append(turn)
                    speakers_set.add(speaker)
                    index += 1
            i += 1

        return TranscriptDocument(
            format="vtt",
            raw_text=text,
            turns=turns,
            speakers=sorted(list(speakers_set)),
        )
