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

from config_window.utils import (
    assign,
    clear_launches,
    config,
    pack_preset,
    set_widget_states,
    set_widget_states_with_colors,
)
from config_window.vars import Vars
from pack import Pack
from paths import Assets
from PIL import ImageTk
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

INTRO_TEXT = "Welcome to the Corruption tab!\n\n Normally I'd put tutorials and help like this elsewhere, but I realize that this is probably the most complex and in-depth feature to be added to EdgeWare. Don't worry, we'll work through it together!\n\nEach tab will go over a feature of corruption, while also highlighting where the settings are for reference. Any additional details not covered here can be found in the \"About\" tab!"
START_TEXT = 'To start corruption mode, you can use these settings in the top left to turn it on. If turning it on is greyed out, it means the current pack does not support corruption! Down below are more toggle settings for fine-tuning corruption to work how you want it.\n\n Remember, for any of these settings, if your mouse turns into a "question mark" while hovering over it, you can stay hovered to view a tooltip on what the setting does!'
TRANSITION_TEXT = "Transitions are how each corruption level fades into eachother. While running corruption mode, the current level and next level are accessed simultaneously to blend the two together. You can choose the blending modes with the top option, and how edgeware transitions from one corruption level to the next with the bottom option. The visualizer image is purely to help understand how the transitions work, with the two colours representing both accessed levels. The sliders below fine-tune how long each level will last, so for a rough estimation on how long full corruption will take, you can multiply the active slider by the number of levels."


class CorruptionModeTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, pack: Pack):
        super().__init__()

        ctime_group = []
        cpopup_group = []
        claunch_group = []
        ctutorialstart_group = []
        ctutorialtransition_group = []

        corruptionFrame = Frame(self.viewPort)

        corruptionSettingsFrame = Frame(corruptionFrame)
        corruptionSubFrame1 = Frame(corruptionSettingsFrame)

        corruptionStartFrame = Frame(corruptionSubFrame1, borderwidth=5, relief=RAISED)

        corruptionEnabled_group = []

        corruptionToggle = Checkbutton(corruptionStartFrame, text="Turn on Corruption", variable=vars.corruption_mode, cursor="question_arrow")
        corruptionFullToggle = Checkbutton(corruptionStartFrame, text="Full Permissions Mode", variable=vars.corruption_full, cursor="question_arrow")
        corruptionRecommendedToggle = Button(
            corruptionStartFrame,
            text="Recommended Settings",
            cursor="question_arrow",
            height=2,
            command=lambda: pack_preset(pack, vars, "corruption", vars.preset_danger.get()),
        )
        corruptionEnabled_group.append(corruptionToggle)
        ctutorialstart_group.append(corruptionStartFrame)
        ctutorialstart_group.append(corruptionToggle)
        ctutorialstart_group.append(corruptionFullToggle)
        ctutorialstart_group.append(corruptionRecommendedToggle)

        corruptionFrame.pack(fill="x")
        corruptionSettingsFrame.pack(fill="x", side="left")
        corruptionSubFrame1.pack(fill="both", side="top")
        corruptionStartFrame.pack(fill="both", side="left")

        corruptionToggle.pack(fill="x", expand=1)
        corruptionFullToggle.pack(fill="x", expand=1)
        corruptionRecommendedToggle.pack(fill="x", padx=2, pady=2)

        CreateToolTip(
            corruptionToggle,
            "Corruption Mode gradually makes the pack more depraved, by slowly toggling on previously hidden"
            " content. Or at least that's the idea, pack creators can do whatever they want with it.\n\n"
            "Corruption uses the 'mood' feature, which must be supported with a corruption.json file in the resource"
            ' folder. Over time moods will "unlock", leading to new things you haven\'t seen before the longer you use'
            ' EdgeWare.\n\nFor more information, check out the "About" tab. \n\nNOTE: currently not implemented! Holy god I hope I remember to remove this notice later!',
        )
        CreateToolTip(corruptionFullToggle, "This setting allows corruption mode to change config settings as it goes through corruption levels.")
        CreateToolTip(
            corruptionRecommendedToggle,
            'Pack creators can set "default corruption settings" for their pack, to give'
            " users a more designed and consistent experience. This setting turns those on (if they exist)."
            '\n\nSidenote: this will load configurations similarly to the option in the "Pack Info" tab, however this one will only load corruption-specific settings.',
        )

        corruptionFadeFrame = Frame(corruptionSubFrame1, borderwidth=5, relief=RAISED)
        fadeInfoFrame = Frame(corruptionFadeFrame)
        fadeSubInfo = Frame(fadeInfoFrame)
        triggerInfoFrame = Frame(corruptionFadeFrame)
        triggerSubInfo = Frame(triggerInfoFrame)

        fade_types = ["Normal", "Abrupt"]
        fadeDropdown = OptionMenu(fadeSubInfo, vars.corruption_fade, *fade_types, command=lambda key: fade_helper(key))
        fadeDropdown.configure(width=9, highlightthickness=0)
        fadeDescription = Label(fadeInfoFrame, text="Error loading fade description!", borderwidth=2, relief=GROOVE, wraplength=150)
        fadeDescription.configure(height=3, width=22)
        fadeImageNormal = ImageTk.PhotoImage(file=Assets.CORRUPTION_DEFAULT)
        fadeImageAbrupt = ImageTk.PhotoImage(file=Assets.CORRUPTION_ABRUPT)
        fadeImageContainer = Label(fadeSubInfo, image=fadeImageNormal, borderwidth=2, relief=GROOVE)
        trigger_types = ["Timed", "Popup", "Launch"]
        triggerDropdown = OptionMenu(triggerSubInfo, vars.corruption_trigger, *trigger_types, command=lambda key: trigger_helper(key, False))
        triggerDropdown.configure(width=9, highlightthickness=0)
        triggerDescription = Label(triggerInfoFrame, text="Error loading trigger description!", borderwidth=2, relief=GROOVE, wraplength=150)
        triggerDescription.configure(height=3, width=22)

        ctutorialtransition_group.append(corruptionFadeFrame)
        ctutorialtransition_group.append(fadeInfoFrame)
        ctutorialtransition_group.append(fadeSubInfo)
        ctutorialtransition_group.append(triggerInfoFrame)
        ctutorialtransition_group.append(triggerSubInfo)
        ctutorialtransition_group.append(fadeDropdown)
        ctutorialtransition_group.append(fadeDescription)
        ctutorialtransition_group.append(triggerDropdown)
        ctutorialtransition_group.append(triggerDescription)

        corruptionFadeFrame.pack(fill="both", side="left")
        fadeInfoFrame.pack(side="top", fill="both", pady=1)
        fadeSubInfo.pack(side="left", fill="x")
        fadeDropdown.pack(side="top")
        fadeImageContainer.pack(side="top")
        fadeDescription.pack(side="left", fill="y", padx=3, ipadx=2, ipady=2)
        triggerInfoFrame.pack(side="top", fill="both", pady=1)
        triggerSubInfo.pack(side="left", fill="x")
        triggerDropdown.pack(side="top")
        triggerDescription.pack(side="left", fill="y", padx=3, ipadx=2, ipady=2)

        # -Timer-

        corruptionTimeFrame = Frame(corruptionSettingsFrame)
        corruptionTimeFrame.pack(fill="x", side="top")
        cTimerFrame = Frame(corruptionTimeFrame)
        corruptionTimerButton = Button(
            cTimerFrame,
            text="Manual time...",
            command=lambda: assign(vars.corruption_time, simpledialog.askinteger("Manual Level Time (sec)", prompt="[5-1800]: ")),
        )
        corruptionTimerScale = Scale(cTimerFrame, label="Level Time", variable=vars.corruption_time, orient="horizontal", from_=5, to=1800)
        cPopupsFrame = Frame(corruptionTimeFrame)
        corruptionPopupsButton = Button(
            cPopupsFrame,
            text="Manual popups...",
            command=lambda: assign(vars.corruption_popups, simpledialog.askinteger("Manual Level Popups (per transition)", prompt="[1-100]: ")),
        )
        corruptionPopupsScale = Scale(cPopupsFrame, label="Level Popups", variable=vars.corruption_popups, orient="horizontal", from_=1, to=100)
        cLaunchesFrame = Frame(corruptionTimeFrame)
        corruptionLaunchesButton = Button(
            cLaunchesFrame,
            text="Manual launches...",
            command=lambda: assign(vars.corruption_launches, simpledialog.askinteger("Manual Level Launches (per transition)", prompt="[2-31]: ")),
        )
        corruptionLaunchesScale = Scale(cLaunchesFrame, label="Level Launches", variable=vars.corruption_launches, orient="horizontal", from_=2, to=31)
        cOtherTimerFrame = Frame(corruptionTimeFrame)
        clearLaunchesButton = Button(cOtherTimerFrame, text="Reset Launches", height=3, command=lambda: clear_launches(True))

        ctutorialtransition_group.append(corruptionTimerButton)
        ctutorialtransition_group.append(corruptionTimerScale)
        ctutorialtransition_group.append(corruptionPopupsButton)
        ctutorialtransition_group.append(corruptionPopupsScale)
        ctutorialtransition_group.append(corruptionLaunchesButton)
        ctutorialtransition_group.append(corruptionLaunchesScale)

        cTimerFrame.pack(side="left", fill="x", padx=1, expand=1)
        corruptionTimerScale.pack(fill="y")
        corruptionTimerButton.pack(fill="y")
        cPopupsFrame.pack(side="left", fill="x", padx=1, expand=1)
        corruptionPopupsScale.pack(fill="y")
        corruptionPopupsButton.pack(fill="y")
        cLaunchesFrame.pack(side="left", fill="x", padx=1, expand=1)
        corruptionLaunchesScale.pack(fill="y")
        corruptionLaunchesButton.pack(fill="y")
        cOtherTimerFrame.pack(side="left", fill="x", padx=1, expand=1)
        clearLaunchesButton.pack()

        ctime_group.append(corruptionTimerButton)
        ctime_group.append(corruptionTimerScale)
        cpopup_group.append(corruptionPopupsButton)
        cpopup_group.append(corruptionPopupsScale)
        claunch_group.append(corruptionLaunchesButton)
        claunch_group.append(corruptionLaunchesScale)

        def fade_helper(key):
            if key == "Normal":
                fadeDescription.configure(text="Gradually transitions between corruption levels.")
                fadeImageContainer.configure(image=fadeImageNormal)
            if key == "Abrupt":
                fadeDescription.configure(text="Immediately switches to new level upon timer completion.")
                fadeImageContainer.configure(image=fadeImageAbrupt)

        def trigger_helper(key, tutorialMode):
            if key == "Timed":
                triggerDescription.configure(text="Transitions based on time elapsed in current session.")
                if tutorialMode:
                    set_widget_states_with_colors(True, ctime_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, cpopup_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, claunch_group, "lime green", "forest green")
                else:
                    set_widget_states(True, ctime_group)
                    set_widget_states(False, cpopup_group)
                    set_widget_states(False, claunch_group)
            if key == "Popup":
                triggerDescription.configure(text="Transitions based on number of popups in current session.")
                if tutorialMode:
                    set_widget_states_with_colors(False, ctime_group, "lime green", "forest green")
                    set_widget_states_with_colors(True, cpopup_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, claunch_group, "lime green", "forest green")
                else:
                    set_widget_states(False, ctime_group)
                    set_widget_states(True, cpopup_group)
                    set_widget_states(False, claunch_group)
            if key == "Launch":
                triggerDescription.configure(text="Transitions based on number of EdgeWare launches.")
                if tutorialMode:
                    set_widget_states_with_colors(False, ctime_group, "lime green", "forest green")
                    set_widget_states_with_colors(False, cpopup_group, "lime green", "forest green")
                    set_widget_states_with_colors(True, claunch_group, "lime green", "forest green")
                else:
                    set_widget_states(False, ctime_group)
                    set_widget_states(False, cpopup_group)
                    set_widget_states(True, claunch_group)

        # -Tutorial-

        corruptionTutorialFrame = Frame(corruptionFrame)
        corruptionTabMaster = ttk.Notebook(corruptionTutorialFrame)
        cTabIntro = Frame(None)
        cTabStart = Frame(None)
        cTabTransitions = Frame(None)
        corruptionTabMaster.add(cTabIntro, text="Intro")
        corruptionTabMaster.add(cTabStart, text="Start")
        corruptionTabMaster.add(cTabTransitions, text="Transitions")

        corruptionTutorialFrame.pack(side="left", fill="both", expand=1)
        corruptionTabMaster.pack(fill="both", expand=1)

        corruptionIntroBody = Label(cTabIntro, text=INTRO_TEXT, wraplength=300)
        corruptionStartBody = Label(cTabStart, text=START_TEXT, wraplength=300)
        corruptionTransitionBody = Label(cTabTransitions, text=TRANSITION_TEXT, wraplength=300)

        corruptionIntroBody.pack(fill="both", padx=2, pady=2)
        corruptionStartBody.pack(fill="both", padx=2, pady=2)
        corruptionTransitionBody.pack(fill="both", padx=2, pady=2)

        # -Additional Settings-

        corruptionAdditionalFrame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        corruptionAddSub1 = Frame(corruptionAdditionalFrame)
        corruptionAddSub2 = Frame(corruptionAdditionalFrame)
        corruptionAddSub3 = Frame(corruptionAdditionalFrame)

        corruptionWallpaperToggle = Checkbutton(corruptionAddSub1, text="Don't Cycle Wallpaper", variable=vars.corruption_wallpaper, cursor="question_arrow")
        corruptionThemeToggle = Checkbutton(corruptionAddSub1, text="Don't Cycle Themes", variable=vars.corruption_themes, cursor="question_arrow")
        corruptionPurityToggle = Checkbutton(corruptionAddSub2, text="Purity Mode", variable=vars.corruption_purity, cursor="question_arrow")
        corruptionDevToggle = Checkbutton(corruptionAddSub2, text="Corruption Dev View", variable=vars.corruption_dev_mode, cursor="question_arrow")

        ctutorialstart_group.append(corruptionAdditionalFrame)
        ctutorialstart_group.append(corruptionAddSub1)
        ctutorialstart_group.append(corruptionAddSub2)
        ctutorialstart_group.append(corruptionAddSub3)
        ctutorialstart_group.append(corruptionWallpaperToggle)
        ctutorialstart_group.append(corruptionThemeToggle)
        ctutorialstart_group.append(corruptionPurityToggle)
        ctutorialstart_group.append(corruptionDevToggle)

        corruptionAdditionalFrame.pack(fill="x")
        corruptionAddSub1.pack(fill="both", side="left", expand=1)
        corruptionAddSub2.pack(fill="both", side="left", expand=1)
        corruptionAddSub3.pack(fill="both", side="left", expand=1)

        corruptionWallpaperToggle.pack(fill="x", side="top")
        corruptionThemeToggle.pack(fill="x", side="top")
        corruptionPurityToggle.pack(fill="x", side="top")
        corruptionDevToggle.pack(fill="x", side="top")

        CreateToolTip(
            corruptionWallpaperToggle,
            "Prevents the wallpaper from cycling as you go through corruption levels, instead defaulting to a pack defined static one.",
        )
        CreateToolTip(
            corruptionThemeToggle,
            "Prevents the theme from cycling as you go through corruption levels, instead staying as "
            'the theme you set in the "General" tab of the config window.',
        )
        CreateToolTip(
            corruptionPurityToggle,
            "Starts corruption mode at the highest corruption level, then works backwards to level 1. "
            "Retains all of your other settings for this mode, if applicable.",
        )
        CreateToolTip(
            corruptionDevToggle,
            "Enables captions on popups that show various info.\n\n Mood: the mood in which the popup belongs to\n"
            "Valid Level: the corruption levels in which the popup spawns\nCurrent Level: the current corruption level\n\n"
            "Additionally, this also enables extra print logs in debug.py, allowing you to see what the corruption is currently doing.",
        )

        # -Info-

        corruptionPathFrame = Frame(self.viewPort, borderwidth=5, relief=RAISED)

        corruptionLabel = "--CORRUPTION PATH--"
        corruptionPathLabel = Label(corruptionPathFrame, text=corruptionLabel)

        pathInnerFrame = Frame(corruptionPathFrame)
        pathTree = ttk.Treeview(pathInnerFrame, height=6, show="headings", columns=("level", "moods"))
        pathScrollbarY = ttk.Scrollbar(corruptionPathFrame, orient="vertical", command=pathTree.yview)
        pathScrollbarX = ttk.Scrollbar(pathInnerFrame, orient="horizontal", command=pathTree.xview)
        pathTree.configure(yscroll=pathScrollbarY.set, xscroll=pathScrollbarX.set)

        pathTree.heading("level", text="LEVEL")
        pathTree.column("level", width=40, stretch=False, anchor="center")
        pathTree.heading("moods", text="MOODS", anchor="w")

        lineWidth = 0
        # if os.path.isfile(pack.CORRUPTION):
        #     try:
        #         with open(pack.CORRUPTION, 'r') as f:
        #             l = json.loads(f.read())
        #             for key in list(l):
        #                 if key == "moods":
        #                     for level, i in l[key]:
        #                         corruptionList.append((f'{level}', str(level.keys()).strip('[]')))
        #
        #     except Exception as e:
        #         logging.warning(f'error in corruption.json. Aborting preview load. {e}')
        #     try:
        #         for level in corruptionList:
        #             if sum(len(i) for i in level) > lineWidth:
        #                 lineWidth = sum(len(i) for i in level)
        #             pathTree.insert('', 'end', values=level)
        #     except Exception as e:
        #         logging.warning(f'error in loading corruption treeview. {e}')

        # just doing a magic number, long story short treeview is butts for horizontal scrolling
        pathTree.column("moods", anchor="w", stretch=True, minwidth=int(lineWidth * 5.5))

        corruptionPathFrame.pack(fill="x")
        corruptionPathLabel.pack(pady=1, fill="x", side="top")
        pathInnerFrame.pack(fill="both", side="left", expand=1)
        pathScrollbarX.pack(side="bottom", fill="x")
        pathTree.pack(side="left", fill="both", expand=1)
        pathScrollbarY.pack(side="left", fill="y")

        def corruptionTutorialHelper(event):
            tab = event.widget.tab("current")["text"]
            config["themeType"].strip()
            if tab == "Start":
                set_widget_states_with_colors(True, ctutorialstart_group, "lime green", "forest green")
                set_widget_states(True, ctutorialtransition_group)
                trigger_helper(vars.corruption_trigger.get(), False)
            elif tab == "Transitions":
                set_widget_states_with_colors(True, ctutorialtransition_group, "lime green", "forest green")
                set_widget_states(True, ctutorialstart_group)
                trigger_helper(vars.corruption_trigger.get(), True)
            else:
                set_widget_states(True, ctutorialstart_group)
                set_widget_states(True, ctutorialtransition_group)
                trigger_helper(vars.corruption_trigger.get(), False)
            set_widget_states(os.path.isfile(pack.paths.corruption), corruptionEnabled_group)

        corruptionTabMaster.bind("<<NotebookTabChanged>>", corruptionTutorialHelper)

        fade_helper(vars.corruption_fade.get())
        trigger_helper(vars.corruption_trigger.get(), False)
        set_widget_states(os.path.isfile(pack.paths.corruption), corruptionEnabled_group)
