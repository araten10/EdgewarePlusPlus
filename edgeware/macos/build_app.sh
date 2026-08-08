#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
EDGWARE_DIR="$(dirname "$SCRIPT_DIR")"
cd "$EDGWARE_DIR"

VENV_DIR=".venv"
DIST_DIR="dist"
BUILD_DIR="build"
APP_NAME="Edgeware++"

echo "+==============[ $APP_NAME macOS Builder ]==============+"
echo

# --- Detect Python 3.12+ ---
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

try_python "/opt/homebrew/bin/python3.12" ||
try_python "/usr/local/bin/python3.12" ||
try_python "python3.12" ||
# try_python "python3"  # --> REMOVE

if [ -z "$PYTHON" ]; then
    echo "Python 3.12+ not found. Attempting to install via Homebrew..."
    echo

    # --- Install Homebrew if missing ---
    if ! command -v brew &>/dev/null; then
        echo "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)" || {
            echo "Failed to install Homebrew."
            echo "Please install it manually from https://brew.sh and try again."
            exit 1
        }
        # Add Homebrew to PATH for this session (Apple Silicon default location)
        if [ -d "/opt/homebrew/bin" ] && [[ ":$PATH:" != *":/opt/homebrew/bin:"* ]]; then
            export PATH="/opt/homebrew/bin:$PATH"
        elif [ -d "/usr/local/bin" ] && [[ ":$PATH:" != *":/usr/local/bin:"* ]]; then
            export PATH="/usr/local/bin:$PATH"
        fi
    fi

    # --- Install python@3.12 and python-tk@3.12 ---
    brew install python@3.12 python-tk@3.12 || {
        echo "Failed to install python@3.12 or python-tk@3.12 via Homebrew."
        exit 1
    }

    echo
    echo "Retrying Python detection..."

    # Re-run detection now that Homebrew packages are installed
    PYTHON=""
    try_python "/opt/homebrew/bin/python3.12" ||
    try_python "/usr/local/bin/python3.12" ||
    try_python "python3.12" ||
    # try_python "python3"  <-- REMOVE

    if [ -z "$PYTHON" ]; then
        echo "Error: Python 3.12+ still not found after installation."
        echo "Please check your Homebrew installation and try again."
        exit 1
    fi
fi

if ! command -v mpv &>/dev/null; then
    echo "mpv not found. Attempting to install via Homebrew..."
    ensure_homebrew
    brew install mpv || {
        echo "Failed to install mpv via Homebrew."
        exit 1
    }
fi

echo "Python version: $($PYTHON --version 2>&1)"

# --- Check tkinter ---
$PYTHON -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "tkinter not found. Attempting to install python-tk@3.12 via Homebrew..."
    if command -v brew &>/dev/null; then
        brew install python-tk@3.12 || {
            echo "Failed to install python-tk@3.12."
            echo "Please install it manually: brew install python-tk@3.12"
            exit 1
        }
        # Re-detect Python after installing tk
        PYTHON=""
        try_python "/opt/homebrew/bin/python3.12" ||
        try_python "/usr/local/bin/python3.12" ||
        try_python "python3.12" ||
        try_python "python3"
    else
        echo "Error: tkinter not found and Homebrew is not available."
        echo "Install Homebrew (https://brew.sh) then: brew install python-tk@3.12"
        exit 1
    fi

    if [ -z "$PYTHON" ]; then
        echo "Error: Python 3.12+ not found after installing tkinter."
        exit 1
    fi

    $PYTHON -c "import tkinter" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "Error: tkinter still not available after installation."
        exit 1
    fi
fi

# --- Create venv if needed ---
if [ ! -d "$VENV_DIR" ]; then
    echo
    echo "Creating virtual environment..."
    $PYTHON -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment"
        exit 1
    fi
fi

source "$VENV_DIR/bin/activate"

# --- Install dependencies ---
echo
echo "Installing dependencies..."
pip install -r requirements.txt pyinstaller pillow
if [ $? -ne 0 ]; then
    echo "Failed to install requirements"
    exit 1
fi

