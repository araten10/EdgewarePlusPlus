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
    Scale,
    Checkbutton,
    Frame,
    Label,
    Listbox,
    Message,
    OptionMenu,
    Scale,
    Text,
    Tk,
    font,
)

class ManualScale(tk.Frame):
    def __init__(self, label: Label, *args, **kwargs):
        super().__init__(borderwidth=1, relief="groove", *args, **kwargs)
        inner = Frame(self)
        Scale(inner, label=label, orient="horizontal").pack(fill="x", expand=True)
        Button(inner, text="Manual").pack(fill="x", expand=True, pady=[4, 0])
        inner.pack(padx=4, pady=4, fill="both", expand=True)

    def pack(self):
        super().pack(padx=4, pady=4, side="left", expand=True, fill="x")


class Toggle(tk.Checkbutton):
    def __init__(self, text: str, *args, **kwargs):
        super().__init__(text=text, borderwidth=1, relief="groove", *args, **kwargs)

    def pack(self):
        super().pack(padx=4, pady=4, ipadx=4, ipady=4, side="left", expand=True)


class Section(tk.Frame):
    def __init__(self, title: str, message: str, *args, **kwargs):
        super().__init__(borderwidth=2, relief="raised", *args, **kwargs)
        title_font = font.Font(font="Default")
        title_font.configure(size=15)
        Label(self, text=title, font=title_font).pack()
        Message(self, text=message, width=675).pack(fill="both")

    def pack(self):
        super().pack(padx=8, pady=8, fill="x")


class SettingsRow(tk.Frame):
    def pack(self):
        super().pack(fill="x")
