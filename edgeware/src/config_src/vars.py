from tkinter import BooleanVar, IntVar, StringVar

ConfigVar = IntVar | BooleanVar | StringVar


class Vars:
    entries: dict[str, ConfigVar] = {}

    def __init__(self, config: dict):
        self.config = config

        self.delay = self.make(IntVar, "delay")
        self.image_chance = self.make(IntVar, "popupMod")
        self.web_chance = self.make(IntVar, "webMod")
        self.audio_chance = self.make(IntVar, "audioMod")
        self.prompt_chance = self.make(IntVar, "promptMod")
        self.fill_drive = self.make(BooleanVar, "fill")

        self.fill_delay = self.make(IntVar, "fill_delay")
        self.replace_images = self.make(BooleanVar, "replace")
        self.replace_threshold = self.make(IntVar, "replaceThresh")
        self.run_at_startup = self.make(BooleanVar, "start_on_logon")

    def make(self, var_init: type[ConfigVar], key: str) -> ConfigVar:
        value = self.config[key]
        var = var_init()
        match var:
            case IntVar():
                var.set(int(value))
            case BooleanVar():
                var.set(bool(value))
            case StringVar():
                var.set(value.strip())

        self.entries[key] = var
        return var
