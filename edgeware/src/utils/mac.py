from pathlib import Path

import vlc  # TODO: May fail


def set_wallpaper(wallpaper: Path) -> None:
    pass


def set_vlc_window(player: vlc.MediaPlayer, window_id: int) -> None:
    player.set_nsobject(window_id)


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    pass


def toggle_run_at_startup(state: bool) -> None:
    pass
