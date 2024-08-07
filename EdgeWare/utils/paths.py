import os
from dataclasses import dataclass
from pathlib import Path

PATH = Path(__file__).parent.parent

LOG_PATH = PATH / "logs"


@dataclass
class Process:
    CONFIG = PATH / "config.pyw"
    PANIC = PATH / "panic.pyw"
    START = PATH / "start.pyw"

    DISCORD = PATH / "subprocesses" / "discord_handler.pyw"
    POPUP = PATH / "subprocesses" / "popup.pyw"
    PROMPT = PATH / "subprocesses" / "prompt.pyw"
    SUBLABEL = PATH / "subprocesses" / "sublabel.pyw"


@dataclass
class Resource:
    ROOT = PATH / "resource"

    # Directories
    AUDIO = ROOT / "aud"
    IMAGE = ROOT / "img"
    SUBLIMINALS = ROOT / "subliminals"
    VIDEO = ROOT / "vid"

    # Files
    CAPTIONS = ROOT / "captions.json"
    CONFIG = ROOT / "config.json"
    CORRUPTION = ROOT / "corruption.json"
    DISCORD = ROOT / "discord.dat"
    ICON = ROOT / "icon.ico"
    INFO = ROOT / "info.json"
    SPLASH = None
    MEDIA = ROOT / "media.json"
    PROMPT = ROOT / "prompt.json"
    WALLPAPER = ROOT / "wallpaper.png"
    WEB = ROOT / "web.json"
    WEB_RESOURCE = ROOT / "webResource.json"


for file_format in ["png", "gif", "jpg", "jpeg", "bmp"]:
    path = Resource.ROOT / f"loading_splash.{file_format}"
    if os.path.isfile(path):
        Resource.SPLASH = path
        break


# Data generated by Edgeware
@dataclass
class Data:
    ROOT = PATH / "data"

    CONFIG = PATH / "config.cfg"
    PRESETS = PATH / "presets"

    # Timer mode files
    HID_TIME = PATH / "hid_time.dat"
    PASS_HASH = PATH / "pass.hash"

    MOODS = PATH / "moods"
    UNNAMED_MOODS = PATH / "moods" / "unnamed"

    CHAOS_TYPE = ROOT / "chaos_type.dat"
    CORRUPTION_LAUNCHES = ROOT / "corruption_launches.dat"
    CORRUPTION_LEVEL = ROOT / "corruption_level.dat"
    CORRUPTION_POPUPS = ROOT / "corruption_popups.dat"
    HIBERNATE = ROOT / "hibernate_handler.dat"
    MAX_SUBLIMINALS = ROOT / "max_subliminals.dat"
    MAX_VIDEOS = ROOT / "max_videos.dat"
    MEDIA_IMAGES = ROOT / "media_images.dat"
    MEDIA_VIDEO = ROOT / "media_video.dat"


@dataclass
class Defaults:
    ROOT = PATH / "default_assets"

    CORRUPTION_ABRUPT = ROOT / "corruption_abruptfade.png"
    CORRUPTION_DEFAULT = ROOT / "corruption_defaultfade.png"
    CORRUPTION_NOISE = ROOT / "corruption_noisefade.png"
    CONFIG = ROOT / "default_config.json"
    CONFIG_ICON = ROOT / "config_icon.ico"
    ICON = ROOT / "default_icon.ico"
    IMAGE = ROOT / "default_image.png"
    PANIC_ICON = ROOT / "panic_icon.ico"
    PANIC_WALLPAPER = ROOT / "default_win10.jpg"
    SPIRAL = ROOT / "default_spiral.gif"
    SPLASH = ROOT / "loading_splash.png"
    THEME_DEMO = ROOT / "theme_demo.png"
    WALLPAPER = ROOT / "default_wallpaper.png"
