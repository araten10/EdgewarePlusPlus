import ast
import json
import logging
import os
from pathlib import Path
from tkinter import (
    GROOVE,
    RAISED,
    Button,
    Canvas,
    Checkbutton,
    Frame,
    Label,
    Message,
    OptionMenu,
    Scale,
    Text,
    Tk,
    font,
    messagebox,
    simpledialog,
    ttk,
)

from config_window.annoyance.audio_video import AudioVideoTab
from config_window.annoyance.captions import CaptionsTab
from config_window.annoyance.dangerous_settings import DangerousSettingsTab
from config_window.annoyance.moods import MoodsTab
from config_window.annoyance.popup import PopupTab
from config_window.annoyance.wallpaper import WallpaperTab
from config_window.general.booru import BooruTab
from config_window.general.default_file import DefaultFileTab
from config_window.general.file import FileTab
from config_window.general.info import InfoTab
from config_window.general.start import StartTab
from config_window.modes.basic import BasicModesTab
from config_window.modes.dangerous_modes import DangerousModesTab
from config_window.modes.hibernate import HibernateModeTab
from config_window.troubleshooting import TroubleshootingTab
from config_window.utils import (
    all_children,
    assign,
    clear_launches,
    config,
    export_resource,
    get_live_version,
    import_resource,
    pack_preset,
    set_widget_states,
    set_widget_states_with_colors,
    write_save,
)
from config_window.vars import Vars
from pack import Pack
from pack.data import UniversalSet
from paths import DEFAULT_PACK_PATH, Assets, CustomAssets, Data
from PIL import ImageTk
from settings import load_default_config
from widgets.tooltip import CreateToolTip

PATH = Path(__file__).parent

config["wallpaperDat"] = ast.literal_eval(config["wallpaperDat"])
default_config = load_default_config()
pack = Pack(Data.PACKS / config["packPath"] if config["packPath"] else DEFAULT_PACK_PATH)


pil_logger = logging.getLogger("PIL")
pil_logger.setLevel(logging.INFO)

