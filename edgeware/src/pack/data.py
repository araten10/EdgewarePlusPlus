from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class CaptionMood:
    mood: str
    max_clicks: int
    captions: list[str]


@dataclass
class Captions:
    moods: list[CaptionMood] = field(default_factory=list)
    close_text: str = "I Submit <3"
    denial: list[str] = field(default_factory=lambda: ["Not for you~"])
    subliminal: list[str] = field(default_factory=list)
    notification: list[str] = field(default_factory=list)
    default: list[str] = field(default_factory=list)


@dataclass
class CorruptionLevel:
    moods: set[str]
    wallpaper: str | None
    config: dict[str, str | int]


@dataclass
class Discord:
    text: str = "[No discord.dat resource]"
    image: str = "default"


@dataclass
class Info:
    name: str = "Unnamed Pack"
    mood_file: Path = Path()
    creator: str = "Anonymous"
    version: str = "1.0"
    description: str = "No description set."


@dataclass
class PromptMood:
    mood: str
    weight: float
    prompts: list[str]


@dataclass
class Prompts:
    moods: list[PromptMood] = field(default_factory=list)
    min_length: int = 1
    max_length: int = 1
    command_text: str = "Type for me, slut~"
    submit_text: str = "I Submit <3"


@dataclass
class Web:
    url: str
    args: list[str]
    mood: str | None


@dataclass
class ActiveMoods:
    exists: bool = False
    media: set[str] = field(default_factory=lambda: set(["default"]))
    captions: set[str] = field(default_factory=lambda: set(["default"]))
    prompts: set[str] = field(default_factory=lambda: set(["default"]))
    web: set[str] = field(default_factory=set)


@dataclass
class Media:
    path: Path
    mood: str
