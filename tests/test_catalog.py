import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from ai_chat_export.catalog import filter_workspace, format_datetime, load_catalog
from ai_chat_export.ide import load_sessions
from tests.support import write_chat


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_timestamp_shape(self):
        moment = datetime(2026, 8, 15, 16, 42)
        self.assertEqual(format_datetime(moment), "Aug 15, 2026 04:42 PM")

    def test_titled_chat_workspace_and_time(self):
        moment = datetime(2026, 8, 15, 16, 42)
        cwd = self.root / "SoggyMapMaker"
        cwd.mkdir()
        write_chat(
            self.root / "chats",
            chat_id="chat-new",
            cwd=str(cwd),
            title="Fantasy Map Maker",
            updated_ms=int(moment.timestamp() * 1000),
            messages=[],
            with_store=False,
        )
        chats = load_catalog(self.root / "chats")
        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0].display_title, "Fantasy Map Maker")
        self.assertEqual(chats[0].workspace_name, "SoggyMapMaker")
        self.assertEqual(chats[0].updated_label, "Aug 15, 2026 04:42 PM")

    def test_missing_title_uses_id(self):
        write_chat(
            self.root / "chats",
            chat_id="abc-123",
            cwd=str(self.root),
            include_title=False,
            with_store=False,
        )
        chats = load_catalog(self.root / "chats")
        self.assertEqual(chats[0].display_title, "abc-123")

    def test_newest_first(self):
        base = self.root / "chats"
        write_chat(base, chat_id="older", cwd=str(self.root), title="Older", updated_ms=10, with_store=False)
        write_chat(base, chat_id="newer", cwd=str(self.root), title="Newer", updated_ms=20, with_store=False)
        titles = [chat.display_title for chat in load_catalog(base)]
        self.assertEqual(titles, ["Newer", "Older"])

    def test_unsupported_schema_is_omitted(self):
        write_chat(
            self.root / "chats",
            chat_id="future",
            cwd=str(self.root),
            schema=2,
            with_store=False,
        )
        warnings: list[str] = []
        chats = load_catalog(self.root / "chats", warnings)
        self.assertEqual(chats, [])
        self.assertTrue(any("Unsupported schemaVersion" in note for note in warnings))

    def test_unreadable_metadata_is_omitted(self):
        write_chat(
            self.root / "chats",
            chat_id="broken",
            cwd=str(self.root),
            raw_meta=b"{not json",
            with_store=False,
        )
        warnings: list[str] = []
        chats = load_catalog(self.root / "chats", warnings)
        self.assertEqual(chats, [])
        self.assertTrue(any("Unreadable metadata" in note for note in warnings))

    def test_missing_store_stays_listable(self):
        write_chat(
            self.root / "chats",
            chat_id="meta-only",
            cwd=str(self.root),
            title="Notes",
            with_store=False,
        )
        chats = load_catalog(self.root / "chats")
        self.assertEqual(chats[0].has_store, False)
        self.assertEqual(chats[0].display_title, "Notes")

    def test_this_workspace_keeps_launch_directory(self):
        launch = self.root / "launch"
        other = self.root / "other"
        launch.mkdir()
        other.mkdir()
        base = self.root / "chats"
        write_chat(base, chat_id="here", cwd=str(launch), title="Here", with_store=False)
        write_chat(base, chat_id="there", cwd=str(other), title="There", with_store=False)
        kept = filter_workspace(load_catalog(base), str(launch))
        self.assertEqual([chat.display_title for chat in kept], ["Here"])

    def test_windows_workspace_match_is_case_insensitive(self):
        launch = self.root / "LaunchDir"
        launch.mkdir()
        swapped = "".join(character.lower() if character.isupper() else character.upper() for character in str(launch))
        base = self.root / "chats"
        write_chat(base, chat_id="here", cwd=swapped, title="Here", with_store=False)
        kept = filter_workspace(load_catalog(base), str(launch))
        if sys.platform == "win32":
            self.assertEqual([chat.id for chat in kept], ["here"])
        else:
            self.assertEqual(kept, [])

    def test_ide_transcript_joins_the_chat_list(self):
        moment = datetime(2026, 1, 2, 9, 0)
        write_chat(
            self.root / "chats",
            chat_id="cli-chat",
            cwd=str(self.root),
            title="Older chat",
            updated_ms=int(moment.timestamp() * 1000),
            with_store=False,
        )
        newer = datetime(2026, 6, 1, 9, 0)
        _write_transcript(
            self.root / "projects",
            project="demo",
            transcript_id="ide-chat",
            lines=[_user_line("River map")],
            mtime=newer.timestamp(),
        )
        sessions = load_sessions(self.root / "chats", self.root / "projects")
        self.assertEqual([item.id for item in sessions], ["ide-chat", "cli-chat"])
        self.assertEqual(sessions[0].source, "ide")
        self.assertEqual(sessions[0].source_label, "Cu-IDE")
        self.assertEqual(sessions[1].source, "cli")
        self.assertEqual(sessions[1].source_label, "Cu-CLI")

    def test_missing_projects_root_keeps_chats(self):
        write_chat(
            self.root / "chats",
            chat_id="cli-chat",
            cwd=str(self.root),
            title="Kept",
            with_store=False,
        )
        sessions = load_sessions(self.root / "chats", self.root / "missing-projects")
        self.assertEqual([item.id for item in sessions], ["cli-chat"])
        self.assertEqual(sessions[0].source_label, "Cu-CLI")

    def test_custom_projects_root_is_the_one_that_is_read(self):
        _write_transcript(
            self.root / "left",
            project="demo",
            transcript_id="from-left",
            lines=[_user_line("Left query")],
        )
        _write_transcript(
            self.root / "right",
            project="demo",
            transcript_id="from-right",
            lines=[_user_line("Right query")],
        )
        sessions = load_sessions(self.root / "chats", self.root / "right")
        self.assertEqual([item.id for item in sessions], ["from-right"])

    def test_shared_id_is_listed_once_as_cli(self):
        write_chat(
            self.root / "chats",
            chat_id="same",
            cwd=str(self.root),
            title="From the chat store",
            with_store=False,
        )
        _write_transcript(
            self.root / "projects",
            project="demo",
            transcript_id="same",
            lines=[_user_line("Only in the transcript")],
        )
        sessions = load_sessions(self.root / "chats", self.root / "projects")
        self.assertEqual([item.id for item in sessions], ["same"])
        self.assertEqual(sessions[0].source_label, "Cu-CLI")
        self.assertEqual(sessions[0].display_title, "From the chat store")

    def test_ide_title_is_the_first_query_line(self):
        _write_transcript(
            self.root / "projects",
            project="demo",
            transcript_id="titled",
            lines=[_user_line("River map\nsecond line")],
        )
        sessions = load_sessions(self.root / "missing-chats", self.root / "projects")
        self.assertEqual(sessions[0].display_title, "River map")

    def test_ide_without_a_query_uses_the_id(self):
        payload = {
            "role": "user",
            "message": {"content": [{"type": "text", "text": "<timestamp>Friday</timestamp>"}]},
        }
        _write_transcript(
            self.root / "projects",
            project="demo",
            transcript_id="untitled",
            lines=[json.dumps(payload)],
        )
        sessions = load_sessions(self.root / "missing-chats", self.root / "projects")
        self.assertEqual(sessions[0].display_title, "untitled")
        self.assertIsNone(sessions[0].title)

    def test_ide_time_uses_the_file_stamp(self):
        moment = datetime(2026, 8, 15, 16, 42)
        _write_transcript(
            self.root / "projects",
            project="demo",
            transcript_id="timed",
            lines=[_user_line("River map")],
            mtime=moment.timestamp(),
        )
        sessions = load_sessions(self.root / "missing-chats", self.root / "projects")
        self.assertEqual(sessions[0].updated_label, format_datetime(moment))

    def test_ide_workspace_comes_from_the_trusted_path(self):
        launch = self.root / "SoggyMapMaker"
        launch.mkdir()
        _write_transcript(
            self.root / "projects",
            project="demo",
            transcript_id="placed",
            lines=[_user_line("River map")],
            workspace=str(launch),
        )
        sessions = load_sessions(self.root / "missing-chats", self.root / "projects")
        self.assertEqual(sessions[0].workspace_name, "SoggyMapMaker")
        kept = filter_workspace(sessions, str(launch))
        self.assertEqual([item.id for item in kept], ["placed"])

    def test_missing_workspace_path_stays_out_of_this_workspace(self):
        _write_transcript(
            self.root / "projects",
            project="loose-folder",
            transcript_id="loose",
            lines=[_user_line("River map")],
        )
        sessions = load_sessions(self.root / "missing-chats", self.root / "projects")
        self.assertEqual(sessions[0].workspace_name, "loose-folder")
        self.assertEqual(filter_workspace(sessions, str(self.root)), [])

    def test_unreadable_transcript_is_omitted_and_named(self):
        folder = self.root / "projects" / "demo" / "agent-transcripts" / "broken"
        folder.mkdir(parents=True)
        (folder / "broken.jsonl").write_bytes(b"\xff")
        warnings: list[str] = []
        sessions = load_sessions(self.root / "missing-chats", self.root / "projects", warnings)
        self.assertEqual(sessions, [])
        self.assertTrue(any("broken" in note for note in warnings))


def _user_line(query: str) -> str:
    payload = {
        "role": "user",
        "message": {
            "content": [{"type": "text", "text": f"<user_query>\n{query}\n</user_query>"}]
        },
    }
    return json.dumps(payload)


def _write_transcript(
    root: Path,
    *,
    project: str,
    transcript_id: str,
    lines: list[str],
    workspace: str | None = None,
    mtime: float | None = None,
) -> Path:
    project_dir = root / project
    project_dir.mkdir(parents=True, exist_ok=True)
    if workspace is not None:
        (project_dir / ".workspace-trusted").write_text(
            json.dumps({"workspacePath": workspace}),
            encoding="utf-8",
        )
    folder = project_dir / "agent-transcripts" / transcript_id
    folder.mkdir(parents=True)
    path = folder / f"{transcript_id}.jsonl"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


if __name__ == "__main__":
    unittest.main()
