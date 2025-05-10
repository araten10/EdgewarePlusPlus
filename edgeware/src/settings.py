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

import ast
import json
import logging
import shutil
import subprocess
import sys
from dataclasses import dataclass
from tkinter import BooleanVar, IntVar, StringVar
from typing import Callable

from paths import DEFAULT_PACK_PATH, Assets, Data, Process
from voluptuous import All, Length, Range, Schema, Union

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
    var: Callable
    setting: Callable


# fmt: off
CONFIG_ITEMS = {
    # Start
    "pack_path": Item("packPath", Schema(Union(str, None)), StringVar, str),
    "theme": Item("themeType", Schema(Union("Original", "Dark", "The One", "Ransom", "Goth", "Bimbo")), StringVar, str),
    "theme_ignore_config": Item("themeNoConfig", BOOLEAN, BooleanVar, bool),
    "startup_splash": Item("showLoadingFlair", BOOLEAN, BooleanVar, bool),
    "run_on_save_quit": Item("runOnSaveQuit", BOOLEAN, BooleanVar, bool),
    "desktop_icons": Item("desktopIcons", BOOLEAN, BooleanVar, bool),
    "safe_mode": Item("safeMode", BOOLEAN, BooleanVar, bool),
    "message_off": Item("messageOff", BOOLEAN, BooleanVar, bool),
    "global_panic_key": Item("globalPanicButton", STRING, StringVar, str),
    "panic_key": Item("panicButton", STRING, StringVar, str),
    "preset_danger": Item("presetsDanger", BOOLEAN, BooleanVar, bool),

    # Booru Downloader
    "booru_download": Item("downloadEnabled", BOOLEAN, BooleanVar, bool),
    "min_score": Item("booruMinScore", Schema(int), IntVar, int),

    # Popups
    "delay": Item("delay", NONNEGATIVE, IntVar, int),
    "image_chance": Item("popupMod", PERCENTAGE, IntVar, int),
    "web_chance": Item("webMod", PERCENTAGE, IntVar, int),
    "prompt_chance": Item("promptMod", PERCENTAGE, IntVar, int),
    "prompt_max_mistakes": Item("promptMistakes", NONNEGATIVE, IntVar, int),
    "opacity": Item("lkScaling", PERCENTAGE, IntVar, to_float),
    "timeout_enabled": Item("timeoutPopups", BOOLEAN, BooleanVar, bool),
    "timeout": Item("popupTimeout", NONNEGATIVE, IntVar, s_to_ms),
    "web_on_popup_close": Item("webPopup", BOOLEAN, BooleanVar, bool),
    "buttonless": Item("buttonless", BOOLEAN, BooleanVar, bool),
    "single_mode": Item("singleMode", BOOLEAN, BooleanVar, bool),
    "popup_subliminals": Item("popupSubliminals", BOOLEAN, BooleanVar, bool),
    "subliminal_chance": Item("subliminalsChance", PERCENTAGE, IntVar, int),
    "subliminal_opacity": Item("subliminalsAlpha", PERCENTAGE, IntVar, to_float),
    "max_subliminals": Item("maxSubliminals", NONNEGATIVE, IntVar, int),
    "denial_mode": Item("denialMode", BOOLEAN, BooleanVar, bool),
    "denial_chance": Item("denialChance", PERCENTAGE, IntVar, int),

    # Audio/Video
    "audio_chance": Item("audioMod", PERCENTAGE, IntVar, int),
    "max_audio": Item("maxAudio", NONNEGATIVE, IntVar, int),
    "video_chance": Item("vidMod", PERCENTAGE, IntVar, int),
    "video_volume": Item("videoVolume", PERCENTAGE, IntVar, int),
    "max_video_enabled": Item("maxVideoBool", BOOLEAN, BooleanVar, bool),
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
    "rotate_wallpaper": Item("rotateWallpaper", BOOLEAN, BooleanVar, bool),
    "wallpaper_timer": Item("wallpaperTimer", NONNEGATIVE, IntVar, s_to_ms),
    "wallpaper_variance": Item("wallpaperVariance", NONNEGATIVE, IntVar, s_to_ms),

    # Dangerous Settings
    "fill_drive": Item("fill", BOOLEAN, BooleanVar, bool),
    "fill_delay": Item("fill_delay", NONNEGATIVE, IntVar, lambda value: int(value) * 10),
    "replace_images": Item("replace", BOOLEAN, BooleanVar, bool),
    "replace_threshold": Item("replaceThresh", NONNEGATIVE, IntVar, int),
    "drive_path": Item("drivePath", STRING, StringVar, str),
    "panic_disabled": Item("panicDisabled", BOOLEAN, BooleanVar, bool),
    "run_at_startup": Item("start_on_logon", BOOLEAN, BooleanVar, bool),
    "show_on_discord": Item("showDiscord", BOOLEAN, BooleanVar, bool),

    # Basic Modes
    "lowkey_mode": Item("lkToggle", BOOLEAN, BooleanVar, bool),
    "lowkey_corner": Item("lkCorner", Schema(Union(int, Range(min=0, max=4))), IntVar, int),
    "moving_chance": Item("movingChance", PERCENTAGE, IntVar, int),
    "moving_random": Item("movingRandom", BOOLEAN, BooleanVar, bool),
    "moving_speed": Item("movingSpeed", NONNEGATIVE, IntVar, int),

    # Dangerous Modes
    "timer_mode": Item("timerMode", BOOLEAN, BooleanVar, bool),
    "timer_time": Item("timerSetupTime", NONNEGATIVE, IntVar, lambda value: int(value) * 60 * 1000),
    "timer_password": Item("safeword", STRING, StringVar, str),
    "mitosis_mode": Item("mitosisMode", BOOLEAN, BooleanVar, bool),
    "mitosis_strength": Item("mitosisStrength", NONNEGATIVE, IntVar, int),

    # Hibernate
    "hibernate_mode": Item("hibernateMode", BOOLEAN, BooleanVar, bool),
    "hibernate_fix_wallpaper": Item("fixWallpaper", BOOLEAN, BooleanVar, bool),
    "hibernate_type": Item("hibernateType", Schema(Union("Original", "Spaced", "Glitch", "Ramp", "Pump-Scare")), StringVar, str),
    "hibernate_delay_min": Item("hibernateMin", NONNEGATIVE, IntVar, s_to_ms),
    "hibernate_delay_max": Item("hibernateMax", NONNEGATIVE, IntVar, s_to_ms),
    "hibernate_activity": Item("wakeupActivity", NONNEGATIVE, IntVar, int),
    "hibernate_activity_length": Item("hibernateLength", NONNEGATIVE, IntVar, s_to_ms),

    # Corruption
    "corruption_mode": Item("corruptionMode", BOOLEAN, BooleanVar, bool),
    "corruption_full": Item("corruptionFullPerm", BOOLEAN, BooleanVar, bool),
    "corruption_trigger": Item("corruptionTrigger", Schema(Union("Timed", "Popup", "Launch")), StringVar, str),
    "corruption_fade": Item("corruptionFadeType", Schema(Union("Normal", "Abrupt")), StringVar, str),
    "corruption_time": Item("corruptionTime", NONNEGATIVE, IntVar, s_to_ms),
    "corruption_popups": Item("corruptionPopups", NONNEGATIVE, IntVar, int),
    "corruption_launches": Item("corruptionLaunches", NONNEGATIVE, IntVar, int),
    "corruption_wallpaper": Item("corruptionWallpaperCycle", BOOLEAN, BooleanVar, negation),
    "corruption_themes": Item("corruptionThemeCycle", BOOLEAN, BooleanVar, negation),
    "corruption_purity": Item("corruptionPurityMode", BOOLEAN, BooleanVar, bool),
    "corruption_dev_mode": Item("corruptionDevMode", BOOLEAN, BooleanVar, bool),

    # Troubleshooting
    "toggle_hibernate_skip": Item("toggleHibSkip", BOOLEAN, BooleanVar, bool),
    "toggle_internet": Item("toggleInternet", BOOLEAN, BooleanVar, bool),
    "toggle_mood_set": Item("toggleMoodSet", BOOLEAN, BooleanVar, bool),
    "mpv_subprocess": Item("mpvSubprocess", BOOLEAN, BooleanVar, bool),
}
# fmt: on


