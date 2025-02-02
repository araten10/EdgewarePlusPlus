import logging
import sys
import time
from random import random
from tkinter import Tk, messagebox

from features.corruption_config import CorruptionConfig
from pack import Pack
from paths import Data
from roll import RollTarget, roll_targets
from settings import Settings
from state import State
from utils import utils


def corruption_danger_check(settings: Settings, pack: Pack) -> None:
    if not (settings.corruption_mode and settings.corruption_full):
        return

    dangers = []
    for level in pack.corruption_levels:
        if level.config is not None:
            for key, value in level.config.items():
                if key in CorruptionConfig.DANGEROUS and key not in dangers:
                    dangers.append(key)

                range = CorruptionConfig.SAFE_RANGE.get(key)
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


def apply_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    level = pack.corruption_levels[state.corruption_level - 1]
    pack.active_moods = level.moods.copy()

    if settings.corruption_wallpaper:
        utils.set_wallpaper(pack.paths.root / (level.wallpaper or pack.wallpaper))

    if settings.corruption_full:
        for key, value in level.config.items():
            if key in CorruptionConfig.BLACKLIST:
                continue

            if settings.corruption_dev_mode:
                logging.info(f"Changing {key} to {value}")
            settings.config[key] = value

        # Reload settings from the config dict so the changes get applied
        settings.load_settings()


def update_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    if settings.corruption_purity:
        state.corruption_level -= 1 if state.corruption_level > 1 else 0
    else:
        state.corruption_level += 1 if state.corruption_level < len(pack.corruption_levels) else 0
    apply_corruption_level(settings, pack, state)


def handle_corruption_fade(settings: Settings, pack: Pack, state: State, targets: list[RollTarget]) -> None:
    if roll_fade(settings, state):
        # If roll succeeds, set corruption level to one higher (or lower) than normal
        if settings.corruption_purity:
            state.corruption_level -= 1 if state.corruption_level > 1 else 0
        else:
            state.corruption_level += 1 if state.corruption_level < len(pack.corruption_levels) else 0

        # Bandaid fix, do something better
        true_wallpaper_setting = settings.corruption_wallpaper
        if true_wallpaper_setting == True:
            settings.corruption_wallpaper = False

        apply_corruption_level(settings, pack, state)
        # Roll and spawn popup as normal, now with new corruption level
        roll_targets(settings, targets)
        # Revert back to original corruption level and apply
        if settings.corruption_purity:
            state.corruption_level += 1 if state.corruption_level < len(pack.corruption_levels) else 0
        else:
            state.corruption_level -= 1 if state.corruption_level > 1 else 0
        apply_corruption_level(settings, pack, state)

        # Bandaid fix, do something better
        if true_wallpaper_setting == True:
            settings.corruption_wallpaper = True
    else:
        roll_targets(settings, targets)


def roll_fade(settings: Settings, state: State) -> bool:
    match settings.corruption_trigger:
        case "Timed":
            fade_percentage = (time.time() - state.corruption_time_start) / (settings.corruption_time / 1000)
        case "Popup":
            fade_percentage = state.corruption_popup_number / settings.corruption_popups
        case "Launch":
            fade_percentage = state.corruption_launches_number / (settings.corruption_launches * state.corruption_level)
        case _:
            logging.error(f"Unknown corruption trigger {settings.corruption_trigger}.")
    if settings.corruption_dev_mode and fade_percentage:
        print(f"Current next mood chance: {fade_percentage:.1%}")
    # Take results and roll them
    match settings.corruption_fade:
        case "Normal":
            if fade_percentage > random():
                return True
            else:
                return False
        case _:
            logging.error(f"Unknown corruption fade {settings.corruption_fade}.")


def timed(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    update_corruption_level(settings, pack, state)
    state.corruption_time_start = time.time()
    root.after(settings.corruption_time, lambda: timed(root, settings, pack, state))


def popup(settings: Settings, pack: Pack, state: State) -> None:
    previous_popup_number = 0
    total_popup_number = 0

    def observer() -> None:
        nonlocal previous_popup_number, total_popup_number
        if state.popup_number > previous_popup_number:
            total_popup_number += 1

        previous_popup_number = state.popup_number

        if total_popup_number >= settings.corruption_popups:
            update_corruption_level(settings, pack, state)
            total_popup_number = 0

        state.corruption_popup_number = total_popup_number

    state._popup_number.attach(observer)


def launch(settings: Settings, pack: Pack, state: State) -> None:
    if Data.CORRUPTION_LAUNCHES.is_file():
        with open(Data.CORRUPTION_LAUNCHES, "r+") as f:
            launches = int(f.readline())

            for i in range(len(pack.corruption_levels)):
                if launches >= (settings.corruption_launches * i):
                    update_corruption_level(settings, pack, state)

            f.seek(0)
            f.write(str(launches + 1))
            f.truncate()
            state.corruption_launches_number = launches
    else:
        apply_corruption_level(settings, pack, state)
        with open(Data.CORRUPTION_LAUNCHES, "w") as f:
            f.seek(0)
            f.write(str(1))
            f.truncate()
        state.corruption_launches_number = 1


def handle_corruption(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if not settings.corruption_mode:
        return

    if settings.corruption_purity:
        state.corruption_level = len(pack.corruption_levels)

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
