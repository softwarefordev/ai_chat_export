import json
import tempfile
import unittest
from pathlib import Path

from ai_chat_export.ide import load_ide_conversation
from ai_chat_export.transcript import build_transcript


class IdeTranscriptTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_lines_become_one_agent_stretch_with_a_caption(self):
        folder = self.root / "agent-transcripts" / "room"
        folder.mkdir(parents=True)
        lines = [
            _user("River map"),
            _assistant([{"type": "text", "text": "First reply"}]),
            json.dumps({"type": "turn_ended", "status": "success"}),
            _assistant(
                [
                    {"type": "text", "text": "Second reply"},
                    {
                        "type": "tool_use",
                        "name": "Shell",
                        "input": {
                            "command": "secret-command-text",
                            "description": "List the map files",
                        },
                    },
                ]
            ),
            json.dumps({"type": "note", "text": "NOT-IN-BODY"}),
        ]
        (folder / "room.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        conversation, prompts = load_ide_conversation(folder)
        transcript = build_transcript(
            conversation.messages,
            prompts,
            show_tools=True,
            skipped=conversation.skipped,
        )
        agents = [block for block in transcript.blocks if block.kind == "agent"]
        self.assertEqual(len(agents), 1)
        self.assertIn("First reply", agents[0].text)
        self.assertIn("Second reply", agents[0].text)
        self.assertEqual(agents[0].captions, ["Ran List the map files"])
        self.assertNotIn("secret-command-text", agents[0].captions[0])
        body = "\n".join(block.text for block in transcript.blocks)
        self.assertNotIn("NOT-IN-BODY", body)
        self.assertNotIn("turn_ended", body)
        self.assertIn("Skipped unrecognized data line 5", transcript.footer)


def _user(query: str) -> str:
    return json.dumps(
        {
            "role": "user",
            "message": {
                "content": [{"type": "text", "text": f"<user_query>\n{query}\n</user_query>"}]
            },
        }
    )


def _assistant(content: list[dict]) -> str:
    return json.dumps({"role": "assistant", "message": {"content": content}})


if __name__ == "__main__":
    unittest.main()
