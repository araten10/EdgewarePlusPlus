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
