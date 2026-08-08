# -*- mode: python ; coding: utf-8 -*-
import os

# Spec lives in edgeware/macos/; project root is edgeware/
EDGWARE_DIR = os.path.abspath(os.path.join(SPECPATH, '..'))

a = Analysis(
    [os.path.join(EDGWARE_DIR, 'src/panic.py')],
    pathex=[EDGWARE_DIR],
    binaries=[],
    datas=[],
    hiddenimports=[
        'multiprocessing.connection',
        'tkinter', 'tkinter.simpledialog',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'desktop_notifier', 'booru', 'sounddevice',
        'screeninfo', 'numpy', 'pandas', 'scipy',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Edgeware++ Panic',
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
    name='Edgeware++ Panic',
)

app = BUNDLE(
    coll,
    name='Edgeware++ Panic.app',
    icon=os.path.join(EDGWARE_DIR, 'assets/default_panic_icon.ico'),
    bundle_identifier='com.edgewareplusplus.panic',
    info_plist={
        'CFBundleName': 'Edgeware++ Panic',
        'CFBundleDisplayName': 'Edgeware++ Panic',
        'CFBundleShortVersionString': '1.0.0',
        'LSUIElement': True,
        'NSHighResolutionCapable': True,
    },
)
