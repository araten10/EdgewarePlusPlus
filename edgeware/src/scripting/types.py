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

from dataclasses import dataclass
from typing import Callable, Protocol

type LuaValue = int | float | bool | str | None | LuaFunction | LuaTable
type LuaTable = dict[str | int, LuaValue]
type EvalFunction = Callable[[Environment], LuaValue]


class LuaError(Exception):
    pass


# For type hints, full definition is in environment.py
class Environment:
    pass


# Created by return statements in blocks, extracted in function calls
@dataclass
class ReturnValue:
    inner: LuaValue


class LuaFunction(Protocol):
    def __call__(self, env: Environment, *args: LuaValue) -> ReturnValue | None: ...
