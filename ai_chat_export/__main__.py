"""Command line entry for ai-chat-export."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ai_chat_export.catalog import Chat, load_catalog
from ai_chat_export.picker import (
    call_with_restore,
    read_key,
    run_picker,
    setup_terminal,
    teardown_terminal,
)
from ai_chat_export.render_html import render_html
from ai_chat_export.render_md import render_markdown
from ai_chat_export.store import load_conversation
from ai_chat_export.transcript import build_transcript


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-chat-export",
        description="Export a Cursor agent session to HTML. Pass --markdown to also write Markdown.",
    )
    parser.add_argument("--id", dest="chat_id", help="Chat id to export. Omit to open the picker.")
    parser.add_argument(
        "--theme",
        choices=("dark", "light"),
        default="dark",
        help="HTML theme written into the file (default: dark).",
    )
    parser.add_argument(
        "--tools",
        action="store_true",
        help="Include one caption per tool call. Omit raw tool output.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Include system text, injected context, reasoning, tool captions, and raw tool output.",
    )
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Include the conversation summary and Cursor command blocks after the user query.",
    )
    parser.add_argument(
        "--markdown",
        action="store_true",
        help="Also write a Markdown file beside the HTML page.",
    )
    parser.add_argument("--out", type=Path, help="Directory for the export files.")
    parser.add_argument(
        "--chats-root",
        type=Path,
        help="Catalog root. Defaults to ~/.cursor/chats.",
    )
    args = parser.parse_args(argv)
    chats_root = args.chats_root or (Path.home() / ".cursor" / "chats")
    out_dir = args.out or Path.cwd()
    if args.chat_id:
        return export_session(
            chats_root=chats_root,
            chat_id=args.chat_id,
            out_dir=out_dir,
            theme=args.theme,
            verbose=args.verbose,
            show_tools=args.tools,
            show_detail=args.detail,
            write_markdown=args.markdown,
        )
    warnings: list[str] = []
    chats = load_catalog(chats_root, warnings)
    for note in warnings:
        print(note, file=sys.stderr)

    def keys():
        while True:
            key = read_key()
            if key:
                yield key

    def write(frame: str) -> None:
        sys.stdout.write("\x1b[H\x1b[2J")
        sys.stdout.write(frame)
        sys.stdout.flush()

    def body():
        try:
            result = run_picker(
                chats,
                args.theme,
                keys(),
                str(Path.cwd()),
                write,
            )
        except KeyboardInterrupt:
            return 130
        if result.delete_requested or result.chat_id is None:
            return 0
        return export_session(
            chats_root=chats_root,
            chat_id=result.chat_id,
            out_dir=out_dir,
            theme=args.theme,
            verbose=args.verbose,
            show_tools=args.tools,
            show_detail=args.detail,
            write_markdown=args.markdown,
        )

    state: dict[str, object] = {"saved": None}

    def setup() -> None:
        state["saved"] = setup_terminal()

    def teardown() -> None:
        teardown_terminal(state["saved"])

    return call_with_restore(body, teardown, setup)


def export_with_picker(
    chats: list[Chat],
    *,
    theme: str,
    keys,
    launch_dir: str,
    out_dir: Path,
    verbose: bool,
    show_tools: bool = False,
    show_detail: bool = False,
    write_markdown: bool = False,
    chats_root: Path,
    stdout,
    setup,
    teardown,
) -> int:
    def body():
        try:
            frames: list[str] = []
            result = run_picker(chats, theme, keys, launch_dir, frames.append)
            stdout.write("".join(frames))
        except KeyboardInterrupt:
            return 130
        if result.delete_requested or result.chat_id is None:
            return 0
        return export_session(
            chats_root=chats_root,
            chat_id=result.chat_id,
            out_dir=out_dir,
            theme=theme,
            verbose=verbose,
            show_tools=show_tools,
            show_detail=show_detail,
            write_markdown=write_markdown,
            stdout=stdout,
        )

    return call_with_restore(body, teardown, setup)


def export_session(
    *,
    chats_root: Path,
    chat_id: str,
    out_dir: Path,
    theme: str = "dark",
    verbose: bool = False,
    show_tools: bool = False,
    show_detail: bool = False,
    write_markdown: bool = False,
    stdout=None,
    stderr=None,
) -> int:
    output = stdout or sys.stdout
    error = stderr or sys.stderr
    warnings: list[str] = []
    chats = load_catalog(chats_root, warnings)
    for note in warnings:
        print(note, file=error)
    chat = next((item for item in chats if item.id == chat_id), None)
    if chat is None:
        print(f"Chat not found: {chat_id}", file=error)
        return 1
    if not chat.has_store:
        print(f"Chat has no transcript: {chat_id}", file=error)
        return 1
    try:
        conversation = load_conversation(chat.path / "store.db")
    except (OSError, ValueError, KeyError) as exc:
        print(f"Chat has no transcript: {chat_id} ({exc})", file=error)
        return 1
    if not conversation.messages:
        print(f"Chat has no transcript: {chat_id}", file=error)
        return 1
    transcript = build_transcript(
        conversation.messages,
        _prompts(chat.path),
        verbose=verbose,
        show_tools=show_tools,
        show_detail=show_detail,
        skipped=conversation.skipped,
        unlinked_images=conversation.unlinked_images,
    )
    stem = safe_stem(chat.title, chat.id)
    html_path = out_dir / f"{stem}.html"
    md_path = out_dir / f"{stem}.md"
    out_dir.mkdir(parents=True, exist_ok=True)
    document = {
        "title": chat.display_title,
        "workspace": chat.workspace_name,
        "timestamp": chat.updated_label,
    }
    html_path.write_text(
        render_html(transcript, theme=theme, **document),
        encoding="utf-8",
    )
    print(html_path.resolve(), file=output)
    if write_markdown:
        md_path.write_text(render_markdown(transcript, **document), encoding="utf-8")
        print(md_path.resolve(), file=output)
    return 0


def safe_stem(title: str | None, chat_id: str) -> str:
    raw = (title or "").strip() or chat_id
    cleaned = []
    for character in raw:
        if character in '<>:"/\\|?*' or ord(character) < 32:
            cleaned.append(" ")
        else:
            cleaned.append(character)
    stem = " ".join("".join(cleaned).split()).rstrip(" .")
    if not stem:
        return chat_id
    return stem[:80]


def _prompts(chat_dir: Path) -> list[str]:
    path = chat_dir / "prompt_history.json"
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError):
        return []
    if not isinstance(payload, list):
        return []
    return [item for item in payload if isinstance(item, str)]


if __name__ == "__main__":
    sys.exit(main())
