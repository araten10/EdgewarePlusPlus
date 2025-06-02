# Copyright (C) 2025 Araten & Marigold
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

from tkinter import (
    SINGLE,
    Button,
    Checkbutton,
    Frame,
    Listbox,
)

from config.vars import Vars
from config.window.utils import (
    add_list,
    config,
    remove_list_,
    reset_list,
    set_widget_states_with_colors,
)
from config.window.widgets.layout import ConfigSection
from config.window.widgets.scroll_frame import ScrollFrame

BOORU_TEXT = 'Please note that the "Booru Downloader" is not currently in a great state. We managed to patch it in Edgeware++ to function properly, however it can lead to performance issues and its not guaranteed that it will work in the future.\n\nIf you encounter bugs with the Booru settings, feel free to leave a Github issue (github.com/araten10/EdgewarePlusPlus/issues) detailing the problem, but also be aware that this feature is fairly low priority for us.'


class BooruTab(ScrollFrame):
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        download_section = ConfigSection(self.viewPort, "Booru Settings", BOORU_TEXT)
        download_section.pack()

        download_frame = Frame(download_section)
        download_frame.pack(fill="both")

        tag_frame = Frame(download_frame)
        tag_frame.pack(fill="y", side="left")
        tag_listbox = Listbox(tag_frame, selectmode=SINGLE)
        tag_listbox.pack(fill="x")
        for tag in config["tagList"].split(">"):
            tag_listbox.insert(1, tag)
        add_tag = Button(tag_frame, text="Add Tag", command=lambda: add_list(tag_listbox, "tagList", "New Tag", "Enter Tag(s)"))
        add_tag.pack(fill="x")
        remove_tag = Button(
            tag_frame,
            text="Remove Tag",
            command=lambda: remove_list_(tag_listbox, "tagList", "Remove Failed", 'Cannot remove all tags. To download without a tag, use "all" as the tag.'),
        )
        remove_tag.pack(fill="x")
        reset_tags = Button(tag_frame, text="Reset Tags", command=lambda: reset_list(tag_listbox, "tagList", "all"))
        reset_tags.pack(fill="x")

        # TODO: Currently nonfunctional
        # booru_frame = Frame(download_frame)
        # booru_frame.pack(fill="y", side="left")
        # Label(booru_frame, text="Download Mode").pack(fill="x")
        # min_score_slider = Scale(booru_frame, from_=-50, to=100, orient="horizontal", variable=vars.min_score, label="Minimum Score")
        # min_score_slider.pack(fill="x")

        download_group = [tag_listbox, add_tag, remove_tag, reset_tags]
        set_widget_states_with_colors(vars.booru_download.get(), download_group, "white", "gray25")

        enable_frame = Frame(download_frame)
        enable_frame.pack(fill="both", side="right")
        Checkbutton(
            enable_frame,
            text="Download from Booru",
            variable=vars.booru_download,
            command=lambda: (set_widget_states_with_colors(vars.booru_download.get(), download_group, "white", "gray25")),
        ).pack()
