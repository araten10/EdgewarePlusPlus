import gc
import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path
from tkinter import Toplevel

import mpv
from paths import CustomAssets, Process
from settings import load_default_config
from Xlib.display import Display
from Xlib.error import BadWindow

from os_utils.linux_utils import get_desktop_environment, get_wallpaper_commands, get_wallpaper_function

# Stores references to all mpv players so that they don't get terminated by the
# garbage collector prematurely before the X window created by Tkinter has been
# destroyed, otherwise Tkinter may produce an X error and crash the program
mpv_players = []
x_display = Display()


def mpv_player_gc(phase: str, info: dict) -> None:
    global mpv_players
    if phase != "stop":
        return

    alive = []
    for player, x_window in mpv_players:
        try:
            x_window.get_attributes()
            alive.append((player, x_window))
        except BadWindow:
            # Only terminate the player once the X window is destroyed
            player.terminate()

    mpv_players = alive


gc.callbacks.append(mpv_player_gc)


def init_mpv(player: mpv.MPV) -> None:
    player["gpu-context"] = "x11"  # Required on Wayland for embedding the player
    mpv_players.append((player, x_display.create_resource_object("window", player.wid)))


def close_mpv(player: mpv.MPV) -> None:
    player.stop()


def set_borderless(window: Toplevel) -> None:
    if get_desktop_environment() == "kde":
        window.overrideredirect(True)
    else:
        window.attributes("-type", "splash")


def set_wallpaper(wallpaper: Path) -> None:
    desktop = get_desktop_environment()
    commands = get_wallpaper_commands(wallpaper, desktop)
    function = get_wallpaper_function(wallpaper, desktop)

    if len(commands) > 0:
        for command in commands:
            try:
                subprocess.Popen(command, shell=True)
            except Exception as e:
                logging.warning(f"Failed to run {command}. Reason: {e}")
    elif function:
        try:
            function()
        except Exception as e:
            logging.warning(f"Failed to set wallpaper. Reason: {e}")
    else:
        logging.info(f"Can't set wallpaper for desktop environment {desktop}")


def open_directory(url: str) -> None:
    subprocess.Popen(["xdg-open", url])


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    default_config = load_default_config()

    filename = f"{title}.desktop"
    file = (location if location else Path(os.path.expanduser("~/Desktop"))) / filename
    content = [
        "[Desktop Entry]",
        f"Version={default_config['versionplusplus']}",
        f"Name={title}",
        f"Exec={shlex.join([str(sys.executable), str(process)])}",
        f"Icon={icon}",
        "Terminal=false",
        "Type=Application",
        "Categories=Application;",
    ]

    file.write_text("\n".join(content))
    if get_desktop_environment() == "gnome":
        subprocess.run(f'gio set "{str(file.absolute())}" metadata::trusted true', shell=True)


def toggle_run_at_startup(state: bool) -> None:
    autostart_path = Path(os.path.expanduser("~/.config/autostart"))
    if state:
        make_shortcut("Edgeware++", Process.MAIN, CustomAssets.icon(), autostart_path)
    else:
        (autostart_path / "Edgeware++.desktop").unlink(missing_ok=True)
