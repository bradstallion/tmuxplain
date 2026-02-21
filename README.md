# tmuxplain

> **because someone had to explain it to you**

A terminal UI for managing tmux sessions — browse, attach, rename, kill, and
preview sessions without ever leaving the keyboard.

Built with [Textual](https://github.com/Textualize/textual).

![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue)
![Textual](https://img.shields.io/badge/ui-textual-blueviolet)

---

## Features

- **Session list** with status (attached/detached), window count, and creation time
- **Live preview** of the selected session via `tmux capture-pane`
- **Drill into windows** — attach directly to a specific window
- **Inline search** — filter sessions by typing `/`
- **Sort** by name, creation date, or attached status
- **Full keyboard and mouse** support
- **Contextual footer** that updates per screen
- **Help screen** (`?`) with a full tmux keybinding reference
- **Config file** for persistent preferences

---

## Requirements

- Python 3.10+
- tmux (any reasonably recent version)

---

## Installation

### With pipx (recommended)

```sh
pipx install git+https://github.com/bradstallion/tmuxplain.git
```

After installation the `tmuxplain` command is available globally.

### With pip inside a virtualenv

```sh
pip install .
```

### For development

```sh
git clone https://github.com/bradstallion/tmuxplain.git
cd tmuxplain
python -m venv venv
source venv/bin/activate
pip install -e .
```

---

## Usage

```sh
tmuxplain
```

Or, without installing:

```sh
python -m tmuxplain
```

---

## Keybindings

### Session list

| Key | Action |
|-----|--------|
| `n` | New session |
| `r` | Rename selected session |
| `k` | Kill selected session (confirmation prompt) |
| `Enter` | Attach to selected session |
| `→` | Drill into session windows |
| `/` | Filter / search sessions (Esc to cancel) |
| `s` | Cycle sort: name → date → attached |
| `R` | Refresh list |
| `?` | Help screen |
| `q` | Quit |

### Window list

| Key | Action |
|-----|--------|
| `Enter` | Attach to selected window |
| `Esc` | Back to session list |

### Help screen

| Key | Action |
|-----|--------|
| `Esc` / `q` | Close |

---

## Configuration

tmuxplain reads `~/.config/tmuxplain/config.toml` on startup.
The file is optional; all settings have defaults.

```toml
# Skip the "Kill session?" confirmation dialog
skip_kill_confirmation = false

# Default sort order: "name" | "date" | "attached"
default_sort = "name"

# UI theme: "dark" | "light"
color_theme = "dark"
```

---

## Running tests

```sh
python -m pytest tests/
```

---

## Project layout

```
tmuxplain/
├── __init__.py
├── __main__.py   # python -m tmuxplain
├── main.py       # entry point
├── app.py        # Textual screens and widgets
├── tmux.py       # all tmux subprocess calls
├── config.py     # config loading
└── help.py       # help screen content
tests/
└── test_tmux.py
pyproject.toml
```
