"""
build.py
========
Pipeline completo de empaquetado de NeuroSoft.

Produce: dist/NeuroSoft.exe  (un único ejecutable, sin consola)

Pasos:
    1. Verifica dependencias (pyinstaller, pywebview) — las instala si faltan.
    2. Ejecuta `npm run build` en el frontend → genera neurosoft-frontend/dist.
    3. Ejecuta PyInstaller con neurosoft.spec → genera dist/NeuroSoft.exe.
    4. Reporta el tamaño final y la ubicación.

Uso:
    python build.py                 # build normal
    python build.py --skip-frontend # usa el dist/ que ya está compilado
    python build.py --clean         # borra dist/ y build/ antes
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "neurosoft-backend"
FRONTEND = ROOT / "neurosoft-frontend"
VENDOR = ROOT / "vendor"
VENV_PY = BACKEND / "venv" / "Scripts" / ("python.exe" if sys.platform == "win32" else "python")

# Instalador oficial de Ollama para Windows (Fase G.1c del ROADMAP)
# El usuario pidió bundlear Ollama completo — el installer pesa ~700 MB.
OLLAMA_WIN_URL  = "https://ollama.com/download/OllamaSetup.exe"
OLLAMA_WIN_NAME = "OllamaSetup.exe"


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _log(msg: str, level: str = "info") -> None:
    color = {
        "info":  "\033[36m",  # cyan
        "ok":    "\033[32m",  # verde
        "warn":  "\033[33m",  # amarillo
        "err":   "\033[31m",  # rojo
    }.get(level, "")
    reset = "\033[0m" if color else ""
    print(f"{color}[build]{reset} {msg}", flush=True)


def _run(cmd: list[str], cwd: Path | None = None, check: bool = True, env: dict | None = None) -> int:
    _log(f"$ {' '.join(cmd)}  (cwd={cwd or ROOT})")
    r = subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env)
    if check and r.returncode != 0:
        _log(f"comando falló con código {r.returncode}", "err")
        sys.exit(r.returncode)
    return r.returncode


def _python_exe() -> str:
    """Devuelve el intérprete del venv del backend si existe, si no el actual."""
    if VENV_PY.exists():
        return str(VENV_PY)
    return sys.executable


def _human_size(path: Path) -> str:
    try:
        size = path.stat().st_size
    except Exception:
        return "?"
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


# ─────────────────────────────────────────────────────────────
# Pasos
# ─────────────────────────────────────────────────────────────

def step_check_tools() -> None:
    _log("Verificando herramientas…")

    # Node
    try:
        subprocess.run(
            ["npm" if sys.platform != "win32" else "npm.cmd", "--version"],
            check=True, capture_output=True,
        )
    except Exception:
        _log("npm no está instalado o no está en PATH. Instale Node.js LTS.", "err")
        sys.exit(1)

    # Python deps de build
    py = _python_exe()
    for pkg, mod in (("pyinstaller", "PyInstaller"), ("pywebview", "webview")):
        try:
            subprocess.run(
                [py, "-c", f"import {mod}"], check=True, capture_output=True,
            )
        except subprocess.CalledProcessError:
            _log(f"Instalando {pkg}…", "warn")
            _run([py, "-m", "pip", "install", pkg])

    _log("Herramientas OK.", "ok")


def step_build_frontend(skip: bool = False) -> None:
    if skip:
        _log("Omitiendo build del frontend (--skip-frontend).", "warn")
        return
    _log("Compilando frontend con Vite…")
    npm = "npm.cmd" if sys.platform == "win32" else "npm"
    # Instalar deps si falta node_modules
    if not (FRONTEND / "node_modules").is_dir():
        _run([npm, "install"], cwd=FRONTEND)
    _run([npm, "run", "build"], cwd=FRONTEND)
    dist = FRONTEND / "dist"
    if not (dist / "index.html").exists():
        _log("npm run build terminó sin producir dist/index.html", "err")
        sys.exit(1)
    _log(f"Frontend compilado -> {dist}", "ok")


def step_download_ollama(skip: bool = False) -> None:
    """
    Descarga el instalador oficial de Ollama para Windows al directorio
    `vendor/ollama/` para que sea empaquetado por PyInstaller.
    Si ya existe y pesa > 100 MB, se asume válido y se omite.
    """
    if skip:
        _log("Omitiendo descarga de Ollama (--skip-ollama).", "warn")
        return
    if sys.platform != "win32":
        _log("Plataforma != win32, se omite el bundle de Ollama.", "warn")
        return

    target_dir = VENDOR / "ollama"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / OLLAMA_WIN_NAME

    if target.exists() and target.stat().st_size > 100 * 1024 * 1024:
        _log(f"Ollama installer ya presente -> {target} ({_human_size(target)})", "ok")
        return

    _log(f"Descargando Ollama desde {OLLAMA_WIN_URL} (~700 MB, puede tardar)…")
    try:
        # urlretrieve con barra de progreso simple
        def _progress(block, block_size, total_size):
            if total_size <= 0:
                return
            pct = min(100.0, block * block_size * 100.0 / total_size)
            if int(pct) % 5 == 0:
                print(f"  … {pct:5.1f}%  ({block * block_size // (1024*1024)} MB)", end="\r", flush=True)

        urllib.request.urlretrieve(OLLAMA_WIN_URL, target, reporthook=_progress)
        print()  # newline después de la barra
        sha = hashlib.sha256(target.read_bytes()).hexdigest()[:16]
        _log(f"Ollama descargado -> {target} ({_human_size(target)})  sha256={sha}…", "ok")
    except Exception as e:
        _log(f"Falló la descarga de Ollama: {e}", "err")
        _log("El build continuará, pero el usuario deberá instalar Ollama manualmente.", "warn")


def step_clean() -> None:
    for d in ("dist", "build"):
        p = ROOT / d
        if p.exists():
            _log(f"Limpiando {p}…", "warn")
            shutil.rmtree(p, ignore_errors=True)


def step_pyinstaller() -> None:
    _log("Empaquetando con PyInstaller…")
    py = _python_exe()

    # Leer la version actual desde el codigo fuente para que el endpoint
    # GET /api/v1/version sepa cual es la version empaquetada.
    import re
    config_py = ROOT / "neurosoft-backend" / "app" / "core" / "config.py"
    version_match = None
    if config_py.exists():
        content = config_py.read_text(encoding="utf-8")
        version_match = re.search(r'api_version\s*[=:]\s*"([^"]+)"', content)
    current_version = version_match.group(1) if version_match else "2.0.0"
    _log(f"Version detectada: {current_version}", "info")

    # NEUROSOFT_LATEST_VERSION: si quieres que los clientes vean
    # "actualizacion disponible", setea esta variable ANTES de buildear.
    # Ejemplo: $env:NEUROSOFT_LATEST_VERSION="2.1.0"; python build.py
    latest = os.environ.get("NEUROSOFT_LATEST_VERSION", current_version)
    if latest != current_version:
        _log(f"ATENCION: NEUROSOFT_LATEST_VERSION={latest} (actual={current_version})", "warn")
        _log("Los clientes veran notificacion de actualizacion.", "warn")

    env = os.environ.copy()
    env["NEUROSOFT_CURRENT_VERSION"] = current_version
    env["NEUROSOFT_LATEST_VERSION"] = latest

    _run([
        py, "-m", "PyInstaller",
        "--clean",
        "--noconfirm",
        "neurosoft.spec",
    ], cwd=ROOT, env=env)
    exe = ROOT / "dist" / ("NeuroSoft.exe" if sys.platform == "win32" else "NeuroSoft")
    if not exe.exists():
        _log("PyInstaller terminó pero no encontré el ejecutable.", "err")
        sys.exit(1)
    _log(f"Ejecutable generado: {exe}  ({_human_size(exe)})", "ok")


def step_make_update() -> None:
    """
    Genera un archivo .nsupdate con el frontend compilado + manifest.
    Este archivo se envia al clinico para actualizar via ConfigPage > Actualizar.
    """
    import zipfile
    import re as _re

    frontend_dist = FRONTEND / "dist"
    if not frontend_dist.exists():
        _log("Frontend dist/ no encontrado. Ejecuta npm run build primero.", "err")
        sys.exit(1)

    # Leer version
    config_py = BACKEND / "app" / "core" / "config.py"
    version = "0.0.0"
    if config_py.exists():
        m = _re.search(r'api_version\s*[=:]\s*"([^"]+)"', config_py.read_text(encoding="utf-8"))
        if m:
            version = m.group(1)

    out_name = f"neurosoft-v{version}.nsupdate"
    out_path = ROOT / "dist" / out_name

    manifest = {
        "version": version,
        "fecha": time.strftime("%Y-%m-%d"),
        "tipo": "frontend",
        "nota": "Actualizacion de interfaz. No requiere reinstalar el .exe.",
    }

    _log(f"Generando {out_name} con version {version}...", "info")

    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for f in frontend_dist.rglob("*"):
            if f.is_file():
                arcname = "frontend/" + str(f.relative_to(frontend_dist)).replace("\\", "/")
                zf.write(f, arcname)

    _log(f"Archivo generado: {out_path}  ({_human_size(out_path)})", "ok")
    _log(f"Envia este archivo al clinico para que lo suba en ConfigPage > Actualizar.", "info")


def step_report() -> None:
    exe = ROOT / "dist" / ("NeuroSoft.exe" if sys.platform == "win32" else "NeuroSoft")
    print()
    _log("=" * 55, "ok")
    _log(f"Build completado - {_human_size(exe)}", "ok")
    _log(f"Ubicacion: {exe}", "ok")
    _log("=" * 55, "ok")
    print()
    _log("Para probar:  doble-click en el .exe.", "info")
    _log("Los datos se guardan en: %APPDATA%/NeuroSoft (Windows).", "info")


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(description="Build de NeuroSoft → .exe")
    parser.add_argument("--skip-frontend", action="store_true",
                        help="No recompila el frontend (usa dist/ existente)")
    parser.add_argument("--clean", action="store_true",
                        help="Limpia dist/ y build/ antes del empaquetado")
    parser.add_argument("--skip-ollama", action="store_true",
                        help="No descarga el instalador de Ollama (util para builds rapidos)")
    parser.add_argument("--make-update", action="store_true",
                        help="Genera un archivo .nsupdate con el frontend + changelog (sin .exe)")
    args = parser.parse_args()

    t0 = time.time()
    step_check_tools()
    if args.clean:
        step_clean()
    step_build_frontend(skip=args.skip_frontend)

    if args.make_update:
        step_make_update()
        _log(f"Tiempo total: {time.time() - t0:.1f}s", "info")
        return 0

    step_download_ollama(skip=args.skip_ollama)
    step_pyinstaller()
    step_report()
    _log(f"Tiempo total: {time.time() - t0:.1f}s", "info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
