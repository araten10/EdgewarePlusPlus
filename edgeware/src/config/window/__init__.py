# Copyright (C) 2024 Araten & Marigold
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

import ast
import json
import logging
import os
from tkinter import (
    Button,
    Canvas,
    Checkbutton,
    Event,
    Frame,
    Label,
    Listbox,
    Message,
    OptionMenu,
    Scale,
    Text,
    Tk,
    Toplevel,
    font,
    messagebox,
    ttk,
)

from pack import Pack
from pack.data import UniversalSet
from paths import DEFAULT_PACK_PATH, CustomAssets, Data

from config import load_default_config
from config.vars import Vars
from config.window.import_pack import import_pack
from config.window.tabs.annoyance.dangerous_settings import DangerousSettingsTab
from config.window.tabs.annoyance.moods import MoodsTab
from config.window.tabs.annoyance.popup_tweaks import PopupTweaksTab
from config.window.tabs.annoyance.popup_types import PopupTypesTab
from config.window.tabs.annoyance.wallpaper import WallpaperTab
from config.window.tabs.general.booru import BooruTab
from config.window.tabs.general.default_file import DefaultFileTab
from config.window.tabs.general.info import InfoTab
from config.window.tabs.general.start import StartTab
from config.window.tabs.modes import BasicModesTab
from config.window.tabs.corruption import CorruptionModeTab
from config.window.tabs.troubleshooting import TroubleshootingTab
from config.window.tabs.tutorial import open_tutorial
from config.window.utils import (
    all_children,
    config,
    get_live_version,
    refresh,
    write_save,
)

config["wallpaperDat"] = ast.literal_eval(config["wallpaperDat"])
default_config = load_default_config()
pack = Pack(Data.PACKS / config["packPath"] if config["packPath"] else DEFAULT_PACK_PATH)


pil_logger = logging.getLogger("PIL")
pil_logger.setLevel(logging.INFO)

# Generate mood file if it doesn't exist or is invalid
if not pack.info.mood_file.is_file() or isinstance(pack.active_moods, UniversalSet):
    Data.MOODS.mkdir(parents=True, exist_ok=True)
    with open(pack.info.mood_file, "w+") as f:
        f.write(json.dumps({"active": list(map(lambda mood: mood.name, pack.index.moods))}))


