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


import os

from paths import Data

# Fix scaling on high resolution displays
try:
    from ctypes import windll

    windll.shcore.SetProcessDpiAwareness(0)  # Tell Windows that you aren't DPI aware.
except Exception:
    pass  # Fails on non-Windows systems or if shcore is not available

# Add mpv to PATH
os.environ["PATH"] += os.pathsep + str(Data.ROOT)
