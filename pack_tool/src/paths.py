# Copyright (C) 2024 LewdDevelopment
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import Path

PATH = Path(__file__).parent.parent
DEFAULT_PACK = PATH / "default_pack.yml"


class Source:
    def __init__(self, root: str):
        self.root = PATH / root

        # Directories
        self.media = self.root / "media"
        self.subliminals = self.root / "subliminals"
        self.wallpapers = self.root / "wallpapers"

        # Files
        self.icon = self.root / "icon.ico"
        self.pack = self.root / "pack.yml"
        self.splash = self.root / "loading_splash"


class Build:
    def __init__(self, root: str):
        self.root = PATH / root

        # Directories
        self.audio = self.root / "aud"
        self.image = self.root / "img"
        self.subliminals = self.root / "subliminals"
        self.video = self.root / "vid"

        # Files
        self.config = self.root / "config.json"
        self.corruption = self.root / "corruption.json"
        self.discord = self.root / "discord.dat"
        self.icon = self.root / "icon.ico"
        self.index = self.root / "index.json"
        self.info = self.root / "info.json"
        self.splash = self.root / "loading_splash"
        self.wallpaper = self.root / "wallpaper.png"

        # Legacy
        self.captions = self.root / "captions.json"
        self.media = self.root / "media.json"
        self.prompt = self.root / "prompt.json"
        self.web = self.root / "web.json"
