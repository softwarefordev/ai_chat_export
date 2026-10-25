import contextlib
import io
import sys
import tempfile
import types
import unittest
from datetime import datetime
from pathlib import Path
from unittest import mock

from ai_chat_export.__main__ import export_with_picker
from ai_chat_export.catalog import Chat, load_catalog
from ai_chat_export.picker import (
    SOURCE_WIDTH,
    TIME_WIDTH,
    render_frame,
    run_picker,
    teardown_terminal,
)
from tests.support import sample_messages, write_chat


def _chat(title: str, workspace: str, chat_id: str, moment: datetime, source: str = "cli") -> Chat:
    return Chat(
        id=chat_id,
        title=title,
        cwd=workspace,
        workspace_name=workspace,
        updated_at_ms=int(moment.timestamp() * 1000),
        has_store=True,
        path=Path("."),
        source=source,
    )


class PickerTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.launch = self.root / "SoggyMapMaker"
        self.other = self.root / "SpiralBench"
        self.launch.mkdir()
        self.other.mkdir()
        self.chats_root = self.root / "chats"
        moment = datetime(2026, 8, 15, 16, 42)
        newer = int(moment.timestamp() * 1000)
        messages, prompts = sample_messages()
        write_chat(
            self.chats_root,
            chat_id="here",
            cwd=str(self.launch),
            title="Fantasy Map Maker",
            updated_ms=newer,
            messages=messages,
            prompts=prompts,
        )
        write_chat(
            self.chats_root,
            chat_id="there",
            cwd=str(self.other),
            title="Apply Opsx",
            updated_ms=newer - 1000,
            messages=messages,
            prompts=prompts,
        )
        self.chats = load_catalog(self.chats_root)

    def tearDown(self):
        self.tmp.cleanup()

    def _frames(self, keys, theme="terminal-dark", width=80, extension=".html", sources=None):
        frames: list[str] = []
        result = run_picker(
            self.chats,
            theme,
            keys,
            str(self.launch),
            frames.append,
            width=width,
            extension=extension,
            sources=sources,
        )
        return result, frames

    def test_columns_share_workspace_and_time_at_an_explicit_width(self):
        width = 72
        short = _chat("Map", "SoggyMapMaker", "short", datetime(2026, 9, 1, 9, 5), source="ide")
        long_title = _chat("T" * 80, "SpiralBench", "long", datetime(2026, 8, 15, 16, 42))
        frame = render_frame([long_title, short], 0, "all", "terminal-dark", width=width)
        lines = frame.splitlines()
        header, source, rule, first, second = lines[0], lines[1], lines[2], lines[3], lines[4]
        self.assertEqual(rule, "-" * width)
        self.assertIn("All sources", source)
        self.assertEqual(lines[-3], "-" * width)
        self.assertEqual(len(header), width)
        self.assertEqual(header[-TIME_WIDTH:], "Last updated".rjust(TIME_WIDTH))
        self.assertTrue(first.startswith("> "))
        self.assertTrue(second.startswith("  "))
        self.assertFalse(second.startswith(">"))
        self.assertTrue(first.split("  ", 1)[0].endswith("..."))
        self.assertEqual(first[-TIME_WIDTH:], long_title.updated_label.rjust(TIME_WIDTH))
        self.assertEqual(second[-TIME_WIDTH:], short.updated_label.rjust(TIME_WIDTH))
        self.assertNotEqual(len(long_title.updated_label), len(short.updated_label))
        workspace_at = first.index("SpiralBench")
        self.assertEqual(second.index("SoggyMapMaker"), workspace_at)
        self.assertLess(workspace_at, width - TIME_WIDTH)
        source_at = first.index("Cu-CLI")
        self.assertEqual(first[source_at : source_at + SOURCE_WIDTH], "Cu-CLI")
        self.assertEqual(second.index("Cu-IDE"), source_at)
        self.assertLess(workspace_at, source_at)
        self.assertLess(source_at, width - TIME_WIDTH)

        wide_workspace = _chat("Title", "W" * 40, "wide", datetime(2026, 8, 15, 16, 42))
        wide = render_frame([wide_workspace], 0, "workspace", "terminal-dark", width=width)
        row = wide.splitlines()[3]
        cell = row[-(TIME_WIDTH + 2 + SOURCE_WIDTH + 2 + 24) : -(TIME_WIDTH + 2 + SOURCE_WIDTH + 2)]
        self.assertEqual(cell, ("W" * 21) + "...")
        self.assertIn("This workspace *", wide.splitlines()[0])

    def test_movement_scope_enter_esc_and_backspace(self):
        result, frames = self._frames(["down", "up", "enter"])
        self.assertIsNone(result.chat_id)
        self.assertIn("> Fantasy Map Maker", frames[-1])
        self.assertIn("theme: terminal-dark", frames[-1])
        name = "file: Fantasy Map Maker.html"
        self.assertIn(name, frames[-1])
        self.assertNotIn(name + "_", frames[-1])
        self.assertIn(f";{len(name) + 1}H", frames[-1])
        self.assertIn("\x1b[1 q", frames[-1])
        self.assertIn("\x1b[?25h", frames[-1])
        self.assertIn("\x1b[?25l", frames[0])
        self.assertNotIn("\x1b[1 q", frames[0])
        self.assertIn("type to edit", frames[-1])
        self.assertIn("Enter names the file", frames[0])

        result, frames = self._frames(["enter", "down"])
        self.assertIn("> Fantasy Map Maker", frames[-1])
        self.assertNotIn("> Apply Opsx", frames[-1])

        result, frames = self._frames(["enter", "esc"])
        self.assertIsNone(result.chat_id)
        self.assertIn("> Fantasy Map Maker", frames[-1])
        self.assertNotIn("type to edit", frames[-1])
        self.assertNotIn("file:", frames[-1])
        self.assertIn("\x1b[?25l", frames[-1])
        self.assertNotIn("\x1b[1 q", frames[-1])

        _, frames = self._frames(["i", "enter"])
        text = frames[-1]
        self.assertLess(text.index("id: here"), text.index("file: "))

        long_keys = ["enter", *["x"] * 90]
        _, frames = self._frames(long_keys, width=80)
        lines = frames[-1].splitlines()
        hint = "type to edit   Enter writes   Esc returns"
        name = lines[lines.index(hint) - 1]
        self.assertEqual(len(name), 79)
        self.assertTrue(name.endswith("x"))
        self.assertIn(";80H", frames[-1])
        self.assertIn("\x1b[1 q", frames[-1])
        self.assertIn("> Fantasy Map Maker", frames[-1])
        self.assertIn("-" * 80, frames[-1])

        result, frames = self._frames(["down", "up", "enter", "enter"])
        self.assertEqual(result.chat_id, "here")
        self.assertEqual(result.file_name, "Fantasy Map Maker.html")

        result, frames = self._frames(["down", "enter"])
        self.assertIsNone(result.chat_id)
        self.assertIn("Apply Opsx.html", frames[-1])

        result, frames = self._frames(["down", "enter"], extension=".md")
        self.assertIn("Apply Opsx.md", frames[-1])

        result, frames = self._frames(["right"])
        self.assertIsNone(result.chat_id)
        self.assertIn("This workspace *", frames[-1])
        self.assertIn("Fantasy Map Maker", frames[-1])
        self.assertNotIn("Apply Opsx", frames[-1])

        result, frames = self._frames(["esc"])
        self.assertIsNone(result.chat_id)
        self.assertIn("theme: terminal-dark", frames[-1])

        result, frames = self._frames(["backspace", "esc"], theme="terminal-light")
        self.assertIsNone(result.chat_id)
        self.assertFalse(result.delete_requested)
        self.assertIn("theme: terminal-light", frames[-1])

    def test_reserved_names_use_the_chat_id(self):
        messages, prompts = sample_messages()
        write_chat(
            self.chats_root,
            chat_id="room-id",
            cwd=str(self.launch),
            title="CON",
            updated_ms=9_000_000_000_000,
            messages=messages,
            prompts=prompts,
        )
        chats = load_catalog(self.chats_root)
        frames: list[str] = []
        run_picker(chats, "terminal-dark", ["enter"], str(self.launch), frames.append, width=80)
        self.assertIn("file: room-id.html", frames[-1])
        self.assertNotIn("file: CON.html", frames[-1])

        default = "Fantasy Map Maker.html"
        keys = ["enter", *["backspace"] * len(default), *"COM1", "enter"]
        out = self.root / "reserved-out"
        out.mkdir()
        stdout = io.StringIO()
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=keys,
            launch_dir=str(self.launch),
            out_dir=out,
            verbose=False,
            chats_root=self.chats_root,
            stdout=stdout,
            setup=lambda: None,
            teardown=lambda: None,
        )
        self.assertEqual(code, 0)
        self.assertTrue((out / "here.html").is_file())
        self.assertFalse((out / "COM1.html").exists())

    def test_footer_shows_the_requested_theme(self):
        for name in ("terminal-light", "dark-web", "light-web"):
            _, frames = self._frames(["esc"], theme=name)
            self.assertIn(f"theme: {name}", frames[-1])

    def test_id_toggle_follows_selection_and_hides_for_an_empty_list(self):
        _, frames = self._frames(["esc"])
        self.assertNotIn("id:", frames[0])
        self.assertIn("i id", frames[0])

        _, frames = self._frames(["i"])
        self.assertNotIn("id:", frames[0])
        self.assertIn("id: here", frames[-1])

        _, frames = self._frames(["i", "i"])
        self.assertNotIn("id:", frames[-1])

        _, frames = self._frames(["I"])
        self.assertIn("id: here", frames[-1])

        _, frames = self._frames(["i", "down"])
        self.assertIn("id: there", frames[-1])
        self.assertNotIn("id: here", frames[-1])

        frames = []
        run_picker([], "terminal-dark", ["i"], str(self.launch), frames.append, width=80)
        self.assertNotIn("id:", frames[-1])
        self.assertIn("i id", frames[-1])

    def test_enter_writes_files_and_esc_writes_none(self):
        out = self.root / "out"
        out.mkdir()
        stdout = io.StringIO()
        restored = []
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=["enter", "enter"],
            launch_dir=str(self.launch),
            out_dir=out,
            verbose=False,
            chats_root=self.chats_root,
            stdout=stdout,
            setup=lambda: restored.append("setup"),
            teardown=lambda: restored.append("teardown"),
        )
        self.assertEqual(code, 0)
        html_path = out / "Fantasy Map Maker.html"
        self.assertTrue(html_path.is_file())
        self.assertFalse((out / "Fantasy Map Maker.md").exists())
        self.assertIn(str(html_path.resolve()), stdout.getvalue())
        self.assertEqual(restored, ["setup", "teardown"])

        marked = self.root / "marked"
        marked.mkdir()
        stdout = io.StringIO()
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=["enter", "enter"],
            launch_dir=str(self.launch),
            out_dir=marked,
            verbose=False,
            write_markdown=True,
            chats_root=self.chats_root,
            stdout=stdout,
            setup=lambda: None,
            teardown=lambda: None,
        )
        md_path = marked / "Fantasy Map Maker.md"
        self.assertEqual(code, 0)
        self.assertTrue(md_path.is_file())
        self.assertFalse((marked / "Fantasy Map Maker.html").exists())
        self.assertIn(str(md_path.resolve()), stdout.getvalue())
        self.assertNotIn("Fantasy Map Maker.html", stdout.getvalue())

        empty = self.root / "empty"
        empty.mkdir()
        stdout = io.StringIO()
        restored.clear()
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=["esc"],
            launch_dir=str(self.launch),
            out_dir=empty,
            verbose=False,
            chats_root=self.chats_root,
            stdout=stdout,
            setup=lambda: restored.append("setup"),
            teardown=lambda: restored.append("teardown"),
        )
        self.assertEqual(code, 0)
        self.assertEqual(list(empty.iterdir()), [])
        self.assertEqual(restored, ["setup", "teardown"])

    def test_edited_cleared_and_cancelled_names(self):
        default = "Fantasy Map Maker.html"
        edited = self.root / "edited"
        edited.mkdir()
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=["enter", *["backspace"] * len(default), *"notes", "enter"],
            launch_dir=str(self.launch),
            out_dir=edited,
            verbose=False,
            chats_root=self.chats_root,
            stdout=io.StringIO(),
            setup=lambda: None,
            teardown=lambda: None,
        )
        self.assertEqual(code, 0)
        self.assertTrue((edited / "notes.html").is_file())
        self.assertFalse((edited / default).exists())

        cleared = self.root / "cleared"
        cleared.mkdir()
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=["enter", *["backspace"] * len(default), "enter"],
            launch_dir=str(self.launch),
            out_dir=cleared,
            verbose=False,
            chats_root=self.chats_root,
            stdout=io.StringIO(),
            setup=lambda: None,
            teardown=lambda: None,
        )
        self.assertEqual(code, 0)
        self.assertTrue((cleared / default).is_file())

        cancelled = self.root / "cancelled"
        cancelled.mkdir()
        stdout = io.StringIO()
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=["enter", "esc", "esc"],
            launch_dir=str(self.launch),
            out_dir=cancelled,
            verbose=False,
            chats_root=self.chats_root,
            stdout=stdout,
            setup=lambda: None,
            teardown=lambda: None,
        )
        self.assertEqual(code, 0)
        self.assertEqual(list(cancelled.iterdir()), [])
        self.assertIn("type to edit", stdout.getvalue())
        self.assertIn("Enter names the file", stdout.getvalue())

        untitled = _chat("", "bench", "bare-id", datetime(2026, 8, 15, 16, 42))
        frames: list[str] = []
        result = run_picker(
            [untitled], "terminal-dark", ["enter"], str(self.launch), frames.append, extension=".html"
        )
        self.assertIsNone(result.chat_id)
        self.assertIn("bare-id.html", frames[-1])

        result = run_picker(
            [untitled],
            "terminal-dark",
            ["enter", *["backspace"] * len("bare-id.html"), *"a/b", "enter"],
            str(self.launch),
            frames.append,
        )
        self.assertEqual(result.file_name, "a b.html")

    def test_interrupt_restores_terminal(self):
        def keys():
            raise KeyboardInterrupt
            yield "enter"

        restored = []
        code = export_with_picker(
            self.chats,
            theme="terminal-dark",
            keys=keys(),
            launch_dir=str(self.launch),
            out_dir=self.root / "unused",
            verbose=False,
            chats_root=self.chats_root,
            stdout=io.StringIO(),
            setup=lambda: restored.append("setup"),
            teardown=lambda: restored.append("teardown"),
        )
        self.assertEqual(code, 130)
        self.assertEqual(restored, ["setup", "teardown"])
        self.assertFalse((self.root / "unused").exists())

    def test_teardown_shows_the_default_cursor(self):
        for saved in (None, object()):
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                teardown_terminal(saved)
            text = stdout.getvalue()
            self.assertIn("\x1b[?25h", text)
            self.assertIn("\x1b[0 q", text)

        termios = types.ModuleType("termios")
        termios.TCSADRAIN = 1
        termios.tcsetattr = mock.Mock()
        stdout = io.StringIO()
        with (
            contextlib.redirect_stdout(stdout),
            mock.patch.dict(sys.modules, {"termios": termios}),
            mock.patch("ai_chat_export.picker.os.name", "posix"),
        ):
            teardown_terminal(["saved-attributes"])
        self.assertIn("\x1b[?25h", stdout.getvalue())
        self.assertIn("\x1b[0 q", stdout.getvalue())
        termios.tcsetattr.assert_called_once_with(sys.stdin.fileno(), 1, ["saved-attributes"])

    def test_source_key_cycles_and_composes_with_workspace(self):
        _, frames = self._frames(["s", "s", "s", "s", "S"])
        self.assertIn("s source", frames[0])
        self.assertIn("i id", frames[0])
        self.assertIn("Enter names the file", frames[0])
        self.assertIn("Copilot-CLI", frames[0])
        self.assertIn("Copilot-IDE", frames[0])
        self.assertIn("All sources *", frames[0])
        self.assertIn("Cursor-CLI *", frames[1])
        self.assertNotIn("All sources *", frames[1])
        self.assertIn("Cursor-IDE *", frames[2])
        self.assertIn("Copilot-CLI *", frames[3])
        self.assertIn("Copilot-IDE *", frames[4])
        self.assertIn("All sources *", frames[5])

        _, flagged = self._frames(["s"], sources={"cli"})
        self.assertIn("Cursor-CLI *", flagged[0])
        self.assertIn("Cursor-IDE *", flagged[-1])

        _, shifted = self._frames(["down", "s"])
        self.assertIn("> Fantasy Map Maker", shifted[-1])
        self.assertNotIn("> Apply Opsx", shifted[-1])

        ide = Chat(
            id="ide-here",
            title="River",
            cwd=str(self.launch),
            workspace_name="SoggyMapMaker",
            updated_at_ms=int(datetime(2026, 9, 1, 9, 5).timestamp() * 1000),
            has_store=True,
            path=self.launch,
            source="ide",
        )
        cli = Chat(
            id="cli-here",
            title="Map",
            cwd=str(self.launch),
            workspace_name="SoggyMapMaker",
            updated_at_ms=int(datetime(2026, 8, 1, 9, 5).timestamp() * 1000),
            has_store=True,
            path=self.launch,
            source="cli",
        )
        elsewhere = Chat(
            id="cli-there",
            title="Bench",
            cwd=str(self.other),
            workspace_name="SpiralBench",
            updated_at_ms=int(datetime(2026, 7, 1, 9, 5).timestamp() * 1000),
            has_store=True,
            path=self.other,
            source="cli",
        )
        mixed: list[str] = []
        run_picker(
            [ide, cli, elsewhere],
            "terminal-dark",
            ["s", "right"],
            str(self.launch),
            mixed.append,
            width=80,
        )
        self.assertIn("Cursor-CLI *", mixed[-1])
        self.assertIn("This workspace *", mixed[-1])
        self.assertIn("> Map", mixed[-1])
        self.assertNotIn("River", mixed[-1])
        self.assertNotIn("Bench", mixed[-1])

        copilot = Chat(
            id="cp-here",
            title="Copilot row",
            cwd=str(self.launch),
            workspace_name="SoggyMapMaker",
            updated_at_ms=int(datetime(2026, 6, 1, 9, 5).timestamp() * 1000),
            has_store=True,
            path=self.launch,
            source="cp-cli",
        )
        copilot_ide = Chat(
            id="cp-ide-here",
            title="Ide copilot",
            cwd=str(self.launch),
            workspace_name="SoggyMapMaker",
            updated_at_ms=int(datetime(2026, 5, 1, 9, 5).timestamp() * 1000),
            has_store=True,
            path=self.launch,
            source="cp-ide",
        )
        subset: list[str] = []
        run_picker(
            [ide, cli, copilot, copilot_ide],
            "terminal-dark",
            ["s"],
            str(self.launch),
            subset.append,
            width=80,
            sources={"cli", "ide"},
        )
        self.assertIn("Cursor-CLI *", subset[0])
        self.assertIn("Cursor-IDE *", subset[0])
        self.assertNotIn("All sources *", subset[0])
        self.assertNotIn("Copilot-CLI *", subset[0])
        self.assertNotIn("Copilot-IDE *", subset[0])
        self.assertNotIn("Copilot row", subset[0])
        self.assertNotIn("Ide copilot", subset[0])
        self.assertIn("All sources *", subset[-1])

        typed, named = self._frames(["enter", "s", "down"])
        self.assertIsNone(typed.chat_id)
        self.assertIn("file: Fantasy Map Maker.htmls", named[-1])
        self.assertIn("All sources *", named[-1])
        self.assertIn("> Fantasy Map Maker", named[-1])

        empty: list[str] = []
        result = run_picker(
            [ide],
            "terminal-dark",
            ["enter"],
            str(self.launch),
            empty.append,
            width=80,
            sources={"cli"},
        )
        self.assertIsNone(result.chat_id)
        self.assertIsNone(result.file_name)
        self.assertIn("(no chats)", empty[-1])

        _, subset = self._frames(["s"], sources={"cli", "later"})
        self.assertIn("All sources *", subset[-1])


if __name__ == "__main__":
    unittest.main()
