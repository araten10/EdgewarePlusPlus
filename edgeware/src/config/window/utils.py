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

import json
import logging
import multiprocessing
import os
import shutil
import subprocess
import sys
import urllib
from pathlib import Path
from threading import Thread
from tkinter import BooleanVar, Button, Event, IntVar, Label, Listbox, StringVar, TclError, Toplevel, Widget, messagebox, simpledialog

import os_utils
import utils
from paths import Data, Process
from pynput import keyboard

from config import load_config
from config.items import CONFIG_DANGER, DangerLevel
from config.vars import Vars

# TODO: Don't load these here
config = load_config()
log_file = utils.init_logging("config")


class KeyListenerWindow(Toplevel):
    def __init__(self) -> None:
        super().__init__()
        self.resizable(False, False)
        self.title("Key Listener")
        self.wm_attributes("-topmost", 1)
        self.geometry("250x250")
        self.focus_force()
        Label(self, text="Press any key or exit").pack(expand=1, fill="both")


def request_legacy_panic_key(button: Button, var: StringVar) -> None:
    window = KeyListenerWindow()

    def assign_panic_key(event: Event) -> None:
        button.configure(text=f"Set Legacy\nPanic Key\n<{event.keysym}>")
        var.set(str(event.keysym))
        window.destroy()

    window.bind("<KeyPress>", assign_panic_key)


def request_global_panic_key(button: Button, var: StringVar) -> None:
    window = KeyListenerWindow()

    def close() -> None:
        window.destroy()
        process.terminate()

    def assign_panic_key(key: str) -> None:
        button.configure(text=f"Set Global\nPanic Key\n<{key}>")
        var.set(key)
        close()

    def run_listener(connection: multiprocessing.connection.Connection) -> None:
        with keyboard.Listener(on_release=lambda key: connection.send(str(key))) as listener:
            listener.join()

    def receive_panic_key() -> None:
        try:
            key = parent_connection.recv()
            window.after(0, lambda: assign_panic_key(key))
        except EOFError:
            pass  # The window was closed before a key was pressed

    parent_connection, child_connection = multiprocessing.Pipe()
    process = multiprocessing.Process(target=run_listener, args=(child_connection,))
    process.start()

    Thread(target=receive_panic_key).start()

    window.protocol("WM_DELETE_WINDOW", close)


# TODO: Review these functions
def all_children(widget: Widget) -> list[Widget]:
    return [widget] + [subchild for child in widget.winfo_children() for subchild in all_children(child)]


def confirm_overwrite(path: Path) -> bool:
    if not path.exists():
        return True

    type = "directory" if path.is_dir() else "file"
    delete = shutil.rmtree if path.is_dir() else os.remove

    confirm = messagebox.askyesno("Confirm", f'Path "{path}" already exists. This {type} will be deleted and overwritten. Is this okay?')
    if confirm:
        delete(path)

    return confirm


def get_live_version() -> str:
    url = "http://raw.githubusercontent.com/araten10/EdgewarePlusPlus/main/edgeware/assets/default_config.json"

    test = config["toggleInternet"]
    if test != 0:
        logging.info("GitHub connection is disabled, version will not be checked.")
        return "Version check disabled!"

    try:
        with open(urllib.request.urlretrieve(url)[0], "r") as live_config:
            return json.loads(live_config.read())["versionplusplus"]
    except Exception as e:
        logging.warning(f"Failed to fetch version on GitHub.\n\tReason: {e}")
        return "Could not check version."


def write_save(vars: Vars, exit_at_end: bool = False) -> None:
    if vars.safe_mode.get() and exit_at_end and not safe_check(vars):
        return

    logging.info("starting config save write...")
    temp = config.copy()
    temp["wallpaperDat"] = str(config["wallpaperDat"])

    os_utils.toggle_run_at_startup(vars.run_at_startup.get())

    for key, var in vars.entries.items():
        value = var.get()
        if key == "packPath":
            value = value if value != "default" else None
        temp[key] = (1 if value else 0) if type(value) is bool else value

    with open(Data.CONFIG, "w") as file:
        file.write(json.dumps(temp))
        logging.info(f"wrote config file: {json.dumps(temp)}")

    if not (len(sys.argv) > 1 and sys.argv[1] == "--first-launch-configure") and vars.run_on_save_quit.get() and exit_at_end:
        subprocess.Popen([sys.executable, Process.MAIN])

    if exit_at_end:
        logging.info("exiting config")
        sys.exit()
    else:
        messagebox.showinfo("Success!", "Settings saved successfully!")


def assign(obj: StringVar | IntVar | BooleanVar, var: str | int | bool) -> None:
    try:
        obj.set(var)
    except Exception as e:
        logging.warning(f"Failed to assign variable. Reason: {e}")


