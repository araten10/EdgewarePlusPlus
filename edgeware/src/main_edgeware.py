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
    from threading import Thread

    from paths import Data

    # Fix scaling on high resolution displays
    try:
        from ctypes import windll

        windll.shcore.SetProcessDpiAwareness(0)  # Tell Windows that you aren't DPI aware.
    except Exception:
        pass  # Fails on non-Windows systems or if shcore is not available

    # Add mpv to PATH
    os.environ["PATH"] += os.pathsep + str(Data.ROOT)

    def pyglet_run() -> None:
        import pyglet

        pyglet.app.run()

    Thread(target=pyglet_run, daemon=True).start()  # Required for pyglet events

from threading import Thread
from tkinter import Tk

import utils
from config import first_launch_configure
from config.settings import Settings
from features.audio import play_audio
from features.corruption import corruption_danger_check, handle_corruption
from features.drive import fill_drive, replace_images
from features.hibernate import main_hibernate, start_main_hibernate
from features.image_popup import ImagePopup
from features.misc import (
    display_notification,
    handle_discord,
    handle_keyboard,
    handle_mitosis_mode,
    handle_panic_lockout,
    handle_wallpaper,
    make_desktop_icons,
    make_tray_icon,
    open_web,
)
from features.prompt import Prompt
from features.startup_splash import StartupSplash
from features.subliminal_popup import SubliminalPopup
from features.video_popup import VideoPopup
from pack import Pack
from panic import start_panic_listener
from roll import RollTarget, roll_targets
from scripting import run_script
from state import State


def main(root: Tk, settings: Settings, pack: Pack, targets: list[RollTarget]) -> None:
    roll_targets(settings, targets)
    Thread(target=lambda: fill_drive(root, settings, pack, state), daemon=True).start()  # Thread for performance reasons
    root.after(settings.delay, lambda: main(root, settings, pack, targets))


if __name__ == "__main__":
    utils.init_logging("main")

    first_launch_configure()

    root = Tk()
    root.withdraw()
    settings = Settings()
    pack = Pack(settings.pack_path)
    state = State()

    settings.corruption_mode = settings.corruption_mode and pack.corruption_levels
    corruption_danger_check(settings, pack)

    # TODO: Use a dict?
    targets = [
        RollTarget(lambda: ImagePopup(root, settings, pack, state), lambda: settings.image_chance if not settings.mitosis_mode else 0),
        RollTarget(lambda: VideoPopup(root, settings, pack, state), lambda: settings.video_chance if not settings.mitosis_mode else 0),
        RollTarget(lambda: SubliminalPopup(settings, pack), lambda: settings.subliminal_chance),
        RollTarget(lambda: Prompt(settings, pack, state), lambda: settings.prompt_chance),
        RollTarget(lambda: play_audio(root, settings, pack, state), lambda: settings.audio_chance),
        RollTarget(lambda: open_web(pack), lambda: settings.web_chance),
        RollTarget(lambda: display_notification(settings, pack), lambda: settings.notification_chance),
    ]

    def start_main() -> None:
        make_tray_icon(root, settings, pack, state, lambda: main_hibernate(root, settings, pack, state, targets))
        make_desktop_icons(settings)
        handle_keyboard(root, settings, state)
        start_panic_listener(root, settings, state)
        Thread(target=lambda: replace_images(settings, pack), daemon=True).start()  # Thread for performance reasons
        handle_corruption(root, settings, pack, state)
        handle_discord(settings, pack)
        handle_panic_lockout(root, settings, state)
        handle_mitosis_mode(root, settings, pack, state)

        if settings.hibernate_mode:
            start_main_hibernate(root, settings, pack, state, targets)
        else:
            handle_wallpaper(root, settings, pack, state)
            main(root, settings, pack, targets)

    run_script(root, settings, pack, state)
    if settings.startup_splash:
        StartupSplash(settings, pack, start_main)
    else:
        start_main()

    root.mainloop()
