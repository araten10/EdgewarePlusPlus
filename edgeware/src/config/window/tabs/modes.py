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
    OptionMenu,
    StringVar,
)

from config.vars import Vars
from config.window.widgets.layout import PAD, ConfigDropdown, ConfigRow, ConfigScale, ConfigSection, ConfigToggle, set_enabled_when
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip

LOWKEY_TEXT = "Forces popups to spawn in the corner of your screen, rather than randomly all over. Best used with popup timeout or high delay as popups will stack on top of eachother."
HIBERNATE_TEXT = "Runs Edgeware++ covertly, without any popups. Instead, after a certain amount of time a barrage of popups will all spawn at once depending on the hibernate mode set.\n\nMinimum/maximum sleep durations determine the range of the payload timer- hibernate mode will activate sometime between these two values.\nAwaken activity determines the intensity of the hibernate mode payload, essentially the amount of popups spawned when it triggers.\nMax activity length is how long the payload lasts, if using a hibernate type that has a duration."
MITOSIS_TEXT = "When a popup is closed, more popups will spawn in its place depending on the mitosis strength.\n\nWhile not dangerous by itself, this can easily cause performance issues and other problems if the popup delay is set too low and mitosis strength too high. It is generally safe to experiment with this at slower popup intervals, but make sure you know what you're doing before increasing it too high."


class BasicModesTab(ScrollFrame):
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        # Lowkey
        lowkey_section = ConfigSection(self.viewPort, "Lowkey Mode", LOWKEY_TEXT)
        lowkey_section.pack()

        lowkey_row = ConfigRow(lowkey_section)
        lowkey_row.pack()

        ConfigToggle(lowkey_row, "Enable Lowkey Mode", variable=vars.lowkey_mode).pack()
        lowkey_corners = ["Top Right", "Top Left", "Bottom Left", "Bottom Right", "Random"]
        lowkey_corner_string = StringVar(self, lowkey_corners[vars.lowkey_corner.get()])
        lowkey_dropdown = OptionMenu(lowkey_row, lowkey_corner_string, *lowkey_corners, command=lambda x: (vars.lowkey_corner.set(lowkey_corners.index(x))))
        lowkey_dropdown.pack(padx=PAD, pady=PAD, side="left", fill="x", expand=True)
        set_enabled_when(lowkey_dropdown, enabled=(vars.lowkey_mode, True))

        # Mitosis
        mitosis_section = ConfigSection(self.viewPort, "Mitosis Mode", MITOSIS_TEXT)
        mitosis_section.pack()

        mitosis_row_1 = ConfigRow(mitosis_section)
        mitosis_row_1.pack()
        ConfigToggle(mitosis_row_1, "Enable Mitosis Mode", variable=vars.mitosis_mode).pack()
        mitosis_row_2 = ConfigRow(mitosis_section)
        mitosis_row_2.pack()
        ConfigScale(mitosis_row_2, "Mitosis Strength (number of popups)", vars.mitosis_strength, 2, 10, enabled=(vars.mitosis_mode, True)).pack()

        # Hibernate
        hibernate_section = ConfigSection(self.viewPort, "Hibernate Mode", HIBERNATE_TEXT)
        hibernate_section.pack()

        hibernate_row_1 = ConfigRow(hibernate_section)
        hibernate_row_1.pack()
        ConfigToggle(hibernate_row_1, "Enable Hibernate Mode", variable=vars.hibernate_mode).pack()

        hibernate_row_2 = ConfigRow(hibernate_section)
        hibernate_row_2.pack()
        ConfigDropdown(
            hibernate_row_2,
            vars.hibernate_type,
            {
                "Original": "Creates an immediate quantity of popups on wakeup based on the awaken activity.",
                "Spaced": "Creates popups consistently over the hibernate length, based on popup delay.",
                "Glitch": "Creates popups at random times over the hibernate length, with the max amount spawned based on awaken activity.",
                "Ramp": "Creates a ramping amount of popups over the hibernate length based on awaken activity, fastest speed based on popup delay.",
                "Pump-Scare": "Spawns a popup, usually accompanied by audio, then quickly deletes it. Best used on packs with short audio files. Like a horror game, but horny?",
                "Chaos": "Every time hibernate activates, a random type (other than chaos) is selected.",
            },
            width=42,
            wrap=295,
            enabled=(vars.hibernate_mode, True),
        ).pack()

        hibernate_row_3 = ConfigRow(hibernate_section)
        hibernate_row_3.pack()
        hibernate_fix_wallpaper = ConfigToggle(hibernate_row_3, "Fix Wallpaper", variable=vars.hibernate_fix_wallpaper, enabled=(vars.hibernate_mode, True))
        hibernate_fix_wallpaper.pack()
        CreateToolTip(
            hibernate_fix_wallpaper,
            "When enabled, this setting reverts your wallpaper back to your panic wallpaper automatically once the hibernate payload has "
            "finished running and you've closed every popup. This ensures your computer looks as 'normal' as possible when hibernate mode is "
            "not currently spawning popups.",
        )

        hibernate_row_4 = ConfigRow(hibernate_section)
        hibernate_row_4.pack()
        ConfigScale(hibernate_row_4, "Minimum Sleep Duration (seconds)", vars.hibernate_delay_min, 1, 7200, enabled=(vars.hibernate_mode, True)).pack()
        ConfigScale(hibernate_row_4, "Maximum Sleep Duration (seconds)", vars.hibernate_delay_max, 2, 14400, enabled=(vars.hibernate_mode, True)).pack()

        hibernate_row_5 = ConfigRow(hibernate_section)
        hibernate_row_5.pack()
        ConfigScale(
            hibernate_row_5,
            "Awaken Activity",
            vars.hibernate_activity,
            1,
            50,
            enabled=[(vars.hibernate_mode, True), (vars.hibernate_type, ["Original", "Glitch", "Ramp", "Chaos"])],
        ).pack()
        ConfigScale(
            hibernate_row_5,
            "Max Activity Length (seconds)",
            vars.hibernate_activity_length,
            5,
            300,
            enabled=[(vars.hibernate_mode, True), (vars.hibernate_type, ["Spaced", "Glitch", "Ramp", "Chaos"])],
        ).pack()
