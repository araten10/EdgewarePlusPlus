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
from pack import Pack
from paths import Data
from roll import roll
from settings import Settings
from state import State


def corruption_danger_check(settings: Settings, pack: Pack) -> None:
    if not (settings.corruption_mode and settings.corruption_full):
        return

    dangers = []
    for level in pack.corruption_levels:
        if level.config is not None:
            for key, value in level.config.items():
                if key in settings.corruption_danger and key not in dangers:
                    dangers.append(key)

                range = settings.corruption_safe_range.get(key)
                if range:
                    min, max = range
                    if min and value < min:
                        dangers.append(f"Low {key} ({value})")
                    if max and value > max:
                        dangers.append(f"High {key} ({value})")

    if dangers:
        proceed = messagebox.askyesno(
            "Corruption config warning",
            "You are using corruption in full permission mode, meaning your pack is capable of changing Edgeware's settings\n\n"
            f"Your pack changes the following settings which may be dangerous: {dangers}\n\n"
            "Are you sure you want to proceed?",
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

    if settings.corruption_wallpaper:
        os_utils.set_wallpaper(pack.paths.root / (level.wallpaper or pack.wallpaper))

    if settings.corruption_full:
        for key, value in level.config.items():
            if key in settings.corruption_block or (not settings.corruption_themes and key == "themeType"):
                continue

            if settings.corruption_dev_mode:
                logging.info(f"Changing {key} to {value}")
            settings.config[key] = value

        # Reload settings from the config dict so the changes get applied
        settings.load_settings()


def update_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    state.corruption_level = next_corruption_level(settings, pack, state)
    apply_corruption_level(settings, pack, state)


def fade_chance(settings: Settings, state: State) -> float:
    match settings.corruption_fade:
        case "Normal":
            chance = corruption_level_progress(settings, state)
            if settings.corruption_dev_mode:
                logging.info(f"Current next mood chance: {chance:.1%}")
            return chance
        case "Abrupt":
            return 0
        case _:
            logging.warning(f"Unknown corruption fade {settings.corruption_fade}.")
            return 0


def corruption_level_progress(settings: Settings, state: State) -> float:
    match settings.corruption_trigger:
        case "Timed":
            return (time.time() - state.corruption_time_start) / (settings.corruption_time / 1000)
        case "Popup":
            return state.corruption_popup_number / settings.corruption_popups
        case "Launch":
            return state.corruption_launches_number / (settings.corruption_launches * state.corruption_level)
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

    pack.active_moods = lambda: pack.corruption_levels[
        (next_corruption_level(settings, pack, state) if roll(fade_chance(settings, state)) else state.corruption_level) - 1
    ].moods

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
        case _:
            logging.error(f"Unknown corruption trigger {settings.corruption_trigger}.")
