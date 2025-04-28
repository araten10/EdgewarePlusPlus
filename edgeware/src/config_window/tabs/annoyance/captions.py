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
    CENTER,
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    Message,
    Scale,
    simpledialog,
)
from tkinter.font import Font

from config_window.utils import (
    assign,
)
from config_window.vars import Vars
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

INTRO_TEXT = "Captions are small bits of randomly chosen text that adorn the top of each popup, and can be set by the pack creator. Many packs include captions, so don't be shy in trying them out!"
CAPTION_TEXT = "These settings below will only work for compatible packs, but use captions to add new features. The first checks the caption's mood with the filename of the popup image, and links the caption if they match. The second allows for captions of a certain mood to make the popup require multiple clicks to close. More detailed info on both these settings can be found in the hover tooltip."
SUBLIMINAL_TEXT = 'Subliminal message popups briefly flash a caption on screen in big, bold text before disappearing.\n\nThis is largely meant to be for short, minimal captions such as "OBEY", "DROOL", and other vaguely fetishy things. "Use Subliminal specific mood" allows for this without interfering with other captions, as it uses the special mood "subliminals" which don\'t appear in the regular caption pool. However, these subliminals are set by the pack creator, so if none are set the default will be used instead.'
NOTIFICATION_TEXT = 'These are a special type of caption-centric popup that uses your operating system\'s notification feature. For examples, this system is usually used for things like alerts ("You may now safely remove your USB device") or web browser notifications if you have those enabled. ("User XYZ has liked your youtube comment")'


class CaptionsTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]) -> None:
        super().__init__()

        # Captions
        Label(self.viewPort, text="Captions", font=title_font, relief=GROOVE).pack(pady=2)

        intro_message = Message(self.viewPort, text=INTRO_TEXT, justify=CENTER, width=675)
        intro_message.pack(fill="both")
        message_group.append(intro_message)

        enable_captions_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        enable_captions_frame.pack(fill="x", pady=(0, 5))
        Checkbutton(enable_captions_frame, text="Enable Popup Captions", variable=vars.captions_in_popups).pack(fill="both", expand=1)

        caption_message = Message(self.viewPort, text=CAPTION_TEXT, justify=CENTER, width=675)
        caption_message.pack(fill="both")
        message_group.append(caption_message)

        caption_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        caption_frame.pack(fill="x")
        filename_mood_toggle = Checkbutton(caption_frame, text="Use filename for caption moods", variable=vars.filename_caption_moods, cursor="question_arrow")
        filename_mood_toggle.pack(fill="y", side="left", expand=1)
        CreateToolTip(
            filename_mood_toggle,
            "When enabled, captions will try and match the filename of the image they attach to.\n\n"
            'This is done using the start of the filename. For example, a mood named "goon" would match captions of that mood to popups '
            'of images named things like "goon300242", "goon-love", "goon_ytur8843", etc.\n\n'
            "This is how Edgeware processed captions before moods were implemented fully in Edgeware++. The reason you'd turn this off, however, "
            "is that if the mood doesn't match the filename, it won't display at all.\n\n For example, if you had a mood named \"succubus\", but "
            'no filtered files started with "succubus", the captions of that mood would never show up. Thus it is recommended to only turn this on if '
            "the pack supports it.",
        )
        multi_click_toggle = Checkbutton(caption_frame, text="Multi-Click popups", variable=vars.multi_click_popups, cursor="question_arrow")
        multi_click_toggle.pack(fill="y", side="left", expand=1)
        CreateToolTip(
            multi_click_toggle,
            "If the pack creator uses advanced caption settings, this will enable the feature for certain popups to take multiple clicks "
            "to close. This feature must be set-up beforehand and won't do anything if not supported.",
        )

        # Sublimnal messages
        Label(self.viewPort, text="Subliminal Message Popups", font=title_font, relief=GROOVE).pack(pady=2)

        subliminal_message = Message(self.viewPort, text=SUBLIMINAL_TEXT, justify=CENTER, width=675)
        subliminal_message.pack(fill="both")
        message_group.append(subliminal_message)

        # NOTE: subliminal message popups used to be called "capPop" back when all of this was compressed to a single page and there was little space.
        # I am not messing about with the variables on this in case users want to import their old settings.
        # (however, the name was awful and needed to be changed so people could actually understand it)
        subliminal_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        subliminal_frame.pack(fill="x")

        subliminal_chance_rame = Frame(subliminal_frame)
        subliminal_chance_rame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        Scale(
            subliminal_chance_rame, label="Subliminal Message Chance", from_=0, to=100, orient="horizontal", variable=vars.subliminal_message_popup_chance
        ).pack(fill="x", padx=1, expand=1)
        Button(
            subliminal_chance_rame,
            text="Manual Subliminal...",
            command=lambda: assign(vars.subliminal_message_popup_chance, simpledialog.askinteger("Manual Caption Popup Chance (%)", prompt="[0-100]: ")),
        ).pack(fill="x")

        subliminal_opacity_frame = Frame(subliminal_frame)
        subliminal_opacity_frame.pack(fill="x", side="left", expand=1)
        Scale(
            subliminal_opacity_frame, label="Subliminal Message Opacity", from_=1, to=100, orient="horizontal", variable=vars.subliminal_message_popup_opacity
        ).pack(fill="x", padx=1, expand=1)
        Button(
            subliminal_opacity_frame,
            text="Manual Opacity...",
            command=lambda: assign(vars.subliminal_message_popup_opacity, simpledialog.askinteger("Manual Caption Popup Opacity (%)", prompt="[1-100]: ")),
        ).pack(fill="x")

        subliminal_timer_frame = Frame(subliminal_frame)
        subliminal_timer_frame.pack(fill="x", side="left", padx=(3, 0), expand=1)
        Scale(
            subliminal_timer_frame, label="Subliminal Message Timer (ms)", from_=1, to=1000, orient="horizontal", variable=vars.subliminal_message_popup_timeout
        ).pack(fill="x", padx=1, expand=1)
        Button(
            subliminal_timer_frame,
            text="Manual Timer...",
            command=lambda: assign(vars.subliminal_message_popup_timeout, simpledialog.askinteger("Manual Subliminal Message Timer (ms)", prompt="[1-1000]: ")),
        ).pack(fill="x")

        # Notifications
        Label(self.viewPort, text="Notifications", font=title_font, relief=GROOVE).pack(pady=2)

        notification_message = Message(self.viewPort, text=NOTIFICATION_TEXT, justify=CENTER, width=675)
        notification_message.pack(fill="both")
        message_group.append(notification_message)

        notification_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        notification_frame.pack(fill="x")

        notification_chance_frame = Frame(notification_frame)
        notification_chance_frame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        Scale(notification_chance_frame, label="Notification Chance", from_=0, to=100, orient="horizontal", variable=vars.notification_chance).pack(
            fill="x", padx=1, expand=1
        )
        Button(
            notification_chance_frame,
            text="Manual Notification...",
            command=lambda: assign(vars.notification_chance, simpledialog.askinteger("Manual Notification Chance (%)", prompt="[0-100]: ")),
        ).pack(fill="x")

        notification_image_chance_frame = Frame(notification_frame)
        notification_image_chance_frame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        Scale(
            notification_image_chance_frame, label="Notification Image Chance", from_=0, to=100, orient="horizontal", variable=vars.notification_image_chance
        ).pack(fill="x", padx=1, expand=1)
        Button(
            notification_image_chance_frame,
            text="Manual Notification Image...",
            command=lambda: assign(vars.notification_image_chance, simpledialog.askinteger("Manual Notification Image Chance (%)", prompt="[0-100]: ")),
        ).pack(fill="x")
