"""Build NeuroSoft-LicenseAdmin.exe — panel de licencias para el titular."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VENV_PY = ROOT / "neurosoft-backend" / "venv" / "Scripts" / "python.exe"
OUT = ROOT / "dist" / "NeuroSoft-LicenseAdmin.exe"


def main() -> None:
    py = str(VENV_PY if VENV_PY.exists() else sys.executable)
    cmd = [py, "-m", "PyInstaller", "--clean", "--noconfirm", str(ROOT / "license_admin.spec")]
    print("[license-admin] Building…")
    r = subprocess.run(cmd, cwd=str(ROOT))
    if r.returncode != 0:
        sys.exit(r.returncode)
    built = ROOT / "dist" / "NeuroSoft-LicenseAdmin.exe"
    if built.exists():
        mb = built.stat().st_size / (1024 * 1024)
        print(f"[license-admin] OK -> {built} ({mb:.1f} MB)")
    else:
        print("[license-admin] ERROR: exe no encontrado")
        sys.exit(1)


if __name__ == "__main__":
    main()