# --- Clean previous build ---
echo
echo "Cleaning previous build..."
rm -rf "$BUILD_DIR" "$DIST_DIR"

# --- Build Edgeware (main app) ---
echo
echo "Building $APP_NAME.app..."
pyinstaller --noconfirm macos/edgeware.spec
if [ $? -ne 0 ]; then
    echo "Failed to build $APP_NAME"
    exit 1
fi

# --- Build Config ---
echo
echo "Building $APP_NAME Config.app..."
pyinstaller --noconfirm macos/config.spec
if [ $? -ne 0 ]; then
    echo "Failed to build $APP_NAME Config"
    exit 1
fi

# --- Build Panic ---
echo
echo "Building $APP_NAME Panic.app..."
pyinstaller --noconfirm macos/panic.spec
if [ $? -ne 0 ]; then
    echo "Failed to build $APP_NAME Panic"
    exit 1
fi

# --- Copy data files into .app bundles ---
echo
echo "Setting up .app bundles..."

for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    app_label=$(basename "$app_bundle" .app)
    echo "  Setting up $app_label.app..."

    RESOURCES="$app_bundle/Contents/Resources"

    # .spec datas handles assets, presets, ANGLE libs, and videoprops (ffprobe)
    # User data directories are now in ~/Library/Application Support/EdgewarePlusPlusMacosPython/
    # and are created at runtime by paths.py
    # libmpv.dylib is collected by PyInstaller via the spec binaries list;
    # the redundant manual copy previously at Resources/lib/ has been removed
    # because it had un-rebased absolute Homebrew paths.
done

# --- Copy ANGLE dylibs to Contents/Frameworks/ ---
# The ANGLE dylibs have install_name @rpath/libEGL.dylib etc.
# PyInstaller's built-in @rpath already includes Contents/Frameworks/.
# Copying them there lets the dynamic linker resolve @rpath references.
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    _angle_src="$app_bundle/Contents/Resources/src/os_utils/angle_libs"
    if [ -d "$_angle_src" ]; then
        mkdir -p "$app_bundle/Contents/Frameworks"
        for _angle_dylib in libEGL.dylib libGLESv2.dylib; do
            if [ -f "$_angle_src/$_angle_dylib" ]; then
                cp -f "$_angle_src/$_angle_dylib" "$app_bundle/Contents/Frameworks/"
            fi
        done
    fi
done

# --- Bundle Homebrew data files and verify self-containment ---
# This replaces the former bundle_homebrew_deps.sh. The bundled app MUST
# work without any links to the user's system or Homebrew packages.
echo "Bundling Homebrew data files..."

BREW_PREFIX="$(brew --prefix 2>/dev/null || echo "/opt/homebrew")"
CELLAR="${BREW_PREFIX}/Cellar"

_copy_tree() {
    local src="$1" dst="$2"
    if [ -d "$src" ]; then
        mkdir -p "$(dirname "$dst")"
        rsync -aL --delete "$src"/ "$dst"/ 2>/dev/null || cp -RfL "$src" "$dst" 2>/dev/null || true
    fi
}

_copy_file() {
    local src="$1" dst="$2"
    if [ -f "$src" ] || [ -L "$src" ]; then
        mkdir -p "$(dirname "$dst")"
        cp -fL "$src" "$dst" 2>/dev/null || cp -f "$src" "$dst" 2>/dev/null || true
    fi
}

_cellar_path() {
    local formula="$1" subpath="$2"
    local version_dir
    version_dir="$(ls -d "${CELLAR}/${formula}"/*/ 2>/dev/null | sort -V | tail -1)"
    [ -n "$version_dir" ] && echo "${version_dir}${subpath}"
}

