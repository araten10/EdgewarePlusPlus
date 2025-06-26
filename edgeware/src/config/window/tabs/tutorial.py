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

from pathlib import Path
from tkinter import Event, Frame, Label, Tk, Toplevel, ttk

from config.themes import theme_change
from config.window.utils import (
    config,
)
from config.window.widgets.scroll_frame import ScrollFrame
from paths import Assets
from tkinterweb import HtmlFrame

HIBERNATE_TYPE_TEXT = "Original: The original hibernate type that came with base Edgeware. Spawns a barrage of popups instantly, the max possible amount is based on your awaken activity.\n\nSpaced: Essentially runs Edgeware normally, but over a brief period of time before ceasing generation of new popups. Because of this awaken activity isn't used, instead popup delay is looked at for frequency of popups.\n\nGlitch: Creates popups at random-ish intervals over a period of time. The total amount of popups spawned is based on the awaken activity. Perfect for those who want a 'virus-like' experience, or just something different every time.\n\nRamp: Similar to spaced, only the popup frequency gets faster and faster over the hibernate length. After reaching the max duration, it will spawn a number of popups equal to the awaken activity at a speed slightly faster than your popup delay. Best used with long hibernate length values and fairly short popup delay. (keep in mind that if the popup delay is too short though, popups can potentially not appear or lag behind)\n\nPump-Scare: Do you like haunted houses or scary movies? Don't you wish that instead of screamers and jumpscares, they had porn pop out at you instead? This is kind of like that. When hibernate is triggered a popup with audio will appear for around a second or two, then immediately disappear. This works best on packs with short, immediate audio files: old Edgeware packs that contain half-hour long hypno files will likely not reach meaningful audio in time. Large audio files can also hamper effectiveness of the audio and lead to desync with the popup.\n\nChaos: Every time hibernate activates, it randomly selects any of the other hibernate modes."

def open_tutorial(parent: Tk) -> None:
    root = Toplevel(parent)
    root.geometry("740x900")
    root.focus_force()
    root.title("Edgeware++ Tutorial")

    tutorial_frame = Frame(root)
    tutorial_frame.pack(expand=1, fill="both")
    tutorial_notebook = ttk.Notebook(tutorial_frame, style="lefttab.TNotebook")
    tutorial_notebook.pack(expand=1, fill="both")

    # TkinterWeb looks for images in different places on Linux and Windows with load_file, this is a workaround
    def load_html(tab: HtmlFrame, file: Path) -> None:
        with open(file, "r", encoding="utf-8") as f:
            # base_url ignores the last part of the path and seems to expect a path to a file
            tab.load_html(f.read(), base_url=f"file:///{file}".replace("\\", "/"))

    tab_about = HtmlFrame(tutorial_frame, messages_enabled=False)
    tutorial_notebook.add(tab_about, text="Intro/About")
    load_html(tab_about, Assets.TUTORIAL_INTRO)

    tab_start = HtmlFrame(tutorial_frame, messages_enabled=False)
    tutorial_notebook.add(tab_start, text="Getting Started")
    load_html(tab_start, Assets.TUTORIAL_GETSTARTED)

    tab_basic_settings = HtmlFrame(tutorial_frame, messages_enabled=False)
    tutorial_notebook.add(tab_basic_settings, text="Settings 101")
    load_html(tab_basic_settings, Assets.TUTORIAL_BASICSETTINGS)

    tab_hibernate_type = ScrollFrame(tutorial_frame)
    tutorial_notebook.add(tab_hibernate_type, text="Hibernate Types")
    Label(tab_hibernate_type.viewPort, text=HIBERNATE_TYPE_TEXT, anchor="nw", wraplength=460).pack()

    # HtmlFrame Workaround:
    # HtmlFrame has a bug that makes it incompatible with Notebook on 64bit windows. This bug is known by the developers and is not being fixed due to it being an error larger than the scope of the program.
    # The bug makes it so if you swap tabs from an HtmlFrame to a second HtmlFrame, the program crashes after a few seconds.
    # There is a workaround fix for it that comes included with tkinterweb, however upon trying it it didn't work at all. It rendered everything incorrectly and would have required further rewrites than necessary for a "fix"
    # So as a workaround to the workaround to the bug, I've made it so when you switch tabs, you briefly switch to a blank Frame before switching to the proper HtmlFrame. This way there is no crashing since you will always be going to a new HtmlFrame tab from a regular Frame.
    # The tab is a hidden tab and swapping is nearly invisible to the human eye, at least on most modern systems.
    tab_fix = Frame(tutorial_frame)
    tutorial_notebook.add(tab_fix, text="")
    tutorial_notebook.hide(tab_fix)

    def frame_workaround(event: Event) -> None:
        target_tab = tutorial_notebook.tk.call(tutorial_notebook._w, "identify", "tab", event.x, event.y)
        tutorial_notebook.select(tab_fix)
        tutorial_notebook.hide(tab_fix)
        tutorial_notebook.select(target_tab)

    tutorial_notebook.bind("<Button-1>", frame_workaround)
    # End of HtmlFrame workaround

    theme_change(config["themeType"].strip(), root)
