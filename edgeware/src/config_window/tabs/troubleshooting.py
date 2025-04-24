from tkinter import (
    GROOVE,
    RAISED,
    Checkbutton,
    Frame,
    Label,
    messagebox,
    Button,

)
from tkinter.font import Font
import os
import logging

import os_utils
import utils
from config_window.vars import Vars
from config_window.utils import log_file
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip
from paths import Data
from pack import Pack

def get_log_number() -> int:
    return len(os.listdir(Data.LOGS)) if os.path.exists(Data.LOGS) else 0


def delete_logs(log_number_label: Label):
    try:
        if not messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete all logs? There are currently {get_log_number()}.", icon="warning"):
            return

        if not (os.path.exists(Data.LOGS) and os.listdir(Data.LOGS)):
            return

        logs = os.listdir(Data.LOGS)
        for file in logs:
            if os.path.splitext(file)[0] == os.path.splitext(log_file)[0]:
                continue

            if os.path.splitext(file)[1].lower() == ".txt":
                os.remove(Data.LOGS / file)
        log_number_label.configure(text=f"Total Logs: {get_log_number()}")
    except Exception as e:
        logging.warning(f"could not clear logs. this might be an issue with attempting to delete the log currently in use. if so, ignore this prompt. {e}")

class TroubleshootingTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, pack: Pack):
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
            state=("normal" if os_utils.is_linux() else "disabled"),
        )
        mpv_subprocess_toggle.pack(fill="x", side="top")
        CreateToolTip(
            mpv_subprocess_toggle,
            "By default, the video player of Edgeware++, mpv, is ran in a subprocess to fix a crash resulting from an X error when a popup"
            " embedding mpv is closed. But this may result in slightly longer load times for videos and animated GIFs.\n\n"
            "You can disable this setting to run mpv in the main process at the risk of an inconsistent experience and crashes.\n\n"
            "This setting is only available on Linux.",
        )

        # Directories
        Label(self.viewPort, text="Directories", font=title_font, relief=GROOVE).pack(pady=2)

        logs_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        logs_frame.pack(fill="x", pady=2)

        logs_col_1 = Frame(logs_frame)
        logs_col_1.pack(fill="both", side="left", expand=1)
        log_number_label = Label(logs_col_1, text=f"Total Logs: {get_log_number()}")
        log_number_label.pack(fill="both", expand=1)

        logs_col_2 = Frame(logs_frame)
        logs_col_2.pack(fill="both", side="left", expand=1)
        Button(logs_col_2, text="Open Logs Folder", command=lambda: os_utils.open_directory(Data.LOGS)).pack(fill="x", expand=1)
        delete_logs_button = Button(logs_col_2, text="Delete All Logs", command=lambda: delete_logs(log_number_label), cursor="question_arrow")
        delete_logs_button.pack(fill="x", expand=1)
        CreateToolTip(delete_logs_button, "This will delete every log (except the log currently being written).")

        moods_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        moods_frame.pack(fill="x", pady=2)

        moods_col_1 = Frame(moods_frame)
        moods_col_1.pack(fill="both", side="left", expand=1)
        id = pack.info.mood_file.with_suffix("").name
        using_unique = id == utils.compute_mood_id(pack.paths)
        Label(moods_col_1, text=("Using Unique ID?: " + ("✓" if using_unique else "✗")), fg=("green" if using_unique else "red")).pack(fill="both", expand=1)
        Label(moods_col_1, text=(f"Pack ID is: {id}")).pack(fill="both", expand=1)

        moods_col_2 = Frame(moods_frame)
        moods_col_2.pack(fill="both", side="left", expand=1)
        open_moods_button = Button(
            moods_col_2, height=2, text="Open Moods Folder", command=lambda: os_utils.open_directory(Data.MOODS), cursor="question_arrow"
        )
        open_moods_button.pack(fill="x", expand=1)
        CreateToolTip(
            open_moods_button,
            'If your currently loaded pack has a "info.json" file, it can be found under the pack name in this folder.\n\n'
            "If it does not have this file however, Edgeware++ will generate a Unique ID for it, so you can still save your mood settings "
            'without it. When using a Unique ID, your mood config file will be put into a subfolder called "unnamed".',
        )

        Button(self.viewPort, height=2, text="Open Pack Folder", command=lambda: os_utils.open_directory(pack.paths.root)).pack(fill="x", pady=2)
