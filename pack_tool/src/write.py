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

import json
import logging
from pathlib import Path

import schemas
import yaml
from paths import Build


def write_json(data: dict, path: Path) -> None:
    logging.info(f"Writing {path.name}")
    with open(path, "w") as f:
        json.dump(data, f, indent=2)


def write_info(pack: yaml.Node, build: Build) -> None:
    if not pack["info"]["generate"]:
        logging.info("Skipping info.json")
        return

    schemas.INFO(pack["info"])

    info = {
        "name": pack["info"]["name"],
        "id": pack["info"]["id"],
        "creator": pack["info"]["creator"],
        "version": pack["info"]["version"],
        "description": pack["info"]["description"].strip(),
    }

    write_json(info, build.info)


def write_discord(pack: yaml.Node, build: Build) -> None:
    if not pack["discord"]["generate"]:
        logging.info("Skipping discord.dat")
        return

    schemas.DISCORD(pack["discord"])

    with open(build.discord, "w") as f:
        logging.info("Writing discord.dat")
        f.write(pack["discord"]["status"])


def write_index(pack: yaml.Node, build: Build, media: dict[str, [str]]) -> set[str]:
    if not pack["index"]["generate"]:
        logging.info("Skipping index.json")
        return set()

    schemas.INDEX(pack["index"])

    index = {
        "default": {},
        "moods": [],
    }

    def set_if_defined(src: yaml.Node, src_key: str, dest: dict, dest_key: str) -> bool:
        if src_key in src:
            dest[dest_key] = src[src_key]
            return True
        return False

    def load_base(yaml_base: yaml.Node, json_base: dict) -> None:
        set_if_defined(yaml_base, "max-clicks", json_base, "maxClicks")
        set_if_defined(yaml_base, "captions", json_base, "captions")
        set_if_defined(yaml_base, "denial", json_base, "denial")
        set_if_defined(yaml_base, "subliminal-messages", json_base, "subliminals")
        set_if_defined(yaml_base, "notifications", json_base, "notifications")
        set_if_defined(yaml_base, "prompts", json_base, "prompts")
        if "web" in yaml_base:
            json_base["web"] = []
            json_base["webArgs"] = []
            for web in yaml_base["web"]:
                json_base["web"].append(web["url"])
                json_base["webArgs"].append(web.get("args", []))

    yaml_default = pack["index"]["default"]
    json_default = index["default"]
    load_base(yaml_default, json_default)
    set_if_defined(yaml_default, "popup-close", json_default, "popupClose")
    set_if_defined(yaml_default, "prompt-command", json_default, "promptCommand")
    set_if_defined(yaml_default, "prompt-submit", json_default, "promptSubmit")
    set_if_defined(yaml_default, "prompt-min-length", json_default, "promptMinLength")
    set_if_defined(yaml_default, "prompt-max-length", json_default, "promptMaxLength")

    media = media.copy()  # We don't want to modify the original media dict
    for yaml_mood in pack["index"]["moods"]:
        mood = yaml_mood["mood"]
        json_mood = {"mood": mood}
        load_base(yaml_mood, json_mood)
        if set_if_defined(media, mood, json_mood, "media"):
            del media[mood]
        index["moods"].append(json_mood)

    for mood in media:
        index["moods"].append({"mood": mood, "media": media[mood]})

    write_json(index, build.index)
    return set(map(lambda mood: mood["mood"], index["moods"]))


def write_corruption(pack: yaml.Node, build: Build, moods: set[str]) -> None:
    if not pack["corruption"]["generate"]:
        logging.info("Skipping corruption.json")
        return

    schemas.CORRUPTION(pack["corruption"])

    corruption = {"moods": {}, "wallpapers": {}, "config": {}}

    active_moods = set()
    for i, level in enumerate(pack["corruption"]["levels"]):
        n = str(i + 1)
        corruption["moods"][n] = {}

        remove = []
        if "remove-moods" in level:
            for mood in level["remove-moods"]:
                if mood in active_moods:
                    remove.append(mood)
                    active_moods.remove(mood)
                else:
                    logging.warning(f"Corruption level {n} is trying to remove an inactive mood {mood}, skipping")
        corruption["moods"][n]["remove"] = remove

        add = []
        if "add-moods" in level:
            for mood in level["add-moods"]:
                if mood in moods:
                    add.append(mood)
                    active_moods.add(mood)
                else:
                    logging.warning(f"Corruption level {n} is trying to add a nonexistent mood {mood}, skipping")
        corruption["moods"][n]["add"] = add

        if "wallpaper" in level:
            corruption["wallpapers"][n] = level["wallpaper"]

        if "config" in level:
            corruption["config"][n] = level["config"]

    write_json(corruption, build.corruption)


# TODO: config.json
