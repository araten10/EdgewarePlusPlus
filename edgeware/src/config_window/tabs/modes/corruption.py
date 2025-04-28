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

import os
from tkinter import (
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    OptionMenu,
    Scale,
    simpledialog,
    ttk,
)
from tkinter.font import Font

from config_window.preset import apply_preset
from config_window.utils import (
    assign,
    clear_launches,
    config,
    set_widget_states,
    set_widget_states_with_colors,
)
from config_window.vars import Vars
from pack import Pack
from paths import Assets
from PIL import ImageTk
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

INTRO_TEXT = "Welcome to the Corruption tab!\n\n Normally I'd put tutorials and help like this elsewhere, but I realize that this is probably the most complex and in-depth feature to be added to Edgeware. Don't worry, we'll work through it together!\n\nEach tab will go over a feature of corruption, while also highlighting where the settings are for reference. Any additional details not covered here can be found in the \"About\" tab!"
START_TEXT = 'To start corruption mode, you can use these settings in the top left to turn it on. If turning it on is greyed out, it means the current pack does not support corruption! Down below are more toggle settings for fine-tuning corruption to work how you want it.\n\n Remember, for any of these settings, if your mouse turns into a "question mark" while hovering over it, you can stay hovered to view a tooltip on what the setting does!'
TRANSITION_TEXT = "Transitions are how each corruption level fades into eachother. While running corruption mode, the current level and next level are accessed simultaneously to blend the two together. You can choose the blending modes with the top option, and how edgeware transitions from one corruption level to the next with the bottom option. The visualizer image is purely to help understand how the transitions work, with the two colours representing both accessed levels. The sliders below fine-tune how long each level will last, so for a rough estimation on how long full corruption will take, you can multiply the active slider by the number of levels."


class CorruptionModeTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, pack: Pack) -> None:
        super().__init__()

        corruption_frame = Frame(self.viewPort)
        corruption_frame.pack(fill="x")

        corruption_settings_frame = Frame(corruption_frame)
        corruption_settings_frame.pack(fill="x", side="left")

        basic_settings_frame = Frame(corruption_settings_frame)
        basic_settings_frame.pack(fill="both", side="top")

        # Start
        start_frame = Frame(basic_settings_frame, borderwidth=5, relief=RAISED)
        start_frame.pack(fill="both", side="left")
        corruption_toggle = Checkbutton(start_frame, text="Turn on Corruption", variable=vars.corruption_mode, cursor="question_arrow")
        corruption_toggle.pack(fill="x", expand=1)
        CreateToolTip(
            corruption_toggle,
            "Corruption Mode gradually makes the pack more depraved, by slowly toggling on previously hidden"
            " content. Or at least that's the idea, pack creators can do whatever they want with it.\n\n"
            "Corruption uses the 'mood' feature, which must be supported with a corruption.json file in the resource"
            ' folder. Over time moods will "unlock", leading to new things you haven\'t seen before the longer you use'
            ' Edgeware.\n\nFor more information, check out the "About" tab. \n\nNOTE: currently not implemented! Holy god I hope I remember to remove this notice later!',
        )
        full_permission_toggle = Checkbutton(start_frame, text="Full Permissions Mode", variable=vars.corruption_full, cursor="question_arrow")
        full_permission_toggle.pack(fill="x", expand=1)
        CreateToolTip(full_permission_toggle, "This setting allows corruption mode to change config settings as it goes through corruption levels.")
        recommended_settings_button = Button(
            start_frame,
            text="Recommended Settings",
            cursor="question_arrow",
            height=2,
            command=lambda: apply_preset(pack.config, vars, ["corruptionMode", "corruptionTime", "corruptionFadeType"]),
        )
        recommended_settings_button.pack(fill="x", padx=2, pady=2)
        CreateToolTip(
            recommended_settings_button,
            'Pack creators can set "default corruption settings" for their pack, to give'
            " users a more designed and consistent experience. This setting turns those on (if they exist)."
            '\n\nSidenote: this will load configurations similarly to the option in the "Pack Info" tab, however this one will only load corruption-specific settings.',
        )
        start_group = [corruption_toggle]

        # Transition
        transition_frame = Frame(basic_settings_frame, borderwidth=5, relief=RAISED)
        transition_frame.pack(fill="both", side="left")

        fade_frame = Frame(transition_frame)
        fade_frame.pack(side="top", fill="both", pady=1)

        fade_selection_frame = Frame(fade_frame)
        fade_selection_frame.pack(side="left", fill="x")
        fade_types = ["Normal", "Abrupt"]
        fade_dropdown = OptionMenu(fade_selection_frame, vars.corruption_fade, *fade_types, command=lambda key: fade_helper(key))
        fade_dropdown.configure(width=9, highlightthickness=0)
        fade_dropdown.pack(side="top")
        fade_normal_image = ImageTk.PhotoImage(file=Assets.CORRUPTION_DEFAULT)
        fade_abrupt_image = ImageTk.PhotoImage(file=Assets.CORRUPTION_ABRUPT)
        fade_image = Label(fade_selection_frame, image=fade_normal_image, borderwidth=2, relief=GROOVE)
        fade_image.pack(side="top")

        fade_description = Label(fade_frame, text="Error loading fade description!", borderwidth=2, relief=GROOVE, wraplength=150)
        fade_description.configure(height=3, width=22)
        fade_description.pack(side="left", fill="y", padx=3, ipadx=2, ipady=2)

        trigger_frame = Frame(transition_frame)
        trigger_frame.pack(side="top", fill="both", pady=1)

        trigger_selection_frame = Frame(trigger_frame)
        trigger_selection_frame.pack(side="left", fill="x")
        trigger_types = ["Timed", "Popup", "Launch"]
        trigger_dropdown = OptionMenu(trigger_selection_frame, vars.corruption_trigger, *trigger_types, command=lambda key: trigger_helper(key, False))
        trigger_dropdown.configure(width=9, highlightthickness=0)
        trigger_dropdown.pack(side="top")

        trigger_description = Label(trigger_frame, text="Error loading trigger description!", borderwidth=2, relief=GROOVE, wraplength=150)
        trigger_description.configure(height=3, width=22)
        trigger_description.pack(side="left", fill="y", padx=3, ipadx=2, ipady=2)

        # Level progress
        level_frame = Frame(corruption_settings_frame)
        level_frame.pack(fill="x", side="top")

        level_time_frame = Frame(level_frame)
        level_time_frame.pack(side="left", fill="x", padx=1, expand=1)
        level_time_scale = Scale(level_time_frame, label="Level Time", variable=vars.corruption_time, orient="horizontal", from_=5, to=1800)
        level_time_scale.pack(fill="y")
        level_time_manual = Button(
            level_time_frame,
            text="Manual time...",
            command=lambda: assign(vars.corruption_time, simpledialog.askinteger("Manual Level Time (sec)", prompt="[5-1800]: ")),
        )
        level_time_manual.pack(fill="y")
        level_time_group = [level_time_scale, level_time_manual]

        level_popups_frame = Frame(level_frame)
        level_popups_frame.pack(side="left", fill="x", padx=1, expand=1)
        level_popups_scale = Scale(level_popups_frame, label="Level Popups", variable=vars.corruption_popups, orient="horizontal", from_=1, to=100)
        level_popups_scale.pack(fill="y")
        level_popups_manual = Button(
            level_popups_frame,
            text="Manual popups...",
            command=lambda: assign(vars.corruption_popups, simpledialog.askinteger("Manual Level Popups (per transition)", prompt="[1-100]: ")),
        )
        level_popups_manual.pack(fill="y")
        level_popup_group = [level_popups_scale, level_popups_manual]

        level_launches_frame = Frame(level_frame)
        level_launches_frame.pack(side="left", fill="x", padx=1, expand=1)
        level_launches_scale = Scale(level_launches_frame, label="Level Launches", variable=vars.corruption_launches, orient="horizontal", from_=2, to=31)
        level_launches_scale.pack(fill="y")
        level_launches_manual = Button(
            level_launches_frame,
            text="Manual launches...",
            command=lambda: assign(vars.corruption_launches, simpledialog.askinteger("Manual Level Launches (per transition)", prompt="[2-31]: ")),
        )
        level_launches_manual.pack(fill="y")
        level_launch_group = [level_launches_scale, level_launches_manual]

        Button(level_frame, text="Reset Launches", height=3, command=lambda: clear_launches(True)).pack(side="left", fill="x", padx=1, expand=1)

        # Tutorial
        tutorial_frame = Frame(corruption_frame)
        tutorial_frame.pack(side="left", fill="both", expand=1)
        tutorial_notebook = ttk.Notebook(tutorial_frame)
        tutorial_notebook.pack(fill="both", expand=1)

        tutorial_intro_tab = Frame(None)
        tutorial_notebook.add(tutorial_intro_tab, text="Intro")
        Label(tutorial_intro_tab, text=INTRO_TEXT, wraplength=300).pack(fill="both", padx=2, pady=2)

        tutorial_start_tab = Frame(None)
        tutorial_notebook.add(tutorial_start_tab, text="Start")
        Label(tutorial_start_tab, text=START_TEXT, wraplength=300).pack(fill="both", padx=2, pady=2)

        tutorial_transition_tab = Frame(None)
        tutorial_notebook.add(tutorial_transition_tab, text="Transitions")
        Label(tutorial_transition_tab, text=TRANSITION_TEXT, wraplength=300).pack(fill="both", padx=2, pady=2)

        # Miscellaneous settings
        misc_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        misc_frame.pack(fill="x")

        misc_col_1 = Frame(misc_frame)
        misc_col_1.pack(fill="both", side="left", expand=1)

        wallpaper_toggle = Checkbutton(misc_col_1, text="Don't Cycle Wallpaper", variable=vars.corruption_wallpaper, cursor="question_arrow")
        wallpaper_toggle.pack(fill="x", side="top")
        CreateToolTip(
            wallpaper_toggle,
            "Prevents the wallpaper from cycling as you go through corruption levels, instead defaulting to a pack defined static one.",
        )

        theme_toggle = Checkbutton(misc_col_1, text="Don't Cycle Themes", variable=vars.corruption_themes, cursor="question_arrow")
        theme_toggle.pack(fill="x", side="top")
        CreateToolTip(
            theme_toggle,
            "Prevents the theme from cycling as you go through corruption levels, instead staying as "
            'the theme you set in the "General" tab of the config window.',
        )

        misc_col_2 = Frame(misc_frame)
        misc_col_2.pack(fill="both", side="left", expand=1)

        purity_toggle = Checkbutton(misc_col_2, text="Purity Mode", variable=vars.corruption_purity, cursor="question_arrow")
        purity_toggle.pack(fill="x", side="top")
        CreateToolTip(
            purity_toggle,
            "Starts corruption mode at the highest corruption level, then works backwards to level 1. "
            "Retains all of your other settings for this mode, if applicable.",
        )

        dev_toggle = Checkbutton(misc_col_2, text="Corruption Dev View", variable=vars.corruption_dev_mode, cursor="question_arrow")
        dev_toggle.pack(fill="x", side="top")
        CreateToolTip(
            dev_toggle,
            "Enables captions on popups that show various info.\n\n Mood: the mood in which the popup belongs to\n"
            "Valid Level: the corruption levels in which the popup spawns\nCurrent Level: the current corruption level\n\n"
            "Additionally, this also enables extra print logs in debug.py, allowing you to see what the corruption is currently doing.",
        )

        # Corruption path
        corruption_path_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        corruption_path_frame.pack(fill="x")

        Label(corruption_path_frame, text="--CORRUPTION PATH--").pack(pady=1, fill="x", side="top")

        path_tree_frame = Frame(corruption_path_frame)
        path_tree_frame.pack(fill="both", side="left", expand=1)

        path_tree = ttk.Treeview(path_tree_frame, height=6, show="headings", columns=("level", "moods", "wallpaper", "config"))
        path_tree.heading("level", text="LEVEL")
        path_tree.column("level", anchor="center", stretch=False, width=40)
        path_tree.heading("moods", text="MOODS")
        path_tree.column("moods", anchor="w", stretch=True)
        path_tree.heading("wallpaper", text="WALLPAPER")
        path_tree.column("wallpaper", anchor="w", stretch=True)
        path_tree.heading("config", text="CONFIG", anchor="w")
        path_tree.column("config", anchor="w", stretch=True)

        path_scrollbar_x = ttk.Scrollbar(path_tree_frame, orient="horizontal", command=path_tree.xview)
        path_scrollbar_y = ttk.Scrollbar(corruption_path_frame, orient="vertical", command=path_tree.yview)
        path_tree.configure(yscroll=path_scrollbar_y.set, xscroll=path_scrollbar_x.set)

        # Pack order is important
        path_scrollbar_x.pack(side="bottom", fill="x")
        path_tree.pack(side="left", fill="both", expand=1)
        path_scrollbar_y.pack(side="left", fill="y")

        for i, level in enumerate(pack.corruption_levels):
            path_tree.insert("", "end", values=[i + 1, str(list(level.moods)), level.wallpaper, level.config])

        tutorial_start_group = [
            start_frame,
            corruption_toggle,
            full_permission_toggle,
            recommended_settings_button,
            misc_frame,
            misc_col_1,
            wallpaper_toggle,
            theme_toggle,
            misc_col_2,
            purity_toggle,
            dev_toggle,
        ]

        tutorial_transition_group = [
            transition_frame,
            fade_frame,
            fade_selection_frame,
            fade_dropdown,
            fade_description,
            trigger_frame,
            trigger_selection_frame,
            trigger_dropdown,
            trigger_description,
            level_time_scale,
            level_time_manual,
            level_popups_scale,
            level_popups_manual,
            level_launches_scale,
            level_launches_manual,
        ]

        def fade_helper(key):
            if key == "Normal":
                fade_description.configure(text="Gradually transitions between corruption levels.")
                fade_image.configure(image=fade_normal_image)
            if key == "Abrupt":
                fade_description.configure(text="Immediately switches to new level upon timer completion.")
                fade_image.configure(image=fade_abrupt_image)

        def trigger_helper(key, tutorial_mode):
            if key == "Timed":
                trigger_description.configure(text="Transitions based on time elapsed in current session.")
                if tutorial_mode:
                    set_widget_states_with_colors(True, level_time_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, level_popup_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, level_launch_group, "lime green", "forest green")
                else:
                    set_widget_states(True, level_time_group)
                    set_widget_states(False, level_popup_group)
                    set_widget_states(False, level_launch_group)
            if key == "Popup":
                trigger_description.configure(text="Transitions based on number of popups in current session.")
                if tutorial_mode:
                    set_widget_states_with_colors(False, level_time_group, "lime green", "forest green")
                    set_widget_states_with_colors(True, level_popup_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, level_launch_group, "lime green", "forest green")
                else:
                    set_widget_states(False, level_time_group)
                    set_widget_states(True, level_popup_group)
                    set_widget_states(False, level_launch_group)
            if key == "Launch":
                trigger_description.configure(text="Transitions based on number of Edgeware launches.")
                if tutorial_mode:
                    set_widget_states_with_colors(False, level_time_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, level_popup_group, "lime green", "forest green")
                    set_widget_states_with_colors(True, level_launch_group, "lime green", "forest green")
                else:
                    set_widget_states(False, level_time_group)
                    set_widget_states(False, level_popup_group)
                    set_widget_states(True, level_launch_group)

        def corruption_tutorial_helper(event):
            tab = event.widget.tab("current")["text"]
            config["themeType"].strip()
            if tab == "Start":
                set_widget_states_with_colors(True, tutorial_start_group, "lime green", "forest green")
                set_widget_states(True, tutorial_transition_group)
                trigger_helper(vars.corruption_trigger.get(), False)
            elif tab == "Transitions":
                set_widget_states_with_colors(True, tutorial_transition_group, "lime green", "forest green")
                set_widget_states(True, tutorial_start_group)
                trigger_helper(vars.corruption_trigger.get(), True)
            else:
                set_widget_states(True, tutorial_start_group)
                set_widget_states(True, tutorial_transition_group)
                trigger_helper(vars.corruption_trigger.get(), False)
            set_widget_states(os.path.isfile(pack.paths.corruption), start_group)

        tutorial_notebook.bind("<<NotebookTabChanged>>", corruption_tutorial_helper)

        fade_helper(vars.corruption_fade.get())
        trigger_helper(vars.corruption_trigger.get(), False)
        set_widget_states(os.path.isfile(pack.paths.corruption), start_group)
