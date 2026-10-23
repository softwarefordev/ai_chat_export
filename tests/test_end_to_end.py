import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from session_export.__main__ import main
from tests.support import sample_messages, write_chat


class EndToEndTests(unittest.TestCase):
    def test_help_exits_zero(self):
        completed = subprocess.run(
            [sys.executable, "-m", "session_export", "--help"],
            cwd=Path(__file__).resolve().parents[1],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("--theme", completed.stdout)
        self.assertIn("--tools", completed.stdout)
        self.assertIn("--detail", completed.stdout)
        self.assertIn("--markdown", completed.stdout)
        readme = Path(__file__).resolve().parents[1].joinpath("README.md").read_text(encoding="utf-8")
        self.assertIn("--detail", readme)
        self.assertIn("Cursor command blocks", readme)
        self.assertIn("HTML is the default.", readme)
        self.assertIn(
            "The list shows the title, workspace, and time in aligned columns.",
            readme,
        )
        self.assertIn("`i` shows the selected chat id.", readme)
        self.assertIn("`--markdown` also writes a Markdown file", readme)
        self.assertNotIn("writes nothing", readme)

    def test_id_export_of_synthetic_fixture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            messages, prompts = sample_messages()
            write_chat(
                root / "chats",
                chat_id="demo",
                cwd=str(root),
                title="Fantasy Map Maker",
                messages=messages,
                prompts=prompts,
            )
            out = root / "out"
            stdout = io.StringIO()
            with contextlib.redirect_stdout(stdout):
                code = main(
                    [
                        "--id",
                        "demo",
                        "--chats-root",
                        str(root / "chats"),
                        "--out",
                        str(out),
                    ]
                )
            self.assertEqual(code, 0)
            html_path = out / "Fantasy Map Maker.html"
            page = html_path.read_text(encoding="utf-8")
            self.assertIn("Please add a river tool.", page)
            self.assertIn("The river tool lives in tools/river.py.", page)
            self.assertNotIn("http", page.lower())
            self.assertFalse((out / "Fantasy Map Maker.md").exists())
            self.assertIn(str(html_path.resolve()), stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
