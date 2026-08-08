# -*- mode: python ; coding: utf-8 -*-
import os

# Spec lives in edgeware/macos/; project root is edgeware/
EDGWARE_DIR = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(EDGWARE_DIR, 'src/main_config.py')],
    pathex=[EDGWARE_DIR],
    binaries=[],
    datas=[
        (os.path.join(EDGWARE_DIR, 'assets'), 'assets'),
        (os.path.join(EDGWARE_DIR, 'data/presets'), 'data/presets'),
    ],
    hiddenimports=[
        'tkinter', 'tkinter.ttk', 'tkinter.messagebox', 'tkinter.simpledialog',
        'tkinterweb', 'tkinter_tooltip',
        'PIL', 'PIL.Image', 'PIL.ImageTk',
        'pynput', 'pynput.keyboard',
        'voluptuous',
        'requests',
        'screeninfo',
        'tkcalendar', 'ttkwidgets', 'tktimepicker',
        'AppKit', 'Foundation', 'Quartz',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'desktop_notifier', 'booru', 'sounddevice',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Edgeware++ Config',
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
    name='Edgeware++ Config',
)

app = BUNDLE(
    coll,
    name='Edgeware++ Config.app',
    icon=os.path.join(EDGWARE_DIR, 'assets/default_config_icon.ico'),
    bundle_identifier='com.edgewareplusplus.config',
    info_plist={
        'CFBundleName': 'Edgeware++ Config',
        'CFBundleDisplayName': 'Edgeware++ Config',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': False,
        'NSHighResolutionCapable': True,
        'NSRequiresAquaSystemAppearance': False,
    },
)
