# Copyright (C) 2024 Marigold & Araten
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

from voluptuous import ALLOW_EXTRA, All, Optional, Range, Schema, Union, Url

CAPTION = Schema(
    {
        "generate": bool,
        "close-text": str,
        Optional("denial"): Union([str], None),
        "default-captions": [str],
        Optional("subliminal-messages"): Union([str], None),
        Optional("notifications"): Union([str], None),
        "prefixes": Union(
            [
                {
                    "name": str,
                    Optional("chance"): All(Union(int, float), Range(min=0, max=100)),
                    Optional("max-clicks"): All(int, Range(min=1)),
                    "captions": [str],
                }
            ],
            None,
        ),
    },
    required=True,
    extra=ALLOW_EXTRA,
)

PROMPT = Schema(
    {
        "generate": bool,
        Optional("command"): Union(str, None),
        "submit-text": str,
        "minimum-length": All(int, Range(min=1)),
        "maximum-length": All(int, Range(min=1)),
        "default-prompts": {
            "weight": All(int, Range(min=0)),
            "prompts": Union([str], None),
        },
        "moods": Union(
            [
                {
                    "name": str,
                    "weight": All(int, Range(min=0)),
                    "prompts": [str],
                }
            ],
            None,
        ),
    },
    required=True,
    extra=ALLOW_EXTRA,
)

WEB = Schema(
    {
        "generate": bool,
        "urls": [{"url": Url(), "mood": str, Optional("args"): [str]}],
    },
    required=True,
    extra=ALLOW_EXTRA,
)
