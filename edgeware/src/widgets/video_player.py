import io
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
    def __init__(self, master: Misc, settings: Settings, width: int, height: int):
        super().__init__(master, width=width, height=height, bg="black")
        self.pack()

        self.settings = settings
        self.properties = {
            "loop": "inf",
            "hwdec": "auto" if self.settings.video_hardware_acceleration else "no",
            "input-cursor-passthrough": "yes",  # Required for buttonless closing
        }

        if os_utils.is_linux():
            self.properties["gpu-context"] = "x11"  # Required on Wayland for embedding the player

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
