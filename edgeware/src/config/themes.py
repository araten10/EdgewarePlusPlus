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
from tkinter import Button, Canvas, Checkbutton, Frame, Label, Message, Misc, OptionMenu, Scale, TclError, Text, font, ttk

from tkinterweb import HtmlFrame


@dataclass
class Theme:
    fg: str
    bg: str
    active_bg: str
    disabled_bg: str
    button_fg: str
    tab_bg: str
    tab_frame_bg: str
    trough: str
    select: str
    text_fg: str
    text_bg: str
    font: tuple[str, int]
    transparent_bg: str
    message_font: tuple[str, int]
    default_font_family: str
    default_font_size: int
    heading_font_family: str


THEMES = {
    "Original": Theme(
        fg="black",
        bg="#d9d9d9",
        active_bg="#ececec",
        disabled_bg="gray35",
        button_fg="black",
        tab_bg="#d9d9d9",
        tab_frame_bg="#f0f0f0",
        trough="#b3b3b3",
        select="#ffffff",
        text_fg="black",
        text_bg="white",
        font=("TkDefaultFont", 9),
        transparent_bg="#000001",
        message_font=("TkDefaultFont", 8),
        default_font_family="TkDefaultFont",  # Added
        default_font_size=10,  # Added
        heading_font_family="TkDefaultFont",  # Added
    ),
    "Dark": Theme(
        fg="ghost white",
        bg="#282c34",
        active_bg="#282c34",
        disabled_bg="gray65",
        button_fg="ghost white",
        tab_bg="#1b1d23",
        tab_frame_bg="#282c34",
        trough="#c8c8c8",
        select="#1b1d23",
        text_fg="ghost white",
        text_bg="#1b1d23",
        font=("TkDefaultFont", 9),
        transparent_bg="#f9fafe",
        message_font=("TkDefaultFont", 8),
        default_font_family="TkDefaultFont",  # Added
        default_font_size=10,  # Added
        heading_font_family="TkDefaultFont",  # Added
    ),
    "The One": Theme(
        fg="#00ff41",
        bg="#282c34",
        active_bg="#1b1d23",
        disabled_bg="#37573d",
        button_fg="#00ff41",
        tab_bg="#1b1d23",
        tab_frame_bg="#282c34",
        trough="#009a22",
        select="#1b1d23",
        text_fg="#00ff41",
        text_bg="#1b1d23",
        font=("Consolas", 9),
        transparent_bg="#00ff42",
        message_font=("Consolas", 8),
        default_font_family="Consolas",
        default_font_size=8,
        heading_font_family="Consolas",
    ),
    "Ransom": Theme(
        fg="white",
        bg="#841212",
        active_bg="#841212",
        disabled_bg="573737",
        button_fg="yellow",
        tab_bg="#5c0d0d",
        tab_frame_bg="#841212",
        trough="#c8c8c8",
        select="#5c0d0d",
        text_fg="black",
        text_bg="white",
        font=("Arial Bold", 9),
        transparent_bg="#fffffe",
        message_font=("Arial", 8),
        default_font_family="Arial",
        default_font_size=10,  # Added
        heading_font_family="Arial Bold",
    ),
    "Goth": Theme(
        fg="MediumPurple1",
        bg="#282c34",
        active_bg="#282c34",
        disabled_bg="#4b3757",
        button_fg="MediumPurple1",
        tab_bg="#1b1d23",
        tab_frame_bg="#282c34",
        trough="MediumOrchid2",
        select="#1b1d23",
        text_fg="purple4",
        text_bg="MediumOrchid2",
        font=("Constantia", 9),
        transparent_bg="#ba9afe",
        message_font=("Constantia", 8),
        default_font_family="Constantia",
        default_font_size=10,  # Added
        heading_font_family="Constantia",
    ),
    "Bimbo": Theme(
        fg="deep pink",
        bg="pink",
        active_bg="hot pink",
        disabled_bg="#bc7abf",
        button_fg="deep pink",
        tab_bg="light pink",
        tab_frame_bg="pink",
        trough="hot pink",
        select="light pink",
        text_fg="magenta2",
        text_bg="light pink",
        font=("Constantia", 9),
        transparent_bg="#ff3aa4",
        message_font=("Constantia", 8),
        default_font_family="Constantia",
        default_font_size=10,  # Added
        heading_font_family="Constantia",
    ),
}


def theme_change(name: str, root: Misc, style: ttk.Style | None = None) -> None:
    from config.window.utils import all_children, config  # Circular import

    theme = THEMES["Original" if config["themeNoConfig"] is True else name]

    for widget in all_children(root):
        if isinstance(widget, Frame) or isinstance(widget, Canvas):
            widget.configure(bg=theme.bg)
        if isinstance(widget, Button):
            widget.configure(bg=theme.bg, fg=theme.button_fg, activebackground=theme.active_bg, activeforeground=theme.fg)
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
            widget.configure(bg=theme.bg, fg=theme.fg, activebackground=theme.bg, troughcolor=theme.trough, highlightthickness=0)
        if isinstance(widget, Checkbutton):
            # activebackground was "bg" but "Button-activebackground" is true color for default theme
            widget.configure(
                bg=theme.bg,
                fg=theme.fg,
                selectcolor=theme.select,
                activebackground=theme.active_bg,
                activeforeground=theme.fg,
                highlightthickness=0,
            )
        if isinstance(widget, Message):
            widget.configure(bg=theme.bg, fg=theme.fg, font=theme.message_font)
        if isinstance(widget, HtmlFrame):
            widget.add_css(f"html{{background: {theme.bg}; color: {theme.fg}; font-family: {theme.default_font_family};}}")

    if style:
        style.configure("TFrame", background=theme.tab_frame_bg)
        style.configure("TNotebook", background=theme.tab_frame_bg)
        style.map("TNotebook.Tab", background=[("selected", theme.tab_frame_bg)])
        style.configure("TNotebook.Tab", background=theme.tab_bg, foreground=theme.fg)

    default_font = font.nametofont("TkDefaultFont")
    default_font.configure(family=theme.default_font_family, size=theme.default_font_size)

    heading_font = font.nametofont("TkHeadingFont")
    heading_font.configure(family=theme.heading_font_family, size=15, weight="normal")

    for widget in all_children(root):
        try:
            if widget["state"] == "disabled":
                widget.configure(bg=theme.disabled_bg)
        except TclError:
            pass
