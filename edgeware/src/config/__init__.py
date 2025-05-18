# Copyright (C) 2024 Araten & Marigold
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
import shutil
import subprocess
import sys

from paths import Assets, Data, Process


def first_launch_configure() -> None:
    if not Data.CONFIG.is_file():
        subprocess.run([sys.executable, Process.CONFIG, "--first-launch-configure"])


def load_config() -> dict:
    if not Data.CONFIG.is_file():
        Data.ROOT.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(Assets.DEFAULT_CONFIG, Data.CONFIG)

    default_config = load_default_config()
    with open(Data.CONFIG, "r+") as f:
        config = json.loads(f.read())

        new_keys = False
        for key, value in default_config.items():
            if key not in config:
                config[key] = value
                new_keys = True

        if new_keys:
            f.seek(0)
            f.write(json.dumps(config))
            f.truncate()

    return config


def load_default_config() -> dict:
    with open(Assets.DEFAULT_CONFIG) as f:
        default_config = json.loads(f.read())

    return default_config
