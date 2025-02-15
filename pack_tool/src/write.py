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

    base_mapping = [
        ("max-clicks", "maxClicks"),
        ("captions", "captions"),
        ("denial", "denial"),
        ("subliminal-messages", "subliminals"),
        ("notifications", "notifications"),
        ("prompts", "prompts"),
    ]

    default_mapping = [
        ("popup-close", "popupClose"),
        ("prompt-command", "promptCommand"),
        ("prompt-submit", "promptSubmit"),
        ("prompt-min-length", "promptMinLength"),
        ("prompt-max-length", "promptMaxLength"),
    ]

    def load_base(yaml_base: yaml.Node, json_base: dict) -> None:
        for yaml_key, json_key in base_mapping:
            value = yaml_base.get(yaml_key)
            if value is not None:
                json_base[json_key] = value

        if "web" in yaml_base:
            json_base["web"] = []
            json_base["webArgs"] = []
            for web in yaml_base["web"]:
                json_base["web"].append(web["url"])
                json_base["webArgs"].append(web.get("args", []))

    load_base(pack["index"]["default"], index["default"])
    for yaml_key, json_key in default_mapping:
        value = pack["index"]["default"].get(yaml_key)
        if value is not None:
            index["default"][json_key] = value

    media = media.copy()  # We don't want to modify the original media dict
    for yaml_mood in pack["index"]["moods"]:
        mood_name = yaml_mood["mood"]
        json_mood = {"mood": mood_name}
        load_base(yaml_mood, json_mood)

        media_list = media.get(mood_name)
        if media_list is not None:
            json_mood["media"] = media_list
            del media[mood_name]

        index["moods"].append(json_mood)

    for mood_name in media:
        index["moods"].append({"mood": mood_name, "media": media[mood_name]})

    write_json(index, build.index)
    return set(map(lambda mood: mood["mood"], index["moods"]))


def write_legacy(pack: yaml.Node, build: Build, media: dict[str, [str]]) -> None:
    if not pack["index"]["generate"]:
        logging.info("Skipping legacy JSON files")
        return set()

    schemas.INDEX(pack["index"])

    pack["index"]["default"]

    captions = {
        "default": [],
        "prefix": [],
        "prefix_settings": {},
    }

    prompt = {
        "minLen": 1,
        "maxLen": 1,
        "moods": [],
        "freqList": [],
    }

    web = {"urls": [], "moods": [], "args": []}

    special_mapping = [("denial", "denial"), ("subliminal-messages", "subliminals"), ("notifications", "notifications")]

    default_mapping = [
        ("popup-close", "subtext", captions),
        ("prompt-command", "commandtext", prompt),
        ("prompt-submit", "subtext", prompt),
        ("prompt-min-length", "minLen", prompt),
        ("prompt-max-length", "maxLen", prompt),
    ]

    def load_base(base: yaml.Node, mood_name: str = "default") -> None:
        if "max-clicks" in base:
            if mood_name != "default" and mood_name not in captions["prefix"]:
                captions["prefix"].append(mood_name)
            captions["prefix_settings"][mood_name] = {"max": base["max-clicks"]}

        if "captions" in base:
            if mood_name != "default" and mood_name not in captions["prefix"]:
                captions["prefix"].append(mood_name)
            captions[mood_name] = base["captions"]

        for yaml_key, json_key in special_mapping:
            value = base.get(yaml_key)
            if value is not None:
                if json_key not in captions:
                    captions[json_key] = []
                captions[json_key].extend(value)

        if "prompts" in base:
            prompt["moods"].append(mood_name)
            prompt[mood_name] = base["prompts"]
            prompt["freqList"].append(1)

        if "web" in base:
            for yaml_web in base["web"]:
                web["urls"].append(yaml_web["url"])
                web["moods"].append(mood_name)

                args_string = ""
                for arg in yaml_web.get("args", []):
                    if "," in arg:
                        logging.error(f"Legacy web args must not contain commas, invalid arg: {arg}")
                    else:
                        if args_string != "":
                            args_string += ","
                        args_string += f"{arg}"

                web["args"].append(args_string)

    load_base(pack["index"]["default"])
    for yaml_key, json_key, json_dict in default_mapping:
        value = pack["index"]["default"].get(yaml_key)
        if value is not None:
            json_dict[json_key] = value

    for mood in pack["index"]["moods"]:
        load_base(mood, mood["mood"])

    write_json(media, build.media)
    write_json(captions, build.captions)
    write_json(prompt, build.prompt)
    write_json(web, build.web)


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
