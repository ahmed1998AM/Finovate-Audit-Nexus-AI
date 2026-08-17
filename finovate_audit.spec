# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None

# إضافة مسارات بايثون الحالية لضمان عثور PyInstaller على المكتبات المثبتة
for path in sys.path:
    if "site-packages" in path:
        print(f"Adding to search path: {path}")

# إجبار النظام على جمع كافة التبعيات بشكل شامل
hidden_imports = [
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.lifespan',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.h11_impl',
    'uvicorn.protocols.http.httptools_impl',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.websockets_impl',
    'uvicorn.protocols.websockets.wsproto_impl',
    'email_validator',
    'pydantic_settings',
    'passlib.handlers.bcrypt',
    'jose',
    'backend.services.updater',
    'version',
]

# إضافة كافة الموديلات الفرعية لضمان عدم نسيان أي ملف
hidden_imports += collect_submodules('PySide6')
hidden_imports += collect_submodules('fastapi')
hidden_imports += collect_submodules('uvicorn')
hidden_imports += collect_submodules('sqlalchemy')

extra_datas = [
    ('frontend', 'frontend'),
    ('database', 'database'),
    ('agents', 'agents'),
    ('backend', 'backend'),
    ('connectors', 'connectors'),
    ('assets', 'assets'),
    ('config', 'config'),
    ('templates', 'templates'),
]
extra_datas += collect_data_files('PySide6')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=extra_datas,
    hiddenimports=hidden_imports,
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
