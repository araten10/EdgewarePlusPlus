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


class HibernateModeTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font) -> None:
        super().__init__()

        Label(self.viewPort, text="Hibernate Mode", font=title_font, relief=GROOVE).pack(pady=2)

        hibernate_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        hibernate_frame.pack(fill="x")

        type_frame = Frame(hibernate_frame)
        type_frame.pack(fill="x", side="left")
        hibernate_toggle = Checkbutton(
            type_frame,
            text="Hibernate Mode",
            variable=vars.hibernate_mode,
            command=lambda: widget_state_helper(vars.hibernate_type.get()),
            cursor="question_arrow",
        )
        hibernate_toggle.pack(fill="x", side="top")
        CreateToolTip(
            hibernate_toggle,
            "Runs Edgeware silently without any popups.\n\n"
            "After a random time in the specified range, Edgeware activates and barrages the user with popups "
            'based on the "Awaken Activity" value (depending on the hibernate type), then goes back to "sleep".\n\n'
            'Check the "About" tab for more detailed information on each hibernate type.',
        )
        fix_wallpaper_toggle = Checkbutton(type_frame, text="Fix Wallpaper", variable=vars.hibernate_fix_wallpaper, cursor="question_arrow")
        fix_wallpaper_toggle.pack(fill="x", side="top")
        CreateToolTip(
            fix_wallpaper_toggle,
            '"fixes" your wallpaper after hibernate is finished by changing it to'
            " your panic wallpaper. If left off, it will keep the pack's wallpaper on until you panic"
            " or change it back yourself.",
        )
        hibernate_types = ["Original", "Spaced", "Glitch", "Ramp", "Pump-Scare", "Chaos"]
        OptionMenu(type_frame, vars.hibernate_type, *hibernate_types, command=lambda key: widget_state_helper(key)).pack(fill="x", side="top")

        description_frame = Frame(hibernate_frame, borderwidth=2, relief=GROOVE)
        description_frame.pack(fill="both", side="left", expand=1, padx=2, pady=2)
        description = Label(description_frame, text="Error loading Hibernate Description!", wraplength=175)
        description.pack(fill="y", pady=2)

        min_sleep_frame = Frame(hibernate_frame)
        min_sleep_frame.pack(fill="x", side="left")
        min_sleep_scale = Scale(min_sleep_frame, label="Min Sleep (sec)", variable=vars.hibernate_delay_min, orient="horizontal", from_=1, to=7200)
        min_sleep_scale.pack(fill="y")
        min_sleep_manual = Button(
            min_sleep_frame,
            text="Manual min...",
            command=lambda: assign(vars.hibernate_delay_min, simpledialog.askinteger("Manual Minimum Sleep (sec)", prompt="[1-7200]: ")),
        )
        min_sleep_manual.pack(fill="y")

        max_sleep_frame = Frame(hibernate_frame)
        max_sleep_frame.pack(fill="x", side="left")
        max_sleep_button = Scale(max_sleep_frame, label="Max Sleep (sec)", variable=vars.hibernate_delay_max, orient="horizontal", from_=2, to=14400)
        max_sleep_button.pack(fill="y")
        max_sleep_manual = Button(
            max_sleep_frame,
            text="Manual max...",
            command=lambda: assign(vars.hibernate_delay_max, simpledialog.askinteger("Manual Maximum Sleep (sec)", prompt="[2-14400]: ")),
        )
        max_sleep_manual.pack(fill="y")

        activity_frame = Frame(hibernate_frame)
        activity_frame.pack(fill="x", side="left")
        activity_scale = Scale(activity_frame, label="Awaken Activity", orient="horizontal", from_=1, to=50, variable=vars.hibernate_activity)
        activity_scale.pack(fill="y")
        activity_manual = Button(
            activity_frame,
            text="Manual act...",
            command=lambda: assign(vars.hibernate_activity, simpledialog.askinteger("Manual Wakeup Activity", prompt="[1-50]: ")),
        )
        activity_manual.pack(fill="y")

        length_frame = Frame(hibernate_frame)
        length_frame.pack(fill="x", side="left")
        length_scale = Scale(length_frame, label="Max Length (sec)", variable=vars.hibernate_activity_length, orient="horizontal", from_=5, to=300)
        length_scale.pack(fill="y")
        length_manual = Button(
            length_frame,
            text="Manual length...",
            command=lambda: assign(vars.hibernate_activity_length, simpledialog.askinteger("Manual Hibernate Length", prompt="[5-300]: ")),
        )
        length_manual.pack(fill="y")

        sleep_group = [min_sleep_scale, min_sleep_manual, max_sleep_button, max_sleep_manual]
        activity_group = [activity_scale, activity_manual]
        length_group = [length_scale, length_manual]

        def widget_state_helper(key: str) -> None:
            if key == "Original":
                description.configure(text="Creates an immediate quantity of popups on wakeup based on the awaken activity.\n\n")
                if vars.hibernate_mode.get():
                    set_widget_states(False, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Spaced":
                description.configure(text="Creates popups consistently over the hibernate length, based on popup delay.\n\n")
                if vars.hibernate_mode.get():
                    set_widget_states(False, activity_group)
                    set_widget_states(True, length_group)
                    set_widget_states(True, sleep_group)
            if key == "Glitch":
                description.configure(text="Creates popups at random times over the hibernate length, with the max amount spawned based on awaken activity.\n")
                if vars.hibernate_mode.get():
                    set_widget_states(True, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Ramp":
                description.configure(
                    text="Creates a ramping amount of popups over the hibernate length, popups at fastest speed based on awaken activity, fastest speed based on popup delay."
                )
                if vars.hibernate_mode.get():
                    set_widget_states(True, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Pump-Scare":
                description.configure(
                    text="Spawns a popup, usually accompanied by audio, then quickly deletes it. Best used on packs with short audio files. Like a horror game, but horny?"
                )
                if vars.hibernate_mode.get():
                    set_widget_states(False, length_group)
                    set_widget_states(False, activity_group)
                    set_widget_states(True, sleep_group)
            if key == "Chaos":
                description.configure(text="Every time hibernate activates, a random type (other than chaos) is selected.\n\n")
                if vars.hibernate_mode.get():
                    set_widget_states(True, length_group)
                    set_widget_states(True, activity_group)
                    set_widget_states(True, sleep_group)
            if not vars.hibernate_mode.get():
                set_widget_states(False, length_group)
                set_widget_states(False, activity_group)
                set_widget_states(False, sleep_group)

        widget_state_helper(vars.hibernate_type.get())
