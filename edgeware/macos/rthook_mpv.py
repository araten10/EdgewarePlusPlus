# -*- coding: utf-8 -*-
"""PyInstaller runtime hook: pre-load libmpv.dylib + ANGLE dylibs from the app bundle.

The python-mpv package uses ctypes.util.find_library('mpv') on macOS,
which only searches standard library paths.  When running inside a
PyInstaller .app bundle, libmpv.dylib lives in Contents/Resources/
and won't be found by find_library.  We load it explicitly with ctypes
so the dynamic linker caches the handle for when the mpv package
attempts its own lookup.

ANGLE libraries (libEGL.dylib, libGLESv2.dylib) are pre-loaded so that
their @rpath-based install_name resolves correctly.  They are copied to
Contents/Frameworks/ by the build script, which is already on PyInstaller's
@rpath search list.
"""
import ctypes
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False) and sys.platform == "darwin":
    _bundle_res = Path(sys.executable).parent.parent / "Resources"

    # Prefer the PyInstaller-collected copy in Resources/ (rebased with
    # @rpath install names) over the legacy Resources/lib/ copy which has
    # hardcoded absolute Homebrew paths that won't resolve in the bundle.
    _candidates = [
        _bundle_res / "libmpv.dylib",
        _bundle_res / "lib" / "libmpv.dylib",
    ]

    _libmpv = None
    for _c in _candidates:
        if _c.is_file():
            _libmpv = _c
            break

    if _libmpv is not None:
        try:
            ctypes.CDLL(str(_libmpv))
        except OSError as exc:
            print(f"Warning: failed to pre-load {_libmpv.name}: {exc}",
                  file=sys.stderr)
        else:
            # Add Resources/ (and lib/ if it exists) to DYLD_LIBRARY_PATH so
            # that transitive @rpath dependencies of libmpv can be resolved.
            # NOTE: DYLD_LIBRARY_PATH is ignored by SIP on macOS 10.11+
            # for code-signed processes.  LC_RPATH entries on the executable
            # are the primary mechanism for @rpath resolution.
            _lib_dirs = []
            _res_dir = str(_bundle_res)
            _lib_dir = str(_libmpv.parent)
            if _res_dir not in _lib_dirs:
                _lib_dirs.append(_res_dir)
            if _lib_dir != _res_dir and _lib_dir not in _lib_dirs:
                _lib_dirs.append(_lib_dir)
            old = os.environ.get("DYLD_LIBRARY_PATH", "")
            os.environ["DYLD_LIBRARY_PATH"] = os.pathsep.join(_lib_dirs) + (os.pathsep + old if old else "")

    # Pre-load ANGLE libraries from Frameworks/ (for @rpath resolution)
    # and Resources/ (original PyInstaller datas location)
    _angle_frameworks = _bundle_res.parent / "Frameworks"
    _angle_lib_dir = _bundle_res / "src" / "os_utils" / "angle_libs"
    for _angle_lib in ("libEGL.dylib", "libGLESv2.dylib"):
        for _candidate in (_angle_frameworks / _angle_lib, _angle_lib_dir / _angle_lib):
            if _candidate.is_file():
                try:
                    ctypes.CDLL(str(_candidate))
                except OSError as exc:
                    print(f"Warning: failed to pre-load {_angle_lib}: {exc}",
                          file=sys.stderr)
                break

    # Set DYLD_LIBRARY_PATH for ANGLE directories too
    _angle_dirs = []
    if _angle_frameworks.is_dir():
        _angle_dirs.append(str(_angle_frameworks))
    if _angle_lib_dir.is_dir():
        _angle_dirs.append(str(_angle_lib_dir))
    if _angle_dirs:
        _old = os.environ.get("DYLD_LIBRARY_PATH", "")
        os.environ["DYLD_LIBRARY_PATH"] = os.pathsep.join(_angle_dirs) + (os.pathsep + _old if _old else "")
