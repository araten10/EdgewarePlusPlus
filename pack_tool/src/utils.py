# Copyright (C) 2024 Marigold & Araten
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import logging
from pathlib import Path

import yaml
from voluptuous import Schema
from voluptuous.error import Invalid


def write_json(data: dict, path: Path) -> None:
    logging.info(f"Writing {path.name}")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def validate(pack: yaml.Node, key: str, schema: Schema) -> bool:
    try:
        data = pack.get(key)
        schema(data)
        return data["generate"]
    except Invalid as e:
        logging.error(f"{key} format is invalid. Reason: {e}")
        return False