for APP_BUNDLE in "$DIST_DIR"/*.app; do
    [ -d "$APP_BUNDLE" ] || continue
    APP_LABEL="$(basename "$APP_BUNDLE" .app)"
    RESOURCES="$APP_BUNDLE/Contents/Resources"
    HOMEBREW="$RESOURCES/bundle/homebrew"

    # Only the main app bundles libmpv; skip Config and Panic
    if [ ! -f "${RESOURCES}/libmpv.dylib" ] && [ ! -f "${RESOURCES}/libmpv.2.dylib" ]; then
        echo "  ${APP_LABEL}.app — skipping (no libmpv)"
        continue
    fi

    echo "  ${APP_LABEL}.app"

    # 1. Fontconfig
    echo "    fontconfig..."
    _copy_tree "${BREW_PREFIX}/etc/fonts"                        "${HOMEBREW}/etc/fonts"
    _copy_tree "$(_cellar_path fontconfig share/fontconfig)"     "${HOMEBREW}/share/fontconfig"
    _fc_conf="${HOMEBREW}/etc/fonts/fonts.conf"
    if [ -f "$_fc_conf" ]; then
        sed -i '' '/<cachedir>\/opt\/homebrew\/var\/cache\/fontconfig<\/cachedir>/d' "$_fc_conf" 2>/dev/null || true
    fi

    # 2. OpenSSL
    echo "    openssl..."
    _copy_tree "${BREW_PREFIX}/etc/openssl@3"                    "${HOMEBREW}/etc/openssl@3"
    # NOTE: we deliberately skip lib/engines-3 and lib/ossl-modules
    # — these contain dylibs with hardcoded Cellar paths that can't be
    # reliably rebased during bundling (rsync may re-copy over fixes).
    # They are optional OpenSSL extensions and are not needed for normal
    # certificate verification.
    _ossl_cert="${HOMEBREW}/etc/openssl@3/cert.pem"
    if [ -L "$_ossl_cert" ]; then
        _ca_cert="${BREW_PREFIX}/etc/ca-certificates/cert.pem"
        [ -f "$_ca_cert" ] && { rm -f "$_ossl_cert"; cp -fL "$_ca_cert" "$_ossl_cert"; }
    fi

    # 3. mpv binary + config
    echo "    mpv..."
    mkdir -p "${HOMEBREW}/etc/mpv"
    _copy_file "${BREW_PREFIX}/bin/mpv"                     "${HOMEBREW}/bin/mpv"
    if [ -L "${HOMEBREW}/bin/mpv" ]; then
        _copy_file "$(readlink -f "${BREW_PREFIX}/bin/mpv" 2>/dev/null || \
                      realpath "${BREW_PREFIX}/bin/mpv" 2>/dev/null || \
                      echo "${BREW_PREFIX}/bin/mpv")"   "${HOMEBREW}/bin/mpv"
    fi

    # Fix mpv binary's hardcoded Homebrew paths
    _mpv_bin="${HOMEBREW}/bin/mpv"
    if [ -f "$_mpv_bin" ]; then
        _brew_paths="$(otool -L "$_mpv_bin" 2>/dev/null | sed -n 's/^[[:space:]]*\(\/opt\/homebrew\/[^ ]*\).*/\1/p')"
        for _old_path in $_brew_paths; do
            _lib_name="${_old_path##*/}"
            install_name_tool -change "$_old_path" "@rpath/${_lib_name}" "$_mpv_bin" 2>/dev/null || true
        done
        # mpv is at Contents/Resources/bundle/homebrew/bin/ — need 4 levels up to reach Contents/
        install_name_tool -delete_rpath "@executable_path/../../Frameworks" "$_mpv_bin" 2>/dev/null || true
        install_name_tool -delete_rpath "@executable_path/../../Resources"  "$_mpv_bin" 2>/dev/null || true
        install_name_tool -add_rpath "@executable_path/../../../../Frameworks" "$_mpv_bin" 2>/dev/null || true
        install_name_tool -add_rpath "@executable_path/../../../../Resources"  "$_mpv_bin" 2>/dev/null || true
    fi

    # 4. GLib & gettext locales
    echo "    locales..."
    _copy_tree "$(_cellar_path glib share/locale)"           "${HOMEBREW}/share/locale"
    _gettext_ver="$(_cellar_path gettext "")"
    [ -n "$_gettext_ver" ] && _copy_tree "${_gettext_ver}share/locale" "${HOMEBREW}/share/gettext-locale"

    find "${HOMEBREW}" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find "${HOMEBREW}" -type d -exec chmod 755 {} \; 2>/dev/null || true
    [ -f "${HOMEBREW}/bin/mpv" ] && chmod 755 "${HOMEBREW}/bin/mpv"

    # 5. Rebase ALL bundled homebrew dylibs with hardcoded Cellar paths
    echo "    rebasing bundled dylib paths..."
    for _hb_dylib in $(find "${HOMEBREW}" -name "*.dylib" -type f 2>/dev/null); do
        codesign --remove-signature "$_hb_dylib" 2>/dev/null || true
        _brew_paths="$(otool -L "$_hb_dylib" 2>/dev/null | sed -n 's/^[[:space:]]*\(\/opt\/homebrew\/[^ ]*\).*/\1/p')"
        for _old_path in $_brew_paths; do
            _lib_name="${_old_path##*/}"
            install_name_tool -change "$_old_path" "@rpath/${_lib_name}" "$_hb_dylib" 2>/dev/null || true
        done
    done

    echo "    Done ($(du -sh "${HOMEBREW}" 2>/dev/null | cut -f1))"
