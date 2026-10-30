"""
Unit tests for transcript parsers.
"""

import unittest
from meeting_action_agent.parsers.text_parser import PlainTextTranscriptParser
from meeting_action_agent.parsers.vtt_parser import WebVTTTranscriptParser
from meeting_action_agent.parsers.srt_parser import SRTTranscriptParser
from meeting_action_agent.parsers.factory import get_parser


class TestTranscriptParsers(unittest.TestCase):

    def test_plaintext_parser(self):
        text = """
        [10:00:00] Alice: Welcome everyone.
        [10:00:15] Bob: Good morning Alice. Can we review the tasks?
        """
        parser = PlainTextTranscriptParser()
        doc = parser.parse(text)
        self.assertEqual(len(doc.turns), 2)
        self.assertEqual(doc.turns[0].speaker, "Alice")
        self.assertEqual(doc.turns[0].timestamp, "10:00:00")
        self.assertEqual(doc.turns[1].speaker, "Bob")
        self.assertEqual(doc.turns[1].detected_intent, "question")
        self.assertIn("Alice", doc.speakers)
        self.assertIn("Bob", doc.speakers)

    def test_vtt_parser(self):
        vtt_content = """WEBVTT

00:01:00.000 --> 00:01:05.000
<v Sarah Chen>Let's kick off Sprint 14.</v>

00:01:06.000 --> 00:01:10.000
<v David Miller>I am working on the schema migration.</v>
"""
        parser = WebVTTTranscriptParser()
        doc = parser.parse(vtt_content)
        self.assertEqual(len(doc.turns), 2)
        self.assertEqual(doc.turns[0].speaker, "Sarah Chen")
        self.assertEqual(doc.turns[1].speaker, "David Miller")

    def test_srt_parser(self):
        srt_content = """1
00:00:01,000 --> 00:00:04,000
Elena: The frontend is ready.

2
00:00:05,000 --> 00:00:08,000
Marcus: Security scan will begin Thursday.
"""
        parser = SRTTranscriptParser()
        doc = parser.parse(srt_content)
        self.assertEqual(len(doc.turns), 2)
        self.assertEqual(doc.turns[0].speaker, "Elena")
        self.assertEqual(doc.turns[1].speaker, "Marcus")

    def test_parser_factory_autodetection(self):
        vtt_sample = "WEBVTT\n00:00:01.000 --> 00:00:02.000\nHello"
        srt_sample = "1\n00:00:01,000 --> 00:00:02,000\nHello"
        txt_sample = "[10:00:00] Alice: Hello"

        self.assertIsInstance(get_parser("auto", vtt_sample), WebVTTTranscriptParser)
        self.assertIsInstance(get_parser("auto", srt_sample), SRTTranscriptParser)
        self.assertIsInstance(get_parser("auto", txt_sample), PlainTextTranscriptParser)


if __name__ == "__main__":
    unittest.main()
