import getpass
import logging
import os
import random
import sys
import time
from hashlib import md5

from paths import Data, PackPaths
from screeninfo import Monitor, get_monitors
from settings import Settings


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


def primary_monitor() -> Monitor:
    return next(m for m in get_monitors() if m.is_primary)


def random_monitor(settings: Settings) -> Monitor:
    enabled_monitors = [m for m in get_monitors() if m.name not in settings.disabled_monitors]
    return random.choice(enabled_monitors or primary_monitor())
