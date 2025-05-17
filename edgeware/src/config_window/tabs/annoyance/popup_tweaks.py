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

from tkinter import CENTER, GROOVE, RAISED, BooleanVar, Checkbutton, Frame, Label, Message, Misc, Scale
from tkinter.font import Font

from config_window.utils import (
    config,
    set_widget_states,
)
from screeninfo import Monitor, get_monitors
from settings import Vars
from widgets.config_widgets import (
    ConfigScale,
    ConfigToggle,
)
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

OVERLAY_TEXT = 'Overlays are more or less modifiers for popups- adding onto them without changing their core behaviour.\n\n•Subliminals add a transparent gif over affected popups, defaulting to a hypnotic spiral if there are none added in the current pack. (this may cause performance issues with lots of popups, try a low max to start)\n•Denial "censors" a popup by blurring it, simple as.'


class MonitorCheckbutton(ConfigToggle):
    def __init__(self, master: Misc, monitor: Monitor) -> None:
        self.monitor = monitor
        self.var = BooleanVar(master, self.monitor.name not in config["disabledMonitors"])
        super().__init__(master, text=f"{self.monitor.name} ({self.monitor.width}x{self.monitor.height})", variable=self.var, command=self.update_monitors)

    def update_monitors(self) -> None:
        if self.var.get():
            config["disabledMonitors"].remove(self.monitor.name)
        else:
            config["disabledMonitors"].append(self.monitor.name)


class PopupTweaksTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]) -> None:
        super().__init__()

        popup_frame_2 = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        popup_frame_2.pack(fill="x")
        ConfigScale(popup_frame_2, label="Popup Opacity (%)", from_=5, to=100, variable=vars.opacity).pack()

        timeout_frame = Frame(popup_frame_2)
        timeout_frame.pack(fill="y", side="left", padx=3, expand=1)
        timeout_scale = ConfigScale(timeout_frame, label="Time (sec)", from_=1, to=120, variable=vars.timeout)
        timeout_scale.pack()
        ConfigToggle(
            timeout_frame,
            "Popup Timeout",
            variable=vars.timeout_enabled,
            command=lambda: set_widget_states(vars.timeout_enabled.get(), timeout_group),
        ).pack()

        timeout_group = [timeout_scale]
        set_widget_states(vars.timeout_enabled.get(), timeout_group)

        popup_frame_3 = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        popup_frame_3.pack(fill="x")

        ConfigToggle(popup_frame_3, "Popup close opens web page", variable=vars.web_on_popup_close).pack()

        buttonless_toggle = ConfigToggle(popup_frame_3, "Buttonless Closing Popups", variable=vars.buttonless, cursor="question_arrow")
        buttonless_toggle.pack()
        CreateToolTip(
            buttonless_toggle,
            'Disables the "close button" on popups and allows you to click anywhere on the popup to close it.\n\n'
            "IMPORTANT: The panic keyboard hotkey will only work in this mode if you use it while *holding down* the mouse button over a popup!",
        )

        single_mode_toggle = ConfigToggle(popup_frame_3, "Single Roll Per Popup", variable=vars.single_mode, cursor="question_arrow")
        single_mode_toggle.pack()
        CreateToolTip(
            single_mode_toggle,
            'The randomization in Edgeware does not check to see if a previous "roll" succeeded or not when a popup is spawned.\n\n'
            "For example, if you have audio, videos, and prompts all turned on, there's a very real chance you will get all of them popping up at the same "
            "time if the percentage for each is high enough.\n\nThis mode ensures that only one of these types will spawn whenever a popup is created. It "
            "delivers a more consistent experience and less double (or triple) popups.\n\nADVANCED DETAILS: In this mode, the chance of a popup appearing "
            "is used as a weight to choose a single popup type to spawn.",
        )

        # Overlays
        Label(self.viewPort, text="Popup Overlays", font=title_font, relief=GROOVE).pack(pady=2)

        overlay_message = Message(self.viewPort, text=OVERLAY_TEXT, justify=CENTER, width=675)
        overlay_message.pack(fill="both")
        message_group.append(overlay_message)

        overlay_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        overlay_frame.pack(fill="x")

        subliminal_frame = Frame(overlay_frame)
        subliminal_frame.pack(fill="x", side="left", padx=(3, 0))
        ConfigToggle(
            subliminal_frame,
            "Subliminal Overlays",
            variable=vars.popup_subliminals,
            command=lambda: set_widget_states(vars.popup_subliminals.get(), subliminals_group),
        ).pack()

        subliminal_chance_frame = Frame(subliminal_frame)
        subliminal_chance_frame.pack(fill="x", side="left", padx=3)
        subliminal_chance_scale = ConfigScale(subliminal_chance_frame, label="Sublim. Chance (%)", from_=1, to=100, variable=vars.subliminal_chance)
        subliminal_chance_scale.pack()

        subliminal_alpha_frame = Frame(subliminal_frame)
        subliminal_alpha_frame.pack(fill="x", side="left", padx=3)
        subliminal_alpha_scale = ConfigScale(subliminal_alpha_frame, label="Sublim. Alpha (%)", from_=1, to=99, variable=vars.subliminal_opacity)
        subliminal_alpha_scale.pack()

        max_subliminal_frame = Frame(subliminal_frame)
        max_subliminal_frame.pack(fill="x", side="left", padx=3)
        max_subliminal_scale = ConfigScale(max_subliminal_frame, label="Max Subliminals", from_=1, to=200, variable=vars.max_subliminals)
        max_subliminal_scale.pack()

        subliminals_group = [
            subliminal_chance_scale,
            subliminal_alpha_scale,
            max_subliminal_scale,
        ]
        set_widget_states(vars.popup_subliminals.get(), subliminals_group)

        denial_frame = Frame(overlay_frame)
        denial_frame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        ConfigToggle(denial_frame, "Denial Overlays", variable=vars.denial_mode, command=lambda: set_widget_states(vars.denial_mode.get(), denial_group)).pack()
        denial_chance_slider = ConfigScale(denial_frame, label="Denial Chance", from_=1, to=100, variable=vars.denial_chance)
        denial_chance_slider.pack()

        denial_group = [denial_chance_slider]
        set_widget_states(vars.denial_mode.get(), denial_group)

        # Monitors
        Label(self.viewPort, text="Enabled Monitors", font=title_font, relief=GROOVE).pack(pady=2)

        monitor_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        monitor_frame.pack(fill="x")
        for monitor in get_monitors():
            MonitorCheckbutton(monitor_frame, monitor).pack()

        # Movement
        Label(self.viewPort, text="Movement Mode", font=title_font, relief=GROOVE).pack(pady=2)

        movement_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        movement_frame.pack(fill="x")

        movement_chance_frame = Frame(movement_frame)
        movement_chance_frame.pack(fill="x", side="left")
        movement_chance = ConfigScale(movement_chance_frame, label="Moving Chance", from_=0, to=100, variable=vars.moving_chance)
        movement_chance.pack()
        CreateToolTip(
            movement_chance,
            'Gives each popup a chance to move around the screen instead of staying still. The popup will have the "Buttonless" '
            "property, so it is easier to click.\n\nNOTE: Having many of these popups at once may impact performance. Try a lower percentage chance or higher popup delay to start.",
        )
        movement_direction = ConfigToggle(movement_chance_frame, "Random Direction", variable=vars.moving_random, cursor="question_arrow")
        movement_direction.pack()
        CreateToolTip(movement_direction, "Makes moving popups move in a random direction rather than the static diagonal one.")

        movement_speed_frame = Frame(movement_frame)
        movement_speed_frame.pack(fill="x", side="left")
        Scale(movement_speed_frame, label="Max Movespeed", from_=1, to=15, orient="horizontal", variable=vars.moving_speed).pack(fill="x")

        hardware_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        hardware_frame.pack(fill="x")

        hardware_acceleration_toggle = Checkbutton(
            hardware_frame, text="Enable hardware acceleration", variable=vars.video_hardware_acceleration, cursor="question_arrow"
        )
        hardware_acceleration_toggle.pack(fill="both", side="top", expand=1, padx=2)
        CreateToolTip(
            hardware_acceleration_toggle, "Disabling hardware acceleration may increase CPU usage, but it can provide a more consistent and stable experience."
        )
