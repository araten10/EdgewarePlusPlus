import json
import logging
import os
from collections.abc import Callable
from dataclasses import asdict
from json.decoder import JSONDecodeError
from pathlib import Path
from typing import TypeVar

from paths import Data, PackPaths
from utils import utils
from voluptuous import ALLOW_EXTRA, PREVENT_EXTRA, All, Any, Equal, In, Length, Number, Optional, Range, Required, Schema, Url
from voluptuous.error import Invalid

from pack.data import CorruptionLevel, Default, Discord, Index, Info, Mood, MoodBase, MoodSet, UniversalSet, Web

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


def load_corruption(paths: PackPaths) -> list[CorruptionLevel]:
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
                levels.append(CorruptionLevel(MoodSet(mood_change["add"]), wallpaper or wallpapers.get("default"), config_change))
            else:
                new_moods = levels[i - 1].moods.copy()
                for mood in mood_change["add"]:
                    new_moods.add(mood)
                for mood in mood_change["remove"]:
                    new_moods.remove(mood)

                levels.append(CorruptionLevel(new_moods, wallpaper or levels[i - 1].wallpaper, config_change))

        return levels

    return try_load(paths.corruption, load) or []


def load_discord(paths: PackPaths) -> Discord:
    default = Discord()

    def load(content: str) -> Discord:
        image_ids = ["furcock_img", "blacked_img", "censored_img", "goon_img", "goon2_img", "hypno_img", "futa_img", "healslut_img", "gross_img"]
        discord = content.split("\n")

        Schema(All([str], Length(min=1)))(discord)
        has_image = len(discord) > 1 and len(discord[1]) > 0
        if has_image:
            Schema(In(image_ids))(discord[1])

        return Discord(discord[0], discord[1] if has_image else default.image)

    return try_load(paths.discord, load) or default


def load_index(paths: PackPaths) -> Index:
    def load(content: str) -> Index:
        index = json.loads(content)

        base_schema = Schema(
            {
                "maxClicks": All(int, Range(min=1)),
                "captions": [str],
                "denial": [str],
                "subliminals": [str],
                "notifications": [str],
                "prompts": [str],
                "web": [Url()],
                "webArgs": [[str]],
            },
            extra=ALLOW_EXTRA,
        )

        Schema(
            {
                "default": base_schema.extend(
                    {
                        "popupClose": str,
                        "promptCommand": str,
                        "promptSubmit": str,
                        "promptMinLength": All(int, Range(min=1)),
                        "promptMaxLength": All(int, Range(min=1)),
                    }
                ),
                "moods": [base_schema.extend({Required("mood"): str, "media": [str]})],
            },
            extra=ALLOW_EXTRA,
        )(index)

        default = index.get("default", {})
        moods = index.get("moods", [])

        Schema(Range(min=default.get("promptMinLength", 1), msg='"promptMaxLength" must be greater than or equal to "minLength"'))(
            default.get("promptMaxLength", 1)
        )

        def validate_web_args(base: MoodBase) -> None:
            Schema(Range(max=len(base.get("web", [])), msg='Length of "webArgs" must be less than or equal to "web"'))(len(base.get("webArgs", [])))

        validate_web_args(default)
        for mood in moods:
            validate_web_args(mood)

        def load_base(base: dict) -> MoodBase:
            web = []
            for i in range(len(base.get("web", []))):
                args = base.get("webArgs", [])
                web.append(Web(base["web"][i], args[i] if len(args) > i else [""]))

            return asdict(
                MoodBase(
                    base.get("maxClicks", 1),
                    base.get("captions", []),
                    base.get("denial", []),
                    base.get("subliminals", []),
                    base.get("notifications", []),
                    base.get("prompts", []),
                    web,
                )
            )

        def fix_web(base: MoodBase) -> MoodBase:
            base.web = [Web(web["url"], web["args"]) for web in base.web]
            return base

        return Index(
            fix_web(
                Default(
                    **load_base(default),
                    popup_close=default.get("popupClose", "I Submit <3"),
                    prompt_command=default.get("promptCommand", "Type for me, slut~"),
                    prompt_submit=default.get("promptSubmit", "I Submit <3"),
                    prompt_min_length=default.get("promptMinLength", 1),
                    prompt_max_length=default.get("promptMaxLength", 1),
                )
            ),
            [fix_web(Mood(**load_base(mood), name=mood["mood"])) for mood in moods],
            {file: mood["mood"] for mood in moods for file in mood.get("media", [])},
        )

    return try_load(paths.index, load) or load_index_fallback(paths)


