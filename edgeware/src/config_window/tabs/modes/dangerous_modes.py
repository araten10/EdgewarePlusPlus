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
    GROOVE,
    RAISED,
    Checkbutton,
    Entry,
    Frame,
    Label,
    Scale,
)
from tkinter.font import Font

from config_window.utils import set_widget_states
from config_window.vars import Vars
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip


class DangerousModesTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font) -> None:
        super().__init__()

        # Timer
        Label(self.viewPort, text="Timer Settings", font=title_font, relief=GROOVE).pack(pady=2)

        timer_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        timer_frame.pack(fill="x")

        timer_toggle = Checkbutton(
            timer_frame,
            text="Timer Mode",
            variable=vars.timer_mode,
            command=lambda: set_widget_states(vars.timer_mode.get(), timer_group),
            cursor="question_arrow",
        )
        timer_toggle.pack(side="left", fill="x", padx=5)
        CreateToolTip(
            timer_toggle,
            'Enables "Run on Startup" and disables the Panic function until the time limit is reached.\n\n'
            '"Safeword" allows you to set a password to re-enable Panic, if need be.\n\n'
            "Note: Run on Startup does not need to stay enabled for Timer Mode to work. However, disabling it may cause "
            "instability when running Edgeware multiple times without changing config settings.",
        )
        timer_slider = Scale(timer_frame, label="Timer Time (mins)", from_=1, to=1440, orient="horizontal", variable=vars.timer_time)
        timer_slider.pack(side="left", fill="x", expand=1, padx=10)

        safeword_frame = Frame(timer_frame)
        safeword_frame.pack(side="right", fill="x", padx=5)
        Label(safeword_frame, text="Emergency Safeword").pack()
        timer_safeword = Entry(safeword_frame, show="*", textvariable=vars.timer_password)
        timer_safeword.pack(expand=1, fill="both")

        timer_group = [timer_safeword, timer_slider]
        set_widget_states(vars.timer_mode.get(), timer_group)

        # Mitosis
        Label(self.viewPort, text="Mitosis Mode", font=title_font, relief=GROOVE).pack(pady=2)

        mitosis_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        mitosis_frame.pack(fill="x")

        mitosis_toggle = Checkbutton(
            mitosis_frame,
            text="Mitosis Mode",
            variable=vars.mitosis_mode,
            command=lambda: set_widget_states(vars.mitosis_mode.get(), mitosis_group),
            cursor="question_arrow",
        )
        mitosis_toggle.pack(side="left", fill="x", padx=5)
        CreateToolTip(mitosis_toggle, "When a popup is closed, more popups will spawn in it's place based on the mitosis strength.")
        mitosis_strength = Scale(mitosis_frame, label="Mitosis Strength", orient="horizontal", from_=2, to=10, variable=vars.mitosis_strength)
        mitosis_strength.pack(side="left", fill="x", expand=1, padx=10)

        mitosis_group = [mitosis_strength]
        set_widget_states(vars.mitosis_mode.get(), mitosis_group)
