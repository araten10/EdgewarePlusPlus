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
import os
import random
import sys
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
from os_utils import check_accessibility_permission, check_input_monitoring_permission, make_shortcut, send_panic_tray, set_wallpaper, show_accessibility_dialog, show_input_monitoring_dialog
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


def send_notification(settings: Settings, pack: Pack, notification: str | None = None) -> None:
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
    def _tray_panic():
        try:
            logging.info("TRAY: panic callback entered")
            send_panic_tray()
            logging.info("TRAY: IPC message sent successfully")
        except Exception as e:
            logging.error(f"TRAY: exception in panic callback: {e}", exc_info=True)
            raise
    menu = [pystray.MenuItem("Panic", _tray_panic)]
    if settings.hibernate_mode:

        def skip_hibernate() -> None:
            if state.hibernate_active:
                return

            root.after_cancel(state.hibernate_id)
            hibernate_activity()

        menu.append(pystray.MenuItem("Skip to Hibernate", skip_hibernate))

    if sys.platform == "darwin":
        import AppKit
        state.tray = pystray.Icon(
            "Edgeware++", Image.open(pack.icon), "Edgeware++", menu,
            darwin_nsapplication=AppKit.NSApplication.sharedApplication(),
        )
        state.tray.run_detached()
    else:
        state.tray = pystray.Icon("Edgeware++", Image.open(pack.icon), "Edgeware++", menu)
        # state.tray.run()
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

        def observer() -> None:
            if state.popup_number == 0:
                mitosis_popup(root, settings, pack, state)

        state._popup_number.attach(observer)
        mitosis_popup(root, settings, pack, state)


def _keyboard_listener_process(child_conn: Connection) -> None:
    """Target for the keyboard listener subprocess.

    Runs pynput's CGEventTap on the subprocess's main thread, which is
    required on macOS for TSM (Text Services Manager) APIs to work
    correctly.  Sends (type, key_str) tuples back via the pipe.
    """
    from utils import init_logging
    init_logging("keyboard_listener")
    logging.info("Keyboard listener subprocess started (PID %d)", os.getpid())

    def callback(event_type: str) -> Callable:
        return lambda key: child_conn.send((event_type, str(key)))

    try:
        logging.info("Creating pynput keyboard Listener")
        with keyboard.Listener(on_press=callback("press"), on_release=callback("release")) as listener:
            logging.info("Pynput listener thread alive: %s", listener.is_alive())
            listener.join()
    except Exception as exc:
        logging.error("Keyboard listener subprocess crashed: %s", exc, exc_info=True)
    finally:
        try:
            child_conn.close()
        except Exception:
            pass


def stop_keyboard_listener(state: State) -> None:
    """Stop any running keyboard listener.

    On macOS this stops the in-process pynput listener; on other
    platforms it terminates the pynput subprocess and closes the receive pipe.
    """
    if sys.platform == "darwin":
        listener = getattr(state, "keyboard_listener", None)
        if listener is not None:
            try:
                listener.stop()
            except Exception:
                pass
            state.keyboard_listener = None
        return

    if state.keyboard_process and state.keyboard_process.is_alive():
        try:
            state.keyboard_process.terminate()
            state.keyboard_process.join(timeout=2)
        except Exception:
            pass
    if state.keyboard_receive_conn:
        try:
            state.keyboard_receive_conn.close()
        except Exception:
            pass
        state.keyboard_receive_conn = None


def handle_keyboard(root: Tk, settings: Settings, state: State, accessibility_granted: bool = True) -> None:
    if not accessibility_granted:
        logging.warning("Skipping keyboard listener: Accessibility permission not granted")
        return

    if sys.platform == "darwin":
        _handle_keyboard_darwin(root, settings, state)
        return

    alt = [str(keyboard.Key.alt), str(keyboard.Key.alt_gr), str(keyboard.Key.alt_l), str(keyboard.Key.alt_r)]

    def receive() -> None:
        while True:
            try:
                event_type, key_str = parent_conn.recv()
            except (EOFError, OSError):
                return

            if event_type == "press" and key_str in alt:
                root.after(0, lambda: setattr(state, "alt_held", True))
            if event_type == "release":
                if key_str in alt:
                    root.after(0, lambda: setattr(state, "alt_held", False))
                if key_str == settings.global_panic_key:
                    _root, _settings = root, settings
                    root.after(0, lambda: panic(_root, _settings, state))

    ctx = multiprocessing.get_context("spawn")
    parent_conn, child_conn = ctx.Pipe()
    state.keyboard_process = ctx.Process(target=_keyboard_listener_process, args=(child_conn,), daemon=True)
    state.keyboard_process.start()
    child_conn.close()
    state.keyboard_receive_conn = parent_conn

    Thread(target=receive, daemon=True).start()


def _handle_keyboard_darwin(root: Tk, settings: Settings, state: State) -> None:
    """macOS keyboard listener using a direct in-process Quartz CGEventTap.

    A pynput subprocess does not reliably receive key events inside the bundled
    .app (Input Monitoring trust is lost), and running pynput in-process crashes or
    never receives physical keys in the frozen app. The raw Quartz CGEventTap runs
    in-process on a daemon thread and is polled via Tk's after(), avoiding both
    subprocess permission inheritance and pynput's macOS TSM main-thread crash.
    """
    from os_utils.keyboard_listener_darwin import DarwinKeyboardListener

    def on_panic() -> None:
        if state.panic_shutdown:
            return
        _root, _settings = root, settings
        try:
            root.after(0, lambda: panic(_root, _settings, state))
        except Exception as e:
            logging.warning(f"CGEventTap on_panic scheduling failed: {e}")

    def on_alt_change(held: bool) -> None:
        if state.panic_shutdown:
            return
        root.after(0, lambda: setattr(state, "alt_held", held))

    alt_names = [
        str(keyboard.Key.alt), str(keyboard.Key.alt_gr),
        str(keyboard.Key.alt_l), str(keyboard.Key.alt_r),
    ]

    listener = DarwinKeyboardListener(
        target_key=settings.global_panic_key,
        on_panic=on_panic,
        alt_keys=alt_names,
        on_alt_change=on_alt_change,
    )

    if not listener.start():
        logging.error("Failed to start macOS CGEventTap keyboard listener (Input Monitoring permission likely missing)")
        root.after(0, lambda: show_input_monitoring_dialog(root))
        return

    state.keyboard_listener = listener
    logging.info(f"macOS CGEventTap keyboard listener started for key: {settings.global_panic_key}")

    def poll_listener() -> None:
        if state.panic_shutdown:
            return
        try:
            listener.poll()
        except Exception as e:
            logging.warning(f"CGEventTap poll error: {e}")
        root.after(listener._poll_interval_ms, poll_listener)

    # Start polling from the main thread.
    root.after(0, poll_listener)
