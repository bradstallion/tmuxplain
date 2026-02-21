"""Help screen content — tmux reference table."""

HELP_CONTENT = """\
# tmux Quick Reference

Press **Esc** or **q** to close.

---

## Setup

| Command | Description |
|---------|-------------|
| `tmux` | Start a new unnamed session |
| `tmux new -s name` | Start a new named session |
| `tmux ls` | List all sessions |
| `tmux a` | Attach to the last session |
| `tmux a -t name` | Attach to a specific session |
| `tmux kill-session -t name` | Kill a session |
| `tmux kill-server` | Kill tmux server and all sessions |

---

## Sessions  *(prefix = Ctrl+b)*

| Key | Description |
|-----|-------------|
| `$` | Rename current session |
| `d` | Detach from current session |
| `s` | Interactive session list |
| `(` | Switch to previous session |
| `)` | Switch to next session |
| `L` | Switch to last (most recently used) session |

---

## Windows  *(prefix = Ctrl+b)*

| Key | Description |
|-----|-------------|
| `c` | Create new window |
| `,` | Rename current window |
| `w` | Interactive window list |
| `n` | Next window |
| `p` | Previous window |
| `0–9` | Switch to window by number |
| `&` | Kill current window |
| `f` | Find window by name |
| `.` | Move window to a different index |

---

## Panes  *(prefix = Ctrl+b)*

| Key | Description |
|-----|-------------|
| `%` | Split pane vertically (left/right) |
| `"` | Split pane horizontally (top/bottom) |
| `o` | Cycle to next pane |
| `q` | Show pane numbers (press number to jump) |
| `x` | Kill current pane |
| `z` | Toggle zoom on current pane |
| `{` | Swap pane with the previous one |
| `}` | Swap pane with the next one |
| `↑ ↓ ← →` | Navigate between panes |
| `Alt+↑ ↓ ← →` | Resize current pane |
| `!` | Break pane into its own window |
| `Space` | Cycle through preset layouts |

---

## Copy Mode  *(prefix = Ctrl+b)*

| Key | Description |
|-----|-------------|
| `[` | Enter copy mode |
| `]` | Paste most recent buffer |
| `Space` *(in copy mode)* | Start selection |
| `Enter` *(in copy mode)* | Copy selection and exit copy mode |
| `q` *(in copy mode)* | Quit copy mode |
| `g` / `G` | Jump to top / bottom of history |
| `/` | Search forward |
| `?` | Search backward |

---

## Other  *(prefix = Ctrl+b)*

| Key | Description |
|-----|-------------|
| `?` | List all keybindings |
| `:` | Open tmux command prompt |
| `t` | Show clock |
| `~` | Show previous messages |
| `r` | Reload tmux config |

---

## tmux Navigator Keybindings

| Key | Action |
|-----|--------|
| `n` | New session |
| `r` | Rename selected session |
| `k` | Kill selected session |
| `Enter` | Attach to selected session |
| `→` | Drill into session windows |
| `/` | Filter / search sessions |
| `s` | Cycle sort order (name → date → attached) |
| `R` | Refresh session list |
| `?` | This help screen |
| `q` | Quit |
"""
