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
import multiprocessing
import random
import time
import webbrowser
from collections.abc import Callable
from multiprocessing.connection import Connection
from threading import Thread
from tkinter import Tk

import pystray
from config.settings import Settings
from desktop_notifier.common import Attachment, Icon
from desktop_notifier.sync import DesktopNotifierSync
from os_utils import make_shortcut, set_wallpaper
from pack import Pack
from panic import panic
from paths import CustomAssets, Process
from PIL import Image
from pynput import keyboard
from pypresence import Presence
from roll import roll
from state import State


def open_web(pack: Pack, web: str | None = None) -> None:
    web = web or pack.random_web()
    if web:
        # webbrowser.open can pause Edgeware if opening the browser takes a long time
        Thread(target=lambda: webbrowser.open(web), daemon=True).start()


def display_notification(settings: Settings, pack: Pack, notification: str | None = None) -> None:
    notification = notification or pack.random_notification()
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
    menu = [pystray.MenuItem("Panic", lambda: panic(root, settings, state))]
    if settings.hibernate_mode:

        def skip_hibernate() -> None:
            if state.hibernate_active:
                return

            root.after_cancel(state.hibernate_id)
            hibernate_activity()

        menu.append(pystray.MenuItem("Skip to Hibernate", skip_hibernate))

    state.tray = pystray.Icon("Edgeware++", Image.open(pack.icon), "Edgeware++", menu)
    Thread(target=state.tray.run, daemon=True).start()


def make_desktop_icons(settings: Settings) -> None:
    if settings.desktop_icons:
        make_shortcut("Edgeware++", Process.MAIN, CustomAssets.icon())
        make_shortcut("Edgeware++ Config", Process.CONFIG, CustomAssets.config_icon())
        make_shortcut("Edgeware++ Panic", Process.PANIC, CustomAssets.panic_icon())


def handle_wallpaper(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    def rotate(previous: str = None) -> None:
        if settings.hibernate_fix_wallpaper and not state.hibernate_active and state.popup_number == 0:
            return

        wallpapers = settings.wallpapers.copy()
        if previous:
            wallpapers.remove(previous)

        wallpaper = random.choice(wallpapers)
        set_wallpaper(pack.paths.root / wallpaper)

        t = settings.wallpaper_timer
        v = settings.wallpaper_variance
        root.after(t + random.randint(-v, v), lambda: rotate(wallpaper))

    if settings.corruption_mode and settings.corruption_wallpaper:
        return

    if settings.rotate_wallpaper and len(settings.wallpapers) > 1:
        rotate()
    elif pack.wallpaper:
        set_wallpaper(pack.wallpaper)


def handle_discord(settings: Settings, pack: Pack) -> None:
    if not settings.show_on_discord:
        return

    try:
        presence = Presence("820204081410736148")
        presence.connect()
        presence.update(state=pack.discord.text, large_image=pack.discord.image, start=int(time.time()))
    except Exception as e:
        logging.warning(f"Setting Discord presence failed. Reason: {e}")


def handle_panic_lockout(root: Tk, settings: Settings, state: State) -> None:
    def panic_lockout_over() -> None:
        state.panic_lockout_active = False

    if settings.panic_lockout:
        state.panic_lockout_active = True
        root.after(settings.panic_lockout_time, panic_lockout_over)


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


def keyboard_listener(connection: Connection) -> None:
    def callback(type: str) -> None:
        return lambda key: connection.send((type, str(key)))

    with keyboard.Listener(on_press=callback("press"), on_release=callback("release")) as listener:
        listener.join()


def handle_keyboard(root: Tk, settings: Settings, state: State) -> None:
    alt = [str(keyboard.Key.alt), str(keyboard.Key.alt_gr), str(keyboard.Key.alt_l), str(keyboard.Key.alt_r)]

    def receive() -> None:
        while True:
            try:
                type, key = parent_connection.recv()
            except EOFError:
                break  # Panic

            if type == "press" and key in alt:
                state.alt_held = True
            if type == "release":
                if key in alt:
                    state.alt_held = False
                panic(root, settings, state, condition=(key == settings.global_panic_key))

    parent_connection, child_connection = multiprocessing.Pipe()
    state.keyboard_process = multiprocessing.Process(target=keyboard_listener, args=(child_connection,))
    state.keyboard_process.start()

    Thread(target=receive).start()
