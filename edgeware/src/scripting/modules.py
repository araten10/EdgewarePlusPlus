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
from features.audio import play_audio
from features.corruption import update_corruption_level, next_corruption_level
from features.image_popup import ImagePopup
from features.misc import open_web, send_notification
from features.prompt import Prompt
from features.subliminal_popup import SubliminalPopup
from features.video_popup import VideoPopup
from os_utils import set_wallpaper
from pack import Pack
from pack.data import MoodSet
from panic import panic
from roll import roll
from state import State

from scripting.environment import Environment


def resource(dir: Path, file: str | None) -> Path | None:
    return dir / file if file else None


def callback(env: Environment, function: Callable | None) -> Callable | None:
    return (lambda: function(env)) if function else None


def assign_globals(env: Environment, globals: dict[str, object]) -> None:
    for name, value in globals.items():
        env.assign(name, value)


def close_popups(state: State) -> None:
    for popup in state.popups.copy():
        popup.close()

# make sure that added_moods and removed_moods are mutually exclusive. Then update mood sets in use
def clean_script_moods_and_update(settings: Settings, pack: Pack, state: State):
    pack.scripted_moods["added"].difference_update(pack.scripted_moods["removed"])
    pack.scripted_moods["removed"].difference_update(pack.scripted_moods["added"])
    pack.update_moods(
        state.corruption_level,
        next_corruption_level(settings, pack, state)
    )

def add_script_mood(_env: Environment, settings: Settings, pack: Pack, state: State, mood_name: str):
    if not settings.corruption_mode:
        print(f"Not adding mood {mood_name}. Corruption is not enabled")
        return

    if mood_name in pack.allowed_moods:
        print(f"Added {mood_name}")
        pack.scripted_moods["added"].add(mood_name)
        clean_script_moods_and_update(settings, pack, state)
    else:
        print(f"Mood \"{mood_name}\" is not a mood enabled for this pack")

def remove_script_mood(_env: Environment, settings: Settings, pack: Pack, state: State, mood_name: str):
    if not settings.corruption_mode:
        print(f"Not removing mood {mood_name}. Corruption is not enabled")
        return

    if mood_name in pack.allowed_moods:
        print(f"Removed {mood_name}")
        pack.scripted_moods["removed"].add(mood_name)
        clean_script_moods_and_update(settings, pack, state)
    else:
        print(f"Mood \"{mood_name}\" is not a mood enabled for this pack")

def edgeware_v0(root: Tk, settings: Settings, pack: Pack, state: State) -> Callable:
    from scripting import ReturnValue

    edgeware_v0_global = {
        "print": lambda _env, *args: print(*args),
        "after": lambda env, ms, callback: root.after(ms, lambda: callback(env)),
        "roll": lambda _env, chance: ReturnValue(roll(chance)),
        "corrupt": lambda _env: update_corruption_level(settings, pack, state),
        "panic": lambda _env: panic(root, settings, state, disable=False),
        "close_popups": lambda _env: close_popups(state),
        "set_popup_close_text": lambda _env, text: pack.index.default.__setattr__("popup_close", text),
        "image": lambda _env, image: ImagePopup(root, settings, pack, state, resource(pack.paths.image, image)),
        "video": lambda _env, video: VideoPopup(root, settings, pack, state, resource(pack.paths.video, video)),
        "audio": lambda env, audio, on_stop: play_audio(root, settings, pack, state, resource(pack.paths.audio, audio), callback(env, on_stop)),
        "prompt": lambda env, prompt, on_close: Prompt(settings, pack, state, prompt, callback(env, on_close)),
        "web": lambda _env, web: open_web(pack, web),
        "subliminal": lambda _env, subliminal: SubliminalPopup(settings, pack, subliminal),
        "notification": lambda _env, notification: send_notification(settings, pack, notification),
    }
    return lambda env: assign_globals(env, edgeware_v0_global)

