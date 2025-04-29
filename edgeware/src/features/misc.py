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

import json
import logging
import random
import subprocess
import time
import webbrowser
from collections.abc import Callable
from threading import Thread
from tkinter import Tk

import os_utils
import pystray
from desktop_notifier.common import Attachment, Icon
from desktop_notifier.sync import DesktopNotifierSync
from pack import Pack
from panic import panic
from paths import CustomAssets, Data, Process
from PIL import Image
from pygame import mixer
from pynput import keyboard
from pypresence import Presence
from roll import roll
from settings import Settings
from state import State


def play_audio(pack: Pack) -> None:
    # Pygame will not stop additional sounds from being played when the max is
    # reached, so we need to check if there are empty channels
    audio = pack.random_audio()
    if audio and mixer.find_channel():
        sound = mixer.Sound(str(audio))
        # TODO POTENTIAL SETTINGS: Volume, fadein, fadeout, separating music from sounds
        # https://www.pygame.org/docs/ref/mixer.html#pygame.mixer.Sound
        sound.play()


def open_web(pack: Pack) -> None:
    web = pack.random_web()
    if web:
        webbrowser.open(web)


def display_notification(settings: Settings, pack: Pack) -> None:
    notification = pack.random_notification()
    if not notification:
        return

    image = pack.random_image()
    notifier = DesktopNotifierSync(app_name="Edgeware++", app_icon=Icon(pack.icon))
    notifier.send(
        title=pack.info.name,
        message=notification,
        attachment=Attachment(image) if roll(settings.notification_image_chance) and image else None,
    )


def make_tray_icon(root: Tk, settings: Settings, pack: Pack, state: State, hibernate_activity: Callable[[], None]) -> None:
    menu = [] if settings.panic_disabled else [pystray.MenuItem("Panic", lambda: panic(root, settings, state))]
    if settings.hibernate_mode:

        def skip_hibernate() -> None:
            if state.hibernate_active:
                return

            root.after_cancel(state.hibernate_id)
            hibernate_activity()

        menu.append(pystray.MenuItem("Skip to Hibernate", skip_hibernate))

    icon = pystray.Icon("Edgeware++", Image.open(pack.icon), "Edgeware++", menu)
    Thread(target=icon.run, daemon=True).start()


def make_desktop_icons(settings: Settings) -> None:
    if settings.desktop_icons:
        os_utils.make_shortcut("Edgeware++", Process.MAIN, CustomAssets.icon())
        os_utils.make_shortcut("Edgeware++ Config", Process.CONFIG, CustomAssets.config_icon())
        os_utils.make_shortcut("Edgeware++ Panic", Process.PANIC, CustomAssets.panic_icon())


def handle_booru_download(settings: Settings, state: State) -> None:
    if not settings.booru_download:
        return

    root = f"https://{settings.booru_name}.booru.org"
    url = f"{root}/index.php?page=post&s=list&tags={settings.booru_tags}"

    # TODO: Reimplement with a different library


def handle_wallpaper(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    def rotate(previous: str = None) -> None:
        if settings.hibernate_fix_wallpaper and not state.hibernate_active and state.popup_number == 0:
            return

        wallpapers = settings.wallpapers.copy()
        if previous:
            wallpapers.remove(previous)

        wallpaper = random.choice(wallpapers)
        os_utils.set_wallpaper(pack.paths.root / wallpaper)

        t = settings.wallpaper_timer
        v = settings.wallpaper_variance
        root.after(t + random.randint(-v, v), lambda: rotate(wallpaper))

    if settings.corruption_mode and settings.corruption_wallpaper:
        return

    if settings.rotate_wallpaper and len(settings.wallpapers) > 1:
        rotate()
    else:
        os_utils.set_wallpaper(pack.wallpaper)


def handle_discord(root: Tk, settings: Settings, pack: Pack) -> None:
    if not settings.show_on_discord:
        return

    try:
        presence = Presence("820204081410736148")
        presence.connect()
        presence.update(state=pack.discord.text, large_image=pack.discord.image, start=int(time.time()))
    except Exception as e:
        logging.warning(f"Setting Discord presence failed. Reason: {e}")


def handle_timer_mode(root: Tk, settings: Settings, state: State) -> None:
    def timer_over() -> None:
        state.timer_active = False

    if settings.timer_mode:
        state.timer_active = True
        root.after(settings.timer_time, timer_over)


def mitosis_popup(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    # Imports done here to avoid circular imports
    from features.image_popup import ImagePopup
    from features.video_popup import VideoPopup

    try:
        popup = random.choices([ImagePopup, VideoPopup], [settings.image_chance, settings.video_chance], k=1)[0]
    except ValueError:
        popup = ImagePopup  # Exception thrown when both chances are 0
    popup(root, settings, pack, state)


def handle_mitosis_mode(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if settings.mitosis_mode:
        # Import done here to avoid circular imports

        def observer() -> None:
            if state.popup_number == 0:
                mitosis_popup(root, settings, pack, state)

        state._popup_number.attach(observer)
        mitosis_popup(root, settings, pack, state)


def handle_keyboard(root: Tk, settings: Settings, state: State) -> None:
    alt = [keyboard.Key.alt, keyboard.Key.alt_gr, keyboard.Key.alt_l, keyboard.Key.alt_r]

    def on_press(key: keyboard.Key) -> None:
        if key in alt:
            state.alt_held = True

    def on_release(key: keyboard.Key) -> None:
        if key in alt:
            state.alt_held = False
        panic(root, settings, state, global_key=str(key))

    keyboard.Listener(on_press=on_press, on_release=on_release).start()
