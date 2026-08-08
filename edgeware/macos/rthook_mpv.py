# -*- coding: utf-8 -*-
"""PyInstaller runtime hook: pre-load libmpv.dylib from the app bundle.

The python-mpv package uses ctypes.util.find_library('mpv') on macOS,
which only searches standard library paths.  When running inside a
PyInstaller .app bundle, libmpv.dylib lives in Contents/Resources/lib/
and won't be found by find_library.  We load it explicitly with ctypes
so the dynamic linker caches the handle for when the mpv package
attempts its own lookup.
"""
import ctypes
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False) and sys.platform == "darwin":
    _libmpv = Path(sys.executable).parent.parent / "Resources" / "lib" / "libmpv.dylib"
    if _libmpv.is_file():
        try:
            ctypes.CDLL(str(_libmpv))
        except OSError as exc:
            print(f"Warning: failed to pre-load libmpv.dylib from bundle: {exc}",
                  file=sys.stderr)
        else:
            # Also add the lib directory to DYLD_LIBRARY_PATH so that
            # transitive dependencies of libmpv can be resolved.
            # NOTE: DYLD_LIBRARY_PATH is ignored by SIP on macOS 10.11+
            # for code-signed processes. If libmpv has transitive
            # dependencies not bundled alongside it (e.g., libbluray,
            # libdvdnav from Homebrew), they must be bundled and
            # rebased with install_name_tool, or video playback will
            # fail at runtime with "library not loaded" errors.
            _lib_dir = str(_libmpv.parent)
            old = os.environ.get("DYLD_LIBRARY_PATH", "")
            os.environ["DYLD_LIBRARY_PATH"] = _lib_dir + (os.pathsep + old if old else "")
