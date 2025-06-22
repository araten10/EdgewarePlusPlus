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

from tkinter import BooleanVar, Misc

from config.vars import Vars
from config.window.utils import config
from config.window.widgets.layout import ConfigRow, ConfigScale, ConfigSection, ConfigToggle
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip
from screeninfo import Monitor, get_monitors

OVERLAY_TEXT = 'Overlays are more or less modifiers for popups- adding onto them without changing their core behaviour.\n\n•Hypno adds a transparent gif over affected popups, defaulting to a hypnotic spiral if there are none added in the current pack. (this may cause performance issues with lots of popups, try a low max to start)\n•Denial "censors" a popup by blurring it.'
CAPTION_TEXT = "Captions are small bits of randomly chosen text that adorn the top of each popup, and can be set by the pack creator. Many packs include captions, so don't be shy in trying them out!"
MONITORS_TEXT = "Here you can choose what monitors Edgeware++ will spawn popups on! By default every monitor that is detected is turned on, but if you want porn to amass on your second screen while you're focusing on something on your main monitor, this is a good way to do it~"
MOVEMENT_TEXT = 'Gives each popup a chance to move around the screen instead of staying still. The popup will have the "Buttonless" property (see "Misc Tweaks" above for more information), so it is easier to click.\n\nNOTE: Having many of these popups at once may impact performance. Try a lower movement chance or higher popup delay to start!'
MISC_TEXT = '•"Buttonless Closing Popups" removes the "close" button on every image and video popup, allowing you to click anywhere on the popup to close it. This makes closing popups much easier, but certain packs may have custom buttons that will no longer be seen.\n•"Multi Click Popups" is a setting that needs to be supported by the pack, and makes popups under certain moods take more clicks to close.\n•"Popup Opacity" affects the opacity/transparency of all popups.'
TIMEOUT_TEXT = "After a certain time, popups will fade out and delete themselves. This is a great setting to use with Lowkey Mode, or to keep a steady stream of porn flowing with little need for user interaction."


class MonitorToggle(ConfigToggle):
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
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        # Captions
        captions_section = ConfigSection(self.viewPort, "Captions", CAPTION_TEXT)
        captions_section.pack()

        captions_row = ConfigRow(captions_section)
        captions_row.pack()

        ConfigToggle(captions_row, "Enable Popup Captions", variable=vars.captions_in_popups).pack()

        # Overlays
        overlays_section = ConfigSection(self.viewPort, "Overlays", OVERLAY_TEXT)
        overlays_section.pack()

        hypno_row = ConfigRow(overlays_section)
        hypno_row.pack()

        ConfigScale(hypno_row, label="Hypno Chance (%)", from_=0, to=100, variable=vars.hypno_chance).pack()
        ConfigScale(hypno_row, label="Hypno Opacity (%)", from_=1, to=99, variable=vars.hypno_opacity).pack()

        denial_row = ConfigRow(overlays_section)
        denial_row.pack()

        ConfigScale(denial_row, label="Denial Chance (%)", from_=0, to=100, variable=vars.denial_chance).pack()

        # Opacity & Clickthrough
        opacity_section = ConfigSection(self.viewPort, "Opacity")
        opacity_section.pack()

        opacity_row = ConfigRow(opacity_section)
        opacity_row.pack()
        ConfigScale(opacity_row, label="Popup Opacity (%)", from_=5, to=100, variable=vars.opacity).pack()

        clickthrough_row = ConfigRow(opacity_section)
        clickthrough_row.pack()

        clickthrough_toggle = ConfigToggle(clickthrough_row, "Clickthrough Popups", variable=vars.clickthrough_enabled, cursor="question_arrow")
        clickthrough_toggle.pack()
        CreateToolTip(
            clickthrough_toggle,
            "Extra reminder to set opacity to less than 100% when using this! Timeout should also be set appropriately. You probably will have a very confusing experience otherwise!",
        )

        # Timeout
        timeout_section = ConfigSection(self.viewPort, "Popup Timeout", TIMEOUT_TEXT)
        timeout_section.pack()

        timeout_row = ConfigRow(timeout_section)
        timeout_row.pack()

        # Misc Tweaks
        misc_section = ConfigSection(self.viewPort, "Misc. Tweaks", MISC_TEXT)
        misc_section.pack()

        misc_row = ConfigRow(misc_section)
        misc_row.pack()

        buttonless_toggle = ConfigToggle(misc_row, "Buttonless Closing Popups", variable=vars.buttonless, cursor="question_arrow")
        buttonless_toggle.pack()
        CreateToolTip(
            buttonless_toggle,
            "IMPORTANT: The panic keyboard hotkey will only work in this mode if you use it while *holding down* the mouse button over a popup!",
        )

        ConfigToggle(misc_row, "Multi-Click popups", variable=vars.multi_click_popups).pack()

        ConfigToggle(timeout_row, "Popup Timeout", variable=vars.timeout_enabled).pack()

        timeout_row_2 = ConfigRow(timeout_section)
        timeout_row_2.pack()

        timeout_scale = ConfigScale(timeout_row_2, label="Time (sec)", from_=1, to=120, variable=vars.timeout, enabled=(vars.timeout_enabled, True))
        timeout_scale.pack()

        # Monitors
        monitors_section = ConfigSection(self.viewPort, "Monitors", MONITORS_TEXT)
        monitors_section.pack()

        for monitor in get_monitors():
            monitor_row = ConfigRow(monitors_section)
            monitor_row.pack()
            MonitorToggle(monitor_row, monitor).pack()

        # Movement
        movement_section = ConfigSection(self.viewPort, "Popup Movement", MOVEMENT_TEXT)
        movement_section.pack()

        movement_chance_row = ConfigRow(movement_section)
        movement_chance_row.pack()

        ConfigScale(movement_chance_row, label="Moving Popup Chance", from_=0, to=100, variable=vars.moving_chance).pack()
        ConfigScale(movement_chance_row, label="Max Movespeed", from_=1, to=15, variable=vars.moving_speed).pack()
