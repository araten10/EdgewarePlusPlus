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

import logging

from paths import DEFAULT_PACK_PATH, Data
from voluptuous.error import Invalid

from config import load_config, load_default_config
from config.items import CONFIG_ITEMS


class Settings:
    def __init__(self) -> None:
        self.config = load_config()
        self.load_settings()
        logging.info(f"Config loaded: {self.config}")

    def load_settings(self) -> None:
        default_config = load_default_config()
        for name, item in CONFIG_ITEMS.items():
            if not item.setting:
                continue
            value = self.config[item.key]

            try:
                item.schema(value)
            except Invalid:
                default_value = default_config[item.key]
                logging.warning(f'Invalid value "{value}" for config "{item.key}", using default value "{default_value}"')
                value = default_value

            setattr(self, name, item.setting(value))

        self.pack_path = Data.PACKS / self.pack_path if self.pack_path else DEFAULT_PACK_PATH
        self.hibernate_fix_wallpaper = self.hibernate_fix_wallpaper and self.hibernate_mode

        import os_utils  # Circular import

        self.clickthrough_enabled = self.clickthrough_enabled and os_utils.is_windows()
