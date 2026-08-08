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
import sys
import threading
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
        logging.info(f"DO_PANIC: entered, disable={disable}, condition={condition}, "
                     f"panic_disabled={settings.panic_disabled}, "
                     f"thread={threading.current_thread().name}")
        if (disable and settings.panic_disabled) or not condition:
            logging.info("DO_PANIC: early return (disabled/condition)")
            return

        if settings.panic_lockout and state.panic_lockout_active:
            password = simpledialog.askstring("Panic", "Enter Panic Password")
            if password != settings.panic_lockout_password:
                return

        set_wallpaper(CustomAssets.panic_wallpaper())
        if state.keyboard_process:
            try:
                state.keyboard_process.terminate()
                state.keyboard_process.join(timeout=2)
            except Exception:
                pass
        if state.tray and sys.platform == "darwin":
            # pystray's public API (visible=False, stop()) only hides the
            # button or stops the event loop — it does NOT fully remove the
            # NSStatusItem from the status bar. The only way to do that is
            # via the private _status_bar / _status_item attributes, which
            # is why we pin pystray==0.19.5 in requirements.txt.
            try:
                state.tray._status_bar.removeStatusItem_(state.tray._status_item)
            except Exception as e:
                logging.debug(f"Error removing status item during panic: {e}")

            # pyglet.app.run() is not used on macOS (tkinter drives the
            # event loop), so pyglet.app.exit() is not needed either.

            # Close all open popups so their video players / render loops
            # are stopped BEFORE we exit. Each popup.close() must fully
            # join its mpv/pyglet threads, or the mpv event thread can
            # race with teardown.
            remaining = list(state.popups)
            while remaining:
                popup = remaining.pop(0)
                try:
                    popup.close()
                except Exception as e:
                    logging.debug(f"Error closing popup during panic: {e}")
                # Remove from popups list to avoid double-close
                if popup in state.popups:
                    state.popups.remove(popup)

            # On macOS background threads (pyglet tick, keyboard receive
            # handler, popup timers) call into Python via _tkinter C code,
            # which calls PyEval_RestoreThread.  If the GIL is released by
            # Tcl/Cocoa event polling during Tk or Python teardown a
            # fatal Python error occurs:
            #   Fatal Python error: PyEval_RestoreThread: NULL tstate
            #
            # Strategy:
            # 1. Set a shutdown flag so new callbacks are not scheduled.
            # 2. Close the keyboard receive connection so the receive
            #    thread dies immediately (unblocks on recv()).
            # 3. Cancel the tick_pyglet loop so it stops scheduling new
            #    callbacks every 16ms.
            # 4. Queue root.quit() to stop the Tk mainloop cleanly.
            # 5. Use a threading.Event so os._exit(0) is only called
            #    after mainloop() has returned — this avoids the race
            #    where a Tk after() callback fires into Python via
            #    _tkinter C code after the GIL state is corrupted.
            state._panic_shutdown = True

            # Close the keyboard receive pipe so the receive thread's
            # parent_conn.recv() unblocks with EOFError/OSError.
            if state.keyboard_receive_conn:
                try:
                    state.keyboard_receive_conn.close()
                except Exception:
                    pass

            # Cancel the tick_pyglet callback chain
            if state._tick_pyglet_id is not None:
                try:
                    root.after_cancel(state._tick_pyglet_id)
                except Exception:
                    pass

            logging.info("DO_PANIC: scheduling root.quit()")
            root.after(0, root.quit)
            return
        else:
            if state.tray:
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
                        logging.info(f"PANIC_LISTENER: received message '{message}'")
                        if message == PANIC_MESSAGE:
                            logging.info("PANIC_LISTENER: dispatching panic (disable=False)")
                            panic(root, settings, state, disable=False)
                        elif message == "panic_tray":
                            logging.info("PANIC_LISTENER: dispatching tray panic (disable=True)")
                            panic(root, settings, state, disable=True)
        except OSError as e:
            logging.warning(f"Failed to start panic listener, some panic sources may not be functional. Reason: {e}")

    Thread(target=listen, daemon=True).start()


def send_panic() -> None:
    with Client(address=ADDRESS, authkey=AUTHKEY) as connection:
        connection.send(PANIC_MESSAGE)


def send_panic_tray() -> None:
    """Send a panic signal via IPC, mimicking tray menu click.

    Used by the tray menu callback to avoid calling panic() directly
    from pystray's Cocoa callback thread, which can cause threading issues.
    """
    with Client(address=ADDRESS, authkey=AUTHKEY) as connection:
        connection.send("panic_tray")


if __name__ == "__main__":
    send_panic()
