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

import json
import logging
import os
import shutil
from json.decoder import JSONDecodeError
from tkinter import BooleanVar, IntVar, StringVar, messagebox, simpledialog

from paths import Data

from config.vars import Vars
from config.window.utils import confirm_overwrite


def list_presets() -> list[str]:
    Data.PRESETS.mkdir(parents=True, exist_ok=True)
    return [preset.split(".")[0] for preset in os.listdir(Data.PRESETS) if preset.endswith(".cfg")]


def load_preset(name: str) -> dict:
    preset = Data.PRESETS / f"{name}.cfg"
    try:
        with open(preset, "r") as f:
            return json.loads(f.read())
    except FileNotFoundError:
        logging.info(f"{preset.name} not found.")
    except JSONDecodeError as e:
        logging.warning(f"{preset.name} is not valid JSON. Reason: {e}")

    return {}


def load_preset_description(name: str) -> str:
    description = Data.PRESETS / f"{name}.txt"
    if not description.is_file():
        return "This preset has no description file."

    with open(description, "r") as f:
        return f.read()


def save_preset() -> str | None:
    """If successful, returns the name of the saved preset"""
    name = simpledialog.askstring("Save Preset", "Preset name")
    if not name:
        messagebox.showinfo("Cancelled", "Preset name not provided.")
        return None

    path = Data.PRESETS / f"{name}.cfg"
    if not confirm_overwrite(path):
        messagebox.showinfo("Cancelled", "Pack import cancelled.")
        return None

    shutil.copyfile(Data.CONFIG, path)
    messagebox.showinfo("Done", f'Preset saved to "{path}".')
    return name


def apply_preset(preset: dict, vars: Vars, select: list[str] | None = None) -> None:
    danger = vars.preset_danger.get()
    select = select or vars.entries.keys()

    for key, value in preset.items():
        if key not in select:
            continue

        var = vars.entries[key]
        match var:
            case IntVar():
                var.set(int(value))
            case BooleanVar():
                var.set(value == 1)
            case StringVar():
                var.set(value.strip())

    if danger:
        vars.safe_mode.set(True)

    messagebox.showinfo(
        "Done",
        "Config been loaded successfully.\n\nChanges have not been automatically saved. "
        "You may choose to look over the new settings before either saving or exiting the program.",
    )