def first_launch_configure() -> None:
    if not Data.CONFIG.is_file():
        subprocess.run([sys.executable, Process.CONFIG, "--first-launch-configure"])


def load_config() -> dict:
    if not Data.CONFIG.is_file():
        Data.ROOT.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Assets.DEFAULT_CONFIG, Data.CONFIG)

    default_config = load_default_config()
    with open(Data.CONFIG, "r+") as f:
        config = json.loads(f.read())

        new_keys = False
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                new_keys = True

        if new_keys:
            f.seek(0)
            f.write(json.dumps(config))
            f.truncate()

    return config


def load_default_config() -> dict:
    with open(Assets.DEFAULT_CONFIG) as f:
        default_config = json.loads(f.read())

    return default_config


class Settings:
    def __init__(self) -> None:
        self.config = load_config()
        self.load_settings()
        logging.info(f"Config loaded: {self.config}")

    def load_settings(self) -> None:
        for name, item in CONFIG_ITEMS.items():
            value = self.config[item.key]
            item.schema(value)
            setattr(self, name, item.setting(value))

        # TODO: Include these in CONFIG_ITEMS?
        self.booru_tags = self.config["tagList"].replace(">", " ")  # TODO: Store in a better way
        self.disabled_monitors = self.config["disabledMonitors"]
        self.wallpapers = list(ast.literal_eval(self.config["wallpaperDat"]).values())  # TODO: Can fail, store in a better way
        self.drive_avoid_list = self.config["avoidList"].split(">")  # TODO: Store in a better way

        self.pack_path = Data.PACKS / self.pack_path if self.pack_path else DEFAULT_PACK_PATH

        self.timeout_enabled = self.timeout_enabled or self.lowkey_mode
        self.timeout = self.timeout if not self.lowkey_mode else self.delay
        self.web_on_popup_close = self.web_on_popup_close and not self.lowkey_mode
        self.subliminal_chance = self.subliminal_chance if self.popup_subliminals else 0
        self.denial_chance = self.denial_chance if self.denial_mode else 0

        self.max_video = self.max_video if self.max_video_enabled else float("inf")

        self.mitosis_mode = self.mitosis_mode or self.lowkey_mode
        self.mitosis_strength = self.mitosis_strength if not self.lowkey_mode else 1

        self.hibernate_fix_wallpaper = self.hibernate_fix_wallpaper and self.hibernate_mode

        import os_utils  # Circular import

        self.mpv_subprocess = self.mpv_subprocess and os_utils.is_linux()


ConfigVar = IntVar | BooleanVar | StringVar


class Vars:
    entries: dict[str, ConfigVar] = {}

    def __init__(self, config: dict) -> None:
        self.config = config

        self.config["packPath"] = self.config["packPath"] or "default"
        for name, item in CONFIG_ITEMS.items():
            value = self.config[item.key]
            item.schema(value)
            setattr(self, name, self.make(item.var, item.key))

    def make(self, var_init: type[ConfigVar], key: str) -> ConfigVar:
        value = self.config[key]
        var = var_init()
        match var:
            case IntVar():
                var.set(int(value))
            case BooleanVar():
                var.set(bool(value))
            case StringVar():
                var.set(value.strip())

        self.entries[key] = var
        return var
