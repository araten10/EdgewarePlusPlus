#!/usr/bin/env bash

runtimeVer=$(grep '^runtime-version:' io.github.araten10.EdgewarePlusPlus.yaml | cut -d"'" -f2)

flatpak-pip-generator \
    --runtime="org.freedesktop.Sdk//$runtimeVer" \
    --output=python-deps \
    --requirements-file=../edgeware/requirements.txt \
    --prefer-wheels=pillow,dbus-fast,desktop-notifier,pybind11,poetry-core
