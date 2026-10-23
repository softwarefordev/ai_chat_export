import tempfile
import unittest
from pathlib import Path

from ai_chat_export.store import load_conversation
from ai_chat_export.transcript import build_transcript, caption
from tests.support import PNG, sample_messages, write_db, write_protobuf_db


class StoreTests(unittest.TestCase):
    def test_messages_stay_in_order_without_checkpoint_duplicate(self):
        messages, _prompts = sample_messages()
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "store.db"
            write_db(db_path, messages, [], [b"not-json-blob"])
            conversation = load_conversation(db_path)
        self.assertEqual(
            [message["role"] for message in conversation.messages],
            ["system", "user", "assistant", "tool"],
        )
        self.assertEqual(len(conversation.skipped), 1)
        self.assertEqual(conversation.unlinked_images, [])

    def test_protobuf_checkpoints_precede_the_live_tail_once(self):
        early = {"role": "user", "content": "EARLY_TURN"}
        reply = {"role": "assistant", "content": "EARLY_REPLY"}
        mid = {"role": "user", "content": "MID_TURN"}
        late = {"role": "user", "content": "LATE_TURN"}
        summary = b"<summary>CHECKPOINT_SUMMARY_TEXT</summary>"
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "store.db"
            write_protobuf_db(
                db_path,
                checkpoints=[([early, reply], summary), ([early, mid], summary)],
                live=[late],
            )
            conversation = load_conversation(db_path)
        texts = [message["content"] for message in conversation.messages]
        self.assertEqual(texts, ["EARLY_TURN", "EARLY_REPLY", "MID_TURN", "LATE_TURN"])
        self.assertEqual(texts.count("EARLY_TURN"), 1)
        self.assertNotIn("CHECKPOINT_SUMMARY_TEXT", "\n".join(texts))

    def test_protobuf_footer_skips_checkpoints_and_side_blobs_only(self):
        early = {"role": "user", "content": "EARLY_TURN"}
        late = {"role": "user", "content": "LATE_TURN"}
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "store.db"
            ids = write_protobuf_db(
                db_path,
                checkpoints=[([early], b"<summary>CHECKPOINT_SUMMARY_TEXT</summary>")],
                live=[late],
                side_blobs=[(8, b"# Tasks\nfile body"), (3, b"\x0a\x05specs")],
                unknown_live=[b"mystery-bytes-not-a-turn"],
            )
            conversation = load_conversation(db_path)
        footer = "\n".join(conversation.skipped)
        self.assertNotIn(ids["checkpoint_ids"][0], footer)
        self.assertNotIn(ids["side_ids"][0], footer)
        self.assertNotIn(ids["side_ids"][1], footer)
        self.assertIn(ids["unknown_ids"][0], conversation.skipped)
        texts = [message["content"] for message in conversation.messages]
        self.assertEqual(texts, ["EARLY_TURN", "LATE_TURN"])


