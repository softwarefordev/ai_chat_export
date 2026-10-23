import io
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from ai_chat_export.__main__ import export_with_picker
from ai_chat_export.catalog import Chat, load_catalog
from ai_chat_export.picker import TIME_WIDTH, render_frame, run_picker
from tests.support import sample_messages, write_chat


def _chat(title: str, workspace: str, chat_id: str, moment: datetime) -> Chat:
    return Chat(
        id=chat_id,
        title=title,
        cwd=workspace,
        workspace_name=workspace,
        updated_at_ms=int(moment.timestamp() * 1000),
        has_store=True,
        path=Path("."),
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

    def _frames(self, keys, theme="dark", width=80):
        frames: list[str] = []
        result = run_picker(
            self.chats, theme, keys, str(self.launch), frames.append, width=width
        )
        return result, frames

    def test_columns_share_workspace_and_time_at_an_explicit_width(self):
        width = 72
        short = _chat("Map", "SoggyMapMaker", "short", datetime(2026, 9, 1, 9, 5))
        long_title = _chat("T" * 80, "SpiralBench", "long", datetime(2026, 8, 15, 16, 42))
        frame = render_frame([long_title, short], 0, "all", "dark", width=width)
        lines = frame.splitlines()
        header, rule, first, second = lines[0], lines[1], lines[2], lines[3]
        self.assertEqual(rule, "-" * width)
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

        wide_workspace = _chat("Title", "W" * 40, "wide", datetime(2026, 8, 15, 16, 42))
        wide = render_frame([wide_workspace], 0, "workspace", "dark", width=width)
        row = wide.splitlines()[2]
        cell = row[-(TIME_WIDTH + 2 + 24) : -(TIME_WIDTH + 2)]
        self.assertEqual(cell, ("W" * 21) + "...")
        self.assertIn("This workspace *", wide.splitlines()[0])

    def test_movement_scope_enter_esc_and_backspace(self):
        result, frames = self._frames(["down", "up", "enter"])
        self.assertEqual(result.chat_id, "here")
        self.assertFalse(result.delete_requested)
        self.assertIn("> Fantasy Map Maker", frames[-1])
        self.assertIn("theme: dark", frames[-1])

        result, frames = self._frames(["down", "enter"])
        self.assertEqual(result.chat_id, "there")
        self.assertIn("> Apply Opsx", frames[-1])

        result, frames = self._frames(["right"])
        self.assertIsNone(result.chat_id)
        self.assertIn("This workspace *", frames[-1])
        self.assertIn("Fantasy Map Maker", frames[-1])
        self.assertNotIn("Apply Opsx", frames[-1])

        result, frames = self._frames(["esc"])
        self.assertIsNone(result.chat_id)
        self.assertIn("theme: dark", frames[-1])

        result, frames = self._frames(["backspace", "esc"], theme="light")
        self.assertIsNone(result.chat_id)
        self.assertFalse(result.delete_requested)
        self.assertIn("theme: light", frames[-1])

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
        run_picker([], "dark", ["i"], str(self.launch), frames.append, width=80)
        self.assertNotIn("id:", frames[-1])
        self.assertIn("i id", frames[-1])

    def test_enter_writes_files_and_esc_writes_none(self):
        out = self.root / "out"
        out.mkdir()
        stdout = io.StringIO()
        restored = []
        code = export_with_picker(
            self.chats,
            theme="dark",
            keys=["enter"],
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
            theme="dark",
            keys=["enter"],
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
        self.assertIn(str(md_path.resolve()), stdout.getvalue())

        empty = self.root / "empty"
        empty.mkdir()
        stdout = io.StringIO()
        restored.clear()
        code = export_with_picker(
            self.chats,
            theme="dark",
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

    def test_interrupt_restores_terminal(self):
        def keys():
            raise KeyboardInterrupt
            yield "enter"

        restored = []
        code = export_with_picker(
            self.chats,
            theme="dark",
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


if __name__ == "__main__":
    unittest.main()
