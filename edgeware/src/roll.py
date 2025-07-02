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

import random
from collections.abc import Callable
from dataclasses import dataclass

from config.settings import Settings


@dataclass
class RollTarget:
    function: Callable[[], None]
    chance: Callable[[], int]

    def roll(self) -> None:
        if roll(self.chance()):
            self.function()


def roll_targets(settings: Settings, targets: list[RollTarget]) -> None:
    if settings.single_mode:
        try:
            function = random.choices(list(map(lambda target: target.function, targets)), list(map(lambda target: target.chance, targets)), k=1)[0]
        except ValueError:
            function = targets[0].function  # Exception thrown when all chances are 0
        function()
    else:
        for target in targets:
            target.roll()


def roll(chance: int | float) -> bool:
    """Chance is either an integer between 0 and 100 or a float between 0 and 1"""
    return (random.randint(1, 100) if isinstance(chance, int) else random.random()) <= chance