# text for the about tab
ANNOYANCE_TEXT = 'The "Annoyance" section consists of the 5 main configurable settings of Edgeware:\nDelay\nPopup Frequency\nWebsite Frequency\nAudio Frequency\nPromptFrequency\n\nEach is fairly self explanatory, but will still be expounded upon in this section. Delay is the forced time delay between each tick of the "clock" for Edgeware. The longer it is, the slower things will happen. Popup frequency is the percent chance that a randomly selected popup will appear on any given tick of the clock, and similarly for the rest, website being the probability of opening a website or video from /resource/vid/, audio for playing a file from /resource/aud/, and prompt for a typing prompt to pop up.\n\nThese values can be set by adjusting the bars, or by clicking the button beneath each respective slider, which will allow you to type in an explicit number instead of searching for it on the scrollbar.\n\nIn order to disable any feature, lower its probability to 0, to ensure that you\'ll be getting as much of any feature as possible, turn it up to 100.\nThe popup setting "Mitosis mode" changes how popups are displayed. Instead of popping up based on the timer, the program create a single popup when it starts. When the submit button on ANY popup is clicked to close it, a number of popups will open up in its place, as given by the "Mitosis Strength" setting.\n\nPopup timeout will result in popups timing out and closing after a certain number of seconds.'
DRIVE_TEXT = 'The "Drive" portion of Edgeware has three features: fill drive, replace images, and Booru downloader.\n\n"Fill Drive" does exactly what it says: it attempts to fill your hard drive with as much porn from /resource/img/ as possible. It does, however, have some restrictions. It will (should) not place ANY images into folders that start with a "." or have their names listed in the folder name blacklist.\nIt will also ONLY place images into the User folder and its subfolders.\nFill drive has one modifier, which is its own forced delay. Because it runs with between 1 and 8 threads at any given time, when unchecked it can fill your drive VERY quickly. To ensure that you get that nice slow fill, you can adjust the delay between each folder sweep it performs and the max number of threads.\n\n"Replace Images" is more complicated. Its searching is the exact same as fill drive, but instead of throwing images everywhere, it will seek out folders with large numbers of images (more than the threshold value) and when it finds one, it will replace ALL of the images with porn from /resource/img/. REMEMBER THAT IF YOU CARE ABOUT YOUR PHOTOS, AND THEY\'RE IN A FOLDER WITH MORE IMAGES THAN YOUR CHOSEN THRESHOLD VALUE, EITHER BACK THEM UP IN A ZIP OR SOMETHING OR DO. NOT. USE. THIS SETTING. I AM NOT RESPONSIBLE FOR YOUR OWN DECISION TO RUIN YOUR PHOTOS. Edgeware will attempt to backup any replaced images under /data/backups, but DO NOT RELY ON THIS FEATURE IN ANY CIRCUMSTANCE. ALWAYS BACKUP YOUR FILES YOURSELF.\n\nBooru downloader allows you to download new items from a Booru of your choice. For the booru name, ONLY the literal name is used, like "censored" or "blacked" instead of the full url. This is not case sensitive. Use the "Validate" button to ensure that downloading will be successful before running. For tagging, if you want to have multiple tags, they can be combined using "tag1+tag2+tag3" or if you want to add blacklist tags, type your tag and append a "+-blacklist_tag" after the desired tag.'
STARTUP_TEXT = 'Start on launch does exactly what it says it does and nothing more: it allows Edgeware to start itself whenever you start up and log into your PC.\n\nPlease note that the method used does NOT edit registry or schedule any tasks. The "lazy startup" method was used for both convenience of implementation and convenience of cleaning.\n\nIf you forget to turn off the "start on logon" setting before uninstalling, you will need to manually go to your Startup folder and remove "edgeware.bat".'
WALLPAPER_TEXT = "The Wallpaper section allows you to set up rotating wallpapers of your choice from any location, or auto import all images from the /resource/ folder (NOT /resource/img/ folder) to use as wallpapers.\n\nThe rotate timer is the amount of time the program will wait before rotating to another randomly selected wallpaper, and the rotate variation is the amount above or below that set value that can randomly be selected as the actual wait time."
HIBERNATE_TEXT = 'The Hibernate feature is an entirely different mode for Edgeware to operate in.\nInstead of constantly shoving popups, lewd websites, audio, and prompts in your face, hibernate starts quiet and waits for a random amount of time between its provided min and max before exploding with a rapid assortment of your chosen payloads. Once it finishes its barrage, it settles back down again for another random amount of time, ready to strike again when the time is right.\n\n\nThis feature is intend to be a much "calmer" way to use Edgeware; instead of explicitly using it to edge yourself or get off, it\'s supposed to lie in wait for you and perform bursts of self-sabotage to keep drawing you back to porn.\n\n In EdgeWare++, the hibernate function has been expanded with two key features: fix wallpaper and hibernate types. Fix wallpaper is fairly straightforward, it changes your wallpaper back to your panic wallpaper after hibernate is finished. Hibernate types are a bit more complicated, as each one changes the the way hibernate handles payloads. There is a short-form description next to the dropdown menu for quick reference, but you can check the about tab labelled "Hibernate Types" for a more detailed description of each type. Also, if you wish to trial out any of these types and don\'t want to wait, you can enable the "Toggle Tray Hibernate Skip" option in the troubleshooting tab to immediately skip to hibernate starting, on command.'
HIBERNATE_TYPE_TEXT = "Check the \"Hibernate\" about tab for more information on what this is and how it works.\n\nOriginal: The original hibernate type that came with base EdgeWare. Spawns a barrage of popups instantly, the max possible amount is based on your awaken activity.\n\nSpaced: Essentially runs EdgeWare normally, but over a brief period of time before ceasing generation of new popups. Because of this awaken activity isn't used, instead popup delay is looked at for frequency of popups.\n\nGlitch: Creates popups at random-ish intervals over a period of time. The total amount of popups spawned is based on the awaken activity. Perfect for those who want a 'virus-like' experience, or just something different every time.\n\nRamp: Similar to spaced, only the popup frequency gets faster and faster over the hibernate length. After reaching the max duration, it will spawn a number of popups equal to the awaken activity at a speed slightly faster than your popup delay. Best used with long hibernate length values and fairly short popup delay. (keep in mind that if the popup delay is too short though, popups can potentially not appear or lag behind)\n\nPump-Scare: Do you like haunted houses or scary movies? Don't you wish that instead of screamers and jumpscares, they had porn pop out at you instead? This is kind of like that. When hibernate is triggered a popup with audio will appear for around a second or two, then immediately disappear. This works best on packs with short, immediate audio files: old EdgeWare packs that contain half-hour long hypno files will likely not reach meaningful audio in time. Large audio files can also hamper effectiveness of the audio and lead to desync with the popup.\n\nChaos: Every time hibernate activates, it randomly selects any of the other hibernate modes."
CORRUPTION_TEXT = "This is a feature not currently implemented in the release version of EdgeWare. But it will be soon! Feel free to slide the sliders around and press some buttons. It currently won't do anything but sometimes just feels good to do."
ADVANCED_TEXT = 'The "Debug Config Edit" section is also something previously only accessible by directly editing the config.cfg file. It offers full and complete customization of all setting values without any limitations outside of variable typing.\n\n\nPlease use this feature with discretion, as any erroneous values will result in a complete deletion and regeneration of the config file from the default, and certain value ranges are likely to result in crashes or unexpected glitches in the program.\n\nOtherwise, the Troubleshooting tab is fairly self explanatory. All features here will hopefully help issues you might have while running EdgeWare. If you didn\'t already know, you can hover over any option that gives your cursor a "question mark sign" to get a more detailed description of what it does.'
THANK_AND_ABOUT_TEXT = "[NOTE: this is the thanks page from the original EdgeWare. I didn't want to replace/remove it and erase credit to the original creator! Sorry if this caused confusion!]\n\nThank you so much to all the fantastic artists who create and freely distribute the art that allows programs like this to exist, to all the people who helped me work through the various installation problems as we set the software up (especially early on), and honestly thank you to ALL of the people who are happily using Edgeware. \n\nIt truly makes me happy to know that my work is actually being put to good use by people who enjoy it. After all, at the end of the day that's really all I've ever really wanted, but figured was beyond reach of a stupid degreeless neet.\nI love you all <3\n\n\n\nIf you like my work, please feel free to help support my neet lifestyle by donating to $PetitTournesol on Cashapp; by no means are you obligated or expected to, but any and all donations are greatly appreciated!"

