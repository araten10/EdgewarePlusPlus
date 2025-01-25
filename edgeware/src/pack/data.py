from dataclasses import dataclass, field
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
    max_clicks: int = 1
    captions: list[str] = field(default_factory=list)
    denial: list[str] = field(default_factory=list)
    subliminals: list[str] = field(default_factory=list)
    notifications: list[str] = field(default_factory=list)
    prompts: list[str] = field(default_factory=list)
    web: list[Web] = field(default_factory=list)


@dataclass
class Default(MoodBase):
    popup_close: str = "I Submit <3"
    prompt_command: str = "Type for me, slut~"
    prompt_submit: str = "I Submit <3"
    prompt_min_length: int = 1
    prompt_max_length: int = 1


@dataclass
class Mood(MoodBase):
    name: str | None = None


@dataclass
class Index:
    default: Default = field(default_factory=Default)
    moods: list[Mood] = field(default_factory=list)
    media_moods: dict[str, str] = field(default_factory=dict)


@dataclass
class Info:
    name: str = "Unnamed Pack"
    mood_file: Path = Path()
    creator: str = "Anonymous"
    version: str = "1.0"
    description: str = "No description set."
