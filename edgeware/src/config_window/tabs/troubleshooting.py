from tkinter import (
    GROOVE,
    RAISED,
    Checkbutton,
    Frame,
    Label,
)
from tkinter.font import Font

import os_utils
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
        mood_settings_toggle = Checkbutton(troubleshooting_col_1, text="Turn Off Mood Settings", variable=vars.toggle_mood_set, cursor="question_arrow")
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

        troubleshooting_col_2 = Frame(troubleshooting_frame)
        troubleshooting_col_2.pack(fill="both", side="left", expand=1)
        github_connection_toggle = Checkbutton(
            troubleshooting_col_2, text="Disable Connection to GitHub", variable=vars.toggle_internet, cursor="question_arrow"
        )
        github_connection_toggle.pack(fill="x", side="top")
        CreateToolTip(
            github_connection_toggle,
            "In some cases, having a slow internet connection can cause the config window to delay opening for a long time.\n\n"
            "Edgeware connects to GitHub just to check if there's a new update, but sometimes even this can take a while.\n\n"
            "If you have noticed this, try enabling this setting- it will disable all connections to GitHub on future launches.",
        )

        mpv_subprocess_toggle = Checkbutton(
            troubleshooting_col_2,
            text="Run mpv in a Subprocess (Linux Only)",
            variable=vars.mpv_subprocess,
            cursor="question_arrow",
            state=("active" if os_utils.is_linux() else "disabled"),
        )
        mpv_subprocess_toggle.pack(fill="x", side="top")
        CreateToolTip(
            mpv_subprocess_toggle,
            "By default, the video player of Edgeware++, mpv, is ran in a subprocess to fix a crash resulting from an X error when a popup"
            " embedding mpv is closed. But this may result in slightly longer load times for videos and animated GIFs.\n\n"
            "You can disable this setting to run mpv in the main process at the risk of an inconsistent experience and crashes.\n\n"
            "This setting is only available on Linux.",
        )