PLUSPLUS_TEXT = 'Thanks for taking the time to check out this extension on EdgeWare! However you found it, I appreciate that it interested you enough to give it a download.\n\nI am not an expert programmer by any means, so apologies if there are any bugs or errors in this version. My goal is to not do anything crazy ambitious like rewrite the entire program or fix up the backend, but rather just add on functionality that I thought could improve the base version. Because of this, i\'m hoping that compatability between those who use normal EdgeWare and those who use this version stays relatively stable. If you were given this version directly without a download link and are curious about development updates, you can find updates and links to the github @ twitter @ara10ten.\n\n Current changes:\n\n•Added a option under "misc" to enable/disable desktop icon generation.\n•Added options to cap the number of audio popups and video popups.\n•Added a chance slider for subliminals, and a max subliminals slider.\n•Added feature to change Startup Graphic and Icon per pack. (name the file(s) "loading_splash" and/or "icon.ico" in the resource folder)\n•Added feature to enable warnings for "Dangerous Settings".\n•Added hover tooltips on some things to make the program easier to understand.\n•Added troubleshooting tab under "advanced" with some settings to fix things for certain users.\n•Added feature to click anywhere on popup to close.\n•Made the EdgewareSetup.bat more clear with easier to read text. Hopefully if you\'re seeing this it all worked out!\n•Moved the import/export resources button to be visible on every page, because honestly they\'re pretty important\n•Added the "Pack Info" tab with lots of fun goodies and stats so you know what you\'re getting into with each pack.\n•Added a simplified error console in the "advanced" tab.\n•Overhauled Hibernate with a bunch of new modes and features\n•Added file tab with multiple file management settings\n•Added feature to enable or disable moods (feature in regular edgeware that went unused afaik)\n•Added corruption. What is it? Dont worry about it.\n•Added support to playing videos in VLC, enabling faster loading.\n•Added advanced caption settings to captions.json.\n•Added theme support with multiple themes to switch between.\n•Pack creators can now create a config preset for their pack.\n•Two new popup types, Subliminal Messages and Moving Popups, with help from /u/basicmo!\n•Experimental Linux support!'
PACKINFO_TEXT = 'The pack info section contains an overview for whatever pack is currently loaded.\n\nThe "Stats" tab allows you to see what features are included in the current pack (or if a pack is even loaded at all), but keep in mind all of these features have default fallbacks if they aren\'t included. It also lets you see a lot of fun stats relating to the pack, including almost everything you\'ll encounter while using EdgeWare. Keep in mind that certain things having "0" as a stat doesn\'t mean you can\'t use it, for example, having 0 subliminals uses the default spiral and having 0 images displays a very un-sexy circle.\n\nThe "Information" tab gets info on the pack from //resource//info.json, which is a new addition to EdgeWare++. This feature was added to allow pack creators to give the pack a formal name and description without having to worry about details being lost if transferred from person to person. Think of it like a readme. Also included in this section is the discord status info, which gives what your discord status will be set to if that setting is turned on, along with the image. As of time of writing (or if I forget to update this later), the image cannot be previewed as it is "hard coded" into EdgeWare\'s discord application and accessed through the API. As I am not the original creator of EdgeWare, and am not sure how to contact them, the best I could do is low-res screenshots or the name of each image. I chose the latter. Because of this hard-coding, the only person i\'ve run into so far who use these images is PetitTournesol themselves, but it should be noted that anyone can use them as long as they know what to add to the discord.dat file. This is partially the reason I left this information in.\n\nThe "Moods" tab is where you can access mood settings and previews for the current pack. The left table shows information for media (linking moods to images, videos, etc), captions, and prompts, while the "Corruption Path" area shows how these moods correlate to corruption levels.'
FILE_TEXT = 'The file tab is for all your file management needs, whether it be saving things, loading things, deleting things, or looking around in config folders. The Preset window has also been moved here to make more room for general options.\n\nThere are only two things that aren\'t very self explanatory: deleting logs and unique IDs.\n\nWhile deleting logs is fairly straightforward, it should be noted that it will not delete the log currently being written during the session, so the "total logs in folder" stat will always display as "1".\n\nUnique IDs are a feature to help assist with saving moods. In short, they are a generated identifier that is used when saving to a "moods json file", which is tapped into when selecting what moods you want to see in the "Pack Info" tab. Unique IDs are only used if the pack does not have a \'info.json\' file, otherwise the pack name is just used instead. If you are rapidly editing a pack without info.json and want EdgeWare++ to stop generating new mood files, there is an option to disable it in the troubleshooting tab.\n\n When manually editing mood config jsons, you don\'t need to worry about how the unique ID is generated- the file tab will tell you what to look for. If you are curious though, here is the exact formula:\n\nnum_images + num_audio + num_video + wallpaper(y/n) + loading_splash(y/n) + discord_status(y/n) + icon(y/n) + corruption(y/n)\n\nFor example:\nA pack with 268 images, 7 audio, 6 videos, has a wallpaper, doesn\'t have a custom loading splash, has a discord status, doesn\'t have a custom icon, and doesn\'t have a corruption file, would generate "26876wxdxx.json" in //moods//unnamed (mood files go in unnamed when using unique IDs)'

