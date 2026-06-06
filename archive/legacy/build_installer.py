"""
Build beta installer for NeuroSoft.

Normal flow:
    python build_installer.py

Useful fast flow after `python build.py --skip-ollama`:
    python build_installer.py --skip-app-build

If Inno Setup is installed, this creates:
    dist/NeuroSoft_Beta_Setup.exe

If Inno Setup is missing, it creates a portable fallback:
    dist/NeuroSoft_Beta_Portable.zip
"""
from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DIST = ROOT / "dist"
EXE = DIST / "NeuroSoft.exe"
ISS = ROOT / "installer" / "NeuroSoftInstaller.iss"
SETUP = DIST / "NeuroSoft_Beta_Setup.exe"
PORTABLE_ZIP = DIST / "NeuroSoft_Beta_Portable.zip"


def log(message: str) -> None:
    print(f"[installer] {message}", flush=True)


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    log("$ " + " ".join(cmd))
    result = subprocess.run(cmd, cwd=str(cwd))
    if result.returncode != 0:
        raise SystemExit(result.returncode)


def find_iscc() -> str | None:
    found = shutil.which("ISCC.exe") or shutil.which("ISCC")
    if found:
        return found
    candidates = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def install_inno_with_winget() -> None:
    winget = shutil.which("winget")
    if not winget:
        raise SystemExit("winget no esta disponible. Instale Inno Setup 6 manualmente.")
    run([
        winget,
        "install",
        "--id",
        "JRSoftware.InnoSetup",
        "--exact",
        "--silent",
        "--accept-package-agreements",
        "--accept-source-agreements",
    ])


def build_app(skip: bool) -> None:
    if skip:
        log("Omitiendo build PyInstaller (--skip-app-build).")
    else:
        run([sys.executable, "build.py", "--skip-ollama"])
    if not EXE.exists():
        raise SystemExit(f"No existe {EXE}. Ejecute primero python build.py --skip-ollama.")


def build_portable_zip() -> None:
    DIST.mkdir(exist_ok=True)
    if PORTABLE_ZIP.exists():
        PORTABLE_ZIP.unlink()
    files = [
        EXE,
        ROOT / "GUIA_RAPIDA_BETA.md",
        ROOT / "INSTRUCCIONES_BETA_TESTER.md",
        ROOT / "README.md",
    ]
    with zipfile.ZipFile(PORTABLE_ZIP, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for file in files:
            if file.exists():
                zf.write(file, file.name)
    log(f"ZIP portable generado: {PORTABLE_ZIP}")


def compile_inno(iscc: str) -> None:
    if SETUP.exists():
        SETUP.unlink()
    run([iscc, str(ISS)])
    if not SETUP.exists():
        raise SystemExit("Inno Setup termino sin generar NeuroSoft_Beta_Setup.exe.")
    log(f"Instalador generado: {SETUP}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build NeuroSoft beta installer")
    parser.add_argument("--skip-app-build", action="store_true")
    parser.add_argument("--install-inno", action="store_true",
                        help="Instala Inno Setup 6 via winget si no esta disponible.")
    args = parser.parse_args()

    build_app(skip=args.skip_app_build)

    iscc = find_iscc()
    if not iscc and args.install_inno:
        install_inno_with_winget()
        iscc = find_iscc()

    if iscc:
        compile_inno(iscc)
    else:
        build_portable_zip()
        log("Para generar instalador real instale Inno Setup 6 y re-ejecute:")
        log("  winget install --id JRSoftware.InnoSetup --exact")
        log("  python build_installer.py --skip-app-build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
