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

import ctypes
import logging
import os
import subprocess
import tempfile
from ctypes import windll
from pathlib import Path
from tkinter import Toplevel

import mpv
from paths import PATH, CustomAssets, Process

PYW = {
    Process.CONFIG: PATH / "config.pyw",
    Process.MAIN: PATH / "edgeware.pyw",
    Process.PANIC: PATH / "panic.pyw",
}


def close_mpv(player: mpv.MPV) -> None:
    player.terminate()


def set_borderless(window: Toplevel) -> None:
    window.overrideredirect(True)


def set_clickthrough(window: Toplevel) -> None:
    ws_ex_layered = 0x00080000
    ws_ex_transparent = 0x00000020
    gwl_exstyle = -20

    hwnd = windll.user32.GetParent(window.winfo_id())
    ex_style = windll.user32.GetWindowLongW(hwnd, gwl_exstyle)
    ex_style |= ws_ex_transparent | ws_ex_layered
    windll.user32.SetWindowLongW(hwnd, gwl_exstyle, ex_style)


def set_wallpaper(wallpaper: Path) -> None:
    ctypes.windll.user32.SystemParametersInfoW(20, 0, str(wallpaper), 0)


def open_directory(url: str) -> None:
    subprocess.Popen(f'explorer "{url}"')


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    filename = f"{title}.lnk"
    file = (location if location else Path(os.path.expanduser("~\\Desktop"))) / filename

    pyw_process = PYW[process]

    with tempfile.NamedTemporaryFile(
        "w",
        suffix=".bat",
        delete=False,
    ) as bat:
        bat.writelines(
            [
                '@echo off\nset SCRIPT="%TEMP%\\%RANDOM%-%RANDOM%-%RANDOM%-%RANDOM%.vbs"\n',
                'echo Set oWS = WScript.CreateObject("WScript.Shell") >> %SCRIPT%\n',
                'echo sLinkFile = "' + str(file) + '" >> %SCRIPT%\n',
                "echo Set oLink = oWS.CreateShortcut(sLinkFile) >> %SCRIPT%\n",
                'echo oLink.WorkingDirectory = "' + str(pyw_process.parent) + '\\" >> %SCRIPT%\n',
                'echo oLink.IconLocation = "' + str(icon) + '" >> %SCRIPT%\n',
                'echo oLink.TargetPath = "' + str(pyw_process) + '" >> %SCRIPT%\n',
                "echo oLink.Save >> %SCRIPT%\n",
                "cscript /nologo %SCRIPT%\n",
                "del %SCRIPT%",
            ]
        )  # write built shortcut script text to temporary batch file

    try:
        subprocess.run(bat.name)
    except Exception as e:
        logging.warning(f"failed to call or remove temp batch file for making shortcuts\n\tReason: {e}")

    if os.path.exists(bat.name):
        os.remove(bat.name)


def toggle_run_at_startup(state: bool) -> None:
    startup_path = Path(os.path.expanduser("~\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup"))
    if state:
        make_shortcut("Edgeware++", Process.MAIN, CustomAssets.icon(), startup_path)
    else:
        (startup_path / "Edgeware++.lnk").unlink(missing_ok=True)
