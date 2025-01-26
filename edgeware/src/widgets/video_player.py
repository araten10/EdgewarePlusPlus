import time
from itertools import cycle
from pathlib import Path
from threading import Thread
from tkinter import Label, TclError, Toplevel

import imageio
from PIL import Image, ImageTk
from utils import utils
from videoprops import get_video_properties

try:
    import vlc
except FileNotFoundError:
    pass


class VideoPlayer:
    def __init__(self, master: Toplevel, video: Path, size: tuple[int, int], volume: int, vlc_mode: bool):
        self.vlc_mode = vlc_mode
        if self.vlc_mode:
            try:
                #potential TODO: add support for --video-filter, fun stuff in there

                # Max repeat value. This is hacky but seems to be the easiest way to loop the video.
                self.player = vlc.Instance("--input-repeat=65535").media_player_new()
                utils.set_vlc_window(self.player, master.winfo_id())
                self.player.video_set_mouse_input(False)
                self.player.video_set_key_input(False)
                self.player.audio_set_volume(volume)
                self.player.set_media(vlc.Media(video))
                self.player.play()
            except Exception as e:
                print(f"error in video player. {e}")
        else:
            self.label = Label(master)
            self.label.pack()
            self.size = size

            properties = get_video_properties(video)
            frame_rate = properties["avg_frame_rate"].split("/")
            self.delay = float(frame_rate[1]) / float(frame_rate[0])
            self.frames = cycle(imageio.get_reader(video).iter_data())

            # TODO: Find a better solution for audio / video
            # try:
            #     audio = AudioFileClip(str(video)).to_soundarray()
            #     # TODO: Setting the volume this way is extremely slow
            #     # audio = [[volume / 100 * v[0], volume / 100 * v[1]] for v in audio]
            #     samplerate = len(audio) / float(properties["duration"])
            #     sounddevice.play(audio, samplerate=samplerate, loop=True)  # TODO: Can't play multiple sounds at once
            # except KeyError:
            #     pass  # Video has no audio

            Thread(target=self.animate, daemon=True).start()

    def animate(self) -> None:
        try:
            while True:
                start = time.perf_counter()

                # Load a new frame
                frame = next(self.frames)
                image = ImageTk.PhotoImage(Image.fromarray(frame).resize(self.size))
                self.label.config(image=image)

                # Discard the previous frame
                self.image = image

                end = time.perf_counter()
                time.sleep(max(0, self.delay - (end - start)))
        except TclError:
            pass  # Exception thrown when closing

    def on_close(self) -> None:
        if self.vlc_mode:
            self.player.stop()
