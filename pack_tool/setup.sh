#!/bin/bash

python3 --version
if [ $? -ne 0 ]; then
    echo "Python not found"
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

if [ ! -f "pack_tool.sh" ]; then
    echo "#!/bin/bash" >> pack_tool.sh
    echo ".venv/bin/python3 src/main.py \"\$@\"" >> pack_tool.sh
    chmod +x pack_tool.sh
fi
