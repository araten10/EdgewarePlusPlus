from tkinter import Tk

from features.popup import Popup
from pack import Pack
from settings import Settings
from state import State
from videoprops import get_video_properties
from widgets.video_player import VideoPlayer


class VideoPopup(Popup):
    def __init__(self, root: Tk, settings: Settings, pack: Pack, state: State):
        self.media = pack.random_video()
        if not self.should_init(settings, state):
            return
        super().__init__(root, settings, pack, state)

        properties = get_video_properties(self.media)
        self.compute_geometry(properties["width"], properties["height"])

        player = VideoPlayer(self, self.width, self.height)
        player.volume = self.settings.video_volume
        player.vf = self.try_denial_filter(True)
        player.play(str(self.media))

        self.init_finish()

    def should_init(self, settings: Settings, state: State) -> bool:
        if state.video_number < settings.max_video and self.media:
            state.video_number += 1
            return True
        return False

    def close(self) -> None:
        super().close()
        self.state.video_number -= 1
