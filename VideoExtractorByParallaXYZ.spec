# -*- mode: python ; coding: utf-8 -*-

# New architecture: binaries are NOT bundled in the .exe
# They are placed in bin/ directory next to the .exe
# This allows yt-dlp.exe to be updated independently

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[
        # NO binaries bundled - they will be external in bin/ folder
    ],
    datas=[
        # Only bundle icons in _MEIPASS (they don't need updates)
        ('assets/icons/icon.ico', 'assets/icons'),
        ('assets/icons/refresh.ico', 'assets/icons'),
        ('assets/icons/download-btn.ico', 'assets/icons'),
    ],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Video Extractor By ParallaXYZ',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icons/icon.ico'],
)