class ConfigWindow(Tk):
    def __init__(self) -> None:
        global config, vars
        super().__init__()

        # window things
        self.title("Edgeware++ Config")
        self.geometry("740x900")
        try:
            self.iconbitmap(CustomAssets.config_icon())
            logging.info("set iconbitmap.")
        except Exception:
            logging.warning("failed to set iconbitmap.")

        window_font = font.nametofont("TkDefaultFont")
        title_font = font.Font(font="Default")
        title_font.configure(size=13)

        vars = Vars(config)

        # grouping for enable/disable
        message_group = []

        local_version = default_config["versionplusplus"]
        live_version = get_live_version()

        # tab display code start
        notebook = ttk.Notebook(self)  # tab manager
        notebook.pack(expand=1, fill="both")

        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        general_notebook = ttk.Notebook(general_tab)
        general_notebook.pack(expand=1, fill="both")
        general_notebook.add(StartTab(vars, title_font, message_group, local_version, live_version, pack), text="Start")  # startup screen, info and presets
        general_notebook.add(InfoTab(vars, title_font, message_group, pack), text="Pack Info")  # pack information
        general_notebook.add(BooruTab(vars, title_font), text="Booru Downloader")  # tab for booru downloader
        general_notebook.add(DefaultFileTab(vars, message_group), text="Change Default Files")  # tab for changing default files

        annoyance_tab = ttk.Frame(notebook)
        notebook.add(annoyance_tab, text="Annoyance/Runtime")
        annoyance_notebook = ttk.Notebook(annoyance_tab)
        annoyance_notebook.pack(expand=1, fill="both")
        annoyance_notebook.add(PopupTypesTab(vars, title_font, message_group), text="Popup Types")  # tab for popup types
        annoyance_notebook.add(PopupTweaksTab(vars, title_font, message_group), text="Popup Tweaks")  # tab for popup settings/tweaks/changes etc
        annoyance_notebook.add(WallpaperTab(vars, message_group, pack), text="Wallpaper")  # tab for wallpaper rotation settings
        annoyance_notebook.add(MoodsTab(vars, title_font, message_group, pack), text="Moods")  # tab for mood settings
        annoyance_notebook.add(DangerousSettingsTab(vars, title_font, message_group), text="Dangerous Settings")  # tab for potentially dangerous settings

        notebook.add(BasicModesTab(vars, title_font), text="Modes") # tab for general modes
        notebook.add(CorruptionModeTab(vars, title_font, pack), text="Corruption")  # tab for corruption mode

        notebook.add(TroubleshootingTab(vars, title_font, pack), text="Troubleshooting")  # tab for miscellaneous settings with niche use cases

        notebook.add(Frame(name="tutorial"), text="Tutorial")  # tab for tutorial, etc
        last_tab = notebook.index(notebook.select())  # get initial tab to prevent switching to tutorial
        notebook.bind("<<NotebookTabChanged>>", lambda event: tutorial_container(event, self))

        def tutorial_container(event: Event, root: Tk) -> None:
            nonlocal last_tab
            # print(event.widget.select())
            if event.widget.select() == ".tutorial":
                open_tutorial(root, style, window_font, title_font)
                notebook.select(last_tab)
            else:
                last_tab = notebook.index(notebook.select())

        style = ttk.Style(self)  # style setting for left aligned tabs

        # going to vent here for a second: I have no idea why ttk doesn't use the default theme by default
        # and I also don't know why switching to the default theme is the only way to remove ugly borders on notebook tabs
        # apparently borderwidth, highlightthickness, and anything else just decides to not work...
        style.theme_use("default")

        style.layout(
            "Tab",
            [
                (
                    "Notebook.tab",
                    {
                        "sticky": "nswe",
                        "children": [
                            (
                                "Notebook.padding",
                                {
                                    "side": "top",
                                    "sticky": "nswe",
                                    "children":
                                    # [('Notebook.focus', {'side': 'top', 'sticky': 'nswe', 'children': (Removes ugly selection dots from tabs)
                                    [("Notebook.label", {"side": "top", "sticky": ""})],
                                    # })],
                                },
                            )
                        ],
                    },
                )
            ],
        )
        style.configure("lefttab.TNotebook", tabposition="wn")

        pack_frame = Frame(self)
        pack_frame.pack(fill="x")
        Button(pack_frame, text="Import New Pack", command=lambda: import_window(self)).pack(fill="both", side="left", expand=1)
        Button(pack_frame, text="Switch Pack", command=lambda: switch_window(self, vars)).pack(fill="x", side="left", expand=1)
        Button(self, text="Save & Exit", command=lambda: write_save(vars, True)).pack(fill="x")

        theme_change(config["themeType"].strip(), self, style, window_font, title_font)

        # messageOff toggle here, for turning off all help messages
        toggle_help(vars.message_off.get(), message_group)

        # first time alert popup
        # if not settings['is_configed'] == 1:
        #    messagebox.showinfo('First Config', 'Config has not been run before. All settings are defaulted to frequency of 0 except for popups.\n[This alert will only appear on the first run of config]')
        # version alert, if core web version (0.0.0) is different from the github configdefault, alerts user that update is available
        #   if user is a bugfix patch behind, the _X at the end of the 0.0.0, they will not be alerted
        #   the version will still be red to draw attention to it
        if local_version.split("_")[0] != live_version.split("_")[0] and not (local_version.endswith("DEV") or config["toggleInternet"]):
            messagebox.showwarning(
                "Update Available",
                'Main local version and web version are not the same.\nPlease visit the Github and download the newer files,\nor use the direct download link on the "Start" tab.',
            )
        self.mainloop()


