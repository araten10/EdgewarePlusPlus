from collections.abc import Callable
from tkinter import Label, Toplevel

import os_utils
import utils
from pack import Pack
from PIL import Image, ImageTk
from settings import Settings
from widgets.video_player import VideoPlayer


class StartupSplash(Toplevel):
    def __init__(self, settings: Settings, pack: Pack, callback: Callable[[], None]):
        super().__init__(bg="black")

        self.callback = callback
        self.opacity = 0

        self.attributes("-topmost", True)
        os_utils.set_borderless(self)

        monitor = utils.primary_monitor()

        image = Image.open(pack.startup_splash)

        # TODO: Better scaling
        scale = 0.6
        width = int(image.width * scale)
        height = int(image.height * scale)
        x = monitor.x + (monitor.width - width) // 2
        y = monitor.y + (monitor.height - height) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")

        if getattr(image, "n_frames", 0) > 1:
            self.player = VideoPlayer(self, settings, width, height)
            self.player.play(pack.startup_splash)
        else:
            label = Label(self, width=width, height=height)
            label.pack()

            resized = image.resize((width, height), Image.LANCZOS).convert("RGBA")
            self.photo_image = ImageTk.PhotoImage(resized)
            label.config(image=self.photo_image)

        self.fade_in()

    def fade_in(self) -> None:
        if self.opacity < 1:
            self.opacity += 0.01
            self.attributes("-alpha", self.opacity)
            self.after(10, self.fade_in)
        else:
            self.after(2000, self.fade_out)

    def fade_out(self) -> None:
        if self.opacity > 0:
            self.opacity -= 2 * 0.01
            self.attributes("-alpha", self.opacity)
            self.after(10 // 4, self.fade_out)
        else:
            if hasattr(self, "player"):
                self.player.close()
            self.destroy()
            self.callback()
