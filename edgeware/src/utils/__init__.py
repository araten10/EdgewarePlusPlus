import getpass
import logging
import os
import platform
import sys
import time
from hashlib import md5

from paths import Data, PackPaths


class RedactUsernameFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        message = super().format(record)
        return message.replace(getpass.getuser(), "[USERNAME_REDACTED]")


def init_logging(filename: str) -> str:
    Data.LOGS.mkdir(parents=True, exist_ok=True)
    log_time = time.asctime().replace(" ", "_").replace(":", "-")
    log_file = f"{log_time}-{filename}.txt"

    handlers = [logging.StreamHandler(stream=sys.stdout), logging.FileHandler(filename=Data.LOGS / log_file)]
    for handler in handlers:
        handler.setFormatter(RedactUsernameFormatter("%(levelname)s:%(message)s"))

    logging.basicConfig(level=logging.INFO, force=True, handlers=handlers)

    return log_file


def compute_mood_id(paths: PackPaths) -> str:
    data = []
    for path, dirs, files in os.walk(paths.root):
        data.append(sorted(files))

    return md5(str(sorted(data)).encode()).hexdigest()


def is_linux():
    return platform.system() == "Linux"


def is_windows():
    return platform.system() == "Windows"


def is_mac():
    return platform.system() == "Darwin"


if is_linux():
    from utils.linux import *  # noqa: F403
elif is_windows():
    from utils.windows import *  # noqa: F403
elif is_mac():
    from utils.mac import *  # noqa: F403
else:
    raise RuntimeError(f"Unsupported operating system: {platform.system()}")
