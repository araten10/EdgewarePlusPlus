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
    Listbox,
)

from config.vars import Vars
from config.window.utils import (
    add_list,
    config,
    remove_list_,
    reset_list,
)
from config.window.widgets.layout import PAD, ConfigRow, ConfigSection, ConfigToggle, set_enabled_when
from config.window.widgets.scroll_frame import ScrollFrame

BOORU_TEXT = 'Please note that the "Booru Downloader" is not currently in a great state. We managed to patch it in Edgeware++ to function properly, however it can lead to performance issues and its not guaranteed that it will work in the future.\n\nIf you encounter bugs with the Booru settings, feel free to leave a Github issue (github.com/araten10/EdgewarePlusPlus/issues) detailing the problem, but also be aware that this feature is fairly low priority for us.'


class BooruTab(ScrollFrame):
    def __init__(self, vars: Vars) -> None:
        super().__init__()

        download_section = ConfigSection(self.viewPort, "Booru Settings", BOORU_TEXT)
        download_section.pack()

        download_row = ConfigRow(download_section)
        download_row.pack()
        ConfigToggle(download_row, "Download from Booru", variable=vars.booru_download).pack()

        tag_row = ConfigRow(download_section)
        tag_row.pack()

        tag_listbox = Listbox(tag_row, selectmode=SINGLE)
        tag_listbox.pack(padx=PAD, pady=PAD, fill="x")
        for tag in config["tagList"].split(">"):
            tag_listbox.insert(1, tag)
        add_tag = Button(tag_row, text="Add Tag", command=lambda: add_list(tag_listbox, "tagList", "New Tag", "Enter Tag(s)"))
        add_tag.pack(padx=PAD, pady=1, fill="x")
        remove_tag = Button(
            tag_row,
            text="Remove Tag",
            command=lambda: remove_list_(tag_listbox, "tagList", "Remove Failed", 'Cannot remove all tags. To download without a tag, use "all" as the tag.'),
        )
        remove_tag.pack(padx=PAD, pady=1, fill="x")
        reset_tags = Button(tag_row, text="Reset Tags", command=lambda: reset_list(tag_listbox, "tagList", "all"))
        reset_tags.pack(padx=PAD, pady=1, fill="x")

        # TODO: Currently nonfunctional
        # min_score_slider = Scale(booru_frame, from_=-50, to=100, orient="horizontal", variable=vars.min_score, label="Minimum Score")
        # min_score_slider.pack(fill="x")

        set_enabled_when(tag_row, enabled=(vars.booru_download, True))