# corruption tutorial text
CINTRO_TEXT = "Welcome to the Corruption tab!\n\n Normally I'd put tutorials and help like this elsewhere, but I realize that this is probably the most complex and in-depth feature to be added to EdgeWare. Don't worry, we'll work through it together!\n\nEach tab will go over a feature of corruption, while also highlighting where the settings are for reference. Any additional details not covered here can be found in the \"About\" tab!"
CSTART_TEXT = 'To start corruption mode, you can use these settings in the top left to turn it on. If turning it on is greyed out, it means the current pack does not support corruption! Down below are more toggle settings for fine-tuning corruption to work how you want it.\n\n Remember, for any of these settings, if your mouse turns into a "question mark" while hovering over it, you can stay hovered to view a tooltip on what the setting does!'
CTRANSITION_TEXT = "Transitions are how each corruption level fades into eachother. While running corruption mode, the current level and next level are accessed simultaneously to blend the two together. You can choose the blending modes with the top option, and how edgeware transitions from one corruption level to the next with the bottom option. The visualizer image is purely to help understand how the transitions work, with the two colours representing both accessed levels. The sliders below fine-tune how long each level will last, so for a rough estimation on how long full corruption will take, you can multiply the active slider by the number of levels."

# Generate mood file if it doesn't exist or is invalid
if not pack.info.mood_file.is_file() or isinstance(pack.active_moods, UniversalSet):
    Data.MOODS.mkdir(parents=True, exist_ok=True)
    with open(pack.info.mood_file, "w+") as f:
        f.write(json.dumps({"active": list(map(lambda mood: mood.name, pack.index.moods))}))


