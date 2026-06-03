"""
app/domain/clinical_engine/baremos_overlays.py
================================================
Sprint 9 — Sistema de baremos múltiples (overlays).

El motor de scoring sigue usando `BD_NEURO_MAESTRA.json` como fuente
primaria. Esta utilidad detecta y registra (sin aplicar) baremos
adicionales en `data/baremos/*.json` para que:

  • `/api/v1/baremos/info` los reporte en la metadata.
  • El frontend muestre al clínico qué fuentes están disponibles.
  • Una iteración futura permita `POST /scores/` con `fuente_baremo=…`.

La filosofía es **conservadora**: no romper el motor de scoring actual,
sólo enriquecer la observabilidad.
"""
from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def discover_overlays(baremos_dir: Path) -> list[dict[str, Any]]:
    """
    Escanea `data/baremos/*.json` y devuelve metadata de cada archivo.

    Cada entrada del listado tiene:
        {
          "fuente_id": "neuronorma_colombia",
          "fuente_nombre": "Neuronorma Colombia",
          "path": "data/baremos/neuronorma_colombia.json",
          "checksum_sha256": "...",
          "pruebas": ["FCSRT", "TowerOfLondon", ...],
          "total_pruebas": 12,
          "valid": true,
          "error": null
        }

    NO carga las pruebas al singleton del scoring engine — sólo enumera.
    """
    if not baremos_dir.exists() or not baremos_dir.is_dir():
        return []

    overlays = []
    for fp in sorted(baremos_dir.glob("*.json")):
        entry: dict[str, Any] = {
            "fuente_id": fp.stem,
            "fuente_nombre": fp.stem.replace("_", " ").title(),
            "path": str(fp.relative_to(baremos_dir.parent.parent))
                    if baremos_dir.parent.parent in fp.parents
                    else str(fp),
            "checksum_sha256": None,
            "pruebas": [],
            "total_pruebas": 0,
            "valid": False,
            "error": None,
            "meta": {},
        }
        try:
            raw_bytes = fp.read_bytes()
            entry["checksum_sha256"] = hashlib.sha256(raw_bytes).hexdigest()
            raw = json.loads(raw_bytes.decode("utf-8"))
            meta = raw.get("_meta", {}) or {}
            entry["fuente_id"] = meta.get("fuente_id", entry["fuente_id"])
            entry["fuente_nombre"] = meta.get("fuente_nombre", entry["fuente_nombre"])
            entry["meta"] = {
                k: v for k, v in meta.items()
                if k not in ("baterias",)
            }
            baterias = raw.get("baterias", {}) or {}
            pruebas: list[str] = []
            for grupo_pruebas in baterias.values():
                if isinstance(grupo_pruebas, dict):
                    pruebas.extend(grupo_pruebas.keys())
            entry["pruebas"] = sorted(set(pruebas))
            entry["total_pruebas"] = len(entry["pruebas"])
            entry["valid"] = True
        except json.JSONDecodeError as e:
            entry["error"] = f"JSON inválido: {e}"
        except Exception as e:
            entry["error"] = f"Error de lectura: {e}"
        overlays.append(entry)
    return overlays


def get_overlays_for_settings() -> list[dict[str, Any]]:
    """Helper: descubre overlays usando la ruta convencional
    `<baremo_path>.parent/baremos/`."""
    try:
        from app.core.config import settings
        baremo_path = Path(settings.baremo_path)
        overlays_dir = baremo_path.parent / "baremos"
        return discover_overlays(overlays_dir)
    except Exception as e:
        logger.warning("No se pudo descubrir overlays: %s", e)
        return []
