"""
Servicio autoritativo de mapeo CIE-10 → CIE-11 (backend).

El frontend mantiene cie11Map.js como caché; este módulo es la fuente
de verdad para persistencia, informes y futura transición RIPS.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

_DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "cie10_to_cie11.json"


@lru_cache(maxsize=1)
def _load_mapping() -> dict[str, dict[str, str]]:
    if not _DATA_PATH.exists():
        logger.warning("cie10_to_cie11.json no encontrado en %s", _DATA_PATH)
        return {}
    with open(_DATA_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return {k.upper().replace(".", ""): v for k, v in raw.items() if not k.startswith("_") and isinstance(v, dict)}


def map_cie10_to_cie11(codigo10: str | None) -> dict[str, str] | None:
    """
    Mapea un código CIE-10 a su equivalente CIE-11.

    Returns:
        {"cie11": "6A70", "nombre11": "..."} o None si no hay mapeo.
    """
    if not codigo10:
        return None
    table = _load_mapping()
    key = str(codigo10).strip().upper().replace(".", "")
    direct = table.get(key)
    if direct:
        return {"cie11": direct["cie11"], "nombre11": direct.get("nombre11", "")}
    base = key[:3] if len(key) >= 3 else key
    fallback = table.get(base)
    if fallback:
        return {"cie11": fallback["cie11"], "nombre11": fallback.get("nombre11", "")}
    return None


def resolve_cie11_code(codigo10: str | None) -> str | None:
    """Retorna solo el código CIE-11 o None."""
    mapped = map_cie10_to_cie11(codigo10)
    return mapped["cie11"] if mapped else None


def list_all_mappings() -> list[dict[str, Any]]:
    """Lista completa para inspección / sincronización."""
    table = _load_mapping()
    return [{"codigo10": k, **v} for k, v in sorted(table.items())]
