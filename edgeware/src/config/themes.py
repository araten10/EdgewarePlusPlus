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
    active_bg: str
    text_fg: str
    text_bg: str
    font: (str, int)
    transparent_bg: str


THEMES = {
    "Original": Theme(fg="black", bg="#d9d9d9", active_bg="#ececec", text_fg="black", text_bg="white", font=("TkDefaultFont", 9), transparent_bg="#000001"),
    "Dark": Theme(
        fg="ghost white", bg="#282c34", active_bg="#282c34", text_fg="ghost white", text_bg="#1b1d23", font=("TkDefaultFont", 9), transparent_bg="#f9fafe"
    ),
    "The One": Theme(fg="#00ff41", bg="#282c34", active_bg="#1b1d23", text_fg="#00ff41", text_bg="#1b1d23", font=("Consolas", 9), transparent_bg="#00ff42"),
    "Ransom": Theme(fg="white", bg="#841212", active_bg="#841212", text_fg="black", text_bg="white", font=("Arial Bold", 9), transparent_bg="#fffffe"),
    "Goth": Theme(
        fg="MediumPurple1", bg="#282c34", active_bg="#282c34", text_fg="purple4", text_bg="MediumOrchid2", font=("Constantia", 9), transparent_bg="#ba9afe"
    ),
    "Bimbo": Theme(
        fg="deep pink",
        bg="pink",
        active_bg="hot pink",
        text_fg="magenta2",
        text_bg="light pink",
        font=("Constantia", 9),
        transparent_bg="#ff3aa4",
    ),
}


# To be cleaned up

CONFIG_THEMES = {
    "Original": {
        "bg-disabled": "gray35",
        "background": "#f0f0f0",
        "Button-fg": "black",  # Added
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
        "bg-disabled": "gray65",
        "background": "#282c34",
        "Button-fg": "ghost white",
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
        "bg-disabled": "#37573d",
        "background": "#282c34",
        "Button-fg": "#00ff41",
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
        "bg-disabled": "573737",
        "background": "#841212",
        "Button-fg": "yellow",
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
        "bg-disabled": "#4b3757",
        "background": "#282c34",
        "Button-fg": "MediumPurple1",
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
        "bg-disabled": "#bc7abf",
        "background": "pink",
        "Button-fg": "deep pink",
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


def theme_change(name: str, root: Misc, style: ttk.Style, mfont: Font, tfont: Font) -> None:
    from config.window.utils import all_children, config  # Circular import

    t = CONFIG_THEMES["Original" if config["themeNoConfig"] is True else name]
    theme = THEMES["Original" if config["themeNoConfig"] is True else name]

    for widget in all_children(root):
        if isinstance(widget, Frame) or isinstance(widget, Canvas):
            widget.configure(bg=theme.bg)
        if isinstance(widget, Button):
            widget.configure(bg=theme.bg, fg=t["Button-fg"], activebackground=theme.active_bg, activeforeground=theme.fg)
        if isinstance(widget, Label):
            if not hasattr(widget, "ignore_theme_fg"):
                widget.configure(fg=theme.fg)
            if not hasattr(widget, "ignore_theme_bg"):
                widget.configure(bg=theme.bg)
        if isinstance(widget, OptionMenu):
            widget.configure(bg=theme.bg, fg=theme.fg, highlightthickness=0, activebackground=theme.active_bg, activeforeground=theme.fg)
        if isinstance(widget, Text):
            widget.configure(bg=theme.text_bg, fg=theme.text_fg)
        if isinstance(widget, Scale):
            widget.configure(bg=theme.bg, fg=theme.fg, activebackground=theme.bg, troughcolor=t["troughcolor"], highlightthickness=0)
        if isinstance(widget, Checkbutton):
            # activebackground was "bg" but "Button-activebackground" is true color for default theme
            widget.configure(
                bg=theme.bg,
                fg=theme.fg,
                selectcolor=t["selectcolor"],
                activebackground=theme.active_bg,
                activeforeground=theme.fg,
                highlightthickness=0,
            )
        if isinstance(widget, Message):
            widget.configure(bg=theme.bg, fg=theme.fg, font=t["Message-font"])
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