class TranscriptTests(unittest.TestCase):
    def test_query_portion_omits_markup_and_injected_context(self):
        query = "Please add a river tool."
        wrapped = (
            "<timestamp>Friday, Oct 23, 2026, 11:13 AM (UTC-7)</timestamp>\n"
            f"<user_query>\n{query}\n</user_query>"
        )
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "INJECTED_CONTEXT_BLOCK"},
                    {"type": "text", "text": wrapped},
                ],
            }
        ]
        transcript = build_transcript(messages, [query])
        you = next(block for block in transcript.blocks if block.kind == "you")
        visible = "\n".join(block.text for block in transcript.blocks)
        self.assertEqual(you.text, query)
        self.assertNotIn("<timestamp>", visible)
        self.assertNotIn("<user_query>", visible)
        self.assertNotIn("INJECTED_CONTEXT_BLOCK", visible)

    def test_plain_prompt_without_elements_is_the_query(self):
        query = "Please add a river tool."
        transcript = build_transcript(
            [{"role": "user", "content": query}],
            [query],
        )
        you = next(block for block in transcript.blocks if block.kind == "you")
        self.assertEqual(you.text, query)

    def test_summary_only_message_is_omitted(self):
        summary = "Earlier turns covered the exporter."
        messages = [
            {
                "role": "user",
                "content": f"<conversation_summary>\n{summary}\n</conversation_summary>",
            }
        ]
        transcript = build_transcript(messages, [])
        self.assertEqual(transcript.blocks, [])
        visible = "\n".join(block.text + block.detail for block in transcript.blocks)
        self.assertNotIn(summary, visible)

    def test_user_info_only_is_context_when_verbose(self):
        preamble = "<user_info>\nOS Version: win32\n</user_info>"
        messages = [{"role": "user", "content": preamble}]
        hidden = build_transcript(messages, [])
        self.assertFalse(any(block.kind == "you" for block in hidden.blocks))
        shown = build_transcript(messages, [], verbose=True)
        self.assertFalse(any(block.kind == "you" for block in shown.blocks))
        context = next(block for block in shown.blocks if block.kind == "context")
        self.assertIn("OS Version: win32", context.text)

    def test_default_transcript_filters_and_captions(self):
        messages, prompts = sample_messages()
        transcript = build_transcript(messages, prompts, verbose=False)
        visible = "\n".join(block.text for block in transcript.blocks)
        captions = [item for block in transcript.blocks for item in block.captions]
        self.assertIn("Please add a river tool.", visible)
        self.assertNotIn("INJECTED_CONTEXT_BLOCK", visible)
        self.assertNotIn("SYSTEM_PROMPT_TEXT", visible)
        self.assertNotIn("REASONING_PRIVATE", visible)
        self.assertNotIn("TOOL_RESULT_PAYLOAD", visible)
        self.assertEqual(captions, [])

    def test_default_omits_command_blocks_and_hidden_layers(self):
        query = "Please add a river tool."
        messages = [
            {"role": "system", "content": "SYSTEM_PROMPT_TEXT"},
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "INJECTED_CONTEXT_BLOCK\n<cursor_commands>\nopsx-propose\n</cursor_commands>",
                    },
                    {"type": "text", "text": f"<user_query>{query}</user_query>"},
                ],
            },
            {
                "role": "assistant",
                "content": [
                    {"type": "reasoning", "text": "REASONING_PRIVATE"},
                    {"type": "text", "text": "Visible answer."},
                    {
                        "type": "tool-call",
                        "toolName": "Shell",
                        "args": {"command": "SECRET_COMMAND_XYZ", "description": "List map tool modules"},
                    },
                ],
            },
            {
                "role": "tool",
                "content": [{"type": "tool-result", "toolName": "Shell", "result": "TOOL_RESULT_PAYLOAD"}],
            },
        ]
        transcript = build_transcript(messages, [query])
        visible = "\n".join(
            block.text + "\n" + block.detail + "\n" + "\n".join(block.captions)
            for block in transcript.blocks
        )
        piece_text = "\n".join(piece.text for block in transcript.blocks for piece in block.pieces)
        self.assertIn(query, visible)
        self.assertNotIn("opsx-propose", visible)
        self.assertNotIn("cursor_commands", visible)
        self.assertNotIn("SYSTEM_PROMPT_TEXT", visible)
        self.assertNotIn("REASONING_PRIVATE", visible + piece_text)
        self.assertNotIn("TOOL_RESULT_PAYLOAD", visible + piece_text)
        self.assertNotIn("Ran List map tool modules", visible + piece_text)
        self.assertEqual([block.kind for block in transcript.blocks], ["you", "agent"])

    def test_show_tools_captions_omit_command_and_result(self):
        messages, prompts = sample_messages()
        transcript = build_transcript(messages, prompts, show_tools=True)
        captions = [item for block in transcript.blocks for item in block.captions]
        visible = "\n".join(block.text for block in transcript.blocks)
        self.assertEqual(
            captions,
            ["Read tools/river.py", "Glob *.py", "Ran List map tool modules"],
        )
        self.assertNotIn("SECRET_COMMAND_XYZ", "\n".join(captions))
        self.assertNotIn("TOOL_RESULT_PAYLOAD", visible)
        self.assertNotIn("TOOL_RESULT_PAYLOAD", "\n".join(captions))

    def test_shell_without_description_hides_command(self):
        text = caption(
            {"toolName": "Shell", "args": {"command": "SECRET_COMMAND_XYZ"}}
        )
        self.assertEqual(text, "Ran command")
        self.assertNotIn("SECRET_COMMAND_XYZ", text)

    def test_detail_places_command_after_the_query(self):
        query = "Please add a river tool."
        command = "opsx-propose user turns"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"INJECTED_CONTEXT_BLOCK\n<cursor_commands>\n{command}\n</cursor_commands>",
                    },
                    {"type": "text", "text": f"<user_query>{query}</user_query>"},
                ],
            }
        ]
        transcript = build_transcript(messages, [query], show_detail=True)
        you = next(block for block in transcript.blocks if block.kind == "you")
        self.assertEqual(you.text, query)
        self.assertEqual(you.detail, command)
        self.assertNotIn("cursor_commands", you.detail)

    def test_detail_without_a_command_keeps_the_query_only(self):
        query = "Please add a river tool."
        messages = [{"role": "user", "content": f"<user_query>{query}</user_query>"}]
        transcript = build_transcript(messages, [query], show_detail=True)
        you = transcript.blocks[0]
        self.assertEqual(you.text, query)
        self.assertEqual(you.detail, "")

    def test_detail_and_verbose_show_the_command_once(self):
        query = "Please add a river tool."
        command = "opsx-propose user turns"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"INJECTED_CONTEXT_BLOCK\n<cursor_commands>\n{command}\n</cursor_commands>",
                    },
                    {"type": "text", "text": f"<user_query>{query}</user_query>"},
                ],
            }
        ]
        transcript = build_transcript(messages, [query], verbose=True, show_detail=True)
        you = next(block for block in transcript.blocks if block.kind == "you")
        context = next(block for block in transcript.blocks if block.kind == "context")
        self.assertEqual(you.detail, command)
        self.assertIn("INJECTED_CONTEXT_BLOCK", context.text)
        self.assertNotIn(command, context.text)
        self.assertNotIn(command, you.text)
        shown = you.text + "\n" + you.detail + "\n" + context.text
        self.assertEqual(shown.count(command), 1)

    def test_detail_places_summary_after_the_query(self):
        query = "Please add a river tool."
        summary = "Earlier turns covered the exporter."
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"<conversation_summary>\n{summary}\n</conversation_summary>",
                    },
                    {"type": "text", "text": f"<user_query>{query}</user_query>"},
                ],
            }
        ]
        transcript = build_transcript(messages, [query], show_detail=True)
        you = next(block for block in transcript.blocks if block.kind == "you")
        self.assertEqual(you.text, query)
        self.assertEqual(you.detail, summary)
        self.assertNotIn("conversation_summary", you.detail)

    def test_summary_only_appears_with_detail(self):
        summary = "Earlier turns covered the exporter."
        messages = [
            {
                "role": "user",
                "content": f"<conversation_summary>\n{summary}\n</conversation_summary>",
            }
        ]
        hidden = build_transcript(messages, [])
        self.assertEqual(hidden.blocks, [])
        shown = build_transcript(messages, [], show_detail=True)
        you = next(block for block in shown.blocks if block.kind == "you")
        self.assertEqual(you.text, "")
        self.assertEqual(you.detail, summary)

    def test_detail_and_verbose_show_summary_and_command_once(self):
        query = "Please add a river tool."
        summary = "Earlier turns covered the exporter."
        command = "opsx-propose user turns"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": (
                            "INJECTED_CONTEXT_BLOCK\n"
                            f"<conversation_summary>\n{summary}\n</conversation_summary>\n"
                            f"<cursor_commands>\n{command}\n</cursor_commands>"
                        ),
                    },
                    {"type": "text", "text": f"<user_query>{query}</user_query>"},
                ],
            }
        ]
        transcript = build_transcript(messages, [query], verbose=True, show_detail=True)
        you = next(block for block in transcript.blocks if block.kind == "you")
        context = next(block for block in transcript.blocks if block.kind == "context")
        self.assertEqual(you.text, query)
        self.assertEqual(you.detail, f"{summary}\n\n{command}")
        self.assertIn("INJECTED_CONTEXT_BLOCK", context.text)
        self.assertNotIn(summary, context.text)
        self.assertNotIn(command, context.text)
        shown = you.text + "\n" + you.detail + "\n" + context.text
        self.assertEqual(shown.count(summary), 1)
        self.assertEqual(shown.count(command), 1)

    def test_verbose_without_detail_keeps_the_command_off_the_you_turn(self):
        query = "Please add a river tool."
        command = "opsx-propose user turns"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"INJECTED_CONTEXT_BLOCK\n<cursor_commands>\n{command}\n</cursor_commands>",
                    },
                    {"type": "text", "text": f"<user_query>{query}</user_query>"},
                ],
            }
        ]
        transcript = build_transcript(messages, [query], verbose=True)
        you = next(block for block in transcript.blocks if block.kind == "you")
        context = next(block for block in transcript.blocks if block.kind == "context")
        self.assertEqual(you.text, query)
        self.assertEqual(you.detail, "")
        self.assertNotIn(command, you.text)
        self.assertIn("INJECTED_CONTEXT_BLOCK", context.text)

    def test_verbose_includes_hidden_layers(self):
        messages, prompts = sample_messages()
        transcript = build_transcript(messages, prompts, verbose=True)
        kinds = [block.kind for block in transcript.blocks]
        piece_kinds = [piece.kind for block in transcript.blocks for piece in block.pieces]
        text = "\n".join(
            [block.text for block in transcript.blocks]
            + [piece.text for block in transcript.blocks for piece in block.pieces]
        )
        self.assertIn("system", kinds)
        self.assertIn("context", kinds)
        self.assertIn("reasoning", piece_kinds)
        self.assertIn("tool_output", piece_kinds)
        self.assertIn("caption", piece_kinds)
        self.assertEqual(kinds.count("agent"), 1)
        self.assertIn("SYSTEM_PROMPT_TEXT", text)
        self.assertIn("INJECTED_CONTEXT_BLOCK", text)
        self.assertIn("REASONING_PRIVATE", text)
        self.assertIn("TOOL_RESULT_PAYLOAD", text)
        self.assertIn("Ran List map tool modules", text)

    def test_turn_timestamp_uses_catalog_style_on_you_and_agent(self):
        query = "Please add a river tool."
        raw = "Friday, Oct 23, 2026, 11:13 AM (UTC-7)"
        messages = [
            {
                "role": "user",
                "content": f"<timestamp>{raw}</timestamp>\n<user_query>{query}</user_query>",
            },
            {"role": "assistant", "content": [{"type": "text", "text": "Done."}]},
        ]
        transcript = build_transcript(messages, [query])
        you, agent = transcript.blocks
        self.assertEqual(you.timestamp, "Oct 23, 2026 11:13 AM")
        self.assertEqual(agent.timestamp, "Oct 23, 2026 11:13 AM")

    def test_unparsed_timestamp_collapses_and_missing_time_is_omitted(self):
        query = "Please add a river tool."
        messages = [
            {
                "role": "user",
                "content": "<timestamp>  sometime\nnext   week  </timestamp>\n"
                f"<user_query>{query}</user_query>",
            },
            {"role": "assistant", "content": "Answer"},
        ]
        transcript = build_transcript(messages, [query])
        self.assertEqual(transcript.blocks[0].timestamp, "sometime next week")
        self.assertEqual(transcript.blocks[1].timestamp, "sometime next week")
        bare = build_transcript(*sample_messages())
        self.assertTrue(all(block.timestamp == "" for block in bare.blocks))

    def test_footer_names_skipped_blob_and_unlinked_image(self):
        messages, prompts = sample_messages()
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "store.db"
            write_db(db_path, messages, [PNG], [b"not-json-blob"])
            conversation = load_conversation(db_path)
        transcript = build_transcript(
            conversation.messages,
            prompts,
            skipped=conversation.skipped,
            unlinked_images=conversation.unlinked_images,
        )
        footer = "\n".join(transcript.footer)
        self.assertEqual(len(conversation.skipped), 1)
        self.assertEqual(len(conversation.unlinked_images), 1)
        self.assertIn(conversation.skipped[0], footer)
        self.assertIn(conversation.unlinked_images[0], footer)
        body = "\n".join(block.text for block in transcript.blocks)
        self.assertNotIn(conversation.unlinked_images[0], body)


if __name__ == "__main__":
    unittest.main()
