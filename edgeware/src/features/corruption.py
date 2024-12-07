import logging
from tkinter import Tk

from pack import Pack
from paths import Data, Resource
from settings import Settings
from state import State
from utils import utils


def apply_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    level = pack.corruption_levels[state.corruption_level - 1]
    pack.active_moods.media = level.moods.copy()
    if settings.corruption_wallpaper:
        utils.set_wallpaper(Resource.ROOT / (level.wallpaper or pack.wallpaper))
    # if settings.corruption_full:


def update_corruption_level(settings: Settings, pack: Pack, state: State) -> None:
    if settings.corruption_purity:
        state.corruption_level -= 1 if state.corruption_level > 1 else 0
    else:
        state.corruption_level += 1 if state.corruption_level < len(pack.corruption_levels) else 0
    apply_corruption_level(settings, pack, state)


def timed(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    update_corruption_level(settings, pack, state)
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
    else:
        apply_corruption_level(pack, state)
        with open(Data.CORRUPTION_LAUNCHES, "w") as f:
            f.seek(0)
            f.write(str(1))
            f.truncate()


def handle_corruption(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if not settings.corruption_mode:
        return

    if settings.corruption_purity:
        state.corruption_level = len(pack.corruption_levels)

    match settings.corruption_trigger:
        case "Timed":
            apply_corruption_level(settings, pack, state)
            root.after(settings.corruption_time, lambda: timed(root, settings, pack, state))
        case "Popup":
            apply_corruption_level(settings, pack, state)
            popup(settings, pack, state)
        case "Launch":
            launch(settings, pack, state)
        case _:
            logging.error(f"Unknown corruption trigger {settings.corruption_trigger}.")
