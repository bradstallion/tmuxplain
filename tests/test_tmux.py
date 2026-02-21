"""Tests for tmuxplain.tmux (subprocess layer)."""
from __future__ import annotations

import subprocess
from unittest.mock import MagicMock, patch

import pytest

import tmuxplain.tmux as tmux_ops


# ── is_installed ──────────────────────────────────────────────────────────────

def test_is_installed_true():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        assert tmux_ops.is_installed() is True


def test_is_installed_false():
    with patch("shutil.which", return_value=None):
        assert tmux_ops.is_installed() is False


# ── _format_ts ────────────────────────────────────────────────────────────────

def test_format_ts_valid():
    result = tmux_ops._format_ts("0")
    assert result  # any non-empty string
    assert "-" in result  # looks like a date


def test_format_ts_invalid():
    assert tmux_ops._format_ts("not-a-number") == "not-a-number"


# ── list_sessions ─────────────────────────────────────────────────────────────

_FAKE_LS_OUTPUT = "alpha|2|1700000000|1\nbeta|1|1699000000|0\n"


def _mock_run_ls(args, **kwargs):
    m = MagicMock()
    m.returncode = 0
    m.stdout = _FAKE_LS_OUTPUT
    return m


def test_list_sessions_returns_sessions():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        with patch("tmuxplain.tmux._run", side_effect=_mock_run_ls):
            sessions = tmux_ops.list_sessions()
    assert len(sessions) == 2
    names = [s.name for s in sessions]
    assert "alpha" in names
    assert "beta" in names


def test_list_sessions_attached_flag():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        with patch("tmuxplain.tmux._run", side_effect=_mock_run_ls):
            sessions = {s.name: s for s in tmux_ops.list_sessions()}
    assert sessions["alpha"].attached is True
    assert sessions["beta"].attached is False


def test_list_sessions_sort_name():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        with patch("tmuxplain.tmux._run", side_effect=_mock_run_ls):
            sessions = tmux_ops.list_sessions(sort="name")
    assert sessions[0].name == "alpha"
    assert sessions[1].name == "beta"


def test_list_sessions_sort_attached():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        with patch("tmuxplain.tmux._run", side_effect=_mock_run_ls):
            sessions = tmux_ops.list_sessions(sort="attached")
    assert sessions[0].attached is True


def test_list_sessions_tmux_not_installed():
    with patch("shutil.which", return_value=None):
        assert tmux_ops.list_sessions() == []


def test_list_sessions_tmux_error():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        m = MagicMock()
        m.returncode = 1
        m.stdout = ""
        with patch("tmuxplain.tmux._run", return_value=m):
            assert tmux_ops.list_sessions() == []


# ── kill_session ──────────────────────────────────────────────────────────────

def test_kill_session_success():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        m = MagicMock(returncode=0)
        with patch("tmuxplain.tmux._run", return_value=m):
            assert tmux_ops.kill_session("mysession") is True


def test_kill_session_failure():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        m = MagicMock(returncode=1)
        with patch("tmuxplain.tmux._run", return_value=m):
            assert tmux_ops.kill_session("mysession") is False


# ── rename_session ────────────────────────────────────────────────────────────

def test_rename_session_success():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        m = MagicMock(returncode=0)
        with patch("tmuxplain.tmux._run", return_value=m):
            assert tmux_ops.rename_session("old", "new") is True


# ── new_session ───────────────────────────────────────────────────────────────

def test_new_session_success():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        m = MagicMock(returncode=0)
        with patch("tmuxplain.tmux._run", return_value=m):
            assert tmux_ops.new_session("test") is True


# ── list_windows ──────────────────────────────────────────────────────────────

_FAKE_WINDOWS = "0|editor|1|2\n1|shell|0|1\n"


def test_list_windows():
    with patch("shutil.which", return_value="/usr/bin/tmux"):
        m = MagicMock(returncode=0, stdout=_FAKE_WINDOWS)
        with patch("tmuxplain.tmux._run", return_value=m):
            windows = tmux_ops.list_windows("mysession")
    assert len(windows) == 2
    assert windows[0].name == "editor"
    assert windows[0].active is True
    assert windows[1].active is False


# ── attach_command ────────────────────────────────────────────────────────────

def test_attach_command_outside_tmux(monkeypatch):
    monkeypatch.delenv("TMUX", raising=False)
    cmd = tmux_ops.attach_command("mysession")
    assert cmd == ["tmux", "attach-session", "-t", "mysession"]


def test_attach_command_inside_tmux(monkeypatch):
    monkeypatch.setenv("TMUX", "/tmp/tmux-1000/default,12345,0")
    cmd = tmux_ops.attach_command("mysession")
    assert cmd == ["tmux", "switch-client", "-t", "mysession"]
