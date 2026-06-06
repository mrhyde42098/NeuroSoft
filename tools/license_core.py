"""Lógica compartida de generación e inventario de licencias NeuroSoft."""
from __future__ import annotations

import csv
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

DEFAULT_EMAIL_TEMPLATE = """Hola {name},

Gracias por participar en la beta de NeuroSoft.

Tu clave de activación ({type_label}):
{key}

Pasos:
1. Instala NeuroSoft-Setup.exe (elige carpeta de instalación).
2. Al abrir, ingresa la clave cuando se solicite.
3. Acepta el acuerdo de uso (solo la primera vez en ese equipo).
4. Inicia sesión con las credenciales que te enviamos por separado.

Institución: {institution}
{days_line}

{notes_line}

Cualquier duda, responde a este correo.

— {sender}
"""

DEFAULT_SETTINGS = {
    "default_institution": "",
    "default_prefix": "BETA2026",
    "default_sender": "Equipo NeuroSoft",
    "default_batch_size": 50,
    "email_template": DEFAULT_EMAIL_TEMPLATE,
}


def _admin_dir() -> Path:
    base = Path(os.getenv("APPDATA", Path.home())) / "NeuroSoft" / "LicenseAdmin"
    base.mkdir(parents=True, exist_ok=True)
    return base


def history_path() -> Path:
    return _admin_dir() / "license_history.json"


def inventory_path() -> Path:
    return _admin_dir() / "license_inventory.json"


def settings_path() -> Path:
    return _admin_dir() / "license_settings.json"


def _load_json(path: Path, default: dict | list) -> dict | list:
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return default


def _save_json(path: Path, data: dict | list) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_settings() -> dict:
    data = _load_json(settings_path(), DEFAULT_SETTINGS.copy())
    if isinstance(data, dict):
        merged = {**DEFAULT_SETTINGS, **data}
        return merged
    return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    _save_json(settings_path(), settings)


def load_history() -> list[dict]:
    p = history_path()
    data = _load_json(p, [])
    if isinstance(data, list):
        return data
    legacy = Path(__file__).resolve().parent.parent / "license_history.json"
    if legacy.exists():
        with open(legacy, encoding="utf-8") as f:
            hist = json.load(f)
        save_history_entries(hist)
        return hist
    return []


def save_history_entries(entries: list[dict]) -> None:
    _save_json(history_path(), entries[-2000:])


def append_history(entry: dict) -> None:
    hist = load_history()
    hist.append(entry)
    save_history_entries(hist)


def load_inventory() -> dict:
    data = _load_json(inventory_path(), {"version": 1, "keys": []})
    if not isinstance(data, dict):
        return {"version": 1, "keys": []}
    data.setdefault("keys", [])
    return data


def save_inventory(inv: dict) -> None:
    _save_json(inventory_path(), inv)


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def inventory_register(entry: dict, *, status: str = "available") -> None:
    """Registra o actualiza una clave en el inventario."""
    inv = load_inventory()
    keys = inv.setdefault("keys", [])
    key = entry.get("key", "")
    existing = next((k for k in keys if k.get("key") == key), None)
    row = {
        "key": key,
        "type": entry.get("type", "beta"),
        "name": entry.get("name", ""),
        "email": entry.get("email", ""),
        "institution": entry.get("institution", ""),
        "days": entry.get("days"),
        "batch": entry.get("batch", ""),
        "notes": entry.get("notes", ""),
        "status": status,
        "created": entry.get("date") or _now_str(),
        "assigned_date": entry.get("assigned_date"),
        "assigned_to": entry.get("assigned_to", ""),
    }
    if existing:
        existing.update({k: v for k, v in row.items() if v not in (None, "") or k == "status"})
    else:
        keys.append(row)
    save_inventory(inv)


