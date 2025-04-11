from pathlib import Path
from tkinter import Label, Misc

import filetype
import mpv
from os_utils import close_mpv, init_mpv
from settings import Settings

try:
    import vlc
except FileNotFoundError:
    pass


class VideoPlayer:
    def __init__(self, master: Misc, settings: Settings, width: int, height: int):
        self.settings = settings

        label = Label(master, width=width, height=height)
        label.pack()
        label.wait_visibility()  # Needs to be visible to be drawn on

        if self.settings.vlc_mode:
            # Max repeat value. This is hacky but seems to be the easiest way to loop the video.
            self.vlc_player = vlc.Instance("--input-repeat=65535").media_player_new()
            self.vlc_player.set_xwindow(label.winfo_id())  # utils.set_vlc_window(self.player, master.winfo_id())
            self.vlc_player.video_set_mouse_input(False)
            self.vlc_player.video_set_key_input(False)
            self.vlc_player.audio_set_volume(settings.video_volume)
        else:
            self.mpv_player = mpv.MPV(wid=label.winfo_id())
            init_mpv(self.mpv_player)
            self.mpv_player["hwdec"] = "auto" if self.settings.video_hardware_acceleration else "no"
            self.mpv_player.loop = True
            self.mpv_player.volume = self.settings.video_volume

    def set_filter(self, filter: str) -> None:
        if self.settings.vlc_mode:
            pass  # TODO
        else:
            self.mpv_player.vf = filter

    def play(self, media: Path) -> None:
        if self.settings.vlc_mode:
            vlc_media = vlc.Media(media)

            if self.settings.video_hardware_acceleration:
                vlc_media.add_option(":avcodec-hw=none")

            if filetype.is_image(media):
                vlc_media.add_option(":demux=avformat")

            self.vlc_player.set_media(vlc_media)
            self.vlc_player.play()
        else:
            self.mpv_player.play(str(media))

    def close(self) -> None:
        if self.settings.vlc_mode:
            self.vlc_player.stop()
        else:
            close_mpv(self.mpv_player)
