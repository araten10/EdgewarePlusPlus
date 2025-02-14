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

import argparse
import logging
import shutil
import sys
from copy import copy_icon, copy_loading_splash, copy_media, copy_subliminals, copy_wallpapers

import yaml
from paths import DEFAULT_PACK, Build, Source
from write import write_corruption, write_discord, write_index, write_info


def new_pack(source: Source) -> None:
    if source.root.exists():
        logging.error(f"{source.root} already exists")
    else:
        (source.media / "default").mkdir(parents=True, exist_ok=True)
        source.subliminals.mkdir(parents=True, exist_ok=True)
        source.wallpapers.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(DEFAULT_PACK, source.pack)

        logging.info(f"Created a template for a new pack at {source.root}")


def build_pack(args: argparse.Namespace, source: Source, build: Build) -> None:
    build.root.mkdir(parents=True, exist_ok=True)

    media = copy_media(source, build, args.compimg, args.compvid, args.rename)
    copy_subliminals(source, build)
    copy_wallpapers(source, build)
    copy_icon(source, build)
    copy_loading_splash(source, build)

    with open(source.pack, "r") as f:
        pack = yaml.safe_load(f)

        write_info(pack, build)
        write_discord(pack, build)
        moods = write_index(pack, build, media)
        write_corruption(pack, build, moods)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="pack source directory")
    parser.add_argument("-o", "--output", default="build", help="output directory name")
    parser.add_argument("-n", "--new", action="store_true", help="create a new pack template and exit")
    parser.add_argument("-v", "--compvid", action="store_true", help="compresses video files using ffmpeg")
    parser.add_argument("-i", "--compimg", action="store_true", help="compresses image files using pillow")
    parser.add_argument("-r", "--rename", action="store_true", help="appends mood name to files")
    args = parser.parse_args()

    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    source = Source(args.source)
    build = Build(args.output)

    if args.new:
        new_pack(source)
    elif source.root.is_dir():
        build_pack(args, source, build)
    else:
        logging.error(f"{source.root} does not exist or is not a directory")
