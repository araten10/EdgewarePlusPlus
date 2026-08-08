# macOS Build Procedure

This document describes the build process for the Edgeware++ macOS `.app` bundles,
including the decisions, pitfalls, and workarounds discovered during development.

## Build Overview

```
edgeware/macos/build_app.sh
  ├── Python 3.12+ detection (with Homebrew auto-install fallback)
  ├── Virtual environment creation
  ├── pip install (requirements.txt + pyinstaller + pillow)
  ├── PyInstaller build (3 specs: edgeware, config, panic)
  ├── Post-build: copy ANGLE dylibs to Contents/Frameworks/
  ├── Post-build: add LC_RPATH entries via install_name_tool
  ├── Post-build: strip macOS extended attributes (xattr)
  ├── Post-build: ad-hoc code signing (step-by-step, not --deep)
  └── Output: dist/*.app
```

## Key Files

| File | Role |
|------|------|
| `macos/build_app.sh` | Orchestrates everything |
| `macos/edgeware.spec` | Main app spec — bundles mpv/ffmpeg dylibs + ANGLE + videoprops |
| `macos/config.spec` | Config app spec (no video libs needed) |
| `macos/panic.spec` | Panic app spec (minimal) |
| `macos/rthook_mpv.py` | Runtime hook — pre-loads libmpv + ANGLE dylibs at startup |
| `src/os_utils/mac_angle.py` | ANGLE renderer — checks Frameworks/ then Resources/ for dylibs |
| `macos/test_bundle.py` | Validates video rendering using bundled ANGLE dylibs |

## The ANGLE @rpath Problem

The ANGLE dylibs (`libEGL.dylib`, `libGLESv2.dylib`) were compiled from source
with their `install_name` set to `@rpath/libEGL.dylib` and `@rpath/libGLESv2.dylib`.

In the PyInstaller bundle:
- `@executable_path` = `Contents/MacOS/`
- PyInstaller sets `@rpath` = `@executable_path/../Frameworks` = `Contents/Frameworks/`
- ANGLE dylibs are copied to `Contents/Resources/src/os_utils/angle_libs/` (via spec `datas`)

**Mismatch**: The dynamic linker looks for `@rpath/libEGL.dylib` in `Contents/Frameworks/`
but the dylibs are in `Contents/Resources/...`. Solution: copy them to `Contents/Frameworks/`
in the build script (lines 193-208 of `build_app.sh`).

## The Code Signing Problem

### Symptom

On macOS 26 (and potentially earlier versions), `codesign --deep --force --sign -`
fails with:

```
dist/Edgeware++.app: resource fork, Finder information, or similar detritus not allowed
```

This causes PyInstaller's built-in signing to fail, and our manual `--deep` signing
to also fail. The result is an unsigned bundle that macOS kills on launch with:

```
SIGKILL (Code Signature Invalid)
EXC_BAD_ACCESS subtype UNKNOWN_0x32
termination namespace CODESIGNING indicator "Invalid Page"
```

### Root Cause

Multiple factors combine to break signing:

1. **Extended attributes**: PyInstaller and other build tools add `com.apple.provenance`,
   `com.apple.FinderInfo`, and `com.apple.fileprovider.fpfs#P` extended attributes to
   files and directories inside the bundle. These attributes trigger the "resource fork"
   error in `codesign`.

2. **`codesign --deep`**: The `--deep` flag causes codesign to recursively sign all
   nested content. On bundles with many Homebrew-sourced dylibs, this recursively
   adds provenance attributes that then break the outer signature.

3. **BSD `find` vs GNU `find`**: macOS uses BSD `find` which does NOT support the
   `-executable` predicate. The initial signing loop used `find ... -executable` which
   silently matched nothing, leaving ffprobe and other executables unsigned.

4. **Symlinks**: PyInstaller creates symlinks between `Contents/Resources/` and
   `Contents/Frameworks/`. BSD `find` without `-L` follows neither, so some executable
   copies were skipped.

### The Working Signing Procedure

