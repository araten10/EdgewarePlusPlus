#!/bin/sh
SCRIPT="${1:-main_edgeware}.py"
if [ "$#" -gt 0 ]; then
    shift
fi
exec python3 /app/share/edgeware/src/"$SCRIPT" "$@"
