import json
import os
import sqlite3
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from ai_chat_export.catalog import (
    SESSION_SOURCES,
    Chat,
    column_label,
    filter_workspace,
    format_datetime,
    format_timestamp,
    load_catalog,
)
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

    def test_copilot_column_label(self):
        self.assertEqual([item.id for item in SESSION_SOURCES], ["cli", "ide", "cp-cli"])
        self.assertEqual(column_label("cli"), "Cu-CLI")
        self.assertEqual(column_label("ide"), "Cu-IDE")
        chat = Chat(
            id="cp-1",
            title="Map",
            cwd="C:/work",
            workspace_name="work",
            updated_at_ms=0,
            has_store=True,
            path=Path("."),
            source="cp-cli",
        )
        self.assertEqual(chat.source, "cp-cli")
        self.assertEqual(chat.source_label, "Cp-CLI")

    def test_copilot_session_joins_the_list(self):
        write_chat(
            self.root / "chats",
            chat_id="cli-chat",
            cwd=str(self.root),
            title="Older chat",
            updated_ms=1_000,
            with_store=False,
        )
        launch = self.root / "SoggyMapMaker"
        moment = datetime(2026, 10, 24, 22, 30, tzinfo=timezone.utc)
        _write_copilot(
            self.root / "copilot",
            session_id="cp-chat",
            summary="River map",
            cwd=str(launch),
            updated_at="2026-10-24T22:30:00.000Z",
            user_message="River map",
        )
        orphan = self.root / "copilot" / "session-state" / "orphan"
        orphan.mkdir(parents=True)
        sessions = load_sessions(
            self.root / "chats",
            self.root / "missing-projects",
            copilot_root=self.root / "copilot",
        )
        self.assertEqual([item.id for item in sessions], ["cp-chat", "cli-chat"])
        copilot = sessions[0]
        self.assertEqual(copilot.source_label, "Cp-CLI")
        self.assertEqual(copilot.title, "River map")
        self.assertEqual(copilot.workspace_name, "SoggyMapMaker")
        self.assertEqual(copilot.updated_label, format_timestamp(int(moment.timestamp() * 1000)))
        self.assertEqual(filter_workspace(sessions, str(launch)), [copilot])
        self.assertNotIn("orphan", [item.id for item in sessions])

    def test_missing_copilot_root_keeps_chats(self):
        write_chat(
            self.root / "chats",
            chat_id="cli-chat",
            cwd=str(self.root),
            title="Kept",
            with_store=False,
        )
        sessions = load_sessions(
            self.root / "chats",
            self.root / "missing-projects",
            copilot_root=self.root / "missing-copilot",
        )
        self.assertEqual([item.id for item in sessions], ["cli-chat"])

    def test_custom_copilot_root_is_the_one_that_is_read(self):
        _write_copilot(self.root / "left", session_id="from-left", summary="Left")
        _write_copilot(self.root / "right", session_id="from-right", summary="Right")
        sessions = load_sessions(
            self.root / "missing-chats",
            self.root / "missing-projects",
            copilot_root=self.root / "right",
        )
        self.assertEqual([item.id for item in sessions], ["from-right"])

    def test_copilot_id_stays_beside_the_agent_chat(self):
        write_chat(
            self.root / "chats",
            chat_id="same",
            cwd=str(self.root),
            title="Chat copy",
            with_store=False,
        )
        _write_copilot(self.root / "copilot", session_id="same", summary="Copilot copy")
        sessions = load_sessions(
            self.root / "chats",
            self.root / "missing-projects",
            copilot_root=self.root / "copilot",
        )
        self.assertEqual(sorted(item.source for item in sessions), ["cli", "cp-cli"])
        copilot = next(item for item in sessions if item.source == "cp-cli")
        self.assertEqual(copilot.source_label, "Cp-CLI")

    def test_copilot_title_falls_back_to_the_user_line_then_the_id(self):
        _write_copilot(
            self.root / "copilot",
            session_id="from-line",
            summary="  ",
            user_message="First line\nsecond",
        )
        _write_copilot(self.root / "copilot", session_id="from-id", summary="", user_message="  ")
        sessions = {
            item.id: item
            for item in load_sessions(
                self.root / "missing-chats",
                copilot_root=self.root / "copilot",
            )
        }
        self.assertEqual(sessions["from-line"].title, "First line")
        self.assertIsNone(sessions["from-id"].title)
        self.assertEqual(sessions["from-id"].display_title, "from-id")

    def test_copilot_unparsed_time_and_missing_workspace(self):
        _write_copilot(
            self.root / "copilot",
            session_id="loose",
            summary="Loose",
            cwd="",
            updated_at="not a time",
        )
        sessions = load_sessions(
            self.root / "missing-chats",
            copilot_root=self.root / "copilot",
        )
        self.assertEqual(sessions[0].updated_label, "not a time")
        self.assertEqual(sessions[0].workspace_name, "")
        self.assertEqual(filter_workspace(sessions, str(self.root)), [])

    def test_unreadable_copilot_store_is_omitted_and_named(self):
        write_chat(
            self.root / "chats",
            chat_id="cli-chat",
            cwd=str(self.root),
            title="Kept",
            with_store=False,
        )
        bad = self.root / "bad-copilot"
        bad.mkdir()
        (bad / "session-store.db").write_text("not a database", encoding="utf-8")
        warnings: list[str] = []
        sessions = load_sessions(
            self.root / "chats",
            self.root / "missing-projects",
            warnings,
            bad,
        )
        self.assertEqual([item.id for item in sessions], ["cli-chat"])
        self.assertTrue(any(note.startswith("Unreadable Copilot store:") for note in warnings))


def _write_copilot(
    root: Path,
    *,
    session_id: str,
    summary: str = "",
    cwd: str = "",
    updated_at: str = "2026-01-01T00:00:00.000Z",
    user_message: str | None = None,
    assistant: str | None = None,
) -> None:
    root.mkdir(parents=True, exist_ok=True)
    database = root / "session-store.db"
    fresh = not database.exists()
    connection = sqlite3.connect(database)
    if fresh:
        connection.execute(
            "CREATE TABLE sessions (id TEXT, cwd TEXT, summary TEXT, updated_at TEXT)"
        )
        connection.execute(
            "CREATE TABLE turns ("
            "session_id TEXT, turn_index INTEGER, user_message TEXT, assistant_response TEXT)"
        )
    connection.execute(
        "INSERT INTO sessions (id, cwd, summary, updated_at) VALUES (?, ?, ?, ?)",
        (session_id, cwd, summary, updated_at),
    )
    if user_message is not None:
        connection.execute(
            "INSERT INTO turns (session_id, turn_index, user_message, assistant_response) "
            "VALUES (?, ?, ?, ?)",
            (session_id, 0, user_message, assistant),
        )
    connection.commit()
    connection.close()
    (root / "session-state" / session_id).mkdir(parents=True, exist_ok=True)


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