done
echo "✓ Homebrew data bundling complete"

# --- Remove leftover COLLECT directories ---
echo
echo "Cleaning up COLLECT directories..."
for dir in "$DIST_DIR/Edgeware++" "$DIST_DIR/Edgeware++ Config" "$DIST_DIR/Edgeware++ Panic"; do
    rm -rf "$dir"
done

# --- Convert icon for app bundles ---
echo
echo "Setting up app icons..."
if [ -f "assets/default_icon.ico" ]; then
    $PYTHON -c "
from PIL import Image
import sys
try:
    img = Image.open('assets/default_icon.ico')
    sizes = img.info.get('sizes', {(img.width, img.height)})
    largest = max(sizes, key=lambda s: s[0] * s[1])
    img.resize(largest, Image.LANCZOS).save('icon.icns', format='ICNS')
    print('Icon converted successfully')
except Exception as e:
    print(f'Icon conversion failed (non-fatal): {e}')
    sys.exit(0)
" 2>/dev/null || echo "  Icon conversion skipped (Pillow not available or icon not found)"

    if [ -f "icon.icns" ]; then
        for app_bundle in "$DIST_DIR"/*.app; do
            [ -d "$app_bundle" ] || continue
            cp icon.icns "$app_bundle/Contents/Resources/" 2>/dev/null || true
            # Update Info.plist to reference the icon
            if [ -f "$app_bundle/Contents/Info.plist" ]; then
                $PYTHON -c "
import plistlib
plist_path = '$app_bundle/Contents/Info.plist'
with open(plist_path, 'rb') as f:
    plist = plistlib.load(f)
plist['CFBundleIconFile'] = 'icon.icns'
with open(plist_path, 'wb') as f:
    plistlib.dump(plist, f)
" 2>/dev/null || true
            fi
        done
        rm -f icon.icns
    fi
fi

# --- Add LC_RPATH entries to executables (BEFORE codesign) ---
echo
echo "Adding rpath entries to executables..."
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    _exe="$app_bundle/Contents/MacOS/$(basename "$app_bundle" .app)"
    if [ -f "$_exe" ]; then
        install_name_tool -add_rpath @executable_path/../Frameworks "$_exe" 2>/dev/null || true
        install_name_tool -add_rpath @executable_path/../Resources "$_exe" 2>/dev/null || true
        echo "  Added rpaths to $(basename "$app_bundle")"
    fi
done

# --- Strip extended attributes (prevents codesign "resource fork" errors) ---
# macOS extended attributes (com.apple.provenance, com.apple.FinderInfo, etc.)
# are added during build by various tools and interfere with codesign on
# newer macOS versions, causing "resource fork, Finder information, or
# similar detritus not allowed" errors.  Strip them before signing.
echo
echo "Stripping extended attributes..."
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    xattr -r -c "$app_bundle" 2>/dev/null || true
    echo "  Stripped xattrs from $(basename "$app_bundle")"
done

# --- Fix library permissions ---
echo
echo "Fixing library permissions..."
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    find "$app_bundle" -name "*.dylib" -exec chmod 755 {} \; 2>/dev/null || true
    find "$app_bundle" -name "*.so" -exec chmod 755 {} \; 2>/dev/null || true
done

# --- Ad-hoc code signing ---
# Sign nested executables first, then the outer bundle.  Using --deep on
# bundles with many Homebrew-sourced dylibs triggers "resource fork" errors
# on newer macOS.  Individual signing avoids this.
#
# NOTE: macOS uses BSD find which doesn't support -executable. We use
# -perm to find files with any execute bit set.
echo
echo "Ad-hoc code signing..."
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    app_label=$(basename "$app_bundle")

    # Sign all nested frameworks
    find "$app_bundle" -name "*.framework" -type d -exec codesign --force --sign - --timestamp=none {} \; 2>/dev/null || true

    # Strip xattrs (PyInstaller's signing adds provenance attrs that break outer signing)
    xattr -r -c "$app_bundle" 2>/dev/null || true

    # Sign all executable files (must be done AFTER xattr strip)
    # Also follow symlinks (-L) so bundled copies in both Resources/ and Frameworks/ are signed
    find -L "$app_bundle" -type f \( -perm -0001 -o -perm -0010 -o -perm -0100 \) ! -path "*_CodeSignature*" -exec codesign --force --sign - --timestamp=none {} \; 2>/dev/null || true

    # Strip xattrs one final time before signing the outer bundle
    xattr -r -c "$app_bundle" 2>/dev/null || true

    # Sign the outer bundle
    codesign --force --sign - --timestamp=none "$app_bundle" 2>&1 \
        && echo "  Signed $app_label" \
        || echo "  Signing failed for $app_label"
done

# --- CRITICAL: Verify self-containment AFTER all signing ---
echo
echo "Verifying app self-containment..."
_brew_link_fail=0
for APP_BUNDLE in "$DIST_DIR"/*.app; do
    [ -d "$APP_BUNDLE" ] || continue
    APP_LABEL="$(basename "$APP_BUNDLE" .app)"

    for _binary in $(find -L "$APP_BUNDLE" \( -name "*.dylib" -o -name "*.so" -o -name "mpv" \) -type f 2>/dev/null); do
        _bad_paths="$(otool -L "$_binary" 2>/dev/null | sed -n 's/^[[:space:]]*\(\/opt\/homebrew\/[^ ]*\).*/\1/p')"
        if [ -n "$_bad_paths" ]; then
            echo "  ERROR: ${APP_LABEL} — $_binary still has Homebrew paths:"
            for _bp in $_bad_paths; do
                echo "    $_bp"
            done
            _brew_link_fail=1
        fi
    done
