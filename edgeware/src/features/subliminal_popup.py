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

from tkinter import Label, Toplevel

import os_utils
import utils
from config.settings import Settings
from pack import Pack


class SubliminalPopup(Toplevel):
    def __init__(self, settings: Settings, pack: Pack) -> None:
        self.subliminal = pack.random_subliminal()
        if not self.should_init():
            return
        super().__init__()

        self.attributes("-topmost", True)
        os_utils.set_borderless(self)
        self.attributes("-alpha", settings.subliminal_opacity)
        if os_utils.is_windows():
            self.wm_attributes("-transparentcolor", settings.theme.transparent_bg)

        monitor = utils.random_monitor(settings)

        label = Label(
            self,
            text=self.subliminal,
            font=(settings.theme.font, min(monitor.width, monitor.height) // 10),
            wraplength=monitor.width / 1.5,
            fg=settings.theme.fg,
            bg=(settings.theme.transparent_bg if os_utils.is_windows() else settings.theme.bg),
        )
        label.pack()

        x = monitor.x + (monitor.width - label.winfo_reqwidth()) // 2
        y = monitor.y + (monitor.height - label.winfo_reqheight()) // 2

        self.geometry(f"+{x}+{y}")
        self.after(settings.subliminal_timeout, self.destroy)

    def should_init(self) -> bool:
        return self.subliminal
