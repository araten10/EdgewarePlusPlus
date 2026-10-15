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

from pathlib import Path
from tkinter import Tk
from typing import Callable

from config.settings import Settings
from features.popup import Popup
from features.video_player import VideoPlayer
from pack import Pack
from state import State
from videoprops import get_video_properties


class VideoPopup(Popup):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State, media: Path | None = None, on_close: Callable[[], None] | None = None) -> None:
        self.media = media or pack.random_video()
        if not self.should_init(settings, state):
            return
        super().__init__(root, settings, pack, state, on_close)

        properties = get_video_properties(self.media)
        width, height = properties["width"], properties["height"]
        
        # Detect video rotation metadata
        rotation = properties.get("tags", {}).get("rotate", 0)
        
        for data in properties.get("side_data_list", []):
            if data.get("side_data_type") == "Display Matrix" and "rotation" in data:
                rotation = data["rotation"]
                break
        
        # Swap dimensions for portrait rotation
        if round(float(rotation)) % 180 == 90:
            width, height = height, width
        
        self.compute_geometry(width, height)

        self.player = VideoPlayer(self, self.settings, self.width, self.height)
        self.player.properties["volume"] = self.settings.video_volume
        self.player.properties["glsl-shaders"] = self.try_denial_filter(True)
        self.player.play(self.media)

        self.init_finish()

    def should_init(self, settings: Settings, state: State) -> bool:
        if state.video_number < settings.max_video and self.media:
            state.video_number += 1
            return True
        return False

    def close(self) -> None:
        self.player.close()
        super().close()
        self.state.video_number -= 1
