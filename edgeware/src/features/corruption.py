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
import sys
import time
from tkinter import Tk, messagebox

import os_utils
from config.items import CONFIG_DANGER, CORRUPTION_BLOCK, DangerLevel
from config.settings import Settings
from pack import Pack
from pack.data import MoodSet
from paths import Data
from roll import roll
from state import State


def corruption_danger_check(settings: Settings, pack: Pack) -> None:
    if not (settings.corruption_mode and settings.corruption_full):
        return

    danger_levels = {
        DangerLevel.EXTREME: [],
        DangerLevel.MAJOR: [],
        DangerLevel.MEDIUM: [],
        DangerLevel.MINOR: [],
    }

    for level in pack.corruption_levels:
        if level.config is None:
            continue

        for key, value in level.config.items():
            danger = CONFIG_DANGER.get(key)
            if not danger:
                continue

            warning = f"\n•{danger.warning or key}"
            if danger.check(value) and warning not in danger_levels[danger.level]:
                danger_levels[danger.level].append(warning)

    danger_num = 0
    warnings = ""
    for level, dangers in danger_levels.items():
        danger_num += len(dangers)
        if dangers:
            warnings += f"\n\n{level.value.capitalize()}{''.join(dangers)}"

    if danger_num:
        proceed = messagebox.askyesno(
            "Corruption Config Warning",
            "You are using corruption in full permission mode, meaning your pack is capable of changing Edgeware's settings.\n\n"
            f"Your pack changes {danger_num} setting(s) which may be dangerous. Are you sure you want to proceed? {warnings}",
            icon="warning",
        )
        if not proceed:
            sys.exit()


def next_corruption_level(settings: Settings, pack: Pack, state: State) -> int:
    if settings.corruption_purity:
        return state.corruption_level - (1 if state.corruption_level > 1 else 0)
    else:
        return state.corruption_level + (1 if state.corruption_level < len(pack.corruption_levels) else 0)


def apply_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    level = pack.corruption_levels[state.corruption_level - 1]

    pack.active_moods.update(level.added_moods)
    pack.active_moods.difference_update(level.removed_moods)

    if settings.corruption_wallpaper and level.wallpaper:
        os_utils.set_wallpaper(pack.paths.root / level.wallpaper)

    if settings.corruption_full:
        for key, value in level.config.items():
            if key in CORRUPTION_BLOCK or (not settings.corruption_themes and key == "themeType"):
                logging.info(f"Change of {key} blocked")
                continue

            if settings.corruption_dev_mode:
                logging.info(f"Changing {key} to {value}")
            settings.config[key] = value

        # Reload settings from the config dict so the changes get applied
        settings.load_settings()


def update_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    state.corruption_level = next_corruption_level(settings, pack, state)
    apply_corruption_level(settings, pack, state)


def fade(settings: Settings, pack: Pack, state: State) -> MoodSet:
    match settings.corruption_fade:
        case "Normal":
            chance = corruption_level_progress(settings, state)
            if settings.corruption_dev_mode:
                logging.info(f"Current next mood chance: {chance:.1%}")
        case "Abrupt":
            chance = 0
        case _:
            chance = 0
            logging.warning(f"Unknown corruption fade {settings.corruption_fade}.")

    if not roll(chance):
        return pack.active_moods

    next_level = pack.corruption_levels[next_corruption_level(settings, pack, state)]
    return pack.active_moods | next_level.added_moods - next_level.removed_moods


def corruption_level_progress(settings: Settings, state: State) -> float:
    match settings.corruption_trigger:
        case "Timed":
            return (time.time() - state.corruption_time_start) / (settings.corruption_time / 1000)
        case "Popup":
            return state.corruption_popup_number / settings.corruption_popups
        case "Launch":
            return state.corruption_launches_number / (settings.corruption_launches * state.corruption_level)
        case "Script":
            return 0
        case _:
            logging.warning(f"Unknown corruption trigger {settings.corruption_trigger}.")
            return 0


def timed(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    update_corruption_level(settings, pack, state)
    state.corruption_time_start = time.time()
    root.after(settings.corruption_time, lambda: timed(root, settings, pack, state))


def popup(settings: Settings, pack: Pack, state: State) -> None:
    previous_popup_number = 0

    def observer() -> None:
        nonlocal previous_popup_number
        if state.popup_number > previous_popup_number:
            state.corruption_popup_number += 1

        previous_popup_number = state.popup_number

        if state.corruption_popup_number >= settings.corruption_popups:
            update_corruption_level(settings, pack, state)
            state.corruption_popup_number = 0

    state._popup_number.attach(observer)


def launch(settings: Settings, pack: Pack, state: State) -> None:
    if Data.CORRUPTION_LAUNCHES.is_file():
        with open(Data.CORRUPTION_LAUNCHES, "r+") as f:
            launches = int(f.readline())

            state.corruption_launches_number = launches
            for i in range(len(pack.corruption_levels)):
                if launches >= (settings.corruption_launches * i):
                    update_corruption_level(settings, pack, state)

            f.seek(0)
            f.write(str(launches + 1))
            f.truncate()
    else:
        apply_corruption_level(settings, pack, state)
        with open(Data.CORRUPTION_LAUNCHES, "w") as f:
            f.seek(0)
            f.write(str(1))
            f.truncate()


def handle_corruption(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if not settings.corruption_mode:
        return

    if settings.corruption_purity:
        state.corruption_level = len(pack.corruption_levels)

    pack.get_active_moods = lambda: fade(settings, pack, state)

    match settings.corruption_trigger:
        case "Timed":
            apply_corruption_level(settings, pack, state)
            state.corruption_time_start = time.time()
            root.after(settings.corruption_time, lambda: timed(root, settings, pack, state))
        case "Popup":
            apply_corruption_level(settings, pack, state)
            popup(settings, pack, state)
        case "Launch":
            launch(settings, pack, state)
        case "Script":
            apply_corruption_level(settings, pack, state)
        case _:
            logging.error(f"Unknown corruption trigger {settings.corruption_trigger}.")
