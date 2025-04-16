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
