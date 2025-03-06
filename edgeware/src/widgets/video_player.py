from threading import Thread
from tkinter import Label, Misc

import mpv


class VideoPlayer(mpv.MPV):
    def __init__(self, master: Misc, width: int, height: int):
        label = Label(master, width=width, height=height)
        label.pack()
        label.wait_visibility()  # Needs to be visible for mpv to draw on it

        super().__init__(wid=label.winfo_id())
        self["hwdec"] = "auto"  # Enable hardware acceleration
        self.loop = True

    def terminate(self) -> None:
        # Run in a thread as a workaround for X error
        # https://github.com/jaseg/python-mpv/issues/114
        Thread(target=super().terminate).start()