def safe_check(vars: Vars) -> bool:
    danger_levels = {
        DangerLevel.EXTREME: [],
        DangerLevel.MAJOR: [],
        DangerLevel.MEDIUM: [],
        DangerLevel.MINOR: [],
    }

    for key, var in vars.entries.items():
        danger = CONFIG_DANGER.get(key)
        if danger and danger.check(var.get()):
            danger_levels[danger.level].append(f"\n•{danger.warning or key}")

    danger_num = 0
    warnings = ""
    for level, dangers in danger_levels.items():
        danger_num += len(dangers)
        if dangers:
            warnings += f"\n\n{level.value.capitalize()}{''.join(dangers)}"

    return (
        messagebox.askyesno(
            "Dangerous Settings Detected!",
            f"{danger_num} potentially dangerous setting(s) detected! Do you want to save anyway? {warnings}",
            icon="warning",
        )
        if danger_num
        else True
    )


def clear_launches(confirmation: bool) -> None:
    try:
        if os.path.exists(Data.CORRUPTION_LAUNCHES):
            os.remove(Data.CORRUPTION_LAUNCHES)
            if confirmation:
                messagebox.showinfo(
                    "Cleaning Completed",
                    "The file that manages corruption launches has been deleted, and will be remade next time you start Edgeware with corruption on!",
                )
        else:
            if confirmation:
                messagebox.showinfo(
                    "No launches file!",
                    "There is no launches file to delete!\n\nThe launches file is used"
                    " for the launch transition mode, and is automatically deleted when you load a new pack. To generate a new"
                    " one, simply start Edgeware with the corruption setting on!",
                )
    except Exception as e:
        print(f"failed to clear launches. {e}")
        logging.warning(f"could not delete the corruption launches file. {e}")


def add_list(tk_list_obj: Listbox, key: str, title: str, text: str) -> None:
    name = simpledialog.askstring(title, text)
    if name != "" and name is not None:
        config[key] = f"{config[key]}>{name}"
        tk_list_obj.insert(2, name)


def remove_list(tk_list_obj: Listbox, key: str, title: str, text: str) -> None:
    index = int(tk_list_obj.curselection()[0])
    item_name = tk_list_obj.get(index)
    if index > 0:
        config[key] = config[key].replace(f">{item_name}", "")
        tk_list_obj.delete(tk_list_obj.curselection())
    else:
        messagebox.showwarning(title, text)


def remove_list_(tk_list_obj: Listbox, key: str, title: str, text: str) -> None:
    index = int(tk_list_obj.curselection()[0])
    item_name = tk_list_obj.get(index)
    print(config[key])
    print(item_name)
    print(len(config[key].split(">")))
    if len(config[key].split(">")) > 1:
        if index > 0:
            config[key] = config[key].replace(f">{item_name}", "")
        else:
            config[key] = config[key].replace(f"{item_name}>", "")
        tk_list_obj.delete(tk_list_obj.curselection())
    else:
        messagebox.showwarning(title, text)


def reset_list(tk_list_obj: Listbox, key: str, default: str) -> None:
    try:
        tk_list_obj.delete(0, 999)
    except Exception as e:
        print(e)
    config[key] = default
    for setting in config[key].split(">"):
        tk_list_obj.insert(1, setting)


def set_widget_states(state: bool, widgets: list[Widget], demo: bool = False) -> None:
    theme = config["themeType"].strip()

    # TODO: Use the same Theme objects as the main program
    if theme == "Original" or (config["themeNoConfig"] and not demo):
        set_widget_states_with_colors(state, widgets, "#f0f0f0", "gray35")
    else:
        if theme == "Dark":
            set_widget_states_with_colors(state, widgets, "#282c34", "gray65")
        if theme == "The One":
            set_widget_states_with_colors(state, widgets, "#282c34", "#37573d")
        if theme == "Ransom":
            set_widget_states_with_colors(state, widgets, "#841212", "#573737")
        if theme == "Goth":
            set_widget_states_with_colors(state, widgets, "#282c34", "#4b3757")
        if theme == "Bimbo":
            set_widget_states_with_colors(state, widgets, "#ffc5cd", "#bc7abf")


def set_widget_states_with_colors(state: bool, widgets: list[Widget], color_on: str, color_off: str) -> None:
    for widget in widgets:
        for child in [widget, *all_children(widget)]:
            # TODO: Better way to check if state and bg exist as options
            try:
                child.configure(state=("normal" if state else "disabled"))
            except TclError:
                pass

            try:
                child.configure(bg=(color_on if state else color_off))
            except TclError:
                pass


def refresh() -> None:
    subprocess.Popen([sys.executable, Process.CONFIG])
    sys.exit()
