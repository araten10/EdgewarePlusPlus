import json
import logging
import os
from collections.abc import Callable
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TypeVar

from paths import Data, Resource
from utils import utils
from voluptuous import ALLOW_EXTRA, PREVENT_EXTRA, All, Any, Equal, In, Length, Number, Optional, Range, Schema, Url
from voluptuous.error import Invalid

from pack.data import ActiveMoods, CaptionMood, Captions, CorruptionLevel, Discord, Info, Media, PromptMood, Prompts, Web

T = TypeVar("T")


def try_load(path: Path, load: Callable[[str], T]) -> T | None:
    try:
        with open(path) as f:
            return load(f.read())
    except FileNotFoundError:
        logging.info(f"{path.name} not found.")
    except JSONDecodeError as e:
        logging.warning(f"{path.name} is not valid JSON. Reason: {e}")
    except Invalid as e:
        logging.warning(f"{path.name} format is invalid. Reason: {e}")

    return None


def length_equal_to(data: dict, key: str, equal_to: str) -> None:
    Schema(Equal(len(data[equal_to]), msg=f'Length of "{key}" must be equal to "{equal_to}"'))(len(data[key]))


def load_captions() -> Captions:
    default = Captions()

    def load(content: str) -> Captions:
        captions = json.loads(content)

        # TODO: Better "prefix_settings" validation
        schema = Schema(
            {
                "prefix": [str],
                Optional("prefix_settings"): {
                    Optional(str): {
                        Optional("caption"): str,
                        Optional("images"): str,
                        Optional("chance"): All(Any(int, float), Range(min=0, max=100, min_included=False)),
                        Optional("max"): All(int, Range(min=1)),
                    }
                },
                Optional("subtext"): str,
                Optional("denial"): All([str], Length(min=1)),
                Optional("subliminals"): All([str], Length(min=1)),
                Optional("notifications"): All([str], Length(min=1)),
                "default": [str],
            },
            required=True,
            extra=ALLOW_EXTRA,
        )

        schema(captions)
        schema.extend(dict.fromkeys(captions["prefix"], All([str], Length(min=1))), extra=PREVENT_EXTRA)(captions)

        moods = []
        for prefix in captions["prefix"]:
            prefix_settings = captions.get("prefix_settings", {}).get(prefix, {})
            moods.append(CaptionMood(prefix, prefix_settings.get("max", 1), captions[prefix]))

        return Captions(
            moods,
            captions.get("subtext", default.close_text),
            captions.get("denial", default.denial),
            captions.get("subliminals", default.subliminal),
            captions.get("notifications", default.notification),
            captions["default"],
        )

    return try_load(Resource.CAPTIONS, load) or default


def load_corruption() -> list[CorruptionLevel]:
    def load(content: str) -> list[CorruptionLevel]:
        corruption = json.loads(content)

        Schema(
            {
                "moods": {Number(scale=0): {"add": [str], "remove": [str]}},
                "wallpapers": {Any(Number(scale=0), "default"): str},
                "config": {Number(scale=0): {str: Any(int, str)}},
            }
        )(corruption)

        moods = corruption["moods"]
        wallpapers = corruption["wallpapers"]
        configs = corruption["config"]

        levels: list[CorruptionLevel] = []
        for i in range(max(len(moods), len(wallpapers) - (1 if "default" in wallpapers else 0), len(configs))):
            n = str(i + 1)

            mood_change = moods.get(n, {"add": [], "remove": []})
            wallpaper = wallpapers.get(n)
            config_change = configs.get(n, {})

            if i == 0:
                levels.append(CorruptionLevel(set(mood_change["add"]), wallpaper or wallpapers.get("default"), config_change))
            else:
                new_moods = levels[i - 1].moods.copy()
                for mood in mood_change["add"]:
                    new_moods.add(mood)
                for mood in mood_change["remove"]:
                    new_moods.remove(mood)

                levels.append(CorruptionLevel(new_moods, wallpaper or levels[i - 1].wallpaper, config_change))

        return levels

    return try_load(Resource.CORRUPTION, load) or []


