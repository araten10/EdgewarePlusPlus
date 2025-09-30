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

import logging
import os
import subprocess
from pathlib import Path
from typing import Callable

import filetype
from paths import Build, Source
from PIL import Image
from pyffmpeg import FFmpeg

CopyFunction = Callable[[Path, Path], None]


def copy_media(copy: CopyFunction, source: Source, build: Build, compress_images: bool, compress_videos: bool, rename: bool) -> dict[str, [str]]:
    media = {}

    if not source.media.is_dir():
        logging.error(f"{source.media} does not exist or is not a directory, unable to read media")
        return media

    moods = os.listdir(source.media)
    if len(moods) == 0:
        logging.error("Media directory exists, but it is empty")
        return media

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
            if file_path.is_file():
                if filetype.is_image(file_path):
                    location = build.image
                    # animated gifs compress down to a single frame, so they are skipped until we find a sane solution
                    if compress_images and not filetype.image_match(file_path).mime == "image/gif":
                        copy = compress_image
                elif filetype.is_video(file_path):
                    location = build.video
                    # Can remove video type check once we support more filetypes for compression
                    if compress_videos and filetype.video_match(file_path).mime == "video/mp4":
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
    # If H265 causes issues, change (or add setting) back down to H264
    subprocess.run(f'"{FFmpeg()._ffmpeg_file}" -y -i "{source}" -vcodec libx265 -crf 30 "{destination}"', shell=True)


def compress_image(source: Path, destination: Path) -> None:
    image = Image.open(source)
    image.save(destination, optimize=True, quality=85)


def copy_hypno(copy: CopyFunction, source: Source, build: Build, skip_legacy: bool) -> None:
    source_dir = source.hypno
    if not source_dir.is_dir():
        logging.warning(f"{source_dir} does not exist or is not a directory, attempting to read legacy directory")

        source_dir = source.hypno_legacy
        if not source_dir.is_dir():
            logging.warning(f"{source.hypno_legacy} does not exist or is not a directory")
            return

    hypno = os.listdir(source_dir)
    if len(hypno) == 0:
        logging.warning("Hypno directory exists, but it is empty")
        return

    logging.info("Copying hypno")
    build_dirs = [build.hypno] + ([] if skip_legacy else [build.hypno_legacy])
    for build_dir in build_dirs:
        build_dir.mkdir(parents=True, exist_ok=True)
        for filename in hypno:
            file_path = source_dir / filename
            if filetype.is_image(file_path):
                copy(file_path, build_dir / filename)
            else:
                logging.warning(f"{file_path} is not an image")


def copy_wallpapers(copy: CopyFunction, source: Source, build: Build) -> None:
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
            copy(file_path, build.root / filename)
        else:
            logging.warning(f"{file_path} is not an image")

    if not default_found:
        logging.warning("No default wallpaper.png found")


def copy_icon(copy: CopyFunction, source: Source, build: Build) -> None:
    if not os.path.exists(source.icon):
        return

    if filetype.is_image(source.icon):
        logging.info("Copying icon")
        copy(source.icon, build.icon)
    else:
        logging.warning(f"{source.icon} is not an image")


def copy_loading_splash(copy: CopyFunction, source: Source, build: Build) -> None:
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
            copy(loading_splash_path, build.splash.with_suffix(extension))
            loading_splash_found = True
        else:
            logging.warning(f"{loading_splash_path} is not an image")


def copy_script(copy: CopyFunction, source: Source, build: Build) -> None:
    if not os.path.exists(source.script):
        return

    logging.info("Copying script")
    copy(source.script, build.script)
