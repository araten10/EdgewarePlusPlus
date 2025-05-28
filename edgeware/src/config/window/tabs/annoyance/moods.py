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

import json
import logging
from tkinter import (
    CENTER,
    GROOVE,
    RAISED,
    VERTICAL,
    Event,
    Frame,
    Label,
    Message,
    Misc,
    ttk,
)
from tkinter.font import Font

from config.vars import Vars
from config.window.utils import (
    config,
)
from config.window.widgets.scroll_frame import ScrollFrame
from config.window.widgets.layout import (
    ConfigRow,
    ConfigSection,
)
from pack import Pack
from ttkwidgets import CheckboxTreeview

MOOD_TEXT = 'Moods are a very important part of edgeware, but also something completely optional to the end-user. Every piece of media has a mood attached to it, and edgeware checks to see if that mood is enabled before deciding to show it. Think of moods like booru tags, categories, or genres.\n\nIn this tab you can disable or enable moods. Don\'t like a particular fetish included in a pack? Turn it off! By default, all moods are turned on...\n\n...Except for packs that utilize corruption. A more in-depth explanation can be found on the "corruption" tab (under modes), but the quick summary is that corruption turns on and off moods automatically over a period of time.\n\nPS: Moods date back all the way to the original edgeware- they just had no purpose. Because of this, every pack is "compatible" with the moods feature- but most older ones just have everything set to "default", which might not show up in this window.'


def update_moods(pack: Pack, mood_name: str, check: bool) -> None:
    if config["toggleMoodSet"]:
        return

    try:
        with open(pack.info.mood_file, "r+") as f:
            active_moods = json.loads(f.read())
            if check:
                active_moods["active"].append(mood_name)
            else:
                active_moods["active"].remove(mood_name)

            f.seek(0)
            f.write(json.dumps(active_moods))
            f.truncate()
    except Exception as e:
        logging.warning(f"error updating mood files. {e}")


# if you are working on this i'm just letting you know there's like almost no documentation for ttkwidgets
# source code is here https://github.com/TkinterEP/ttkwidgets/blob/master/ttkwidgets/checkboxtreeview.py
class MoodsTreeview(CheckboxTreeview):
    def __init__(self, master: Misc, pack: Pack, **kw) -> None:
        super().__init__(master, **kw)
        # disabled tag to mar disabled items
        self.tag_configure("disabled", foreground="grey")
        self.edgeware_pack = pack

    def _box_click(self, event: Event) -> None:
        """Check or uncheck box when clicked."""
        x, y, widget = event.x, event.y, event.widget
        elem = widget.identify("element", x, y)
        if "image" in elem:
            # a box was clicked
            item = self.identify_row(y)
            if self.tag_has("disabled", item):
                return  # do nothing when disabled
            if self.tag_has("unchecked", item) or self.tag_has("tristate", item):
                self.change_state(item, "checked")
                update_moods(self.edgeware_pack, item, True)
            elif self.tag_has("checked"):
                self.change_state(item, "unchecked")
                update_moods(self.edgeware_pack, item, False)


class MoodsTab(ScrollFrame):
    def __init__(self, vars: Vars, title_font: Font, message_group: list[Message], pack: Pack) -> None:
        super().__init__()

        moods_section = ConfigSection(self.viewPort, "Moods", MOOD_TEXT)
        moods_section.pack()
        #message_group.append(moods_message)

        moods_tree = MoodsTreeview(moods_section, pack, height=15, show="tree", name="mediaTree")
        moods_tree.pack(side="left", fill="both", expand=1)
        moods_scrollbar = ttk.Scrollbar(moods_section, orient=VERTICAL, command=moods_tree.yview)
        moods_scrollbar.pack(side="left", fill="y")
        moods_tree.configure(yscroll=moods_scrollbar.set)

        for mood in pack.index.moods:
            parent = moods_tree.insert("", "end", iid=mood.name, values=mood.name, text=mood.name)

            mood_info = [
                ("Media", sum([1 for key, value in pack.index.media_moods.items() if value == mood.name]), 0),
                ("Max clicks", mood.max_clicks, 1),
                ("Captions", len(mood.captions), 0),
                ("Denial messages", len(mood.denial), 0),
                ("Subliminal messages", len(mood.subliminals), 0),
                ("Notifications", len(mood.notifications), 0),
                ("Prompts", len(mood.prompts), 0),
                ("Web URLs", len(mood.web), 0),
            ]
            for key, value, ignore in mood_info:
                if value != ignore:
                    moods_tree.insert(parent, "end", iid=(f"{mood.name}-{key}"), text=f"{key}: {value}")
                    moods_tree.change_state((f"{mood.name}-{key}"), "disabled")

        if len(moods_tree.get_children()) == 0:
            moods_tree.insert("", "0", iid="NAmi", text="No moods found in pack!")
            moods_tree.change_state("NAmi", "disabled")

        if not config["toggleMoodSet"]:
            try:
                with open(pack.info.mood_file, "r") as f:
                    active_moods = json.loads(f.read())
                    for mood_checkbox in moods_tree.get_children():
                        value = moods_tree.item(mood_checkbox, "values")
                        if value[0] in active_moods["active"]:
                            moods_tree.change_state(value[0], "checked")
            except Exception as e:
                logging.warning(f"error checking media treeview nodes. {e}")
