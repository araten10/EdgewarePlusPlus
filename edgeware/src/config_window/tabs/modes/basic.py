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

LOWKEY_TEXT = "Forces popups to spawn in the corner of your screen, rather than randomly all over. Best used with Popup Timeout or high delay as popups will stack on top of eachother."

class BasicModesTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font) -> None:
        super().__init__()

        # Lowkey
        lowkey_section = ConfigSection(self.viewPort, "Lowkey Mode", LOWKEY_TEXT)
        lowkey_section.pack()

        lowkey_row = ConfigRow(lowkey_section)
        lowkey_row.pack()

        lowkey_toggle = ConfigToggle(lowkey_row, "Lowkey Mode", variable=vars.lowkey_mode, command=lambda: set_widget_states(vars.lowkey_mode.get(), lowkey_group))
        lowkey_toggle.pack()
        lowkey_corners = ["Top Right", "Top Left", "Bottom Left", "Bottom Right", "Random"]
        lowkey_corner_string = StringVar(self, lowkey_corners[vars.lowkey_corner.get()])
        lowkey_dropdown = OptionMenu(lowkey_row, lowkey_corner_string, *lowkey_corners, command=lambda x: (vars.lowkey_corner.set(lowkey_corners.index(x))))
        lowkey_dropdown.pack(side="left", expand=True)

        lowkey_group = [lowkey_dropdown]
        set_widget_states(vars.lowkey_mode.get(), lowkey_group)

        # Movement
        Label(self.viewPort, text="Movement Mode", font=title_font, relief=GROOVE).pack(pady=2)

        movement_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        movement_frame.pack(fill="x")

        movement_chance_frame = Frame(movement_frame)
        movement_chance_frame.pack(fill="x", side="left")
        movement_chance = Scale(movement_chance_frame, label="Moving Chance", orient="horizontal", variable=vars.moving_chance, cursor="question_arrow")
        movement_chance.pack(fill="x")
        CreateToolTip(
            movement_chance,
            'Gives each popup a chance to move around the screen instead of staying still. The popup will have the "Buttonless" '
            "property, so it is easier to click.\n\nNOTE: Having many of these popups at once may impact performance. Try a lower percentage chance or higher popup delay to start.",
        )
        movement_direction = Checkbutton(movement_chance_frame, text="Random Direction", variable=vars.moving_random, cursor="question_arrow")
        movement_direction.pack(fill="x")
        CreateToolTip(movement_direction, "Makes moving popups move in a random direction rather than the static diagonal one.")

        movement_speed_frame = Frame(movement_frame)
        movement_speed_frame.pack(fill="x", side="left")
        Scale(movement_speed_frame, label="Max Movespeed", from_=1, to=15, orient="horizontal", variable=vars.moving_speed).pack(fill="x")
        Button(
            movement_speed_frame, text="Manual speed...", command=lambda: assign(vars.moving_speed, simpledialog.askinteger("Manual Speed", prompt="[1-15]: "))
        ).pack(fill="x")
