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

from pathlib import Path
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    Button,
    Frame,
    Label,
    Message,
    Misc,
    filedialog,
)

from config.vars import Vars
from paths import CustomAssets, Data
from PIL import Image, ImageTk
from widgets.scroll_frame import ScrollFrame

INTRO_TEXT = 'Changing these will change the default file Edgeware++ falls back on when a replacement isn\'t provided by a pack. The files you choose will be stored under "data."'


class DefaultImageFrame(Frame):
    def __init__(
        self,
        master: Misc,
        image_file: Path,
        custom_file: Path,
        scale: float | None,
        filetypes: tuple[str, str],
        current_text: str,
        change_text: str,
        message: str,
    ) -> None:
        super().__init__(master, borderwidth=5, relief=RAISED)

        self.custom_file = custom_file
        self.scale = scale
        self.filetypes = filetypes

        self.pack(side="left", fill="both", padx=2, expand=1)

        col_1 = Frame(self)
        col_1.pack(side="left", fill="both")
        button = Button(col_1, text=change_text, command=self.change)
        button.pack(side="top", fill="both", padx=1)
        Message(col_1, text=message, justify=CENTER, borderwidth=5, relief=GROOVE).pack(side="top", fill="both", expand=1)

        col_2 = Frame(self, width=150)
        col_2.pack(side="left", fill="x", padx=(5, 0))
        Label(col_2, text=current_text).pack(fill="both")
        self.photo_image = ImageTk.PhotoImage(self.resize(Image.open(image_file)))
        self.label = Label(col_2, image=self.photo_image)
        self.label.pack()

    def change(self) -> None:
        selected_file = filedialog.askopenfile("rb", filetypes=[self.filetypes])
        if not selected_file:
            return

        image = Image.open(selected_file.name).convert("RGB")
        image.save(self.custom_file)
        self.photo_image = ImageTk.PhotoImage(self.resize(image))
        self.label.config(image=self.photo_image)
        self.label.update_idletasks()

    def resize(self, image: Image.Image) -> Image.Image:
        return image.resize((int(self.winfo_screenwidth() * self.scale), int(self.winfo_screenwidth() * self.scale)), Image.NEAREST) if self.scale else image


class DefaultFileTab(ScrollFrame):
    def __init__(self, vars: Vars, message_group: list[Message]) -> None:
        super().__init__()

        intro_message = Message(self.viewPort, text=INTRO_TEXT, justify=CENTER, width=675)
        intro_message.pack(fill="both")
        message_group.append(intro_message)

        row_1 = Frame(self.viewPort)
        row_1.pack(fill="x")
        DefaultImageFrame(
            row_1,
            CustomAssets.startup_splash(),
            Data.STARTUP_SPLASH,
            0.09,
            ("image file", ".jpg .jpeg .png .gif"),
            "Current Default Loading Splash",
            "Change Default Loading Splash",
            'LOADING SPLASH:\n\nUsed in "Show Loading Flair" setting (found in "Start" tab). Packs can have custom '
            "splashes, which will appear instead of this. Accepts .jpg or .png and will be shrunk to a slightly smaller size.",
        )
        DefaultImageFrame(
            row_1,
            CustomAssets.theme_demo(),
            Data.THEME_DEMO,
            None,
            ("image file", ".jpg .jpeg .png"),
            "Current Theme Demo",
            "Change Default Theme Demo",
            "THEME DEMO:\n\nUsed in the \"Start\" tab, supports .jpg or .png. Must be 150x75! If you don't crop your image to that, you'll have a bad time!!",
        )

        row_2 = Frame(self.viewPort)
        row_2.pack(fill="x")
        DefaultImageFrame(
            row_2,
            CustomAssets.icon(),
            Data.ICON,
            0.04,
            ("icon file", ".ico"),
            "Icon",
            "Change Default Icon",
            "ICON:\n\nUsed in desktop shortcuts and tray icon. Only supports .ico files.",
        )
        DefaultImageFrame(
            row_2,
            CustomAssets.config_icon(),
            Data.CONFIG_ICON,
            0.04,
            ("icon file", ".ico"),
            "Config Icon",
            "Change Config Icon",
            "CONFIG ICON:\n\nUsed in desktop shortcuts and the config window. Only supports .ico files.",
        )
        DefaultImageFrame(
            row_2,
            CustomAssets.panic_icon(),
            Data.PANIC_ICON,
            0.04,
            ("icon file", ".ico"),
            "Panic Icon",
            "Change Panic Icon",
            "PANIC ICON:\n\nUsed in desktop shortcuts. Only supports .ico files.",
        )

        row_3 = Frame(self.viewPort)
        row_3.pack(fill="x")
        DefaultImageFrame(
            row_3,
            CustomAssets.subliminal_overlay(),
            Data.SUBLIMINAL_OVERLAY,
            0.08,
            ("image file", ".jpg .jpeg .png .gif"),
            "Current Default Spiral",
            "Change Default Spiral",
            'SPIRAL:\n\nUsed in "Subliminal Overlays" setting (found in "Popups" tab). Packs can have custom '
            "Subliminals, which will appear instead of this. Accepts .jpg, .png, or .gif, but should be animated. "
            "(doesn't animate on this page to save on resources- try and aim for a small filesize on this image!)",
        )
