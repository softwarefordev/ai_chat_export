"""Terminal picker for choosing a chat to export."""

from __future__ import annotations

import os
import shutil
import sys
from collections.abc import Callable
from dataclasses import dataclass

from ai_chat_export.catalog import Chat, filter_workspace
from ai_chat_export.names import clean_stem, export_stem

TIME_WIDTH = 21
WORKSPACE_CAP = 24


@dataclass(frozen=True)
class PickerResult:
    chat_id: str | None
    delete_requested: bool = False
    file_name: str | None = None


def run_picker(
    chats: list[Chat],
    theme: str,
    keys,
    launch_dir: str,
    write,
    rows: int = 20,
    width: int | None = None,
    extension: str = ".html",
) -> PickerResult:
    scope = "all"
    selected = 0
    show_id = False
    naming: Chat | None = None
    draft = ""
    default_name = ""

    def visible() -> list[Chat]:
        if scope == "workspace":
            return filter_workspace(chats, launch_dir)
        return list(chats)

    def paint() -> None:
        nonlocal selected
        shown = visible()
        if shown:
            selected = min(selected, len(shown) - 1)
        else:
            selected = 0
        write(render_frame(shown, selected, scope, theme, rows, width, show_id) + HIDE_CURSOR)

    def paint_name() -> None:
        shown = visible()
        frame = render_frame(shown, selected, scope, theme, rows, width, show_id)
        write(append_name_line(frame, draft, _frame_width(width)))

    paint()
    for key in keys:
        if naming is not None:
            if key == "enter":
                name = confirm_file_name(draft, default_name, extension, naming.id)
                return PickerResult(naming.id, False, name)
            if key == "esc":
                naming = None
                paint()
                continue
            if key == "backspace":
                draft = draft[:-1]
            elif len(key) == 1 and key.isprintable():
                draft += key
            paint_name()
            continue
        shown = visible()
        if key == "up" and shown:
            selected = max(0, selected - 1)
        elif key == "down" and shown:
            selected = min(len(shown) - 1, selected + 1)
        elif key in ("left", "right"):
            scope = "workspace" if scope == "all" else "all"
            selected = 0
        elif key == "backspace":
            pass
        elif key in ("i", "I"):
            show_id = not show_id
        elif key == "esc":
            paint()
            return PickerResult(None, False)
        elif key == "enter":
            shown = visible()
            if not shown:
                return PickerResult(None, False)
            naming = shown[selected]
            default_name = default_file_name(naming, extension)
            draft = default_name
            paint_name()
            continue
        else:
            continue
        paint()
    return PickerResult(None, False)


