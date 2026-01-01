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

import math

SIGMA = 16
RADIUS = 2 * SIGMA

kernel = []
sum = 0

for i in range(RADIUS):
    value = (1 / math.sqrt(2 * math.pi * SIGMA**2)) * math.exp(-(i**2) / (2 * SIGMA**2))
    sum += value * (2 if i > 0 else 1)
    kernel.append(value)

for i in range(RADIUS):
    kernel[i] /= sum

print(kernel)
