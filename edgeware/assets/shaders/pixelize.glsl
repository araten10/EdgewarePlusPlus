// Copyright (C) 2025 Araten & Marigold
//
// This file is part of Edgeware++.
//
// Edgeware++ is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// Edgeware++ is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with Edgeware++.  If not, see <https://www.gnu.org/licenses/>.

//!HOOK NATIVE
//!BIND HOOKED

#define SIZE 32

vec4 hook()
{
    int x = int(HOOKED_pos.x * HOOKED_size.x);
    int y = int(HOOKED_pos.y * HOOKED_size.y);

    int box_x = x - x % SIZE;
    int box_y = y - y % SIZE;

    vec4 average = vec4(0.0, 0.0, 0.0, 1.0);
    for (int rel_x = 0; rel_x < SIZE; rel_x++)
    {
        int x_off = box_x + rel_x - x;
        for (int rel_y = 0; rel_y < SIZE; rel_y++)
        {
            int y_off = box_y + rel_y - y;
            average.rgb += HOOKED_texOff(vec2(x_off, y_off)).rgb;
        }
    }
    average.rgb /= SIZE * SIZE;
    return average;
}
