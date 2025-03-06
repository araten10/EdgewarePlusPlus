import random
from tkinter import Label, Toplevel

import utils
from features.theme import get_theme
from pack import Pack
from screeninfo import get_monitors
from settings import Settings


class SubliminalMessagePopup(Toplevel):
    def __init__(self, settings: Settings, pack: Pack):
        self.subliminal_message = pack.random_subliminal_message()
        if not self.should_init():
            return
        super().__init__()

        self.theme = get_theme(settings)

        self.attributes("-topmost", True)
        utils.set_borderless(self)
        self.attributes("-alpha", settings.subliminal_message_popup_opacity)
        if utils.is_windows():
            self.wm_attributes("-transparentcolor", self.theme.transparent_bg)

        monitor = random.choice(get_monitors())

        font = (self.theme.font, min(monitor.width, monitor.height) // 10)
        label = Label(
            self,
            text=self.subliminal_message,
            font=font,
            wraplength=monitor.width / 1.5,
            fg=self.theme.fg,
            bg=(self.theme.transparent_bg if utils.is_windows() else self.theme.bg),
        )
        label.pack()

        x = monitor.x + (monitor.width - label.winfo_reqwidth()) // 2
        y = monitor.y + (monitor.height - label.winfo_reqheight()) // 2

        self.geometry(f"+{x}+{y}")
        self.after(settings.subliminal_message_popup_timeout, self.destroy)

    def should_init(self) -> bool:
        return self.subliminal_message
