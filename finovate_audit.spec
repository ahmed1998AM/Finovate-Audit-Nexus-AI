# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import re
from PyInstaller.utils.hooks import collect_submodules, collect_data_files

block_cipher = None
project_root = os.path.abspath(os.getcwd())

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
    'loguru',
    'oracledb',
    'pandas',
    'numpy',
    'matplotlib',
    'sqlalchemy',
    'alembic',
]

# الحل النووي: قراءة ملف التبعيات وإضافة كل شيء فيه
try:
    req_file = 'requirements-windows.txt' if os.path.exists('requirements-windows.txt') else 'requirements.txt'
    with open(req_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # استخراج اسم المكتبة فقط (مثلاً fastapi من fastapi==0.109.0)
                match = re.match(r'^([a-zA-Z0-9_\-\[\]]+)', line)
                if match:
                    pkg = match.group(1).split('[')[0].replace('-', '_')
                    if pkg not in hidden_imports:
                        hidden_imports.append(pkg)
except Exception as e:
    print(f"Warning: Could not read requirements file: {e}")

# إضافة كافة الموديلات الفرعية لضمان عدم نسيان أي ملف
hidden_imports += collect_submodules('PySide6')
hidden_imports += collect_submodules('fastapi')
hidden_imports += collect_submodules('uvicorn')
hidden_imports += collect_submodules('sqlalchemy')
hidden_imports += collect_submodules('loguru')

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
    pathex=[project_root],
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
    [],
    exclude_binaries=True,
    name='FinovateAudit',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets/icon.ico'],
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='FinovateAudit',
)
