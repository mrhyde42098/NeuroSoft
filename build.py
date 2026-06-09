"""
build.py
========
Pipeline completo de empaquetado de NeuroSoft.

Produce (por defecto, onedir):
    dist/NeuroSoft/NeuroSoft.exe  (+ dependencias en la misma carpeta)
    dist/update.json              (manifest firmado para auto-update)
    dist/NeuroSoft-Setup.exe      (Inno Setup, Ollama opcional)

Uso:
    python build.py                      # build completo optimizado
    python build.py --skip-frontend
    python build.py --skip-ollama        # instalador ~50 MB sin IA local
    python build.py --legacy-onefile     # neurosoft.spec (onefile legacy)
    python build.py --make-update        # solo .nsupdate de frontend
    python build.py --clean
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "neurosoft-backend"
FRONTEND = ROOT / "neurosoft-frontend"
VENDOR = ROOT / "vendor"
VENV_PY = BACKEND / "venv" / "Scripts" / ("python.exe" if sys.platform == "win32" else "python")

DEFAULT_SPEC = "config_optimizada.spec"
LEGACY_SPEC = "neurosoft.spec"
DEFAULT_ISS = ROOT / "installer" / "NeuroSoftOptimized.iss"

OLLAMA_WIN_URL = "https://ollama.com/download/OllamaSetup.exe"
OLLAMA_WIN_NAME = "OllamaSetup.exe"

ISCC_CANDIDATES = [
    Path(r"C:\Users\DESKTOP\AppData\Local\Programs\Inno Setup 6\ISCC.exe"),
    Path(os.environ.get("ProgramFiles(x86)", "")) / "Inno Setup 6" / "ISCC.exe",
    Path(os.environ.get("ProgramFiles", "")) / "Inno Setup 6" / "ISCC.exe",
]


def _log(msg: str, level: str = "info") -> None:
    color = {
        "info": "\033[36m",
        "ok": "\033[32m",
        "warn": "\033[33m",
        "err": "\033[31m",
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


def _read_version() -> str:
    config_py = BACKEND / "app" / "core" / "config.py"
    if config_py.exists():
        m = re.search(r'api_version\s*[=:]\s*"([^"]+)"', config_py.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return "2.0.0"


def _resolve_exe_path(*, onedir: bool) -> Path:
    if onedir:
        return ROOT / "dist" / "NeuroSoft" / ("NeuroSoft.exe" if sys.platform == "win32" else "NeuroSoft")
    return ROOT / "dist" / ("NeuroSoft.exe" if sys.platform == "win32" else "NeuroSoft")


def step_check_tools() -> None:
    _log("Verificando herramientas…")
    try:
        subprocess.run(
            ["npm.cmd" if sys.platform == "win32" else "npm", "--version"],
            check=True,
            capture_output=True,
        )
    except Exception:
        _log("npm no está instalado o no está en PATH.", "err")
        sys.exit(1)

    py = _python_exe()
    for pkg, mod in (("pyinstaller", "PyInstaller"), ("pywebview", "webview")):
        try:
            subprocess.run([py, "-c", f"import {mod}"], check=True, capture_output=True)
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
    if not (FRONTEND / "node_modules").is_dir():
        _run([npm, "install"], cwd=FRONTEND)
    _run([npm, "run", "build"], cwd=FRONTEND)
    if not (FRONTEND / "dist" / "index.html").exists():
        _log("npm run build terminó sin index.html", "err")
        sys.exit(1)
    _log(f"Frontend compilado -> {FRONTEND / 'dist'}", "ok")


def step_download_ollama(skip: bool = False) -> None:
    if skip:
        _log("Omitiendo descarga de Ollama (--skip-ollama).", "warn")
        return
    if sys.platform != "win32":
        _log("Plataforma != win32, se omite Ollama.", "warn")
        return

    target_dir = VENDOR / "ollama"
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / OLLAMA_WIN_NAME

    if target.exists() and target.stat().st_size > 100 * 1024 * 1024:
        _log(f"Ollama ya presente -> {target} ({_human_size(target)})", "ok")
        return

    _log(f"Descargando Ollama desde {OLLAMA_WIN_URL}…")
    try:
        def _progress(block, block_size, total_size):
            if total_size <= 0:
                return
            pct = min(100.0, block * block_size * 100.0 / total_size)
            if int(pct) % 10 == 0:
                print(f"  … {pct:5.1f}%", end="\r", flush=True)

        urllib.request.urlretrieve(OLLAMA_WIN_URL, target, reporthook=_progress)
        print()
        _log(f"Ollama descargado -> {target} ({_human_size(target)})", "ok")
    except Exception as e:
        _log(f"Falló descarga de Ollama: {e}", "warn")


def step_clean() -> None:
    for d in ("dist", "build"):
        p = ROOT / d
        if p.exists():
            _log(f"Limpiando {p}…", "warn")
            shutil.rmtree(p, ignore_errors=True)


def step_baremos_shards() -> None:
    master = BACKEND / "data" / "BD_NEURO_MAESTRA.json"
    script = ROOT / "docs" / "scripts" / "split_baremos_poblacion.py"
    if not master.exists() or not script.exists():
        _log("Baremos master ausente — omitiendo shards.", "warn")
        return
    _run([_python_exe(), str(script), "--input", str(master)], check=True)
    _log("Baremos shards OK.", "ok")


def step_manual_pdf() -> None:
    script = ROOT / "docs" / "scripts" / "generate_manual_pdf.py"
    if not script.exists():
        _log("generate_manual_pdf.py no encontrado — omitiendo PDF.", "warn")
        return
    out = ROOT / "dist" / "MANUAL_BETA_TESTER.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)
    _run([_python_exe(), str(script), str(out)], check=True)
    if out.exists():
        _log(f"Manual PDF -> {out} ({_human_size(out)})", "ok")


def step_py_compile_backend() -> None:
    _run([_python_exe(), "-m", "py_compile", str(BACKEND / "app" / "main.py")], check=True)


def step_pyinstaller(*, spec: str, onedir: bool) -> Path:
    _log(f"Empaquetando con PyInstaller ({spec})…")
    py = _python_exe()
    current_version = _read_version()
    _log(f"Versión detectada: {current_version}", "info")

    latest = os.environ.get("NEUROSOFT_LATEST_VERSION", current_version)
    if latest != current_version:
        _log(f"NEUROSOFT_LATEST_VERSION={latest} (build={current_version})", "warn")

    env = os.environ.copy()
    env["NEUROSOFT_CURRENT_VERSION"] = current_version
    env["NEUROSOFT_LATEST_VERSION"] = latest

    _run([py, "-m", "PyInstaller", "--clean", "--noconfirm", spec], cwd=ROOT, env=env)

    exe = _resolve_exe_path(onedir=onedir)
    if not exe.exists():
        _log(f"PyInstaller terminó pero no encontré {exe}", "err")
        sys.exit(1)
    _log(f"Ejecutable -> {exe} ({_human_size(exe)})", "ok")
    return exe


def step_package_onedir_zip(version: str) -> Path | None:
    """ZIP del directorio onedir para auto-update de carpeta completa."""
    src = ROOT / "dist" / "NeuroSoft"
    if not src.is_dir():
        return None
    out = ROOT / "dist" / f"NeuroSoft-v{version}-win64.zip"
    _log(f"Empaquetando {out.name}…")
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for f in src.rglob("*"):
            if f.is_file():
                arc = str(f.relative_to(src)).replace("\\", "/")
                zf.write(f, arc)
    _log(f"ZIP onedir -> {out} ({_human_size(out)})", "ok")
    return out


def step_update_manifest(*, onedir: bool, nsupdate: Path | None = None) -> None:
    script = ROOT / "tools" / "generate_update_manifest.py"
    if not script.exists():
        _log("generate_update_manifest.py no encontrado.", "warn")
        return

    version = _read_version()
    py = _python_exe()
    cmd = [py, str(script), "--version", version]

    exe = _resolve_exe_path(onedir=onedir)
    if exe.exists():
        cmd += ["--exe", str(exe)]

    zip_path = ROOT / "dist" / f"NeuroSoft-v{version}-win64.zip"
    if zip_path.exists():
        cmd += ["--dir-zip", str(zip_path)]

    if nsupdate is None:
        nsupdate = ROOT / "dist" / f"neurosoft-v{version}.nsupdate"
    if nsupdate.exists():
        cmd += ["--nsupdate", str(nsupdate)]

    _run(cmd, check=True)


def step_inno_setup(iss: Path | None = None, *, include_ollama: bool = False) -> None:
    iscc = next((p for p in ISCC_CANDIDATES if p.exists()), None)
    if iscc is None:
        _log("ISCC.exe no encontrado — omitiendo NeuroSoft-Setup.exe.", "warn")
        return
    iss = iss or DEFAULT_ISS
    if not iss.exists():
        _log(f"{iss.name} no encontrado.", "warn")
        return
    cmd = [str(iscc), str(iss)]
    ollama_bin = VENDOR / "ollama" / OLLAMA_WIN_NAME
    if include_ollama and ollama_bin.is_file():
        cmd.append("/DINCLUDE_OLLAMA=1")
        _log("Instalador INCLUYE Ollama (~1.4 GB)…", "warn")
    else:
        _log("Instalador compacto SIN Ollama embebido (~50 MB)…", "info")
    _log(f"Compilando {iss.name}…")
    _run(cmd, check=True)
    setup = ROOT / "dist" / "NeuroSoft-Setup.exe"
    if setup.exists():
        _log(f"Instalador -> {setup} ({_human_size(setup)})", "ok")


def step_make_update() -> Path:
    frontend_dist = FRONTEND / "dist"
    if not frontend_dist.exists():
        _log("Frontend dist/ no encontrado.", "err")
        sys.exit(1)

    version = _read_version()
    out_path = ROOT / "dist" / f"neurosoft-v{version}.nsupdate"
    manifest = {
        "version": version,
        "fecha": time.strftime("%Y-%m-%d"),
        "tipo": "frontend",
        "nota": "Actualización de interfaz. No requiere reinstalar el .exe.",
    }
    _log(f"Generando {out_path.name}…")
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
        for f in frontend_dist.rglob("*"):
            if f.is_file():
                arc = "frontend/" + str(f.relative_to(frontend_dist)).replace("\\", "/")
                zf.write(f, arc)
    _log(f"nsupdate -> {out_path} ({_human_size(out_path)})", "ok")
    return out_path


def step_verify_bundle(*, onedir: bool, skip: bool = False) -> None:
    if skip:
        _log("Omitiendo smoke test del bundle (--skip-bundle-verify).", "warn")
        return
    if sys.platform != "win32":
        _log("Smoke test desktop solo en Windows — omitiendo.", "warn")
        return
    script = ROOT / "tools" / "verify_desktop_bundle.py"
    if not script.exists():
        _log("verify_desktop_bundle.py no encontrado — omitiendo.", "warn")
        return
    exe = _resolve_exe_path(onedir=onedir)
    if not exe.exists():
        _log(f"No hay exe para verificar: {exe}", "err")
        sys.exit(1)
    _log("Smoke test desktop (ventana + /health)…")
    _run([_python_exe(), str(script), "--exe", str(exe)], check=True)
    _log("Smoke test desktop OK.", "ok")


def step_report(*, onedir: bool) -> None:
    exe = _resolve_exe_path(onedir=onedir)
    setup = ROOT / "dist" / "NeuroSoft-Setup.exe"
    print()
    _log("=" * 55, "ok")
    _log(f"Build completado — exe {_human_size(exe)}", "ok")
    _log(f"Ubicación: {exe}", "ok")
    if setup.exists():
        _log(f"Instalador: {setup} ({_human_size(setup)})", "ok")
    _log("=" * 55, "ok")
    print()
    _log("Datos de usuario: %APPDATA%/NeuroSoft", "info")
    _log("Actualizaciones: dist/update.json + .nsupdate", "info")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build NeuroSoft desktop")
    parser.add_argument("--skip-frontend", action="store_true")
    parser.add_argument("--clean", action="store_true")
    parser.add_argument("--skip-ollama", action="store_true")
    parser.add_argument("--skip-shards", action="store_true")
    parser.add_argument("--skip-manual", action="store_true")
    parser.add_argument("--skip-inno", action="store_true")
    parser.add_argument("--skip-manifest", action="store_true", help="No genera update.json")
    parser.add_argument("--legacy-onefile", action="store_true", help="Usa neurosoft.spec (onefile)")
    parser.add_argument("--spec", default=None, help="Archivo .spec personalizado")
    parser.add_argument("--make-update", action="store_true")
    parser.add_argument(
        "--skip-bundle-verify",
        action="store_true",
        help="No ejecuta tools/verify_desktop_bundle.py tras PyInstaller",
    )
    args = parser.parse_args()

    onedir = not args.legacy_onefile
    spec = args.spec or (LEGACY_SPEC if args.legacy_onefile else DEFAULT_SPEC)

    t0 = time.time()
    step_check_tools()
    if args.clean:
        step_clean()
    step_build_frontend(skip=args.skip_frontend)
    step_py_compile_backend()

    if args.make_update:
        out = step_make_update()
        if not args.skip_manifest:
            step_update_manifest(onedir=onedir, nsupdate=out)
        _log(f"Tiempo total: {time.time() - t0:.1f}s", "info")
        return 0

    if not args.skip_shards:
        step_baremos_shards()

    step_pyinstaller(spec=spec, onedir=onedir)
    step_verify_bundle(onedir=onedir, skip=args.skip_bundle_verify)

    nsupdate = step_make_update()

    if onedir:
        step_package_onedir_zip(_read_version())

    if not args.skip_manifest:
        step_update_manifest(onedir=onedir, nsupdate=nsupdate)

    step_download_ollama(skip=args.skip_ollama)

    if not args.skip_manual:
        step_manual_pdf()
    if not args.skip_inno:
        # Evita que Inno Setup elija el onefile legacy si coexisten ambos artefactos
        legacy_onefile = ROOT / "dist" / "NeuroSoft.exe"
        onedir_exe = ROOT / "dist" / "NeuroSoft" / "NeuroSoft.exe"
        if onedir_exe.exists() and legacy_onefile.exists():
            _log(f"Eliminando onefile legacy obsoleto -> {legacy_onefile.name}", "warn")
            legacy_onefile.unlink(missing_ok=True)
        step_inno_setup(include_ollama=not args.skip_ollama)

    step_report(onedir=onedir)
    _log(f"Tiempo total: {time.time() - t0:.1f}s", "info")
    return 0


if __name__ == "__main__":
    sys.exit(main())
