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
from enum import Enum
from tkinter import BooleanVar, IntVar, StringVar
from typing import Callable

from voluptuous import All, Range, Schema, Union
from voluptuous.error import Invalid

from config.themes import THEMES

BROKEN = True  # For config items that can't be changed by corruption

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


class DangerLevel(Enum):
    EXTREME = "extreme"
    MAJOR = "major"
    MEDIUM = "medium"
    MINOR = "minor"


@dataclass
class Danger:
    level: DangerLevel
    schema: Schema  # When validation passes, the value is dangerous
    warning: str | None = None

    def check(self, value: object) -> bool:
        try:
            self.schema(value)
            return True
        except Invalid:
            return False


@dataclass
class Item:
    key: str
    schema: Callable
    var: Callable | None
    setting: Callable | None
    danger: Danger | None = None

    # TODO: Find a better solution for this
    block: bool = False


REPLACE_IMAGES_DANGER = "Replace Images is enabled! THIS WILL DELETE FILES ON YOUR COMPUTER! Only enable this willingly and cautiously! Read the documentation in the Annoyance/Runtime Dangerous tab!"
RUN_AT_STARTUP_DANGER = "Launch on PC Startup is enabled! This will run Edgeware when you start your computer!"
FILL_DRIVE_DANGER = (
    "Fill Drive is enabled! Edgeware will place images all over your computer! Even if you want this, make sure the protected directories are right!"
)
PANIC_LOCKOUT_DANGER = "Panic Lockout is enabled! Panic cannot be used until a specific time! Make sure you know your Safeword!"
MITOSIS_MODE_DANGER = "Mitosis Mode is enabled! With high popup rates, this could create a chain reaction, causing lag!"
HIBERNATE_DELAY_MIN_DANGER = "You are running Hibernate Mode with a short minimum cooldown! You might experience lag if a bunch of hibernate modes overlap!"
HIBERNATE_DELAY_MAX_DANGER = "You are running Hibernate Mode with a short maximum cooldown! You might experience lag if a bunch of hibernate modes overlap!"
SHOW_ON_DISCORD_DANGER = "Show on Discord is enabled! This could lead to potential embarassment if you're on your main account!"
PANIC_DISABLED_DANGER = "Panic Hotkey is disabled! If you want to easily close Edgeware, read the tooltip in the Annoyance tab for other ways to panic!"
RUN_ON_SAVE_QUIT_DANGER = "Edgeware will run on Save & Exit (AKA: when you hit Yes!)"


