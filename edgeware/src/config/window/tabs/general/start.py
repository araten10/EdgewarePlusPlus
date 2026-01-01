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

import textwrap
import webbrowser
from tkinter import (
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    OptionMenu,
    Scale,
    StringVar,
    Text,
)

from config.vars import Vars
from config.window.preset import apply_preset, list_presets, load_preset, load_preset_description, save_preset
from config.window.utils import all_children, request_global_panic_key, set_widget_states
from config.window.widgets.layout import (
    PAD,
    ConfigRow,
    ConfigSection,
    ConfigToggle,
)
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip
from pack import Pack
from panic import send_panic
from paths import CustomAssets
from PIL import ImageTk

INTRO_TEXT = 'Welcome to Edgeware++!\nYou can use the tabs at the top of this window to navigate the various config settings for the main program. Annoyance/Runtime is for how the program works while running, Modes is for more complicated and involved settings that change how Edgeware works drastically, and Troubleshooting and About are for learning this program better and fixing errors should anything go wrong.\n\nAside from these helper memos, there are also tooltips on several buttons and sliders. If you see your mouse cursor change to a "question mark", hover for a second or two to see more information on the setting.'
THEME_TEXT = "You'll have to save and refresh the config window to get the theme to show up properly, but this tab will change to the currently selected theme so you can see what it looks like! None of the sliders or buttons in this section do anything, so feel free to play around with them to test it out!"
PANIC_TEXT = '"Panic" is a feature that allows you to instantly halt the program and revert your desktop background back to the "panic background" set in the wallpaper sub-tab. (found in the annoyance tab)\n\nThere are a few ways to initiate panic, but one of the easiest to access is setting a hotkey here. You should also make sure to change your panic wallpaper to your currently used wallpaper before using Edgeware!'
PRESET_TEXT = "Please be careful before importing unknown config presets! Double check to make sure you're okay with the settings before launching Edgeware."


