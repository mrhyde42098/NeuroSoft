"""Lógica compartida de generación de licencias NeuroSoft (sin GUI)."""
from __future__ import annotations

import hashlib
import json
import os
import secrets
from datetime import datetime, timezone
from pathlib import Path

PRODUCT_ID = "NSFT"

TYPE_META = {
    "perpetual": {
        "label": "Perpetua",
        "desc": "Cliente pagador · sin vencimiento · sin marca de agua en PDF",
        "watermark": False,
        "days_default": 0,
    },
    "trial": {
        "label": "Prueba",
        "desc": "Demo temporal · marca de agua · expira automáticamente",
        "watermark": True,
        "days_default": 14,
    },
    "beta": {
        "label": "Beta tester",
        "desc": "Evaluación pre-lanzamiento · marca de agua · sin expiración en clave",
        "watermark": True,
        "days_default": 0,
    },
    "master": {
        "label": "Master (admin)",
        "desc": "Solo titular del software · acceso total · NO distribuir",
        "watermark": False,
        "days_default": 0,
    },
}


def history_path() -> Path:
    base = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft" / "LicenseAdmin"
    base.mkdir(parents=True, exist_ok=True)
    return base / "license_history.json"


def load_history() -> list[dict]:
    p = history_path()
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    # migrar historial legacy en raíz del repo
    legacy = Path(__file__).resolve().parent.parent / "license_history.json"
    if legacy.exists():
        with open(legacy, encoding="utf-8") as f:
            data = json.load(f)
        save_history_entries(data)
        return data
    return []


def save_history_entries(entries: list[dict]) -> None:
    with open(history_path(), "w", encoding="utf-8") as f:
        json.dump(entries[-1000:], f, indent=2, ensure_ascii=False)


def append_history(entry: dict) -> None:
    hist = load_history()
    hist.append(entry)
    save_history_entries(hist)


def generate_key(
    license_type: str,
    licensee: str,
    email: str,
    doc: str = "",
    days: int = 0,
    institution: str = "",
) -> str:
    type_map = {"perpetual": 0, "trial": 1, "beta": 2, "master": 3}
    now = int(datetime.now(timezone.utc).timestamp())
    identity = f"{licensee}|{email}|{doc}|{institution}".encode()
    id_hash = hashlib.sha256(identity).digest()[:8]
    payload = bytearray(32)
    payload[0] = 1
    payload[1] = type_map.get(license_type, 0)
    payload[2:6] = now.to_bytes(4, "big")
    payload[6:8] = days.to_bytes(2, "big")
    payload[8:16] = id_hash
    payload[16:] = secrets.token_bytes(16)
    hex_str = payload.hex().upper()
    blocks = [hex_str[i : i + 4] for i in range(0, 32, 4)]
    return f"{PRODUCT_ID}-{'-'.join(blocks[:8])}"


def email_template(entry: dict) -> str:
    meta = TYPE_META.get(entry.get("type", "beta"), TYPE_META["beta"])
    return f"""Hola {entry.get('name', '')},

Gracias por participar en la beta de NeuroSoft.

Tu clave de activación ({meta['label']}):
{entry.get('key', '')}

Pasos:
1. Instala NeuroSoft-Setup.exe (elige carpeta de instalación).
2. Al abrir, ingresa la clave cuando se solicite.
3. Acepta el acuerdo de uso (solo la primera vez en ese equipo).
4. Inicia sesión con las credenciales que te enviamos por separado.

Institución registrada: {entry.get('institution') or '—'}
{"Duración: " + str(entry.get('days')) + " días" if entry.get('days') else "Sin fecha de vencimiento en clave"}

Cualquier duda, responde a este correo.

— Equipo NeuroSoft
"""
