"""Textual app — all screens and widgets for tmuxito."""
from __future__ import annotations

from typing import Optional

from rich.text import Text
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, ScrollableContainer
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Input,
    Label,
    MarkdownViewer,
    Static,
)

import tmuxito.tmux as tmux_ops
from tmuxito.config import Config, load_config
from tmuxito.help import HELP_CONTENT


# ── Modal: kill confirmation ──────────────────────────────────────────────────

class KillConfirmScreen(ModalScreen):
    """Ask the user to confirm before killing a session."""

    BINDINGS = [
        Binding("y", "confirm", "Yes"),
        Binding("n", "cancel", "No"),
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, session_name: str) -> None:
        super().__init__()
        self.session_name = session_name

    def compose(self) -> ComposeResult:
        with Container(id="kill-dialog"):
            yield Label(
                f"Kill session [bold red]{self.session_name!r}[/bold red]?",
                id="kill-label",
            )
            with Horizontal(id="kill-buttons"):
                yield Button("Yes  [y]", variant="error", id="btn-yes")
                yield Button("No  [n]", variant="primary", id="btn-no")

    def action_confirm(self) -> None:
        self.dismiss(True)

    def action_cancel(self) -> None:
        self.dismiss(False)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(event.button.id == "btn-yes")


# ── Modal: new session ────────────────────────────────────────────────────────

