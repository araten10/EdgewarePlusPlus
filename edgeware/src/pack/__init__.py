import random
from pathlib import Path

import filetype
from paths import Assets, CustomAssets, PackPaths
from settings import Settings

from pack.data import CaptionMood, PromptMood, Web
from pack.load import list_media, load_captions, load_corruption, load_discord, load_info, load_media, load_moods, load_prompt, load_web


class Pack:
    def __init__(self, root: Path):
        self.paths = PackPaths(root)

        # Pack files
        self.captions = load_captions(self.paths)
        self.corruption_levels = load_corruption(self.paths)
        self.discord = load_discord(self.paths)
        self.info = load_info(self.paths)
        self.media_moods = load_media(self.paths)
        self.prompts = load_prompt(self.paths)
        self.web = load_web(self.paths)

        # Data files
        self.active_moods = load_moods(self.info.mood_file)

        # Media
        self.images = list_media(self.paths.image, filetype.is_image, self.media_moods)
        self.videos = list_media(self.paths.video, filetype.is_video, self.media_moods)
        self.audio = list_media(self.paths.audio, filetype.is_audio, self.media_moods)
        self.subliminal_overlays = list_media(self.paths.subliminals, filetype.is_image)

        # Paths
        self.icon = self.paths.icon if self.paths.icon.is_file() else CustomAssets.icon()
        self.wallpaper = self.paths.wallpaper if self.paths.wallpaper.is_file() else Assets.DEFAULT_WALLPAPER
        self.startup_splash = next((path for path in self.paths.splash if path.is_file()), None) or CustomAssets.startup_splash()

    def filter_media(self, media_list: list[Path]) -> list[Path]:
        filter_function = lambda media: media.mood is None or media.mood in self.active_moods.media  # noqa: E731
        return list(filter(filter_function, media_list)) if self.active_moods.exists else media_list

    def has_image(self) -> bool:
        return len(self.filter_media(self.images)) > 0

    def random_image(self) -> Path:
        return random.choice(self.filter_media(self.images)).path

    def has_video(self) -> bool:
        return len(self.filter_media(self.videos)) > 0

    def random_video(self) -> Path:
        return random.choice(self.filter_media(self.videos)).path

    def has_audio(self) -> bool:
        return len(self.filter_media(self.audio)) > 0

    def random_audio(self) -> Path:
        return random.choice(self.filter_media(self.audio)).path

    def random_subliminal_overlay(self) -> Path:
        if len(self.subliminal_overlays) > 0:
            return random.choice(self.subliminal_overlays).path
        return CustomAssets.subliminal_overlay()

    def filter_captions(self) -> list[CaptionMood]:
        filter_function = lambda c: c.mood in self.active_moods.captions  # noqa: E731
        return list(filter(filter_function, self.captions.moods)) if self.active_moods.exists else self.captions.moods

    def caption_mood_of_media(self, media: Path) -> CaptionMood | None:
        for c in self.filter_captions():
            if media.name.startswith(c.mood):
                return c
        return None

    def find_caption_list(self, settings: Settings, media: Path | None = None) -> list[str]:
        if media and settings.filename_caption_moods:
            mood = self.caption_mood_of_media(media)
            return mood.captions if mood else self.captions.default

        moods = [self.captions.default] + list(map(lambda c: c.captions, self.filter_captions()))
        return [caption for mood in moods for caption in mood]

    def has_captions(self, settings: Settings, media: Path | None = None) -> bool:
        return len(self.find_caption_list(settings, media)) > 0

    def random_caption(self, settings: Settings, media: Path | None = None) -> str:
        return random.choice(self.find_caption_list(settings, media))

    def random_clicks_to_close(self, media: Path) -> int:
        mood = self.caption_mood_of_media(media)
        if mood:
            return random.randint(1, mood.max_clicks)
        return 1

    def has_subliminal_messages(self, settings: Settings) -> bool:
        return len(self.captions.subliminal) > 0 if settings.subliminal_caption_mood else self.has_captions(settings)

    def random_subliminal_message(self, settings: Settings) -> str:
        return random.choice(self.captions.subliminal) if settings.subliminal_caption_mood else self.random_caption(settings)

    def has_notifications(self, settings: Settings) -> bool:
        return len(self.captions.notification) > 0 if settings.notification_mood else self.has_captions(settings)

    def random_notification(self, settings: Settings) -> str:
        return random.choice(self.captions.notification) if settings.notification_mood else self.random_caption(settings)

    def random_denial(self) -> str:
        return random.choice(self.captions.denial)  # Guaranteed to be non-empty

    def filter_prompts(self) -> list[PromptMood]:
        filter_function = lambda p: p.mood in self.active_moods.prompts  # noqa: E731
        return list(filter(filter_function, self.prompts.moods)) if self.active_moods.exists else self.prompts.moods

    def has_prompts(self) -> bool:
        return len(self.filter_prompts()) > 0

    def random_prompt(self) -> str:
        moods = self.filter_prompts()
        mood = random.choices(moods, list(map(lambda p: p.weight, moods)), k=1)[0]
        length = random.randint(self.prompts.min_length, self.prompts.max_length)

        prompt = ""
        for n in range(length):
            prompt += random.choice(mood.prompts) + " "

        return prompt.strip()

    def filter_web(self) -> list[Web]:
        filter_function = lambda w: w.mood is None or w.mood in self.active_moods.web  # noqa: E731
        return list(filter(filter_function, self.web)) if self.active_moods.exists else self.web

    def has_web(self) -> bool:
        return len(self.filter_web()) > 0

    def random_web(self) -> str:
        web = random.choice(self.filter_web())
        return web.url + random.choice(web.args)
