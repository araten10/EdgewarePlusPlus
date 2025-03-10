from pathlib import Path
from tkinter import Toplevel

import mpv


def close_mpv(player: mpv.MPV) -> None:
    pass


def set_borderless(window: Toplevel) -> None:
    pass


def set_wallpaper(wallpaper: Path) -> None:
    pass


def open_directory(url: str) -> None:
    pass


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    pass


def toggle_run_at_startup(state: bool) -> None:
    pass
