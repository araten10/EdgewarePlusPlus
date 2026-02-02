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

from scripting.types import Environment, LuaValue


class Environment:
    def __init__(self, scope: dict[str, LuaValue], external: Environment | None = None, closure: set[str] | None = None) -> None:
        self.scope = scope
        self.external = external
        self.closure = closure

    def is_global(self) -> bool:
        return self.external is None

    # Find the scope in which a variable is defined
    def find(self, name: str, closure: set[str] | None = None) -> dict[str, LuaValue]:
        if self.is_global():
            return self.scope

        in_scope = name in self.scope and (closure is None or name in closure)
        next_closure = closure if closure is not None else self.closure
        return self.scope if in_scope else self.external.find(name, next_closure)

    def get(self, name: str) -> LuaValue:
        return self.find(name).get(name)

    def define(self, name: str, value: LuaValue) -> None:
        self.scope[name] = value

    def assign(self, name: str, value: LuaValue) -> None:
        self.find(name)[name] = value
