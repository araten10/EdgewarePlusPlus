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

from tkinter import CENTER, Message
from tkinter.font import Font

from config.vars import Vars
from config.window.widgets.layout import ConfigRow, ConfigScale, ConfigSection, ConfigToggle
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip

FREQUENCY_TEXT = 'This tab dictates the frequency of every popup type you will see during runtime, which in turn affects nearly every other tab in the config window! Each popup here will have a short description to help you decide how much you want to see of it. To check and see what types of popups your currently loaded pack supports, you can head on over to "Pack Info" (Underneath "General") and see how much media there is of each type.\n\nThe "Popup Timer Delay" setting affects the duration between each popup spawning, no matter the type. Once the timer has elapsed, a new popup will spawn, and then the type is randomly chosen from the chances set. It\'s recommended that you don\'t set this number too low to start- try 8000ms-10000ms (8-10 seconds) and adjust it from there based on how you feel!'
SINGLE_TEXT = 'When a new popup is spawned, it uses the percentage chance of each type to determine which popup to choose. However, by default the popup does not check to see if a previous "type roll" has succeeded during the spawn process before starting the next one. Because of this, it\'s possible for multiple popups to spawn at once if the chance for multiple types is high enough.\n\n"Single Roll Per Popup" (sometimes referred to as "Single Mode") stops the "rolling process" once one type is picked. This allows for a much more consistent experience, with a maximum of only one popup spawning at a time (things like "Hibernate Mode" are an exception). Of course, sometimes having a bunch of popups spam your screen is also fun at times- this is a fake virus program after all!'
IMAGE_TEXT = "Image popups are the most common type of popup. Every single pack will have these, and most of your time using Edgeware++ will be spent staring at these lovely things~\n\nThe reason a percentage slider exists for this is to create a more inconsistent experience. If no probability slider is set to 100% on this tab, there's a chance that nothing will spawn. If you want Edgeware++ to surprise you, consider turning this down to 60% or so!"
AUDIO_TEXT = "Audio popups have no visuals attached, focusing only on sound. Because of this, there's no way to disable them once they stop (besides panic), but maybe that's something you want...~\n\nGenerally, you probably want a low maximum count on this, as well as a low frequency. Packs sometimes use long files for audio (hypno, binural, ASMR, etc), so you might have to set the maximum to \"1\" in this case, assuming the pack doesn't have suggested settings to do it for you."
VIDEO_TEXT = 'Video popups are functionally exactly the same as image popups, just animated and with sound support. Edgeware++ uses MPV to play videos, and if you run into any trouble displaying these you may want to check out the "Troubleshooting" tab for a few video debugging options.'
WEBSITE_TEXT = "Opens up a website in your default browser whenever a roll is passed. Please be aware that you could potentially be linked to a website with malicious intent or aggressive popups/ads.\n\nIts recommended to leave this chance relatively low so having new websites open is more of a nice suprise instead of an annoyance."
PROMPT_TEXT = 'Prompt popups require you to repeat a prompt via a text box before they can be closed. The intent with this is to help drill mantras into your brain or generally make you more horny by having to repeat something degrading.\n\n"Prompt Mistakes" is the number of mistakes you can make in your reply and still have it be accepted. This is perfect for people who type with one hand, or have had porn degrade their IQ for the last few hours, or both...'
NOTIFICATION_TEXT = 'These are a special type of caption-centric popup that uses your operating system\'s notification feature. For examples, this system is usually used for things like alerts ("You may now safely remove your USB device") or web browser notifications if you have those enabled. ("User XYZ has liked your youtube comment")'
SUBLIMINAL_TEXT = 'Subliminal message popups briefly flash a caption on screen in big, bold text before disappearing.\n\nThis is largely meant to be for short, minimal captions such as "OBEY", "DROOL", and other vaguely fetishy things. To help with this, they can tap into a specific "subliminal mood" if the pack creator sets it up. Otherwise default captions will be used instead. (See "Popup Tweaks" for more info on captions)'


class PopupTypesTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]) -> None:
        super().__init__()

        # Popup Frequency
        popup_freq_section = ConfigSection(self.viewPort, "General Popup Frequency", FREQUENCY_TEXT)
        popup_freq_section.pack()

        popup_freq_row = ConfigRow(popup_freq_section)
        popup_freq_row.pack()

        ConfigScale(popup_freq_row, label="Popup Timer Delay (ms)", from_=10, to=60000, variable=vars.delay).pack()

        single_message = Message(popup_freq_section, text=SINGLE_TEXT, justify=CENTER, width=675)
        single_message.pack(fill="both")
        # for when hiding help gets refactored?
        # message_group.append(single_message)

        single_mode = ConfigToggle(popup_freq_section, "Single Roll Per Popup", variable=vars.single_mode, cursor="question_arrow")
        single_mode.pack()

        CreateToolTip(
            single_mode,
            "In this mode, the chance of a popup appearing is used as a weight to choose a single popup type to spawn (the popup type with the highest percentage will be picked the most, etc).",
        )

        # Image
        popup_image_section = ConfigSection(self.viewPort, "Image Popups", IMAGE_TEXT)
        popup_image_section.pack()

        ConfigScale(popup_image_section, label="Image Popup Chance (%)", from_=0, to=100, variable=vars.image_chance).pack()

        # Audio
        audio_section = ConfigSection(self.viewPort, "Audio Popups", AUDIO_TEXT)
        audio_section.pack()

        audio_row = ConfigRow(audio_section)
        audio_row.pack()

        ConfigScale(audio_row, label="Audio Popup Chance (%)", from_=0, to=100, variable=vars.audio_chance).pack()
        ConfigScale(audio_row, label="Max Audio Popups", from_=1, to=50, variable=vars.max_audio).pack()
        ConfigScale(audio_row, label="Audio Volume (%)", from_=1, to=100, variable=vars.audio_volume).pack()

        # Video
        video_section = ConfigSection(self.viewPort, "Video Popups", VIDEO_TEXT)
        video_section.pack()

        video_row = ConfigRow(video_section)
        video_row.pack()

        ConfigScale(video_row, label="Video Popup Chance (%)", from_=0, to=100, variable=vars.video_chance).pack()
        ConfigScale(video_row, label="Max Video Popups", from_=1, to=50, variable=vars.max_video).pack()
        ConfigScale(video_row, label="Video Volume (%)", from_=0, to=100, variable=vars.video_volume).pack()

        # Website
        web_section = ConfigSection(self.viewPort, "Website Popups", WEBSITE_TEXT)
        web_section.pack()
        ConfigScale(web_section, label="Website Freq (%)", from_=0, to=100, variable=vars.web_chance).pack()

        # Prompts
        prompt_section = ConfigSection(self.viewPort, "Prompt Popups", PROMPT_TEXT)
        prompt_section.pack()

        prompt_row = ConfigRow(prompt_section)
        prompt_row.pack()

        ConfigScale(prompt_row, label="Prompt Chance (%)", from_=0, to=100, variable=vars.prompt_chance).pack()
        ConfigScale(prompt_row, label="Prompt Mistakes", from_=0, to=150, variable=vars.prompt_max_mistakes).pack()

        # Subliminal
        subliminal_section = ConfigSection(self.viewPort, "Subliminal Popups", SUBLIMINAL_TEXT)
        subliminal_section.pack()

        subliminal_row = ConfigRow(subliminal_section)
        subliminal_row.pack()

        ConfigScale(subliminal_row, label="Subliminal Popup Chance (%)", from_=0, to=100, variable=vars.subliminal_chance).pack()
        ConfigScale(subliminal_row, label="Subliminal Popup Length (ms)", from_=1, to=1000, variable=vars.subliminal_timeout).pack()
        ConfigScale(subliminal_row, label="Subliminal Popup Opacity (%)", from_=1, to=100, variable=vars.subliminal_opacity).pack()

        # Notification
        notification_section = ConfigSection(self.viewPort, "Notification Popups", NOTIFICATION_TEXT)
        notification_section.pack()

        notification_row = ConfigRow(notification_section)
        notification_row.pack()

        ConfigScale(notification_row, label="Notification Chance (%)", from_=0, to=100, variable=vars.notification_chance).pack()
        ConfigScale(notification_row, label="Notification Image Chance (%)", from_=0, to=100, variable=vars.notification_image_chance).pack()
