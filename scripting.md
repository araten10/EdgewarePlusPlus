# Scripting

Edgeware++ packs allow pack creators to write custom scripts that will be executed while running the pack. Edgeware++ uses a custom language that aims to conform to a subset of [Lua](https://www.lua.org/). Scripts must be placed in a file called `script.lua` at the root of a pack and currently the script can't be split into multiple files.

## Language

Edgeware++ currently supports the following features of Lua.

### Comments

```lua
-- Single-line comment

--[[
  Multi-line comment
]]
```

### Basic data types and variables

```lua
integer = 1
float = 0.5
string = "Hello world!"
boolean = true
none = nil
local var = "Local variable"
a, b, c = 1, 2, 3
local one, two = "first", 2
```

### Tables

```lua
empty_table = {}
empty_table["key"] = "value"
empty_table.key = "value"
empty_table[1] = "value"

struct_like = {name = "Table", another = true}
array_like = {1, empty_table, "Third"}
dict_like = {["key"] = "value", ["k"] = "v"}
```

### Operators

```lua
(1 + 2) * 3 / (-4) -- Arithmetic
10 > 5 -- Comparisons
(true and true) or (false and false) -- Boolean operators
```

### Do blocks

```lua
do
    local var = 1
    return var
end
```

### While loops

```lua
i = 0
while i < 10 do
    i = i + 1
end
```

### If statements

```lua
if condition then
    print("The condition was true")
elseif other_condtion then
    print("The other condition was true")
else
    print("Both conditions were false")
end
```

### Functions

```lua
function add(a, b)
    return a + b
end

add(1, 2)

local function is_two(n)
    local two = add(1, 1)
    if n == two then
        return true
    end
    return false
end

print(is_two(2))
print(is_two(3))
```

## Modules

### Basic v1

Provides basic Lua functions. Import with `require("basic_v1")`

---

`print(...)`: Prints any number of arguments.
- `...`: Variadic arguments.

### Edgeware v1

Provides the core functionality for interacting with Edgeware's features. Import with `ew = require("edgeware_v1")`, optionally replacing `ew` with any name of your choice.

---

`ew.after(ms, callback)`: Schedule a function call after a specified time.
- `ms`: Milliseconds to wait.
- `callback`: Function taking no arguments.

---

`ew.roll(chance)`: Returns true with a given chance.
- `chance`: Chance to return true, integer between 1 and 100.
- **Returns**: True or false.

---

`ew.panic()`: Call the panic functionality of Edgeware, closing it.

---

`ew.close_popups()`: Close all currently open popups.

---

**UNSTABLE** - The behavior of this function may change.

`ew.set_active_moods(moods)`: Set the active moods.
- `moods`: List of moods, e.g., `{"furry", "goon"}`.

---

`ew.progress_corruption()`: Progress to the next corruption level, requires corruption to be enabled.

---

`ew.set_wallpaper(filename)`: Set the user's wallpaper.
- `filename`: Filename in the root of the pack.

---

`ew.set_popup_close_text(text)`: Set the text on the close button of popups.
- `text`: New text.

---

`ew.set_prompt_command_text(text)`: Set the command text at the top of prompts.
- `text`: New text.

---

`ew.set_prompt_submit_text(text)`: Set the text on the submit button of prompts.
- `text`: New text.

---

`ew.set_prompt_min_length(length)`: Set the minimum length of a prompt, must be less than or equal to the maximum length.
- `length`: Minimum length.

---

`ew.set_prompt_max_length(length)`: Set the maximum length of a prompt, must be greater than or equal to the minimum length.
- `length`: Maximum length.

---

`ew.open_image(args)`: Open an image popup.
- `args`: Table with the following optional fields:
  - `filename`: Filename of an image in the `img` directory of a pack, if not provided, a random image from the pack is used.
  - `on_close`: Function taking no arguments called after the popup is closed.

---

`ew.open_video(args)`: Open a video popup.
- `args`: Table with the following optional fields:
  - `filename`: Filename of a video in the `vid` directory of a pack, if not provided, a random video from the pack is used.
  - `on_close`: Function taking no arguments called after the popup is closed.

---

`ew.play_audio(args)`: Play an audio file.
- `args`: Table with the following optional fields:
  - `filename`: Filename of an audio file in the `aud` directory of a pack, if not provided, a random audio file from the pack is used.
  - `on_stop`: Function taking no arguments called after the audio file stops playing.

---

`ew.open_prompt(args)`: Open a prompt.
- `args`: Table with the following optional fields:
  - `text`: Prompt text, if not provided, a random prompt from the pack is used.
  - `on_close`: Function taking no arguments called after the prompt is closed.

---

`ew.open_web(args)`: Open a web page in a browser.
- `args`: Table with the following optional fields:
  - `url`: URL to open, if not provided, a random URL from the pack is used.

---

`ew.open_subliminal(args)`: Open a subliminal popup.
- `args`: Table with the following optional fields:
  - `text`: Subliminal text, if not provided, a random subliminal from the pack is used.

---

`ew.send_notification(args)`
- `args`: Table with the following optional fields:
  - `text`: Notification text, if not provided, a random notification from the pack is used.
