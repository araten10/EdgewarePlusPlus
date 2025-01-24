import json
import logging
import os
import shutil
import textwrap
import zipfile
from pathlib import Path
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
    filedialog,
    messagebox,
    simpledialog,
    ttk,
)
from tkinter.font import Font

from config_window.utils import (
    export_resource,
    import_resource,
    log_file,
    pack_preset,
    refresh,
    set_widget_states,
    write_save,
)
from config_window.vars import Vars
from pack import Pack
from paths import Data
from utils import utils
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

PACK_IMPORT_TEXT = 'If you\'re familiar with Edgeware, you may know that by default you can only have one pack imported under "resource". But you can also import multiple packs under "data/packs" using the "Import New Pack" button and choose which one you want to use with the dropdown menu on the left. This way you only need to import each pack once and you can conveniently switch between them. After choosing a pack from the dropdown menu, click the "Save & Refresh" button to update the config window to reflect your choice.\n\nPacks can still be imported and exported the old way using the "Import Default Pack" and "Export Default Pack" buttons, make sure to select "default" from the dropdown if you want to do this!'
PRESET_TEXT = "Please be careful before importing unknown config presets! Double check to make sure you're okay with the settings before launching Edgeware."


# TODO: Review these functions
def save_and_refresh(vars: Vars) -> None:
    write_save(vars)
    refresh()


def import_new_pack() -> None:
    try:
        pack_zip = filedialog.askopenfile("r", defaultextension=".zip")
        if not pack_zip:
            return

        with zipfile.ZipFile(pack_zip.name, "r") as zip:
            pack_name = Path(pack_zip.name).with_suffix("").name
            import_location = Data.PACKS / pack_name
            import_location.mkdir(parents=True, exist_ok=True)
            zip.extractall(import_location)

        messagebox.showinfo("Done", "New pack imported")
        refresh()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to import new pack.\n[{e}]")


def get_presets() -> list[str]:
    Data.PRESETS.mkdir(parents=True, exist_ok=True)
    return os.listdir(Data.PRESETS)


def get_preset_description(name: str) -> str:
    try:
        with open(Data.PRESETS / f"{name.lower()}.txt", "r") as file:
            text = ""
            for line in file.readlines():
                text += line
            return text
    except Exception:
        return "This preset has no description file."


def apply_preset(name: str):
    try:
        shutil.copyfile(Data.PRESETS / f"{name.lower()}.cfg", Data.CONFIG)
        refresh()
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load preset.\n\n{e}")


def save_preset(name: str) -> bool:
    try:
        if name is not None and name != "":
            shutil.copyfile(Data.CONFIG, Data.PRESETS / f"{name.lower()}.cfg")
            with open(Data.PRESETS / f"{name.lower()}.cfg", "rw") as file:
                file_json = json.loads(file.readline())
                file_json["drivePath"] = "C:/Users/"
                file.write(json.dumps(file_json))
            return True
        return False
    except Exception:
        return True


def get_pack_config_number(pack: Pack) -> int:
    if not pack.paths.config.exists():
        return 0

    try:
        with open(pack.paths.config) as f:
            config = json.loads(f.read())
            number = len(config)
            if "version" in config:
                number -= 1
            if "versionplusplus" in config:
                number -= 1
            return number
    except Exception as e:
        logging.warning(f"Could not load pack suggested settings. Reason: {e}")
        return 0


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


def open_directory(url):
    try:
        utils.open_directory(url)
    except Exception as e:
        logging.warning(f"failed to open explorer view\n\tReason: {e}")
        messagebox.showerror("Explorer Error", "Failed to open explorer view.")


class FileTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message], pack: Pack):
        super().__init__()

        # TODO: Save default preset if there are none?

        # Save/load
        Label(self.viewPort, text="Save/Load", font=title_font, relief=GROOVE).pack(pady=2)

        pack_import_message = Message(self.viewPort, text=PACK_IMPORT_TEXT, justify=CENTER, width=675)
        message_group.append(pack_import_message)
        pack_import_message.pack(fill="both")

        Button(self.viewPort, text="Save Settings", command=lambda: write_save(vars)).pack(fill="x", pady=2)
        Button(self.viewPort, text="Save & Refresh", command=lambda: save_and_refresh(vars)).pack(fill="x", pady=2)

        import_export_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        import_export_frame.pack(fill="x", pady=2)

        pack_selection_frame = Frame(import_export_frame)
        pack_selection_frame.pack(fill="both", pady=2, expand=1)
        Data.PACKS.mkdir(parents=True, exist_ok=True)
        pack_list = ["default"] + os.listdir(Data.PACKS)
        pack_dropdown = OptionMenu(pack_selection_frame, vars.pack_path, *pack_list)
        pack_dropdown["menu"].insert_separator(1)
        pack_dropdown.pack(padx=2, fill="x", side="left")
        Button(pack_selection_frame, text="Import New Pack", command=import_new_pack).pack(padx=2, fill="x", side="left", expand=1)

        ttk.Separator(import_export_frame, orient="horizontal").pack(fill="x", pady=2)
        Button(import_export_frame, text="Import Default Pack", command=lambda: import_resource(self.viewPort)).pack(
            padx=2, pady=2, fill="x", side="left", expand=1
        )
        Button(import_export_frame, text="Export Default Pack", command=export_resource).pack(padx=2, pady=2, fill="x", side="left", expand=1)

        # Presets
        Label(self.viewPort, text="Config Presets", font=title_font, relief=GROOVE).pack(pady=2)

        # TODO: Move these functions
        def change_description_text(key: str):
            preset_name_label.configure(text=f"{key} Description")
            preset_description_label.configure(text=preset_description_wrap.fill(text=get_preset_description(key)))

        def update_helper_func(key: str):
            preset_var.set(key)
            change_description_text(key)

        def do_save() -> bool:
            name_ = simpledialog.askstring("Save Preset", "Preset name")
            existed = os.path.exists(Data.PRESETS / f"{name_.lower()}.cfg")
            if name_ is not None and name_ != "":
                write_save(vars)
                if existed:
                    if messagebox.askquestion("Overwrite", "A preset with this name already exists. Overwrite it?") == "no":
                        return False
            if save_preset(name_) and not existed:
                preset_list.insert(0, "Default")
                preset_list.append(name_.capitalize())
                preset_var.set("Default")
                preset_dropdown["menu"].delete(0, "end")
                for item in preset_list:
                    preset_dropdown["menu"].add_command(label=item, command=lambda x=item: update_helper_func(x))
                preset_var.set(preset_list[0])
            return True

        preset_message = Message(self.viewPort, text=PRESET_TEXT, justify=CENTER, width=675)
        preset_message.pack(fill="both")
        # TODO: Is this commented out on purpose?
        # message_group.append(preset_message)

        preset_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        preset_frame.pack(fill="both", pady=2)

        preset_list = [_.split(".")[0].capitalize() for _ in get_presets() if _.endswith(".cfg")]
        preset_var = StringVar(self.viewPort, preset_list.pop(0))

        preset_selection_frame = Frame(preset_frame)
        preset_selection_frame.pack(side="left", fill="x", padx=6)
        preset_dropdown = OptionMenu(preset_selection_frame, preset_var, preset_var.get(), *preset_list, command=lambda key: change_description_text(key))
        preset_dropdown.pack(fill="x", expand=1)
        Button(preset_selection_frame, text="Load Preset", command=lambda: apply_preset(preset_var.get())).pack(fill="both", expand=1)
        Label(preset_selection_frame).pack(fill="both", expand=1)
        Label(preset_selection_frame).pack(fill="both", expand=1)
        Button(preset_selection_frame, text="Save Preset", command=do_save).pack(fill="both", expand=1)

        preset_description_frame = Frame(preset_frame, borderwidth=2, relief=GROOVE)
        preset_description_frame.pack(side="right", fill="both", expand=1)
        preset_name_label = Label(preset_description_frame, text="Default Description", font="Default 15")
        preset_name_label.pack(fill="y", pady=4)
        preset_description_wrap = textwrap.TextWrapper(width=100, max_lines=5)
        preset_description_label = Label(preset_description_frame, text=preset_description_wrap.fill(text="Default Text Here"), relief=GROOVE)
        preset_description_label.pack(fill="both", expand=1)
        change_description_text("Default")

        pack_preset_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        pack_preset_frame.pack(fill="x", pady=2)

        pack_preset_col_1 = Frame(pack_preset_frame)
        pack_preset_col_1.pack(fill="both", side="left", expand=1)
        pack_config_number = get_pack_config_number(pack)
        Label(pack_preset_col_1, text=f"Number of suggested config settings: {pack_config_number}").pack(fill="both", side="top")
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
            command=lambda: pack_preset(pack, vars, "full", vars.preset_danger.get()),
        )
        load_pack_preset_button.pack(fill="both", expand=1)
        CreateToolTip(
            load_pack_preset_button,
            "In EdgeWare++, the functionality was added for pack creators to add a config file to their pack, "
            "allowing for quick loading of setting presets tailored to their intended pack experience. It is highly recommended you save your "
            "personal preset beforehand, as this will overwrite all your current settings.\n\nIt should also be noted that this can potentially "
            "enable settings that can change or delete files on your computer, if the pack creator set them up in the config! Be careful out there!",
        )

        pack_preset_group = [load_pack_preset_button]
        if pack_config_number == 0:
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
        Button(logs_col_2, text="Open Logs Folder", command=lambda: open_directory(Data.LOGS)).pack(fill="x", expand=1)
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
        open_moods_button = Button(moods_col_2, height=2, text="Open Moods Folder", command=lambda: open_directory(Data.MOODS), cursor="question_arrow")
        open_moods_button.pack(fill="x", expand=1)
        CreateToolTip(
            open_moods_button,
            'If your currently loaded pack has a "info.json" file, it can be found under the pack name in this folder.\n\n'
            "If it does not have this file however, EdgeWare++ will generate a Unique ID for it, so you can still save your mood settings "
            'without it. When using a Unique ID, your mood config file will be put into a subfolder called "unnamed".',
        )

        Button(self.viewPort, height=2, text="Open Pack Folder", command=lambda: open_directory(pack.paths.root)).pack(fill="x", pady=2)
