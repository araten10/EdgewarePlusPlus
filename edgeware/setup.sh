#!/bin/bash

version_string=$(python3 --version)
if [ $? -ne 0 ]; then
    echo "Python not found"
    echo "Please install Python 3 and try again"
    exit
fi

IFS=" " read -r p version <<< "$version_string"
IFS="." read -r major minor patch <<< "$version"
if (( !($major == 3 && $minor >= 12) )); then
    echo "Python version 3.12 or higher recommended"
fi

python3 -c "import tkinter"
if [ $? -ne 0 ]; then
    echo "tkinter not found"
    echo "Please install python3-tk (Debian), python3-tkinter (Fedora), or tk (Arch) and try again"
    exit
fi

mpv --version
if [ $? -ne 0 ]; then
    echo "mpv not found"
    echo "Please install mpv and try again"
    exit
fi

python3 -m venv .venv
if [ $? -eq 0 ]; then
    source .venv/bin/activate
else
    echo "Failed to create virtual environment"
    exit
fi

python3 -m pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit
fi

shortcut() {
    source=$1
    script=${2:-$1}

    if [ ! -f "$script.sh" ]; then
        echo "#!/bin/bash" >> $script.sh
        echo ".venv/bin/python3 src/${source}.py" >> $script.sh
        chmod +x $script.sh
    fi
}

shortcut "main_edgeware" "edgeware"
shortcut "main_config" "config"
shortcut "panic"
