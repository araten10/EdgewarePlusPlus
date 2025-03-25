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

import yaml
from legacy import schemas
from paths import Build
from utils import validate, write_json


def write_media(build: Build, media: dict[str, [str]]) -> set[str]:
    write_json(media, build.media)
    return set(media.keys())


def write_captions(pack: yaml.Node, build: Build) -> set[str]:
    if not validate(pack, "captions", schemas.CAPTION):
        logging.info("Skipping captions.json")
        return set()

    captions = {
        "subtext": pack["captions"]["close-text"],
        "default": pack["captions"]["default-captions"],
        "prefix": [],
        "prefix_settings": {},
    }

    denial = pack["captions"].get("denial", None)
    if denial:
        captions["denial"] = denial

    subliminal_messages = pack["captions"].get("subliminal-messages", None)
    if subliminal_messages:
        captions["subliminals"] = subliminal_messages

    notifications = pack["captions"].get("notifications", None)
    if notifications:
        captions["notifications"] = notifications

    prefixes = pack["captions"]["prefixes"]
    if prefixes:
        for prefix in prefixes:
            prefix_name = prefix["name"]

            captions["prefix"].append(prefix_name)
            captions[prefix_name] = prefix["captions"]

            prefix_settings = {}
            if "chance" in prefix:
                prefix_settings["chance"] = prefix["chance"]
            if "max-clicks" in prefix:
                prefix_settings["max"] = prefix["max-clicks"]

            if prefix_settings:
                captions["prefix_settings"][prefix_name] = prefix_settings

    write_json(captions, build.captions)
    return set(captions["prefix"])


def write_prompt(pack: yaml.Node, build: Build) -> set[str]:
    if not validate(pack, "prompt", schemas.PROMPT):
        logging.info("Skipping prompt.json")
        return set()

    prompt = {
        "subtext": pack["prompt"]["submit-text"],
        "minLen": pack["prompt"]["minimum-length"],
        "maxLen": pack["prompt"]["maximum-length"],
        "moods": [],
        "freqList": [],
    }

    command = pack["prompt"].get("command", None)
    if command:
        prompt["commandtext"] = command

    default = pack["prompt"]["default-prompts"]
    if default["prompts"]:
        prompt["moods"].append("default")
        prompt["freqList"].append(default["weight"])
        prompt["default"] = default["prompts"]

    moods = pack["prompt"]["moods"]
    if moods:
        for mood in moods:
            mood_name = mood["name"]

            prompt["moods"].append(mood_name)
            prompt["freqList"].append(mood["weight"])
            prompt[mood_name] = mood["prompts"]

    write_json(prompt, build.prompt)
    return set(prompt["moods"])


def write_web(pack: yaml.Node, build: Build) -> set[str]:
    if not validate(pack, "web", schemas.WEB):
        logging.info("Skipping web.json")
        return set()

    web = {"urls": [], "moods": [], "args": []}

    for url in pack["web"]["urls"]:
        web["urls"].append(url["url"])
        web["moods"].append(url["mood"])

        args_string = ""
        if "args" in url:
            for arg in url["args"]:
                if "," in arg:
                    logging.error(f"Web args must not contain commas, invalid arg: {arg}")
                else:
                    if args_string != "":
                        args_string += ","
                    args_string += f"{arg}"

        web["args"].append(args_string)

    write_json(web, build.web)
    return set(web["moods"])
