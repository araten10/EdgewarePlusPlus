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

import logging
from tkinter import BooleanVar, IntVar, StringVar

from voluptuous.error import Invalid

from config import load_default_config
from config.items import CONFIG_ITEMS

ConfigVar = IntVar | BooleanVar | StringVar


class Vars:
    entries: dict[str, ConfigVar] = {}

    def __init__(self, config: dict) -> None:
        self.config = config
        default_config = load_default_config()

        self.config["packPath"] = self.config["packPath"] or "default"
        for name, item in CONFIG_ITEMS.items():
            if not item.var:
                continue
            value = self.config[item.key]

            try:
                item.schema(value)
            except Invalid:
                default_value = default_config[item.key]
                logging.warning(f'Invalid value "{value}" for config "{item.key}", using default value "{default_value}"')
                value = default_value

            setattr(self, name, self.make(item.var, item.key))

    def make(self, var_init: type[ConfigVar], key: str) -> ConfigVar:
        value = self.config[key]
        var = var_init()
        match var:
            case IntVar():
                var.set(int(value))
            case BooleanVar():
                var.set(bool(value))
            case StringVar():
                var.set(value.strip())

        self.entries[key] = var
        return var
