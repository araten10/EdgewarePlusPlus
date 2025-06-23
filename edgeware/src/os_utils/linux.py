# Copyright (C) 2024 Araten & Marigold
#
# This file is part of Edgeware++.
#
# Edgeware++ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Edgeware++ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edgeware++.  If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import shlex
import subprocess
import sys
from pathlib import Path
from tkinter import Toplevel

import mpv
from config import load_default_config
from paths import CustomAssets, Process

from os_utils.linux_utils import get_desktop_environment, get_wallpaper_commands, get_wallpaper_function


def close_mpv(player: mpv.MPV) -> None:
    player.stop()


def set_borderless(window: Toplevel) -> None:
    if get_desktop_environment() == "kde":
        window.overrideredirect(True)
    else:
        window.attributes("-type", "splash")


def set_clickthrough(window: Toplevel) -> None:
    pass


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
