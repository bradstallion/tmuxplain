"""Entry point for tmuxplain."""
from __future__ import annotations

import subprocess
import sys

import tmuxplain.tmux as tmux_ops
from tmuxplain.app import TmuxNavigatorApp


def main() -> None:
    if not tmux_ops.is_installed():
        print("tmux is not installed or not found in PATH.", file=sys.stderr)
        sys.exit(1)

    app = TmuxNavigatorApp()
    result = app.run()

    # If the user selected a session/window to attach to, do it now.
    if result:
        cmd = tmux_ops.attach_command(result)
        subprocess.run(cmd)


if __name__ == "__main__":
    main()
