#!/usr/bin/env python3
"""
Genera dist/update.json firmado para el sistema de auto-actualización desktop.

Uso:
    python tools/generate_update_manifest.py
    python tools/generate_update_manifest.py --exe dist/NeuroSoft/NeuroSoft.exe
    python tools/generate_update_manifest.py --nsupdate dist/neurosoft-v2.0.0.nsupdate

Requiere NEUROSOFT_UPDATE_HMAC_KEY en el entorno (o deriva de SECRET_KEY en dev).
"""
from __future__ import annotations

import argparse
import hashlib
import hmac
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "neurosoft-backend"
sys.path.insert(0, str(BACKEND))


def _read_version() -> str:
    config_py = BACKEND / "app" / "core" / "config.py"
    if config_py.exists():
        m = re.search(r'api_version\s*[=:]\s*"([^"]+)"', config_py.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return "0.0.0"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _hmac_key() -> str:
    import os

    explicit = os.getenv("NEUROSOFT_UPDATE_HMAC_KEY", "").strip()
    if explicit:
        return explicit
    from app.infrastructure.auth.auth_service import SECRET_KEY

    return hashlib.sha256(("nsupdate-hmac::" + SECRET_KEY).encode("utf-8")).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description="Genera update.json firmado")
    parser.add_argument("--version", default=None)
    parser.add_argument("--exe", type=Path, default=None, help="Ruta al NeuroSoft.exe")
    parser.add_argument("--nsupdate", type=Path, default=None)
    parser.add_argument("--dir-zip", type=Path, default=None, help="ZIP onedir completo")
    parser.add_argument("--exe-url", default=None)
    parser.add_argument("--dir-zip-url", default=None)
    parser.add_argument("--nsupdate-url", default=None)
    parser.add_argument("-o", "--output", type=Path, default=ROOT / "dist" / "update.json")
    args = parser.parse_args()

    version = args.version or _read_version()
    artifacts: dict = {}

    exe_candidates = [
        args.exe,
        ROOT / "dist" / "NeuroSoft" / "NeuroSoft.exe",
        ROOT / "dist" / "NeuroSoft.exe",
    ]
    for cand in exe_candidates:
        if cand and cand.is_file():
            artifacts["windows_x64_exe"] = {
                "filename": "NeuroSoft.exe",
                "sha256": _sha256(cand),
                "size_bytes": cand.stat().st_size,
                "url": args.exe_url,
            }
            break

    zip_candidates = [
        args.dir_zip,
        ROOT / "dist" / f"NeuroSoft-v{version}-win64.zip",
    ]
    for cand in zip_candidates:
        if cand and cand.is_file():
            artifacts["windows_x64_dir_zip"] = {
                "filename": cand.name,
                "sha256": _sha256(cand),
                "size_bytes": cand.stat().st_size,
                "url": args.dir_zip_url,
            }
            break

    ns_candidates = [
        args.nsupdate,
        ROOT / "dist" / f"neurosoft-v{version}.nsupdate",
    ]
    for cand in ns_candidates:
        if cand and cand.is_file():
            artifacts["frontend_nsupdate"] = {
                "filename": cand.name,
                "sha256": _sha256(cand),
                "size_bytes": cand.stat().st_size,
                "url": args.nsupdate_url,
            }
            break

    manifest = {
        "version": version,
        "released": __import__("datetime").date.today().isoformat(),
        "channel": "stable",
        "artifacts": artifacts,
    }
    body = json.dumps(manifest, sort_keys=True, separators=(",", ":")).encode("utf-8")
    manifest["signature"] = hmac.new(_hmac_key().encode("utf-8"), body, hashlib.sha256).hexdigest()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"OK -> {args.output}  (v{version}, {len(artifacts)} artifacts)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
