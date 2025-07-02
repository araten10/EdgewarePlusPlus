# Copyright (C) 2025 Araten & Marigold
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

from pathlib import Path
from tkinter import Tk
from typing import Callable

from config.settings import Settings
from features.image_popup import ImagePopup
from features.misc import (
    display_notification,
    open_web,
    play_audio,
)
from features.prompt import Prompt
from features.subliminal_message_popup import SubliminalMessagePopup
from features.video_popup import VideoPopup
from os_utils import set_wallpaper
from pack import Pack
from panic import panic
from state import State

from scripting.environment import Environment


def media(dir: Path, file: str | None) -> Path | None:
    return dir / file if file else None


def wrap(env: Environment, function: Callable | None) -> Callable | None:
    return (lambda: function(env)) if function else None


def get_modules(root: Tk, settings: Settings, pack: Pack, state: State) -> dict:
    popups = {
        "image": lambda env, image: ImagePopup(root, settings, pack, state, media(pack.paths.image, image)),
        "video": lambda env, video: VideoPopup(root, settings, pack, state, media(pack.paths.video, video)),
        "audio": lambda env, audio, on_stop: play_audio(root, settings, pack, state, media(pack.paths.audio, audio), wrap(env, on_stop)),
        "prompt": lambda env, prompt, on_close: Prompt(settings, pack, state, prompt, wrap(env, on_close)),
        "web": lambda env, web: open_web(pack, web),
        "subliminal": lambda env, subliminal: SubliminalMessagePopup(settings, pack, subliminal),
        "notification": lambda env, notification: display_notification(settings, pack, notification),
    }

    return {
        "standard": {"print": lambda env, *args: print(*args)},
        "edgeware": {
            "take_main": lambda env: setattr(state, "main_taken", True),
            "panic": lambda env: panic(root, settings, state, disable=False),
            "after": lambda env, ms, callback: root.after(ms, lambda: callback(env)),
            "set_wallpaper": lambda env, wallpaper: set_wallpaper(pack.paths.root / wallpaper),
            **popups,
        },
    }
