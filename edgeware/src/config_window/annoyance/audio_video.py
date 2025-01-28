import webbrowser
from tkinter import (
    CENTER,
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
from widgets.tooltip import CreateToolTip

PLAYBACK_TEXT = 'It is highly recommended to set up VLC and enable this setting. While it is an external download and could have it\'s own share of troubleshooting, it will massively increase performance and also fix a potential issue of videos having no audio. More details on this are listed in the hover tooltip for the "Use VLC to play videos" setting.'


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

        # Playback options
        Label(self.viewPort, text="Playback Options", font=title_font, relief=GROOVE).pack(pady=2)

        playback_message = Message(self.viewPort, text=PLAYBACK_TEXT, justify=CENTER, width=675)
        playback_message.pack(fill="both")
        message_group.append(playback_message)

        playback_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        playback_frame.pack(fill="x")

        toggle_vlc = Checkbutton(playback_frame, text="Use VLC to play videos", variable=vars.vlc_mode, cursor="question_arrow")
        toggle_vlc.pack(fill="both", side="top", expand=1, padx=2)
        CreateToolTip(
            toggle_vlc,
            "Going to get a bit technical here:\n\nBy default, EdgeWare loads videos by taking the source file, turning every frame into an image, and then playing the images in "
            "sequence at the specified framerate. The upside to this is it requires no additional dependencies, but it has multiple downsides. Firstly, it's very slow: you may have "
            "noticed that videos take a while to load and also cause excessive memory usage. Secondly, there is a bug that can cause certain users to not have audio while playing videos."
            "\n\nSo here's an alternative: by installing VLC to your computer and using this option, you can make videos play much faster and use less memory by using libvlc. "
            "If videos were silent for you this will hopefully fix that as well.\n\nPlease note that this feature has the potential to break in the future as VLC is a program independent "
            "from EdgeWare. For posterity's sake, the current version of VLC as of writing this tooltip is 3.0.20.",
        )

        Label(
            playback_frame,
            text="NOTE: Installing VLC is required for this option!\nMake sure you download the version your OS supports!\nIf you have a 64 bit OS, download x64!",
            width=10,
        ).pack(fill="both", side="top", expand=1, padx=2)
        Button(playback_frame, text="Go to VLC's website", command=lambda: webbrowser.open("https://www.videolan.org/vlc/")).pack(
            fill="both", side="top", padx=2
        )
