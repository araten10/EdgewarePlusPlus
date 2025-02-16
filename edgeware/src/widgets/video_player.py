from pathlib import Path
from tkinter import Toplevel

import mpv


class VideoPlayer:
    def __init__(self, master: Toplevel, video: Path, volume: int):
        self.player = mpv.MPV(wid=master.winfo_id())
        self.player.loop = True
        self.player.volume = volume
        self.player.play(str(video))
