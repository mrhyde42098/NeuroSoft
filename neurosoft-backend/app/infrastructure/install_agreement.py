"""
Acuerdo de uso — una sola aceptación por equipo (machine_id).
Persistido en %APPDATA%/NeuroSoft/install_agreement.json (offline).
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime
from pathlib import Path

from app.infrastructure.license_manager import _LICENSE_DIR, _machine_id

logger = logging.getLogger("neurosoft.install_agreement")

CURRENT_VERSION = "2.0.0"
_AGREEMENT_FILE = "install_agreement.json"


def _path() -> Path:
    _LICENSE_DIR.mkdir(parents=True, exist_ok=True)
    return _LICENSE_DIR / _AGREEMENT_FILE


def get_agreement_status() -> dict:
    path = _path()
    if not path.exists():
        return {
            "accepted": False,
            "version": None,
            "accepted_at": None,
            "current_version": CURRENT_VERSION,
            "machine_id": _machine_id()[:12] + "...",
        }
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        accepted = (
            data.get("version") == CURRENT_VERSION
            and data.get("machine_id") == _machine_id()
            and bool(data.get("accepted_at"))
        )
        return {
            "accepted": accepted,
            "version": data.get("version"),
            "accepted_at": data.get("accepted_at"),
            "current_version": CURRENT_VERSION,
            "machine_id": _machine_id()[:12] + "...",
        }
    except Exception:
        return {
            "accepted": False,
            "version": None,
            "accepted_at": None,
            "current_version": CURRENT_VERSION,
            "machine_id": _machine_id()[:12] + "...",
        }


def accept_agreement(
    *,
    user_id: str | None = None,
    user_name: str | None = None,
    documento: str | None = None,
    tarjeta_profesional: str | None = None,
) -> dict:
    payload = {
        "version": CURRENT_VERSION,
        "machine_id": _machine_id(),
        "accepted_at": datetime.now(UTC).isoformat(),
        "user_id": user_id,
        "user_name": user_name,
        "documento": documento,
        "tarjeta_profesional": tarjeta_profesional,
    }
    _path().write_text(json.dumps(payload, indent=2), encoding="utf-8")
    logger.info("Acuerdo de uso %s aceptado en equipo %s", CURRENT_VERSION, _machine_id()[:8])
    return get_agreement_status()
