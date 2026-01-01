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

import getpass
import logging
import os
import random
import sys
import time
from hashlib import md5

from config.settings import Settings
from paths import Data, PackPaths
from screeninfo import Monitor, get_monitors


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

    logging.info(f"Python version: {sys.version}")
    return log_file


def compute_mood_id(paths: PackPaths) -> str:
    data = []
    for path, dirs, files in os.walk(paths.root):
        data.append(sorted(files))

    return md5(str(sorted(data)).encode()).hexdigest()


def primary_monitor() -> Monitor | None:
    monitors = get_monitors()

    # Return the first monitor if no primary monitor is found
    return next((m for m in monitors if m.is_primary), monitors[0] if monitors else None)


def random_monitor(settings: Settings) -> Monitor:
    enabled_monitors = [m for m in get_monitors() if m.name not in settings.disabled_monitors]
    return random.choice(enabled_monitors or primary_monitor())