def load_discord() -> Discord:
    default = Discord()

    def load(content: str) -> Discord:
        image_ids = ["furcock_img", "blacked_img", "censored_img", "goon_img", "goon2_img", "hypno_img", "futa_img", "healslut_img", "gross_img"]
        discord = content.split("\n")

        Schema(All([str], Length(min=1)))(discord)
        has_image = len(discord) > 1 and len(discord[1]) > 0
        if has_image:
            Schema(In(image_ids))(discord[1])

        return Discord(discord[0], discord[1] if has_image else default.image)

    return try_load(Resource.DISCORD, load) or default


def load_info() -> Info:
    default = Info(mood_file=Data.MOODS / f"{utils.compute_mood_id()}.json")

    def load(content: str) -> Info:
        info = json.loads(content)

        Schema({"name": str, "id": str, "creator": str, "version": str, "description": str}, required=True)(info)

        return Info(info["name"], Data.MOODS / f"{info['id']}.json", info["creator"], info["version"], info["description"])

    return try_load(Resource.INFO, load) or default


def load_media() -> dict[str, str]:
    def load(content: str) -> dict[str, str]:
        media = json.loads(content)

        Schema({str: All([str], Length(min=1))})(media)

        # Mapping from media to moods
        media_moods = {}
        for mood, files in media.items():
            for file in files:
                media_moods[file] = mood

        return media_moods

    return try_load(Resource.MEDIA, load) or {}


def load_prompt() -> Prompts:
    default = Prompts()

    def load(content: str) -> Prompts:
        prompt = json.loads(content)

        schema = Schema(
            {
                "moods": All([str], Length(min=1)),
                "freqList": All([All(Any(int, float), Range(min=0, min_included=False))], Length(min=1)),
                "minLen": All(int, Range(min=1)),
                "maxLen": All(int, Range(min=1)),
                Optional("subtext"): str,
                Optional("commandtext"): str,
            },
            required=True,
            extra=ALLOW_EXTRA,
        )

        schema(prompt)
        length_equal_to(prompt, "freqList", "moods")
        Schema(Range(min=prompt["minLen"], msg='"maxLen" must be greater than or equal to "minLen"'))(prompt["maxLen"])
        schema.extend(dict.fromkeys(prompt["moods"], All([str], Length(min=1))), extra=PREVENT_EXTRA)(prompt)

        moods = []
        for i in range(len(prompt["moods"])):
            mood = prompt["moods"][i]
            moods.append(PromptMood(mood, prompt["freqList"][i], prompt[mood]))
        return Prompts(moods, prompt["minLen"], prompt["maxLen"], prompt.get("commandtext", default.command_text), prompt.get("subtext", default.submit_text))

    return try_load(Resource.PROMPT, load) or default


def load_web() -> list[Web]:
    def load(content: str) -> list[Web]:
        web = json.loads(content)

        Schema({"urls": All([Url()], Length(min=1)), "args": All([str], Length(min=1)), Optional("moods"): All([str], Length(min=1))}, required=True)(web)

        length_equal_to(web, "args", "urls")
        if "moods" in web:
            length_equal_to(web, "moods", "urls")

        web_list = []
        for i in range(len(web["urls"])):
            web_list.append(Web(web["urls"][i], web["args"][i].split(","), web["moods"][i] if "moods" in web else None))

        return web_list

    return try_load(Resource.WEB, load) or []


def load_moods(mood_file: Path) -> ActiveMoods:
    def load(content: str) -> ActiveMoods:
        moods = json.loads(content)

        # TODO: Validate that moods exist in the pack
        Schema({"media": [str], "captions": [str], "prompts": [str], "web": [str]}, required=True)(moods)

        return ActiveMoods(True, set(moods["media"]), set(moods["captions"]), set(moods["prompts"]), set(moods["web"]))

    return try_load(mood_file, load) or ActiveMoods()


def list_media(dir: Path, is_valid: Callable[[str], bool], media_moods: dict[str, str] = {}) -> list[Media]:
    return [Media(dir / file, media_moods.get(file, None)) for file in os.listdir(dir) if is_valid(dir / file)] if dir.is_dir() else []
