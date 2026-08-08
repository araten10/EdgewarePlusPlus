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

# --- Verify ANGLE libraries (macOS only, shipped with the project) ---
if [ "$(uname)" = "Darwin" ]; then
    ANGLE_DIR="src/os_utils/angle_libs"
    if [ ! -f "$ANGLE_DIR/libEGL.dylib" ] || [ ! -f "$ANGLE_DIR/libGLESv2.dylib" ]; then
        echo "Error: ANGLE libraries missing from $ANGLE_DIR"
        echo "These are compiled from source and should be shipped with the project."
        echo "If you cloned the repository, check that the binary files were included."
        exit 1
    fi
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
