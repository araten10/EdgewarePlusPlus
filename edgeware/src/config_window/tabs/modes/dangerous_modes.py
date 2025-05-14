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
from settings import Vars
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip
from widgets.config_widgets import (
    ConfigDropdown,
    ConfigRow,
    ConfigScale,
    ConfigSection,
    ConfigToggle,
)

TIMER_TEXT = 'Makes it so you cannot panic for a specified duration, essentially forcing you to endure the payload until the timer is up.\n\nA safeword can be used if you wish to still use panic during this time. It is recommended that you generate one via a password generator/keysmash and save it somewhere easily accessible; not only does this help in emergency situations where you need to turn off Edgeware++, but also makes it harder to memorize so the \"fetishistic danger\" remains.'
MITOSIS_TEXT = 'When a popup is closed, more popups will spawn in its place depending on the mitosis strength.\n\nWhile not dangerous by itself, this can easily cause performance issues and other problems if the popup delay is set too low and mitosis strength too high. It is generally safe to experiment with this at slower popup intervals, but make sure you know what you\'re doing before increasing it too high.'
class DangerousModesTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font) -> None:
        super().__init__()

        # Timer
        timer_section = ConfigSection(self.viewPort, "Timer Mode", TIMER_TEXT)
        timer_section.pack()

        timer_row = ConfigRow(timer_section)
        timer_row.pack()

        ConfigToggle(timer_row, "Enable Timer Mode", variable=vars.timer_mode, command=lambda: set_widget_states(vars.timer_mode.get(), timer_group)).pack()
        safeword_frame = Frame(timer_row)
        safeword_frame.pack(side="left", expand=True)
        Label(safeword_frame, text="Emergency Safeword").pack()
        timer_safeword = Entry(safeword_frame, show="*", textvariable=vars.timer_password)
        timer_safeword.pack(expand=1, fill="both")

        timer_scale = ConfigScale(timer_section, "Timer Lockout Time (minutes)", vars.timer_time, 1, 1440)
        timer_scale.pack()

        timer_group = [timer_safeword, timer_scale]
        set_widget_states(vars.timer_mode.get(), timer_group)

        # Mitosis
        mitosis_section = ConfigSection(self.viewPort, "Mitosis Mode", MITOSIS_TEXT)
        mitosis_section.pack()

        mitosis_row = ConfigRow(mitosis_section)
        mitosis_row.pack()
        ConfigToggle(mitosis_row, "Enable Mitosis Mode", variable=vars.mitosis_mode, command=lambda: set_widget_states(vars.mitosis_mode.get(), mitosis_group)).pack()

        mitosis_scale = ConfigScale(mitosis_section, "Mitosis Strength (number of popups)", vars.mitosis_strength, 2, 10)
        mitosis_scale.pack()

        mitosis_group = [mitosis_scale]
        set_widget_states(vars.mitosis_mode.get(), mitosis_group)