# fmt: off
CONFIG_ITEMS = {
    # Start
    "pack_path": Item("packPath", Schema(Union(str, None)), StringVar, lambda value: value),
    "theme": Item("themeType", Schema(Union("Original", "Dark", "The One", "Ransom", "Goth", "Bimbo")), StringVar, lambda value: THEMES[value]),
    "theme_ignore_config": Item("themeNoConfig", BOOLEAN, BooleanVar, None, block=True),
    "startup_splash": Item("showLoadingFlair", BOOLEAN, BooleanVar, bool, block=True),
    "run_on_save_quit": Item("runOnSaveQuit", BOOLEAN, BooleanVar, None, danger=Danger(DangerLevel.MINOR, Schema(1), RUN_ON_SAVE_QUIT_DANGER), block=True),
    "desktop_icons": Item("desktopIcons", BOOLEAN, BooleanVar, bool, block=True),
    "safe_mode": Item("safeMode", BOOLEAN, BooleanVar, None, block=True),
    "message_off": Item("messageOff", BOOLEAN, BooleanVar, None, block=True),
    "global_panic_key": Item("globalPanicButton", STRING, StringVar, str, block=True),  # while disabling panic could be used for danger-chasing fetishists, changing the hotkey serves little purpose
    "preset_danger": Item("presetsDanger", BOOLEAN, BooleanVar, None, block=True),

    # Popup Types
    "delay": Item("delay", NONNEGATIVE, IntVar, int, danger=Danger(DangerLevel.MEDIUM, Schema(Range(max=1999)))),
    "single_mode": Item("singleMode", BOOLEAN, BooleanVar, bool),
    "image_chance": Item("popupMod", PERCENTAGE, IntVar, int),
    "audio_chance": Item("audioMod", PERCENTAGE, IntVar, int),
    "max_audio": Item("maxAudio", NONNEGATIVE, IntVar, int),
    "audio_volume": Item("audioVolume", PERCENTAGE, IntVar, to_float),
    "fade_in_duration": Item("fadeInDuration", NONNEGATIVE, IntVar, int),
    "fade_out_duration": Item("fadeOutDuration", NONNEGATIVE, IntVar, int),
    "video_chance": Item("vidMod", PERCENTAGE, IntVar, int),
    "max_video": Item("maxVideos", NONNEGATIVE, IntVar, int),
    "video_volume": Item("videoVolume", PERCENTAGE, IntVar, int),
    "web_chance": Item("webMod", PERCENTAGE, IntVar, int),
    "web_on_popup_close": Item("webPopup", BOOLEAN, BooleanVar, bool),
    "prompt_chance": Item("promptMod", PERCENTAGE, IntVar, int),
    "prompt_max_mistakes": Item("promptMistakes", NONNEGATIVE, IntVar, int),
    "subliminal_chance": Item("capPopChance", PERCENTAGE, IntVar, int),
    "subliminal_timeout": Item("capPopTimer", NONNEGATIVE, IntVar, int),
    "subliminal_opacity": Item("capPopOpacity", PERCENTAGE, IntVar, to_float),
    "notification_chance": Item("notificationChance", PERCENTAGE, IntVar, int),
    "notification_image_chance": Item("notificationImageChance", PERCENTAGE, IntVar, int),

    # Popup Tweaks
    "captions_in_popups": Item("showCaptions", BOOLEAN, BooleanVar, bool),
    "hypno_chance": Item("subliminalsChance", PERCENTAGE, IntVar, int),
    "hypno_opacity": Item("subliminalsAlpha", PERCENTAGE, IntVar, to_float),
    "denial_chance": Item("denialChance", PERCENTAGE, IntVar, int),
    "buttonless": Item("buttonless", BOOLEAN, BooleanVar, bool),
    "multi_click_popups": Item("multiClick", BOOLEAN, BooleanVar, bool),
    "opacity": Item("lkScaling", PERCENTAGE, IntVar, to_float),
    "timeout_enabled": Item("timeoutPopups", BOOLEAN, BooleanVar, bool),
    "timeout": Item("popupTimeout", NONNEGATIVE, IntVar, s_to_ms),
    "disabled_monitors": Item("disabledMonitors", Schema([str]), None, list, block=True),
    "moving_chance": Item("movingChance", PERCENTAGE, IntVar, int),
    "moving_speed": Item("movingSpeed", NONNEGATIVE, IntVar, int),
    "clickthrough_enabled": Item("clickthroughPopups", BOOLEAN, BooleanVar, bool),

    # Wallpaper
    "rotate_wallpaper": Item("rotateWallpaper", BOOLEAN, BooleanVar, bool, block=BROKEN),
    "wallpapers": Item("wallpaperDat", STRING, None, lambda value: list(ast.literal_eval(value).values())),
    "wallpaper_timer": Item("wallpaperTimer", NONNEGATIVE, IntVar, s_to_ms),
    "wallpaper_variance": Item("wallpaperVariance", NONNEGATIVE, IntVar, s_to_ms),

    # Booru
    "booru_download": Item("downloadEnabled", BOOLEAN, BooleanVar, bool),
    "booru_tags": Item("tagList", STRING, None, lambda value: value.replace(">", " ")),
    # "min_score": Item("booruMinScore", Schema(int), IntVar, int),  # TODO: Unimplemented

    # Dangerous
    "panic_lockout": Item("timerMode", BOOLEAN, BooleanVar, bool, danger=Danger(DangerLevel.MEDIUM, Schema(1), PANIC_LOCKOUT_DANGER), block=BROKEN),
    "panic_lockout_password": Item("safeword", STRING, StringVar, str, block=True),  # imo, the safeword is a safeword for a reason (timer mode)
    "panic_lockout_time": Item("timerSetupTime", NONNEGATIVE, IntVar, lambda value: value * 60 * 1000, block=BROKEN),
    "drive_avoid_list": Item("avoidList", STRING, None, lambda value: value.split(">"), block=True),
    "fill_drive": Item("fill", BOOLEAN, BooleanVar, bool, danger=Danger(DangerLevel.MAJOR, Schema(1), FILL_DRIVE_DANGER)),
    "fill_delay": Item("fill_delay", NONNEGATIVE, IntVar, lambda value: value * 10),
    "replace_images": Item("replace", BOOLEAN, BooleanVar, bool, danger=Danger(DangerLevel.EXTREME, Schema(1), REPLACE_IMAGES_DANGER), block=BROKEN),
    "replace_threshold": Item("replaceThresh", NONNEGATIVE, IntVar, int, block=BROKEN),
    "drive_path": Item("drivePath", STRING, StringVar, str, block=True),  # We can't know what paths exist and they look different on Linux and Windows
    "panic_disabled": Item("panicDisabled", BOOLEAN, BooleanVar, bool, danger=Danger(DangerLevel.MINOR, Schema(1), PANIC_DISABLED_DANGER)),
    "run_at_startup": Item("start_on_logon", BOOLEAN, BooleanVar, None, danger=Danger(DangerLevel.MAJOR, Schema(1), RUN_AT_STARTUP_DANGER), block=True),
    "show_on_discord": Item("showDiscord", BOOLEAN, BooleanVar, bool, danger=Danger(DangerLevel.MEDIUM, Schema(1), SHOW_ON_DISCORD_DANGER), block=BROKEN),

    # Modes
    "lowkey_mode": Item("lkToggle", BOOLEAN, BooleanVar, bool),
    "lowkey_corner": Item("lkCorner", Schema(Union(int, Range(min=0, max=4))), IntVar, int),
    "mitosis_mode": Item("mitosisMode", BOOLEAN, BooleanVar, bool, danger=Danger(DangerLevel.MEDIUM, Schema(1), MITOSIS_MODE_DANGER), block=BROKEN),
    "mitosis_strength": Item("mitosisStrength", NONNEGATIVE, IntVar, int),
    "hibernate_mode": Item("hibernateMode", BOOLEAN, BooleanVar, bool, block=BROKEN),
    "hibernate_type": Item("hibernateType", Schema(Union("Original", "Spaced", "Glitch", "Ramp", "Pump-Scare", "Chaos")), StringVar, str),
    "hibernate_delay_min": Item("hibernateMin", NONNEGATIVE, IntVar, s_to_ms, danger=Danger(DangerLevel.MEDIUM, Schema(Range(max=29)), HIBERNATE_DELAY_MIN_DANGER)),
    "hibernate_delay_max": Item("hibernateMax", NONNEGATIVE, IntVar, s_to_ms, danger=Danger(DangerLevel.MEDIUM, Schema(Range(max=29)), HIBERNATE_DELAY_MAX_DANGER)),
    "hibernate_activity": Item("wakeupActivity", NONNEGATIVE, IntVar, int, danger=Danger(DangerLevel.MEDIUM, Schema(Range(min=36)))),
    "hibernate_activity_length": Item("hibernateLength", NONNEGATIVE, IntVar, s_to_ms),
    "hibernate_fix_wallpaper": Item("fixWallpaper", BOOLEAN, BooleanVar, bool),

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
    "toggle_mood_set": Item("toggleMoodSet", BOOLEAN, BooleanVar, None, block=True),
    "toggle_internet": Item("toggleInternet", BOOLEAN, BooleanVar, None, block=True),
    "mpv_subprocess": Item("mpvSubprocess", BOOLEAN, BooleanVar, bool, block=True),
    "video_hardware_acceleration": Item("videoHardwareAcceleration", BOOLEAN, BooleanVar, bool),
    "panic_key": Item("panicButton", STRING, StringVar, str, block=True),
}
# fmt: on


CONFIG_DANGER: dict[str, Danger] = {item.key: item.danger for item in CONFIG_ITEMS.values() if item.danger}
CORRUPTION_BLOCK: set[str] = {item.key for item in CONFIG_ITEMS.values() if item.block}