class StartTab(ScrollFrame):
    def __init__(self, vars: Vars, local_version: str, live_version: str, pack: Pack) -> None:
        super().__init__()

        # Information

        information_section = ConfigSection(self.viewPort, "Information", INTRO_TEXT)
        information_section.pack()

        github_frame = Frame(information_section)
        github_frame.pack(fill="both", side="left", expand=1)
        github_url = "https://github.com/araten10/EdgewarePlusPlus"
        download_url = "https://github.com/araten10/EdgewarePlusPlus/archive/refs/heads/main.zip"
        Button(github_frame, text="Open Edgeware++ Github", command=lambda: webbrowser.open(github_url)).pack(fill="both", expand=1)
        Button(github_frame, text="Download Newest Update", command=lambda: webbrowser.open(download_url)).pack(fill="both", expand=1)

        version_frame = Frame(information_section)
        version_frame.pack(fill="both", side="left", expand=1)
        Label(version_frame, text=f"Edgeware++ Local Version:\n{local_version}").pack(fill="x")
        github_label = Label(version_frame, text=f"Edgeware++ Github Version:\n{live_version}")
        if local_version != live_version:
            github_label.configure(bg="red")
            github_label.ignore_theme_bg = True
            github_label.ignore_theme_fg = True
        github_label.pack(fill="x")

        pack_preset_section = Frame(self.viewPort, borderwidth=2, relief=RAISED)
        pack_preset_section.pack(padx=8, pady=8, fill="x")

        pack_preset_col_1 = Frame(pack_preset_section)
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

        pack_preset_col_2 = Frame(pack_preset_section)
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

        if len(pack.config) == 0:
            set_widget_states(False, [load_pack_preset_button])

        # Panic

        panic_section = ConfigSection(self.viewPort, "Panic Settings", PANIC_TEXT)
        panic_section.pack()

        set_global_panic_button = Button(
            panic_section,
            text=f"Set Global\nPanic Key\n<{vars.global_panic_key.get()}>",
            command=lambda: request_global_panic_key(set_global_panic_button, vars.global_panic_key),
            cursor="question_arrow",
        )
        set_global_panic_button.pack(padx=PAD, pady=PAD, fill="x", side="left", expand=1)
        CreateToolTip(set_global_panic_button, "This is a global key that does not require focus to activate. Press the key at any time to perform panic.")
        Button(panic_section, text="Perform Panic", command=send_panic).pack(padx=PAD, pady=PAD, fill="both", side="left", expand=1)

        # Theme

        # TODO: Use Theme object
        def theme_helper(theme: str) -> None:
            skiplist = [
                theme_demo_frame,
                theme_demo_popup_frame,
                theme_demo_prompt_frame,
                theme_demo_config_frame,
                theme_demo_popup_title,
                theme_demo_prompt_title,
                theme_demo_config_title,
            ]
            if theme == "Original":
                for widget in all_children(theme_demo_frame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#f0f0f0")
                    if isinstance(widget, Button):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont", activebackground="#f0f0f0", activeforeground="black")
                    if isinstance(widget, Label):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont")
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont", activebackground="#f0f0f0", activeforeground="black")
                    if isinstance(widget, Text):
                        widget.configure(bg="white", fg="black")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#f0f0f0", fg="black", font="TkDefaultFont", activebackground="#f0f0f0", troughcolor="#c8c8c8")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#f0f0f0", fg="black", font="TkDefaultFont", selectcolor="white", activebackground="#f0f0f0", activeforeground="black"
                        )
                theme_demo_popup_tooltip.background = "#ffffff"
                theme_demo_popup_tooltip.foreground = "#000000"
                theme_demo_popup_tooltip.bordercolor = "#000000"
            if theme == "Dark":
                for widget in all_children(theme_demo_frame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#282c34")
                    if isinstance(widget, Button):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9), activebackground="#282c34", activeforeground="ghost white")
                    if isinstance(widget, Label):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9), activebackground="#282c34", activeforeground="ghost white")
                    if isinstance(widget, Text):
                        widget.configure(bg="#1b1d23", fg="ghost white")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#282c34", fg="ghost white", font=("Segoe UI", 9), activebackground="#282c34", troughcolor="#c8c8c8")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#282c34",
                            fg="ghost white",
                            font=("Segoe UI", 9),
                            selectcolor="#1b1d23",
                            activebackground="#282c34",
                            activeforeground="ghost white",
                        )
                theme_demo_popup_tooltip.background = "#1b1d23"
                theme_demo_popup_tooltip.foreground = "#ffffff"
                theme_demo_popup_tooltip.bordercolor = "#ffffff"
            if theme == "The One":
                for widget in all_children(theme_demo_frame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#282c34")
                    if isinstance(widget, Button):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8), activebackground="#1b1d23", activeforeground="#00ff41")
                    if isinstance(widget, Label):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8), activebackground="#282c34", activeforeground="#00ff41")
                    if isinstance(widget, Text):
                        widget.configure(bg="#1b1d23", fg="#00ff41")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#282c34", fg="#00ff41", font=("Consolas", 8), activebackground="#282c34", troughcolor="#009a22")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#282c34", fg="#00ff41", font=("Consolas", 8), selectcolor="#1b1d23", activebackground="#282c34", activeforeground="#00ff41"
                        )
                theme_demo_popup_tooltip.background = "#1b1d23"
                theme_demo_popup_tooltip.foreground = "#00ff41"
                theme_demo_popup_tooltip.bordercolor = "#00ff41"
            if theme == "Ransom":
                for widget in all_children(theme_demo_frame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#841212")
                    if isinstance(widget, Button):
                        widget.configure(bg="#841212", fg="yellow", font=("Arial", 9), activebackground="#841212", activeforeground="yellow")
                    if isinstance(widget, Label):
                        widget.configure(bg="#841212", fg="white", font=("Arial Bold", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#841212", fg="white", font=("Arial Bold", 9), activebackground="#841212", activeforeground="white")
                    if isinstance(widget, Text):
                        widget.configure(bg="white", fg="black")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#841212", fg="white", font=("Arial", 9), activebackground="#841212", troughcolor="#c8c8c8")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#841212", fg="white", font=("Arial", 9), selectcolor="#5c0d0d", activebackground="#841212", activeforeground="white"
                        )
                theme_demo_popup_tooltip.background = "#ff2600"
                theme_demo_popup_tooltip.foreground = "#ffffff"
                theme_demo_popup_tooltip.bordercolor = "#000000"
            if theme == "Goth":
                for widget in all_children(theme_demo_frame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="#282c34")
                    if isinstance(widget, Button):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9), activebackground="#282c34", activeforeground="MediumPurple1")
                    if isinstance(widget, Label):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9), activebackground="#282c34", activeforeground="MediumPurple1")
                    if isinstance(widget, Text):
                        widget.configure(bg="MediumOrchid2", fg="purple4")
                    if isinstance(widget, Scale):
                        widget.configure(bg="#282c34", fg="MediumPurple1", font=("Constantia", 9), activebackground="#282c34", troughcolor="MediumOrchid2")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="#282c34",
                            fg="MediumPurple1",
                            font=("Constantia", 9),
                            selectcolor="#1b1d23",
                            activebackground="#282c34",
                            activeforeground="MediumPurple1",
                        )
                theme_demo_popup_tooltip.background = "#1b1d23"
                theme_demo_popup_tooltip.foreground = "#cc60ff"
                theme_demo_popup_tooltip.bordercolor = "#b999fe"
            if theme == "Bimbo":
                for widget in all_children(theme_demo_frame):
                    if widget in skiplist:
                        continue
                    if isinstance(widget, Frame):
                        widget.configure(bg="pink")
                    if isinstance(widget, Button):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9), activebackground="hot pink", activeforeground="deep pink")
                    if isinstance(widget, Label):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9))
                    if isinstance(widget, OptionMenu):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9), activebackground="hot pink", activeforeground="deep pink")
                    if isinstance(widget, Text):
                        widget.configure(bg="light pink", fg="magenta2")
                    if isinstance(widget, Scale):
                        widget.configure(bg="pink", fg="deep pink", font=("Constantia", 9), activebackground="pink", troughcolor="hot pink")
                    if isinstance(widget, Checkbutton):
                        widget.configure(
                            bg="pink", fg="deep pink", font=("Constantia", 9), selectcolor="light pink", activebackground="pink", activeforeground="deep pink"
                        )
                theme_demo_popup_tooltip.background = "#ffc5cd"
                theme_demo_popup_tooltip.foreground = "#ff3aa3"
                theme_demo_popup_tooltip.bordercolor = "#ff84c1"
            set_widget_states(False, test_group, theme)

        theme_types = ["Original", "Dark", "The One", "Ransom", "Goth", "Bimbo"]

        theme_section = ConfigSection(self.viewPort, "Theme", THEME_TEXT)
        theme_section.pack()

        theme_selection_frame = Frame(theme_section)
        theme_selection_frame.pack(fill="both", side="left")
        theme_dropdown = OptionMenu(theme_selection_frame, vars.theme, *theme_types, command=lambda key: theme_helper(key))
        theme_dropdown.configure(width=12)
        theme_dropdown.pack(fill="both", side="top")
        ignore_config_toggle = Checkbutton(theme_selection_frame, text="Ignore Config", variable=vars.theme_ignore_config, cursor="question_arrow")
        ignore_config_toggle.pack(fill="both", side="top")
        CreateToolTip(ignore_config_toggle, "When enabled, the selected theme does not apply to the config window.")

        theme_demo_frame = Frame(theme_section)
        theme_demo_frame.pack(fill="both", side="left", expand=1)

        theme_demo_popup_frame = Frame(theme_demo_frame)
        theme_demo_popup_frame.pack(fill="both", side="left", padx=1)
        theme_demo_popup_title = Label(theme_demo_popup_frame, text="Popup")
        theme_demo_popup_title.pack(side="top")
        self.viewPort.demo_popup_image = ImageTk.PhotoImage(file=CustomAssets.theme_demo())  # Stored to avoid garbage collection
        theme_demo_popup_label = Label(
            theme_demo_popup_frame, image=self.viewPort.demo_popup_image, width=150, height=75, borderwidth=2, relief=GROOVE, cursor="question_arrow"
        )
        theme_demo_popup_label.pack(side="top", ipadx=1, ipady=1)
        theme_demo_popup_tooltip = CreateToolTip(
            theme_demo_popup_label,
            "NOTE: the test image is very small, buttons and captions will appear proportionally larger here!\n\nAlso, look! The tooltip changed too!",
        )
        Button(theme_demo_popup_label, text="Test~").place(x=-10, y=-10, relx=1, rely=1, anchor="se")
        Label(theme_demo_popup_label, text="Lewd Caption Here!").place(x=5, y=5)

        theme_demo_prompt_frame = Frame(theme_demo_frame)
        theme_demo_prompt_frame.pack(fill="both", side="left", padx=1)
        theme_demo_prompt_title = Label(theme_demo_prompt_frame, text="Prompt")
        theme_demo_prompt_title.pack()
        theme_demo_prompt_body = Frame(theme_demo_prompt_frame, borderwidth=2, relief=GROOVE, width=100, height=75)
        theme_demo_prompt_body.pack(fill="both", expand=1)
        Label(theme_demo_prompt_body, text="Do as I say~").pack(fill="both", expand=1)
        Text(theme_demo_prompt_body, width=16, height=1).pack(fill="both")
        Button(theme_demo_prompt_body, text="Sure!").pack(expand=1)

        theme_demo_config_frame = Frame(theme_demo_frame)
        theme_demo_config_frame.pack(fill="both", side="left", padx=1)
        theme_demo_config_title = Label(theme_demo_config_frame, text="Config")
        theme_demo_config_title.pack(side="top")
        theme_demo_config_body = Frame(theme_demo_config_frame, borderwidth=2, relief=GROOVE)
        theme_demo_config_body.pack(fill="both", expand=1)

        theme_demo_config_col_1 = Frame(theme_demo_config_body)
        theme_demo_config_col_1.pack(side="left", fill="both", expand=1)
        Button(theme_demo_config_col_1, text="Activated").pack(fill="y")
        Scale(theme_demo_config_col_1, orient="horizontal", from_=1, to=100, highlightthickness=0).pack(fill="y", expand=1)

        theme_demo_config_col_2 = Frame(theme_demo_config_body)
        theme_demo_config_col_2.pack(side="left", fill="both", expand=1)
        theme_demo_config_button_deactivated = Button(theme_demo_config_col_2, text="Deactivated")
        theme_demo_config_button_deactivated.pack(fill="y")
        theme_demo_button_scale_deactivated = Scale(theme_demo_config_col_2, orient="horizontal", from_=1, to=100, highlightthickness=0)
        theme_demo_button_scale_deactivated.pack(fill="y", expand=1)
        test_group = [theme_demo_button_scale_deactivated, theme_demo_config_button_deactivated]
        set_widget_states(False, test_group)

        Checkbutton(theme_demo_config_body, text="Check").pack(fill="y")
        theme_demo_config_dropdown = OptionMenu(theme_demo_config_body, StringVar(self.viewPort, "Option"), *["Option", "Menu"])
        theme_demo_config_dropdown.config(highlightthickness=0)
        theme_demo_config_dropdown.pack(fill="y")

        theme_helper(vars.theme.get())

        # Other

        other_section = ConfigSection(self.viewPort, "General Settings")
        other_section.pack()

        other_row = ConfigRow(other_section)
        other_row.pack()

        toggle_flair_button = ConfigToggle(other_row, text="Show Loading Flair", variable=vars.startup_splash, cursor="question_arrow")
        toggle_flair_button.grid(0, 0)
        CreateToolTip(toggle_flair_button, 'Displays a brief "loading" image before Edgeware startup, which can be set per-pack by the pack creator.')
        ConfigToggle(other_row, text="Run Edgeware on Save & Exit", variable=vars.run_on_save_quit).grid(0, 1)

        ConfigToggle(other_row, text="Create Desktop Icons", variable=vars.desktop_icons).grid(1, 0)
        toggle_safe_mode_button = ConfigToggle(other_row, text='Warn if "Dangerous" Settings Active', variable=vars.safe_mode, cursor="question_arrow")
        toggle_safe_mode_button.grid(1, 1)
        CreateToolTip(
            toggle_safe_mode_button,
            "Asks you to confirm before saving if certain settings are enabled.\n"
            "Things defined as Dangerous Settings:\n\n"
            "Extreme (code red! code red! make sure you fully understand what these do before using!):\n"
            "Replace Images\n\n"
            "Major (very dangerous, can affect your computer):\n"
            "Launch on Startup, Fill Drive\n\n"
            "Medium (can lead to embarassment or reduced control over Edgeware):\n"
            "Timer Mode, Mitosis Mode, Show on Discord, short hibernate cooldown\n\n"
            "Minor (low risk but could lead to unwanted interactions):\n"
            "Disable Panic Hotkey, Run on Save & Exit",
        )

        ConfigToggle(other_row, text="Disable Config Help Messages", variable=vars.message_off).grid(2, 0)

        # Presets

        preset_section = ConfigSection(self.viewPort, "Config Presets", PRESET_TEXT)
        preset_section.pack()

        preset_list = list_presets()
        self.presets_found = bool(preset_list)
        self.preset_var = StringVar(
            self.viewPort, preset_list.pop(0) if self.presets_found else "No presets found"
        )  # Without pop the first item appears twice in the list

        preset_selection_frame = Frame(preset_section)
        preset_selection_frame.pack(side="left", fill="x", padx=6)
        self.preset_dropdown = OptionMenu(preset_selection_frame, self.preset_var, self.preset_var.get(), *preset_list, command=self.set_preset_description)
        self.preset_dropdown.pack(fill="x", expand=1)
        self.load_preset_button = Button(
            preset_selection_frame,
            text="Load Preset",
            command=lambda: apply_preset(load_preset(self.preset_var.get()), vars),
            state=("normal" if self.presets_found else "disabled"),
        )
        self.load_preset_button.pack(fill="both", expand=1)
        Label(preset_selection_frame).pack(fill="both", expand=1)
        Label(preset_selection_frame).pack(fill="both", expand=1)
        Button(preset_selection_frame, text="Save Preset", command=self.save_preset_and_update).pack(fill="both", expand=1)

        preset_description_frame = Frame(preset_section, borderwidth=2, relief=GROOVE)
        preset_description_frame.pack(side="right", fill="both", expand=1)
        self.preset_name_label = Label(preset_description_frame, text="No presets found", font="Default 15")
        self.preset_name_label.pack(fill="y", pady=4)
        self.preset_description_wrap = textwrap.TextWrapper(width=100, max_lines=5)
        self.preset_description_label = Label(preset_description_frame, text=self.preset_description_wrap.fill(text=""), relief=GROOVE)
        self.preset_description_label.pack(fill="both", expand=1)
        self.set_preset_description(self.preset_var.get())

        # For now these buttons have been removed, but the settings to save/refresh without exiting may be useful- might add back in if formatting changes
        # Label(self.viewPort, text="Save", font=title_font, relief=GROOVE).pack(pady=2)
        #
        # Button(self.viewPort, text="Save Settings", command=lambda: write_save(vars)).pack(fill="x", pady=2)
        # Button(self.viewPort, text="Save & Refresh", command=lambda: save_and_refresh(vars)).pack(fill="x", pady=2)

    def set_preset_description(self, name: str) -> None:
        if self.presets_found:
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

        set_widget_states(True, [self.load_preset_button])  # Set state in case there were no presets previously
        self.preset_var.set(name)
        self.set_preset_description(name)
