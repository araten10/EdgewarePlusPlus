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

import ast
import io
import sys

import mpv
from PIL import Image

_, wid, properties_str, media, overlay = sys.argv
properties = ast.literal_eval(properties_str)

player = mpv.MPV(wid=wid)
for key, value in properties.items():
    player[key] = value

if int(overlay):
    bytes = sys.stdin.buffer.read()
    image = Image.open(io.BytesIO(bytes))
    player.create_image_overlay().update(image)

player.play(media)
player.wait_for_playback()
