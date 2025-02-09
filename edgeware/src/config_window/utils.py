import json
import logging
import os
import shutil
import subprocess
import sys
import urllib
import zipfile
from pathlib import Path
from tkinter import BooleanVar, Button, Frame, IntVar, Label, Listbox, StringVar, Tk, Toplevel, Widget, filedialog, messagebox, simpledialog

from config_window.vars import Vars
from pack import Pack
from paths import DEFAULT_PACK_PATH, Data, Process
from settings import load_config
from utils import utils

BUTTON_FACE = "SystemButtonFace" if utils.is_windows() else "gray90"

# TODO: Don't load these here
config = load_config()
log_file = utils.init_logging("config")


# TODO: Review these functions
def all_children(widget: Widget) -> list[Widget]:
    return [widget] + [subchild for child in widget.winfo_children() for subchild in all_children(child)]


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

    utils.toggle_run_at_startup(vars.run_at_startup.get())

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


def assign(obj: StringVar | IntVar | BooleanVar, var: str | int | bool):
    try:
        obj.set(var)
    except Exception as e:
        logging.warning(f"Failed to assign variable. Reason: {e}")


def safe_check(vars: Vars) -> bool:
    dangers = []
    logging.info("running through danger list...")
    if vars.replace_images.get():
        logging.info("extreme dangers found.")
        dangers.append("\n\nExtreme:")
        if vars.replace_images.get():
            dangers.append(
                '\n•Replace Images is enabled! THIS WILL DELETE FILES ON YOUR COMPUTER! Only enable this willingly and cautiously! Read the documentation in the "About" tab!'
            )
    if vars.run_at_startup.get() or vars.fill_drive.get():
        logging.info("major dangers found.")
        dangers.append("\n\nMajor:")
        if vars.run_at_startup.get():
            dangers.append("\n•Launch on Startup is enabled! This will run EdgeWare when you start your computer! (Note: Timer mode enables this setting!)")
        if vars.fill_drive.get():
            dangers.append(
                "\n•Fill Drive is enabled! Edgeware will place images all over your computer! Even if you want this, make sure the protected directories are right!"
            )
    if (
        vars.timer_mode.get()
        or vars.mitosis_mode.get()
        or vars.show_on_discord.get()
        or (vars.hibernate_mode.get() and (int(vars.hibernate_delay_min.get()) < 30 or int(vars.hibernate_delay_max.get()) < 30))
    ):
        logging.info("medium dangers found.")
        dangers.append("\n\nMedium:")
        if vars.timer_mode.get():
            dangers.append("\n•Timer mode is enabled! Panic cannot be used until a specific time! Make sure you know your Safeword!")
        if vars.mitosis_mode.get():
            dangers.append("\n•Mitosis mode is enabled! With high popup rates, this could create a chain reaction, causing lag!")
        if vars.hibernate_mode.get() and (int(vars.hibernate_delay_min.get()) < 30 or int(vars.hibernate_delay_max.get()) < 30):
            dangers.append("\n•You are running hibernate mode with a short cooldown! You might experience lag if a bunch of hibernate modes overlap!")
        if vars.show_on_discord.get():
            dangers.append("\n•Show on Discord is enabled! This could lead to potential embarassment if you're on your main account!")
    if vars.panic_disabled.get() or vars.run_on_save_quit.get():
        logging.info("minor dangers found.")
        dangers.append("\n\nMinor:")
        if vars.panic_disabled.get():
            dangers.append("\n•Panic Hotkey is disabled! If you want to easily close EdgeWare, read the tooltip in the Annoyance tab for other ways to panic!")
        if vars.run_on_save_quit.get():
            dangers.append("\n•EdgeWare will run on Save & Exit (AKA: when you hit Yes!)")
    dangers = " ".join(dangers)
    if len(dangers):
        logging.info("safe mode intercepted save! asking user...")
        if (
            messagebox.askyesno(
                "Dangerous Setting Detected!",
                f"There are {len(dangers)} potentially dangerous settings detected! Do you want to save these settings anyways? {dangers}",
                icon="warning",
            )
            is False
        ):
            logging.info("user cancelled save.")
            return False
    return True


def export_resource() -> bool:
    try:
        logging.info("starting zip export...")
        save_location = filedialog.asksaveasfile("w", defaultextension=".zip")
        with zipfile.ZipFile(save_location.name, "w", compression=zipfile.ZIP_DEFLATED) as zip:
            beyond_root = False
            for root, dirs, files in os.walk(DEFAULT_PACK_PATH):
                for file in files:
                    logging.info(f"write {file}")
                    if beyond_root:
                        zip.write(os.path.join(root, file), os.path.join(Path(root).name, file))
                    else:
                        zip.write(os.path.join(root, file), file)
                for dir in dirs:
                    logging.info(f"make dir {dir}")
                    zip.write(os.path.join(root, dir), dir)
                beyond_root = True
        return True
    except Exception as e:
        logging.fatal(f"failed to export zip\n\tReason: {e}")
        messagebox.showerror("Write Error", "Failed to export resource to zip file.")
        return False


