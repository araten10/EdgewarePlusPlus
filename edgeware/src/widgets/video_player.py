from tkinter import Label, Misc

import mpv
import os_utils
from settings import Settings


class VideoPlayer(mpv.MPV):
    def __init__(self, master: Misc, settings: Settings, width: int, height: int):
        label = Label(master, width=width, height=height)
        label.pack()
        label.wait_visibility()  # Needs to be visible for mpv to draw on it

        super().__init__(wid=label.winfo_id())
        self["hwdec"] = "auto" if settings.video_hardware_acceleration else "no"
        self.loop = True

    def close(self) -> None:
        os_utils.close_mpv(self)
