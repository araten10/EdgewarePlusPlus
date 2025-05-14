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

from tkinter import CENTER, GROOVE, RAISED, BooleanVar, Button, Checkbutton, Frame, Label, Message, Misc, Scale, simpledialog, ttk
from tkinter.font import Font

from config_window.utils import (
    assign,
    config,
    set_widget_states,
)
from screeninfo import Monitor, get_monitors
from settings import Vars
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

INTRO_TEXT = 'Here is where you can change the most important settings of Edgeware: the frequency and behaviour of popups. The "Popup Timer Delay" is how long a popup takes to spawn, and the overall "Popup Chance" then rolls to see if the popup spawns. Keeping the chance at 100% allows for a consistent experience, while lowering it makes for a more random one.\n\nOnce ready to spawn, a popup can be many things: A regular image, a website link (opens in your default browser), a prompt you need to fill out, autoplaying audio or videos, or a subliminal message. All of these are rolled for corresponding to their respective frequency settings, which can be found in the "Audio/Video" tab, "Captions" tab, and this tab as well. There are also plenty of other settings there to configure popups to your liking~! '
OVERLAY_TEXT = 'Overlays are more or less modifiers for popups- adding onto them without changing their core behaviour.\n\n•Subliminals add a transparent gif over affected popups, defaulting to a hypnotic spiral if there are none added in the current pack. (this may cause performance issues with lots of popups, try a low max to start)\n•Denial "censors" a popup by blurring it, simple as.'


class MonitorCheckbutton(Checkbutton):
    def __init__(self, master: Misc, monitor: Monitor) -> None:
        self.monitor = monitor
        self.var = BooleanVar(master, self.monitor.name not in config["disabledMonitors"])
        super().__init__(master, text=f"{self.monitor.name} ({self.monitor.width}x{self.monitor.height})", variable=self.var, command=self.update_monitors)

    def update_monitors(self) -> None:
        if self.var.get():
            config["disabledMonitors"].remove(self.monitor.name)
        else:
            config["disabledMonitors"].append(self.monitor.name)


class PopupTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]) -> None:
        super().__init__()

        intro_message = Message(self.viewPort, text=INTRO_TEXT, justify=CENTER, width=675)
        intro_message.pack(fill="both")
        message_group.append(intro_message)

        popup_frame_1 = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        popup_frame_1.pack(fill="x")

        delay_frame = Frame(popup_frame_1)
        delay_frame.pack(fill="x", side="left", padx=(3, 0), expand=1)
        Scale(delay_frame, label="Popup Timer Delay (ms)", from_=10, to=60000, orient="horizontal", variable=vars.delay).pack(fill="x", expand=1)
        Button(delay_frame, text="Manual delay...", command=lambda: assign(vars.delay, simpledialog.askinteger("Manual Delay", prompt="[10-60000]: "))).pack(
            fill="x", expand=1
        )

        image_chance_frame = Frame(popup_frame_1)
        image_chance_frame.pack(fill="x", side="left", padx=(0, 3))
        image_chance_scale = Scale(image_chance_frame, label="Popup Chance (%)", from_=0, to=100, orient="horizontal", variable=vars.image_chance)
        image_chance_scale.pack(fill="x")
        image_chance_manual = Button(
            image_chance_frame,
            text="Manual popup chance...",
            command=lambda: assign(vars.image_chance, simpledialog.askinteger("Manual Popup Chance", prompt="[0-100]: ")),
        )
        image_chance_manual.pack(fill="x")

        popup_frame_2 = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        popup_frame_2.pack(fill="x")

        web_frame = Frame(popup_frame_2)
        web_frame.pack(fill="y", side="left", padx=3, expand=1)
        Scale(web_frame, label="Website Freq (%)", from_=0, to=100, orient="horizontal", variable=vars.web_chance).pack(fill="x")
        Button(web_frame, text="Manual web...", command=lambda: assign(vars.web_chance, simpledialog.askinteger("Web Chance", prompt="[0-100]: "))).pack(
            fill="x"
        )

        prompt_frame = Frame(popup_frame_2)
        prompt_frame.pack(fill="y", side="left", padx=(3, 0), expand=1)
        Scale(prompt_frame, label="Prompt Freq (%)", from_=0, to=100, orient="horizontal", variable=vars.prompt_chance).pack(fill="x")
        Button(
            prompt_frame, text="Manual prompt...", command=lambda: assign(vars.prompt_chance, simpledialog.askinteger("Manual Prompt", prompt="[0-100]: "))
        ).pack(fill="x")

        prompt_mistakes_frame = Frame(popup_frame_2)
        prompt_mistakes_frame.pack(fill="y", side="left", padx=(0, 3), expand=1)
        Scale(prompt_mistakes_frame, label="Prompt Mistakes", from_=0, to=150, orient="horizontal", variable=vars.prompt_max_mistakes).pack(fill="x")
        prompt_mistakes_manual = Button(
            prompt_mistakes_frame,
            text="Manual mistakes...",
            command=lambda: assign(vars.prompt_max_mistakes, simpledialog.askinteger("Max Mistakes", prompt="Max mistakes allowed in prompt text\n[0-150]: ")),
            cursor="question_arrow",
        )
        prompt_mistakes_manual.pack(fill="x")
        CreateToolTip(
            prompt_mistakes_manual,
            "The number of allowed mistakes when filling out a prompt.\n\nGood for when you can't think straight, or typing with one hand...",
        )

        ttk.Separator(popup_frame_2, orient="vertical").pack(fill="y", side="left")

        Scale(popup_frame_2, label="Popup Opacity (%)", from_=5, to=100, orient="horizontal", variable=vars.opacity).pack(
            fill="both", side="left", padx=3, expand=1
        )

        timeout_frame = Frame(popup_frame_2)
        timeout_frame.pack(fill="y", side="left", padx=3, expand=1)
        timeout_scale = Scale(timeout_frame, label="Time (sec)", from_=1, to=120, orient="horizontal", variable=vars.timeout)
        timeout_scale.pack(fill="x")
        Checkbutton(
            timeout_frame,
            text="Popup Timeout",
            variable=vars.timeout_enabled,
            command=lambda: set_widget_states(vars.timeout_enabled.get(), timeout_group),
        ).pack(fill="x")

        timeout_group = [timeout_scale]
        set_widget_states(vars.timeout_enabled.get(), timeout_group)

        popup_frame_3 = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        popup_frame_3.pack(fill="x")

        Checkbutton(popup_frame_3, text="Popup close opens web page", variable=vars.web_on_popup_close).pack(fill="x", side="left", expand=1)

        buttonless_toggle = Checkbutton(popup_frame_3, text="Buttonless Closing Popups", variable=vars.buttonless, cursor="question_arrow")
        buttonless_toggle.pack(fill="x", side="left", expand=1)
        CreateToolTip(
            buttonless_toggle,
            'Disables the "close button" on popups and allows you to click anywhere on the popup to close it.\n\n'
            "IMPORTANT: The panic keyboard hotkey will only work in this mode if you use it while *holding down* the mouse button over a popup!",
        )

        single_mode_toggle = Checkbutton(popup_frame_3, text="Single Roll Per Popup", variable=vars.single_mode, cursor="question_arrow")
        single_mode_toggle.pack(fill="x", side="left", expand=1)
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
        Checkbutton(
            subliminal_frame,
            text="Subliminal Overlays",
            variable=vars.popup_subliminals,
            command=lambda: set_widget_states(vars.popup_subliminals.get(), subliminals_group),
        ).pack(fill="x")

        subliminal_chance_frame = Frame(subliminal_frame)
        subliminal_chance_frame.pack(fill="x", side="left", padx=3)
        subliminal_chance_scale = Scale(
            subliminal_chance_frame, label="Sublim. Chance (%)", from_=1, to=100, orient="horizontal", variable=vars.subliminal_chance
        )
        subliminal_chance_scale.pack(fill="x")
        subliminal_chance_manual = Button(
            subliminal_chance_frame,
            text="Manual Sub Chance...",
            command=lambda: assign(vars.subliminal_chance, simpledialog.askinteger("Manual Subliminal Chance", prompt="[1-100]: ")),
        )
        subliminal_chance_manual.pack(fill="x")

        subliminal_alpha_frame = Frame(subliminal_frame)
        subliminal_alpha_frame.pack(fill="x", side="left", padx=3)
        subliminal_alpha_scale = Scale(subliminal_alpha_frame, label="Sublim. Alpha (%)", from_=1, to=99, orient="horizontal", variable=vars.subliminal_opacity)
        subliminal_alpha_scale.pack(fill="x")
        subliminal_alpha_manual = Button(
            subliminal_alpha_frame,
            text="Manual Sub Alpha...",
            command=lambda: assign(vars.subliminal_opacity, simpledialog.askinteger("Manual Subliminal Chance", prompt="[1-99]: ")),
        )
        subliminal_alpha_manual.pack(fill="x")

        max_subliminal_frame = Frame(subliminal_frame)
        max_subliminal_frame.pack(fill="x", side="left", padx=3)
        max_subliminal_scale = Scale(max_subliminal_frame, label="Max Subliminals", from_=1, to=200, orient="horizontal", variable=vars.max_subliminals)
        max_subliminal_scale.pack(fill="x")
        max_subliminal_manual = Button(
            max_subliminal_frame,
            text="Manual Max Sub...",
            command=lambda: assign(vars.max_subliminals, simpledialog.askinteger("Manual Max Subliminals", prompt="[1-200]: ")),
        )
        max_subliminal_manual.pack(fill="x")

        subliminals_group = [
            subliminal_chance_scale,
            subliminal_chance_manual,
            subliminal_alpha_scale,
            subliminal_alpha_manual,
            max_subliminal_scale,
            max_subliminal_manual,
        ]
        set_widget_states(vars.popup_subliminals.get(), subliminals_group)

        denial_frame = Frame(overlay_frame)
        denial_frame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        Checkbutton(
            denial_frame, text="Denial Overlays", variable=vars.denial_mode, command=lambda: set_widget_states(vars.denial_mode.get(), denial_group)
        ).pack(fill="x")
        denial_chance_slider = Scale(denial_frame, label="Denial Chance", orient="horizontal", variable=vars.denial_chance)
        denial_chance_slider.pack(fill="x", padx=1, expand=1)
        denial_chance_manual = Button(
            denial_frame,
            text="Manual Denial Chance...",
            command=lambda: assign(vars.denial_chance, simpledialog.askinteger("Manual Denial Chance", prompt="[1-100]: ")),
        )
        denial_chance_manual.pack(fill="x")

        denial_group = [denial_chance_slider, denial_chance_manual]
        set_widget_states(vars.denial_mode.get(), denial_group)

        # Monitors
        Label(self.viewPort, text="Enabled Monitors", font=title_font, relief=GROOVE).pack(pady=2)

        monitor_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        monitor_frame.pack(fill="x")
        for monitor in get_monitors():
            MonitorCheckbutton(monitor_frame, monitor).pack(fill="x", expand=1)

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