The build script signs in this exact order (lines 299-321):

```bash
# 1. Sign frameworks
find "$app_bundle" -name "*.framework" -type d \
    -exec codesign --force --sign - --timestamp=none {} \;

# 2. Strip ALL extended attributes (signing re-adds provenance)
xattr -r -c "$app_bundle"

# 3. Sign ALL executable files using BSD-compatible syntax
#    -L follows symlinks, -perm replaces -executable
find -L "$app_bundle" -type f \
    \( -perm -0001 -o -perm -0010 -o -perm -0100 \) \
    ! -path "*_CodeSignature*" \
    -exec codesign --force --sign - --timestamp=none {} \;

# 4. Strip xattrs AGAIN (signing re-adds provenance)
xattr -r -c "$app_bundle"

# 5. Sign the outer bundle
codesign --force --sign - --timestamp=none "$app_bundle"
```

**Critical rules**:
- Always strip xattrs AFTER signing inner files (codesign re-adds provenance)
- Use `find -L` to follow symlinks
- Use `-perm -0001 -o -perm -0010 -o -perm -0100` instead of `-executable`
- Never use `--deep` on the outer bundle
- Use `--timestamp=none` to avoid network dependency during signing

## The `install_name_tool` Headerpad Limitation

PyInstaller's bootloader binary has no room for additional LC_RPATH load commands.
`install_name_tool -add_rpath` succeeds for `@executable_path/../Frameworks` (one
entry) but fails for a second entry with:

```
larger updated load commands do not fit (the program must be relinked)
```

This is acceptable because PyInstaller already sets `@rpath = @executable_path/../Frameworks`
on the executable, which is the path we need for ANGLE dylib resolution.

## Bundle Layout

```
Edgeware++.app/
├── Contents/
│   ├── MacOS/
│   │   └── Edgeware++              ← main executable (@rpath → Frameworks/)
│   ├── Frameworks/                  ← PyInstaller puts all dylibs here
│   │   ├── libEGL.dylib             ← ANGLE (copied by build script)
│   │   ├── libGLESv2.dylib          ← ANGLE (copied by build script)
│   │   ├── libmpv.dylib             ← collected by spec binaries
│   │   ├── libavcodec.62.dylib      ← collected by spec binaries
│   │   ├── ... (20+ ffmpeg dylibs)  ← collected by spec binaries
│   │   └── Python.framework/        ← bundled Python
│   └── Resources/                   ← mirrors Frameworks/ via symlinks
│       ├── assets/                  ← app assets
│       ├── data/presets/            ← preset data
│       ├── src/os_utils/angle_libs/ ← ANGLE original copy (datas)
│       └── videoprops/binary_dependencies/  ← ffprobe binary
```

## Testing

### Dev Mode Test
```bash
cd edgeware
.venv/bin/python3 macos/test_mpv_embed.py
```
Tests: static image, mpv render, mpv + overlay, hypno overlay, GLSL shader, PIL filter.

### Bundle Simulation Test
```bash
cd edgeware
.venv/bin/python3 macos/test_bundle.py
```
Tests video rendering using the ANGLE dylibs from the bundled app's `Contents/Frameworks/`
and `Contents/Resources/src/os_utils/angle_libs/` directories. Validates that both
paths produce non-black frames.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| App killed with SIGKILL on launch | Code signature invalid | Rebuild with `bash macos/build_app.sh` |
| "resource fork" codesign error | Extended attributes present | `xattr -r -c dist/*.app` then re-sign |
| Black video in bundle | ANGLE dylibs not in Frameworks/ | Verify `Contents/Frameworks/libEGL.dylib` exists |
| "ffprobe not signed" | BSD find skipped ffprobe | Ensure `find -L` with `-perm` in signing loop |
| libmpv.dylib not found | Missing from spec binaries | Verify `brew install mpv ffmpeg` succeeded |
| App starts then exits immediately | Python import error | Check stderr: `dist/Edgeware++.app/Contents/MacOS/Edgeware++ 2>&1` |
