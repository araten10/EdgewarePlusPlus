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

from config.vars import ConfigVar
from config.window.utils import assign, set_widget_states

PAD = 4

Value = int | bool | str
EnabledTuple = Tuple[ConfigVar, Value | list[Value]]
EnabledSpec = EnabledTuple | list[EnabledTuple]


def set_enabled_when(widget: Misc, enabled: EnabledSpec) -> None:
    def to_list(value: object) -> list[object]:
        return value if isinstance(value, list) else [value]

    def set_state(*_) -> None:
        set_widget_states(all([var.get() in to_list(value) for var, value in to_list(enabled)]), [widget])

    set_state()
    for var, value in to_list(enabled):
        var.trace_add("write", set_state)


class StateFrame(Frame):
    """Frame that can be enabled and disabled for help with themes"""

    def __init__(self, master: Misc, **kwargs) -> None:
        super().__init__(master, **kwargs)
        self.state = "normal"

    def __getitem__(self, key: str) -> None:
        return self.state if key == "state" else super().__getitem__(key)

    def configure(self, state: str | None = None, **kwargs) -> None:
        self.state = state or self.state
        super().configure(**kwargs)


class ConfigScale(StateFrame):
    def __init__(self, master: Misc, label: str, variable: IntVar, from_: int, to: int, enabled: EnabledSpec | None = None) -> None:
        super().__init__(master, borderwidth=1, relief="groove")

        inner = StateFrame(self)
        inner.pack(padx=PAD, pady=PAD, fill="both", expand=True)
        Scale(inner, label=label, orient="horizontal", highlightthickness=0, variable=variable, from_=from_, to=to).pack(fill="x", expand=True)
        Button(inner, text="Manual", command=lambda: assign(variable, simpledialog.askinteger(f"{label}", prompt=f"[{from_}-{to}]: "))).pack(
            fill="x", expand=True, pady=[4, 0]
        )

        if enabled:
            set_enabled_when(self, enabled)

    def pack(self) -> None:
        super().pack(padx=PAD, pady=PAD, side="left", expand=True, fill="x")


class ConfigDropdown(Frame):
    def __init__(self, master: Misc, variable: StringVar, items: dict[str, str], height: int = 3, width: int = 22, wrap: int = 150) -> None:
        super().__init__(master, borderwidth=1, relief="groove")
        self.items = items

        inner = Frame(self)
        inner.pack(padx=PAD, pady=PAD, fill="both", expand=True)
        menu = OptionMenu(inner, variable, *items.keys(), command=self.on_change)
        menu.configure(width=9, highlightthickness=0)
        menu.pack(side="left")
        self.label = Label(inner, wraplength=wrap, height=height, width=width)
        self.label.pack(side="left", fill="y")

        self.on_change(variable.get())

    def on_change(self, key: str) -> None:
        self.label.configure(text=self.items[key])

    def pack(self) -> None:
        super().pack(padx=PAD, pady=PAD, side="left", expand=True)


class ConfigToggle(Checkbutton):
    def __init__(self, master: Misc, text: str, **kwargs) -> None:
        super().__init__(master, text=text, borderwidth=1, relief="groove", highlightthickness=0, **kwargs)

    def pack(self) -> None:
        super().pack(padx=PAD, pady=PAD, ipadx=PAD, ipady=PAD, side="left", expand=True)

    def grid(self, row: int, column: int) -> None:
        super().grid(row=row, column=column, padx=PAD, pady=PAD, ipadx=PAD, ipady=PAD, sticky="ew")
        self.master.columnconfigure(column, weight=1)


class ConfigSection(Frame):
    def __init__(self, master: Misc, title: str, message: str | None = None) -> None:
        super().__init__(master, borderwidth=2, relief="raised")

        heading_font = font.nametofont("TkHeadingFont")
        Label(self, text=title, font=heading_font).pack()

        if message:
            Message(self, text=message, width=675).pack(fill="both")

    def pack(self) -> None:
        super().pack(padx=8, pady=8, fill="x")


class ConfigRow(Frame):
    def pack(self) -> None:
        super().pack(fill="x")
