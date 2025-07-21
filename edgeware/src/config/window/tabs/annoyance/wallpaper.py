# Copyright (C) 2025 Araten & Marigold
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

import logging
import os
from tkinter import SINGLE, Button, Frame, IntVar, Label, Listbox, Scale, filedialog, messagebox, simpledialog

from config.vars import Vars
from config.window.utils import (
    config,
    set_widget_states,
)
from config.window.widgets.layout import (
    ConfigRow,
    ConfigSection,
    ConfigToggle,
)
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip
from os_utils import get_wallpaper
from pack import Pack
from paths import CustomAssets, Data
from PIL import Image, ImageTk

ROTATE_TEXT = "Turning on wallpaper rotate disables built-in pack wallpapers, allowing you to cycle through your own instead. Keep in mind some packs use the corruption feature to rotate wallpapers without this setting enabled."
PANIC_TEXT = "This is the panic wallpaper, make sure to set it to your default wallpaper ASAP! Otherwise quitting edgeware via panic will leave you with a nice and generic windows one instead."


def update_max(obj: IntVar, value: int) -> None:
    obj.configure(to=int(value))


class WallpaperTab(ScrollFrame):
    def __init__(self, vars: Vars, pack: Pack) -> None:
        super().__init__()

        self.pack = pack

        panic_section = ConfigSection(self.viewPort, "Panic Wallpaper", PANIC_TEXT)
        panic_section.pack()

        panic_wallpaper_preview_frame = Frame(panic_section)
        panic_wallpaper_preview_frame.pack(fill="x", expand=1)
        Label(panic_wallpaper_preview_frame, text="Current Panic Wallpaper").pack(fill="x")
        self.panic_wallpaper_label = Label(panic_wallpaper_preview_frame, text="Current Panic Wallpaper")
        self.panic_wallpaper_label.pack()
        self.load_panic_wallpaper()

        change_panic_wallpaper_frame = Frame(panic_section)
        change_panic_wallpaper_frame.pack(fill="x")
        set_panic_wallpaper_button = Button(
            change_panic_wallpaper_frame, text="Set Panic Wallpaper", command=self.set_panic_wallpaper, cursor="question_arrow"
        )
        set_panic_wallpaper_button.pack(side="left", fill="x", padx=5, pady=5, expand=1)
        CreateToolTip(
            set_panic_wallpaper_button,
            "When you use panic, the wallpaper will be set to this image.\n\n"
            "This is useful since most packs have a custom wallpaper, which is usually porn...!\n\n"
            "It is recommended to find your preferred/original desktop wallpaper and set it to that.",
        )
        auto_import_panic_wallpaper_button = Button(
            change_panic_wallpaper_frame, text="Auto Import", command=self.auto_import_panic_wallpaper, cursor="question_arrow"
        )
        auto_import_panic_wallpaper_button.pack(side="left", fill="x", padx=5, pady=5, expand=1)
        CreateToolTip(auto_import_panic_wallpaper_button, "Automatically set your current wallpaper as the panic wallpaper.")

        wallpaper_section = ConfigSection(self.viewPort, "Rotating Wallpaper", ROTATE_TEXT)
        wallpaper_section.pack()

        wallpaper_row = ConfigRow(wallpaper_section)
        wallpaper_row.pack()

        ConfigToggle(
            wallpaper_row,
            text="Rotate Wallpapers",
            variable=vars.rotate_wallpaper,
            command=lambda: set_widget_states(vars.rotate_wallpaper.get(), wallpaper_group),
        ).pack()

        self.wallpaper_list = Listbox(wallpaper_section, selectmode=SINGLE)
        self.wallpaper_list.pack(fill="x")
        for key in config["wallpaperDat"]:
            self.wallpaper_list.insert(1, key)

        add_wallpaper_button = Button(wallpaper_section, text="Add/Edit Wallpaper", command=self.add_wallpaper)
        add_wallpaper_button.pack(fill="x")
        remove_wallpaper_button = Button(wallpaper_section, text="Remove Wallpaper", command=self.remove_wallpaper)
        remove_wallpaper_button.pack(fill="x")
        auto_import_wallpaper_button = Button(wallpaper_section, text="Auto Import", command=self.auto_import_wallpaper)
        auto_import_wallpaper_button.pack(fill="x")

        rotate_row = ConfigRow(wallpaper_section)
        rotate_row.pack()

        rotate_delay = Scale(
            rotate_row,
            label="Rotate Timer (sec)",
            orient="horizontal",
            from_=5,
            to=300,
            variable=vars.wallpaper_timer,
            command=lambda val: update_max(rotate_variance, int(val) - 1),
        )
        rotate_delay.pack(fill="x", side="left", expand=1)
        rotate_variance = Scale(
            rotate_row, label="Rotate Variation (sec)", orient="horizontal", from_=0, to=(vars.wallpaper_timer.get() - 1), variable=vars.wallpaper_variance
        )
        rotate_variance.pack(fill="x", side="left", expand=1)

        wallpaper_group = [self.wallpaper_list, add_wallpaper_button, remove_wallpaper_button, auto_import_wallpaper_button, rotate_delay, rotate_variance]
        set_widget_states(vars.rotate_wallpaper.get(), wallpaper_group)

    def add_wallpaper(self) -> None:
        file = filedialog.askopenfile("r", filetypes=[("image file", ".jpg .jpeg .png")])
        if not isinstance(file, type(None)):
            lname = simpledialog.askstring("Wallpaper Name", "Wallpaper Label\n(Name displayed in list)")
            if not isinstance(lname, type(None)):
                print(file.name.split("/")[-1])
                config["wallpaperDat"][lname] = file.name.split("/")[-1]
                self.wallpaper_list.insert(1, lname)

    def remove_wallpaper(self) -> None:
        index = int(self.wallpaper_list.curselection()[0])
        item_name = self.wallpaper_list.get(index)
        if index > 0:
            del config["wallpaperDat"][item_name]
            self.wallpaper_list.delete(self.wallpaper_list.curselection())
        else:
            messagebox.showwarning("Remove Default", "You cannot remove the default wallpaper.")

    def auto_import_wallpaper(self) -> None:
        allow_ = messagebox.askyesno("Confirm", "Current list will be cleared before new list is imported from the /resource folder. Is that okay?")
        if allow_:
            # clear list
            while True:
                try:
                    del config["wallpaperDat"][self.wallpaper_list.get(1)]
                    self.wallpaper_list.delete(1)
                except Exception:
                    break
            for file in os.listdir(self.pack.paths.root):
                if (file.endswith(".png") or file.endswith(".jpg") or file.endswith(".jpeg")) and file != "wallpaper.png":
                    name_ = file.split(".")[0]
                    self.wallpaper_list.insert(1, name_)
                    config["wallpaperDat"][name_] = file

    def set_panic_wallpaper(self) -> None:
        file = filedialog.askopenfile("rb", filetypes=[("image file", ".jpg .jpeg .png")])
        if not file:
            return

        try:
            image = Image.open(file.name).convert("RGB")
            image.save(Data.PANIC_WALLPAPER)
            self.load_panic_wallpaper()
        except Exception as e:
            logging.warning(f"Failed to set panic wallpaper\n{e}")
            messagebox.showwarning("Failed", f"Failed to set panic wallpaper\n{e}")

    def auto_import_panic_wallpaper(self) -> None:
        try:
            image = Image.open(get_wallpaper()).convert("RGB")
            image.save(Data.PANIC_WALLPAPER)
            self.load_panic_wallpaper()
        except Exception as e:
            logging.warning(f"Failed to auto import panic wallpaper\n{e}")
            messagebox.showwarning("Failed", f"Failed to auto import panic wallpaper\n{e}")

    def load_panic_wallpaper(self) -> None:
        self.panic_wallpaper_image = ImageTk.PhotoImage(
            Image.open(CustomAssets.panic_wallpaper()).resize((int(self.winfo_screenwidth() * 0.13), int(self.winfo_screenheight() * 0.13)), Image.NEAREST)
        )
        self.panic_wallpaper_label.config(image=self.panic_wallpaper_image)
        self.panic_wallpaper_label.update_idletasks()
