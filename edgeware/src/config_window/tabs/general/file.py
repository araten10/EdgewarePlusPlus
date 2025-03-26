import logging
import os
import textwrap
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    Message,
    OptionMenu,
    StringVar,
    messagebox,
)
from tkinter.font import Font

import os_utils
import utils
from config_window.preset import apply_preset, list_presets, load_preset, load_preset_description, save_preset
from config_window.utils import (
    log_file,
    refresh,
    set_widget_states,
    write_save,
)
from config_window.vars import Vars
from pack import Pack
from paths import Data
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

PRESET_TEXT = "Please be careful before importing unknown config presets! Double check to make sure you're okay with the settings before launching Edgeware."


# TODO: Review these functions
def save_and_refresh(vars: Vars) -> None:
    write_save(vars)
    refresh()


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


class FileTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message], pack: Pack):
        super().__init__()

        # TODO: Save default preset if there are none?

        # Save/load
        Label(self.viewPort, text="Save", font=title_font, relief=GROOVE).pack(pady=2)

        Button(self.viewPort, text="Save Settings", command=lambda: write_save(vars)).pack(fill="x", pady=2)
        Button(self.viewPort, text="Save & Refresh", command=lambda: save_and_refresh(vars)).pack(fill="x", pady=2)

        # Presets
        Label(self.viewPort, text="Config Presets", font=title_font, relief=GROOVE).pack(pady=2)

        preset_message = Message(self.viewPort, text=PRESET_TEXT, justify=CENTER, width=675)
        preset_message.pack(fill="both")
        message_group.append(preset_message)

        preset_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        preset_frame.pack(fill="both", pady=2)

        preset_list = list_presets()
        self.preset_var = StringVar(self.viewPort, preset_list.pop(0))  # Without pop the first item appears twice in the list

        preset_selection_frame = Frame(preset_frame)
        preset_selection_frame.pack(side="left", fill="x", padx=6)
        self.preset_dropdown = OptionMenu(preset_selection_frame, self.preset_var, self.preset_var.get(), *preset_list, command=self.set_preset_description)
        self.preset_dropdown.pack(fill="x", expand=1)
        Button(preset_selection_frame, text="Load Preset", command=lambda: apply_preset(load_preset(self.preset_var.get()), vars)).pack(fill="both", expand=1)
        Label(preset_selection_frame).pack(fill="both", expand=1)
        Label(preset_selection_frame).pack(fill="both", expand=1)
        Button(preset_selection_frame, text="Save Preset", command=self.save_preset_and_update).pack(fill="both", expand=1)

        preset_description_frame = Frame(preset_frame, borderwidth=2, relief=GROOVE)
        preset_description_frame.pack(side="right", fill="both", expand=1)
        self.preset_name_label = Label(preset_description_frame, text="Default Description", font="Default 15")
        self.preset_name_label.pack(fill="y", pady=4)
        self.preset_description_wrap = textwrap.TextWrapper(width=100, max_lines=5)
        self.preset_description_label = Label(preset_description_frame, text=self.preset_description_wrap.fill(text="Default Text Here"), relief=GROOVE)
        self.preset_description_label.pack(fill="both", expand=1)
        self.set_preset_description(self.preset_var.get())

        pack_preset_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        pack_preset_frame.pack(fill="x", pady=2)

        pack_preset_col_1 = Frame(pack_preset_frame)
        pack_preset_col_1.pack(fill="both", side="left", expand=1)
        Label(pack_preset_col_1, text=f"Number of suggested config settings: {len(pack.config)}").pack(fill="both", side="top")
        pack_preset_danger_toggle = Checkbutton(pack_preset_col_1, text="Toggle on warning failsafes", variable=vars.preset_danger, cursor="question_arrow")
        pack_preset_danger_toggle.pack(fill="both", side="top")
        CreateToolTip(
            pack_preset_danger_toggle,
            'Toggles on the "Warn if "Dangerous" Settings Active" setting after loading the '
            "pack configuration file, regardless if it was toggled on or off in those settings.\n\nWhile downloading and loading "
            "something that could be potentially malicious is a fetish in itself, this provides some peace of mind for those of you "
            "who are more cautious with unknown files. More information on what these failsafe warnings entail is listed on the relevant "
            'setting tooltip in the "General" tab.',
        )

        pack_preset_col_2 = Frame(pack_preset_frame)
        pack_preset_col_2.pack(fill="both", side="left", expand=1)
        load_pack_preset_button = Button(
            pack_preset_col_2,
            text="Load Pack Configuration",
            cursor="question_arrow",
            command=lambda: apply_preset(pack.config, vars),
        )
        load_pack_preset_button.pack(fill="both", expand=1)
        CreateToolTip(
            load_pack_preset_button,
            "In Edgeware++, the functionality was added for pack creators to add a config file to their pack, "
            "allowing for quick loading of setting presets tailored to their intended pack experience. It is highly recommended you save your "
            "personal preset beforehand, as this will overwrite all your current settings.\n\nIt should also be noted that this can potentially "
            "enable settings that can change or delete files on your computer, if the pack creator set them up in the config! Be careful out there!",
        )

        pack_preset_group = [load_pack_preset_button]
        if len(pack.config) == 0:
            set_widget_states(False, pack_preset_group)

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

    def set_preset_description(self, name: str) -> None:
        self.preset_name_label.configure(text=f"{name} Description")
        self.preset_description_label.configure(text=self.preset_description_wrap.fill(text=load_preset_description(name)))

    def save_preset_and_update(self) -> None:
        name = save_preset()
        if not name:
            return

        # Clear menu
        menu = self.preset_dropdown["menu"]
        menu.delete(0, "end")

        # Repopulate menu with preset names, this has to be done individually
        for preset in list_presets():
            # Name must be a default argument to the command function, otherwise the dropdown breaks
            def select_preset(selection: str = preset) -> None:
                self.preset_var.set(selection)
                self.set_preset_description(selection)

            menu.add_command(label=preset, command=select_preset)

        self.preset_var.set(name)
        self.set_preset_description(name)
