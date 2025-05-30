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

from dataclasses import dataclass
from tkinter import Button, Canvas, Checkbutton, Frame, Label, Message, Misc, OptionMenu, Scale, TclError, Text, ttk
from tkinter.font import Font

from tkinterweb import HtmlFrame


@dataclass
class Theme:
    fg: str
    bg: str
    text_fg: str
    text_bg: str
    font: (str, int)
    transparent_bg: str


THEMES = {
    "Original": Theme("#000000", "#f0f0f0", "#000000", "#ffffff", ("TkDefaultFont", 9), "#000001"),
    "Dark": Theme("#f9faff", "#282c34", "#f9faff", "#1b1d23", ("TkDefaultFont", 9), "#f9fafe"),
    "The One": Theme("#00ff41", "#282c34", "#00ff41", "#1b1d23", ("Consolas", 9), "#00ff42"),
    "Ransom": Theme("#ffffff", "#841212", "#000000", "#ffffff", ("Arial Bold", 9), "#fffffe"),
    "Goth": Theme("#ba9aff", "#282c34", "#6a309d", "#db7cf2", ("Constantia", 9), "#ba9afe"),
    "Bimbo": Theme("#ff3aa3", "#ffc5cd", "#f43df2", "#ffc5cd", ("Constantia", 9), "#ff3aa4"),
}


# To be cleaned up

CONFIG_THEMES = {
    "Original": {
        "bg": "#d9d9d9",  # Added
        "bg-disabled": "gray35",
        "background": "#f0f0f0",
        "fg": "black",
        "Button-fg": "black",  # Added
        "Text-fg": "black",  # Added
        "Text-bg": "white",  # Added
        "Button-activebackground": "#ececec",  # Added
        "OptionMenu-activebackground": "#ececec",  # Added
        "troughcolor": "#b3b3b3",  # Added
        "selectcolor": "#ffffff",  # Added
        "Message-font": ("TkDefaultFont", 8),
        "m-family": "TkDefaultFont",  # Added
        "m-size": 10,  # Added
        "t-family": "TkDefaultFont",  # Added
        "Tab-background": "#d9d9d9",
        "Tab-foreground": "black",  # Added
    },
    "Dark": {
        "bg": "#282c34",
        "bg-disabled": "gray65",
        "background": "#282c34",
        "fg": "ghost white",
        "Button-fg": "ghost white",
        "Text-fg": "ghost white",
        "Text-bg": "#1b1d23",
        "Button-activebackground": "#282c34",
        "OptionMenu-activebackground": "#282c34",
        "troughcolor": "#c8c8c8",
        "selectcolor": "#1b1d23",
        "Message-font": ("TkDefaultFont", 8),
        "m-family": "TkDefaultFont",  # Added
        "m-size": 10,  # Added
        "t-family": "TkDefaultFont",  # Added
        "Tab-background": "#1b1d23",
        "Tab-foreground": "#f9faff",
    },
    "The One": {
        "bg": "#282c34",
        "bg-disabled": "#37573d",
        "background": "#282c34",
        "fg": "#00ff41",
        "Button-fg": "#00ff41",
        "Text-fg": "#00ff41",
        "Text-bg": "#1b1d23",
        "Button-activebackground": "#1b1d23",
        "OptionMenu-activebackground": "#282c34",
        "troughcolor": "#009a22",
        "selectcolor": "#1b1d23",
        "Message-font": ("Consolas", 8),
        "m-family": "Consolas",
        "m-size": 8,
        "t-family": "Consolas",
        "Tab-background": "#1b1d23",
        "Tab-foreground": "#00ff41",
    },
    "Ransom": {
        "bg": "#841212",
        "bg-disabled": "573737",
        "background": "#841212",
        "fg": "white",
        "Button-fg": "yellow",
        "Text-fg": "black",
        "Text-bg": "white",
        "Button-activebackground": "#841212",
        "OptionMenu-activebackground": "#841212",
        "troughcolor": "#c8c8c8",
        "selectcolor": "#5c0d0d",
        "Message-font": ("Arial", 8),
        "m-family": "Arial",
        "m-size": 10,  # Added
        "t-family": "Arial Bold",
        "Tab-background": "#5c0d0d",
        "Tab-foreground": "#ffffff",
    },
    "Goth": {
        "bg": "#282c34",
        "bg-disabled": "#4b3757",
        "background": "#282c34",
        "fg": "MediumPurple1",
        "Button-fg": "MediumPurple1",
        "Text-fg": "purple4",
        "Text-bg": "MediumOrchid2",
        "Button-activebackground": "#282c34",
        "OptionMenu-activebackground": "#282c34",
        "troughcolor": "MediumOrchid2",
        "selectcolor": "#1b1d23",
        "Message-font": ("Constantia", 8),
        "m-family": "Constantia",
        "m-size": 10,  # Added
        "t-family": "Constantia",
        "Tab-background": "#1b1d23",
        "Tab-foreground": "MediumPurple1",
    },
    "Bimbo": {
        "bg": "pink",
        "bg-disabled": "#bc7abf",
        "background": "pink",
        "fg": "deep pink",
        "Button-fg": "deep pink",
        "Text-fg": "magenta2",
        "Text-bg": "light pink",
        "Button-activebackground": "hot pink",
        "OptionMenu-activebackground": "hot pink",
        "troughcolor": "hot pink",
        "selectcolor": "light pink",
        "Message-font": ("Constantia", 8),
        "m-family": "Constantia",
        "m-size": 10,  # Added
        "t-family": "Constantia",
        "Tab-background": "light pink",
        "Tab-foreground": "deep pink",
    },
}


