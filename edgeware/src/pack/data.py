from dataclasses import dataclass
from pathlib import Path


# "mood in set" additionally return True if "mood" is the default one
class MoodSet(set):
    def __contains__(self, o: object) -> bool:
        return o is None or super().__contains__(o)


# "mood in set" always returns True, used when a mood file can't be used
class UniversalSet(set):
    def __contains__(self, o: object) -> bool:
        return True


@dataclass
class CorruptionLevel:
    moods: MoodSet[str]
    wallpaper: str | None
    config: dict[str, str | int]


@dataclass
class Discord:
    text: str = "[No discord.dat resource]"
    image: str = "default"


@dataclass
class Web:
    url: str
    args: list[str]


@dataclass
class MoodBase:
    max_clicks: int
    captions: list[str]
    denial: list[str]
    subliminals: list[str]
    notifications: list[str]
    prompts: list[str]
    web: list[Web]


@dataclass
class Default(MoodBase):
    popup_close: str
    prompt_command: str
    prompt_submit: str
    prompt_min_length: int
    prompt_max_length: int


@dataclass
class Mood(MoodBase):
    name: str


@dataclass
class Index:
    default: Default
    moods: list[Mood]
    media_moods: dict[str, str]


@dataclass
class Info:
    name: str = "Unnamed Pack"
    mood_file: Path = Path()
    creator: str = "Anonymous"
    version: str = "1.0"
    description: str = "No description set."
