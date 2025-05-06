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

from tkinter import (
    Button,
    Checkbutton,
    Frame,
    IntVar,
    Label,
    Message,
    Misc,
    OptionMenu,
    Scale,
    StringVar,
    font,
    simpledialog,
)
from typing import Tuple

from config_window.utils import assign, set_widget_states
from config_window.vars import ConfigVar

PAD = 4


class ConfigScale(Frame):
    def __init__(self, master: Misc, label: str, variable: IntVar, from_: int, to: int, enabled: Tuple[ConfigVar, int | bool | str] | None = None) -> None:
        super().__init__(master, borderwidth=1, relief="groove")

        inner = Frame(self)
        inner.pack(padx=PAD, pady=PAD, fill="both", expand=True)
        Scale(inner, label=label, orient="horizontal", highlightthickness=0, variable=variable, from_=from_, to=to).pack(fill="x", expand=True)
        Button(inner, text="Manual", command=lambda: assign(variable, simpledialog.askinteger(f"{label}", prompt=f"[{from_}-{to}]: "))).pack(
            fill="x", expand=True, pady=[4, 0]
        )

        if enabled:
            toggle, value = enabled
            set_state = lambda *args: set_widget_states(toggle.get() == value, [self])
            set_state()
            toggle.trace_add("write", set_state)

    def pack(self) -> None:
        super().pack(padx=PAD, pady=PAD, side="left", expand=True, fill="x")


class ConfigDropdown(Frame):
    def __init__(self, master: Misc, variable: StringVar, items: dict[str, str]) -> None:
        super().__init__(master, borderwidth=1, relief="groove")
        self.items = items

        inner = Frame(self)
        inner.pack(padx=PAD, pady=PAD, fill="both", expand=True)
        menu = OptionMenu(inner, variable, *items.keys(), command=self.on_change)
        menu.configure(width=9,highlightthickness= 0)
        menu.pack(side="left")
        self.label = Label(inner, wraplength=150, height=3, width=22)
        self.label.pack(side="left", fill="y")

        self.on_change(variable.get())

    def on_change(self, key: str) -> None:
        self.label.configure(text=self.items[key])

    def pack(self) -> None:
        super().pack(padx=PAD, pady=PAD, side="left", expand=True)


class ConfigToggle(Checkbutton):
    def __init__(self, master: Misc, text: str, **kwargs) -> None:
        super().__init__(master, text=text, borderwidth=1, relief="groove", **kwargs)

    def pack(self) -> None:
        super().pack(padx=PAD, pady=PAD, ipadx=PAD, ipady=PAD, side="left", expand=True)


class ConfigSection(Frame):
    def __init__(self, master: Misc, title: str, message: str = "") -> None:
        super().__init__(master, borderwidth=2, relief="raised")

        title_font = font.Font(font="Default")
        title_font.configure(size=15)

        Label(self, text=title, font=title_font).pack()
        Message(self, text=message, width=675).pack(fill="both")

    def pack(self) -> None:
        super().pack(padx=8, pady=8, fill="x")


class ConfigRow(Frame):
    def pack(self) -> None:
        super().pack(fill="x")
