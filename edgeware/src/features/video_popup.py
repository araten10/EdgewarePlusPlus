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

import logging

from tkinter import Tk
from config.settings import Settings
from features.vibration_mixin import VibrationMixin
from features.popup import Popup
from features.video_player import VideoPlayer
from features.sextoy import Sextoy
from pack import Pack
from state import State
from videoprops import get_video_properties


class VideoPopup(Popup, VibrationMixin):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State, sextoy: Sextoy) -> None:
        self.media = pack.random_video()
        self.sextoy = sextoy
        if not self.should_init(settings, state):
            return
        super().__init__(root, settings, pack, state)

        properties = get_video_properties(self.media)
        self.compute_geometry(properties["width"], properties["height"])

        self.player = VideoPlayer(self, self.settings, self.width, self.height)
        self.player.properties["volume"] = self.settings.video_volume
        self.player.properties["vf"] = self.try_denial_filter(True)
        self.player.play(self.media)

        if hasattr(self, 'trigger_vibration'):
            try:
                self.trigger_vibration("video_open", getattr(settings, 'sextoys', {}), sextoy)
            except Exception as e:
                logging.info(f"Video open vibration error: {str(e)}")

        self.init_finish()

    def should_init(self, settings: Settings, state: State) -> bool:
        if state.video_number < settings.max_video and self.media:
            state.video_number += 1
            return True
        return False

    def close(self) -> None:
        if hasattr(self, 'trigger_vibration'):
            try:
                self.trigger_vibration("video_close", getattr(self.settings, 'sextoys', {}), self.sextoy)
            except Exception as e:
                logging.info(f"Video close vibration error: {str(e)}")
        self.player.close()
        super().close()
        self.state.video_number -= 1