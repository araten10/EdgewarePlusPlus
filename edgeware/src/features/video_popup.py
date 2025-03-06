from threading import Thread
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

        self.player = VideoPlayer(self, self.width, self.height)
        self.player.volume = self.settings.video_volume
        self.player.vf = self.try_denial_filter(True)
        self.player.play(str(self.media))

        self.init_finish()

    def should_init(self, settings: Settings, state: State) -> bool:
        if state.video_number < settings.max_video and self.media:
            state.video_number += 1
            return True
        return False

    def close(self) -> None:
        # Run in a thread as a workaround for X error
        # https://github.com/jaseg/python-mpv/issues/114
        Thread(target=self.player.terminate).start()

        super().close()
        self.state.video_number -= 1
