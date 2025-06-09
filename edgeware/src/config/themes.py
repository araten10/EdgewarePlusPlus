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
from tkinter import Button, Canvas, Checkbutton, Frame, Label, Message, Misc, OptionMenu, Scale, Scrollbar, TclError, Text, font, ttk

from tkinterweb import HtmlFrame


@dataclass
class Theme:
    # Generic
    fg: str
    bg: str
    active_bg: str
    disabled_bg: str
    trough: str

    # Specific elements
    transparent_bg: str  # Subliminal background color on Windows
    tab_bg: str
    tab_frame_bg: str
    button_fg: str
    text_fg: str
    text_bg: str
    check_select: str

    # Fonts
    font: str = "Segoe UI"
    font_size: int = 9
    title_font: str = "Segoe UI"


THEMES = {
    "Original": Theme(
        fg="black",
        bg="#d9d9d9",
        active_bg="#ececec",
        disabled_bg="gray35",
        trough="#b3b3b3",
        #
        transparent_bg="#000001",
        tab_bg="#d9d9d9",
        tab_frame_bg="#f0f0f0",
        button_fg="black",
        text_fg="black",
        text_bg="white",
        check_select="#ffffff",
    ),
    "Dark": Theme(
        fg="ghost white",
        bg="#282c34",
        active_bg="#282c34",
        disabled_bg="gray65",
        trough="#c8c8c8",
        #
        transparent_bg="#f9fafe",
        tab_bg="#1b1d23",
        tab_frame_bg="#282c34",
        button_fg="ghost white",
        text_fg="ghost white",
        text_bg="#1b1d23",
        check_select="#1b1d23",
    ),
    "The One": Theme(
        fg="#00ff41",
        bg="#282c34",
        active_bg="#1b1d23",
        disabled_bg="#37573d",
        trough="#009a22",
        #
        transparent_bg="#00ff42",
        tab_bg="#1b1d23",
        tab_frame_bg="#282c34",
        button_fg="#00ff41",
        text_fg="#00ff41",
        text_bg="#1b1d23",
        check_select="#1b1d23",
        #
        font="Consolas",
        font_size=8,
        title_font="Consolas",
    ),
    "Ransom": Theme(
        fg="white",
        bg="#841212",
        active_bg="#841212",
        disabled_bg="573737",
        trough="#c8c8c8",
        #
        transparent_bg="#fffffe",
        tab_bg="#5c0d0d",
        tab_frame_bg="#841212",
        button_fg="yellow",
        text_fg="black",
        text_bg="white",
        check_select="#5c0d0d",
        #
        font="Arial",
        title_font="Arial Bold",
    ),
    "Goth": Theme(
        fg="MediumPurple1",
        bg="#282c34",
        active_bg="#282c34",
        disabled_bg="#4b3757",
        trough="MediumOrchid2",
        #
        transparent_bg="#ba9afe",
        tab_bg="#1b1d23",
        tab_frame_bg="#282c34",
        button_fg="MediumPurple1",
        text_fg="purple4",
        text_bg="MediumOrchid2",
        check_select="#1b1d23",
        #
        font="Constantia",
        title_font="Constantia",
    ),
    "Bimbo": Theme(
        fg="deep pink",
        bg="pink",
        active_bg="hot pink",
        disabled_bg="#bc7abf",
        trough="hot pink",
        #
        transparent_bg="#ff3aa4",
        tab_bg="light pink",
        tab_frame_bg="pink",
        button_fg="deep pink",
        text_fg="magenta2",
        text_bg="light pink",
        check_select="light pink",
        #
        font="Constantia",
        title_font="Constantia",
    ),
}


def theme_change(name: str, root: Misc, style: ttk.Style | None = None) -> None:
    # Circular imports
    from config.window.utils import all_children, config
    from config.window.widgets.layout import ConfigTitle

    theme = THEMES["Original" if config["themeNoConfig"] else name]

    for widget in all_children(root):
        match widget:
            case Frame() | Canvas():
                widget.configure(bg=theme.bg)
            case Button():
                widget.configure(bg=theme.bg, fg=theme.button_fg, activebackground=theme.active_bg, activeforeground=theme.fg)
            case ConfigTitle():
                widget.configure(fg=theme.fg, bg=theme.bg, font=(theme.title_font, 15))
            case Label():
                if not hasattr(widget, "ignore_theme_fg"):
                    widget.configure(fg=theme.fg)
                if not hasattr(widget, "ignore_theme_bg"):
                    widget.configure(bg=theme.bg)
            case OptionMenu():
                widget.configure(bg=theme.bg, fg=theme.fg, highlightthickness=0, activebackground=theme.active_bg, activeforeground=theme.fg)
            case Text():
                widget.configure(bg=theme.text_bg, fg=theme.text_fg)
            case Scale():
                widget.configure(bg=theme.bg, fg=theme.fg, activebackground=theme.active_bg, troughcolor=theme.trough, highlightthickness=0)
            case Checkbutton():
                widget.configure(
                    bg=theme.bg,
                    fg=theme.fg,
                    selectcolor=theme.check_select,
                    activebackground=theme.active_bg,
                    activeforeground=theme.fg,
                    highlightthickness=0,
                )
            case Message():
                widget.configure(bg=theme.bg, fg=theme.fg, font=(theme.font, 8))
            case HtmlFrame():
                widget.add_css(f"html{{background: {theme.bg}; color: {theme.fg}; font-family: {theme.font};}}")
            case Scrollbar():
                try:
                    widget.configure(bg=theme.bg, activebackground=theme.active_bg, troughcolor=theme.trough)
                except TclError:
                    pass  # ttk.Scrollbar can't be handled this way?

    if style:
        style.configure("TFrame", background=theme.tab_frame_bg)
        style.configure("TNotebook", background=theme.tab_frame_bg)
        style.map("TNotebook.Tab", background=[("selected", theme.tab_frame_bg)])
        style.configure("TNotebook.Tab", background=theme.tab_bg, foreground=theme.fg)

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family=theme.font, size=theme.font_size)

    for widget in all_children(root):
        try:
            from tkinterweb import TkinterWeb
            if not isinstance(widget, TkinterWeb) and widget["state"] == "disabled":
                widget.configure(bg=theme.disabled_bg)
        except TclError:
            pass
