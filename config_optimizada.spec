# -*- mode: python ; coding: utf-8 -*-
"""
config_optimizada.spec
======================
Receta PyInstaller optimizada para NeuroSoft (pywebview + FastAPI).

Cambios respecto a neurosoft.spec:
  • Modo onedir (COLLECT) — más estable que onefile (sin extraer _MEIPASS en cada arranque).
  • Mismos hidden imports de pywebview que neurosoft.spec (collect_submodules + pythonnet).
  • optimize=0 — bytecode sin optimizar agresivo (paridad calidad con spec legacy).
  • Exclusiones solo de librerías realmente no usadas (numpy, tkinter, tests…).
  • Ollama NO se bundlea (distribuido aparte vía Inno Setup, componente opcional).
  • Post-build: tools/verify_desktop_bundle.py (ventana + /health).

Build:
    python build.py --spec config_optimizada.spec
    pyinstaller --clean --noconfirm config_optimizada.spec

Salida:
    dist/NeuroSoft/NeuroSoft.exe  (+ DLLs y dependencias en la misma carpeta)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

ROOT = Path(os.getcwd()).resolve()
BACKEND = ROOT / "neurosoft-backend"
FRONTEND_DIST = ROOT / "neurosoft-frontend" / "dist"

# ── Datos embebidos ──────────────────────────────────────────

datas: list[tuple[str, str]] = []

if (BACKEND / "app").is_dir():
    datas.append((str(BACKEND / "app"), "app"))

baremo = BACKEND / "data" / "BD_NEURO_MAESTRA.json"
if baremo.exists():
    datas.append((str(baremo), "data"))

stimuli_manifest = BACKEND / "data" / "stimuli_assets" / "stimuli_manifest.json"
if stimuli_manifest.is_file():
    datas.append((str(stimuli_manifest), "data/stimuli_assets"))
    sys.stderr.write("[config_optimizada.spec] stimuli_manifest.json (sin PNG)\n")

if FRONTEND_DIST.is_dir():
    datas.append((str(FRONTEND_DIST), "static"))
else:
    sys.stderr.write(
        "\n[config_optimizada.spec] ADVERTENCIA: falta neurosoft-frontend/dist\n"
    )

alembic_dir = BACKEND / "alembic"
if alembic_dir.is_dir():
    datas.append((str(alembic_dir), "alembic"))
    alembic_ini = BACKEND / "alembic.ini"
    if alembic_ini.exists():
        datas.append((str(alembic_ini), "."))

try:
    datas += collect_data_files("webview", excludes=["**/cef/**", "**/gtk/**", "**/cocoa/**"])
except Exception as exc:
    sys.stderr.write(f"[config_optimizada.spec] webview data: {exc}\n")

# ── Hidden imports (paridad con neurosoft.spec — sin recortes arriesgados) ──

hiddenimports = [
    # Uvicorn / ASGI
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    # SQLAlchemy
    "sqlalchemy.dialects.sqlite",
    "sqlalchemy.sql.default_comparator",
    # APScheduler
    "apscheduler.schedulers.background",
    "apscheduler.triggers.cron",
    "apscheduler.triggers.date",
    "apscheduler.triggers.interval",
    "apscheduler.executors.pool",
    "apscheduler.jobstores.memory",
    # Reportes
    "reportlab.graphics.barcode.code128",
    "reportlab.graphics.barcode.qr",
    "reportlab.pdfbase._fontdata",
    # Auth
    "jwt",
    "passlib.handlers.bcrypt",
    "bcrypt",
    "email_validator",
    # Export
    "docx",
    "docx.oxml",
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.utils",
    # App
    "app",
    "app.main",
]

try:
    hiddenimports += collect_submodules("webview")
except Exception as exc:
    sys.stderr.write(f"[config_optimizada.spec] webview submodules: {exc}\n")

hiddenimports += [
    "webview.platforms.edgechromium",
    "webview.platforms.winforms",
    "webview.platforms.win32",
    "webview.http",
    "webview.util",
    "webview.window",
    "webview.menu",
    "webview.event",
]

for _opt in ("clr_loader", "pythonnet"):
    try:
        __import__(_opt)
        hiddenimports.append(_opt)
    except Exception:
        sys.stderr.write(f"[config_optimizada.spec] ADVERTENCIA: {_opt} no importable en build\n")

# ── Exclusiones — librerías pesadas o plataformas no usadas ──

EXCLUDES = [
    # GUI / notebooks
    "tkinter",
    "matplotlib",
    "matplotlib.tests",
    "PIL.ImageTk",
    "IPython",
    "jedi",
    "notebook",
    # Tests / dev tools (no deben estar en venv de build, pero por si acaso)
    "pytest",
    "_pytest",
    "mypy",
    "mypyc",
    # Ciencia de datos (no usadas)
    "numpy",
    "scipy",
    "pandas",
    "sklearn",
    "torch",
    "tensorflow",
    # PDF alternativo no referenciado en código
    "fitz",
    "pymupdf",
    # pywebview — plataformas que NO usamos en Windows
    "webview.platforms.cef",
    "webview.platforms.gtk",
    "webview.platforms.cocoa",
    "webview.platforms.qt",
    "webview.platforms.mshtml",
    # Win32 extras no requeridos
    "pythonwin",
    "win32com",
    "win32comext",
]

block_cipher = None

a = Analysis(
    [str(ROOT / "launcher.py")],
    pathex=[str(BACKEND)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=EXCLUDES,
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, cipher=block_cipher)

icon_path = str(ROOT / "neurosoft.ico") if (ROOT / "neurosoft.ico").exists() else None

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="NeuroSoft",
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
    codesign_identity=os.environ.get("NEUROSOFT_CODE_SIGN_IDENTITY"),
    entitlements_file=None,
    icon=icon_path,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="NeuroSoft",
)
