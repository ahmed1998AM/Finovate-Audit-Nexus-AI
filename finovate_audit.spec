# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('frontend', 'frontend'),
        ('database', 'database'),
        ('agents', 'agents'),
        ('backend', 'backend'),
        ('connectors', 'connectors'),
        ('assets', 'assets'),
        ('config', 'config'),
        ('templates', 'templates'),
    ],
    hiddenimports=[
        'tinydb',
        'pandas',
        'numpy',
        'matplotlib',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'uvicorn',
        'fastapi',
        'sqlalchemy',
        'alembic',
        'pydantic_settings',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='FinovateAudit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    # Using --onedir for better compatibility and reduced false positives from antivirus.
    # If a single file executable is desired, change this to True and ensure the build scripts
    # or workflows use the --onefile flag with pyinstaller, and remove the --onedir flag.

    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.ico'],
)
