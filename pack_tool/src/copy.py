# Copyright (C) 2024 LewdDevelopment
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

import logging
import os
import shutil
import subprocess
from pathlib import Path

import filetype
from paths import Build, Source
from PIL import Image
from pyffmpeg import FFmpeg


def copy_media(source: Source, build: Build, compimg: bool, compvid: bool, rename: bool) -> dict[str, [str]]:
    media = {}

    if not source.media.is_dir():
        logging.error(f"{source.media} does not exist or is not a directory, unable to read media")
        return set()

    moods = os.listdir(source.media)
    if len(moods) == 0:
        logging.error("Media directory exists, but it is empty")
        return set()

    for mood in moods:
        mood_path = source.media / mood
        if not mood_path.is_dir():
            logging.warning(f"{mood_path} is not a directory")
            continue

        mood_media = os.listdir(mood_path)
        if len(mood_media) == 0:
            logging.warning(f"Mood directory {mood} exists, but it is empty")
            continue

        logging.info(f"Copying media from mood {mood}")
        media[mood] = []
        for filename in mood_media:
            file_path = mood_path / filename

            location = None
            copy = shutil.copyfile
            if file_path.is_file():
                if filetype.is_image(file_path):
                    location = build.image
                    # animated gifs compress down to a single frame, so they are skipped until we find a sane solution
                    if compimg and not filetype.image_match(file_path).mime == "image/gif":
                        copy = compress_image
                elif filetype.is_video(file_path):
                    location = build.video
                    # Can remove video type check once we support more filetypes for compression
                    if compvid and filetype.video_match(file_path).mime == "video/mp4":
                        copy = compress_video
                elif filetype.is_audio(file_path):
                    location = build.audio

            if location:
                location.mkdir(parents=True, exist_ok=True)
                if rename:
                    filename = mood + "_" + filename
                copy(file_path, location / filename)
                media[mood].append(filename)
            else:
                logging.warning(f"{file_path} is not an image, video, or audio file")

    return media


def compress_video(source: Path, destination: Path) -> None:
    try:
        # if h265 causes issues, change (or add setting) back down to h264
        subprocess.run(f'"{FFmpeg()._ffmpeg_file}" -y -i "{source}" -vcodec libx265 -crf 30 "{destination}"', shell=True)
    except Exception as e:
        logging.warning(f"Error compressing video: {e}")


def compress_image(source: Path, destination: Path) -> None:
    try:
        image = Image.open(source)
        image.save(destination, optimize=True, quality=85)
    except Exception as e:
        logging.warning(f"Error compressing image: {e}")


def copy_subliminals(source: Source, build: Build) -> None:
    if not source.subliminals.is_dir():
        return

    subliminals = os.listdir(source.subliminals)
    if len(subliminals) == 0:
        logging.warning("Subliminals directory exists, but it is empty")
        return

    logging.info("Copying subliminals")
    build.subliminals.mkdir(parents=True, exist_ok=True)
    for filename in subliminals:
        file_path = source.subliminals / filename
        if filetype.is_image(file_path):
            shutil.copyfile(file_path, build.subliminals / filename)
        else:
            logging.warning(f"{file_path} is not an image")


def copy_wallpapers(source: Source, build: Build) -> None:
    if not source.wallpapers.is_dir():
        logging.warning(f"{source.wallpapers} does not exist or is not a directory")
        return

    wallpapers = os.listdir(source.wallpapers)
    if len(wallpapers) == 0:
        logging.warning("Wallpaper directory exists, but it is empty")
        return

    logging.info("Copying wallpapers")
    default_found = False
    for filename in wallpapers:
        file_path = source.wallpapers / filename
        default_found = default_found or filename == "wallpaper.png"
        if filetype.is_image(file_path):
            shutil.copyfile(file_path, build.root / filename)
        else:
            logging.warning(f"{file_path} is not an image")

    if not default_found:
        logging.warning("No default wallpaper.png found")


def copy_icon(source: Source, build: Build) -> None:
    if not os.path.exists(source.icon):
        return

    if filetype.is_image(source.icon):
        logging.info("Copying icon")
        shutil.copyfile(source.icon, build.icon)
    else:
        logging.warning(f"{source.icon} is not an image")


def copy_loading_splash(source: Source, build: Build) -> None:
    loading_splash_found = False
    for extension in [".png", ".gif", ".jpg", ".jpeg", ".bmp"]:
        loading_splash_path = source.splash.with_suffix(extension)
        if not os.path.exists(loading_splash_path):
            continue

        if loading_splash_found:
            logging.warning(f"Found multiple loading splashes, ignoring {loading_splash_path}")
            continue

        if filetype.is_image(loading_splash_path):
            logging.info("Copying loading splash")
            shutil.copyfile(loading_splash_path, build.splash.with_suffix(extension))
            loading_splash_found = True
        else:
            logging.warning(f"{loading_splash_path} is not an image")
