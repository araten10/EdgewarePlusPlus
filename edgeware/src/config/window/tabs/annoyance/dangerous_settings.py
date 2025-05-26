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

from tkinter import HORIZONTAL, SINGLE, Button, Checkbutton, Entry, Frame, Label, Listbox, Message, Scale, filedialog, ttk
from tkinter.font import Font

from config.vars import Vars
from config.window.utils import (
    add_list,
    config,
    remove_list,
    reset_list,
    set_widget_states,
)
from config.window.widgets.layout import (
    ConfigRow,
    ConfigScale,
    ConfigSection,
    ConfigToggle,
    set_enabled_when,
)
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.tooltip import CreateToolTip

DRIVE_TEXT = 'There are two main features in this section: "Fill Drive" and "Replace Images". This explanation might be long, but these features are very dangerous, so please pay attention if you plan to use them! Unless you imported settings from a pack you downloaded or got this installation of Edgeware++ from somewhere other than the official github, these should all be off by default.\n\nFill drive will attempt to fill your computer with as much porn from the currently loaded pack as possible. It does, however, have some restrictions, which are further explained in the hover tooltip. Fill delay is a forced delay on saving, as when not properly configured it can fill your drive VERY quickly.\n\nReplace images will seek out folders with large numbers of pre-existing images (more than the threshold value) and when it finds one, it will replace ALL of the images with images from the currently loaded pack. For example, you could point it at certain steam directories to have all of your game preview/banner images replaced with porn. Please, please, please, backup any important images before using this setting... Edgeware will attempt to backup any replaced images under /data/backups, but nobody involved with any Edgeware version past, present, or future, is responsible for any lost images. Don\'t solely rely on the included backup feature... do the smart thing and make personal backups as well!\n\nI understand techdom and gooning are both fetishes about making irresponsible decisions, but at least understand the risks and take a moment to decide on how you want to use these features. Set up blacklists and make backups if you wish to proceed, but to echo the inadequate sex-ed public schools dole out: abstinence is the safest option.'
MISC_TEXT = "These settings are less destructive on your PC, but will either cause embarrassment or give you less control over Edgeware.\n\nDisable Panic Hotkey disables both the panic hotkey and system tray panic. A full list of panic alternatives can be found in the hover tooltip.\nLaunch on PC Startup is self explanatory, but keep caution on this if you're running Edgeware with a strong payload.\nShow on Discord will give you a status on discord while you run Edgeware. There's actually a decent amount of customization for this option, and packs can have their own status. However, this setting could definitely be \"socially destructive\", or at least cause you great (unerotic) shame, so be careful with enabling it."
PANIC_LOCKOUT_TEXT = 'Makes it so you cannot panic for a specified duration, essentially forcing you to endure the payload until the timer is up.\n\nA safeword can be used if you wish to still use panic during this time. It is recommended that you generate one via a password generator/keysmash and save it somewhere easily accessible; not only does this help in emergency situations where you need to turn off Edgeware++, but also makes it harder to memorize so the "fetishistic danger" remains.'


def assign_path(path_entry: Entry, vars: Vars) -> None:
    path_ = str(filedialog.askdirectory(initialdir="/", title="Select Parent Folder"))
    if path_ != "":
        config["drivePath"] = path_
        path_entry.configure(state="normal")
        path_entry.delete(0, 9999)
        path_entry.insert(1, path_)
        path_entry.configure(state="disabled")
        vars.drive_path.set(str(path_entry.get()))


class DangerousSettingsTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]) -> None:
        super().__init__()

        # Panic lockout
        lockout_section = ConfigSection(self.viewPort, "Panic Lockout", PANIC_LOCKOUT_TEXT)
        lockout_section.pack()

        lockout_row = ConfigRow(lockout_section)
        lockout_row.pack()
        ConfigToggle(lockout_row, "Enable Panic Lockout", variable=vars.panic_lockout).pack()
        safeword_frame = Frame(lockout_row)
        safeword_frame.pack(side="left", expand=True)
        Label(safeword_frame, text="Emergency Safeword").pack()
        lockout_safeword = Entry(safeword_frame, show="*", textvariable=vars.panic_lockout_password)
        lockout_safeword.pack(expand=1, fill="both")
        set_enabled_when(lockout_safeword, enabled=(vars.panic_lockout, True))

        ConfigScale(lockout_section, "Panic Lockout Time (minutes)", vars.panic_lockout_time, 1, 1440, enabled=(vars.panic_lockout, True)).pack()

        # Drive
        drive_section = ConfigSection(self.viewPort, "Hard Drive Settings", DRIVE_TEXT)
        drive_section.pack()

        ttk.Separator(drive_section, orient=HORIZONTAL).pack(fill="x", pady=2)

        drive_frame = Frame(drive_section)
        drive_frame.pack(fill="x", pady=5)

        blacklist_frame = Frame(drive_frame)
        blacklist_frame.pack(fill="y", side="left")
        Label(blacklist_frame, text="Folder Name Blacklist").pack(fill="x")
        blacklist_listbox = Listbox(blacklist_frame, selectmode=SINGLE)
        blacklist_listbox.pack(fill="x")
        for name in config["avoidList"].split(">"):
            blacklist_listbox.insert(2, name)
        Button(
            blacklist_frame,
            text="Add Name",
            command=lambda: add_list(blacklist_listbox, "avoidList", "Folder Name", "Fill/replace will skip any folder with given name."),
        ).pack(fill="x")
        Button(
            blacklist_frame,
            text="Remove Name",
            command=lambda: remove_list(blacklist_listbox, "avoidList", "Remove Edgeware", "You cannot remove the Edgeware folder exception."),
        ).pack(fill="x")
        Button(blacklist_frame, text="Reset", command=lambda: reset_list(blacklist_listbox, "avoidList", "Edgeware>AppData")).pack(fill="x")

        fill_replace_frame = Frame(drive_frame)
        fill_replace_frame.pack(fill="y", side="left")

        fill_toggle = Checkbutton(
            fill_replace_frame,
            text="Fill Drive",
            variable=vars.fill_drive,
            command=lambda: set_widget_states(vars.fill_drive.get(), fill_group),
            cursor="question_arrow",
        )
        fill_toggle.pack()
        CreateToolTip(
            fill_toggle,
            '"Fill Drive" does exactly what it says: it attempts to fill your hard drive with as much porn from /resource/img/ as possible. '
            'It does, however, have some restrictions. It will (should) not place ANY images into folders that start with a "." or have their '
            "names listed in the folder name blacklist.\nIt will also ONLY place images into the User folder and its subfolders.\nFill drive has "
            "one modifier, which is its own forced delay. Because it runs with between 1 and 8 threads at any given time, when improperly configured it can "
            "fill your drive VERY quickly. To ensure that you get that nice slow fill, you can adjust the delay between each folder sweep it performs.",
        )
        fill_delay = Scale(fill_replace_frame, label="Fill Delay (10ms)", from_=0, to=250, orient="horizontal", variable=vars.fill_delay)
        fill_delay.pack()
        fill_group = [fill_delay]
        set_widget_states(vars.fill_drive.get(), fill_group)

        replace_toggle = Checkbutton(
            fill_replace_frame,
            text="Replace Images",
            variable=vars.replace_images,
            command=lambda: set_widget_states(vars.replace_images.get(), replace_group),
            cursor="question_arrow",
        )
        replace_toggle.pack()
        CreateToolTip(
            replace_toggle,
            "Seeks out folders with more images than the threshold value, then replaces all of them. No, there is no automated backup!\n\n"
            'I am begging you to read the full documentation in the "About" tab before even thinking about enabling this feature!\n\n'
            "We are not responsible for any pain, suffering, miserere, or despondence caused by your files being deleted! "
            "At the very least, back them up and use the blacklist!",
        )
        replace_threshold = Scale(fill_replace_frame, label="Image Threshold", from_=1, to=1000, orient="horizontal", variable=vars.replace_threshold)
        replace_threshold.pack()
        replace_group = [replace_threshold]
        set_widget_states(vars.replace_images.get(), replace_group)

        path_frame = Frame(drive_frame)
        path_frame.pack(fill="x")
        Label(path_frame, text="Fill/Replace Start Folder").pack(fill="x")
        path_entry = Entry(path_frame)
        path_entry.insert(1, config["drivePath"])
        path_entry.configure(state="disabled")
        path_entry.pack(fill="x")
        Button(path_frame, text="Select", command=lambda: assign_path(path_entry, vars)).pack(fill="x")

        # Misc
        misc_section = ConfigSection(self.viewPort, "Misc. Dangerous Settings", MISC_TEXT)
        misc_section.pack()

        misc_row = ConfigRow(misc_section)
        misc_row.pack()

        panic_disable_toggle = ConfigToggle(misc_row, "Disable Panic Hotkey", variable=vars.panic_disabled, cursor="question_arrow")
        panic_disable_toggle.pack()
        CreateToolTip(
            panic_disable_toggle,
            "This not only disables the panic hotkey, but also the panic function in the system tray as well.\n\n"
            "If you want to use Panic after this, you can still:\n"
            '•Directly run "panic.pyw"\n'
            '•Keep the config window open and press "Perform Panic"\n'
            "•Use the panic desktop icon (if you kept those enabled)",
        )
        ConfigToggle(misc_row, "Launch on PC Startup", variable=vars.run_at_startup).pack()
        discord_toggle = ConfigToggle(misc_row, "Show on Discord", variable=vars.show_on_discord, cursor="question_arrow")
        discord_toggle.pack()
        CreateToolTip(discord_toggle, "Displays a lewd status on discord (if your discord is open), which can be set per-pack by the pack creator.")
