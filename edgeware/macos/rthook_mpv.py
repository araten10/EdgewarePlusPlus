# -*- coding: utf-8 -*-
"""PyInstaller runtime hook: pre-load libmpv.dylib + ANGLE dylibs from the app bundle
and set environment variables for bundled Homebrew data files.

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

Several bundled dylibs (libmpv, libcrypto, libfontconfig, libglib, etc.)
were built by Homebrew and have hardcoded paths to Homebrew directories
baked into their read-only data sections.  The build script copies the
files those paths reference into Contents/Resources/bundle/homebrew/
mimicking the Homebrew layout.  This hook sets environment variables so
that each library finds its files inside the bundle.

If libmpv is bundled but bundle/homebrew/ is missing, the app will
refuse to start because the dylibs cannot resolve their data paths
without system Homebrew.
"""
import ctypes
import os
import sys
from pathlib import Path

if getattr(sys, "frozen", False) and sys.platform == "darwin":
    _bundle_res = Path(sys.executable).parent.parent / "Resources"
    _bundle_hb = _bundle_res / "bundle" / "homebrew"

    # Determine if this app requires Homebrew data (has libmpv bundled)
    _has_libmpv = any((_bundle_res / name).is_file()
                       for name in ("libmpv.dylib", "libmpv.2.dylib"))

    if _has_libmpv and not _bundle_hb.is_dir():
        raise SystemExit(
            f"Edgeware++: required bundle data missing at\n"
            f"  {_bundle_hb}\n"
            f"The app cannot run without Homebrew data bundled inside the .app.\n"
            f"Rebuild the app with build_app.sh."
        )

    # ====================================================================
    # 0. Set environment variables for bundled Homebrew data files
    #    (must happen before any library that uses them is loaded)
    # ====================================================================
    if _bundle_hb.is_dir():
        # Fontconfig: FONTCONFIG_PATH points to the etc/fonts directory
        _fc_etc = _bundle_hb / "etc" / "fonts"
        if _fc_etc.is_dir():
            os.environ["FONTCONFIG_PATH"] = str(_fc_etc)
        # Fontconfig cache directory (writable alternative to hardcoded path)
        # The baked-in fonts.conf has <cachedir>/opt/homebrew/var/cache/fontconfig</cachedir>
        # which is read-only inside the bundle.  Point FONTCONFIG_CACHE to
        # a writable location under ~/Library/Caches instead.
        _fc_cache = Path.home() / "Library" / "Caches" / "Edgeware++" / "fontconfig"
        os.environ["FONTCONFIG_CACHE"] = str(_fc_cache)

        # OpenSSL: config file and certificate bundle
        _ossl_etc = _bundle_hb / "etc" / "openssl@3"
        if _ossl_etc.is_dir():
            _ossl_conf = _ossl_etc / "openssl.cnf"
            if _ossl_conf.is_file():
                os.environ["OPENSSL_CONF"] = str(_ossl_conf)
            _ossl_cert = _ossl_etc / "cert.pem"
            if _ossl_cert.is_file():
                os.environ["SSL_CERT_FILE"] = str(_ossl_cert)
        # OpenSSL engines/modules directory
        _ossl_eng = _bundle_hb / "lib" / "engines-3"
        if _ossl_eng.is_dir():
            os.environ["OPENSSL_ENGINES_DIR"] = str(_ossl_eng)
        _ossl_mod = _bundle_hb / "lib" / "ossl-modules"
        if _ossl_mod.is_dir():
            os.environ["OPENSSL_MODULES_DIR"] = str(_ossl_mod)

        # mpv: MPV_HOME points to user-config directory; also add bin/ to PATH
        # so the mpv subprocess can be found
        _mpv_bin = _bundle_hb / "bin"
        if _mpv_bin.is_dir():
            _path = os.environ.get("PATH", "")
            if str(_mpv_bin) not in _path:
                os.environ["PATH"] = str(_mpv_bin) + os.pathsep + _path
        _mpv_etc = _bundle_hb / "etc" / "mpv"
        if _mpv_etc.is_dir():
            os.environ["MPV_HOME"] = str(_mpv_etc)

        # Lua/LuaJIT: module search paths (force to bundle, no fallback)
        _lua_share = _bundle_hb / "share" / "lua" / "5.1"
        if _lua_share.is_dir():
            os.environ["LUA_PATH"] = str(_lua_share / "?.lua")
            os.environ["LUA_CPATH"] = str(_lua_share / "?.so")

        # GLib locale data (used by harfbuzz, pango, etc.)
        _glib_locale = _bundle_hb / "share" / "locale"
        if _glib_locale.is_dir():
            os.environ["G_LOCALE_DIR"] = str(_glib_locale)

    # ====================================================================
    # 1. Pre-load libmpv.dylib
    # ====================================================================
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

    # ====================================================================
    # 2. Pre-load ANGLE libraries from Frameworks/ (for @rpath resolution)
    #    and Resources/ (original PyInstaller datas location)
    # ====================================================================
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
