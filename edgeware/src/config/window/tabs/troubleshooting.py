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
from config.window.utils import request_legacy_panic_key
from config.window.widgets.layout import (
    ConfigSection,
)
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip
from pack import Pack


class TroubleshootingTab(ScrollFrame):
    def __init__(self, vars: Vars, pack: Pack) -> None:
        super().__init__()

        # Legacy
        legacy_section = ConfigSection(self.viewPort, "Legacy")
        legacy_section.pack()

        set_legacy_panic_button = Button(
            legacy_section,
            text=f"Set Legacy\nPanic Key\n<{vars.panic_key.get()}>",
            command=lambda: request_legacy_panic_key(set_legacy_panic_button, vars.panic_key),
            cursor="question_arrow",
        )
        set_legacy_panic_button.pack(fill="x", side="left", expand=1)
        CreateToolTip(
            set_legacy_panic_button,
            'This is the old panic key, use in case the new panic system doesn\'t work on your computer. To use this hotkey you must be "focused" on an Edgeware image or video popup. Click on a popup before using.',
        )
