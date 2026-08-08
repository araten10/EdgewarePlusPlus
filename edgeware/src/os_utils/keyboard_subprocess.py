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

"""Pynput keyboard listener subprocess target.

Runs pynput in a subprocess so that it gets its own main thread — required
because macOS TSM APIs (called by pynput) assert they run on the main thread.
On non-darwin this is the only keyboard listener implementation.

Must be a top-level function so multiprocessing.spawn can pickle it.
"""

import logging
import os
from multiprocessing.connection import Connection


def _config_keyboard_listener(connection: Connection) -> None:
    """Pynput keyboard listener subprocess target.

    Runs pynput in its own main thread via subprocess. Sends key release
    events back via the multiprocessing pipe.
    """
    try:
        from utils import init_logging
        init_logging("keyboard_listener")
        logging.info("Config keyboard listener subprocess started (PID %d)", os.getpid())
    except Exception as e:
        print(f"Failed to initialize config keyboard listener logging: {e}")

    from pynput import keyboard

    def on_release(key):
        try:
            logging.info("Key released: %s — sending via pipe", key)
            connection.send(str(key))
        except Exception as e:
            logging.error("Failed to send key event: %s", e)
            raise

    try:
        logging.info("Creating pynput keyboard Listener")
        listener = keyboard.Listener(on_release=on_release)
        logging.info("Starting pynput keyboard Listener")
        listener.start()
        logging.info("Pynput listener thread alive: %s", listener.is_alive())
        logging.info("Sending 'focus' to parent")
        connection.send("focus")
        logging.info("'focus' sent — joining listener thread")
        listener.join()
        logging.info("Listener thread joined (exit code: %s)", listener.daemon)
    except Exception as exc:
        logging.error("Config keyboard listener subprocess crashed: %s", exc, exc_info=True)
    finally:
        logging.info("Config keyboard listener subprocess exiting")
        try:
            connection.close()
        except Exception:
            pass
