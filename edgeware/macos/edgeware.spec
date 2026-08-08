# -*- mode: python ; coding: utf-8 -*-
import os
import subprocess
from pathlib import Path

# Spec lives in edgeware/macos/; project root is edgeware/
EDGWARE_DIR = os.path.abspath(os.path.join(SPECPATH, '..'))

# Locate the videoprops package to bundle its ffprobe binary
import videoprops as _vp
_VIDEOPROPS_DIR = str(Path(_vp.__file__).parent)


def brew_prefix(formula):
    try:
        return subprocess.check_output(
            ['brew', '--prefix', formula], text=True
        ).strip()
    except Exception:
        return None


def collect_dylibs(formula):
    """Return (src, dest) pairs for every .dylib in a brewed formula's lib dir."""
    prefix = brew_prefix(formula)
    if not prefix:
        print(f'[mpv-deps] WARNING: could not resolve brew prefix for {formula!r}')
        return []
    lib_dir = os.path.join(prefix, 'lib')
    if not os.path.isdir(lib_dir):
        return []
    out = []
    for fname in os.listdir(lib_dir):
        if fname.endswith('.dylib'):
            full = os.path.join(lib_dir, fname)
            # resolve symlinks (e.g. libmpv.dylib -> libmpv.2.dylib) to the real file
            out.append((os.path.realpath(full), '.'))
    return out


MPV_FORMULAS = [
    'mpv',
    'ffmpeg',
    'jpeg-turbo',
    'libarchive',
    'libass',
    'libbluray',
    'libplacebo',
    'little-cms2',
    'luajit',
    'mujs',
    'rubberband',
    'uchardet',
    'vapoursynth',
    'vulkan-loader',
    'zimg',
    'molten-vk',
]

mpv_binaries = []
_seen = set()
for formula in MPV_FORMULAS:
    for src, dest in collect_dylibs(formula):
        if src not in _seen and os.path.exists(src):
            _seen.add(src)
            mpv_binaries.append((src, dest))

print(f'[mpv-deps] bundling {len(mpv_binaries)} dylibs from {len(MPV_FORMULAS)} formulas')

a = Analysis(
    [os.path.join(EDGWARE_DIR, 'src/main_edgeware.py')],
    pathex=[EDGWARE_DIR],
    binaries=mpv_binaries,
    datas=[
        (os.path.join(EDGWARE_DIR, 'assets'), 'assets'),
        (os.path.join(EDGWARE_DIR, 'data/presets'), 'data/presets'),
        (os.path.join(EDGWARE_DIR, 'src/os_utils/angle_libs'), 'src/os_utils/angle_libs'),
        (os.path.join(_VIDEOPROPS_DIR, 'binary_dependencies'), 'videoprops/binary_dependencies'),
    ],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.simpledialog',
        'PIL', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageFilter',
        'mpv',
        'pyglet', 'pyglet.media',
        'pystray',
        'pynput', 'pynput.keyboard',
        'pypresence',
        'desktop_notifier', 'desktop_notifier.sync', 'desktop_notifier.common',
        'desktop_notifier.backends', 'desktop_notifier.backends.base',
        'desktop_notifier.resources',
        'booru',
        'requests',
        'screeninfo',
        'sounddevice',
        'filetype',
        'get_video_properties',
        'voluptuous',
        'tkinterweb', 'tkinter_tooltip',
        'AppKit', 'Foundation', 'Quartz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[os.path.join(EDGWARE_DIR, 'macos/rthook_mpv.py')],
    excludes=[
        'tkcalendar', 'tktimepicker', 'ttkwidgets',
        'numpy', 'pandas', 'scipy',
        'matplotlib', 'pytest', 'unittest',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Edgeware++',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name='Edgeware++',
)

app = BUNDLE(
    coll,
    name='Edgeware++.app',
    icon=os.path.join(EDGWARE_DIR, 'assets/default_icon.ico'),
    bundle_identifier='com.edgewareplusplus.app',
    info_plist={
        'CFBundleName': 'Edgeware++',
        'CFBundleDisplayName': 'Edgeware++',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
