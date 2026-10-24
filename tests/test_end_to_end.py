import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from ai_chat_export.__main__ import main
from tests.support import sample_messages, write_chat


class EndToEndTests(unittest.TestCase):
    def test_help_exits_zero(self):
        completed = subprocess.run(
            [sys.executable, "-m", "ai_chat_export", "--help"],
            cwd=Path(__file__).resolve().parents[1],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("usage: ai-chat-export", completed.stdout)
        project = Path(__file__).resolve().parents[1].joinpath("pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('name = "ai-chat-export"', project)
        self.assertIn('ai-chat-export = "ai_chat_export.__main__:main"', project)
        self.assertIn("--theme", completed.stdout)
        self.assertIn("terminal-dark", completed.stdout)
        self.assertIn("terminal-light", completed.stdout)
        self.assertIn("dark-web", completed.stdout)
        self.assertIn("light-web", completed.stdout)
        self.assertIn("default: terminal-", completed.stdout)
        self.assertIn("dark).", completed.stdout)
        self.assertIn("--tools", completed.stdout)
        self.assertIn("--detail", completed.stdout)
        self.assertIn("--markdown", completed.stdout)
        self.assertIn("--name", completed.stdout)
        self.assertIn("asks for a file name", completed.stdout)
        self.assertIn("when --id is set", completed.stdout)
        readme = Path(__file__).resolve().parents[1].joinpath("README.md").read_text(encoding="utf-8")
        self.assertTrue(readme.startswith("# ai-chat-export\n"))
        self.assertIn("ai-chat-export", readme)
        self.assertIn("python -m ai_chat_export", readme)
        self.assertIn("--detail", readme)
        self.assertIn("Cursor command blocks", readme)
        self.assertIn("HTML is the default.", readme)
        self.assertIn("terminal-dark", readme)
        self.assertIn("--theme terminal-light", readme)
        self.assertIn(
            "The list shows the title, workspace, and time in aligned columns.",
            readme,
        )
        self.assertIn("`i` shows the selected chat id.", readme)
        self.assertIn(
            "The HTML page lists user turns, and each entry jumps to that turn.",
            readme,
        )
        self.assertIn("`--markdown` writes the Markdown file", readme)
        self.assertIn("Windows reserved device name", readme)
        self.assertIn("`--name` is written as given.", readme)
        self.assertIn("Enter asks for a file name.", readme)
        self.assertIn("The chat list stays on screen.", readme)
        self.assertIn("`--name` requires `--id`.", readme)
        self.assertNotIn("writes nothing", readme)

    def test_former_theme_names_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            completed = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "ai_chat_export",
                    "--theme",
                    "dark",
                    "--id",
                    "missing",
                    "--chats-root",
                    str(root),
                    "--out",
                    str(root),
                ],
                cwd=root,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(list(root.glob("*.html")), [])
            self.assertNotIn("Chat not found", completed.stderr)

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