def import_resource(parent: Tk) -> bool:
    try:
        open_location = filedialog.askopenfile("r", defaultextension=".zip")
        if open_location is None:
            return False
        if os.path.exists(DEFAULT_PACK_PATH):
            resp = confirm_box(
                parent,
                "Confirm",
                "Current resource folder will be deleted and overwritten. Corruption launches will be reset. Is this okay?"
                "\nNOTE: This might take a while when importing larger packs, please be patient!",
            )
            if not resp:
                logging.info("exited import resource overwrite")
                return False
            shutil.rmtree(DEFAULT_PACK_PATH)
            logging.info("removed old resource folder")
        with zipfile.ZipFile(open_location.name, "r") as zip:
            zip.extractall(DEFAULT_PACK_PATH)
            logging.info("extracted all from zip")
        messagebox.showinfo("Done", "Resource importing completed.")
        clear_launches(False)
        refresh()
        return True
    except Exception as e:
        messagebox.showerror("Read Error", f"Failed to import resources from file.\n[{e}]")
        return False


# applyPreset already exists, but there's a reason i'm not using it. I want the per-pack preset to not include every setting unless specified to do so, and
# I also want the settings to not automatically be saved in case the user does not like what the pack sets.
def pack_preset(pack: Pack, vars: Vars, preset_type: str, danger: bool):
    with open(pack.paths.config) as f:
        try:
            pack_config = json.loads(f.read())
            print(pack_config)
            if "version" in pack_config:
                del pack_config["version"]
            if "versionplusplus" in pack_config:
                del pack_config["versionplusplus"]
            if "packPath" in pack_config:
                del pack_config["packPath"]
            filter = []
            num = 0
            if preset_type == "full":
                filter = vars.entries.keys()
            if preset_type == "corruption":
                filter = ["corruptionMode", "corruptionTime", "corruptionFadeType"]
            for c in pack_config:
                if c in filter:
                    num += 1
                    print(f"{c} matches. Looking for list number...")
                    var = vars.entries[c]
                    if isinstance(var, IntVar):
                        var.set(int(pack_config[c]))
                    if isinstance(var, BooleanVar):
                        var.set(pack_config[c] == 1)
                    if isinstance(var, StringVar):
                        var.set(pack_config[c].strip())
            messagebox.showinfo(
                "Load Completed",
                f"Pack config settings have been loaded successfully. There were {num} settings loaded."
                "\n\nChanges have not been automatically saved. You may choose to look over the new settings before either saving or exiting the program.",
            )
            if danger:
                vars.safe_mode.set(True)
        except Exception as e:
            logging.warning(f"could not load pack suggested settings. Reason: {e}")
            messagebox.showwarning("Error Loading File", f"There was an issue loading the pack config file. {e}")


def confirm_box(parent: Tk, btitle: str, message: str) -> bool:
    allow = False
    root = Toplevel(parent)

    def complete(state: bool) -> bool:
        nonlocal allow
        allow = state
        root.quit()

    root.geometry("300x150")
    root.resizable(False, False)
    root.focus_force()
    root.title(btitle)
    Label(root, text=message, wraplength=292).pack(fill="x")
    # Label(root).pack()
    Button(root, text="Continue", command=lambda: complete(True)).pack()
    Button(root, text="Cancel", command=lambda: complete(False)).pack()
    root.mainloop()
    try:
        root.destroy()
    except Exception:
        False
    return allow


def clear_launches(confirmation: bool):
    try:
        if os.path.exists(Data.CORRUPTION_LAUNCHES):
            os.remove(Data.CORRUPTION_LAUNCHES)
            if confirmation:
                messagebox.showinfo(
                    "Cleaning Completed",
                    "The file that manages corruption launches has been deleted, and will be remade next time you start EdgeWare with corruption on!",
                )
        else:
            if confirmation:
                messagebox.showinfo(
                    "No launches file!",
                    "There is no launches file to delete!\n\nThe launches file is used"
                    " for the launch transition mode, and is automatically deleted when you load a new pack. To generate a new"
                    " one, simply start EdgeWare with the corruption setting on!",
                )
    except Exception as e:
        print(f"failed to clear launches. {e}")
        logging.warning(f"could not delete the corruption launches file. {e}")


def add_list(tk_list_obj: Listbox, key: str, title: str, text: str):
    name = simpledialog.askstring(title, text)
    if name != "" and name is not None:
        config[key] = f"{config[key]}>{name}"
        tk_list_obj.insert(2, name)


def remove_list(tk_list_obj: Listbox, key: str, title: str, text: str):
    index = int(tk_list_obj.curselection()[0])
    item_name = tk_list_obj.get(index)
    if index > 0:
        config[key] = config[key].replace(f">{item_name}", "")
        tk_list_obj.delete(tk_list_obj.curselection())
    else:
        messagebox.showwarning(title, text)


def remove_list_(tk_list_obj: Listbox, key: str, title: str, text: str):
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


def reset_list(tk_list_obj: Listbox, key: str, default):
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
        set_widget_states_with_colors(state, widgets, BUTTON_FACE, "gray35")
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
        if not (isinstance(widget, Frame) or isinstance(widget, Label)):
            widget.configure(state=("normal" if state else "disabled"))
        widget.configure(bg=(color_on if state else color_off))


def refresh():
    subprocess.Popen([sys.executable, Process.CONFIG])
    sys.exit()