def load_info(paths: PackPaths) -> Info:
    default = Info(mood_file=Data.MOODS / f"{utils.compute_mood_id(paths)}.json")

    def load(content: str) -> Info:
        info = json.loads(content)

        Schema({"name": str, "id": str, "creator": str, "version": str, "description": str}, required=True)(info)

        return Info(info["name"], Data.MOODS / f"{info['id']}.json", info["creator"], info["version"], info["description"])

    return try_load(paths.info, load) or default


def load_active_moods(mood_file: Path) -> set[str]:
    def load(content: str) -> set[str]:
        moods = json.loads(content)
        Schema({Required("active"): [str]})(moods)
        return MoodSet(moods["active"])

    return try_load(mood_file, load) or UniversalSet()


def list_media(dir: Path, is_valid: Callable[[str], bool]) -> list[Path]:
    return [(dir / file) for file in os.listdir(dir) if is_valid(dir / file)] if dir.is_dir() else []


def load_index_fallback(paths: PackPaths) -> Index:
    index = Index(media_moods=load_media(paths))

    captions = load_captions(paths)
    prompts = load_prompts(paths)
    web = load_web(paths)

    def get_or_add_mood(name: str) -> Mood:
        mood = next((mood for mood in index.moods if mood.name == name), None)
        if not mood:
            mood = Mood(name=name)
            index.moods.append(mood)
        return mood

    # Media
    for mood_name in set(index.media_moods.values()):
        if mood_name == "default":
            continue

        get_or_add_mood(mood_name)

    # Captions
    index.default.captions = captions.get("default", [])
    index.default.denial = captions.get("denial", [])
    index.default.subliminals = captions.get("subliminals", [])
    index.default.notifications = captions.get("notifications", [])
    index.default.popup_close = captions.get("subtext") or index.default.popup_close

    for mood_name in captions.get("prefix", {}):
        if mood_name != "default":
            mood = get_or_add_mood(mood_name)
            mood.captions = captions[mood_name]
            mood.max_clicks = captions.get("prefix_settings", {}).get(mood_name, {}).get("max", 1)

    # Prompts
    index.default.prompts = prompts.get("default", [])
    index.default.prompt_command = prompts.get("commandtext") or index.default.prompt_command
    index.default.prompt_submit = prompts.get("subtext") or index.default.prompt_submit
    index.default.prompt_min_length = prompts.get("minLen", 1)
    index.default.prompt_max_length = prompts.get("maxLen", 1)

    for mood_name in prompts["moods"]:
        if mood_name != "default":
            get_or_add_mood(mood_name).prompts = prompts[mood_name]

    # Web
    indices = range(len(web.get("urls", [])))
    web_moods = web.get("moods", [None for i in indices])
    for i in indices:
        web_url = Web(web["urls"][i], web["args"][i].split(","))

        mood_name = web_moods[i]
        if mood_name is None or mood_name == "default":
            index.default.web.append(web_url)
        else:
            get_or_add_mood(mood_name).web.append(web_url)

    return index


def load_media(paths: PackPaths) -> dict[str, str]:
    def load(content: str) -> dict[str, str]:
        media = json.loads(content)
        Schema({str: All([str], Length(min=1))})(media)
        return {file: mood for mood, files in media.items() for file in files if mood != "default"}

    return try_load(paths.media, load) or {}


def load_captions(paths: PackPaths) -> dict:
    def load(content: str) -> dict:
        captions = json.loads(content)

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

        return captions

    return try_load(paths.captions, load) or {}


def load_prompts(paths: PackPaths) -> dict:
    def load(content: str) -> dict:
        prompts = json.loads(content)

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

        schema(prompts)
        length_equal_to(prompts, "freqList", "moods")
        Schema(Range(min=prompts["minLen"], msg='"maxLen" must be greater than or equal to "minLen"'))(prompts["maxLen"])
        schema.extend(dict.fromkeys(prompts["moods"], All([str], Length(min=1))), extra=PREVENT_EXTRA)(prompts)

        return prompts

    return try_load(paths.prompt, load) or {}


def load_web(paths: PackPaths) -> dict:
    def load(content: str) -> dict:
        web = json.loads(content)

        Schema({"urls": All([Url()], Length(min=1)), "args": All([str], Length(min=1)), Optional("moods"): All([str], Length(min=1))}, required=True)(web)

        length_equal_to(web, "args", "urls")
        if "moods" in web:
            length_equal_to(web, "moods", "urls")

        return web

    return try_load(paths.web, load) or {}
