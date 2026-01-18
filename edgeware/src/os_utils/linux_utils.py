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

import codecs
import os
import re
import shlex
import shutil
import subprocess
from collections.abc import Callable
from configparser import ConfigParser
from pathlib import Path


# Modified from https://stackoverflow.com/a/21213358
def get_desktop_environment() -> str:
    desktop = os.environ.get("XDG_CURRENT_DESKTOP") or os.environ.get("DESKTOP_SESSION")
    if desktop:
        desktop = desktop.lower()

        special_cases = [
            ("xubuntu", "xfce4"),
            ("ubuntustudio", "kde"),
            ("ubuntu", "gnome"),
            ("lubuntu", "lxde"),
            ("kubuntu", "kde"),
            ("razor", "razor-qt"),  # e.g. razorkwin
            ("wmaker", "windowmaker"),  # e.g. wmaker-common
            ("pop", "gnome"),
        ]

        for special, actual in special_cases:
            if desktop.startswith(special):
                return actual
        if "xfce" in desktop:
            return "xfce4"
        return desktop
    if os.environ.get("KDE_FULL_SESSION") == "true":
        return "kde"
    if is_running("xfce-mcs-manage"):
        return "xfce4"
    if is_running("ksmserver"):
        return "kde"

    return "unknown"


def find_set_wallpaper_commands(wallpaper: Path, desktop: str) -> list[str]:
    quoted = shlex.quote(str(wallpaper))
    quoted_hyprland = shlex.quote(f",{wallpaper}")
    quoted_gnome = shlex.quote(f"file://{wallpaper}")

    commands = {
        "xfce4": [
            f"xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-path -s {quoted}",
            "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-style -s 3",
            "xfconf-query -c xfce4-desktop -p /backdrop/screen0/monitor0/image-show -s true",
        ],
        "mate": [f"gsettings set org.mate.background picture-filename {quoted}"],
        "icewm": [f"icewmbg {quoted}"],
        "blackbox": [f"bsetbg -full {quoted}"],
        "lxde": [f"pcmanfm --set-wallpaper {quoted} --wallpaper-mode=scaled"],
        "lxqt": [f"pcmanfm-qt --set-wallpaper {quoted} --wallpaper-mode=scaled"],
        "windowmaker": [f"wmsetbg -s -u {quoted}"],
        "sway": [f'swaybg -o "*" -i {quoted} -m fill'],
        "hyprland": [f"hyprctl hyprpaper preload {quoted}", f"hyprctl hyprpaper wallpaper {quoted_hyprland}"],
        "kde": [f"plasma-apply-wallpaperimage {quoted}"],
        "trinity": [f"dcop kdesktop KBackgroundIface setWallpaper 0 {quoted} 6"],
        **dict.fromkeys(
            ["gnome", "unity", "cinnamon", "x-cinnamon"],
            [
                f"gsettings set org.gnome.desktop.background picture-uri {quoted_gnome}",
                f"gsettings set org.gnome.desktop.background picture-uri-dark {quoted_gnome}",
            ],
        ),
        **dict.fromkeys(["fluxbox", "jwm", "openbox", "afterstep"], [f"fbsetbg {quoted}"]),
    }

    return commands.get(desktop) or (find_set_wm_wallpaper_commands() if desktop in ["i3", "awesome", "dwm", "xmonad", "bspwm"] else [])


def find_set_wm_wallpaper_commands(wallpaper: Path) -> list[str]:
    quoted = shlex.quote(str(wallpaper))
    session = os.environ.get("XDG_SESSION_TYPE", "").lower()  # "x11" or "wayland"

    setters = {
        "x11": [
            ("nitrogen", [f"nitrogen --set-zoom-fill {quoted}"]),
            ("feh", [f"feh --bg-scale {quoted}"]),
            ("habak", [f"habak -ms {quoted}"]),
            ("hsetroot", [f"hsetroot -fill {quoted}"]),
            ("chbg", [f"chbg -once -mode maximize {quoted}"]),
            ("qiv", [f"qiv --root_s {quoted}"]),
            ("xv", [f"xv -max -smooth -root -quit {quoted}"]),
            ("xsri", [f"xsri --center-x --center-y --scale-width=100 --scale-height=100 {quoted}"]),
            ("xli", [f"xli -fullscreen -onroot -quiet -border black {quoted}"]),
            ("xsetbg", [f"xsetbg -fullscreen -border black {quoted}"]),
            ("fvwm-root", [f"fvwm-root -r {quoted}"]),
            ("wmsetbg", [f"wmsetbg -s -S {quoted}"]),
            ("Esetroot", [f"Esetroot -scale {quoted}"]),
            ("display", [f'display -sample `xwininfo -root 2> /dev/null|awk "/geom/{{print $2}}"` -window root {quoted}']),
        ],
        "wayland": [],
    }

    for program, commands in setters.get(session, []):
        if shutil.which(program):
            return commands

    return []


def find_set_wallpaper_function(wallpaper: Path, desktop: str) -> Callable[[], None] | None:
    def razor_qt() -> None:
        desktop_conf = ConfigParser()

        config_home = os.environ.get("XDG_CONFIG_HOME") or os.environ.get("XDG_HOME_CONFIG", os.path.expanduser(".config"))
        config_dir = os.path.join(config_home, "razor")

        # Development version
        desktop_conf_file = os.path.join(config_dir, "desktop.conf")
        if os.path.isfile(desktop_conf_file):
            config_option = r"screens\1\desktops\1\wallpaper"
        else:
            desktop_conf_file = os.path.expanduser(".razor/desktop.conf")
            config_option = r"desktops\1\wallpaper"
        desktop_conf.read(os.path.join(desktop_conf_file))
        try:
            if desktop_conf.has_option("razor", config_option):  # only replacing a value
                desktop_conf.set("razor", config_option, wallpaper)
                with codecs.open(
                    desktop_conf_file,
                    "w",
                    encoding="utf-8",
                    errors="replace",
                ) as f:
                    desktop_conf.write(f)
        except Exception:
            pass

    functions = {"razor-qt": razor_qt}

    return functions.get(desktop)


def find_get_wallpaper_command(desktop: str) -> str | None:
    commands = {
        "mate": ["gsettings get org.mate.background picture-filename"],
        **dict.fromkeys(
            ["gnome", "unity", "cinnamon", "x-cinnamon"],
            [
                "gsettings get org.gnome.desktop.background $(if [ $(gsettings get org.gnome.desktop.interface color-scheme) == \"'default'\" ]; then echo picture-uri; else echo picture-uri-dark; fi)"
            ],
        ),
    }

    return commands.get(desktop)


def is_running(process: str) -> bool:
    s = subprocess.Popen(["ps", "axw"], stdout=subprocess.PIPE)
    if s.stdout:
        return any(re.search(process, line.decode().strip()) for line in s.stdout)
    return False
