from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Subject:
    value: Any
    observers: list[Callable[[], None]] = field(default_factory=list)

    def notify(self) -> None:
        for observer in self.observers:
            observer()

    def attach(self, observer: Callable[[], None]) -> None:
        self.observers.append(observer)


@dataclass
class State:
    audio_number = 0
    fill_number = 0
    _popup_number = Subject(0)
    prompt_active = False
    subliminal_number = 0
    video_number = 0

    timer_active = False

    corruption_time_start = 0
    corruption_popup_number = 0
    corruption_launches_number = 0

    _hibernate_active = Subject(False)
    hibernate_id = None
    pump_scare = False

    corruption_level = 1

    gallery_dl_process = None

    @property
    def popup_number(self) -> int:
        return self._popup_number.value

    @popup_number.setter
    def popup_number(self, value: int) -> None:
        self._popup_number.value = value
        self._popup_number.notify()

    @property
    def hibernate_active(self) -> bool:
        return self._hibernate_active.value

    @hibernate_active.setter
    def hibernate_active(self, value: bool) -> None:
        self._hibernate_active.value = value
        self._hibernate_active.notify()
