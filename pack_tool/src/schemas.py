# Copyright (C) 2024 LewdDevelopment
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from voluptuous import ALLOW_EXTRA, All, Optional, Range, Required, Schema, Url

INFO = Schema(
    {
        "generate": bool,
        "name": str,
        "id": str,
        "creator": str,
        "version": str,
        "description": str,
    },
    required=True,
    extra=ALLOW_EXTRA,
)

DISCORD = Schema({"generate": bool, "status": str}, required=True, extra=ALLOW_EXTRA)

MOOD_BASE = Schema(
    {
        "max-clicks": All(int, Range(min=1)),
        "captions": [str],
        "denial": [str],
        "subliminal-messages": [str],
        "notifications": [str],
        "prompts": [str],
        "web": [{"url": Url(), Optional("args"): [str]}],
    },
    extra=ALLOW_EXTRA,
)

INDEX = Schema(
    {
        Required("generate"): bool,
        Required("default"): MOOD_BASE.extend(
            {
                "popup-close": str,
                "prompt-command": str,
                "prompt-submit": str,
                "prompt-min-length": All(int, Range(min=1)),
                "prompt-max-length": All(int, Range(min=1)),
            },
            extra=ALLOW_EXTRA,
        ),
        Required("moods"): [MOOD_BASE.extend({Required("mood"): str}, extra=ALLOW_EXTRA)],
    },
    extra=ALLOW_EXTRA,
)

CORRUPTION = Schema(
    {
        Required("generate"): bool,
        Required("levels"): [
            {
                "add-moods": [str],
                "remove-moods": [str],
                "wallpaper": str,
                "config": dict,
            }
        ],
    },
    extra=ALLOW_EXTRA,
)
