if __name__ == "__main__":
    import os

    from paths import Data

    # Required on Windows
    os.environ["PATH"] += os.pathsep + str(Data.ROOT)

import logging
from multiprocessing.connection import Client, Listener
from threading import Thread
from tkinter import Tk, simpledialog

import os_utils
from paths import CustomAssets
from settings import Settings
from state import State

ADDRESS = ("localhost", 6000)
AUTHKEY = b"Edgeware++"
PANIC_MESSAGE = "panic"


def panic(root: Tk, settings: Settings, state: State, legacy_key: str | None = None, global_key: str | None = None) -> None:
    if legacy_key and (settings.panic_disabled or legacy_key != settings.panic_key):
        return

    if global_key and (settings.panic_disabled or global_key != settings.global_panic_key):
        return

    if settings.timer_mode and state.timer_active:
        password = simpledialog.askstring("Panic", "Enter Panic Password")
        if password != settings.timer_password:
            return

    os_utils.set_wallpaper(CustomAssets.panic_wallpaper())
    root.destroy()
    if state.gallery_dl_process:
        state.gallery_dl_process.kill()


def start_panic_listener(root: Tk, settings: Settings, state: State) -> None:
    def listen() -> None:
        try:
            with Listener(address=ADDRESS, authkey=AUTHKEY) as listener:
                with listener.accept() as connection:
                    message = connection.recv()
                    if message == PANIC_MESSAGE:
                        panic(root, settings, state)
        except OSError as e:
            logging.warning(f"Failed to start panic listener, some panic sources may not be functional. Reason: {e}")

    Thread(target=listen, daemon=True).start()


def send_panic() -> None:
    with Client(address=ADDRESS, authkey=AUTHKEY) as connection:
        connection.send(PANIC_MESSAGE)


if __name__ == "__main__":
    send_panic()
