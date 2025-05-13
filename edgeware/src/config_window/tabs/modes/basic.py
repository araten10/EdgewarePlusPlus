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
    Button,
    Checkbutton,
    Frame,
    Label,
    OptionMenu,
    Scale,
    StringVar,
    simpledialog,
)
from tkinter.font import Font

from config_window.utils import (
    assign,
    set_widget_states,
)
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

LOWKEY_TEXT = "Forces popups to spawn in the corner of your screen, rather than randomly all over. Best used with popup timeout or high delay as popups will stack on top of eachother."
HIBERNATE_TEXT = "Runs Edgeware++ covertly, without any popups. Instead, after a certain amount of time a barrage of popups will all spawn at once depending on the hibernate mode set.\n\nMinimum/maximum sleep durations determine the range of the payload timer- hibernate mode will activate sometime between these two values.\nAwaken activity determines the intensity of the hibernate mode payload, essentially the amount of popups spawned when it triggers.\nMax activity length is how long the payload lasts, if using a hibernate type that has a duration."

class BasicModesTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font) -> None:
        super().__init__()

        # Lowkey
        lowkey_section = ConfigSection(self.viewPort, "Lowkey Mode", LOWKEY_TEXT)
        lowkey_section.pack()

        lowkey_row = ConfigRow(lowkey_section)
        lowkey_row.pack()

        ConfigToggle(lowkey_row, "Enable Lowkey Mode", variable=vars.lowkey_mode, command=lambda: set_widget_states(vars.lowkey_mode.get(), lowkey_group)).pack()
        lowkey_corners = ["Top Right", "Top Left", "Bottom Left", "Bottom Right", "Random"]
        lowkey_corner_string = StringVar(self, lowkey_corners[vars.lowkey_corner.get()])
        lowkey_dropdown = OptionMenu(lowkey_row, lowkey_corner_string, *lowkey_corners, command=lambda x: (vars.lowkey_corner.set(lowkey_corners.index(x))))
        lowkey_dropdown.pack(side="left", expand=True)

        lowkey_group = [lowkey_dropdown]
        set_widget_states(vars.lowkey_mode.get(), lowkey_group)

        #Hibernate
        hibernate_section = ConfigSection(self.viewPort, "Hibernate Mode", HIBERNATE_TEXT)
        hibernate_section.pack()

        hibernate_row_1 = ConfigRow(hibernate_section)
        hibernate_row_1.pack()

        ConfigToggle(hibernate_row_1, "Enable Hibernate Mode", variable=vars.hibernate_mode, command=lambda: widget_state_helper(vars.hibernate_type.get())).pack()
        ConfigDropdown(
            hibernate_row_1,
            vars.hibernate_type,
            {
                "Original": "Creates an immediate quantity of popups on wakeup based on the awaken activity.",
                "Spaced": "Creates popups consistently over the hibernate length, based on popup delay.",
                "Glitch": "Creates popups at random times over the hibernate length, with the max amount spawned based on awaken activity.",
                "Ramp": "Creates a ramping amount of popups over the hibernate length, popups at fastest speed based on awaken activity, fastest speed based on popup delay.",
                "Pump-Scare": "Spawns a popup, usually accompanied by audio, then quickly deletes it. Best used on packs with short audio files. Like a horror game, but horny?",
                "Chaos": "Every time hibernate activates, a random type (other than chaos) is selected."
            },
            width=42, wrap=295
        ).pack()

        hibernate_row_2 = ConfigRow(hibernate_section)
        hibernate_row_2.pack()

        min_sleep_scale = ConfigScale(hibernate_row_2, "Minimum Sleep Duration (seconds)", vars.hibernate_delay_min, 1, 7200)
        min_sleep_scale.pack()
        max_sleep_scale = ConfigScale(hibernate_row_2, "Maximum Sleep Duration (seconds)", vars.hibernate_delay_max, 2, 14400)
        max_sleep_scale.pack()
        sleep_group = [min_sleep_scale, max_sleep_scale]

        hibernate_row_3 = ConfigRow(hibernate_section)
        hibernate_row_3.pack()

        activity_scale = ConfigScale(hibernate_row_3, "Awaken Activity", vars.hibernate_activity, 1, 50)
        activity_scale.pack()
        length_scale = ConfigScale(hibernate_row_3, "Max Activity Length (seconds)", vars.hibernate_activity_length, 5, 300)
        length_scale.pack()
        activity_group = [activity_scale]
        length_group = [length_scale]

        #Hibernate Lambda
        #TODO: Fix this
        def widget_state_helper(key: str) -> None:
            if key == "Original":
                if vars.hibernate_mode.get():
                    set_widget_states(False, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Spaced":
                if vars.hibernate_mode.get():
                    set_widget_states(False, activity_group)
                    set_widget_states(True, length_group)
                    set_widget_states(True, sleep_group)
            if key == "Glitch":
                if vars.hibernate_mode.get():
                    set_widget_states(True, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Ramp":
                if vars.hibernate_mode.get():
                    set_widget_states(True, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Pump-Scare":
                if vars.hibernate_mode.get():
                    set_widget_states(False, length_group)
                    set_widget_states(False, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Chaos":
                if vars.hibernate_mode.get():
                    set_widget_states(True, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if not vars.hibernate_mode.get():
                set_widget_states(False, length_group)
                set_widget_states(False, activity_group)
                set_widget_states(False, sleep_group)

        widget_state_helper(vars.hibernate_type.get())
