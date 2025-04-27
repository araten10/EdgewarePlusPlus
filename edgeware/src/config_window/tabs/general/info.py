import textwrap
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    Frame,
    Label,
    Message,
    Misc,
    ttk,
)
from tkinter.font import Font

from config_window.utils import set_widget_states
from config_window.vars import Vars
from pack import Pack
from widgets.scroll_frame import ScrollFrame
from widgets.tooltip import CreateToolTip

MULTI_PACK_TEXT = 'NOTE: If you have multiple packs loaded, make sure to apply the pack you want using the "Switch Pack" button at the bottom of the window! This tab shows information on the currently loaded pack, so if info here isn\'t updating, you may have forgot to hit that button!'


def list_length(pack: Pack, attr: str) -> list:
    return len(getattr(pack.index.default, attr)) + sum([len(getattr(mood, attr)) for mood in pack.index.moods])


class StatusItem(Frame):
    def __init__(self, master: Misc, text: str, includes: bool, tooltip: str | None = None) -> None:
        super().__init__(master)

        self.pack(fill="x", side="left", expand=1)
        Label(self, text=text, font="Default 10").pack(padx=2, pady=2, side="top")

        label = Label(
            self, text=("✓" if includes else "✗"), font="Default 14", fg=("green" if includes else "red"), cursor=("question_arrow" if tooltip else "")
        )
        label.pack(padx=2, pady=2, side="top")
        if tooltip:
            CreateToolTip(label, tooltip)


class StatsItem(Frame):
    def __init__(self, master: Misc, text: str, number: int) -> None:
        super().__init__(master)

        self.pack(fill="x", side="left", expand=1)

        Label(self, text=text, font="Default 10").pack(pady=2, side="top")
        ttk.Separator(self, orient="horizontal").pack(fill="x", side="top", padx=10)
        Label(self, text=f"{number}").pack(pady=2, side="top")


class InfoTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message], pack: Pack) -> None:
        super().__init__()

        multi_pack_message = Message(self.viewPort, text=MULTI_PACK_TEXT, justify=CENTER, width=675)
        multi_pack_message.pack(fill="both")
        message_group.append(multi_pack_message)

        # Stats
        Label(self.viewPort, text="Stats", font=title_font, relief=GROOVE).pack(pady=2)

        status_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        status_frame.pack(fill="x", padx=3)
        StatusItem(status_frame, "Pack Loaded", pack.paths.root.exists())
        StatusItem(status_frame, "Info File", pack.paths.info.is_file())
        StatusItem(status_frame, "Pack has Wallpaper", pack.paths.wallpaper.is_file())
        StatusItem(
            status_frame,
            "Custom Startup",
            pack.paths.splash,
            "If you are looking to add this to packs made before Edgeware++,"
            ' put the desired file in /resource/ and name it "loading_splash.png"'
            " (also supports .gif, .bmp and .jpg/jpeg).",
        )
        StatusItem(status_frame, "Custom Discord Status", pack.paths.discord.is_file())
        StatusItem(
            status_frame,
            "Custom Icon",
            pack.paths.icon.is_file(),
            "If you are looking to add this to packs made before Edgeware++,"
            ' put the desired file in /resource/ and name it "icon.ico". (the file must be'
            " a .ico file! make sure you convert properly!)",
        )
        StatusItem(
            status_frame,
            "Corruption",
            pack.paths.corruption.is_file(),
            "An Edgeware++ feature that is kind of hard to describe in a single tooltip.\n\n"
            'For more information, check the "About" tab for a detailed writeup.',
        )

        stats_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        stats_frame.pack(fill="x", pady=1)

        stats_row_1 = Frame(stats_frame)
        stats_row_1.pack(fill="x", side="top")
        StatsItem(stats_row_1, "Images", len(pack.images))
        StatsItem(stats_row_1, "Audio Files", len(pack.audio))
        StatsItem(stats_row_1, "Videos", len(pack.videos))
        StatsItem(stats_row_1, "Web Links", list_length(pack, "web"))

        stats_row_2 = Frame(stats_frame)
        stats_row_2.pack(fill="x", side="top", pady=1)
        StatsItem(stats_row_2, "Prompts", list_length(pack, "prompts"))
        StatsItem(stats_row_2, "Captions", list_length(pack, "captions"))
        StatsItem(stats_row_2, "Subliminals", len(pack.subliminal_overlays))

        # Information
        Label(self.viewPort, text="Information", font=title_font, relief=GROOVE).pack(pady=2)

        info_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        info_frame.pack(fill="x", pady=2)

        description_frame = Frame(info_frame, borderwidth=2, relief=GROOVE)
        description_frame.pack(fill="both", side="right")
        description_title = Label(description_frame, text="Description", font="Default 10")
        description_title.pack(padx=2, pady=2, side="top")
        ttk.Separator(description_frame, orient="horizontal").pack(fill="x", side="top")
        description_wrap = textwrap.TextWrapper(width=80, max_lines=5)
        description_label = Label(description_frame, text=description_wrap.fill(text=pack.info.description))
        description_label.pack(padx=2, pady=2, side="top")

        basic_info_frame = Frame(info_frame, borderwidth=2, relief=GROOVE)
        basic_info_frame.pack(fill="x", side="left", expand=1)

        name_frame = Frame(basic_info_frame)
        name_frame.pack(fill="x")
        name_title = Label(name_frame, text="Pack Name:", font="Default 10")
        name_title.pack(padx=6, pady=2, side="left")
        ttk.Separator(name_frame, orient="vertical").pack(fill="y", side="left")
        name_label = Label(name_frame, text=pack.info.name)
        name_label.pack(padx=2, pady=2, side="left")

        ttk.Separator(basic_info_frame, orient="horizontal").pack(fill="x")

        creator_frame = Frame(basic_info_frame)
        creator_frame.pack(fill="x")
        creator_title = Label(creator_frame, text="Author Name:", font="Default 10")
        creator_title.pack(padx=2, pady=2, side="left")
        ttk.Separator(creator_frame, orient="vertical").pack(fill="y", side="left")
        creator_label = Label(creator_frame, text=pack.info.creator)
        creator_label.pack(padx=2, pady=2, side="left")

        ttk.Separator(basic_info_frame, orient="horizontal").pack(fill="x")

        version_frame = Frame(basic_info_frame)
        version_frame.pack(fill="x")
        version_title = Label(version_frame, text="Version:", font="Default 10")
        version_title.pack(padx=18, pady=2, side="left")
        ttk.Separator(version_frame, orient="vertical").pack(fill="y", side="left")
        version_label = Label(version_frame, text=pack.info.version)
        version_label.pack(padx=2, pady=2, side="left")

        set_widget_states(
            pack.paths.info.is_file(),
            [
                info_frame,
                description_frame,
                description_title,
                description_label,
                name_frame,
                name_title,
                name_label,
                creator_frame,
                creator_title,
                creator_label,
                version_frame,
                version_title,
                version_label,
            ],
        )

        discord_frame = Frame(self.viewPort, borderwidth=5, relief=RAISED)
        discord_frame.pack(fill="x", pady=2)
        discord_status_title = Label(discord_frame, text="Custom Discord Status:", font="Default 10")
        discord_status_title.pack(padx=2, pady=2, side="left")
        ttk.Separator(discord_frame, orient="vertical").pack(fill="y", side="left")
        discord_status_label = Label(discord_frame, text=pack.discord.text)
        discord_status_label.pack(padx=2, pady=2, side="left", expand=1)
        ttk.Separator(discord_frame, orient="vertical").pack(fill="y", side="left")
        discord_image_title = Label(discord_frame, text="Discord Status Image:", font="Default 10")
        discord_image_title.pack(padx=2, pady=2, side="left")
        ttk.Separator(discord_frame, orient="vertical").pack(fill="y", side="left")
        discord_image_label = Label(discord_frame, text=pack.discord.image, cursor="question_arrow")
        discord_image_label.pack(padx=2, pady=2, side="left")
        CreateToolTip(
            discord_image_label,
            "As much as I would like to show you this image, it's fetched from the discord "
            "application API- which I cannot access without permissions, as far as i'm aware.\n\n"
            "Because of this, only packs created by the original Edgeware creator, PetitTournesol, have custom status images.\n\n"
            "Nevertheless, I have decided to put this here not only for those packs, but also for other "
            "packs that tap in to the same image IDs.",
        )

        set_widget_states(pack.paths.discord.is_file(), [discord_frame, discord_status_title, discord_status_label, discord_image_title, discord_image_label])
