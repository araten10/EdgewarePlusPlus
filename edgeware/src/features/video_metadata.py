import json
import subprocess
import sys
from pathlib import Path

from videoprops import which_ffprobe


def get_video_properties(media: str | Path) -> dict:
    output = subprocess.check_output(
        [
            which_ffprobe(),
            "-loglevel",
            "panic",
            "-select_streams",
            "v:0",
            "-show_streams",
            "-print_format",
            "json",
            str(media),
        ],
        encoding="utf-8",
        creationflags=(subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0),
    )

    streams = json.loads(output).get("streams", [])

    if not streams:
        raise RuntimeError(f"No usable video stream found: {media}")

    return streams[0]
