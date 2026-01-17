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

Only one module is currently available which provides all functionality scripts are granted. Load the module by placing `require("edgeware_v0")` at the top of your script file. The module provides the following functions.

- **print(...)** - Prints any number of arguments through Python's print function
- **after(ms, callback)** - Calls the function `callback` after `ms` milliseconds
- **roll(chance)** - Rolls a random integer between 1 and 100 and compares it against `chance`, if the random number is less than or equal to `chance`, returns true, otherwise returns false
- **corrupt()** - Progress to the next corruption level
- **close_popups()** - Close all currently open popups
- **set_popup_close_text(text)** - Set the popup close button's text to `text`
- **image(filename)** - Open an image popup with the image pointed to by `filename` or a random image if `filename` is nil
- **video(filename)** - Open a video popup with the video pointed to by `filename` or a random video if `filename` is nil
- **audio(filename, on_stop)** - Play an audio file pointed to by `filename` or a random audio if `filename` is nil, after the audio has finished playing, calls the function `on_stop` if it is not nil
- **prompt(text, on_close)** - Open a prompt with the text `text` or a random prompt if `text` is nil, after the prompt has been completed, calls the function `on_close` if it is not nil
- **web(link)** - Open the web page `link` or a random web page is `link` is nil
- **subliminal(text)** - Show a subliminal message `text` or a random subliminal message if `text` is nil
- **notification(text)** - Show a notification `text` or a random notification if `text` is nil
