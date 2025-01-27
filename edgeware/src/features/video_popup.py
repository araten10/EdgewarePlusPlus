from tkinter import Label, Tk

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

        video = self.media
        properties = get_video_properties(video)

        self.compute_geometry(properties["width"], properties["height"])
        self.wait_visibility()
        label = Label(self, width=self.width, height=self.height)
        label.pack()
        self.player = VideoPlayer(label, video, (self.width, self.height), self.settings.video_volume, self.settings.vlc_mode)

        self.init_finish()

    def should_init(self, settings: Settings, state: State) -> bool:
        if state.video_number < settings.max_video and self.media:
            state.video_number += 1
            return True
        return False

    def close(self) -> None:
        self.player.on_close()
        super().close()
        self.state.video_number -= 1
