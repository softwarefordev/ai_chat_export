"""Terminal picker for choosing a chat to export."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass

from ai_chat_export.catalog import Chat, filter_workspace

TIME_WIDTH = 21
WORKSPACE_CAP = 24


@dataclass(frozen=True)
class PickerResult:
    chat_id: str | None
    delete_requested: bool = False


def run_picker(
    chats: list[Chat],
    theme: str,
    keys,
    launch_dir: str,
    write,
    rows: int = 20,
    width: int | None = None,
) -> PickerResult:
    scope = "all"
    selected = 0
    show_id = False

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
        write(render_frame(shown, selected, scope, theme, rows, width, show_id))

    paint()
    for key in keys:
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
            paint()
            shown = visible()
            if not shown:
                return PickerResult(None, False)
            return PickerResult(shown[selected].id, False)
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
        f"{index}/{count}  up/down move  left/right scope  Enter exports  Esc closes  i id"
    )
    lines.append(f"theme: {theme}")
    if show_id and chats and 0 <= selected < len(chats):
        lines.append(f"id: {chats[selected].id}")
    return "\n".join(lines) + "\n"


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


def call_with_restore(body, teardown, setup=None):
    if setup is not None:
        setup()
    try:
        return body()
    finally:
        teardown()


def setup_terminal():
    if os.name == "nt":
        return None
    import termios
    import tty

    descriptor = sys.stdin.fileno()
    saved = termios.tcgetattr(descriptor)
    tty.setcbreak(descriptor)
    return saved


def teardown_terminal(saved) -> None:
    if saved is None or os.name == "nt":
        return
    import termios

    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, saved)


def read_key():
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
    return ""
