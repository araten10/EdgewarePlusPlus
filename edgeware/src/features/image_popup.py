import os
import random
from tkinter import Label, Tk

import filetype
from features.popup import Popup
from pack import Pack
from PIL import Image, ImageTk
from roll import roll
from settings import Settings
from state import State
from widgets.video_player import VideoPlayer


class ImagePopup(Popup):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State):
        self.media = pack.random_image()
        self.subliminal = roll(settings.subliminal_chance)
        if not self.should_init(settings, state):
            return
        super().__init__(root, settings, pack, state)

        # TODO: Better way to use downloaded images
        if settings.download_path.is_dir() and self.settings.booru_download and roll(50):
            dir = settings.download_path
            choices = [dir / file for file in os.listdir(dir) if filetype.is_image(dir / file)]
            if len(choices) > 0:
                self.media = random.choice(choices)

        image = Image.open(self.media)
        self.compute_geometry(image.width, image.height)

        # Static               -> image
        # Static,   subliminal -> image overlay, mpv
        # Animated             -> mpv
        # Animated, subliminal -> mpv, ?

        if getattr(image, "n_frames", 0) > 1:
            self.player = VideoPlayer(self, self.settings, self.width, self.height)
            self.player.vf = self.try_denial_filter(True)
            self.player.play(str(self.media))
        else:
            resized = image.resize((self.width, self.height), Image.LANCZOS).convert("RGBA")
            filter = self.try_denial_filter(False)
            final = resized.filter(filter) if filter else resized

            if self.subliminal:
                self.player = VideoPlayer(self, self.settings, self.width, self.height)
                self.player.video_scale_x = max(self.width / self.height, 1)
                self.player.video_scale_y = max(self.height / self.width, 1)
                final.putalpha(int((1 - self.settings.subliminal_opacity) * 255))
                self.player.create_image_overlay().update(final)
                self.player.play(str(self.pack.random_subliminal_overlay()))
            else:
                label = Label(self, width=self.width, height=self.height)
                label.pack()
                self.photo_image = ImageTk.PhotoImage(final)
                label.config(image=self.photo_image)

        self.init_finish()

    def should_init(self, settings: Settings, state: State) -> bool:
        if not self.media:
            return False

        if not self.subliminal:
            return True

        if state.subliminal_number < settings.max_subliminals:
            state.subliminal_number += 1
            return True
        return False

    def close(self) -> None:
        if hasattr(self, "player"):
            self.player.close()
        super().close()
        if self.subliminal:
            self.state.subliminal_number -= 1
