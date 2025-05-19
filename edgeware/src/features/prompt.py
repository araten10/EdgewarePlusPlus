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

from tkinter import Button, Label, Text, Toplevel

import os_utils
import utils
from config.settings import Settings
from pack import Pack
from state import State


class Prompt(Toplevel):
    def __init__(self, settings: Settings, pack: Pack, state: State) -> None:
        self.prompt = pack.random_prompt()
        self.state = state
        if not self.should_init():
            return
        super().__init__()

        self.attributes("-topmost", True)
        os_utils.set_borderless(self)
        self.configure(background=settings.theme.bg)

        monitor = utils.primary_monitor()
        width = monitor.width // 4
        height = monitor.height // 2
        x = monitor.x + (monitor.width - width) // 2
        y = monitor.y + (monitor.height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        Label(self, text="\n" + pack.index.default.prompt_command + "\n", fg=settings.theme.fg, bg=settings.theme.bg, font=settings.theme.font).pack()

        Label(self, text=self.prompt, wraplength=width, fg=settings.theme.fg, bg=settings.theme.bg, font=settings.theme.font).pack()

        input = Text(self, fg=settings.theme.text_fg, bg=settings.theme.text_bg)
        input.pack()
        button = Button(
            self,
            text=pack.index.default.prompt_submit,
            command=lambda: self.submit(settings.prompt_max_mistakes, self.prompt, input.get(1.0, "end-1c")),
            fg=settings.theme.fg,
            bg=settings.theme.bg,
            activeforeground=settings.theme.fg,
            activebackground=settings.theme.bg,
            font=settings.theme.font,
        )
        button.place(x=-10, y=-10, relx=1, rely=1, anchor="se")

    def should_init(self) -> bool:
        if not self.state.prompt_active and self.prompt:
            self.state.prompt_active = True
            return True
        return False

    # Checks that the number of mistakes is at most max_mistakes and if so,
    # closes the prompt window. The number of mistakes is computed as the edit
    # (Levenshtein) distance between a and b.
    # https://en.wikipedia.org/wiki/Levenshtein_distance
    def submit(self, max_mistakes: int, a: str, b: str) -> None:
        d = [[j for j in range(0, len(b) + 1)]] + [[i] for i in range(1, len(a) + 1)]

        for j in range(1, len(b) + 1):
            for i in range(1, len(a) + 1):
                d[i].append(
                    min(
                        d[i - 1][j] + 1,
                        d[i][j - 1] + 1,
                        d[i - 1][j - 1] + (0 if a[i - 1] == b[j - 1] else 1)
                    )
                )  # fmt: skip

        if d[len(a)][len(b)] <= max_mistakes:
            self.destroy()
            self.state.prompt_active = False
