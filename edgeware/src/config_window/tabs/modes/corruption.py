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
from widgets.config_widgets import (
    SettingsScale,
    SettingsToggle,
    Section,
    Row
)

INTRO_TEXT = "Corruption is a highly specialized mode that packs have to explicitly support. When corruption is enabled, it will turn off and on moods based on a trigger set down below. For example, a pack might start off with only vanilla moods but get more fetish-oriented every 10 popups opened.\n\n\"Full Permissions Mode\" can be enabled to allow the pack to change Edgeware++ settings on top of also changing moods. While this allows for very unique packs with lots of changes, this can also be potentially dangerous. Only turn it on for packs you trust!"
TRIGGER_TEXT = 'Triggers are the goals that define how corruption changes over time. Whenever the selected condition is reached, they tell Edgeware++ to advance to the next \"corruption level\". Each setting is per level transition, *not* the total time it takes for corruption to finish.\n\nFor example, let\'s say you set the trigger type to \"timed\" and the time to 60 seconds. That means that every 60 seconds you run Edgeware++ the corruption level will increase, changing the current moods available.\n\nAdditionally, you can change the behaviour of how Edgeware++ transitions from level to level. For example, \"Abrupt\" will immediately change to the next moods when the trigger condition is met, whereas \"Normal\" will gradually increase the chance of pulling media from the next corruption level up until the trigger condition.'

class CorruptionModeTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, pack: Pack) -> None:
        super().__init__()

        #Start
        corruption_start_section = Section("Corruption", INTRO_TEXT, self.viewPort)
        corruption_start_section.pack()
        corruption_start_row = Row(corruption_start_section)
        corruption_start_row.pack()
        corruption_toggle = SettingsToggle("Turn on Corruption", corruption_start_row, variable=vars.corruption_mode, cursor="question_arrow")
        corruption_toggle.pack()
        CreateToolTip(
            corruption_toggle,
            "Corruption Mode gradually makes the pack more depraved, by slowly toggling on previously hidden"
            " content. Or at least that's the idea, pack creators can do whatever they want with it.\n\n"
            "Corruption uses the 'mood' feature, which must be supported with a corruption.json file in the resource"
            ' folder. Over time moods will "unlock", leading to new things you haven\'t seen before the longer you use'
            ' Edgeware. For more information, check out the \"Tutorial\" tab.',
        )
        full_permission_toggle = SettingsToggle("Full Permissions Mode", corruption_start_row, variable=vars.corruption_full, cursor="question_arrow")
        full_permission_toggle.pack()
        CreateToolTip(
            full_permission_toggle,
            "This setting allows corruption mode to change config settings as it goes through corruption levels.\n\nThere are certain settings that can\'t be changed, but usually because they\'d either do nothing or serve no purpose... That means that a lot of \"dangerous settings\" are still fair game! Please only enable this for packs you trust!\n\nIf you are a pack creator or just want to see what settings don\'t work with this mode, you can view the full blacklist in \"src\\features\\corruption_config.py\" (open with your text editor of choice!)"
        )

        #Triggers
        corruption_triggers_section = Section("Triggers", TRIGGER_TEXT, self.viewPort)
        corruption_triggers_section.pack()

        select_trigger_row = Row(corruption_triggers_section)
        select_trigger_row.pack()
        trigger_frame = Frame(select_trigger_row, borderwidth=1, relief="groove")
        trigger_frame.pack(pady=4, ipady=4, side="left", expand=True)

        trigger_selection_frame = Frame(trigger_frame)
        trigger_selection_frame.pack(side="left", fill="x")
        trigger_types = ["Timed", "Popup", "Launch"]
        trigger_dropdown = OptionMenu(trigger_selection_frame, vars.corruption_trigger, *trigger_types, command=lambda key: trigger_helper(key, False))
        trigger_dropdown.configure(width=9, highlightthickness=0)
        trigger_dropdown.pack(side="top", padx=4)

        trigger_description = Label(trigger_frame, text="Error loading trigger description!", wraplength=150)
        trigger_description.configure(height=3, width=22)
        trigger_description.pack(side="left", fill="y", ipadx=4)

        transition_frame = Frame(select_trigger_row, borderwidth=1, relief="groove")
        transition_frame.pack(pady=4, ipady=4, side="left", expand=True)

        fade_frame = Frame(transition_frame)
        fade_frame.pack(side="top", fill="both", pady=1)

        fade_selection_frame = Frame(fade_frame)
        fade_selection_frame.pack(side="left", fill="x")
        fade_types = ["Normal", "Abrupt"]
        fade_dropdown = OptionMenu(fade_selection_frame, vars.corruption_fade, *fade_types, command=lambda key: fade_helper(key))
        fade_dropdown.configure(width=9, highlightthickness=0)
        fade_dropdown.pack(side="top", padx=4)
        fade_normal_image = ImageTk.PhotoImage(file=Assets.CORRUPTION_DEFAULT)
        fade_abrupt_image = ImageTk.PhotoImage(file=Assets.CORRUPTION_ABRUPT)
        fade_image = Label(fade_selection_frame, image=fade_normal_image, borderwidth=2, relief=GROOVE)
        fade_image.pack(side="top", padx=4)

        fade_description = Label(fade_frame, text="Error loading fade description!", wraplength=150)
        fade_description.configure(height=3, width=22)
        fade_description.pack(side="left", fill="y", ipadx=4)

        corruption_triggers_row = Row(corruption_triggers_section)
        corruption_triggers_row.pack()
        corruption_time_scale = SettingsScale(corruption_triggers_row, "Level Time (seconds)", vars.corruption_time, 5, 1800)
        corruption_time_scale.pack()
        level_time_group = [corruption_time_scale]
        corruption_popup_scale = SettingsScale(corruption_triggers_row, "Level Popups", vars.corruption_popups, 1, 100)
        corruption_popup_scale.pack()
        level_popup_group = [corruption_popup_scale]
        corruption_launches_scale = SettingsScale(corruption_triggers_row, "Level Launches", vars.corruption_launches, 2, 31)
        corruption_launches_scale.pack()
        level_launch_group = [corruption_launches_scale]

        corruption_frame = Frame(self.viewPort)
        corruption_frame.pack(fill="x")

        corruption_settings_frame = Frame(corruption_frame)
        corruption_settings_frame.pack(fill="x", side="left")

        basic_settings_frame = Frame(corruption_settings_frame)
        basic_settings_frame.pack(fill="both", side="top")

        # Start
        start_frame = Frame(basic_settings_frame, borderwidth=5, relief=RAISED)
        start_frame.pack(fill="both", side="left")
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

        # Level progress
        level_frame = Frame(corruption_settings_frame)
        level_frame.pack(fill="x", side="top")

        Button(level_frame, text="Reset Launches", height=3, command=lambda: clear_launches(True)).pack(side="left", fill="x", padx=1, expand=1)

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

        fade_helper(vars.corruption_fade.get())
        trigger_helper(vars.corruption_trigger.get(), False)
        set_widget_states(os.path.isfile(pack.paths.corruption), start_group)
