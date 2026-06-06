"""
Catálogo CUPS psicología / neuropsicología (subconjunto semilla).
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Query

cups_router = APIRouter(prefix="/cups", tags=["CUPS"])

_DATA_PATH = Path(__file__).resolve().parents[3] / "domain" / "data" / "cups_psicologia.json"


@lru_cache(maxsize=1)
def _load_cups() -> list[dict[str, Any]]:
    with open(_DATA_PATH, encoding="utf-8") as f:
        raw = json.load(f)
    return list(raw.get("codigos", []))


@cups_router.get(
    "/psicologia",
    summary="Códigos CUPS psicología y neuropsicología",
    description="Subconjunto semilla marcado [VERIFICAR] contra Resolución CUPS vigente.",
)
def list_cups_psicologia(
    tipo: str | None = Query(default=None, description="consulta|terapia|intervencion|neuropsicologia|rehabilitacion"),
    buscar: str | None = Query(default=None, description="Filtrar por código o nombre"),
) -> dict[str, Any]:
    items = _load_cups()
    if tipo:
        t = tipo.strip().lower()
        items = [c for c in items if str(c.get("tipo", "")).lower() == t]
    if buscar:
        b = buscar.strip().upper()
        items = [c for c in items if b in str(c.get("codigo", "")).upper() or b in str(c.get("nombre", "")).upper()]
    meta = {}
    try:
        with open(_DATA_PATH, encoding="utf-8") as f:
            meta = json.load(f).get("_meta", {})
    except OSError:
        pass
    return {"meta": meta, "total": len(items), "codigos": items}
