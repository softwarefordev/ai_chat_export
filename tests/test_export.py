import contextlib
import hashlib
import io
import os
import tempfile
import time
import unittest
from pathlib import Path

from ai_chat_export.__main__ import activity, export_session, main, safe_stem
from ai_chat_export.catalog import format_timestamp
from tests.support import sample_messages, write_chat


class ExportTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.chats = self.root / "chats"
        self.out = self.root / "out"
        self.out.mkdir()
        messages, prompts = sample_messages()
        self.messages = messages
        self.prompts = prompts

    def tearDown(self):
        self.tmp.cleanup()

    def _chat(self, chat_id="chat-1", title="Fantasy Map Maker", **kwargs):
        return write_chat(
            self.chats,
            chat_id=chat_id,
            cwd=str(self.root),
            title=title,
            updated_ms=1_000,
            messages=self.messages,
            prompts=self.prompts,
            **kwargs,
        )

    def test_writes_html_path_in_out_dir(self):
        self._chat()
        stdout = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=stdout,
        )
        self.assertEqual(code, 0)
        html_path = self.out / "Fantasy Map Maker.html"
        md_path = self.out / "Fantasy Map Maker.md"
        self.assertTrue(html_path.is_file())
        self.assertFalse(md_path.exists())
        printed = stdout.getvalue()
        self.assertIn(str(html_path.resolve()), printed)
        self.assertNotIn(str(md_path.resolve()), printed)
        self.assertIn("#161616", html_path.read_text(encoding="utf-8"))

    def test_current_directory_is_the_default(self):
        self._chat()
        previous = Path.cwd()
        os.chdir(self.out)
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                code = main(["--id", "chat-1", "--chats-root", str(self.chats)])
        finally:
            os.chdir(previous)
        html_path = self.out / "Fantasy Map Maker.html"
        self.assertEqual(code, 0)
        self.assertTrue(html_path.is_file())
        self.assertFalse((self.out / "Fantasy Map Maker.md").exists())
        self.assertIn(str(html_path.resolve()), stdout.getvalue())

    def test_tools_flag_and_verbose_modes(self):
        self._chat(chat_id="modes", title="Modes")
        plain = self.out / "plain"
        tools = self.out / "tools"
        verbose = self.out / "verbose"
        self.assertEqual(
            export_session(
                chats_root=self.chats,
                chat_id="modes",
                out_dir=plain,
                stdout=io.StringIO(),
            ),
            0,
        )
        self.assertEqual(
            export_session(
                chats_root=self.chats,
                chat_id="modes",
                out_dir=tools,
                show_tools=True,
                stdout=io.StringIO(),
            ),
            0,
        )
        self.assertEqual(
            export_session(
                chats_root=self.chats,
                chat_id="modes",
                out_dir=verbose,
                verbose=True,
                stdout=io.StringIO(),
            ),
            0,
        )
        plain_page = (plain / "Modes.html").read_text(encoding="utf-8")
        tools_page = (tools / "Modes.html").read_text(encoding="utf-8")
        verbose_page = (verbose / "Modes.html").read_text(encoding="utf-8")
        self.assertNotIn("Ran List map tool modules", plain_page)
        self.assertNotIn("TOOL_RESULT_PAYLOAD", plain_page)
        self.assertIn("Ran List map tool modules", tools_page)
        self.assertNotIn("TOOL_RESULT_PAYLOAD", tools_page)
        self.assertNotIn("SECRET_COMMAND_XYZ", tools_page)
        self.assertIn("Ran List map tool modules", verbose_page)
        self.assertIn("TOOL_RESULT_PAYLOAD", verbose_page)
        self.assertEqual(verbose_page.count("<h2>Agent</h2>"), 1)

    def test_light_theme_and_verbose(self):
        self._chat()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            theme="light",
            verbose=True,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        page = (self.out / "Fantasy Map Maker.html").read_text(encoding="utf-8")
        self.assertIn("#f7f7f4", page)
        self.assertIn("TOOL_RESULT_PAYLOAD", page)
        self.assertIn("SYSTEM_PROMPT_TEXT", page)

    def test_existing_html_is_replaced_and_markdown_stays(self):
        self._chat()
        html_path = self.out / "Fantasy Map Maker.html"
        md_path = self.out / "Fantasy Map Maker.md"
        neighbor = self.out / "notes.txt"
        html_path.write_text("OLD_HTML", encoding="utf-8")
        md_path.write_text("OLD_MD", encoding="utf-8")
        neighbor.write_text("keep-me", encoding="utf-8")
        stdout = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=stdout,
        )
        self.assertEqual(code, 0)
        printed = stdout.getvalue()
        self.assertIn(str(html_path.resolve()), printed)
        self.assertNotIn(str(md_path.resolve()), printed)
        html = html_path.read_text(encoding="utf-8")
        self.assertIn("Please add a river tool.", html)
        self.assertNotIn("OLD_HTML", html)
        self.assertEqual(md_path.read_text(encoding="utf-8"), "OLD_MD")
        self.assertEqual(neighbor.read_text(encoding="utf-8"), "keep-me")

    def test_markdown_flag_writes_and_replaces_both_files(self):
        self._chat()
        html_path = self.out / "Fantasy Map Maker.html"
        md_path = self.out / "Fantasy Map Maker.md"
        html_path.write_text("OLD_HTML", encoding="utf-8")
        md_path.write_text("OLD_MD", encoding="utf-8")
        stdout = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            write_markdown=True,
            stdout=stdout,
        )
        self.assertEqual(code, 0)
        printed = stdout.getvalue()
        self.assertIn(str(html_path.resolve()), printed)
        self.assertIn(str(md_path.resolve()), printed)
        markdown = md_path.read_text(encoding="utf-8")
        self.assertIn("Please add a river tool.", markdown)
        self.assertIn("The river tool lives in tools/river.py.", markdown)
        self.assertNotIn("OLD_MD", markdown)
        self.assertNotIn("#161616", markdown)
        self.assertNotIn("#f7f7f4", markdown)
        with contextlib.redirect_stdout(io.StringIO()):
            cli = main(
                [
                    "--id",
                    "chat-1",
                    "--chats-root",
                    str(self.chats),
                    "--out",
                    str(self.out / "cli"),
                    "--markdown",
                ]
            )
        self.assertEqual(cli, 0)
        self.assertTrue((self.out / "cli" / "Fantasy Map Maker.md").is_file())

    def test_html_only_target_and_neighbor_file(self):
        self._chat()
        html_path = self.out / "Fantasy Map Maker.html"
        md_path = self.out / "Fantasy Map Maker.md"
        neighbor = self.out / "notes.txt"
        html_path.write_text("OLD_HTML", encoding="utf-8")
        neighbor.write_text("keep-me", encoding="utf-8")
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        html = html_path.read_text(encoding="utf-8")
        self.assertIn("Please add a river tool.", html)
        self.assertNotIn("OLD_HTML", html)
        self.assertFalse(md_path.exists())
        self.assertEqual(neighbor.read_text(encoding="utf-8"), "keep-me")

    def test_missing_conversation(self):
        write_chat(
            self.chats,
            chat_id="empty",
            cwd=str(self.root),
            title="Empty",
            with_store=False,
        )
        stderr = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="empty",
            out_dir=self.out,
            stderr=stderr,
        )
        self.assertEqual(code, 1)
        self.assertIn("no transcript", stderr.getvalue())
        self.assertEqual(list(self.out.iterdir()), [])

    def test_unknown_id(self):
        stderr = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="missing",
            out_dir=self.out,
            stderr=stderr,
        )
        self.assertEqual(code, 1)
        self.assertIn("Chat not found", stderr.getvalue())
        self.assertEqual(list(self.out.iterdir()), [])

    def test_untitled_chat_uses_id(self):
        self._chat(chat_id="id-only", title=None, include_title=False)
        code = export_session(
            chats_root=self.chats,
            chat_id="id-only",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "id-only.html").is_file())

    def test_store_bytes_unchanged(self):
        chat_dir = self._chat()
        db_path = chat_dir / "store.db"
        before = hashlib.sha256(db_path.read_bytes()).hexdigest()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        after = hashlib.sha256(db_path.read_bytes()).hexdigest()
        self.assertEqual(before, after)

    def test_safe_stem_strips_illegal_characters(self):
        self.assertEqual(safe_stem('Map: "Maker"', "id"), "Map Maker")

    def test_wrapped_query_detail_and_turn_time(self):
        query = "Show only the query."
        command = "opsx-propose user turns"
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "INJECTED_CONTEXT_BLOCK\n"
                        f"<cursor_commands>\n{command}\n</cursor_commands>",
                    },
                    {
                        "type": "text",
                        "text": "<timestamp>Friday, Oct 23, 2026, 11:13 AM (UTC-7)</timestamp>\n"
                        f"<user_query>\n{query}\n</user_query>",
                    },
                ],
            },
            {"role": "assistant", "content": [{"type": "text", "text": "Done."}]},
        ]
        write_chat(
            self.chats,
            chat_id="wrapped",
            cwd=str(self.root),
            title="Wrapped",
            updated_ms=1_000,
            messages=messages,
            prompts=[query],
        )
        plain = self.out / "plain"
        detail = self.out / "detail"
        self.assertEqual(
            export_session(
                chats_root=self.chats,
                chat_id="wrapped",
                out_dir=plain,
                write_markdown=True,
                stdout=io.StringIO(),
            ),
            0,
        )
        self.assertEqual(
            export_session(
                chats_root=self.chats,
                chat_id="wrapped",
                out_dir=detail,
                show_detail=True,
                write_markdown=True,
                stdout=io.StringIO(),
            ),
            0,
        )
        turn = "Oct 23, 2026 11:13 AM"
        header = format_timestamp(1_000)
        for folder, expect_command in ((plain, False), (detail, True)):
            for name in ("Wrapped.html", "Wrapped.md"):
                document = (folder / name).read_text(encoding="utf-8")
                self.assertIn(query, document)
                self.assertIn(turn, document)
                self.assertIn(header, document)
                self.assertNotIn("<user_query>", document)
                self.assertNotIn("INJECTED_CONTEXT_BLOCK", document)
                if expect_command:
                    self.assertEqual(document.count(command), 1)
                else:
                    self.assertNotIn(command, document)

    def test_terminal_shows_dots_before_the_path_and_a_pipe_stays_quiet(self):
        self._chat()
        stdout = io.StringIO()
        terminal = Terminal()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=stdout,
            stderr=terminal,
        )
        self.assertEqual(code, 0)
        printed = stdout.getvalue()
        self.assertIn(str((self.out / "Fantasy Map Maker.html").resolve()), printed)
        self.assertNotIn("...", printed)
        frames = terminal.getvalue()
        self.assertIn("...", frames)
        self.assertNotIn("Fantasy Map Maker.html", frames)

        quiet = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=io.StringIO(),
            stderr=quiet,
        )
        self.assertEqual(code, 0)
        self.assertNotIn("...", quiet.getvalue())

    def test_open_stretch_advances_through_each_frame(self):
        terminal = Terminal()
        with activity(terminal, 0.03):
            time.sleep(0.12)
        text = terminal.getvalue()
        first = text.find("...")
        self.assertGreaterEqual(first, 0)
        second = text.find("\r..", first + 3)
        self.assertGreater(second, first)
        third = text.find("\r.", second + 3)
        self.assertGreater(third, second)

    def test_missing_chat_shows_dots_before_the_error(self):
        terminal = Terminal()
        code = export_session(
            chats_root=self.chats,
            chat_id="missing",
            out_dir=self.out,
            stdout=io.StringIO(),
            stderr=terminal,
        )
        self.assertEqual(code, 1)
        text = terminal.getvalue()
        error = "Chat not found: missing"
        self.assertLess(text.find("..."), text.find(error))
        self.assertIn("\r   \r" + error + "\n", text)

    def test_catalog_warning_is_a_complete_line_and_the_cycle_resumes(self):
        write_chat(
            self.chats,
            chat_id="bad",
            cwd=str(self.root),
            title="Bad",
            schema=2,
            messages=self.messages,
            prompts=self.prompts,
        )
        self._chat()
        terminal = Terminal()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            stdout=io.StringIO(),
            stderr=terminal,
        )
        self.assertEqual(code, 0)
        text = terminal.getvalue()
        warning = "Unsupported schemaVersion 2 for bad"
        warn_at = text.find(warning)
        self.assertGreaterEqual(warn_at, 0)
        self.assertIn("\r   \r" + warning + "\n", text)
        self.assertLess(text.find("..."), warn_at)
        self.assertIn("...", text[warn_at + len(warning):])


class Terminal(io.StringIO):
    def isatty(self) -> bool:
        return True


if __name__ == "__main__":
    unittest.main()
