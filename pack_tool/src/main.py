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

import argparse
import logging
import os
import platform
import shutil
import sys

import yaml
from copy_files import copy_hypno, copy_icon, copy_loading_splash, copy_media, copy_wallpapers
from legacy.write_files import write_captions, write_media, write_prompt, write_web
from paths import DEFAULT_PACK, PACK_TOOL_ROOT, TEST_BUILD_ROOT, Build, Source
from write_files import write_config, write_corruption, write_discord, write_index, write_info, write_legacy


def new_pack(source: Source) -> None:
    if source.root.exists():
        logging.error(f"{source.root} already exists")
    else:
        (source.media / "default").mkdir(parents=True, exist_ok=True)
        source.hypno.mkdir(parents=True, exist_ok=True)
        source.wallpapers.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DEFAULT_PACK, source.pack)

        logging.info(f"Created a template for a new pack at {source.root}")


def build_pack(args: argparse.Namespace, source: Source, build: Build) -> None:
    if args.test_pack and build.root.exists():
        shutil.rmtree(build.root)
    build.root.mkdir(parents=True, exist_ok=True)

    # You can't make symlinks on Windows with regular permissions?
    # OSError: [WinError 1314] A required privilege is not held by the client
    copy = os.symlink if (args.test_pack and platform.system() != "Windows") else shutil.copyfile
    media = copy_media(copy, source, build, args.compress_images and not args.test_pack, args.compress_videos and not args.test_pack, args.rename)
    copy_hypno(copy, source, build, args.skip_legacy)
    copy_wallpapers(copy, source, build)
    copy_icon(copy, source, build)
    copy_loading_splash(copy, source, build)

    with open(source.pack, "r") as f:
        pack = yaml.safe_load(f)

        write_info(pack, build)
        write_discord(pack, build)

        if "index" in pack:
            moods = write_index(pack, build, media)
            if not args.skip_legacy:
                write_legacy(pack, build, media)
        else:
            logging.info("Index not found in pack.yml, attempting to read legacy formats")
            moods = write_media(build, media)
            moods = moods.union(write_captions(pack, build))
            moods = moods.union(write_prompt(pack, build))
            moods = moods.union(write_web(pack, build))

        write_config(pack, build)
        write_corruption(pack, build, moods)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="pack source directory")
    parser.add_argument("-o", "--output", default="build", help="output directory name")
    parser.add_argument("-t", "--test-pack", action="store_true", help="build and export a test version of the pack to Edgeware")
    parser.add_argument("-n", "--new", action="store_true", help="create a new pack template and exit")
    parser.add_argument("-s", "--skip-legacy", action="store_true", help="don't generate fallback legacy files")
    parser.add_argument("-v", "--compress-videos", action="store_true", help="compresses video files using FFmpeg")
    parser.add_argument("-i", "--compress-images", action="store_true", help="compresses image files using Pillow")
    parser.add_argument("-r", "--rename", action="store_true", help="appends mood name to files for caption compatibility with the original Edgeware")
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    source = Source(PACK_TOOL_ROOT / args.source)
    build = Build(TEST_BUILD_ROOT if args.test_pack else PACK_TOOL_ROOT / args.output)

    if args.new:
        new_pack(source)
    elif source.root.is_dir():
        build_pack(args, source, build)
    else:
        logging.error(f"{source.root} does not exist or is not a directory")
