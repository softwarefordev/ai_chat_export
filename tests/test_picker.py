import io
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from session_export.__main__ import export_with_picker
from session_export.catalog import load_catalog
from session_export.picker import run_picker
from tests.support import sample_messages, write_chat


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

    def _frames(self, keys, theme="dark"):
        frames: list[str] = []
        result = run_picker(self.chats, theme, keys, str(self.launch), frames.append)
        return result, frames

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