def render_frame(
    chats: list[Chat],
    selected: int,
    scope: str,
    theme: str,
    rows: int = 20,
    width: int | None = None,
    show_id: bool = False,
) -> str:
    frame_width = _frame_width(width)
    start = 0
    if chats and len(chats) > rows:
        start = min(max(0, selected - rows // 2), len(chats) - rows)
    window = chats[start : start + rows]
    title_width, workspace_width = _column_widths(
        frame_width, [chat.workspace_name for chat in window]
    )
    rule = "-" * frame_width
    lines = [_header(scope, frame_width), rule]
    if not window:
        lines.append("(no chats)")
    for offset, chat in enumerate(window):
        marker = "> " if start + offset == selected else "  "
        lines.append(
            marker
            + _fit(chat.display_title, title_width)
            + "  "
            + _fit(chat.workspace_name, workspace_width)
            + "  "
            + _fit_right(chat.updated_label, TIME_WIDTH)
        )
    count = len(chats)
    index = (selected + 1) if count else 0
    lines.append(rule)
    lines.append(
        f"{index}/{count}  up/down move  left/right scope  Enter names the file  Esc closes  i id"
    )
    lines.append(f"theme: {theme}")
    if show_id and chats and 0 <= selected < len(chats):
        lines.append(f"id: {chats[selected].id}")
    return "\n".join(lines) + "\n"


HIDE_CURSOR = "\x1b[?25l"
SHOW_CURSOR = "\x1b[?25h"
BLOCK_CURSOR = "\x1b[1 q"
DEFAULT_CURSOR = "\x1b[0 q"


def append_name_line(frame: str, draft: str, frame_width: int) -> str:
    body = frame[:-1] if frame.endswith("\n") else frame
    line = f"file: {draft}"
    room = max(frame_width - 1, 0)
    if len(line) > room:
        line = line[-room:] if room else ""
    text = body + f"\n{line}\ntype to edit   Enter writes   Esc returns\n"
    row = len(body.splitlines()) + 1
    column = len(line) + 1
    return f"{text}\x1b[{row};{column}H{BLOCK_CURSOR}{SHOW_CURSOR}"


def default_file_name(chat: Chat, extension: str) -> str:
    return f"{export_stem(chat.title, chat.id)}{extension}"


def confirm_file_name(draft: str, default: str, extension: str, chat_id: str) -> str:
    text = draft.strip()
    if not text:
        return default
    suffix = ""
    lowered = text.lower()
    for candidate in (".html", ".md"):
        if lowered.endswith(candidate):
            suffix = text[-len(candidate) :]
            text = text[: -len(candidate)]
            break
    stem = clean_stem(text)
    if not stem:
        return default
    return f"{export_stem(stem, chat_id)}{suffix or extension}"


def _frame_width(width: int | None) -> int:
    if width is None:
        width = shutil.get_terminal_size().columns
    return max(int(width), 1)


def _column_widths(frame_width: int, workspace_names: list[str]) -> tuple[int, int]:
    longest = max((len(name) for name in workspace_names), default=0)
    workspace = min(WORKSPACE_CAP, longest)
    title = frame_width - 2 - 2 - workspace - 2 - TIME_WIDTH
    if title < 1:
        workspace = max(0, frame_width - 2 - 2 - 1 - 2 - TIME_WIDTH)
        title = max(0, frame_width - 2 - 2 - workspace - 2 - TIME_WIDTH)
    return title, workspace


def _header(scope: str, frame_width: int) -> str:
    if scope == "all":
        left = "All chats *    This workspace"
    else:
        left = "All chats    This workspace *"
    right = "Last updated".rjust(TIME_WIDTH)
    if frame_width <= TIME_WIDTH:
        return right[-frame_width:]
    room = frame_width - TIME_WIDTH
    if len(left) > room:
        left = left[:room]
    return left.ljust(room) + right


def _fit(text: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(text) <= width:
        return text.ljust(width)
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def _fit_right(text: str, width: int) -> str:
    if len(text) <= width:
        return text.rjust(width)
    if width <= 3:
        return text[:width]
    return text[: width - 3] + "..."


def call_with_restore(
    body: Callable[[], int],
    teardown: Callable[[], None],
    setup: Callable[[], None] | None = None,
) -> int:
    if setup is not None:
        setup()
    try:
        return body()
    finally:
        teardown()


def setup_terminal() -> list | None:
    if os.name == "nt":
        return None
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    tty.setcbreak(descriptor)
    return saved


def teardown_terminal(saved: list | None) -> None:
    sys.stdout.write(SHOW_CURSOR + DEFAULT_CURSOR)
    sys.stdout.flush()
    if saved is None or os.name == "nt":
        return
    import termios

    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved)


def read_key() -> str:
    if os.name == "nt":
        import msvcrt

        character = msvcrt.getwch()
        if character in ("\x00", "\xe0"):
            arrows = {"H": "up", "P": "down", "K": "left", "M": "right"}
            return arrows.get(msvcrt.getwch(), "")
        if character == "\r":
            return "enter"
        if character == "\x1b":
            return "esc"
        if character == "\x08":
            return "backspace"
        if character in ("i", "I"):
            return "i"
        if character == "\x03":
            raise KeyboardInterrupt
        if character.isprintable():
            return character
        return ""
    character = sys.stdin.read(1)
    if character == "\x03":
        raise KeyboardInterrupt
    if character in ("\r", "\n"):
        return "enter"
    if character in ("\x7f", "\x08"):
        return "backspace"
    if character == "\x1b":
        following = sys.stdin.read(2)
        arrows = {"[A": "up", "[B": "down", "[D": "left", "[C": "right"}
        return arrows.get(following, "")
    if character in ("i", "I"):
        return "i"
    if character.isprintable():
        return character
    return ""
