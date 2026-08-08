#!/bin/bash

# --- Detect a suitable Python 3.12+ interpreter ---
PYTHON=""

try_python() {
    local cmd="$1"
    if command -v "$cmd" &>/dev/null; then
        local ver
        ver=$("$cmd" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>/dev/null)
        if [ $? -eq 0 ]; then
            local major minor
            IFS="." read -r major minor <<< "$ver"
            if [ "$major" -eq 3 ] && [ "$minor" -ge 12 ] 2>/dev/null; then
                PYTHON="$cmd"
                return 0
            fi
        fi
    fi
    return 1
}

if [ "$(uname)" = "Darwin" ]; then
    # macOS: prefer Homebrew python3.12, then any python3.12, then python3 if 3.12+
    try_python "/opt/homebrew/bin/python3.12" ||
    try_python "/usr/local/bin/python3.12" ||
    try_python "python3.12" ||
    try_python "python3"
else
    # Linux: prefer python3.12, then python3 if 3.12+
    try_python "python3.12" || try_python "python3"
fi

if [ -z "$PYTHON" ]; then
    echo "Python 3.12+ not found"
    echo "On macOS: brew install python@3.12"
    echo "On Linux: install python3.12 or python3 (3.12+)"
    exit 1
fi

echo "Using Python: $($PYTHON --version 2>&1)"

# --- Check tkinter ---
$PYTHON -c "import tkinter"
if [ $? -ne 0 ]; then
    echo "tkinter not found"
    if [ "$(uname)" = "Darwin" ]; then
        echo "Please run: brew install python-tk@3.12"
    else
        echo "Please install python3-tk (Debian), python3-tkinter (Fedora), or tk (Arch)"
    fi
    exit 1
fi

# --- Check mpv ---
mpv --version
if [ $? -ne 0 ]; then
    echo "mpv not found"
    echo "On macOS: brew install mpv"
    echo "On Linux: install mpv via your package manager"
    exit 1
fi

# --- Fetch ANGLE libraries from Chrome/Chromium (macOS only) ---
if [ "$(uname)" = "Darwin" ]; then
    ANGLE_DIR="src/os_utils/angle_libs"
    mkdir -p "$ANGLE_DIR"

    CHROME_APP="/Applications/Google Chrome.app"
    CHROMIUM_APP="/Applications/Chromium.app"

    ANGLE_SOURCE=""
    if [ -d "$CHROME_APP" ]; then
        ANGLE_SOURCE="$CHROME_APP/Contents/Frameworks/Google Chrome Framework.framework/Versions/Current/Libraries"
    elif [ -d "$CHROMIUM_APP" ]; then
        ANGLE_SOURCE="$CHROMIUM_APP/Contents/Frameworks/Chromium Framework.framework/Versions/Current/Libraries"
    else
        echo "ANGLE libraries not found."
        echo "Google Chrome or Chromium is required for video playback on macOS."
        echo "Please install Google Chrome: https://www.google.com/chrome/"
        echo "Or install Chromium: https://www.chromium.org/getting-chromium/download/"
        exit 1
    fi

    for lib in libEGL.dylib libGLESv2.dylib; do
        if [ -f "$ANGLE_SOURCE/$lib" ]; then
            cp "$ANGLE_SOURCE/$lib" "$ANGLE_DIR/$lib"
            echo "Copied $lib from $(basename "$ANGLE_SOURCE/../../../../../..")"
        else
            echo "Error: $lib not found in $ANGLE_SOURCE"
            echo "Google Chrome or Chromium installation may be corrupted."
            echo "Please reinstall Chrome or Chromium and try again."
            exit 1
        fi
    done
    echo "ANGLE libraries installed successfully."
fi

# --- Create venv ---
$PYTHON -m venv .venv
if [ $? -ne 0 ]; then
    echo "Failed to create virtual environment"
    exit 1
fi

source .venv/bin/activate

# --- Install dependencies ---
$PYTHON -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

shortcut() {
    source=$1
    script=${2:-$1}

    if [ ! -f "$script.sh" ]; then
        echo "#!/bin/bash" > $script.sh
        echo ".venv/bin/python3 src/${source}.py" >> $script.sh
        chmod +x $script.sh
    fi
}

shortcut "main_edgeware" "edgeware"
shortcut "main_config" "config"
shortcut "panic"
