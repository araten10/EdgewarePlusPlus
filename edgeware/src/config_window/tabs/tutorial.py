import textwrap
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    Frame,
    Label,
    Message,
    Misc,
    ttk,
)
from tkinter.font import Font

from config_window.utils import set_widget_states
from config_window.vars import Vars
from pack import Pack
from widgets.scroll_frame import ScrollFrame

ABOUT_INTRO_TEXT = "Hello, and welcome to Edgeware++! Whether you\'ve found this from word of mouth, downloaded a pack from a creator you like, or are a long-time \"original Edgeware\" user, thank you so much for using our program. This is the \"Tutorial\" tab, where you can read detailed help from the basics to more advanced features. If you want to start the tutorial proper, feel free to click on one of the tabs on the left! (I recommend \"Getting Started\"!)"
ABOUT_TEXT = "The original Edgeware was created by PetitTournesol in 2021. By the time I had discovered it in 2023, they had already stopped updating it- something totally understandable, but there were a few things I wanted to fix. I originally got assistance from a “furry gooning discord server” since there was a dedicated development channel full of nice, helpful people. I eventually accomplished my goal of adding a toggle to desktop icon popups, but then I got new ideas… and even more new ideas after those…\n\nA year or so later, I was still working on the program, and had made a few social media accounts to post updates on it. The support I received was much greater than I ever could have hoped- considering I had started this project with quite literally zero python experience, I was happy people were enjoying it. From here I made a new close friend named Marigold, who has been invaluable to the project since! She has not only helped with Linux development (a highly sought after feature), but has helped endlessly with new features, organization, bugfixing, and github usage.\n\nAs I write this, we are still continuing strong on Edgeware++ updates and hope to keep doing so in the future. At this point, we have added so many new features that it’s hard to count… as well as almost completely rewriting the backend. To be honest, I never thought we would still be working on it this far ahead in time, but with everyone’s continued support and interest our passion remains strong. I don’t want to speak prematurely, but maybe after we’re done with Edgeware++, we’ll work together on more fun projects in the future…?\n\nSo once again, thank you for your love and support. As somebody who struggles with mental health issues among various other things, I never thought i’d be able to create something that so many people use and enjoy- and make new friends while doing it. We hope you enjoy the program, and feel similarly inspired to go out there and create some cool, horny things!\n\n-Araten"

DRIVE_TEXT = 'The "Drive" portion of Edgeware has three features: fill drive, replace images, and Booru downloader.\n\n"Fill Drive" does exactly what it says: it attempts to fill your hard drive with as much porn from /resource/img/ as possible. It does, however, have some restrictions. It will (should) not place ANY images into folders that start with a "." or have their names listed in the folder name blacklist.\nIt will also ONLY place images into the User folder and its subfolders.\nFill drive has one modifier, which is its own forced delay. Because it runs with between 1 and 8 threads at any given time, when unchecked it can fill your drive VERY quickly. To ensure that you get that nice slow fill, you can adjust the delay between each folder sweep it performs and the max number of threads.\n\n"Replace Images" is more complicated. Its searching is the exact same as fill drive, but instead of throwing images everywhere, it will seek out folders with large numbers of images (more than the threshold value) and when it finds one, it will replace ALL of the images with porn from /resource/img/. REMEMBER THAT IF YOU CARE ABOUT YOUR PHOTOS, AND THEY\'RE IN A FOLDER WITH MORE IMAGES THAN YOUR CHOSEN THRESHOLD VALUE, EITHER BACK THEM UP IN A ZIP OR SOMETHING OR DO. NOT. USE. THIS SETTING. I AM NOT RESPONSIBLE FOR YOUR OWN DECISION TO RUIN YOUR PHOTOS. Edgeware will attempt to backup any replaced images under /data/backups, but DO NOT RELY ON THIS FEATURE IN ANY CIRCUMSTANCE. ALWAYS BACKUP YOUR FILES YOURSELF.\n\nBooru downloader allows you to download new items from a Booru of your choice. For the booru name, ONLY the literal name is used, like "censored" or "blacked" instead of the full url. This is not case sensitive. Use the "Validate" button to ensure that downloading will be successful before running. For tagging, if you want to have multiple tags, they can be combined using "tag1+tag2+tag3" or if you want to add blacklist tags, type your tag and append a "+-blacklist_tag" after the desired tag.'
HIBERNATE_TYPE_TEXT = "Original: The original hibernate type that came with base Edgeware. Spawns a barrage of popups instantly, the max possible amount is based on your awaken activity.\n\nSpaced: Essentially runs Edgeware normally, but over a brief period of time before ceasing generation of new popups. Because of this awaken activity isn't used, instead popup delay is looked at for frequency of popups.\n\nGlitch: Creates popups at random-ish intervals over a period of time. The total amount of popups spawned is based on the awaken activity. Perfect for those who want a 'virus-like' experience, or just something different every time.\n\nRamp: Similar to spaced, only the popup frequency gets faster and faster over the hibernate length. After reaching the max duration, it will spawn a number of popups equal to the awaken activity at a speed slightly faster than your popup delay. Best used with long hibernate length values and fairly short popup delay. (keep in mind that if the popup delay is too short though, popups can potentially not appear or lag behind)\n\nPump-Scare: Do you like haunted houses or scary movies? Don't you wish that instead of screamers and jumpscares, they had porn pop out at you instead? This is kind of like that. When hibernate is triggered a popup with audio will appear for around a second or two, then immediately disappear. This works best on packs with short, immediate audio files: old Edgeware packs that contain half-hour long hypno files will likely not reach meaningful audio in time. Large audio files can also hamper effectiveness of the audio and lead to desync with the popup.\n\nChaos: Every time hibernate activates, it randomly selects any of the other hibernate modes."

