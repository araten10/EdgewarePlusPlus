import hashlib
import os
import random
import shutil
import time
from pathlib import Path
from tkinter import Tk

import filetype
from pack import Pack
from paths import Data
from settings import Settings
from state import State


def filter_avoid_list(settings: Settings, dirs: list[str]) -> None:
    for dir in dirs.copy():
        if dir in settings.drive_avoid_list or dir.startswith(('.', '$')):
            dirs.remove(dir)


def fill_drive(root: Tk, settings: Settings, pack: Pack, state: State) -> None:
    if not settings.fill_drive or state.fill_number >= 8:
        return
    state.fill_number += 1

    paths = []
    for path, dirs, files in os.walk(settings.drive_path):
        filter_avoid_list(settings, dirs)
        paths.append(Path(path))
    if settings.random_fill:
        random.shuffle(paths)

    def fill() -> None:
        if len(paths) == 0:
            state.fill_number -= 1
            return

        path = paths.pop(0)
        for n in range(random.randint(3, 6)):
            image = pack.random_image()

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
                backup = backups / image.relative_to(Path(settings.drive_path))
                backup.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(image, backup)
                shutil.copyfile(pack.random_image(), image)
