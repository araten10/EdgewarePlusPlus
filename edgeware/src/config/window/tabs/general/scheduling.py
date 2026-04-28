# Copyright (C) 2026 Araten & Marigold
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


from config.window.widgets.layout import (
    ConfigSection,
)
from config.window.widgets.scroll_frame import ScrollFrame
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
    Text,
)
from config.window.utils import set_schedule

INTRO_TEXT = 'Want to have Edgeware run at a specific time every day? What about letting it trigger you randomly every so often? These options should have you covered!\n\nSchedule will run Edgeware whenever a timer is reached, which can be set here. It differs from something like "Hibernate Mode" (Found in the "Modes" tab) by allowing Edgeware to do whatever it can normally do. It also supports much longer forms of waiting, such as hours, days, or even weeks!'


class SchedulingTab(ScrollFrame):
    def __init__(self) -> None:
        super().__init__()

        # Information

        schedule_section = ConfigSection(self.viewPort, "Scheduling", INTRO_TEXT)
        schedule_section.pack()

        schedule_frame = Frame(schedule_section)
        schedule_frame.pack(fill="both", side="left", expand=1)

        Button(schedule_frame, text="Apply Schedule", command=lambda: set_schedule()).pack(fill="both", expand=1)
