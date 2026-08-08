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
import subprocess
import sys
from pathlib import Path
from tkinter import Toplevel

import mpv
from paths import Process, _APP_BUNDLES, _find_app_bundle


def close_mpv(player: mpv.MPV) -> None:
    player.stop()


def set_borderless(window: Toplevel) -> None:
    window.tk.call('wm', 'overrideredirect', window._w, True)


def set_clickthrough(window: Toplevel) -> None:
    pass  # Disabled on macOS via settings.py and popup_tweaks.py


def get_wallpaper() -> Path | None:
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "System Events" to tell desktop 1 to get picture'],
            capture_output=True,
            text=True,
            check=True,
        )
        output = result.stdout.strip()
        if output:
            return Path(output)
    except Exception as e:
        logging.warning(f"Failed to get wallpaper. Reason: {e}")
    return None


def set_wallpaper(wallpaper: Path) -> None:
    script = f'tell application "System Events" to tell every desktop to set picture to "{wallpaper}"'
    try:
        subprocess.run(["osascript", "-e", script], check=True)
    except Exception as e:
        logging.warning(f"Failed to set wallpaper. Reason: {e}")


def open_directory(url: str) -> None:
    subprocess.Popen(["open", url])


def make_shortcut(title: str, process: Path, icon: Path, location: Path | None = None) -> None:
    # FUTUREWORK: Could create Automator .app bundles instead of .command files
    # for a more native macOS experience (e.g. proper icons in Finder, Dock support).
    filename = f"{title}.command"

    if location:
        file = location / filename
    elif getattr(sys, "frozen", False):
        # Frozen builds: write to ~/Applications/Edgeware++/ to avoid macOS TCC
        # permission prompts for Desktop/Documents access.
        app_dir = Path.home() / "Applications" / "Edgeware++"
        app_dir.mkdir(parents=True, exist_ok=True)
        file = app_dir / filename
    else:
        file = Path(os.path.expanduser("~/Desktop")) / filename

    if getattr(sys, "frozen", False):
        bundle = _find_app_bundle(_APP_BUNDLES[title])
        if bundle:
            app_path = bundle
        else:
            # Fallback: assume siblings in the same directory
            app_path = Path(sys.executable).parent.parent.parent.parent / f"{_APP_BUNDLES[title]}.app"
        content = [
            "#!/bin/bash",
            f'open "{app_path}"',
        ]
    else:
        content = [
            "#!/bin/bash",
            f'exec "{sys.executable}" "{process}"',
        ]

    file.write_text("\n".join(content))
    os.chmod(file, 0o755)


def toggle_run_at_startup(state: bool) -> None:
    if getattr(sys, "frozen", False):
        # In frozen mode, register the .app bundle as a login item
        bundle = _find_app_bundle("Edgeware++")
        if bundle:
            script_path = str(bundle)
        else:
            script_path = str(Path(sys.executable).parent.parent.parent)
    else:
        script_path = str(Process.MAIN)

    if state:
        subprocess.run([
            "osascript", "-e",
            f'tell application "System Events" to make login item at end with properties '
            f'{{name:"Edgeware++", path:"{script_path}", hidden:false}}',
        ])
    else:
        subprocess.run([
            "osascript", "-e",
            'tell application "System Events" to delete login item "Edgeware++"',
        ])


def set_schedule(vars) -> None:
    pass


def delete_schedule() -> None:
    pass
