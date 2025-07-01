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

import logging
from tkinter import Tk

import pyglet
from config.settings import Settings
from pack import Pack
from state import State

# Run our update ticks once in `TICKRATE` milliseconds
TICKRATE = 16  # 60 ticks per second


def play_audio(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    audio = pack.random_audio()
    if not audio or len(state.audio_players) >= settings.max_audio:
        return

    # Load in streaming mode to avoid loading entire file into RAM
    # Player doesn't need to be stored but might be needed for planned features
    player = pyglet.media.Player()
    player.queue(pyglet.media.load(str(audio), streaming=True))
    state.audio_players.append(player)
    player.play()

    fade_in(root, settings, player)

    if not player.source.duration:
        logging.warning(f"Duration of {audio.name} could not be determined, fade-out will not function")
        player.on_eos = lambda: stop_player(state, player)
        return

    delay = int(player.source.duration * 1000) - settings.fade_out_duration
    root.after(delay, lambda: fade_out(root, settings, state, player))


def stop_player(state: State, player: pyglet.media.Player) -> None:
    player.pause()
    state.audio_players.remove(player)


def fade_in(root: Tk, settings: Settings, player: pyglet.media.Player) -> None:
    """Gradually raise volume from 0 to the original level over `settings.fade_in_duration` milliseconds."""
    player.volume = 0
    steps = settings.fade_in_duration // TICKRATE
    delta = settings.audio_volume / steps if steps else settings.audio_volume

    def step() -> None:
        player.volume = min(settings.audio_volume, player.volume + delta)
        if player.volume < settings.audio_volume:
            root.after(TICKRATE, step)

    step()


def fade_out(root: Tk, settings: Settings, state: State, player: pyglet.media.Player) -> None:
    """Smoothly lower volume to 0 over `settings.fade_out_duration` milliseconds, then pause the player."""
    steps = settings.fade_out_duration // TICKRATE
    delta = player.volume / steps if steps else player.volume

    def step() -> None:
        player.volume = max(0, player.volume - delta)
        if player.volume > 0:
            root.after(TICKRATE, step)
        else:
            stop_player(state, player)

    step()
