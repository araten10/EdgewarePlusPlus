from tkinter import (
    GROOVE,
    RAISED,
    Button,
    Checkbutton,
    Frame,
    Label,
    Message,
    Scale,
    simpledialog,
)
from tkinter.font import Font

from config_window.utils import (
    assign,
    set_widget_states,
)
from config_window.vars import Vars
from widgets.scroll_frame import ScrollFrame


class AudioVideoTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message]):
        super().__init__()

        # Audio
        Label(self.viewPort, text="Audio", font=title_font, relief=GROOVE).pack(pady=2)

        audio_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        audio_frame.pack(fill="x")

        audio_chance_frame = Frame(audio_frame)
        audio_chance_frame.pack(fill="x", side="left", padx=(3, 0), expand=1)
        Scale(audio_chance_frame, label="Audio Popup Chance (%)", from_=0, to=100, orient="horizontal", variable=vars.audio_chance).pack(fill="x", expand=1)
        Button(
            audio_chance_frame,
            text="Manual audio chance...",
            command=lambda: assign(vars.audio_chance, simpledialog.askinteger("Manual Audio", prompt="[0-100]: ")),
        ).pack(fill="x")

        max_audio_frame = Frame(audio_frame)
        max_audio_frame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        Scale(max_audio_frame, label="Max Audio Popups", from_=1, to=50, orient="horizontal", variable=vars.max_audio).pack(fill="x", expand=1)
        Button(
            max_audio_frame, text="Manual Max Audio...", command=lambda: assign(vars.max_audio, simpledialog.askinteger("Manual Max Audio", prompt="[1-50]: "))
        ).pack(fill="x")

        # Video
        Label(self.viewPort, text="Video", font=title_font, relief=GROOVE).pack(pady=2)

        video_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        video_frame.pack(fill="x")

        video_chance_frame = Frame(video_frame)
        video_chance_frame.pack(fill="x", side="left", padx=(3, 0), expand=1)
        Scale(video_chance_frame, label="Video Popup Chance (%)", from_=0, to=100, orient="horizontal", variable=vars.video_chance).pack(fill="x", pady=(25, 0))
        Button(
            video_chance_frame,
            text="Manual video chance...",
            command=lambda: assign(vars.video_chance, simpledialog.askinteger("Video Chance", prompt="[0-100]: ")),
        ).pack(fill="x")

        video_volume_frame = Frame(video_frame)
        video_volume_frame.pack(fill="x", side="left", expand=1)
        Scale(video_volume_frame, label="Video Volume", from_=0, to=100, orient="horizontal", variable=vars.video_volume).pack(fill="x", pady=(25, 0))
        Button(
            video_volume_frame, text="Manual volume...", command=lambda: assign(vars.video_volume, simpledialog.askinteger("Video Volume", prompt="[0-100]: "))
        ).pack(fill="x")

        max_video_frame = Frame(video_frame)
        max_video_frame.pack(fill="x", side="left", padx=(0, 3), expand=1)
        max_video_toggle = Checkbutton(
            max_video_frame,
            text="Cap Videos",
            variable=vars.max_video_enabled,
            command=lambda: set_widget_states(vars.max_video_enabled.get(), max_video_group),
        )
        max_video_toggle.pack(fill="x")
        max_video_scale = Scale(max_video_frame, label="Max Video Popups", from_=1, to=50, orient="horizontal", variable=vars.max_video)
        max_video_scale.pack(fill="x", expand=1)
        max_video_manual = Button(
            max_video_frame,
            text="Manual Max Videos...",
            command=lambda: assign(vars.max_video, simpledialog.askinteger("Manual Max Videos", prompt="[1-50]: ")),
        )
        max_video_manual.pack(fill="x")

        max_video_group = [max_video_scale, max_video_manual]
        set_widget_states(vars.max_video_enabled.get(), max_video_group)
