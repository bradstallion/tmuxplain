"""Config loading from ~/.config/tmuxito/config.toml."""
from __future__ import annotations

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]
from dataclasses import dataclass
from pathlib import Path

CONFIG_PATH = Path("~/.config/tmuxito/config.toml").expanduser()


@dataclass
class Config:
    skip_kill_confirmation: bool = False
    default_sort: str = "name"   # name | date | attached
    color_theme: str = "dark"


def load_config() -> Config:
    if not CONFIG_PATH.exists():
        return Config()
    try:
        with open(CONFIG_PATH, "rb") as f:
            data = tomllib.load(f)
        return Config(
            skip_kill_confirmation=bool(data.get("skip_kill_confirmation", False)),
            default_sort=str(data.get("default_sort", "name")),
            color_theme=str(data.get("color_theme", "dark")),
        )
    except Exception:
        return Config()
