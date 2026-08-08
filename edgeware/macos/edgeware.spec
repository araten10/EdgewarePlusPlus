# -*- mode: python ; coding: utf-8 -*-
import os

# Spec lives in edgeware/macos/; project root is edgeware/
EDGWARE_DIR = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(EDGWARE_DIR, 'src/main_edgeware.py')],
    pathex=[EDGWARE_DIR],
    binaries=[],
    datas=[
        (os.path.join(EDGWARE_DIR, 'assets'), 'assets'),
        (os.path.join(EDGWARE_DIR, 'data/presets'), 'data/presets'),
        (os.path.join(EDGWARE_DIR, 'src/os_utils/angle_libs'), 'src/os_utils/angle_libs'),
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