# helper funcs for lambdas =======================================================
def theme_change(theme: str, root, style, mfont, tfont) -> None:
    if theme == "Original" or config["themeNoConfig"] is True:
        for widget in all_children(root):
            if isinstance(widget, Message):
                widget.configure(font=(mfont, 8))
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TNotebook", background="#f0f0f0")
        style.map("TNotebook.Tab", background=[("selected", "#f0f0f0")])
        style.configure("TNotebook.Tab", background="#d9d9d9")
    else:
        if theme == "Dark":
            for widget in all_children(root):
                if isinstance(widget, Frame) or isinstance(widget, Canvas):
                    widget.configure(bg="#282c34")
                if isinstance(widget, Button):
                    widget.configure(bg="#282c34", fg="ghost white", activebackground="#282c34", activeforeground="ghost white")
                if isinstance(widget, Label):
                    widget.configure(bg="#282c34", fg="ghost white")
                if isinstance(widget, OptionMenu):
                    widget.configure(bg="#282c34", fg="ghost white", highlightthickness=0, activebackground="#282c34", activeforeground="ghost white")
                if isinstance(widget, Text):
                    widget.configure(bg="#1b1d23", fg="ghost white")
                if isinstance(widget, Scale):
                    widget.configure(bg="#282c34", fg="ghost white", activebackground="#282c34", troughcolor="#c8c8c8", highlightthickness=0)
                if isinstance(widget, Checkbutton):
                    widget.configure(bg="#282c34", fg="ghost white", selectcolor="#1b1d23", activebackground="#282c34", activeforeground="ghost white")
                if isinstance(widget, Message):
                    widget.configure(bg="#282c34", fg="ghost white", font=(mfont, 8))
            style.configure("TFrame", background="#282c34")
            style.configure("TNotebook", background="#282c34")
            style.map("TNotebook.Tab", background=[("selected", "#282c34")])
            style.configure("TNotebook.Tab", background="#1b1d23", foreground="#f9faff")
        if theme == "The One":
            for widget in all_children(root):
                if isinstance(widget, Frame) or isinstance(widget, Canvas):
                    widget.configure(bg="#282c34")
                if isinstance(widget, Button):
                    widget.configure(bg="#282c34", fg="#00ff41", activebackground="#1b1d23", activeforeground="#00ff41")
                if isinstance(widget, Label):
                    widget.configure(bg="#282c34", fg="#00ff41")
                if isinstance(widget, OptionMenu):
                    widget.configure(bg="#282c34", fg="#00ff41", highlightthickness=0, activebackground="#282c34", activeforeground="#00ff41")
                if isinstance(widget, Text):
                    widget.configure(bg="#1b1d23", fg="#00ff41")
                if isinstance(widget, Scale):
                    widget.configure(bg="#282c34", fg="#00ff41", activebackground="#282c34", troughcolor="#009a22", highlightthickness=0)
                if isinstance(widget, Checkbutton):
                    widget.configure(bg="#282c34", fg="#00ff41", selectcolor="#1b1d23", activebackground="#282c34", activeforeground="#00ff41")
                if isinstance(widget, Message):
                    widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8))
            style.configure("TFrame", background="#282c34")
            style.configure("TNotebook", background="#282c34")
            style.map("TNotebook.Tab", background=[("selected", "#282c34")])
            style.configure("TNotebook.Tab", background="#1b1d23", foreground="#00ff41")
            mfont.configure(family="Consolas", size=8)
            tfont.configure(family="Consolas")
        if theme == "Ransom":
            for widget in all_children(root):
                if isinstance(widget, Frame) or isinstance(widget, Canvas):
                    widget.configure(bg="#841212")
                if isinstance(widget, Button):
                    widget.configure(bg="#841212", fg="yellow", activebackground="#841212", activeforeground="yellow")
                if isinstance(widget, Label):
                    widget.configure(bg="#841212", fg="white")
                if isinstance(widget, OptionMenu):
                    widget.configure(bg="#841212", fg="white", highlightthickness=0, activebackground="#841212", activeforeground="white")
                if isinstance(widget, Text):
                    widget.configure(bg="white", fg="black")
                if isinstance(widget, Scale):
                    widget.configure(bg="#841212", fg="white", activebackground="#841212", troughcolor="#c8c8c8", highlightthickness=0)
                if isinstance(widget, Checkbutton):
                    widget.configure(bg="#841212", fg="white", selectcolor="#5c0d0d", activebackground="#841212", activeforeground="white")
                if isinstance(widget, Message):
                    widget.configure(bg="#841212", fg="white", font=("Arial", 8))
            style.configure("TFrame", background="#841212")
            style.configure("TNotebook", background="#841212")
            style.map("TNotebook.Tab", background=[("selected", "#841212")])
            style.configure("TNotebook.Tab", background="#5c0d0d", foreground="#ffffff")
            mfont.configure(family="Arial")
            tfont.configure(family="Arial Bold")
        if theme == "Goth":
            for widget in all_children(root):
                if isinstance(widget, Frame) or isinstance(widget, Canvas):
                    widget.configure(bg="#282c34")
                if isinstance(widget, Button):
                    widget.configure(bg="#282c34", fg="MediumPurple1", activebackground="#282c34", activeforeground="MediumPurple1")
                if isinstance(widget, Label):
                    widget.configure(bg="#282c34", fg="MediumPurple1")
                if isinstance(widget, OptionMenu):
                    widget.configure(bg="#282c34", fg="MediumPurple1", highlightthickness=0, activebackground="#282c34", activeforeground="MediumPurple1")
                if isinstance(widget, Text):
                    widget.configure(bg="MediumOrchid2", fg="purple4")
                if isinstance(widget, Scale):
                    widget.configure(bg="#282c34", fg="MediumPurple1", activebackground="#282c34", troughcolor="MediumOrchid2", highlightthickness=0)
                if isinstance(widget, Checkbutton):
                    widget.configure(bg="#282c34", fg="MediumPurple1", selectcolor="#1b1d23", activebackground="#282c34", activeforeground="MediumPurple1")
                if isinstance(widget, Message):
                    widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 8))
            style.configure("TFrame", background="#282c34")
            style.configure("TNotebook", background="#282c34")
            style.map("TNotebook.Tab", background=[("selected", "#282c34")])
            style.configure("TNotebook.Tab", background="#1b1d23", foreground="MediumPurple1")
            mfont.configure(family="Constantia")
            tfont.configure(family="Constantia")
        if theme == "Bimbo":
            for widget in all_children(root):
                if isinstance(widget, Frame) or isinstance(widget, Canvas):
                    widget.configure(bg="pink")
                if isinstance(widget, Button):
                    widget.configure(bg="pink", fg="deep pink", activebackground="hot pink", activeforeground="deep pink")
                if isinstance(widget, Label):
                    widget.configure(bg="pink", fg="deep pink")
                if isinstance(widget, OptionMenu):
                    widget.configure(bg="pink", fg="deep pink", highlightthickness=0, activebackground="hot pink", activeforeground="deep pink")
                if isinstance(widget, Text):
                    widget.configure(bg="light pink", fg="magenta2")
                if isinstance(widget, Scale):
                    widget.configure(bg="pink", fg="deep pink", activebackground="pink", troughcolor="hot pink", highlightthickness=0)
                if isinstance(widget, Checkbutton):
                    widget.configure(bg="pink", fg="deep pink", selectcolor="light pink", activebackground="pink", activeforeground="deep pink")
                if isinstance(widget, Message):
                    widget.configure(bg="pink", fg="deep pink", font=("Constantia", 8))
            style.configure("TFrame", background="pink")
            style.configure("TNotebook", background="pink")
            style.map("TNotebook.Tab", background=[("selected", "pink")])
            style.configure("TNotebook.Tab", background="lightpink", foreground="deep pink")
            mfont.configure(family="Constantia")
            tfont.configure(family="Constantia")


