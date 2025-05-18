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

import hashlib
import os
import random
import shutil
import time
from pathlib import Path
from tkinter import Tk

import filetype
from config.settings import Settings
from pack import Pack
from paths import Data
from state import State


def filter_avoid_list(settings: Settings, dirs: list[str]) -> None:
    for dir in dirs.copy():
        if dir in settings.drive_avoid_list or dir[0] == ".":
            dirs.remove(dir)


def fill_drive(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if not settings.fill_drive or state.fill_number >= 8:
        return
    state.fill_number += 1

    paths = []
    for path, dirs, files in os.walk(settings.drive_path):
        filter_avoid_list(settings, dirs)
        paths.append(Path(path))

    def fill() -> None:
        if len(paths) == 0:
            state.fill_number -= 1
            return

        path = paths.pop(0)
        for n in range(random.randint(3, 6)):
            image = pack.random_image(unweighted=True)
            if not image:
                continue

            file = hashlib.md5((str(time.time()) + str(image.absolute())).encode()).hexdigest()
            location = path / (file + image.suffix)

            shutil.copyfile(image, location)

        root.after(settings.fill_delay, fill)

    fill()


def replace_images(root: Tk, settings: Settings, pack: Pack) -> None:
    if not settings.replace_images:
        return

    backups = Data.BACKUPS / time.asctime()
    for path, dirs, files in os.walk(settings.drive_path):
        filter_avoid_list(settings, dirs)

        images = []
        for file in files:
            file_path = Path(path) / file
            if filetype.is_image(file_path):
                images.append(file_path)

        if len(images) >= settings.replace_threshold:
            for image in images:
                replacement = pack.random_image(unweighted=True)
                if not replacement:
                    continue

                backup = backups / image.relative_to(Path(settings.drive_path))
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, backup)
                shutil.copyfile(replacement, image)
