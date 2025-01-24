import os
import random
from tkinter import Label, Tk

import filetype
from features.popup import Popup
from pack import Pack
from PIL import Image, ImageFilter
from roll import roll
from settings import Settings
from state import State
from widgets.image_label import GifLike, ImageLabel


class ImagePopup(Popup):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State):
        self.media = pack.random_image()
        self.subliminal = roll(settings.subliminal_chance)
        if not self.should_init(settings, state):
            return
        super().__init__(root, settings, pack, state)

        self.denial = roll(self.settings.denial_chance)

        # TODO: Better way to use downloaded images
        if settings.download_path.is_dir() and self.settings.booru_download and roll(50):
            dir = settings.download_path
            choices = [dir / file for file in os.listdir(dir) if filetype.is_image(dir / file)]
            if len(choices) > 0:
                self.media = random.choice(choices)
        image = Image.open(self.media)

        self.compute_geometry(image.width, image.height)
        ImageLabel(self, self.try_subliminal(image), (self.width, self.height), self.try_denial_filter()).pack()

        self.try_denial_text()
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

    def try_subliminal(self, image: Image.Image) -> Image.Image | GifLike:
        single_frame = not hasattr(image, "n_frames") or image.n_frames == 1
        if self.subliminal and single_frame:
            blend_image = image.convert("RGBA")
            subliminal = Image.open(self.pack.random_subliminal_overlay())

            if hasattr(subliminal, "n_frames") and subliminal.n_frames > 1:
                frames = []
                for i in range(subliminal.n_frames):
                    subliminal.seek(i)
                    blend_frame = subliminal.resize(image.size).convert("RGBA")
                    frame = Image.blend(blend_image, blend_frame, self.settings.subliminal_opacity)
                    frames.append((frame, subliminal.info["duration"]))

                return GifLike(frames)
            else:
                blend_subliminal = subliminal.resize(image.size).convert("RGBA")
                return Image.blend(blend_image, blend_subliminal, self.settings.subliminal_opacity)
        else:
            return image

    def try_denial_filter(self) -> ImageFilter.Filter:
        if self.denial:
            return random.choice([
                ImageFilter.GaussianBlur(5),
                ImageFilter.GaussianBlur(10),
                ImageFilter.GaussianBlur(20),
                ImageFilter.BoxBlur(5),
                ImageFilter.BoxBlur(10),
                ImageFilter.BoxBlur(20),
            ])  # fmt: skip
        else:
            return None

    def try_denial_text(self) -> None:
        if self.denial:
            label = Label(self, text=self.pack.random_denial(), wraplength=self.width, fg=self.theme.fg, bg=self.theme.bg)
            label.place(relx=0.5, rely=0.5, anchor="c")

    def close(self) -> None:
        super().close()
        if self.subliminal:
            self.state.subliminal_number -= 1
