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

from pathlib import Path
from tkinter import Toplevel

import mpv


def close_mpv(player: mpv.MPV) -> None:
    pass


def set_borderless(window: Toplevel) -> None:
    pass


def set_clickthrough(window: Toplevel) -> None:
    pass


def set_wallpaper(wallpaper: Path) -> None:
    pass


def open_directory(url: str) -> None:
    pass


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    pass


def toggle_run_at_startup(state: bool) -> None:
    pass
