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
from typing import Callable
import logging

import os_utils
import utils
from config.settings import Settings
from pack import Pack
from state import State


class Prompt(Toplevel):
    def __init__(self, settings: Settings, pack: Pack, state: State, prompt: str | None = None, on_close: Callable[[], None] | None = None) -> None:
        self.prompt = prompt or pack.random_prompt()
        self.state = state
        if not self.should_init():
            return
        super().__init__()

        self.on_close = on_close
        self.settings = settings

        # NOTE: The global panic keyboard listener must stay alive while the Prompt
        # is open.  Previously we stopped it here to work around macOS focus issues,
        # but that killed the panic hotkey (a regression) and was only restored on
        # a successful submit.  We keep the listener running and instead fix focus via
        # AppKit activation so the user can both type AND trigger panic.

        self.attributes("-topmost", True)
        os_utils.set_borderless(self)
        self.configure(background=settings.theme.bg)

        monitor = utils.primary_monitor()
        width = monitor.width // 4
        height = monitor.height // 2
        x = monitor.x + (monitor.width - width) // 2
        y = monitor.y + (monitor.height - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        Label(
            self,
            text="\n" + pack.index.default.prompt_command + "\n",
            fg=settings.theme.fg,
            bg=settings.theme.bg,
            font=(settings.theme.font, settings.theme.font_size),
        ).pack()

        Label(self, text=self.prompt, wraplength=width, fg=settings.theme.fg, bg=settings.theme.bg, font=(settings.theme.font, settings.theme.font_size)).pack()

        input = Text(self, fg=settings.theme.text_fg, bg=settings.theme.text_bg)
        input.pack()

        self.update_idletasks()
        self.lift()

        # NOTE: Do NOT call grab_set() here.  grab_set() makes this window a
        # full-app modal that steals all input, which breaks the close buttons of
        # every other popup while the Prompt is open.  We keep it focusable and
        # topmost instead, so keyboard entry works but other windows stay usable.

        # Prompt windows stay focusable (not overrideredirect), so they can accept
        # text input. Activate the app and focus the Text widget once the window is
        # mapped.
        self.after(50, lambda: os_utils.focus_window(self))
        input.focus_set()

        button = Button(
            self,
            text=pack.index.default.prompt_submit,
            command=lambda: self.submit(settings.prompt_max_mistakes, self.prompt, input.get(1.0, "end-1c")),
            fg=settings.theme.fg,
            bg=settings.theme.bg,
            activeforeground=settings.theme.fg,
            activebackground=settings.theme.bg,
            font=(settings.theme.font, settings.theme.font_size),
        )
        button.place(x=-10, y=-10, relx=1, rely=1, anchor="se")

    def should_init(self) -> bool:
        if not self.state.prompt_active and self.prompt:
            self.state.prompt_active = True
            return True
        return False

    def destroy(self) -> None:
        """Close the Prompt, guaranteeing the panic keyboard listener survives.

        The global hotkey listener is kept alive while the Prompt is open; this is a
        safety net that restarts it only if an already-started listener was killed by
        any other code path.  It never kills, duplicates, or lazily starts the
        listener.
        """
        super().destroy()
        self.state.prompt_active = False
        try:
            from features.misc import handle_keyboard
            import sys
            if sys.platform == "darwin":
                listener = getattr(self.state, "keyboard_listener", None)
                # The stored listener is a DarwinKeyboardListener (in-process
                # CGEventTap on macOS) or a pynput Listener subprocess target on
                # other platforms; check liveness in a duck-typed way.
                alive = False
                if listener is not None:
                    try:
                        alive = listener.is_alive()
                    except (AttributeError, TypeError):
                        alive = bool(getattr(listener, "_running", False))
                if not alive:
                    logging.info("PROMPT: keyboard listener was down after close - restarting")
                    handle_keyboard(self.master, self.settings, self.state)
            else:
                proc = self.state.keyboard_process
                if (proc is not None and not proc.is_alive()) and getattr(self, "master", None) is not None:
                    logging.info("PROMPT: keyboard listener was down after close - restarting")
                    handle_keyboard(self.master, self.settings, self.state)
        except Exception as e:
            logging.warning(f"PROMPT: failed to verify/restart keyboard listener: {e}")

    # Checks that the number of mistakes is at most max_mistakes and if so,
    # closes the prompt window. The number of mistakes is computed as the edit
    # (Levenshtein) distance between a and b.
    # https://en.wikipedia.org/wiki/Levenshtein_distance
    def submit(self, max_mistakes: int, a: str, b: str) -> None:
        logging.info(f"PROMPT: submit called, prompt={a!r}, input={b!r}, max_mistakes={max_mistakes}")
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
            logging.info(f"PROMPT: accepted (distance={d[len(a)][len(b)]})")
            self.destroy()
            self.state.prompt_active = False
            if self.on_close:
                self.on_close()
        else:
            logging.info(f"PROMPT: rejected (distance={d[len(a)][len(b)]} > {max_mistakes})")