def toggle_help(state: bool, messages: list) -> None:
    if state is True:
        try:
            for widget in messages:
                widget.destroy()
        except Exception as e:
            logging.warning(f"could not properly turn help off. {e}")


def switch_pack(vars: Vars, pack: str) -> None:
    vars.pack_path.set(pack)
    write_save(vars)
    refresh()


def import_window(parent: Tk) -> None:
    root = Toplevel(parent)
    root.geometry("350x225")
    root.resizable(False, True)
    root.focus_force()
    root.title("Import New Pack")

    message = "Would you like to import a new pack, or change the default pack instead?\n\nImporting a new pack saves it to /data/packs, and allows fast switching between all packs saved this way.\n\nChanging the default pack saves it to /resource, overwriting any pack previously saved there.\n"
    Label(root, text=message, wraplength=325).pack(fill="x")
    Button(root, text="Import New", command=lambda: import_pack(False)).pack()
    Button(root, text="Change Default", command=lambda: import_pack(True)).pack()
    Button(root, text="Cancel", command=lambda: root.destroy()).pack()
    root.mainloop()
    root.destroy()


def switch_window(parent: Tk, vars: Vars) -> None:
    root = Toplevel(parent)
    root.geometry("275x340")
    root.resizable(False, True)
    root.focus_force()
    root.title("Switch Pack")

    Label(root, text=f"Currently loaded pack:\n{vars.pack_path.get()}", wraplength=250).pack(fill="x")

    switch_list_frame = Frame(root)
    switch_list_frame.pack()
    switch_list = Listbox(switch_list_frame, width=40, height=15)
    Data.PACKS.mkdir(parents=True, exist_ok=True)
    pack_list = os.listdir(Data.PACKS)
    i = 0
    for i, pack in enumerate(pack_list):
        switch_list.insert(i, pack)

    def get_list_entry(listbox: Listbox) -> str:
        selection = listbox.curselection()
        selected_pack = listbox.get(selection[0])
        print(selected_pack)
        return selected_pack

    switch_list.pack(side="left")
    switch_list_scrollbar = ttk.Scrollbar(switch_list_frame, orient="vertical", command=switch_list.yview)
    switch_list_scrollbar.pack(side="left", fill="y")
    switch_buttons_frame = Frame(root)
    switch_buttons_frame.pack()
    Button(switch_buttons_frame, text="Switch", command=lambda: switch_pack(vars, get_list_entry(switch_list))).pack(side="left")
    Button(switch_buttons_frame, text="Default", command=lambda: switch_pack(vars, "default")).pack(side="left", padx=5)
    Button(switch_buttons_frame, text="Cancel", command=lambda: root.destroy()).pack(side="left")
