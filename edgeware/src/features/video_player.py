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
from pathlib import Path
from tkinter import Label, Misc

import mpv
import os_utils
from config.settings import Settings
from os_utils import close_mpv
from PIL import Image


def make_mpv_player(wid: int, properties: dict[str, str], overlay: Image.Image | None) -> mpv.MPV:
    player = mpv.MPV(wid=wid)
    for key, value in properties.items():
        player[key] = value

    if overlay:
        player.create_image_overlay().update(overlay)

    return player


def mpv_subprocess(media: Path, wid: int, properties: dict[str, str], overlay: Image.Image | None) -> None:
    player = make_mpv_player(wid, properties, overlay)
    player.play(str(media))
    player.wait_for_playback()


class VideoPlayer(Label):
    def __init__(self, master: Misc, settings: Settings, width: int, height: int) -> None:
        super().__init__(master, width=width, height=height, bg="black")
        self.pack()

        self.settings = settings
        self.properties = {
            "loop": "inf",
            "hwdec": "auto" if self.settings.video_hardware_acceleration else "no",
            "input-cursor-passthrough": "yes",  # Required for buttonless closing
        }

        if os_utils.is_linux():
            # Required on Wayland for embedding the player
            temp = mpv.MPV()
            for context in ["x11", "x11egl", "x11vk"]:
                try:
                    temp["gpu-context"] = context  # Check if context is supported
                    self.properties["gpu-context"] = context
                    logging.info(f"Using mpv GPU context {context}")
                    break
                except TypeError:
                    logging.warning(f"mpv GPU context {context} is not supported")

    def play(self, media: Path, overlay: Image.Image | None = None) -> None:
        if not self.settings.mpv_subprocess:
            self.wait_visibility()  # Needs to be visible for mpv to draw on it
            self.player = make_mpv_player(self.winfo_id(), self.properties, overlay)
            self.player.play(str(media))
        else:
            context = multiprocessing.get_context("spawn")  # Audio won't work unless this is used
            self.process = context.Process(target=mpv_subprocess, args=(media, self.winfo_id(), self.properties, overlay))
            self.process.start()

    def close(self) -> None:
        if not self.settings.mpv_subprocess:
            close_mpv(self.player)
        else:
            self.process.terminate()
