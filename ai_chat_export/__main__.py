"""Command line entry for ai-chat-export."""

from __future__ import annotations

import argparse
import json
import sys
import threading
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

_FRAMES = ("...", "..", ".")


class activity:
    """Cycle `...`, `..`, and `.` on a terminal while quiet work runs."""

    def __init__(self, stream, interval: float = 0.2) -> None:
        self.stream = stream
        self.interval = interval
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._shown = False

    def __enter__(self) -> activity:
        isatty = getattr(self.stream, "isatty", None)
        if not callable(isatty) or not isatty():
            return self
        self._shown = True
        self.stream.write("\n" + _FRAMES[0])
        self.stream.flush()
        self._thread = threading.Thread(target=self._spin, daemon=True)
        self._thread.start()
        return self

    def _spin(self) -> None:
        index = 1
        while not self._stop.wait(self.interval):
            frame = _FRAMES[index % len(_FRAMES)]
            index += 1
            self.stream.write("\r" + frame.ljust(len(_FRAMES[0])))
            self.stream.flush()

    def __exit__(self, *exc: object) -> bool:
        if not self._shown:
            return False
        self._stop.set()
        if self._thread is not None:
            self._thread.join()
        self.stream.write("\r" + " " * len(_FRAMES[0]) + "\r")
        self.stream.flush()
        return False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="ai-chat-export",
        description=(
            "Export a Cursor agent session to HTML. Pass --markdown to write Markdown instead. "
            "In the picker, Enter asks for a file name. The title file name is the default."
        ),
    )
    parser.add_argument("--id", dest="chat_id", help="Chat id to export. Omit to open the picker.")
    parser.add_argument(
        "--theme",
        choices=("terminal-dark", "terminal-light", "dark-web", "light-web"),
        default="terminal-dark",
        help="HTML theme written into the file (default: terminal-dark).",
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
        help="Write a Markdown file instead of the HTML page.",
    )
    parser.add_argument("--out", type=Path, help="Directory for the export files.")
    parser.add_argument(
        "--name",
        type=Path,
        help="File path to write when --id is set, including the directory and extension. Replaces --out. Requires --id.",
    )
    parser.add_argument(
        "--chats-root",
        type=Path,
        help="Catalog root. Defaults to ~/.cursor/chats.",
    )
    args = parser.parse_args(argv)
    if args.name is not None and not args.chat_id:
        print("`--name` requires `--id`.", file=sys.stderr)
        return 1
    if args.name is not None and args.out is not None:
        print("Pass either --name or --out.", file=sys.stderr)
        return 1
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
            output_path=args.name,
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
                extension=".md" if args.markdown else ".html",
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
            file_name=result.file_name,
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
            result = run_picker(
                chats,
                theme,
                keys,
                launch_dir,
                frames.append,
                extension=".md" if write_markdown else ".html",
            )
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
            file_name=result.file_name,
            stdout=stdout,
        )

    return call_with_restore(body, teardown, setup)


def export_session(
    *,
    chats_root: Path,
    chat_id: str,
    out_dir: Path,
    theme: str = "terminal-dark",
    verbose: bool = False,
    show_tools: bool = False,
    show_detail: bool = False,
    write_markdown: bool = False,
    file_name: str | None = None,
    output_path: Path | None = None,
    stdout=None,
    stderr=None,
    activity_interval: float = 0.2,
) -> int:
    output = stdout or sys.stdout
    error = stderr or sys.stderr
    if output_path is not None:
        named_error = _named_output_error(output_path)
        if named_error is not None:
            print(named_error, file=error)
            return 1
    warnings: list[str] = []
    with activity(error, activity_interval):
        chats = load_catalog(chats_root, warnings)
    for note in warnings:
        print(note, file=error)
    failure: str | None = None
    html_path: Path | None = None
    md_path: Path | None = None
    with activity(error, activity_interval):
        chat = next((item for item in chats if item.id == chat_id), None)
        if chat is None:
            failure = f"Chat not found: {chat_id}"
        elif not chat.has_store:
            failure = f"Chat has no transcript: {chat_id}"
        else:
            try:
                conversation = load_conversation(chat.path / "store.db")
            except (OSError, ValueError, KeyError) as exc:
                failure = f"Chat has no transcript: {chat_id} ({exc})"
            else:
                if not conversation.messages:
                    failure = f"Chat has no transcript: {chat_id}"
                else:
                    transcript = build_transcript(
                        conversation.messages,
                        _prompts(chat.path),
                        verbose=verbose,
                        show_tools=show_tools,
                        show_detail=show_detail,
                        skipped=conversation.skipped,
                        unlinked_images=conversation.unlinked_images,
                    )
                    document = {
                        "title": chat.display_title,
                        "workspace": chat.workspace_name,
                        "timestamp": chat.updated_label,
                    }
                    if output_path is not None:
                        target = output_path
                    else:
                        if file_name:
                            stem_name = file_name
                        else:
                            suffix = ".md" if write_markdown else ".html"
                            stem_name = f"{safe_stem(chat.title, chat.id)}{suffix}"
                        out_dir.mkdir(parents=True, exist_ok=True)
                        target = out_dir / stem_name
                    target.parent.mkdir(parents=True, exist_ok=True)
                    if write_markdown:
                        md_path = target
                        md_path.write_text(
                            render_markdown(transcript, **document),
                            encoding="utf-8",
                        )
                    else:
                        html_path = target
                        html_path.write_text(
                            render_html(transcript, theme=theme, **document),
                            encoding="utf-8",
                        )
    if failure is not None:
        print(failure, file=error)
        return 1
    if write_markdown:
        assert md_path is not None
        print(md_path.resolve(), file=output)
    else:
        assert html_path is not None
        print(html_path.resolve(), file=output)
    return 0


def _named_output_error(path: Path) -> str | None:
    if not path.name or path.name in {".", ".."}:
        return f"Output path has no file name: {path}"
    if path.exists() and path.is_dir():
        return f"Output path is a directory: {path}"
    return None


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
