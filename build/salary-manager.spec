# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Salary Manager.

Build with (from project root):
    pyinstaller build/salary-manager.spec

Or use the provided build scripts:
    Windows : build\build_exe.bat
    macOS   : bash build/build_exe.sh
"""

import os

# SPECPATH = directory of this .spec file (i.e. <project>/build/)
PROJECT_ROOT = os.path.abspath(os.path.join(SPECPATH, ".."))

block_cipher = None

# ── Collected data ────────────────────────────────────────────────────────────

datas = [
    (os.path.join(PROJECT_ROOT, "frontend"),                  "frontend"),
    (os.path.join(PROJECT_ROOT, "backend", "main.py"),        "backend"),
    (os.path.join(PROJECT_ROOT, "backend", "database.py"),    "backend"),
    (os.path.join(PROJECT_ROOT, "backend", "gmail_integration.py"), "backend"),
    (os.path.join(PROJECT_ROOT, "backend", "models"),         "models"),
]

# ── Hidden imports ────────────────────────────────────────────────────────────

hiddenimports = [
    "uvicorn",
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "fastapi",
    "fastapi.staticfiles",
    "fastapi.responses",
    "starlette",
    "starlette.staticfiles",
    "starlette.responses",
    "starlette.middleware",
    "starlette.middleware.cors",
    "anyio",
    "anyio._backends._asyncio",
    "email.mime.text",
    "email.mime.multipart",
    "imaplib",
    "html.parser",
    "sqlite3",
    "numpy",
    "easyocr",
    "easyocr.easyocr",
    "torch",
    "torchvision",
    "cv2",
    "PIL",
    "PIL.Image"
]

# ── Analysis ──────────────────────────────────────────────────────────────────

a = Analysis(
    [os.path.join(PROJECT_ROOT, "launcher.py")],
    pathex=[PROJECT_ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    # Exclude heavy ML packages — user supplies .pth model files separately
    excludes=[
        "matplotlib", "sklearn",
        "IPython", "notebook", "jupyter",
        "tkinter", "wx", "PyQt5", "PyQt6",
    ],
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
    name="SalaryManager",
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
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="SalaryManager",
)
