# -*- mode: python ; coding: utf-8 -*-
"""
neurosoft.spec
==============
Receta de PyInstaller para empaquetar NeuroSoft en un único ejecutable.

Estructura del bundle:
    /_MEIPASS/
      ├── app/                  ← paquete backend (FastAPI + SQLAlchemy)
      ├── data/                 ← BD_NEURO_MAESTRA.json (baremos)
      ├── static/               ← frontend compilado (Vite build)
      └── launcher.py           ← este entry point

Build manual:
    python build.py             (recomendado — limpio y reproducible)
    pyinstaller --clean neurosoft.spec
"""
from pathlib import Path
import os
import sys

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Detectamos la raíz del proyecto desde la ubicación del .spec
ROOT = Path(os.getcwd()).resolve()
BACKEND = ROOT / "neurosoft-backend"
FRONTEND_DIST = ROOT / "neurosoft-frontend" / "dist"

# ---------------------------------------------------------------
# Assets que van dentro del bundle
# ---------------------------------------------------------------

datas = []

# Paquete 'app' completo (routers, use cases, ORM, etc.)
if (BACKEND / "app").is_dir():
    datas.append((str(BACKEND / "app"), "app"))

# Baremos
baremo = BACKEND / "data" / "BD_NEURO_MAESTRA.json"
if baremo.exists():
    datas.append((str(baremo), "data"))

# Frontend compilado (Vite → /dist)
if FRONTEND_DIST.is_dir():
    datas.append((str(FRONTEND_DIST), "static"))
else:
    sys.stderr.write(
        "\n[neurosoft.spec] ADVERTENCIA: no existe neurosoft-frontend/dist. "
        "Ejecute `npm run build` en el frontend antes de empaquetar.\n"
    )

# §ollama-fix: NO bundlear OllamaSetup.exe dentro de PyInstaller.
# Razón: comprimir un .exe de 1.3 GB dentro de otro .exe de 1.3 GB corrompe
# el archivo (Inno Setup reporta "The setup files are corrupted" al extraer
# y lanzar OllamaSetup desde _MEIPASS). En lugar de eso, distribuimos
# OllamaSetup.exe como archivo separado dentro del instalador Inno Setup
# (NeuroSoft-Setup.exe lo coloca en {app}\vendor\ollama\OllamaSetup.exe).
# El backend busca el archivo junto al .exe principal en producción.
sys.stderr.write("[neurosoft.spec] OllamaSetup.exe NO se bundlea — se distribuye como archivo separado en el instalador.\n")

# Alembic migrations (si llegan a existir dentro del bundle)
alembic_dir = BACKEND / "alembic"
if alembic_dir.is_dir():
    datas.append((str(alembic_dir), "alembic"))
    alembic_ini = BACKEND / "alembic.ini"
    if alembic_ini.exists():
        datas.append((str(alembic_ini), "."))

# pywebview — recursos internos (templates HTML, DLLs WebView2 runtime loader, etc.)
try:
    datas += collect_data_files("webview")
except Exception as _e:
    sys.stderr.write(f"[neurosoft.spec] pywebview data files no disponibles: {_e}\n")


# ---------------------------------------------------------------
# Hidden imports — módulos que PyInstaller no detecta automáticamente
# ---------------------------------------------------------------

hiddenimports = [
    # FastAPI / Uvicorn
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.httptools_impl",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",

    # SQLAlchemy dialect
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

    # PyJWT / passlib
    "jwt",
    "passlib.handlers.bcrypt",
    "bcrypt",

    # Email validators (pydantic)
    "email_validator",

    # Export DOCX / XLSX
    "docx",
    "docx.oxml",
    "openpyxl",
    "openpyxl.styles",
    "openpyxl.utils",

    # App principal
    "app",
    "app.main",
]

# pywebview — incluye todos sus submódulos (platforms, util, http, etc.)
try:
    hiddenimports += collect_submodules("webview")
except Exception as _e:
    sys.stderr.write(f"[neurosoft.spec] pywebview submodules no disponibles: {_e}\n")

# Plataformas específicas (pywebview las carga dinámicamente según SO)
hiddenimports += [
    "webview.platforms.edgechromium",
    "webview.platforms.mshtml",
    "webview.platforms.winforms",
    "webview.platforms.cef",
    "webview.http",
    "webview.util",
    "webview.window",
    "webview.menu",
    "webview.event",
]

# Optional: clr_loader / pythonnet son usados por la plataforma mshtml (IE).
# En sistemas con Edge/WebView2 (todo Windows 10/11 moderno) no son necesarios;
# intentamos incluirlos si están disponibles, si no los ignoramos.
for _opt in ("clr_loader", "pythonnet"):
    try:
        __import__(_opt)
        hiddenimports.append(_opt)
    except Exception:
        pass


# ---------------------------------------------------------------
# Análisis
# ---------------------------------------------------------------

a = Analysis(
    ["launcher.py"],
    pathex=[str(BACKEND)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Librerías pesadas que NO usamos — se excluyen para reducir peso
        "tkinter",
        "matplotlib.tests",
        "PIL.ImageTk",
        "pytest",
        "IPython",
        "jedi",
        "notebook",
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)


# ---------------------------------------------------------------
# Ejecutable único (onefile)
# ---------------------------------------------------------------

icon_path = str(ROOT / "neurosoft.ico") if (ROOT / "neurosoft.ico").exists() else None

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="NeuroSoft",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,                 # ventana GUI — sin consola negra
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    # Firma de codigo: setear NEUROSOFT_CODE_SIGN_IDENTITY al buildear.
    # Requiere un certificado EV Code Signing (DigiCert, Sectigo, etc.).
    # Ejemplo: $env:NEUROSOFT_CODE_SIGN_IDENTITY="CN=NeuroSoft SAS"
    # Sin esta variable, el .exe se genera sin firma y Windows Defender
    # muestra advertencia SmartScreen al instalarlo.
    codesign_identity=os.environ.get("NEUROSOFT_CODE_SIGN_IDENTITY"),
    entitlements_file=None,
    icon=icon_path,
    version_file=None,
)
