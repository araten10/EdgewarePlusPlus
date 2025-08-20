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

from dataclasses import dataclass
from pathlib import Path

PATH = Path(__file__).parent.parent
DEFAULT_PACK_PATH = PATH / "resource"


@dataclass
class Process:
    ROOT = PATH / "src"

    CONFIG = ROOT / "main_config.py"
    MAIN = ROOT / "main_edgeware.py"
    PANIC = ROOT / "panic.py"

    LINUX_MPV = ROOT / "os_utils" / "linux_mpv_subprocess.py"


@dataclass
class Assets:
    ROOT = PATH / "assets"

    CORRUPTION_ABRUPT = ROOT / "corruption_abruptfade.png"
    CORRUPTION_DEFAULT = ROOT / "corruption_defaultfade.png"

    # Unchangeable defaults
    DEFAULT_CONFIG = ROOT / "default_config.json"
    DEFAULT_IMAGE = ROOT / "default_image.png"

    # Changeable defaults
    DEFAULT_CONFIG_ICON = ROOT / "default_config_icon.ico"
    DEFAULT_HYPNO = ROOT / "default_hypno.gif"
    DEFAULT_ICON = ROOT / "default_icon.ico"
    DEFAULT_PANIC_ICON = ROOT / "default_panic_icon.ico"
    DEFAULT_PANIC_WALLPAPER = ROOT / "default_panic_wallpaper.jpg"
    DEFAULT_STARTUP_SPLASH = ROOT / "default_loading_splash.png"
    DEFAULT_THEME_DEMO = ROOT / "default_theme_demo.png"

    # Tutorial pages
    TUTORIAL = ROOT / "tutorial"

    TUTORIAL_UNDERCONSTRUCTION = TUTORIAL / "construction.html"

    TUTORIAL_INTRO = TUTORIAL / "intro.html"
    TUTORIAL_GETSTARTED = TUTORIAL / "gettingstarted.html"
    TUTORIAL_BASICSETTINGS = TUTORIAL / "basicsettings.html"
    TUTORIAL_QUICKGUIDE = TUTORIAL / "quickstart.html"


@dataclass
class Data:
    ROOT = PATH / "data"

    # Directories
    BACKUPS = ROOT / "backups"
    LOGS = ROOT / "logs"
    MOODS = ROOT / "moods"
    PACKS = ROOT / "packs"
    PRESETS = ROOT / "presets"
    BLACKLIST = ROOT / "blacklist"

    # Files
    CONFIG = ROOT / "config.json"
    CORRUPTION_LAUNCHES = ROOT / "corruption_launches.dat"

    # Changed defaults
    CONFIG_ICON = ROOT / "config_icon.ico"
    HYPNO = ROOT / "hypno.png"
    ICON = ROOT / "icon.ico"
    PANIC_ICON = ROOT / "panic_icon.ico"
    PANIC_WALLPAPER = ROOT / "panic_wallpaper.png"
    STARTUP_SPLASH = ROOT / "loading_splash.png"
    THEME_DEMO = ROOT / "theme_demo.png"


@dataclass
class CustomAssets:
    def config_icon() -> Path:
        return Data.CONFIG_ICON if Data.CONFIG_ICON.is_file() else Assets.DEFAULT_CONFIG_ICON

    def hypno() -> Path:
        return Data.HYPNO if Data.HYPNO.is_file() else Assets.DEFAULT_HYPNO

    def icon() -> Path:
        return Data.ICON if Data.ICON.is_file() else Assets.DEFAULT_ICON

    def panic_icon() -> Path:
        return Data.PANIC_ICON if Data.PANIC_ICON.is_file() else Assets.DEFAULT_PANIC_ICON

    def panic_wallpaper() -> Path:
        return Data.PANIC_WALLPAPER if Data.PANIC_WALLPAPER.is_file() else Assets.DEFAULT_PANIC_WALLPAPER

    def startup_splash() -> Path:
        return Data.STARTUP_SPLASH if Data.STARTUP_SPLASH.is_file() else Assets.DEFAULT_STARTUP_SPLASH

    def theme_demo() -> Path:
        return Data.THEME_DEMO if Data.THEME_DEMO.is_file() else Assets.DEFAULT_THEME_DEMO


@dataclass
class PackPaths:
    def __init__(self, root: Path) -> None:
        self.root = root

        # Directories
        self.audio = self.root / "aud"
        self.hypno = self.root / "hypno"
        self.image = self.root / "img"
        self.video = self.root / "vid"

        # Files
        self.config = self.root / "config.json"
        self.corruption = self.root / "corruption.json"
        self.discord = self.root / "discord.dat"
        self.icon = self.root / "icon.ico"
        self.index = self.root / "index.json"
        self.info = self.root / "info.json"
        self.script = self.root / "script.lua"
        self.splash = [self.root / f"loading_splash.{extension}" for extension in ["png", "gif", "jpg", "jpeg", "bmp"]]
        self.wallpaper = self.root / "wallpaper.png"

        # Legacy fallback options
        self.hypno_legacy = self.root / "subliminals"
        self.captions = self.root / "captions.json"
        self.media = self.root / "media.json"
        self.prompt = self.root / "prompt.json"
        self.web = self.root / "web.json"
