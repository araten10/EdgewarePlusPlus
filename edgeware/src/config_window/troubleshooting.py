from tkinter import (
    GROOVE,
    RAISED,
    Checkbutton,
    Frame,
    Label,
)
from tkinter.font import Font

from config_window.vars import Vars
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip


class TroubleshootingTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font):
        super().__init__()

        Label(self.viewPort, text="Troubleshooting", font=title_font, relief=GROOVE).pack(pady=2)

        troubleshooting_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        troubleshooting_frame.pack(fill="x")

        troubleshooting_col_1 = Frame(troubleshooting_frame)
        troubleshooting_col_1.pack(fill="both", side="left", expand=1)
        hibernate_skip_toggle = Checkbutton(
            troubleshooting_col_1, text="Toggle Tray Hibernate Skip", variable=vars.toggle_hibernate_skip, cursor="question_arrow"
        )
        hibernate_skip_toggle.pack(fill="x", side="top")
        CreateToolTip(
            hibernate_skip_toggle,
            "Want to test out how hibernate mode works with your current settings, and hate waiting for the minimum time? Me too!\n\n"
            "This adds a feature in the tray that allows you to skip to the start of hibernate.",
        )

        troubleshooting_col_2 = Frame(troubleshooting_frame)
        troubleshooting_col_2.pack(fill="both", side="left", expand=1)
        github_connection_toggle = Checkbutton(
            troubleshooting_col_2, text="Disable Connection to Github", variable=vars.toggle_internet, cursor="question_arrow"
        )
        github_connection_toggle.pack(fill="x", side="top")
        CreateToolTip(
            github_connection_toggle,
            "In some cases, having a slow internet connection can cause the config window to delay opening for a long time.\n\n"
            "EdgeWare connects to Github just to check if there's a new update, but sometimes even this can take a while.\n\n"
            "If you have noticed this, try enabling this setting- it will disable all connections to Github on future launches.",
        )
        mood_settings_toggle = Checkbutton(troubleshooting_col_2, text="Turn Off Mood Settings", variable=vars.toggle_mood_set, cursor="question_arrow")
        mood_settings_toggle.pack(fill="x", side="top")
        CreateToolTip(
            mood_settings_toggle,
            "If your pack does not have a 'info.json' file with a valid pack name, it will generate a mood setting file based on a unique identifier.\n\n"
            "This unique identifier is created by taking a bunch of values from your pack and putting them all together, including the amount of images,"
            " audio, videos, and whether or not the pack has certain features.\n\n"
            "Because of this, if you are rapidly editing your pack and entering the config window, you could potentially create a bunch of mood settings"
            " files in //moods//unnamed, all pointing to what is essentially the same pack. This will reset your mood settings every time, too.\n\n"
            "In situations like this, I recommend creating a info file with a pack name, but if you're unsure how to do that or just don't want to"
            " deal with all this mood business, you can disable the mood saving feature here.",
        )
