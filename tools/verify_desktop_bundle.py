#!/usr/bin/env python3
"""
Smoke test del bundle desktop NeuroSoft (post-PyInstaller).

Comprueba artefactos embebidos y que el .exe arranca ventana + backend /health.
Pensado para ejecutarse al final de build.py en Windows (falla el build si no pasa).

Uso:
    python tools/verify_desktop_bundle.py
    python tools/verify_desktop_bundle.py --exe dist/NeuroSoft/NeuroSoft.exe
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_EXE = ROOT / "dist" / "NeuroSoft" / "NeuroSoft.exe"

# Módulos críticos para pywebview en Windows (regresión pythonnet/winforms).
REQUIRED_INTERNAL_DIRS = (
    "pythonnet",
    "clr_loader",
    "webview",
    "static",
    "app",
)

STARTUP_TIMEOUT_S = 45
HEALTH_HOST = "127.0.0.1"


def _log(msg: str, *, err: bool = False) -> None:
    stream = sys.stderr if err else sys.stdout
    prefix = "ERROR" if err else "OK"
    print(f"[verify_bundle] {prefix}: {msg}", file=stream, flush=True)


def _startup_log() -> Path:
    appdata = os.environ.get("APPDATA")
    base = Path(appdata) if appdata else Path.home()
    return base / "NeuroSoft" / "startup.log"


def check_bundle_layout(exe: Path) -> list[str]:
    errors: list[str] = []
    if not exe.is_file():
        return [f"No existe el ejecutable: {exe}"]

    internal = exe.parent / "_internal"
    if not internal.is_dir():
        errors.append(f"Falta carpeta onedir: {internal}")
        return errors

    for name in REQUIRED_INTERNAL_DIRS:
        path = internal / name
        if not path.exists():
            errors.append(f"Falta en bundle: _internal/{name}")

    index = internal / "static" / "index.html"
    if not index.is_file():
        errors.append("Falta frontend embebido: _internal/static/index.html")

    main_py = internal / "app" / "main.py"
    if not main_py.is_file():
        errors.append("Falta backend embebido: _internal/app/main.py")

    return errors


def _read_startup_tail(path: Path, max_bytes: int = 16_000) -> str:
    if not path.is_file():
        return ""
    try:
        data = path.read_bytes()
        if len(data) > max_bytes:
            data = data[-max_bytes:]
        return data.decode("utf-8", errors="replace")
    except OSError:
        return ""


def _pick_port_from_log(text: str) -> int | None:
    for line in reversed(text.splitlines()):
        if "puerto elegido:" in line:
            try:
                return int(line.rsplit(":", 1)[-1].strip())
            except ValueError:
                return None
    return None


def _health_ok(port: int) -> bool:
    url = f"http://{HEALTH_HOST}:{port}/health"
    try:
        with urllib.request.urlopen(url, timeout=3) as resp:
            return resp.status == 200
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def check_runtime_launch(exe: Path) -> list[str]:
    if sys.platform != "win32":
        _log("Smoke launch solo en Windows — omitiendo arranque real", err=False)
        return []

    errors: list[str] = []
    log_path = _startup_log()
    marker = time.strftime("%Y-%m-%dT%H:%M")

    # Cerrar instancias previas que bloqueen puertos o el log.
    subprocess.run(
        [
            "powershell",
            "-NoProfile",
            "-Command",
            "Stop-Process -Name NeuroSoft -Force -ErrorAction SilentlyContinue",
        ],
        check=False,
        capture_output=True,
    )
    time.sleep(1)

    proc = subprocess.Popen(
        [str(exe)],
        cwd=str(exe.parent),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    deadline = time.time() + STARTUP_TIMEOUT_S
    log_text = ""
    port: int | None = None

    try:
        while time.time() < deadline:
            if proc.poll() is not None and proc.returncode not in (None, 0):
                log_text = _read_startup_tail(log_path)
                errors.append(
                    f"NeuroSoft.exe terminó con código {proc.returncode} antes de abrir ventana"
                )
                break

            log_text = _read_startup_tail(log_path)
            if "ERROR en webview.start()" in log_text or "EXCEPCIÓN no capturada" in log_text:
                errors.append("startup.log reporta fallo al abrir pywebview (revisar pythonnet/winforms)")
                break

            if "Paso 7: webview.start()" in log_text:
                port = _pick_port_from_log(log_text) or 8765
                if _health_ok(port):
                    _log(f"/health OK en :{port}")
                    time.sleep(2)
                    if proc.poll() is None:
                        _log("Proceso NeuroSoft activo tras abrir ventana")
                        return errors
                    errors.append("El proceso se cerró justo después de arrancar")
                    break

            time.sleep(0.5)

        if not errors and "Paso 7: webview.start()" not in log_text:
            errors.append(
                f"Timeout {STARTUP_TIMEOUT_S}s: no llegó a webview.start() — ver {log_path}"
            )
    finally:
        if proc.poll() is None:
            proc.terminate()
            try:
                proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                proc.kill()

    if errors and log_path.is_file():
        tail = "\n".join(log_text.splitlines()[-8:])
        _log(f"Últimas líneas de startup.log:\n{tail}", err=True)

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke test bundle NeuroSoft desktop")
    parser.add_argument("--exe", type=Path, default=DEFAULT_EXE)
    parser.add_argument("--skip-launch", action="store_true", help="Solo revisar archivos embebidos")
    args = parser.parse_args()

    exe = args.exe.resolve()
    all_errors: list[str] = []

    all_errors.extend(check_bundle_layout(exe))
    if all_errors:
        for e in all_errors:
            _log(e, err=True)
        return 1

    _log(f"Layout del bundle OK ({exe.parent / '_internal'})")

    if not args.skip_launch:
        launch_errors = check_runtime_launch(exe)
        all_errors.extend(launch_errors)

    if all_errors:
        for e in all_errors:
            _log(e, err=True)
        return 1

    _log("Smoke test desktop PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
