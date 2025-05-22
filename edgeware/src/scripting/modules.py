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

from tkinter import Tk

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
from pack import Pack
from state import State


def get_modules(root: Tk, settings: Settings, pack: Pack, state: State) -> dict:
    return {
        "standard": {
            "print": lambda env, *args: print(*args),
        },
        "edgeware": {
            "after": lambda env, ms, callback: root.after(ms, lambda: callback(env)),
            "image": lambda env, image: ImagePopup(root, settings, pack, state, pack.paths.image / image if image else None),
            "video": lambda env, video: VideoPopup(root, settings, pack, state, pack.paths.video / video if video else None),
            "audio": lambda env, audio, on_stop: play_audio(root, settings, pack, pack.paths.audio / audio if audio else None, (lambda: on_stop(env)) if on_stop else None),
            "prompt": lambda env, prompt, on_close: Prompt(settings, pack, state, prompt, (lambda: on_close(env)) if on_close else None),
            "web": lambda env, web: open_web(pack, web),
            "subliminal": lambda env, subliminal: SubliminalMessagePopup(settings, pack, subliminal),
            "notification": lambda env, notification: display_notification(settings, pack, notification),
        }
    }
