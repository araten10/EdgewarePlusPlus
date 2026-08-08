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

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------
# In frozen (PyInstaller) builds, read-only assets stay inside the .app
# bundle, while all user-writable data lives in
# ~/Library/Application Support/EdgewarePlusPlusMacosPython/.  This avoids permission
# problems (the bundle is in /Applications/ and owned by root), prevents
# data loss on app updates, and ensures all three apps (main, config, panic)
# share the same data regardless of where each .app is placed.

if getattr(sys, "frozen", False):
    # sys.executable → .../Edgeware++.app/Contents/MacOS/Edgeware++
    _bundle_dir = Path(sys.executable).parent.parent.parent  # the .app directory
    _BUNDLE_RESOURCES = _bundle_dir / "Contents" / "Resources"
    _USER_DATA = Path.home() / "Library" / "Application Support" / "EdgewarePlusPlusMacosPython"
else:
    _BUNDLE_RESOURCES = None  # Only valid in frozen builds
    _USER_DATA = None  # Only valid in frozen builds

# The legacy PATH variable is kept for backwards compatibility with code
# that references it directly (e.g., pack loading log messages).
if getattr(sys, "frozen", False):
    PATH = _USER_DATA
else:
    PATH = Path(__file__).parent.parent


def _ensure_user_data_dirs() -> None:
    """Create the user data directory structure on first run."""
    if not getattr(sys, "frozen", False):
        return
    for subdir in ["data", "data/packs", "data/backups", "data/logs",
                    "data/moods", "data/blacklist", "data/presets",
                    "resource"]:
        (_USER_DATA / subdir).mkdir(parents=True, exist_ok=True)


def _migrate_bundle_data() -> None:
    """One-shot migration: move data out of the .app bundle into user dir.

    When users have already run a bundled build that stored data inside the
    .app, this copies everything to the new Application Support location
    and removes the old data from the bundle so future updates don't
    silently overwrite user packs.
    """
    if not getattr(sys, "frozen", False):
        return

    # Look for old data inside whichever .app bundle we're currently in
    # (the main bundle is the canonical location, but we also check the
    # sibling Edgeware++.app in case we were called from Config or Panic).
    old_data_src = _BUNDLE_RESOURCES / "data"
    if not old_data_src.exists():
        # Try the sibling main bundle
        sibling = _bundle_dir.parent / "Edgeware++.app"
        if sibling.exists():
            old_data_src = sibling / "Contents" / "Resources" / "data"
        else:
            return  # No old data to migrate

    if not (old_data_src / "config.json").is_file():
        return  # Old data dir exists but has no config — skip

    import logging
    import sys as _sys
    logging.info("Migrating bundle data from %s to %s", old_data_src, _USER_DATA)
    print(f"Edgeware++: migrating data from {old_data_src} to {_USER_DATA}",
          file=_sys.stderr)

    for item in old_data_src.iterdir():
        dest = _USER_DATA / item.name
        if dest.exists():
            if dest.is_dir() and item.is_dir():
                # Deep-merge directory contents (handles nested subdirectories)
                shutil.copytree(item, dest, dirs_exist_ok=True)
            # If dest already exists and isn't a directory merge, leave user data intact
        else:
            if item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dest)

    # Clear the old data directory so updates don't re-bundle stale data
    try:
        for item in old_data_src.iterdir():
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()
    except OSError:
        pass  # Not writable — that's fine, the bundle may be read-only


# Run initialization at import time
_ensure_user_data_dirs()
_migrate_bundle_data()


# ---------------------------------------------------------------------------
# Default pack path
# ---------------------------------------------------------------------------
DEFAULT_PACK_PATH = PATH / "resource"


# ---------------------------------------------------------------------------
# Process entry-points (source-only — .py files don't exist in a bundle)
# ---------------------------------------------------------------------------
@dataclass
class Process:
    ROOT = PATH / "src"

    CONFIG = ROOT / "main_config.py"
    MAIN = ROOT / "main_edgeware.py"
    PANIC = ROOT / "panic.py"


# ---------------------------------------------------------------------------
# Read-only assets (bundled with the app, or in source tree when dev)
# ---------------------------------------------------------------------------
@dataclass
class Assets:
    ROOT = _BUNDLE_RESOURCES / "assets" if getattr(sys, "frozen", False) else PATH / "assets"

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

    # Denial mode mpv shaders
    SHADERS = ROOT / "shaders"
    SHADER_GAUSSIAN_BLUR = SHADERS / "gaussian_blur.glsl"
    SHADER_PIXELIZE = SHADERS / "pixelize.glsl"

    # Tutorial pages
    TUTORIAL = ROOT / "tutorial"
    TUTORIAL_UNDERCONSTRUCTION = TUTORIAL / "construction.html"
    TUTORIAL_INTRO = TUTORIAL / "intro.html"
    TUTORIAL_GETSTARTED = TUTORIAL / "gettingstarted.html"
    TUTORIAL_BASICSETTINGS = TUTORIAL / "basicsettings.html"
    TUTORIAL_QUICKGUIDE = TUTORIAL / "quickstart.html"


# ---------------------------------------------------------------------------
# User-writable data (Application Support in frozen mode)
# ---------------------------------------------------------------------------
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


_APP_BUNDLES = {
    "Edgeware++": "Edgeware++",
    "Edgeware++ Config": "Edgeware++ Config",
    "Edgeware++ Panic": "Edgeware++ Panic",
}


def _find_app_bundle(app_name: str) -> Path | None:
    """Locate a sibling .app bundle.

    Searches the directory containing the current bundle first, then
    /Applications/ and ~/Applications/ as fallbacks.
    Returns None when not in a frozen environment.
    """
    if not getattr(sys, "frozen", False):
        return None

    targets = [f"{app_name}.app"]

    # Directory containing the current .app bundle
    current_dir = _bundle_dir.parent
    for target in targets:
        candidate = current_dir / target
        if candidate.is_dir():
            return candidate

    # Common install locations
    for base in [Path("/Applications"), Path.home() / "Applications"]:
        for target in targets:
            candidate = base / target
            if candidate.is_dir():
                return candidate

    return None


def launch_app(app_name: str, block: bool = False, args: list[str] | None = None) -> None:
    """Launch another Edgeware app by name.

    In a bundle, opens the .app via its executable so we can wait for it.
    From source, runs the Python script directly.
    """
    import subprocess
    import sys

    if args is None:
        args = []

    if getattr(sys, "frozen", False):
        bundle = _find_app_bundle(_APP_BUNDLES[app_name])
        if bundle:
            exe = bundle / "Contents" / "MacOS" / _APP_BUNDLES[app_name]
        else:
            # Fallback: assume siblings in the same directory
            exe = _bundle_dir.parent / f"{_APP_BUNDLES[app_name]}.app" / "Contents" / "MacOS" / _APP_BUNDLES[app_name]
        if block:
            subprocess.run([str(exe)] + args)
        else:
            subprocess.Popen([str(exe)] + args)
    else:
        script = {
            "Edgeware++": Process.MAIN,
            "Edgeware++ Config": Process.CONFIG,
            "Edgeware++ Panic": Process.PANIC,
        }[app_name]
        if block:
            subprocess.run([sys.executable, script] + args)
        else:
            subprocess.Popen([sys.executable, script] + args)
