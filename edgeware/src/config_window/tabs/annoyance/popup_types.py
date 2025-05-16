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

from tkinter import Message
from tkinter.font import Font

from settings import Vars
from widgets.config_widgets import (
    ConfigRow,
    ConfigScale,
    ConfigSection,
)
from widgets.scroll_frame import ScrollFrame

INTRO_TEXT = 'Here is where you can change the most important settings of Edgeware: the frequency and behaviour of popups. The "Popup Timer Delay" is how long a popup takes to spawn, and the overall "Popup Chance" then rolls to see if the popup spawns. Keeping the chance at 100% allows for a consistent experience, while lowering it makes for a more random one.\n\nOnce ready to spawn, a popup can be many things: A regular image, a website link (opens in your default browser), a prompt you need to fill out, autoplaying audio or videos, or a subliminal message. All of these are rolled for corresponding to their respective frequency settings, which can be found in the "Audio/Video" tab, "Captions" tab, and this tab as well. There are also plenty of other settings there to configure popups to your liking~! '
NOTIFICATION_TEXT = 'These are a special type of caption-centric popup that uses your operating system\'s notification feature. For examples, this system is usually used for things like alerts ("You may now safely remove your USB device") or web browser notifications if you have those enabled. ("User XYZ has liked your youtube comment")'
SUBLIMINAL_TEXT = 'Subliminal message popups briefly flash a caption on screen in big, bold text before disappearing.\n\nThis is largely meant to be for short, minimal captions such as "OBEY", "DROOL", and other vaguely fetishy things. "Use Subliminal specific mood" allows for this without interfering with other captions, as it uses the special mood "subliminals" which don\'t appear in the regular caption pool. However, these subliminals are set by the pack creator, so if none are set the default will be used instead.'


class PopupTypesTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]) -> None:
        super().__init__()

        # Popup Frequency
        popup_freq_section = ConfigSection(self.viewPort, "General Popup Frequency")
        popup_freq_section.pack()

        popup_freq_row = ConfigRow(popup_freq_section)
        popup_freq_row.pack()

        ConfigScale(popup_freq_row, label="Popup Timer Delay (ms)", from_=10, to=60000, variable=vars.delay).pack()

        image_chance_scale = ConfigScale(popup_freq_row, label="Popup Chance (%)", from_=0, to=100, variable=vars.image_chance)
        image_chance_scale.pack()

        # Audio
        audio_section = ConfigSection(self.viewPort, "Audio Popups")
        audio_section.pack()

        audio_row = ConfigRow(audio_section)
        audio_row.pack()

        ConfigScale(audio_row, label="Audio Popup Chance (%)", from_=0, to=100, variable=vars.audio_chance).pack()
        ConfigScale(audio_row, label="Max Audio Popups", from_=1, to=50, variable=vars.max_audio).pack()
        ConfigScale(audio_row, label="Audio Volume (%)", from_=1, to=100, variable=vars.audio_volume).pack()

        # Video
        video_section = ConfigSection(self.viewPort, "Video Popups")
        video_section.pack()

        video_row = ConfigRow(video_section)
        video_row.pack()

        ConfigScale(video_row, label="Video Popup Chance (%)", from_=0, to=100, variable=vars.video_chance).pack()
        ConfigScale(video_row, label="Max Video Popups", from_=1, to=50, variable=vars.max_video).pack()
        ConfigScale(video_row, label="Video Volume (%)", from_=1, to=100, variable=vars.video_volume).pack()

        # Prompts
        prompt_section = ConfigSection(self.viewPort, "Prompt Popups")
        prompt_section.pack()

        prompt_row = ConfigRow(prompt_section)
        prompt_row.pack()

        ConfigScale(prompt_row, label="Prompt Chance (%)", from_=0, to=100, variable=vars.prompt_chance).pack()
        ConfigScale(prompt_row, label="Prompt Mistakes", from_=0, to=150, variable=vars.prompt_max_mistakes).pack()

        # Website
        web_section = ConfigSection(self.viewPort, "Website Popups")
        web_section.pack()
        ConfigScale(web_section, label="Website Freq (%)", from_=0, to=100, variable=vars.web_chance).pack()

        # Subliminal
        subliminal_section = ConfigSection(self.viewPort, "Subliminal Popups", SUBLIMINAL_TEXT)
        subliminal_section.pack()

        subliminal_row = ConfigRow(subliminal_section)
        subliminal_row.pack()

        ConfigScale(subliminal_row, label="Subliminal Popup Chance (%)", from_=0, to=100, variable=vars.subliminal_message_popup_chance).pack()
        ConfigScale(subliminal_row, label="Subliminal Popup Length (ms)", from_=1, to=1000, variable=vars.subliminal_message_popup_timeout).pack()
        ConfigScale(subliminal_row, label="Subliminal Popup Opacity (%)", from_=1, to=100, variable=vars.subliminal_message_popup_opacity).pack()

        # Notification
        notification_section = ConfigSection(self.viewPort, "Notification Popups", NOTIFICATION_TEXT)
        notification_section.pack()

        notification_row = ConfigRow(notification_section)
        notification_row.pack()

        ConfigScale(notification_row, label="Notification Chance (%)", from_=0, to=100, variable=vars.notification_chance).pack()
        ConfigScale(notification_row, label="Notification Image Chance (%)", from_=0, to=100, variable=vars.notification_image_chance).pack()