def edgeware_v05(root: Tk, settings: Settings, pack: Pack, state: State) -> Callable:
    from scripting import ReturnValue

    # v0 copied from above function
    edgeware_v0_global = {
        "print": lambda _env, *args: print(*args),
        "after": lambda env, ms, callback: root.after(ms, lambda: callback(env)),
        "roll": lambda _env, chance: ReturnValue(roll(chance)),
        "corrupt": lambda _env: update_corruption_level(settings, pack, state),
        "panic": lambda _env: panic(root, settings, state, disable=False),
        "close_popups": lambda _env: close_popups(state),
        "set_popup_close_text": lambda _env, text: pack.index.default.__setattr__("popup_close", text),
        "image": lambda _env, image: ImagePopup(root, settings, pack, state, resource(pack.paths.image, image)),
        "video": lambda _env, video: VideoPopup(root, settings, pack, state, resource(pack.paths.video, video)),
        "audio": lambda env, audio, on_stop: play_audio(root, settings, pack, state, resource(pack.paths.audio, audio), callback(env, on_stop)),
        "prompt": lambda env, prompt, on_close: Prompt(settings, pack, state, prompt, callback(env, on_close)),
        "web": lambda _env, web: open_web(pack, web),
        "subliminal": lambda _env, subliminal: SubliminalPopup(settings, pack, subliminal),
        "notification": lambda _env, notification: send_notification(settings, pack, notification),
    }

    edgeware_v05_global = edgeware_v0_global.copy()
    
    # using the old "image" and "video" functions for testing because I was struggling to call the new ones in Lua (maybe tables related issue?)
    edgeware_v05_global["image"] = lambda env, image, on_close=None:ImagePopup(root, settings, pack, state, resource(pack.paths.image, image), callback(env, on_close))
    edgeware_v05_global["video"] = lambda env, video, on_close=None:VideoPopup(root, settings, pack, state, resource(pack.paths.image, video), callback(env, on_close))
    edgeware_v05_global["enable_mood"] = lambda _env, mood_name: add_script_mood(_env, settings, pack, state, mood_name)
    edgeware_v05_global["disable_mood"] = lambda _env, mood_name: remove_script_mood(_env, settings, pack, state, mood_name)

    return lambda env: assign_globals(env, edgeware_v05_global)

def edgeware_v1(root: Tk, settings: Settings, pack: Pack, state: State) -> Callable:
    from scripting import ReturnValue

    def set_active_moods(_env: Environment, moods: dict) -> None:
        # TODO: How are lists typically handled in Lua?
        i = 1
        mood_set = MoodSet()
        while i in moods:
            mood_set.add(moods[i])
            i += 1
        pack.active_moods = lambda: mood_set

    index = {
        "set_popup_close_text": lambda _env, text: pack.index.default.__setattr__("popup_close", text),
        "set_prompt_command_text": lambda _env, text: pack.index.default.__setattr__("prompt_command", text),
        "set_prompt_submit_text": lambda _env, text: pack.index.default.__setattr__("prompt_submit", text),
        "set_prompt_min_length": lambda _env, length: pack.index.default.__setattr__("prompt_min_length", length),
        "set_prompt_max_length": lambda _env, length: pack.index.default.__setattr__("prompt_max_length", length),
    }

    popups = {
        "open_image": lambda env, args={}: ImagePopup(
            root, settings, pack, state, resource(pack.paths.image, args.get("filename")), callback(env, args.get("on_close"))
        ),
        "open_video": lambda env, args={}: VideoPopup(
            root, settings, pack, state, resource(pack.paths.video, args.get("filename")), callback(env, args.get("on_close"))
        ),
        "play_audio": lambda env, args={}: play_audio(
            root, settings, pack, state, resource(pack.paths.audio, args.get("filename")), callback(env, args.get("on_stop"))
        ),
        "open_prompt": lambda env, args={}: Prompt(settings, pack, state, args.get("text"), callback(env, args.get("on_close"))),
        "open_web": lambda _env, args={}: open_web(pack, args.get("url")),
        "open_subliminal": lambda _env, args={}: SubliminalPopup(settings, pack, args.get("text")),
        "send_notification": lambda _env, args={}: send_notification(settings, pack, args.get("text")),
    }

    edgeware_v1_local = {
        "after": lambda env, ms, callback: root.after(ms, lambda: callback(env)),
        "roll": lambda _env, chance: ReturnValue(roll(chance)),
        "panic": lambda _env: panic(root, settings, state, disable=False),
        "close_popups": lambda _env: close_popups(state),
        "set_active_moods": set_active_moods,
        # "enable_mood": lambda env, mood: TODO,
        # "disable_mood": lambda env, mood: TODO,
        "progress_corruption": lambda _env: update_corruption_level(settings, pack, state),
        # "set_corruption_level": lambda _env, level: TODO,
        "set_wallpaper": lambda _env, filename: set_wallpaper(resource(pack.paths.root, filename)),
        **index,
        **popups,
    }

    return lambda _env: edgeware_v1_local


def get_modules(root: Tk, settings: Settings, pack: Pack, state: State) -> dict:
    basic_v1_global = {
        "print": lambda _env, *args: print(*args),
    }

    return {
        "edgeware_v0": edgeware_v0(root, settings, pack, state),
        "edgeware_v0.5": edgeware_v05(root, settings, pack, state),
        "edgeware_v1": edgeware_v1(root, settings, pack, state),
        "basic_v1": lambda env: assign_globals(env, basic_v1_global),
    }