done

if [ "$_brew_link_fail" -eq 1 ]; then
    echo ""
    echo "FATAL: Bundled binaries still link to Homebrew paths."
    echo "The app will NOT work on a system without Homebrew. Aborting."
    exit 1
fi
echo "  ✓ No hardcoded Homebrew paths found in any bundled binary"

# --- Done ---
echo
echo "+==============[ Build Complete! ]==============+"
echo
echo "Applications built in: $DIST_DIR/"
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    echo "  $app_bundle"
done
echo
echo "To run:"
for app_bundle in "$DIST_DIR"/*.app; do
    [ -d "$app_bundle" ] || continue
    echo "  open \"$app_bundle\""
done
echo
echo "Notes:"
echo "  - User data lives in ~/Library/Application Support/EdgewarePlusPlusMacosPython/"
echo "  - Pack resources are imported to ~/Library/Application Support/EdgewarePlusPlusMacosPython/data/packs/"
echo "  - ANGLE libraries are bundled at Contents/Resources/src/os_utils/angle_libs/"
echo "  - ANGLE libraries are also copied to Contents/Frameworks/ for @rpath resolution"
echo "  - libmpv.dylib is collected by PyInstaller to Contents/Resources/ (with rebased @rpath install names)"
echo "  - For first-time use, run the Config app to set up your preferences"
echo