def theme_change(theme: str, root: Misc, style: ttk.Style, mfont: Font, tfont: Font) -> None:
    from config.window.utils import all_children, config  # Circular import

    t = CONFIG_THEMES["Original" if config["themeNoConfig"] is True else theme]

    for widget in all_children(root):
        if hasattr(widget, "ignore_theme"):
            continue

        if isinstance(widget, Frame) or isinstance(widget, Canvas):
            widget.configure(bg=t["bg"])
        if isinstance(widget, Button):
            widget.configure(bg=t["bg"], fg=t["Button-fg"], activebackground=t["Button-activebackground"], activeforeground=t["fg"])
        if isinstance(widget, Label):
            widget.configure(bg=t["bg"], fg=t["fg"])
        if isinstance(widget, OptionMenu):
            widget.configure(bg=t["bg"], fg=t["fg"], highlightthickness=0, activebackground=t["OptionMenu-activebackground"], activeforeground=t["fg"])
        if isinstance(widget, Text):
            widget.configure(bg=t["Text-bg"], fg=t["Text-fg"])
        if isinstance(widget, Scale):
            widget.configure(bg=t["bg"], fg=t["fg"], activebackground=t["bg"], troughcolor=t["troughcolor"], highlightthickness=0)
        if isinstance(widget, Checkbutton):
            # activebackground was "bg" but "Button-activebackground" is true color for default theme
            widget.configure(
                bg=t["bg"],
                fg=t["fg"],
                selectcolor=t["selectcolor"],
                activebackground=t["Button-activebackground"],
                activeforeground=t["fg"],
                highlightthickness=0,
            )
        if isinstance(widget, Message):
            widget.configure(bg=t["bg"], fg=t["fg"], font=t["Message-font"])
        if isinstance(widget, HtmlFrame):
            widget.add_css(f"html{{background: {t['bg']}; color: {t['fg']}; font-family: {t['m-family']};}}")
    style.configure("TFrame", background=t["background"])
    style.configure("TNotebook", background=t["background"])
    style.map("TNotebook.Tab", background=[("selected", t["background"])])
    style.configure("TNotebook.Tab", background=t["Tab-background"], foreground=t["Tab-foreground"])
    mfont.configure(family=t["m-family"], size=t["m-size"])
    tfont.configure(family=t["t-family"])

    for widget in all_children(root):
        try:
            if widget["state"] == "disabled":
                widget.configure(bg=t["bg-disabled"])
        except TclError:
            pass
