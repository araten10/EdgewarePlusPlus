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

import ast
from dataclasses import dataclass
from tkinter import BooleanVar, IntVar, StringVar
from typing import Callable, Tuple, Any

from voluptuous import All, Range, Schema, Union, Boolean

from config.themes import THEMES


# Schema definitions for validation
NONNEGATIVE = Schema(All(int, Range(min=0)))
FLOAT = Schema(All(float, Range(min=0)))
PERCENTAGE = Schema(All(int, Range(min=0, max=100)))
BOOLEAN = Schema(All(int, Range(min=0, max=1)))
STRING = Schema(str)


class DictVar:
    """A minimal variable-wrapper around a Python dict, providing .get(), .set(),
    as well as dict-like methods so that UI code can use .keys(), indexing, iteration, etc."""
    def __init__(self):
        self._value: dict[int, dict] = {}

    def get(self) -> dict[int, dict]:
        """Return a plain dict of primitive values, unwrapping any Tkinter Variables."""
        result: dict[int, dict] = {}
        for idx, settings in self._value.items():
            prim_settings: dict[str, object] = {}
            for key, val in settings.items():
                # Unwrap any Tkinter Variable into its primitive value
                prim_settings[key] = val.get() if hasattr(val, "get") and callable(val.get) else val
            result[idx] = prim_settings
        return result

    def set(self, new: dict[int, dict]) -> None:
        """Replace internal dict with a new one."""
        self._value = new

    # Dict-like interface for UI code
    def keys(self):
        return self._value.keys()

    def items(self):
        return self._value.items()

    def __getitem__(self, key):
        return self._value[key]

    def __setitem__(self, key, value):
        self._value[key] = value

    def __contains__(self, key):
        return key in self._value

    def __iter__(self):
        return iter(self._value)

    def __len__(self):
        return len(self._value)
    

def serialize_sextoys(raw: dict[int, dict[str, object]]) -> dict[int, dict[str, object]]:
    """Convert all values in the nested dict to plain Python primitives."""
    result = {}
    for idx, settings in raw.items():
        primitive_settings = {}
        for key, val in settings.items():
            if hasattr(val, "get") and callable(val.get):
                # For DoubleVar, ensure value is float
                value = val.get()
                primitive_settings[key] = float(value) if isinstance(value, float) else value
            else:
                primitive_settings[key] = val
        result[idx] = primitive_settings
    return result


def s_to_ms(value: int) -> int:
    """Convert seconds to milliseconds."""
    return value * 1000


def to_float(value: int) -> float:
    """Convert percentage integer to float fraction."""
    return value / 100


def negation(value: bool) -> bool:
    """Return the logical negation of the given boolean."""
    return not value


@dataclass
class Item:
    key: str
    schema: Callable
    var: Callable | None
    setting: Callable | None

    # TODO: Find a better approach for these flags
    block: bool = False
    danger: bool = False
    safe_range: Tuple[int | None, int | None] | None = None  # Range outside which value is considered dangerous


# fmt: off
CONFIG_ITEMS = {
    # Startup
    "pack_path": Item("packPath", Schema(Union(str, None)), StringVar, lambda value: value),
    "theme": Item("themeType", Schema(Union("Original", "Dark", "The One", "Ransom", "Goth", "Bimbo")), StringVar, lambda value: THEMES[value]),
    "theme_ignore_config": Item("themeNoConfig", BOOLEAN, BooleanVar, None, block=True),
    # ... rest of items unchanged ...
}
# fmt: on
