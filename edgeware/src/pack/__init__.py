# Copyright (C) 2024 Araten & Marigold
#
# This file is part of Edgeware++.
#
# Edgeware++ is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Edgeware++ is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Edgeware++.  If not, see <https://www.gnu.org/licenses/>.

import logging
import random
from pathlib import Path

import filetype
from paths import PATH, CustomAssets, PackPaths

from pack.data import MoodBase, MoodSet
from pack.load import list_media, load_active_moods, load_config, load_corruption, load_discord, load_index, load_info


class Pack:
    def __init__(self, root: Path) -> None:
        logging.info(f"Loading pack at {root.relative_to(PATH)}.")

        self.paths = PackPaths(root)

        # Weights for randomization
        self.image_ranks = {}
        self.video_ranks = {}
        self.audio_ranks = {}

        # Pack files
        self.corruption_levels = load_corruption(self.paths)
        self.discord = load_discord(self.paths)
        self.index = load_index(self.paths)
        self.info = load_info(self.paths)
        self.config = load_config(self.paths)

        # Data files
        self.active_moods = load_active_moods(self.info.mood_file)
        self.allowed_moods = self.active_moods().copy()
        self.block_corruption_moods()
        self.active_moods_dict = {
            "current_level": MoodSet(),
            "next_level": MoodSet()
        }

        # Custom Properties for scripting
        self.scripted_moods = {
            "added": MoodSet(),
            "removed": MoodSet()
        }

        # Media
        self.images = list_media(self.paths.image, filetype.is_image)
        self.videos = list_media(self.paths.video, filetype.is_video)
        self.audio = list_media(self.paths.audio, filetype.is_audio)
        self.hypnos = list_media(self.paths.hypno, filetype.is_image) or list_media(self.paths.hypno_legacy, filetype.is_image) or [CustomAssets.hypno()]

        # Paths
        self.icon = self.paths.icon if self.paths.icon.is_file() else CustomAssets.icon()
        self.wallpaper = self.paths.wallpaper if self.paths.wallpaper.is_file() else None
        self.startup_splash = next((path for path in self.paths.splash if path.is_file()), None) or CustomAssets.startup_splash()

        logging.info(f"Active moods: {self.active_moods()}")

    # currently this refers to active moods for current corruption level(s)
    def get_active_moods(self, use_next_level_moods: bool):
        return self.active_moods_dict[
           "next_level" if use_next_level_moods else "current_level"
        ]

    def update_moods(self, curr_level: int, next_level: int, is_level_update: bool = False):

        # check what changes are introduced by the new level (if any) and override the changes that scripting made
        if is_level_update:
            added_level_moods = MoodSet(
                self.corruption_levels[next_level - 1].moods - self.corruption_levels[curr_level - 1].moods
            )
            print(f"MOODS ADDED BY LEVEL: {added_level_moods}")
            removed_level_moods = MoodSet(
                self.corruption_levels[curr_level - 1].moods - self.corruption_levels[next_level - 1].moods
            )
            print(f"MOODS REMOVED BY LEVEL: {removed_level_moods}")

            self.scripted_moods["added"].difference_update(removed_level_moods)
            self.scripted_moods["removed"].difference_update(added_level_moods)


        # print messages were for debugging, feel free to remove
        print(f"CURR LEVEL MOODS: {self.corruption_levels[curr_level - 1].moods}")
        print(f"NEXT LEVEL MOODS: {self.corruption_levels[next_level - 1].moods}")
        print(f"ADDED SCRIPED MOODS: {self.scripted_moods["added"]}")
        print(f"REMOVED SCRIPTED MOODS: {self.scripted_moods["removed"]}")

        self.active_moods_dict["current_level"] = MoodSet(
            self.corruption_levels[
                curr_level - 1
            ].moods | self.scripted_moods["added"] - self.scripted_moods["removed"]
        )
        print(f"CURR AFTER: {self.active_moods_dict["current_level"]}")
        self.active_moods_dict["next_level"] = MoodSet(
            self.corruption_levels[
                next_level - 1
            ].moods | self.scripted_moods["added"] - self.scripted_moods["removed"]
        )
        print(f"NEXT AFTER: {self.active_moods_dict["next_level"]}")

    def block_corruption_moods(self) -> None:
        active_moods = self.active_moods()
        for level in self.corruption_levels:
            # Remove moods that aren't enabled by the user from each corruption level
            level.moods = MoodSet([mood for mood in level.moods if mood in active_moods])

    def filter_media(self, media_list: list[Path]) -> list[Path]:
        active_moods = self.active_moods()
        return list(filter(lambda media: self.index.media_moods.get(media.name) in active_moods, media_list))

    def random_media(self, media_list: list[Path], media_ranks: dict[Path, int]) -> Path | None:
        filtered = self.filter_media(media_list)
        if not filtered:
            return None

        # Give lower preference to media that has been recently selected
        max_rank = len(media_list)
        ranks = [media_ranks.get(media, max_rank) for media in filtered]
        weights = [2 ** (16 * rank / max_rank) for rank in ranks]
        media = random.choices(filtered, weights, k=1)[0]

        for key, value in media_ranks.items():
            media_ranks[key] = min(value + 1, max_rank)
        media_ranks[media] = 1

        return media

    def random_image(self, unweighted: bool = False) -> Path | None:
        if unweighted:
            images = self.filter_media(self.images)
            return random.choice(images) if images else None
        return self.random_media(self.images, self.image_ranks)

    def random_video(self) -> Path | None:
        return self.random_media(self.videos, self.video_ranks)

    def random_audio(self) -> Path | None:
        return self.random_media(self.audio, self.audio_ranks)

    def random_hypno(self) -> Path:
        return random.choice(self.hypnos)  # Guaranteed to be non-empty

    def find_list(self, attr: str) -> list:
        active_moods = self.active_moods()
        moods = list(filter(lambda mood: mood.name in active_moods, self.index.moods))
        lists = [getattr(self.index.default, attr)] + list(map(lambda mood: getattr(mood, attr), moods))
        return [item for list in lists for item in list]

    def find_media_mood(self, media: Path) -> MoodBase:
        return next((mood for mood in self.index.moods if mood.name == self.index.media_moods.get(media.name)), None) or self.index.default

    def find_captions(self, media: Path | None = None) -> list[str]:
        return (self.find_media_mood(media).captions or self.index.default.captions) if media else self.find_list("captions")

    def random_caption(self, media: Path | None = None) -> str | None:
        captions = self.find_captions(media)
        return random.choice(captions) if captions else None

    def random_clicks_to_close(self, media: Path) -> int:
        return random.randint(1, self.find_media_mood(media).max_clicks)

    def random_subliminal(self) -> str | None:
        subliminals = self.find_list("subliminals")
        return random.choice(subliminals) if subliminals else self.random_caption()

    def random_notification(self) -> str | None:
        notifications = self.find_list("notifications")
        return random.choice(notifications) if notifications else self.random_caption()

    def random_denial(self) -> str:
        return random.choice(self.find_list("denial") or ["Not for you~"])

    def random_prompt(self) -> str | None:
        prompts = self.find_list("prompts")
        if not prompts:
            return None

        length = random.randint(self.index.default.prompt_min_length, self.index.default.prompt_max_length)

        prompt = ""
        for n in range(length):
            prompt += random.choice(prompts) + " "

        return prompt.strip()

    def random_web(self) -> str | None:
        web = random.choice(self.find_list("web") or [None])
        return web.url + random.choice(web.args or [""]) if web else None
