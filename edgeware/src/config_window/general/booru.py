from tkinter import (
    GROOVE,
    RAISED,
    SINGLE,
    Button,
    Checkbutton,
    Entry,
    Frame,
    Label,
    Listbox,
    messagebox,
)
from tkinter.font import Font

import requests
from config_window.utils import (
    add_list,
    config,
    remove_list_,
    reset_list,
    set_widget_states_with_colors,
)
from config_window.vars import Vars

BOORU_FLAG = "<BOORU_INSERT>"  # flag to replace w/ booru name
BOORU_URL = f"https://{BOORU_FLAG}.booru.org/index.php?page=post&s=list&tags="  # basic url
BOORU_VIEW = f"https://{BOORU_FLAG}.booru.org/index.php?page=post&s=view&id="  # post view url
BOORU_PTAG = "&pid="  # page id tag


def validate_booru(name: str) -> bool:
    return requests.get(BOORU_URL.replace(BOORU_FLAG, name)).status_code == 200


class BooruTab(Frame):
    def __init__(self, vars: Vars, title_font: Font):
        super().__init__()

        Label(self, text="Image Download Settings", font=title_font, relief=GROOVE).pack(pady=2)

        download_frame = Frame(self, borderwidth=5, relief=RAISED)
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

        booru_frame = Frame(download_frame)
        booru_frame.pack(fill="y", side="left")
        Label(booru_frame, text="Booru Name").pack(fill="x")
        booru_name_entry = Entry(booru_frame, textvariable=vars.booru_name)
        booru_name_entry.pack(fill="x")
        booru_validate = Button(
            booru_frame,
            text="Validate",
            command=lambda: (
                messagebox.showinfo("Success!", "Booru is valid.")
                if validate_booru(vars.booru_name.get())
                else messagebox.showerror("Failed", "Booru is invalid.")
            ),
        )
        booru_validate.pack(fill="x")
        # TODO: Currently nonfunctional, consider removing completely if this isn't possible with gallery-dl
        # Label(booru_frame, text="Download Mode").pack(fill="x")
        # min_score_slider = Scale(booru_frame, from_=-50, to=100, orient="horizontal", variable=vars.min_score, label="Minimum Score")
        # min_score_slider.pack(fill="x")

        download_group = [tag_listbox, add_tag, remove_tag, reset_tags, booru_name_entry, booru_validate]
        # See comment above
        # download_group.append(min_score_slider)
        set_widget_states_with_colors(vars.booru_download.get(), download_group, "white", "gray25")

        enable_frame = Frame(download_frame)
        enable_frame.pack(fill="both", side="right")
        Checkbutton(
            enable_frame,
            text="Download from Booru",
            variable=vars.booru_download,
            command=lambda: (set_widget_states_with_colors(vars.booru_download.get(), download_group, "white", "gray25")),
        ).pack()
