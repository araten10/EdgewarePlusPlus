from dataclasses import dataclass

from settings import Settings


@dataclass
class Theme:
    fg: str
    bg: str
    text_fg: str
    text_bg: str
    font: (str, int)
    transparent_bg: str


def get_theme(settings: Settings) -> Theme:
    themes = {
        "Original": Theme("#000000", "#f0f0f0", "#000000", "#ffffff", ("TkDefaultFont", 9), "#000001"),
        "Dark": Theme("#f9faff", "#282c34", "#f9faff", "#1b1d23", ("TkDefaultFont", 9), "#f9fafe"),
        "The One": Theme("#00ff41", "#282c34", "#00ff41", "#1b1d23", ("Consolas", 9), "#00ff42"),
        "Ransom": Theme("#ffffff", "#841212", "#000000", "#ffffff", ("Arial Bold", 9), "#fffffe"),
        "Goth": Theme("#ba9aff", "#282c34", "#6a309d", "#db7cf2", ("Constantia", 9), "#ba9afe"),
        "Bimbo": Theme("#ff3aa3", "#ffc5cd", "#f43df2", "#ffc5cd", ("Constantia", 9), "#ff3aa4"),
    }

    if settings.theme in themes:
        return themes[settings.theme]
    return themes["Original"]