class NewSessionScreen(ModalScreen):
    """Prompt for a new session name."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def compose(self) -> ComposeResult:
        with Container(id="new-session-dialog"):
            yield Label("New session name:")
            yield Input(placeholder="my-session", id="new-name")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Create", variant="primary", id="btn-create")
                yield Button("Cancel", id="btn-cancel")

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-create":
            self._submit()
        else:
            self.dismiss(None)

    def _submit(self) -> None:
        name = self.query_one("#new-name", Input).value.strip()
        self.dismiss(name or None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Modal: rename session ─────────────────────────────────────────────────────

class RenameSessionScreen(ModalScreen):
    """Prompt for a new name for an existing session."""

    BINDINGS = [Binding("escape", "cancel", "Cancel")]

    def __init__(self, current_name: str) -> None:
        super().__init__()
        self.current_name = current_name

    def compose(self) -> ComposeResult:
        with Container(id="rename-dialog"):
            yield Label(f"Rename [bold]{self.current_name!r}[/bold]:")
            yield Input(value=self.current_name, id="rename-name")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Rename", variant="primary", id="btn-rename")
                yield Button("Cancel", id="btn-cancel")

    def on_input_submitted(self, _: Input.Submitted) -> None:
        self._submit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "btn-rename":
            self._submit()
        else:
            self.dismiss(None)

    def _submit(self) -> None:
        name = self.query_one("#rename-name", Input).value.strip()
        self.dismiss(name if name and name != self.current_name else None)

    def action_cancel(self) -> None:
        self.dismiss(None)


# ── Help screen ───────────────────────────────────────────────────────────────

class HelpScreen(Screen):
    """Full tmux reference displayed with a MarkdownViewer."""

    BINDINGS = [
        Binding("escape", "go_back", "Close"),
        Binding("q", "go_back", "Close", show=False),
        Binding("?", "go_back", "Close", show=False),
    ]

    def compose(self) -> ComposeResult:
        yield MarkdownViewer(
            HELP_CONTENT,
            show_table_of_contents=False,
            id="help-viewer",
        )
        yield Footer()

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ── Window drill-down screen ──────────────────────────────────────────────────

class WindowScreen(Screen):
    """List windows of a selected session; attach directly to a window."""

    BINDINGS = [
        Binding("escape", "go_back", "Back"),
        Binding("q", "go_back", "Back", show=False),
        Binding("enter", "attach_window", "Attach", priority=True),
    ]

    def __init__(self, session_name: str) -> None:
        super().__init__()
        self.session_name = session_name
        self._windows: list[tmux_ops.TmuxWindow] = []

    def compose(self) -> ComposeResult:
        yield Label("", id="win-title")
        yield DataTable(id="win-table", cursor_type="row", zebra_stripes=True)
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#win-title", Label).update(
            f"Session [bold cyan]{self.session_name}[/bold cyan] — Windows  "
            f"([dim]Enter[/dim] attach · [dim]Esc[/dim] back)"
        )
        table = self.query_one("#win-table", DataTable)
        table.add_column("#", key="idx", width=4)
        table.add_column("Name", key="name")
        table.add_column("Active", key="active", width=8)
        table.add_column("Panes", key="panes", width=6)
        self._load_windows()
        table.focus()

    def _load_windows(self) -> None:
        table = self.query_one("#win-table", DataTable)
        table.clear()
        self._windows = tmux_ops.list_windows(self.session_name)
        if not self._windows:
            table.add_row("—", "[dim]No windows found[/dim]", "", "")
            return
        for w in self._windows:
            active = "[bold green]●[/bold green]" if w.active else "○"
            table.add_row(str(w.index), w.name, active, str(w.panes))

    def action_attach_window(self) -> None:
        table = self.query_one("#win-table", DataTable)
        row = table.cursor_row
        if not self._windows or row >= len(self._windows):
            return
        window = self._windows[row]
        self.app.exit(f"{self.session_name}:{window.index}")

    def action_go_back(self) -> None:
        self.app.pop_screen()


# ── Main session screen ───────────────────────────────────────────────────────

class SessionScreen(Screen):
    """Session list with live preview panel and inline search."""

    BINDINGS = [
        Binding("n", "new_session", "New"),
        Binding("r", "rename_session", "Rename"),
        Binding("k", "kill_session", "Kill"),
        Binding("enter", "attach_session", "Attach", priority=True),
        Binding("right", "open_windows", "Windows", priority=True),
        Binding("/", "start_search", "Search", priority=True),
        Binding("s", "cycle_sort", "Sort"),
        Binding("?", "show_help", "Help"),
        Binding("q", "quit_app", "Quit"),
        Binding("R", "refresh", "Refresh", show=False),
    ]

    def __init__(self, config: Config) -> None:
        super().__init__()
        self.config = config
        self._sessions: list[tmux_ops.TmuxSession] = []
        self._visible: list[tmux_ops.TmuxSession] = []
        self._current_sort: str = config.default_sort
        self._search_active: bool = False

    # ── layout ────────────────────────────────────────────────────────────────

    def compose(self) -> ComposeResult:
        yield Input(
            placeholder="Filter: type to search  •  Esc to cancel",
            id="search-bar",
        )
        with Horizontal(id="main-pane"):
            yield DataTable(
                id="session-table",
                cursor_type="row",
                zebra_stripes=True,
            )
            with ScrollableContainer(id="preview-panel"):
                yield Static("", id="preview-content")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#search-bar").display = False

        table = self.query_one("#session-table", DataTable)
        table.add_column("Session", key="name")
        table.add_column("Status", key="status", width=10)
        table.add_column("Win", key="windows", width=4)
        table.add_column("Created", key="created", width=17)

        self._load_sessions()
        self.set_interval(3.0, self._refresh_preview)
        table.focus()

    # ── data helpers ──────────────────────────────────────────────────────────

    def _load_sessions(self) -> None:
        self._sessions = tmux_ops.list_sessions(sort=self._current_sort)
        filter_text = (
            self.query_one("#search-bar", Input).value
            if self._search_active
            else ""
        )
        self._apply_filter(filter_text)

    def _apply_filter(self, text: str) -> None:
        if text:
            self._visible = [
                s for s in self._sessions
                if text.lower() in s.name.lower()
            ]
        else:
            self._visible = list(self._sessions)
        self._rebuild_table()

    def _rebuild_table(self) -> None:
        table = self.query_one("#session-table", DataTable)
        table.clear()

        if not tmux_ops.is_installed():
            table.add_row(
                "[bold red]tmux not installed — please install tmux[/bold red]",
                "", "", "",
            )
            return

        if not self._visible:
            msg = (
                "[dim]No sessions match.[/dim]"
                if self._sessions
                else "[dim]No sessions.  Press [bold]n[/bold] to create one.[/dim]"
            )
            table.add_row(msg, "", "", "")
            return

        for s in self._visible:
            status = (
                "[bold green]attached[/bold green]"
                if s.attached
                else "[dim]detached[/dim]"
            )
            table.add_row(s.name, status, str(s.windows), s.created)

        self._refresh_preview()

    # ── preview ───────────────────────────────────────────────────────────────

    def _refresh_preview(self) -> None:
        name = self._selected_name()
        panel = self.query_one("#preview-content", Static)
        if not name:
            panel.update("")
            return
        raw = tmux_ops.capture_pane(name)
        if not raw.strip():
            panel.update(f"[dim]No output captured for '{name}'[/dim]")
            return
        try:
            panel.update(Text.from_ansi(raw))
        except Exception:
            panel.update(raw)

    def _selected_name(self) -> Optional[str]:
        table = self.query_one("#session-table", DataTable)
        row = table.cursor_row
        if 0 <= row < len(self._visible):
            return self._visible[row].name
        return None

    # ── events ────────────────────────────────────────────────────────────────

    def on_data_table_row_highlighted(
        self, _: DataTable.RowHighlighted
    ) -> None:
        self._refresh_preview()

    def on_input_changed(self, event: Input.Changed) -> None:
        if event.input.id == "search-bar":
            self._apply_filter(event.value)

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "search-bar":
            self._close_search()

    def on_key(self, event) -> None:
        if event.key == "escape" and self._search_active:
            bar = self.query_one("#search-bar", Input)
            bar.value = ""
            self._apply_filter("")
            self._close_search()
            event.stop()

    # ── search helpers ────────────────────────────────────────────────────────

    def _open_search(self) -> None:
        bar = self.query_one("#search-bar", Input)
        bar.display = True
        bar.focus()
        self._search_active = True

    def _close_search(self) -> None:
        bar = self.query_one("#search-bar", Input)
        bar.display = False
        self._search_active = False
        self.query_one("#session-table").focus()

    # ── actions ───────────────────────────────────────────────────────────────

    def action_start_search(self) -> None:
        self._open_search()

    def action_new_session(self) -> None:
        def _done(name: Optional[str]) -> None:
            if name:
                ok = tmux_ops.new_session(name)
                if ok:
                    self.notify(f"Created session '{name}'")
                    self._load_sessions()
                else:
                    self.notify(f"Failed to create '{name}'", severity="error")

        self.app.push_screen(NewSessionScreen(), _done)

    def action_rename_session(self) -> None:
        name = self._selected_name()
        if not name:
            return

        def _done(new_name: Optional[str]) -> None:
            if new_name:
                ok = tmux_ops.rename_session(name, new_name)
                if ok:
                    self.notify(f"Renamed to '{new_name}'")
                    self._load_sessions()
                else:
                    self.notify("Rename failed", severity="error")

        self.app.push_screen(RenameSessionScreen(name), _done)

    def action_kill_session(self) -> None:
        name = self._selected_name()
        if not name:
            return
        if self.config.skip_kill_confirmation:
            self._do_kill(name)
        else:
            def _done(confirmed: bool) -> None:
                if confirmed:
                    self._do_kill(name)

            self.app.push_screen(KillConfirmScreen(name), _done)

    def _do_kill(self, name: str) -> None:
        ok = tmux_ops.kill_session(name)
        if ok:
            self.notify(f"Killed session '{name}'")
        else:
            self.notify(f"Failed to kill '{name}'", severity="error")
        self._load_sessions()

    def action_attach_session(self) -> None:
        name = self._selected_name()
        if name:
            self.app.exit(name)

    def action_open_windows(self) -> None:
        name = self._selected_name()
        if name:
            self.app.push_screen(WindowScreen(name))

    def action_cycle_sort(self) -> None:
        sorts = ["name", "date", "attached"]
        idx = sorts.index(self._current_sort) if self._current_sort in sorts else 0
        self._current_sort = sorts[(idx + 1) % len(sorts)]
        self._load_sessions()
        self.notify(f"Sort: {self._current_sort}")

    def action_show_help(self) -> None:
        self.app.push_screen(HelpScreen())

    def action_quit_app(self) -> None:
        self.app.exit(None)

    def action_refresh(self) -> None:
        self._load_sessions()


# ── Application ───────────────────────────────────────────────────────────────

class TmuxNavigatorApp(App):
    """tmuxito — because someone had to explain it to you."""

    TITLE = "tmuxito"
    ENABLE_COMMAND_PALETTE = False

    CSS = """
    /* ── Session screen ─────────────────────────────────────────────────── */

    #search-bar {
        height: 3;
        border: tall $primary-darken-2;
    }

    #main-pane {
        height: 1fr;
    }

    #session-table {
        width: 60%;
        height: 100%;
        border-right: tall $primary-darken-2;
    }

    #preview-panel {
        width: 1fr;
        height: 100%;
        background: $surface-darken-1;
        padding: 1 2;
    }

    #preview-content {
        width: 100%;
    }

    /* ── Window screen ──────────────────────────────────────────────────── */

    #win-title {
        height: 3;
        content-align: left middle;
        padding: 0 2;
        background: $primary-darken-3;
        color: $text;
    }

    #win-table {
        height: 1fr;
    }

    /* ── Help screen ────────────────────────────────────────────────────── */

    #help-viewer {
        height: 1fr;
    }

    /* ── Modals ─────────────────────────────────────────────────────────── */

    KillConfirmScreen,
    NewSessionScreen,
    RenameSessionScreen {
        align: center middle;
    }

    #kill-dialog,
    #new-session-dialog,
    #rename-dialog {
        background: $panel;
        border: tall $primary;
        padding: 2 4;
        width: 52;
        height: auto;
    }

    #kill-label {
        margin-bottom: 1;
    }

    #kill-buttons,
    .dialog-buttons {
        margin-top: 1;
        height: auto;
        align: center middle;
    }

    Button {
        margin: 0 1;
    }
    """

    def __init__(self) -> None:
        super().__init__()
        self.config = load_config()

    def on_mount(self) -> None:
        self.push_screen(SessionScreen(self.config))
