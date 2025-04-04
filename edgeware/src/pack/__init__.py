import logging
import random
from pathlib import Path

import filetype
from paths import PATH, Assets, CustomAssets, PackPaths

from pack.data import MoodBase, MoodSet
from pack.load import list_media, load_active_moods, load_config, load_corruption, load_discord, load_index, load_info


class Pack:
    image_ranks = {}
    video_ranks = {}
    audio_ranks = {}

    def __init__(self, root: Path):
        logging.info(f"Loading pack at {root.relative_to(PATH)}.")

        self.paths = PackPaths(root)

        # Pack files
        self.corruption_levels = load_corruption(self.paths)
        self.discord = load_discord(self.paths)
        self.index = load_index(self.paths)
        self.info = load_info(self.paths)
        self.config = load_config(self.paths)

        # Data files
        self.active_moods = load_active_moods(self.info.mood_file)
        self.block_corruption_moods()

        # Media
        self.images = list_media(self.paths.image, filetype.is_image)
        self.videos = list_media(self.paths.video, filetype.is_video)
        self.audio = list_media(self.paths.audio, filetype.is_audio)
        self.subliminal_overlays = list_media(self.paths.subliminals, filetype.is_image) or [CustomAssets.subliminal_overlay()]

        # Paths
        self.icon = self.paths.icon if self.paths.icon.is_file() else CustomAssets.icon()
        self.wallpaper = self.paths.wallpaper if self.paths.wallpaper.is_file() else Assets.DEFAULT_WALLPAPER
        self.startup_splash = next((path for path in self.paths.splash if path.is_file()), None) or CustomAssets.startup_splash()

        logging.info(f"Active moods: {self.active_moods()}")

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

    def random_subliminal_overlay(self) -> Path:
        return random.choice(self.subliminal_overlays)  # Guaranteed to be non-empty

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

    def random_subliminal_message(self) -> str | None:
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
        return web.url + random.choice(web.args) if web else None
