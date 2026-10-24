import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from ai_chat_export.catalog import filter_workspace, format_datetime, load_catalog
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


if __name__ == "__main__":
    unittest.main()
