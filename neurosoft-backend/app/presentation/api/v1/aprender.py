"""
app/presentation/api/v1/aprender.py
===================================
Metadata del Centro de Aprendizaje — manifest + rutas guiadas.

Permite actualizar conteos y rutas sin rebuild del frontend (solo JSON en data/aprender/).

Rutas:
  GET /api/v1/aprender/stats  → manifest (conteos, versión)
  GET /api/v1/aprender/paths  → rutas de estudio guiadas
"""

from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter

logger = logging.getLogger(__name__)

aprender_router = APIRouter(prefix="/aprender", tags=["Centro de Aprendizaje"])

_PROJECT_DATA = Path(__file__).resolve().parents[4] / "data" / "aprender"
_APRENDER_DIR = Path(os.getenv("NEUROSOFT_APRENDER_DIR", str(_PROJECT_DATA)))


@lru_cache(maxsize=8)
def _load_json(name: str) -> dict[str, Any] | list[Any]:
    path = _APRENDER_DIR / name
    if not path.exists():
        logger.warning("Aprender: %s no encontrado en %s", name, path)
        return {} if name == "manifest.json" else []
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        logger.error("Aprender: error cargando %s: %s", name, e)
        return {} if name == "manifest.json" else []


def _invalidate_cache() -> None:
    _load_json.cache_clear()


@aprender_router.get("/stats", summary="Metadata del Centro de Aprendizaje")
def get_stats() -> dict[str, Any]:
    manifest = _load_json("manifest.json")
    if not isinstance(manifest, dict):
        manifest = {}
    from app.core.config import settings

    out = {
        "version": manifest.get("version", "unknown"),
        "updated_at": manifest.get("updated_at"),
        "glosario_count": manifest.get("glosario_count", 0),
        "tarjetas_count": manifest.get("tarjetas_count", 0),
        "quizzes_count": manifest.get("quizzes_count", 0),
        "articulos_count": manifest.get("articulos_count", 0),
        "simulador_count": manifest.get("simulador_count", 0),
        "protocolos_count": manifest.get("protocolos_count", 0),
        "paths_count": manifest.get("paths_count", 0),
    }
    if settings.env != "production":
        out["path"] = str(_APRENDER_DIR)
    return out


@aprender_router.get("/paths", summary="Rutas de estudio guiadas")
def get_paths() -> dict[str, Any]:
    paths = _load_json("paths.json")
    if not isinstance(paths, list):
        paths = []
    manifest = _load_json("manifest.json")
    version = manifest.get("version", "unknown") if isinstance(manifest, dict) else "unknown"
    return {"version": version, "paths": paths, "total": len(paths)}
