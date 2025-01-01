from tkinter import (
    BooleanVar,
    IntVar,
    StringVar,
)

ConfigVar = IntVar | BooleanVar | StringVar


class Vars:
    entries: dict[str, ConfigVar] = {}

    def __init__(self, config: dict):
        self.config = config

    def add(self, var_init: type[ConfigVar], key: str) -> ConfigVar:
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
        return self[key]

    def __getitem__(self, key: str) -> ConfigVar:
        return self.entries[key]
