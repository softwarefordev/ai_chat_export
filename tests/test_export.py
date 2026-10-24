import contextlib
import hashlib
import io
import json
import os
import sqlite3
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

from ai_chat_export.__main__ import Activity, export_session, main, safe_stem
from ai_chat_export.catalog import format_timestamp
from ai_chat_export.picker import run_picker
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
        self.assertIn("#071207", html_path.read_text(encoding="utf-8"))

    def test_current_directory_is_the_default(self):
        self._chat()
        previous = Path.cwd()
        os.chdir(self.out)
        stdout = io.StringIO()
        try:
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "--id",
                        "chat-1",
                        "--chats-root",
                        str(self.chats),
                        "--projects-root",
                        str(self.root / "no-projects"),
                        "--copilot-root",
                        str(self.root / "no-copilot"),
                    ]
                )
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
            theme="light-web",
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

    def test_markdown_flag_writes_markdown_and_leaves_html(self):
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
        self.assertNotIn(str(html_path.resolve()), printed)
        self.assertIn(str(md_path.resolve()), printed)
        self.assertEqual(html_path.read_text(encoding="utf-8"), "OLD_HTML")
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
                    "--projects-root",
                    str(self.root / "no-projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                ]
            )
        self.assertEqual(cli, 0)
        self.assertTrue((self.out / "cli" / "Fantasy Map Maker.md").is_file())
        self.assertFalse((self.out / "cli" / "Fantasy Map Maker.html").exists())

    def test_name_writes_that_path_and_skips_the_title(self):
        self._chat()
        target = self.root / "nested" / "deep" / "page.html"
        stdout = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            output_path=target,
            stdout=stdout,
        )
        self.assertEqual(code, 0)
        self.assertTrue(target.is_file())
        self.assertIn(str(target.resolve()), stdout.getvalue())
        self.assertIn("Please add a river tool.", target.read_text(encoding="utf-8"))
        self.assertFalse((self.out / "Fantasy Map Maker.html").exists())
        self.assertFalse(target.with_suffix(".md").exists())

        markdown = self.root / "notes.md"
        markdown.write_text("OLD", encoding="utf-8")
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            output_path=markdown,
            write_markdown=True,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        text = markdown.read_text(encoding="utf-8")
        self.assertNotIn("OLD", text)
        self.assertIn("Please add a river tool.", text)
        self.assertFalse((self.out / "Fantasy Map Maker.md").exists())
        self.assertFalse((self.root / "notes.html").exists())

        previous = Path.cwd()
        os.chdir(self.root)
        try:
            code = export_session(
                chats_root=self.chats,
                chat_id="chat-1",
                out_dir=self.out,
                output_path=Path("relative.html"),
                stdout=io.StringIO(),
            )
        finally:
            os.chdir(previous)
        self.assertEqual(code, 0)
        self.assertTrue((self.root / "relative.html").is_file())

        folder = self.root / "already"
        folder.mkdir()
        stderr = io.StringIO()
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            output_path=folder,
            stderr=stderr,
        )
        self.assertEqual(code, 1)
        self.assertIn("directory", stderr.getvalue())
        self.assertFalse((self.out / "Fantasy Map Maker.html").exists())

        with contextlib.redirect_stdout(io.StringIO()):
            cli = main(
                [
                    "--id",
                    "chat-1",
                    "--chats-root",
                    str(self.chats),
                    "--name",
                    str(self.root / "from-id.html"),
                    "--projects-root",
                    str(self.root / "no-projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                ]
            )
        self.assertEqual(cli, 0)
        self.assertTrue((self.root / "from-id.html").is_file())
        self.assertFalse((self.out / "Fantasy Map Maker.html").exists())

    def test_name_with_out_writes_nothing(self):
        self._chat()
        target = self.root / "blocked.html"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(
                [
                    "--id",
                    "chat-1",
                    "--chats-root",
                    str(self.root / "missing-catalog"),
                    "--name",
                    str(target),
                    "--out",
                    str(self.out),
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("--name", stderr.getvalue())
        self.assertNotIn("Chat not found", stderr.getvalue())
        self.assertFalse(target.exists())
        self.assertFalse((self.out / "Fantasy Map Maker.html").exists())

    def test_name_without_id_writes_no_file(self):
        self._chat()
        target = self.root / "picker-name.html"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(
                [
                    "--chats-root",
                    str(self.root / "missing-catalog"),
                    "--name",
                    str(target),
                    "--out",
                    str(self.out),
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("`--name` requires `--id`.", stderr.getvalue())
        self.assertNotIn("Pass either --name or --out.", stderr.getvalue())
        self.assertNotIn("Chat not found", stderr.getvalue())
        self.assertFalse(target.exists())
        self.assertFalse((self.out / "Fantasy Map Maker.html").exists())

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
        self.assertEqual(len(safe_stem("A" * 100, "id")), 80)
        self.assertEqual(safe_stem(":::", ""), "export")

    def test_reserved_title_uses_the_chat_id(self):
        self._chat(chat_id="room-id", title="CON")
        code = export_session(
            chats_root=self.chats,
            chat_id="room-id",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "room-id.html").is_file())
        self.assertFalse((self.out / "CON.html").exists())

    def test_reserved_markdown_title_uses_the_chat_id(self):
        self._chat(chat_id="room-id", title="nul")
        code = export_session(
            chats_root=self.chats,
            chat_id="room-id",
            out_dir=self.out,
            write_markdown=True,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "room-id.md").is_file())
        self.assertFalse((self.out / "nul.md").exists())

    def test_reserved_id_uses_export_suffix(self):
        self._chat(chat_id="CON", title=None, include_title=False)
        code = export_session(
            chats_root=self.chats,
            chat_id="CON",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "CON-export.html").is_file())
        self.assertFalse((self.out / "CON.html").exists())

    def test_explicit_reserved_path_is_written_as_given(self):
        self._chat()
        target = self.out / "CON.html"
        code = export_session(
            chats_root=self.chats,
            chat_id="chat-1",
            out_dir=self.out,
            output_path=target,
            stdout=io.StringIO(),
        )
        self.assertEqual(code, 0)
        self.assertTrue(target.is_file())
        self.assertFalse((self.out / "Fantasy Map Maker.html").exists())

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
        plain_md = self.out / "plain-md"
        detail = self.out / "detail"
        detail_md = self.out / "detail-md"
        exports = (
            (plain, False, False),
            (plain_md, False, True),
            (detail, True, False),
            (detail_md, True, True),
        )
        for folder, show_detail, markdown in exports:
            self.assertEqual(
                export_session(
                    chats_root=self.chats,
                    chat_id="wrapped",
                    out_dir=folder,
                    show_detail=show_detail,
                    write_markdown=markdown,
                    stdout=io.StringIO(),
                ),
                0,
            )
        turn = "Oct 23, 2026 11:13 AM"
        header = format_timestamp(1_000)
        for folder, expect_command, markdown in exports:
            name = "Wrapped.md" if markdown else "Wrapped.html"
            other = "Wrapped.html" if markdown else "Wrapped.md"
            self.assertFalse((folder / other).exists())
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
        with Activity(terminal, 0.03):
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

    def test_ide_id_writes_html_without_a_source_cell(self):
        workspace = self.root / "MapFolder"
        workspace.mkdir()
        transcript, trusted = _write_export_transcript(
            self.root / "projects",
            transcript_id="ide-1",
            query="River map",
            reply="The map is ready.",
            workspace=str(workspace),
        )
        before = transcript.read_bytes(), trusted.read_bytes()
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(
                [
                    "--id",
                    "ide-1",
                    "--chats-root",
                    str(self.root / "missing-chats"),
                    "--projects-root",
                    str(self.root / "projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                    "--out",
                    str(self.out),
                ]
            )
        page = (self.out / "River map.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn(str((self.out / "River map.html").resolve()), stdout.getvalue())
        self.assertIn("River map", page)
        self.assertIn("MapFolder", page)
        self.assertIn("The map is ready.", page)
        self.assertNotIn("CLI", page)
        self.assertNotIn("IDE", page)
        self.assertEqual(before, (transcript.read_bytes(), trusted.read_bytes()))

    def test_shared_id_exports_the_agent_chat(self):
        self._chat(chat_id="same", title="Chat copy")
        _write_export_transcript(
            self.root / "projects",
            transcript_id="same",
            query="Only in the transcript",
            reply="Transcript reply.",
            workspace=str(self.root),
        )
        code = export_session(
            chats_root=self.chats,
            projects_root=self.root / "projects",
            chat_id="same",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        page = (self.out / "Chat copy.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("Please add a river tool.", page)
        self.assertNotIn("Only in the transcript", page)

    def test_empty_ide_transcript_writes_no_file(self):
        folder = self.root / "projects" / "demo" / "agent-transcripts" / "empty"
        folder.mkdir(parents=True)
        (folder / "empty.jsonl").write_text(
            json.dumps({"type": "turn_ended", "status": "success"}) + "\n",
            encoding="utf-8",
        )
        stderr = io.StringIO()
        code = export_session(
            chats_root=self.root / "missing-chats",
            projects_root=self.root / "projects",
            chat_id="empty",
            out_dir=self.out,
            stdout=io.StringIO(),
            stderr=stderr,
        )
        self.assertEqual(code, 1)
        self.assertIn("no transcript", stderr.getvalue())
        self.assertEqual(list(self.out.iterdir()), [])

    def test_source_flag_filters_cli_ide_and_rejects_unknown(self):
        self._chat(chat_id="agent-1", title="Fantasy Map Maker")
        _write_export_transcript(
            self.root / "projects",
            transcript_id="ide-1",
            query="River map",
            reply="The map is ready.",
            workspace=str(self.root),
        )
        unknown = self.root / "unknown-out"
        unknown.mkdir()
        stderr = io.StringIO()
        with (
            mock.patch("ai_chat_export.__main__.load_sessions") as load,
            contextlib.redirect_stderr(stderr),
        ):
            with self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "--source",
                        "other",
                        "--id",
                        "agent-1",
                        "--chats-root",
                        str(self.chats),
                        "--projects-root",
                        str(self.root / "projects"),
                        "--copilot-root",
                        str(self.root / "no-copilot"),
                        "--out",
                        str(unknown),
                    ]
                )
        self.assertNotEqual(raised.exception.code, 0)
        load.assert_not_called()
        self.assertNotIn("Chat not found", stderr.getvalue())
        self.assertEqual(list(unknown.iterdir()), [])

        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(
                [
                    "--id",
                    "agent-1",
                    "--source",
                    "cursor-cli",
                    "--chats-root",
                    str(self.chats),
                    "--projects-root",
                    str(self.root / "projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                    "--out",
                    str(self.out),
                ]
            )
        self.assertEqual(code, 0)
        self.assertTrue((self.out / "Fantasy Map Maker.html").is_file())

        rejected = self.root / "rejected"
        rejected.mkdir()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(
                [
                    "--id",
                    "agent-1",
                    "--source",
                    "cursor-ide",
                    "--chats-root",
                    str(self.chats),
                    "--projects-root",
                    str(self.root / "projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                    "--out",
                    str(rejected),
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("Chat not found", stderr.getvalue())
        self.assertEqual(list(rejected.iterdir()), [])

        calls: list[dict] = []

        def fake(chats, theme, keys, launch, write, **kwargs):
            frames: list[str] = []
            result = run_picker(
                chats,
                theme,
                ["s"],
                launch,
                frames.append,
                width=80,
                sources=kwargs.get("sources"),
            )
            calls.append(
                {
                    "sources": kwargs.get("sources"),
                    "frames": frames,
                    "kinds": {chat.source for chat in chats},
                }
            )
            return result

        with (
            mock.patch("ai_chat_export.__main__.run_picker", side_effect=fake),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = main(
                [
                    "--source",
                    "cursor-cli",
                    "--chats-root",
                    str(self.chats),
                    "--projects-root",
                    str(self.root / "projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                    "--out",
                    str(self.out),
                ]
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls[0]["sources"], {"cli"})
        self.assertIn("Cursor-CLI *", calls[0]["frames"][0])
        self.assertIn("Fantasy Map Maker", calls[0]["frames"][0])
        self.assertNotIn("River map", calls[0]["frames"][0])
        self.assertIn("Cursor-IDE *", calls[0]["frames"][-1])
        self.assertIn("River map", calls[0]["frames"][-1])

        with (
            mock.patch("ai_chat_export.__main__.run_picker", side_effect=fake),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = main(
                [
                    "--source",
                    "cursor-cli",
                    "--source",
                    "cursor-ide",
                    "--chats-root",
                    str(self.chats),
                    "--projects-root",
                    str(self.root / "projects"),
                    "--copilot-root",
                    str(self.root / "no-copilot"),
                    "--out",
                    str(self.out),
                ]
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls[1]["sources"], {"cli", "ide"})
        self.assertIn("cli", calls[1]["kinds"])
        self.assertIn("ide", calls[1]["kinds"])
        self.assertIn("Cursor-CLI *", calls[1]["frames"][0])
        self.assertIn("Cursor-IDE *", calls[1]["frames"][0])
        self.assertNotIn("All sources *", calls[1]["frames"][0])
        self.assertIn("Fantasy Map Maker", calls[1]["frames"][0])
        self.assertIn("River map", calls[1]["frames"][0])
        self.assertIn("All sources *", calls[1]["frames"][-1])

    def test_copilot_source_flag_opens_the_picker_and_excludes_the_id(self):
        root = self.root / "copilot"
        _write_copilot_session(
            root,
            session_id="cp-1",
            summary="Harbor notes",
            cwd=str(self.root),
            turns=[("Map the harbor.", "The harbor is mapped.")],
        )
        self.chats.mkdir()
        projects = self.root / "projects"
        projects.mkdir()
        unknown = self.root / "unknown-out"
        unknown.mkdir()
        stderr = io.StringIO()
        with (
            mock.patch("ai_chat_export.__main__.load_sessions") as load,
            contextlib.redirect_stderr(stderr),
        ):
            with self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "--source",
                        "other",
                        "--id",
                        "cp-1",
                        "--chats-root",
                        str(self.chats),
                        "--projects-root",
                        str(projects),
                        "--copilot-root",
                        str(root),
                        "--out",
                        str(unknown),
                    ]
                )
        self.assertNotEqual(raised.exception.code, 0)
        load.assert_not_called()
        self.assertNotIn("Chat not found", stderr.getvalue())
        self.assertEqual(list(unknown.iterdir()), [])

        calls: list[dict] = []

        def fake(chats, theme, keys, launch, write, **kwargs):
            frames: list[str] = []
            result = run_picker(
                chats,
                theme,
                ["s"],
                launch,
                frames.append,
                width=80,
                sources=kwargs.get("sources"),
            )
            calls.append({"sources": kwargs.get("sources"), "frames": frames})
            return result

        with (
            mock.patch("ai_chat_export.__main__.run_picker", side_effect=fake),
            contextlib.redirect_stdout(io.StringIO()),
        ):
            code = main(
                [
                    "--source",
                    "copilot-cli",
                    "--chats-root",
                    str(self.chats),
                    "--projects-root",
                    str(projects),
                    "--copilot-root",
                    str(root),
                    "--out",
                    str(self.out),
                ]
            )
        self.assertEqual(code, 0)
        self.assertEqual(calls[0]["sources"], {"cp-cli"})
        self.assertIn("Copilot-CLI *", calls[0]["frames"][0])
        self.assertIn("Harbor notes", calls[0]["frames"][0])

        rejected = self.root / "rejected"
        rejected.mkdir()
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            code = main(
                [
                    "--id",
                    "cp-1",
                    "--source",
                    "cursor-cli",
                    "--chats-root",
                    str(self.chats),
                    "--projects-root",
                    str(projects),
                    "--copilot-root",
                    str(root),
                    "--out",
                    str(rejected),
                ]
            )
        self.assertEqual(code, 1)
        self.assertIn("Chat not found", stderr.getvalue())
        self.assertEqual(list(rejected.iterdir()), [])

    def test_copilot_id_writes_the_turn_text(self):
        root = self.root / "copilot"
        _write_copilot_session(
            root,
            session_id="cp-1",
            summary="River map",
            events=[
                {"type": "system.message", "data": {"content": "SYSTEM-ONLY"}},
                {"type": "user.message", "data": {"content": "Please add a river."}},
                {
                    "type": "assistant.message",
                    "data": {
                        "content": "",
                        "reasoningText": "REASON-ONLY",
                        "encryptedContent": "SECRET-ENCRYPTED",
                    },
                },
                {"type": "assistant.message", "data": {"content": "The map is ready."}},
                {"type": "user.message", "data": {"content": "Add a lake."}},
                {"type": "assistant.message", "data": {"content": "The lake is marked."}},
            ],
            turns=[("ONLY-IN-TURNS", "ONLY-IN-TURNS-REPLY")],
            index="INDEX-MARKER",
        )
        before = _copilot_bytes(root, "cp-1")
        code = export_session(
            chats_root=self.root / "missing-chats",
            projects_root=self.root / "missing-projects",
            copilot_root=root,
            chat_id="cp-1",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        page = (self.out / "River map.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("Please add a river.", page)
        self.assertIn("The map is ready.", page)
        self.assertIn("Add a lake.", page)
        self.assertIn("The lake is marked.", page)
        self.assertEqual(page.count(">Agent<"), 2)
        self.assertNotIn("ONLY-IN-TURNS", page)
        self.assertNotIn("SYSTEM-ONLY", page)
        self.assertNotIn("REASON-ONLY", page)
        self.assertNotIn("SECRET-ENCRYPTED", page)
        self.assertNotIn("INDEX-MARKER", page)
        self.assertNotIn("Cp-CLI", page)
        self.assertNotIn("CLI", page)
        self.assertNotIn("http", page.lower())
        self.assertEqual(before, _copilot_bytes(root, "cp-1"))
        markdown_out = self.root / "markdown-out"
        markdown_out.mkdir()
        md_code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-1",
            out_dir=markdown_out,
            write_markdown=True,
            stdout=io.StringIO(),
        )
        markdown = (markdown_out / "River map.md").read_text(encoding="utf-8")
        self.assertEqual(md_code, 0)
        self.assertIn("Please add a river.", markdown)
        self.assertIn("The map is ready.", markdown)

    def test_copilot_empty_assistant_has_no_agent_heading(self):
        root = self.root / "copilot"
        _write_copilot_session(
            root,
            session_id="cp-empty-agent",
            summary="Note",
            events=[
                {"type": "user.message", "data": {"content": "Just a note."}},
                {"type": "assistant.message", "data": {"content": ""}},
            ],
        )
        code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-empty-agent",
            out_dir=self.out,
            stdout=io.StringIO(),
        )
        page = (self.out / "Note.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("Just a note.", page)
        self.assertNotIn(">Agent<", page)

    def test_copilot_session_with_no_turns_writes_no_file(self):
        root = self.root / "copilot"
        _write_copilot_session(root, session_id="cp-blank", summary="Blank")
        stderr = io.StringIO()
        code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-blank",
            out_dir=self.out,
            stdout=io.StringIO(),
            stderr=stderr,
        )
        self.assertEqual(code, 1)
        self.assertIn("Chat has no transcript: cp-blank", stderr.getvalue())
        self.assertEqual(list(self.out.iterdir()), [])

    def test_copilot_missing_event_log_uses_turns(self):
        root = self.root / "copilot"
        _write_copilot_session(
            root,
            session_id="cp-turns",
            summary="From turns",
            turns=[("Please add a river.", "The map is ready.")],
        )
        code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-turns",
            out_dir=self.out,
            show_tools=True,
            stdout=io.StringIO(),
        )
        page = (self.out / "From turns.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("Please add a river.", page)
        self.assertIn("The map is ready.", page)
        self.assertNotIn("Read ", page)

    def test_unreadable_copilot_events_fall_back_to_turns(self):
        root = self.root / "copilot"
        folder = _write_copilot_session(
            root,
            session_id="cp-bad-log",
            summary="Recovered",
            turns=[("Please add a river.", "The map is ready.")],
        )
        (folder / "events.jsonl").write_bytes(b"\xff")
        stderr = io.StringIO()
        code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-bad-log",
            out_dir=self.out,
            stdout=io.StringIO(),
            stderr=stderr,
        )
        page = (self.out / "Recovered.html").read_text(encoding="utf-8")
        self.assertEqual(code, 0)
        self.assertIn("Unreadable Copilot events cp-bad-log:", stderr.getvalue())
        self.assertIn("Please add a river.", page)
        self.assertIn("The map is ready.", page)

    def test_copilot_tools_and_verbose_detail(self):
        root = self.root / "copilot"
        events = [
            {"type": "system.message", "data": {"content": "SYSTEM-ONLY"}},
            {"type": "user.message", "data": {"content": "Please add a river."}},
            {
                "type": "assistant.message",
                "data": {
                    "content": "",
                    "reasoningText": "REASON-ONLY",
                    "encryptedContent": "SECRET-ENCRYPTED",
                },
            },
            {
                "type": "tool.execution_start",
                "data": {"toolName": "view", "arguments": {"path": "maps/river.txt"}},
            },
            {
                "type": "tool.execution_complete",
                "data": {"result": "TOOL-RESULT-SECRET"},
            },
            {
                "type": "tool.execution_start",
                "data": {"toolName": "glob", "arguments": {"pattern": "**/*.map"}},
            },
            {
                "type": "tool.execution_start",
                "data": {
                    "toolName": "powershell",
                    "arguments": {
                        "description": "List the map files",
                        "command": "secret-command-text",
                    },
                },
            },
            {
                "type": "tool.execution_start",
                "data": {"toolName": "grep", "arguments": {"pattern": "river"}},
            },
            {
                "type": "tool.execution_start",
                "data": {"toolName": "create", "arguments": {"path": "maps/lake.txt"}},
            },
            {"type": "assistant.message", "data": {"content": "The map is ready."}},
        ]
        _write_copilot_session(root, session_id="cp-tools", summary="Tools", events=events)
        tools_out = self.root / "tools-out"
        tools_out.mkdir()
        tools_code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-tools",
            out_dir=tools_out,
            show_tools=True,
            stdout=io.StringIO(),
        )
        tools_page = (tools_out / "Tools.html").read_text(encoding="utf-8")
        self.assertEqual(tools_code, 0)
        self.assertIn("Read maps/river.txt", tools_page)
        self.assertIn("Glob **/*.map", tools_page)
        self.assertIn("Ran List the map files", tools_page)
        self.assertIn("Grep river", tools_page)
        self.assertIn("Create maps/lake.txt", tools_page)
        self.assertNotIn("TOOL-RESULT-SECRET", tools_page)
        self.assertNotIn("secret-command-text", tools_page)
        self.assertNotIn("REASON-ONLY", tools_page)
        self.assertNotIn("SYSTEM-ONLY", tools_page)
        self.assertNotIn("SECRET-ENCRYPTED", tools_page)
        verbose_out = self.root / "verbose-out"
        verbose_out.mkdir()
        verbose_code = export_session(
            chats_root=self.root / "missing-chats",
            copilot_root=root,
            chat_id="cp-tools",
            out_dir=verbose_out,
            verbose=True,
            stdout=io.StringIO(),
        )
        verbose_page = (verbose_out / "Tools.html").read_text(encoding="utf-8")
        self.assertEqual(verbose_code, 0)
        self.assertIn("Read maps/river.txt", verbose_page)
        self.assertIn("REASON-ONLY", verbose_page)
        self.assertIn("TOOL-RESULT-SECRET", verbose_page)
        self.assertIn("SYSTEM-ONLY", verbose_page)
        self.assertNotIn("SECRET-ENCRYPTED", verbose_page)
        self.assertNotIn("secret-command-text", verbose_page)


def _write_copilot_session(
    root: Path,
    *,
    session_id: str,
    summary: str,
    cwd: str = "",
    events: list[dict] | None = None,
    turns: list[tuple[str, str | None]] | None = None,
    index: str | None = None,
) -> Path:
    root.mkdir(parents=True, exist_ok=True)
    database = root / "session-store.db"
    connection = sqlite3.connect(database)
    connection.execute(
        "CREATE TABLE IF NOT EXISTS sessions (id TEXT, cwd TEXT, summary TEXT, updated_at TEXT)"
    )
    connection.execute(
        "CREATE TABLE IF NOT EXISTS turns ("
        "session_id TEXT, turn_index INTEGER, user_message TEXT, assistant_response TEXT)"
    )
    connection.execute(
        "INSERT INTO sessions (id, cwd, summary, updated_at) VALUES (?, ?, ?, ?)",
        (session_id, cwd, summary, "2026-10-24T22:30:00.000Z"),
    )
    for index_no, (user_message, assistant) in enumerate(turns or []):
        connection.execute(
            "INSERT INTO turns (session_id, turn_index, user_message, assistant_response) "
            "VALUES (?, ?, ?, ?)",
            (session_id, index_no, user_message, assistant),
        )
    connection.commit()
    connection.close()
    folder = root / "session-state" / session_id
    folder.mkdir(parents=True, exist_ok=True)
    if events is not None:
        (folder / "events.jsonl").write_text(
            "\n".join(json.dumps(event) for event in events) + "\n",
            encoding="utf-8",
        )
    if index is not None:
        checkpoint = folder / "checkpoints"
        checkpoint.mkdir()
        (checkpoint / "index.md").write_text(index, encoding="utf-8")
    return folder


def _copilot_bytes(root: Path, session_id: str) -> tuple[bytes, bytes, bytes]:
    folder = root / "session-state" / session_id
    index = folder / "checkpoints" / "index.md"
    events = folder / "events.jsonl"
    return (
        (root / "session-store.db").read_bytes(),
        events.read_bytes() if events.is_file() else b"",
        index.read_bytes() if index.is_file() else b"",
    )


def _write_export_transcript(
    root: Path,
    *,
    transcript_id: str,
    query: str,
    reply: str,
    workspace: str,
) -> tuple[Path, Path]:
    project = root / "demo"
    project.mkdir(parents=True, exist_ok=True)
    trusted = project / ".workspace-trusted"
    trusted.write_text(json.dumps({"workspacePath": workspace}), encoding="utf-8")
    folder = project / "agent-transcripts" / transcript_id
    folder.mkdir(parents=True)
    path = folder / f"{transcript_id}.jsonl"
    lines = [
        {
            "role": "user",
            "message": {
                "content": [{"type": "text", "text": f"<user_query>\n{query}\n</user_query>"}]
            },
        },
        {
            "role": "assistant",
            "message": {"content": [{"type": "text", "text": reply}]},
        },
    ]
    path.write_text("\n".join(json.dumps(line) for line in lines) + "\n", encoding="utf-8")
    return path, trusted


class Terminal(io.StringIO):
    def isatty(self) -> bool:
        return True


if __name__ == "__main__":
    unittest.main()
