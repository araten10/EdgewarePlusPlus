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

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

import pyglet
import pystray


@dataclass
class Subject:
    value: Any
    observers: list[Callable[[], None]] = field(default_factory=list)

    def notify(self) -> None:
        for observer in self.observers:
            observer()

    def attach(self, observer: Callable[[], None]) -> None:
        self.observers.append(observer)


@dataclass
class State:
    fill_number = 0
    _popup_number = Subject(0)
    prompt_active = False
    video_number = 0

    audio_players: list[pyglet.media.Player] = field(default_factory=list)

    # popup_id -> (width, height, x, y)
    popup_geometries: dict[int, (int, int, int, int)] = field(default_factory=dict)
    _next_popup_id = 0

    panic_lockout_active = False

    _hibernate_active = Subject(False)
    hibernate_id = None
    pump_scare = False

    corruption_level = 1
    corruption_time_start = 0  # Milliseconds
    corruption_popup_number = 0
    corruption_launches_number = 1

    tray: pystray.Icon | None = None

    alt_held = False

    @property
    def popup_number(self) -> int:
        return self._popup_number.value

    @popup_number.setter
    def popup_number(self, value: int) -> None:
        self._popup_number.value = value
        self._popup_number.notify()

    @property
    def hibernate_active(self) -> bool:
        return self._hibernate_active.value

    @hibernate_active.setter
    def hibernate_active(self, value: bool) -> None:
        self._hibernate_active.value = value
        self._hibernate_active.notify()

    def get_popup_id(self) -> int:
        id = self._next_popup_id
        self._next_popup_id += 1
        return id
