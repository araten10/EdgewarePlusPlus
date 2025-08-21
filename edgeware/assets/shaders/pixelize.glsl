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
#define SAMPLE 8

vec4 hook()
{
    float width = HOOKED_size.x;
    float height = HOOKED_size.y;

    int x_px = int(HOOKED_pos.x * width);
    int y_px = int(HOOKED_pos.y * height);

    int x_px_min = x_px - x_px % SIZE;
    int x_px_max = x_px_min + SIZE;
    int y_px_min = y_px - y_px % SIZE;
    int y_px_max = y_px_min + SIZE;

    float x_min = float(x_px_min) / width;
    float x_max = float(x_px_max) / width;
    float y_min = float(y_px_min) / height;
    float y_max = float(y_px_max) / height;

    float dx = (x_max - x_min) / SAMPLE;
    float dy = (y_max - y_min) / SAMPLE;

    vec4 average = vec4(0.0, 0.0, 0.0, 1.0);
    int n = 0;
    for (float x = x_min; x < x_max; x += dx)
    {
        for (float y = y_min; y < y_max; y += dy)
        {
            average.rgb += HOOKED_tex(vec2(x, y)).rgb;
            n++;
        }
    }
    average.rgb /= n;
    return average;
}
