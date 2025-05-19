# Copyright (C) 2025 Araten & Marigold
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

import ast
from dataclasses import dataclass
from tkinter import BooleanVar, IntVar, StringVar
from typing import Callable, Tuple

from voluptuous import All, Range, Schema, Union

from config.themes import THEMES

NONNEGATIVE = Schema(All(int, Range(min=0)))
PERCENTAGE = Schema(All(int, Range(min=0, max=100)))
BOOLEAN = Schema(All(int, Range(min=0, max=1)))
STRING = Schema(str)


def s_to_ms(value: int) -> int:
    return value * 1000


def to_float(value: int) -> float:
    return value / 100


def negation(value: bool) -> bool:
    return not value


@dataclass
class Item:
    key: str
    schema: Callable
    var: Callable | None
    setting: Callable | None

    # TODO: Find a better solution for these corruption variables
    block: bool = False
    danger: bool = False
    safe_range: Tuple[int | None, int | None] | None = None  # When the setting has a value outside the given range, it is considered dangerous (min, max)


# fmt: off
CONFIG_ITEMS = {
    # Start
    "pack_path": Item("packPath", Schema(Union(str, None)), StringVar, lambda value: value),
    "theme": Item("themeType", Schema(Union("Original", "Dark", "The One", "Ransom", "Goth", "Bimbo")), StringVar, lambda value: THEMES.get(value, THEMES["Original"])),
    "theme_ignore_config": Item("themeNoConfig", BOOLEAN, BooleanVar, None, block=True),
    "startup_splash": Item("showLoadingFlair", BOOLEAN, BooleanVar, bool, block=True),
    "run_on_save_quit": Item("runOnSaveQuit", BOOLEAN, BooleanVar, None, block=True),
    "desktop_icons": Item("desktopIcons", BOOLEAN, BooleanVar, bool, block=True),
    "safe_mode": Item("safeMode", BOOLEAN, BooleanVar, None, block=True),
    "message_off": Item("messageOff", BOOLEAN, BooleanVar, None, block=True),
    "global_panic_key": Item("globalPanicButton", STRING, StringVar, str, block=True),  # while disabling panic could be used for danger-chasing fetishists, changing the hotkey serves little purpose
    "panic_key": Item("panicButton", STRING, StringVar, str, block=True),
    "preset_danger": Item("presetsDanger", BOOLEAN, BooleanVar, None, block=True),

    # Booru Downloader
    "booru_download": Item("downloadEnabled", BOOLEAN, BooleanVar, bool),
    "booru_tags": Item("tagList", STRING, None, lambda value: value.replace(">", " ")),
    "min_score": Item("booruMinScore", Schema(int), IntVar, int),

    # Popups
    "delay": Item("delay", NONNEGATIVE, IntVar, int, safe_range=(2000, None)),
    "image_chance": Item("popupMod", PERCENTAGE, IntVar, int),
    "web_chance": Item("webMod", PERCENTAGE, IntVar, int),
    "prompt_chance": Item("promptMod", PERCENTAGE, IntVar, int),
    "prompt_max_mistakes": Item("promptMistakes", NONNEGATIVE, IntVar, int),
    "opacity": Item("lkScaling", PERCENTAGE, IntVar, to_float),
    "timeout_enabled": Item("timeoutPopups", BOOLEAN, BooleanVar, bool),
    "timeout": Item("popupTimeout", NONNEGATIVE, IntVar, s_to_ms),
    "web_on_popup_close": Item("webPopup", BOOLEAN, BooleanVar, bool, danger=True),  # opens up web popup on popup close, this one could be cut from this list as it's not listed as dangerous in config but could lead to bad performance
    "buttonless": Item("buttonless", BOOLEAN, BooleanVar, bool),
    "single_mode": Item("singleMode", BOOLEAN, BooleanVar, bool),
    "popup_subliminals": Item("popupSubliminals", BOOLEAN, BooleanVar, bool),
    "subliminal_chance": Item("subliminalsChance", PERCENTAGE, IntVar, int),
    "subliminal_opacity": Item("subliminalsAlpha", PERCENTAGE, IntVar, to_float),
    "max_subliminals": Item("maxSubliminals", NONNEGATIVE, IntVar, int),
    "denial_mode": Item("denialMode", BOOLEAN, BooleanVar, bool),
    "denial_chance": Item("denialChance", PERCENTAGE, IntVar, int),
    "disabled_monitors": Item("disabledMonitors", Schema([str]), None, list, block=True),

    # Audio/Video
    "audio_chance": Item("audioMod", PERCENTAGE, IntVar, int),
    "max_audio": Item("maxAudio", NONNEGATIVE, IntVar, int),
    "audio_volume": Item("audioVolume", PERCENTAGE, IntVar, to_float),
    "video_chance": Item("vidMod", PERCENTAGE, IntVar, int),
    "video_volume": Item("videoVolume", PERCENTAGE, IntVar, int),
    "max_video": Item("maxVideos", NONNEGATIVE, IntVar, int),
    "video_hardware_acceleration": Item("videoHardwareAcceleration", BOOLEAN, BooleanVar, bool),

    # Captions
    "captions_in_popups": Item("showCaptions", BOOLEAN, BooleanVar, bool),
    "filename_caption_moods": Item("captionFilename", BOOLEAN, BooleanVar, bool),
    "multi_click_popups": Item("multiClick", BOOLEAN, BooleanVar, bool),
    "subliminal_message_popup_chance": Item("capPopChance", PERCENTAGE, IntVar, int),
    "subliminal_message_popup_opacity": Item("capPopOpacity", PERCENTAGE, IntVar, to_float),
    "subliminal_message_popup_timeout": Item("capPopTimer", NONNEGATIVE, IntVar, int),
    "notification_chance": Item("notificationChance", PERCENTAGE, IntVar, int),
    "notification_image_chance": Item("notificationImageChance", PERCENTAGE, IntVar, int),

    # Wallpaper
    "wallpapers": Item("wallpaperDat", STRING, None, lambda value: list(ast.literal_eval(value).values())),
    "rotate_wallpaper": Item("rotateWallpaper", BOOLEAN, BooleanVar, bool, block=True),  # Corruption won't work
    "wallpaper_timer": Item("wallpaperTimer", NONNEGATIVE, IntVar, s_to_ms),
    "wallpaper_variance": Item("wallpaperVariance", NONNEGATIVE, IntVar, s_to_ms),

    # Dangerous Settings
    "drive_avoid_list": Item("avoidList", STRING, None, lambda value: value.split(">"), block=True),
    "fill_drive": Item("fill", BOOLEAN, BooleanVar, bool, danger=True),
    "fill_delay": Item("fill_delay", NONNEGATIVE, IntVar, lambda value: value * 10, danger=True),
    "replace_images": Item("replace", BOOLEAN, BooleanVar, bool, block=True),  # Corruption won't work
    "replace_threshold": Item("replaceThresh", NONNEGATIVE, IntVar, int, block=True),  # Corruption won't work
    "drive_path": Item("drivePath", STRING, StringVar, str, block=True),  # We can't know what paths exist and they look different on Linux and Windows
    "panic_disabled": Item("panicDisabled", BOOLEAN, BooleanVar, bool, danger=True),
    "run_at_startup": Item("start_on_logon", BOOLEAN, BooleanVar, None, block=True),
    "show_on_discord": Item("showDiscord", BOOLEAN, BooleanVar, bool, block=True),  # Corruption won't work

    # Basic Modes
    "lowkey_mode": Item("lkToggle", BOOLEAN, BooleanVar, bool),
    "lowkey_corner": Item("lkCorner", Schema(Union(int, Range(min=0, max=4))), IntVar, int),
    "moving_chance": Item("movingChance", PERCENTAGE, IntVar, int),
    "moving_random": Item("movingRandom", BOOLEAN, BooleanVar, bool),
    "moving_speed": Item("movingSpeed", NONNEGATIVE, IntVar, int),

    # Dangerous Modes
    "timer_mode": Item("timerMode", BOOLEAN, BooleanVar, bool, block=True),  # Corruption won't work
    "timer_time": Item("timerSetupTime", NONNEGATIVE, IntVar, lambda value: value * 60 * 1000, block=True),  # Corruption won't work
    "timer_password": Item("safeword", STRING, StringVar, str, block=True),  # imo, the safeword is a safeword for a reason (timer mode)
    "mitosis_mode": Item("mitosisMode", BOOLEAN, BooleanVar, bool, block=True),  # Corruption may not work
    "mitosis_strength": Item("mitosisStrength", NONNEGATIVE, IntVar, int),

    # Hibernate
    "hibernate_mode": Item("hibernateMode", BOOLEAN, BooleanVar, bool, block=True),  # Corruption won't work
    "hibernate_fix_wallpaper": Item("fixWallpaper", BOOLEAN, BooleanVar, bool),
    "hibernate_type": Item("hibernateType", Schema(Union("Original", "Spaced", "Glitch", "Ramp", "Pump-Scare", "Chaos")), StringVar, str),
    "hibernate_delay_min": Item("hibernateMin", NONNEGATIVE, IntVar, s_to_ms),
    "hibernate_delay_max": Item("hibernateMax", NONNEGATIVE, IntVar, s_to_ms, safe_range=(10, None)),
    "hibernate_activity": Item("wakeupActivity", NONNEGATIVE, IntVar, int, safe_range=(0, 35)),
    "hibernate_activity_length": Item("hibernateLength", NONNEGATIVE, IntVar, s_to_ms),

    # Corruption
    "corruption_mode": Item("corruptionMode", BOOLEAN, BooleanVar, bool, block=True),  # if you're turning off corruption mode with corruption just make it the final level lmao
    "corruption_full": Item("corruptionFullPerm", BOOLEAN, BooleanVar, bool, block=True),
    "corruption_trigger": Item("corruptionTrigger", Schema(Union("Timed", "Popup", "Launch")), StringVar, str),
    "corruption_fade": Item("corruptionFadeType", Schema(Union("Normal", "Abrupt")), StringVar, str),
    "corruption_time": Item("corruptionTime", NONNEGATIVE, IntVar, s_to_ms),
    "corruption_popups": Item("corruptionPopups", NONNEGATIVE, IntVar, int),
    "corruption_launches": Item("corruptionLaunches", NONNEGATIVE, IntVar, int),
    "corruption_wallpaper": Item("corruptionWallpaperCycle", BOOLEAN, BooleanVar, negation),
    "corruption_themes": Item("corruptionThemeCycle", BOOLEAN, BooleanVar, negation),
    "corruption_purity": Item("corruptionPurityMode", BOOLEAN, BooleanVar, bool),
    "corruption_dev_mode": Item("corruptionDevMode", BOOLEAN, BooleanVar, bool, block=True),

    # Troubleshooting
    "toggle_hibernate_skip": Item("toggleHibSkip", BOOLEAN, BooleanVar, bool, block=True),
    "toggle_internet": Item("toggleInternet", BOOLEAN, BooleanVar, None, block=True),
    "toggle_mood_set": Item("toggleMoodSet", BOOLEAN, BooleanVar, None, block=True),
    "mpv_subprocess": Item("mpvSubprocess", BOOLEAN, BooleanVar, bool, block=True),
}
# fmt: on
