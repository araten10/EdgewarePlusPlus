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
from config.window.utils import delete_schedule, set_schedule
from config.window.widgets.layout import ConfigSection, ConfigToggle
from config.window.widgets.scroll_frame import ScrollFrame
from tkcalendar import DateEntry
from tktimepicker import SpinTimePickerOld
from tktimepicker import constants as timep

INTRO_TEXT = 'Want to have Edgeware run at a specific time every day? What about letting it trigger you randomly every so often? These options should have you covered!\n\nSchedule will run Edgeware whenever a timer is reached, which can be set here. It differs from something like "Hibernate Mode" (Found in the "Modes" tab) by allowing Edgeware to do whatever it can normally do. It also supports much longer forms of waiting, such as hours, days, or even weeks!'
TIMER_TEXT = "asdfg"


class SchedulingTab(ScrollFrame):
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        # Information

        schedule_section = ConfigSection(self.viewPort, "Scheduling", INTRO_TEXT)
        schedule_section.pack()

        schedule_frame = Frame(schedule_section)
        schedule_frame.pack(fill="both", side="top", expand=1)

        schedule_buttons_frame = Frame(schedule_frame)
        schedule_buttons_frame.pack(fill="both", side="top", expand=1)

        Button(schedule_frame, text="Open Task Scheduler (Windows Only)", height=1, command=lambda: subprocess.Popen("taskschd.msc", shell=True)).pack(
            fill="both", expand=1
        )

        Button(schedule_buttons_frame, text="Apply Schedule", height=3, command=lambda: set_schedule(vars)).pack(fill="both", side="left", expand=1)
        Button(schedule_buttons_frame, text="Delete Schedule", height=3, command=lambda: delete_schedule()).pack(fill="both", side="left", expand=1)

        schedule_time_section = ConfigSection(self.viewPort, "Schedule Timer", TIMER_TEXT)
        schedule_time_section.pack()

        schedule_types = ["Relative", "Absolute"]
        # broken atm
        schedule_dropdown = OptionMenu(schedule_time_section, vars.schedule_type, *schedule_types)
        schedule_dropdown.configure(width=12)
        schedule_dropdown.pack(fill="both", side="top", padx=5, pady=5)

        schedule_options_frame = Frame(schedule_time_section)
        schedule_options_frame.pack(fill="both", side="top", expand=1)

        restart_toggle = ConfigToggle(schedule_options_frame, text="Redo Task On Panic", cursor="question_arrow", variable=vars.repeat_schedule).grid(0, 0)
        # CreateToolTip(
        #     restart_toggle,
        #     'Adds another task with the "same settings" when panic is initiated.\n\n'
        #     'For example, a task scheduled for 3 hours from now would create\n'
        #     'another task 3 hours from when panic was used. A task set for 2:00 AM\n'
        #     'would be set for 2:00 AM the next day. This will also use random variance\n'
        #     'if that setting is enabled!',
        # )
        surprise_toggle = ConfigToggle(schedule_options_frame, text="Random Time In Range", cursor="question_arrow", variable=vars.variance).grid(0, 1)
        # CreateToolTip(
        #     surprise_toggle,
        #     'Randomly shuffles time settings to give you a completely unpredictable task!',
        # )

        time_types = ["Minutes", "Hours", "Days"]

        # Relative Time

        relative_frame = Frame(schedule_time_section, borderwidth=2, relief=GROOVE)
        relative_frame.pack(fill="both", side="top", expand=1)

        Label(relative_frame, text="Run Edgeware++ in...", font="Default 8").pack(pady=2, side="left", fill="both")

        relative_time_number = Entry(relative_frame, textvariable=vars.schedule_time, width=5)
        relative_time_number.pack(padx=5, pady=5, side="left", fill="x")

        Label(relative_frame, text="-", font="Default 8").pack(pady=2, side="left", fill="both")

        variance_time_number = Entry(relative_frame, textvariable=vars.variance_time, width=5)
        variance_time_number.pack(padx=5, pady=5, side="left", fill="x")

        relative_time_type = OptionMenu(relative_frame, vars.time_type, *time_types)
        relative_time_type.pack(padx=5, pady=5, side="left", fill="x")

        # Absolute Time

        absolute_frame = Frame(schedule_time_section, borderwidth=2, relief=GROOVE)
        absolute_frame.pack(fill="both", side="top", expand=1)

        Label(absolute_frame, text="Run Edgeware++ on...", font="Default 8").pack(pady=2, side="left", fill="both")

        absolute_calendar = DateEntry(absolute_frame, date_pattern="mm-dd-yyyy")
        absolute_calendar.pack(padx=5, pady=5, side="left", fill="x")

        Label(absolute_frame, text="at", font="Default 8").pack(pady=2, side="left", fill="both")

        time_picker = SpinTimePickerOld(absolute_frame)
        time_picker.addAll(timep.HOURS12)
        time_picker.configureAll(width=5)
        time_picker.configure_period(width=5)
        time_picker.pack(padx=5, pady=5, side="left", fill="x")

        # def schedule_helper(vars: Vars) -> None:
