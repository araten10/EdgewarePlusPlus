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


import subprocess
from tkinter import (
    GROOVE,
    Button,
    Entry,
    Frame,
    Label,
    OptionMenu,
)

from config.vars import Vars
from config.window.widgets.layout import ConfigSection, ConfigRow, ConfigToggle, set_enabled_when
from config.window.widgets.scroll_frame import ScrollFrame
from os_utils import delete_schedule, set_schedule

INTRO_TEXT = 'Want to have Edgeware run at a specific time every day? What about letting it trigger you randomly every so often? These options should have you covered!\n\nSchedule will run Edgeware whenever a timer is reached, which can be set here. It differs from something like "Hibernate Mode" (Found in the "Modes" tab) by allowing Edgeware to do whatever it can normally do. It also supports much longer forms of waiting, such as hours, days, or even weeks! If you want to make sure your schedule is working, there are debug buttons for it found in the "Troubleshooting" tab.'
TIMER_TEXT = " "
VARIANCE_TEXT = "If you want a little bit of randomness to Edgeware++ scheduling, here's the setting for it! Type in how long you want the task to be randomly *delayed* by, and Edgeware++ will launch sometime inbetween the original schedule time and the delayed time.\n\nNOTE: On Windows Task Scheduler, the delay will not show up in the task overview despite being active. If you want to confirm the delay, you can see it in the Properties of the task, under Triggers->Edit."


class SchedulingTab(ScrollFrame):
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        # Information

        schedule_section = ConfigSection(self.viewPort, "Scheduling", INTRO_TEXT)
        schedule_section.pack()

        schedule_row = ConfigRow(schedule_section)
        schedule_row.pack()

        schedule_toggle = ConfigToggle(schedule_row, "Enable Scheduling", variable=vars.schedule)
        schedule_toggle.grid(0, 0)

        repeat_toggle = ConfigToggle(schedule_row, "Repeat Schedule", variable=vars.repeat_schedule)
        repeat_toggle.grid(0, 1)

        schedule_frame = Frame(schedule_section)
        schedule_frame.pack(fill="both", side="top", expand=1)

        time_types = ["Minutes", "Hours", "Days"]

        # Relative Time

        relative_frame = Frame(schedule_section, borderwidth=2, relief=GROOVE)
        relative_frame.pack(fill="both", side="top", expand=1)

        Label(relative_frame, text="Run Edgeware++ in...", font="Default 8").pack(pady=2, side="left", fill="both")

        relative_time_number = Entry(relative_frame, textvariable=vars.schedule_time, width=5)
        relative_time_number.pack(padx=5, pady=5, side="left", fill="x")

        relative_time_type = OptionMenu(relative_frame, vars.time_type, *time_types)
        relative_time_type.pack(padx=5, pady=5, side="left", fill="x")

        set_enabled_when(relative_time_type, enabled=(vars.schedule, True))
        set_enabled_when(relative_time_number, enabled=(vars.schedule, True))

        Label(relative_frame, text="and repeat every...", font="Default 8").pack(pady=2, side="left", fill="both")

        repeat_time_number = Entry(relative_frame, textvariable=vars.repeat_time, width=5)
        repeat_time_number.pack(padx=5, pady=5, side="left", fill="x")

        repeat_time_type = OptionMenu(relative_frame, vars.repeat_type, *time_types)
        repeat_time_type.pack(padx=5, pady=5, side="left", fill="x")

        set_enabled_when(repeat_time_number, enabled=(vars.repeat_schedule, True))
        set_enabled_when(repeat_time_type, enabled=(vars.repeat_schedule, True))

        # Variance
        variance_section = ConfigSection(self.viewPort, "Variance", VARIANCE_TEXT)
        variance_section.pack()

        variance_frame = Frame(variance_section)
        variance_frame.pack(fill="both", side="top", expand=1)

        Label(variance_frame, text="Delay the scheduled task for up to...", font="Default 8").pack(pady=2, side="left", fill="both")

        variance_time_number = Entry(variance_frame, textvariable=vars.variance_time, width=5)
        variance_time_number.pack(padx=5, pady=5, side="left", fill="x")

        variance_time_type = OptionMenu(variance_frame, vars.variance_type, *time_types)
        variance_time_type.pack(padx=5, pady=5, side="left", fill="x")

        # Absolute Time, if we decide to implement it

        # absolute_frame = Frame(schedule_section, borderwidth=2, relief=GROOVE)
        # absolute_frame.pack(fill="both", side="top", expand=1)
        #
        # Label(absolute_frame, text="Run Edgeware++ on...", font="Default 8").pack(pady=2, side="left", fill="both")
        #
        # absolute_calendar = DateEntry(absolute_frame, date_pattern="mm-dd-yyyy")
        # absolute_calendar.pack(padx=5, pady=5, side="left", fill="x")
        #
        # Label(absolute_frame, text="at", font="Default 8").pack(pady=2, side="left", fill="both")
        #
        # time_picker = SpinTimePickerOld(absolute_frame)
        # time_picker.addAll(timep.HOURS12)
        # time_picker.configureAll(width=5)
        # time_picker.configure_period(width=5)
        # time_picker.pack(padx=5, pady=5, side="left", fill="x")
