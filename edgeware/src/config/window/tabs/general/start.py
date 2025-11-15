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

from tkinter import (
    Button,
)

from config.vars import Vars
from config.window.utils import request_global_panic_key
from config.window.widgets.layout import (
    PAD,
    ConfigSection,
)
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip
from pack import Pack
from panic import send_panic

INTRO_TEXT = 'Welcome to Edgeware++!\nYou can use the tabs at the top of this window to navigate the various config settings for the main program. Annoyance/Runtime is for how the program works while running, Modes is for more complicated and involved settings that change how Edgeware works drastically, and Troubleshooting and About are for learning this program better and fixing errors should anything go wrong.\n\nAside from these helper memos, there are also tooltips on several buttons and sliders. If you see your mouse cursor change to a "question mark", hover for a second or two to see more information on the setting.'
THEME_TEXT = "You'll have to save and refresh the config window to get the theme to show up properly, but this tab will change to the currently selected theme so you can see what it looks like! None of the sliders or buttons in this section do anything, so feel free to play around with them to test it out!"
PANIC_TEXT = '"Panic" is a feature that allows you to instantly halt the program and revert your desktop background back to the "panic background" set in the wallpaper sub-tab. (found in the annoyance tab)\n\nThere are a few ways to initiate panic, but one of the easiest to access is setting a hotkey here. You should also make sure to change your panic wallpaper to your currently used wallpaper before using Edgeware!'
PRESET_TEXT = "Please be careful before importing unknown config presets! Double check to make sure you're okay with the settings before launching Edgeware."


class StartTab(ScrollFrame):
    def __init__(self, vars: Vars, local_version: str, live_version: str, pack: Pack) -> None:
        super().__init__()

        panic_section = ConfigSection(self.viewPort, "Panic Settings", PANIC_TEXT)
        panic_section.pack()

        set_global_panic_button = Button(
            panic_section,
            text=f"Set Global\nPanic Key\n<{vars.global_panic_key.get()}>",
            command=lambda: request_global_panic_key(set_global_panic_button, vars.global_panic_key),
            cursor="question_arrow",
        )
        set_global_panic_button.pack(padx=PAD, pady=PAD, fill="x", side="left", expand=1)
