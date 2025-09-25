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

if __name__ == "__main__":
    import os

    from paths import Data

    # Fix scaling on high resolution displays
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(0)  # Tell Windows that you aren't DPI aware.
    except Exception:
        pass  # Fails on non-Windows systems or if shcore is not available

    # Add mpv to PATH
    os.environ["PATH"] += os.pathsep + str(Data.ROOT)

import logging
from multiprocessing.connection import Client, Listener
from threading import Thread
from tkinter import Tk, simpledialog

import pyglet
from config.settings import Settings
from os_utils import set_wallpaper
from paths import CustomAssets
from state import State

ADDRESS = ("localhost", 6000)
AUTHKEY = b"Edgeware++"
PANIC_MESSAGE = "panic"


def panic(root: Tk, settings: Settings, state: State, condition: bool = True, disable: bool = True) -> None:
    def do_panic() -> None:
        if (disable and settings.panic_disabled) or not condition:
            return

        if settings.panic_lockout and state.panic_lockout_active:
            password = simpledialog.askstring("Panic", "Enter Panic Password")
            if password != settings.panic_lockout_password:
                return

        set_wallpaper(CustomAssets.panic_wallpaper())
        state.tray.stop()
        pyglet.app.exit()
        root.destroy()

    # Make sure panic code is executed in the main thread, otherwise
    # simpledialog will not work from most panic sources
    root.after(0, do_panic)


def start_panic_listener(root: Tk, settings: Settings, state: State) -> None:
    def listen() -> None:
        try:
            with Listener(address=ADDRESS, authkey=AUTHKEY) as listener:
                while True:
                    with listener.accept() as connection:
                        message = connection.recv()
                        if message == PANIC_MESSAGE:
                            panic(root, settings, state, disable=False)
        except OSError as e:
            logging.warning(f"Failed to start panic listener, some panic sources may not be functional. Reason: {e}")

    Thread(target=listen, daemon=True).start()


def send_panic() -> None:
    with Client(address=ADDRESS, authkey=AUTHKEY) as connection:
        connection.send(PANIC_MESSAGE)


if __name__ == "__main__":
    send_panic()