def inventory_mark(key: str, status: str, assigned_to: str = "") -> bool:
    inv = load_inventory()
    for row in inv.get("keys", []):
        if row.get("key") == key:
            row["status"] = status
            if status == "assigned":
                row["assigned_date"] = _now_str()
                row["assigned_to"] = assigned_to or row.get("name", "")
            elif status == "available":
                row["assigned_date"] = None
                row["assigned_to"] = ""
            save_inventory(inv)
            return True
    return False


def inventory_stats() -> dict:
    inv = load_inventory()
    keys = inv.get("keys", [])
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {"available": 0, "assigned": 0, "revoked": 0}
    batches: set[str] = set()
    for k in keys:
        t = k.get("type", "beta")
        by_type[t] = by_type.get(t, 0) + 1
        st = k.get("status", "available")
        by_status[st] = by_status.get(st, 0) + 1
        if k.get("batch"):
            batches.add(k["batch"])
    total = len(keys)
    assigned = by_status.get("assigned", 0)
    return {
        "total": total,
        "assigned": assigned,
        "available": by_status.get("available", 0),
        "revoked": by_status.get("revoked", 0),
        "batches": len(batches),
        "by_type": by_type,
        "by_status": by_status,
    }


def inventory_filter(*, status: str | None = None, batch: str | None = None, query: str = "") -> list[dict]:
    keys = load_inventory().get("keys", [])
    q = query.lower().strip()
    out = []
    for k in keys:
        if status and k.get("status") != status:
            continue
        if batch and k.get("batch") != batch:
            continue
        if q:
            blob = f"{k.get('name','')} {k.get('email','')} {k.get('key','')} {k.get('batch','')}".lower()
            if q not in blob:
                continue
        out.append(k)
    return list(reversed(out))


def inventory_batches() -> list[str]:
    batches = sorted({k.get("batch", "") for k in load_inventory().get("keys", []) if k.get("batch")})
    return batches


def import_csv_inventory(path: str | Path) -> tuple[int, int]:
    """Importa CSV existente al inventario. Retorna (nuevas, total filas)."""
    path = Path(path)
    new_count = 0
    total = 0
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            total += 1
            key = (row.get("key") or "").strip()
            if not key:
                continue
            inv = load_inventory()
            if any(k.get("key") == key for k in inv.get("keys", [])):
                continue
            entry = {
                "date": _now_str(),
                "type": row.get("type", "beta"),
                "name": row.get("name", ""),
                "email": row.get("email", ""),
                "institution": row.get("institution", ""),
                "key": key,
                "batch": row.get("batch") or path.stem,
            }
            st = (row.get("status") or "available").strip().lower()
            inventory_register(entry, status=st if st in ("available", "assigned", "revoked") else "available")
            new_count += 1
    return new_count, total


def export_inventory_csv(path: str | Path, *, status: str | None = None) -> int:
    rows = inventory_filter(status=status)
    fields = ["idx", "status", "type", "name", "email", "institution", "batch", "key", "assigned_to", "assigned_date"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        for i, r in enumerate(rows, 1):
            w.writerow({"idx": i, **r})
    return len(rows)


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


def email_template(entry: dict, settings: dict | None = None) -> str:
    settings = settings or load_settings()
    tpl = settings.get("email_template") or DEFAULT_EMAIL_TEMPLATE
    meta = TYPE_META.get(entry.get("type", "beta"), TYPE_META["beta"])
    days = entry.get("days")
    days_line = f"Duración: {days} días" if days else "Sin fecha de vencimiento en clave"
    notes = (entry.get("notes") or "").strip()
    notes_line = f"Notas: {notes}" if notes else ""
    return tpl.format(
        name=entry.get("name", ""),
        email=entry.get("email", ""),
        key=entry.get("key", ""),
        type_label=meta["label"],
        institution=entry.get("institution") or settings.get("default_institution") or "—",
        days=days or "",
        days_line=days_line,
        notes_line=notes_line,
        sender=settings.get("default_sender", "Equipo NeuroSoft"),
    )