FILE_TEXT = 'The file tab is for all your file management needs, whether it be saving things, loading things, deleting things, or looking around in config folders. The Preset window has also been moved here to make more room for general options.\n\nThere are only two things that aren\'t very self explanatory: deleting logs and unique IDs.\n\nWhile deleting logs is fairly straightforward, it should be noted that it will not delete the log currently being written during the session, so the "total logs in folder" stat will always display as "1".\n\nUnique IDs are a feature to help assist with saving moods. In short, they are a generated identifier that is used when saving to a "moods json file", which is tapped into when selecting what moods you want to see in the "Pack Info" tab. Unique IDs are only used if the pack does not have a \'info.json\' file, otherwise the pack name is just used instead. If you are rapidly editing a pack without info.json and want Edgeware++ to stop generating new mood files, there is an option to disable it in the troubleshooting tab.'

class TutorialTab(Frame):
    def __init__(self, vars: Vars, title_font: Font):
        super().__init__()

        tutorial_frame = Frame(self)
        tutorial_frame.pack(expand=1, fill="both")
        tutorial_notebook = ttk.Notebook(tutorial_frame, style="lefttab.TNotebook")
        tutorial_notebook.pack(expand=1, fill="both")

        tab_about = ScrollFrame()
        tutorial_notebook.add(tab_about, text="Intro/About")
        Label(tab_about.viewPort, text=ABOUT_INTRO_TEXT, anchor="nw", wraplength=460).pack()
        Label(tab_about.viewPort, text="About", font=title_font, relief=GROOVE).pack(pady=2)
        Label(tab_about.viewPort, text=ABOUT_TEXT, anchor="nw", wraplength=460).pack()

        tab_drive = ScrollFrame()
        tutorial_notebook.add(tab_drive, text="Hard Drive")
        Label(tab_drive.viewPort, text=DRIVE_TEXT, anchor="nw", wraplength=460).pack()

        tab_hibernate_type = ScrollFrame()
        tutorial_notebook.add(tab_hibernate_type, text="Hibernate Types")
        Label(tab_hibernate_type.viewPort, text=HIBERNATE_TYPE_TEXT, anchor="nw", wraplength=460).pack()

        tab_file = ScrollFrame()
        tutorial_notebook.add(tab_file, text="File")
        Label(tab_file.viewPort, text=FILE_TEXT, anchor="nw", wraplength=460).pack()