class Config(Tk):
    def __init__(self):
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

        windowFont = font.nametofont("TkDefaultFont")
        title_font = font.Font(font="Default")
        title_font.configure(size=13)

        vars = Vars(config)

        # grouping for enable/disable
        ctime_group = []
        cpopup_group = []
        claunch_group = []
        ctutorialstart_group = []
        ctutorialtransition_group = []
        message_group = []

        local_version = default_config["versionplusplus"]
        live_version = get_live_version()

        # tab display code start
        notebook = ttk.Notebook(self)  # tab manager

        general_tab = ttk.Frame(notebook)
        notebook.add(general_tab, text="General")
        general_notebook = ttk.Notebook(general_tab)
        general_notebook.add(StartTab(vars, title_font, message_group, local_version, live_version), text="Start")  # startup screen, info and presets
        general_notebook.add(FileTab(vars, title_font, message_group, pack), text="File/Presets")  # file management tab
        general_notebook.add(InfoTab(vars, title_font, message_group, pack), text="Pack Info")  # pack information
        general_notebook.add(BooruTab(vars, title_font), text="Booru Downloader")  # tab for booru downloader
        general_notebook.add(DefaultFileTab(vars, message_group), text="Change Default Files")  # tab for changing default files

        annoyance_tab = ttk.Frame(notebook)
        notebook.add(annoyance_tab, text="Annoyance/Runtime")
        annoyance_notebook = ttk.Notebook(annoyance_tab)
        annoyance_notebook.add(PopupTab(vars, title_font, message_group), text="Popups")  # tab for popup settings
        annoyance_notebook.add(AudioVideoTab(vars, title_font, message_group), text="Audio/Video")  # tab for managing audio and video settings
        annoyance_notebook.add(CaptionsTab(vars, title_font, message_group), text="Captions")  # tab for caption settings
        annoyance_notebook.add(WallpaperTab(vars, message_group, pack), text="Wallpaper")  # tab for wallpaper rotation settings
        annoyance_notebook.add(MoodsTab(vars, title_font, message_group, pack), text="Moods")  # tab for mood settings
        annoyance_notebook.add(DangerousSettingsTab(vars, title_font, message_group), text="Dangerous Settings")  # tab for potentially dangerous settings

        modes_tab = ttk.Frame(notebook)
        notebook.add(modes_tab, text="Modes")
        modes_notebook = ttk.Notebook(modes_tab)
        modes_notebook.add(BasicModesTab(vars, title_font), text="Basic Modes")  # tab for basic popup modes
        modes_notebook.add(DangerousModesTab(vars, title_font), text="Dangerous Modes")  # tab for timer mode
        modes_notebook.add(HibernateModeTab(vars, title_font), text="Hibernate")  # tab for hibernate mode
        tabCorruption = ttk.Frame(None)  # tab for corruption mode

        notebook.add(TroubleshootingTab(vars, title_font), text="Troubleshooting")  # tab for miscellaneous settings with niche use cases
        tabInfo = ttk.Frame(None)  # info, github, version, about, etc.

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
        tabInfoExpound = ttk.Notebook(tabInfo, style="lefttab.TNotebook")  # additional subtabs for info on features

        tab_annoyance = ttk.Frame(None)
        tab_drive = ttk.Frame(None)
        tab_wallpaper = ttk.Frame(None)
        tab_launch = ttk.Frame(None)
        tab_hibernate = ttk.Frame(None)
        tab_hibernateType = ttk.Frame(None)
        tab_corruption = ttk.Frame(None)
        tab_advanced = ttk.Frame(None)
        tab_thanksAndAbout = ttk.Frame(None)
        tab_plusPlus = ttk.Frame(None)
        tab_packInfo = ttk.Frame(None)
        tab_file = ttk.Frame(None)

        resourceFrame = Frame(self)
        exportResourcesButton = Button(resourceFrame, text="Export Resource Pack", command=export_resource)
        importResourcesButton = Button(resourceFrame, text="Import Resource Pack", command=lambda: import_resource(self))
        saveExitButton = Button(self, text="Save & Exit", command=lambda: write_save(vars, True))

        # --------------------------------------------------------- #
        # ========================================================= #
        # ===================={BEGIN TABS HERE}==================== #
        # ========================================================= #
        # --------------------------------------------------------- #

        # ===================={CORRUPTION}==============================#
        modes_notebook.add(tabCorruption, text="Corruption")

        corruptionFrame = Frame(tabCorruption)

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

        corruptionIntroBody = Label(cTabIntro, text=CINTRO_TEXT, wraplength=300)
        corruptionStartBody = Label(cTabStart, text=CSTART_TEXT, wraplength=300)
        corruptionTransitionBody = Label(cTabTransitions, text=CTRANSITION_TEXT, wraplength=300)

        corruptionIntroBody.pack(fill="both", padx=2, pady=2)
        corruptionStartBody.pack(fill="both", padx=2, pady=2)
        corruptionTransitionBody.pack(fill="both", padx=2, pady=2)

        # -Additional Settings-

        corruptionAdditionalFrame = Frame(tabCorruption, borderwidth=5, relief=RAISED)
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

        corruptionPathFrame = Frame(tabCorruption, borderwidth=5, relief=RAISED)

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

        # ==========={IN HERE IS ABOUT TAB ITEM INITS}===========#
        notebook.add(tabInfo, text="About")
        tabInfoExpound.add(tab_annoyance, text="Annoyance")
        Label(tab_annoyance, text=ANNOYANCE_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_drive, text="Hard Drive")
        Label(tab_drive, text=DRIVE_TEXT, anchor="nw", wraplength=460).pack()
        # tabInfoExpound.add(tab_export, text='Exporting')
        tabInfoExpound.add(tab_wallpaper, text="Wallpaper")
        Label(tab_wallpaper, text=WALLPAPER_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_launch, text="Startup")
        Label(tab_launch, text=STARTUP_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_hibernate, text="Hibernate")
        Label(tab_hibernate, text=HIBERNATE_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_hibernateType, text="Hibernate Types")
        Label(tab_hibernateType, text=HIBERNATE_TYPE_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_advanced, text="Troubleshooting")
        Label(tab_advanced, text=ADVANCED_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_thanksAndAbout, text="Thanks & About")
        Label(tab_thanksAndAbout, text=THANK_AND_ABOUT_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_plusPlus, text="EdgeWare++")
        Label(tab_plusPlus, text=PLUSPLUS_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_packInfo, text="Pack Info")
        Label(tab_packInfo, text=PACKINFO_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_file, text="File")
        Label(tab_file, text=FILE_TEXT, anchor="nw", wraplength=460).pack()
        tabInfoExpound.add(tab_corruption, text="Corruption")
        Label(tab_corruption, text=CORRUPTION_TEXT, anchor="nw", wraplength=460).pack()
        # ==========={HERE ENDS  ABOUT TAB ITEM INITS}===========#

        theme_change(config["themeType"].strip(), self, style, windowFont, title_font)

        # ==========={TOGGLE ASSOCIATE SETTINGS}===========#
        # all toggleAssociateSettings goes here, because it is rendered after the appropriate theme change

        fade_helper(vars.corruption_fade.get())
        trigger_helper(vars.corruption_trigger.get(), False)
        set_widget_states(os.path.isfile(pack.paths.corruption), corruptionEnabled_group)

        # messageOff toggle here, for turning off all help messages
        toggle_help(vars.message_off.get(), message_group)

        notebook.pack(expand=1, fill="both")
        general_notebook.pack(expand=1, fill="both")
        annoyance_notebook.pack(expand=1, fill="both")
        modes_notebook.pack(expand=1, fill="both")
        tabInfoExpound.pack(expand=1, fill="both")
        resourceFrame.pack(fill="x")
        importResourcesButton.pack(fill="x", side="left", expand=1)
        exportResourcesButton.pack(fill="x", side="left", expand=1)
        saveExitButton.pack(fill="x")

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
def theme_change(theme: str, root, style, mfont, tfont):
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
            for widget in CreateToolTip.instances:
                widget.background = "#1b1d23"
                widget.foreground = "#ffffff"
                widget.bordercolor = "#ffffff"
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
            for widget in CreateToolTip.instances:
                widget.background = "#1b1d23"
                widget.foreground = "#00ff41"
                widget.bordercolor = "#00ff41"
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
            for widget in CreateToolTip.instances:
                widget.background = "#ff2600"
                widget.foreground = "#ffffff"
                widget.bordercolor = "#000000"
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
            for widget in CreateToolTip.instances:
                widget.background = "#1b1d23"
                widget.foreground = "#cc60ff"
                widget.bordercolor = "#b999fe"
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
            for widget in CreateToolTip.instances:
                widget.background = "#ffc5cd"
                widget.foreground = "#ff3aa3"
                widget.bordercolor = "#ff84c1"
            style.configure("TFrame", background="pink")
            style.configure("TNotebook", background="pink")
            style.map("TNotebook.Tab", background=[("selected", "pink")])
            style.configure("TNotebook.Tab", background="lightpink", foreground="deep pink")
            mfont.configure(family="Constantia")
            tfont.configure(family="Constantia")


def toggle_help(state: bool, messages: list):
    if state is True:
        try:
            for widget in messages:
                widget.destroy()
        except Exception as e:
            logging.warning(f"could not properly turn help off. {e}")


if __name__ == "__main__":
    try:
        Config()
    except Exception as e:
        logging.fatal(f"Config encountered fatal error:\n{e}")
        messagebox.showerror("Could not start", f"Could not start config.\n[{e}]")
