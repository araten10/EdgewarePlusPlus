from tkinter import Label, Misc

import mpv
from os_utils import close_mpv, is_linux
from settings import Settings


class VideoPlayer(mpv.MPV):
    def __init__(self, master: Misc, settings: Settings, width: int, height: int):
        label = Label(master, width=width, height=height)
        label.pack()
        label.wait_visibility()  # Needs to be visible for mpv to draw on it

        super().__init__(wid=label.winfo_id())
        self["hwdec"] = "auto" if settings.video_hardware_acceleration else "no"
        if is_linux():
            self["gpu-context"] = "x11"
        self.loop = True

    def close(self) -> None:
        close_mpv(self)
