"""All tmux subprocess interactions — no UI logic here."""
from __future__ import annotations

import datetime
import os
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional


@dataclass
class TmuxSession:
    name: str
    windows: int
    created: str
    attached: bool


@dataclass
class TmuxWindow:
    index: int
    name: str
    active: bool
    panes: int


def is_installed() -> bool:
    return shutil.which("tmux") is not None


def _run(args: list[str], timeout: int = 5) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _format_ts(ts_str: str) -> str:
    try:
        dt = datetime.datetime.fromtimestamp(int(ts_str))
        return dt.strftime("%Y-%m-%d %H:%M")
    except (ValueError, OSError, OverflowError):
        return ts_str


def list_sessions(sort: str = "name") -> list[TmuxSession]:
    if not is_installed():
        return []
    try:
        res = _run([
            "tmux", "list-sessions", "-F",
            "#{session_name}|#{session_windows}|#{session_created}|#{session_attached}",
        ])
        if res.returncode != 0:
            return []
        sessions: list[TmuxSession] = []
        for line in res.stdout.strip().splitlines():
            parts = line.split("|")
            if len(parts) != 4:
                continue
            name, windows, created, attached = parts
            sessions.append(TmuxSession(
                name=name,
                windows=int(windows),
                created=_format_ts(created),
                attached=attached == "1",
            ))
        if sort == "date":
            sessions.sort(key=lambda s: s.created)
        elif sort == "attached":
            sessions.sort(key=lambda s: (not s.attached, s.name.lower()))
        else:
            sessions.sort(key=lambda s: s.name.lower())
        return sessions
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def kill_session(name: str) -> bool:
    if not is_installed():
        return False
    try:
        res = _run(["tmux", "kill-session", "-t", name])
        return res.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def rename_session(old_name: str, new_name: str) -> bool:
    if not is_installed():
        return False
    try:
        res = _run(["tmux", "rename-session", "-t", old_name, new_name])
        return res.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def new_session(name: str) -> bool:
    if not is_installed():
        return False
    try:
        res = _run(["tmux", "new-session", "-d", "-s", name])
        return res.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return False


def capture_pane(session: str) -> str:
    """Return the visible content of the first pane of *session*."""
    if not is_installed():
        return ""
    try:
        # Try with ANSI escape codes first
        res = _run(["tmux", "capture-pane", "-t", session, "-p", "-e"])
        if res.returncode == 0:
            return res.stdout
        # Fallback: plain text
        res = _run(["tmux", "capture-pane", "-t", session, "-p"])
        return res.stdout if res.returncode == 0 else ""
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return ""


def list_windows(session: str) -> list[TmuxWindow]:
    if not is_installed():
        return []
    try:
        res = _run([
            "tmux", "list-windows", "-t", session, "-F",
            "#{window_index}|#{window_name}|#{window_active}|#{window_panes}",
        ])
        if res.returncode != 0:
            return []
        windows: list[TmuxWindow] = []
        for line in res.stdout.strip().splitlines():
            parts = line.split("|")
            if len(parts) != 4:
                continue
            index, name, active, panes = parts
            windows.append(TmuxWindow(
                index=int(index),
                name=name,
                active=active == "1",
                panes=int(panes),
            ))
        return windows
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return []


def attach_command(target: str) -> list[str]:
    """Return the correct tmux command to attach to *target* (session or session:window)."""
    if os.environ.get("TMUX"):
        return ["tmux", "switch-client", "-t", target]
    return ["tmux", "attach-session", "-t", target]
