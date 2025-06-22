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

import os
import random
import shutil
import time
import logging
from pathlib import Path
from threading import Thread
from tkinter import Button, Label, TclError, Tk, Toplevel

import os_utils
import utils
from config.settings import Settings
from desktop_notifier.common import Icon
from desktop_notifier.sync import DesktopNotifierSync
from features.misc import mitosis_popup, open_web
from features.sextoy import Sextoy
from features.vibration_mixin import VibrationMixin
from pack import Pack
from panic import panic
from paths import Data
from PIL import ImageFilter
from roll import roll
from state import State


class Popup(Toplevel, VibrationMixin):
    media: Path  # Defined by subclasses

    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State, sextoy: Sextoy) -> None:
        state.popup_number += 1
        super().__init__(bg="black")

        self.root = root
        self.settings = settings
        self.pack = pack
        self.state = state
        self.popup_id = state.get_popup_id()
        self.theme = settings.theme

        self.denial = roll(self.settings.denial_chance)

        self.bind("<KeyPress>", lambda event: panic(self.root, self.settings, self.state, condition=(event.keysym == self.settings.panic_key)))
        self.attributes("-topmost", True)
        os_utils.set_borderless(self)

        self.opacity = self.settings.opacity
        self.attributes("-alpha", self.opacity)

    def init_finish(self) -> None:
        self.try_denial_text()
        self.try_caption()
        self.try_corruption_dev()
        self.try_button()
        self.try_move()
        self.try_multi_click()
        self.try_timeout()
        self.try_pump_scare()

    def compute_geometry(self, source_width: int, source_height: int) -> None:
        self.monitor = utils.random_monitor(self.settings)

        source_size = max(source_width, source_height) / min(self.monitor.width, self.monitor.height)
        target_size = (random.randint(30, 70) if not self.settings.lowkey_mode else random.randint(20, 50)) / 100
        scale = target_size / source_size

        self.width = int(source_width * scale)
        self.height = int(source_height * scale)

        if self.settings.lowkey_mode:
            corner = self.settings.lowkey_corner
            if corner == 4:  # Random corner
                corner = random.randint(0, 3)

            right = corner == 0 or corner == 3  # Top right or bottom right
            bottom = corner == 2 or corner == 3  # Bottom left or bottom right
            self.x = self.monitor.x + (self.monitor.width - self.width if right else 0)
            self.y = self.monitor.y + (self.monitor.height - self.height if bottom else 0)
        else:
            positions = []
            weights = []

            # Divide the area of possible coordinates with respect to the
            # monitor and popup sizes into a grid of side * side squares.
            # Considering each pixel individually is unnecessary and too slow.
            side = 50
            area_width = self.monitor.width - self.width
            area_height = self.monitor.height - self.height
            for x_index in range(area_width // side):
                for y_index in range(area_height // side):
                    # Possible coordinates for this popup
                    sx = x_index * side + self.monitor.x
                    sy = y_index * side + self.monitor.y
                    sw = self.width
                    sh = self.height

                    # Compute the weight for this position, preferring positions
                    # that reduce popup overlap and clustering
                    geometries = self.state.popup_geometries.copy().values()  # Copied in case a popup is closed during iteration
                    weight = float("inf") if geometries else 1
                    for w, h, x, y in geometries:
                        intersection = max(0, min(sx + sw, x + w) - max(sx, x)) * max(0, min(sy + sh, y + h) - max(sy, y))
                        nonoverlap = 1 - intersection / (sw * sh)
                        distance_squared = (sx + sw / 2 - (x + w / 2)) ** 2 + (sy + sh / 2 - (y + h / 2)) ** 2
                        weight = min(2 ** (32 * nonoverlap) + distance_squared, weight)

                    positions.append((sx, sy))
                    weights.append(weight)

            # Select a position inside the chosen square randomly
            min_x, min_y = random.choices(positions, weights)[0]

            # In case the area can't be neatly divided into squares
            max_x = min_x + side
            max_x += (area_width % side if area_width - max_x < side else 0) - 1
            max_y = min_y + side
            max_y += (area_height % side if area_height - max_y < side else 0) - 1

            self.x = random.randint(min_x, max_x)
            self.y = random.randint(min_y, max_y)

        self.state.popup_geometries[self.popup_id] = (self.width, self.height, self.x, self.y)
        self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def try_denial_filter(self, mpv: bool) -> ImageFilter.Filter | str:
        mpv_filters = ["gblur=sigma=5", "gblur=sigma=10", "gblur=sigma=20"]
        image_filters = [ImageFilter.GaussianBlur(5), ImageFilter.GaussianBlur(10), ImageFilter.GaussianBlur(20)]
        return random.choice(mpv_filters if mpv else image_filters) if self.denial else ""

    def try_denial_text(self) -> None:
        if self.denial:
            label = Label(
                self, text=self.pack.random_denial(), wraplength=self.width, fg=self.theme.fg, bg=self.theme.bg, font=(self.theme.font, self.theme.font_size)
            )
            label.place(relx=0.5, rely=0.5, anchor="c")

    def try_caption(self) -> None:
        caption = self.pack.random_caption(self.media)
        if self.settings.captions_in_popups and caption:
            try:
                self.trigger_vibration("caption", getattr(self.settings, 'sextoys', {}), self.sextoy)
            except Exception as e:
                logging.info(f"Caption vibration error: {str(e)}")
            label = Label(self, text=caption, wraplength=self.width, fg=self.theme.fg, bg=self.theme.bg, font=(self.theme.font, self.theme.font_size))
            label.place(x=5, y=5)

    def try_corruption_dev(self) -> None:
        if self.settings.corruption_dev_mode:
            levels = []
            mood = self.pack.index.media_moods.get(self.media.name, None)
            for level in self.pack.corruption_levels:
                if mood in level.moods:
                    levels.append(self.pack.corruption_levels.index(level) + 1)

            label_mood = Label(self, text=f"Popup mood: {mood}", fg=self.theme.fg, bg=self.theme.bg, font=(self.theme.font, self.theme.font_size))
            label_level = Label(self, text=f"Valid Levels: {levels}", fg=self.theme.fg, bg=self.theme.bg, font=(self.theme.font, self.theme.font_size))
            label_current_level = Label(
                self, text=f"Current Level: {self.state.corruption_level}", fg=self.theme.fg, bg=self.theme.bg, font=(self.theme.font, self.theme.font_size)
            )

            label_mood.place(x=5, y=(self.height // 2))
            label_level.place(x=5, y=(self.height // 2 + label_mood.winfo_reqheight() + 2))
            label_current_level.place(x=5, y=(self.height // 2 + label_mood.winfo_reqheight() + label_level.winfo_reqheight() + 4))

    def try_button(self) -> None:
        if self.settings.buttonless:
            self.bind("<ButtonRelease-1>", lambda _: self.click())
        else:
            button = Button(
                self,
                text=self.pack.index.default.popup_close,
                command=self.click,
                fg=self.theme.fg,
                bg=self.theme.bg,
                activeforeground=self.theme.fg,
                activebackground=self.theme.bg,
                font=(self.theme.font, self.theme.font_size),
            )
            button.place(x=-10, y=-10, relx=1, rely=1, anchor="se")

    def try_move(self) -> None:
        def move() -> None:
            speed_x = 0 if self.settings.moving_chance else self.settings.moving_speed
            speed_y = 0 if self.settings.moving_chance else self.settings.moving_speed
            while speed_x == 0 and speed_y == 0:
                speed_x = random.randint(-self.settings.moving_speed, self.settings.moving_speed)
                speed_y = random.randint(-self.settings.moving_speed, self.settings.moving_speed)

            try:
                while True:
                    self.x += speed_x
                    self.y += speed_y

                    left = self.x <= self.monitor.x
                    right = self.x + self.width >= self.monitor.x + self.monitor.width
                    if left or right:
                        speed_x = -speed_x

                    top = self.y <= self.monitor.y
                    bottom = self.y + self.height >= self.monitor.y + self.monitor.height
                    if top or bottom:
                        speed_y = -speed_y

                    self.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")
                    time.sleep(0.01)
            except TclError:
                pass  # Exception thrown when closing

        if roll(self.settings.moving_chance):
            Thread(target=move, daemon=True).start()

    def try_multi_click(self) -> None:
        self.clicks_to_close = self.pack.random_clicks_to_close(self.media) if self.settings.multi_click_popups else 1

    def try_timeout(self) -> None:
        def fade_out() -> None:
            try:
                while self.opacity > 0:
                    self.opacity -= 0.01
                    self.attributes("-alpha", self.opacity)
                    time.sleep(0.015)
                self.close()
            except TclError:
                pass  # Exception thrown when manually closed during fade out

        if self.settings.timeout_enabled and not self.state.pump_scare:
            self.after(self.settings.timeout, Thread(target=fade_out, daemon=True).start)

    def try_pump_scare(self) -> None:
        if self.state.pump_scare:
            self.after(2500, self.close)

    def try_web_open(self) -> None:
        if self.settings.web_on_popup_close and roll((100 - self.settings.web_chance) / 2):
            open_web(self.pack)

    def try_mitosis(self) -> None:
        if self.settings.mitosis_mode and not self.settings.lowkey_mode:
            for n in range(self.settings.mitosis_strength):
                mitosis_popup(self.root, self.settings, self.pack, self.state)

    def click(self) -> None:
        self.clicks_to_close -= 1
        if self.clicks_to_close <= 0:
            if self.state.alt_held:
                self.blacklist_media()
            self.close()
            self.try_mitosis()

    def blacklist_media(self) -> None:
        filename = os.path.basename(self.media).split("/")[-1]
        path_blacklist = Data.BLACKLIST / "".join(self.pack.info.name.split())
        if not os.path.exists(path_blacklist):
            os.makedirs(path_blacklist)
        shutil.move(self.media, path_blacklist)
        notifier = DesktopNotifierSync(app_name="Edgeware++", app_icon=Icon(self.pack.icon))
        notifier.send(title=self.pack.info.name, message=f"{filename} has been successfully sent to blacklist")

    def close(self) -> None:
        self.state.popup_number -= 1
        self.state.popup_geometries.pop(self.popup_id)
        self.try_web_open()
        self.destroy()
