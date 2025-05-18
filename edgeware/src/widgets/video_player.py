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

import io
import logging
import subprocess
import sys
from pathlib import Path
from threading import Thread
from tkinter import Label, Misc

import mpv
import os_utils
from os_utils import close_mpv
from paths import Process
from PIL import Image
from settings import Settings


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
                    break
                except TypeError:
                    logging.warning(f"mpv GPU context {context} is not supported")

    def play(self, media: Path, overlay: Image.Image | None = None) -> None:
        if not self.settings.mpv_subprocess:
            self.wait_visibility()  # Needs to be visible for mpv to draw on it

            self.mpv = mpv.MPV(wid=self.winfo_id())
            for key, value in self.properties.items():
                self.mpv[key] = value

            if overlay:
                self.mpv.create_image_overlay().update(overlay)

            self.mpv.play(str(media))
        else:
            self.process = subprocess.Popen(
                [
                    sys.executable,
                    Process.LINUX_MPV,
                    str(self.winfo_id()),
                    str(self.properties),
                    media,
                    "1" if overlay else "0",
                ],
                stdin=subprocess.PIPE,
            )

            if overlay:

                def send_overlay() -> None:
                    bytes_io = io.BytesIO()
                    overlay.save(bytes_io, format="PNG")
                    self.process.communicate(input=bytes_io.getvalue())

                Thread(target=send_overlay).start()

    def close(self) -> None:
        if not self.settings.mpv_subprocess:
            close_mpv(self.mpv)
        else:
            self.process.kill()
