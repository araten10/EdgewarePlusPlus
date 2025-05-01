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

import asyncio
import logging
from pathlib import Path
from tkinter import Label, Tk

import booru
import requests
from features.popup import Popup
from pack import Pack
from PIL import Image, ImageTk
from roll import roll
from settings import Settings
from state import State
from widgets.video_player import VideoPlayer


class ImagePopup(Popup):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State, media: Path | None = None) -> None:
        self.media = media or pack.random_image()
        self.subliminal = roll(settings.subliminal_chance)
        if not self.should_init(settings, state):
            return
        super().__init__(root, settings, pack, state)

        # TODO: Better booru integration
        if self.settings.booru_download and roll(50):
            try:
                gel = booru.Gelbooru()
                result = booru.resolve(asyncio.run(gel.search_image(query=self.settings.booru_tags, limit=1)))
                data = requests.get(result[0], stream=True)
                image = Image.open(data.raw)
            except KeyError:
                logging.error(f'No results for tags "{self.settings.booru_tags}" on Gelbooru')
                image = Image.open(self.media)
        else:
            image = Image.open(self.media)
        self.compute_geometry(image.width, image.height)

        # Static               -> image
        # Static,   subliminal -> image overlay, mpv
        # Animated             -> mpv
        # Animated, subliminal -> mpv, ?

        if getattr(image, "n_frames", 0) > 1:
            self.player = VideoPlayer(self, self.settings, self.width, self.height)
            self.player.properties["vf"] = self.try_denial_filter(True)
            self.player.play(str(self.media))
        else:
            resized = image.resize((self.width, self.height), Image.LANCZOS).convert("RGBA")
            filter = self.try_denial_filter(False)
            final = resized.filter(filter) if filter else resized

            if self.subliminal:
                self.player = VideoPlayer(self, self.settings, self.width, self.height)
                self.player.properties["video-scale-x"] = max(self.width / self.height, 1)
                self.player.properties["video-scale-y"] = max(self.height / self.width, 1)
                final.putalpha(int((1 - self.settings.subliminal_opacity) * 255))
                self.player.play(self.pack.random_subliminal_overlay(), final)
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
