"""
app/presentation/api/v1/reservorio.py
======================================
Expone el banco de recomendaciones clínicas por cuadro clínico (reservorio
IN&S) para consumo del frontend, eliminando la duplicación que existía con
`datosClinicos.js::RECOMMENDATIONS_LIB`.

Single source of truth = `app/domain/data/reservorio_recomendaciones.json`
(consumido también por el PDF generator en `report_pro/narrative.py`).

Rutas:
  GET /api/v1/reservorio/info                       -> metadata (versión, fuente, total)
  GET /api/v1/reservorio/cuadros?poblacion=<grupo>  -> lista de cuadros (resumido)
  GET /api/v1/reservorio/cuadros/{grupo}/{cuadro_id}-> cuadro completo (label+recs)
  GET /api/v1/reservorio/sugerir                    -> sugerencia automática
                                                      (query: resultados_json
                                                       + poblacion)
"""
from __future__ import annotations

import json
import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter, HTTPException, Query

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reservorio", tags=["Banco de recomendaciones"])


_DEFAULT_PATH = Path(__file__).parent.parent.parent.parent / "domain" / "data" / "reservorio_recomendaciones.json"
_RESERVORIO_PATH = Path(os.getenv("NEUROSOFT_RESERVORIO_PATH", str(_DEFAULT_PATH)))


@lru_cache(maxsize=1)
def _load_reservorio() -> dict[str, Any]:
    """Carga el JSON del reservorio (cacheado)."""
    if not _RESERVORIO_PATH.exists():
        logger.warning("Reservorio no encontrado en %s", _RESERVORIO_PATH)
        return {"version": "missing", "source": "", "grupos": {}}
    try:
        with open(_RESERVORIO_PATH, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:  # noqa: BLE001
        logger.error("Error cargando reservorio: %s", e)
        return {"version": "error", "source": str(e), "grupos": {}}


def _invalidate_cache() -> None:
    """Para tests / hot-reload."""
    _load_reservorio.cache_clear()


@router.get("/info", summary="Metadata del reservorio")
def get_info() -> dict[str, Any]:
    data = _load_reservorio()
    grupos_meta = data.get("grupos", {})
    total = sum(len(g.get("cuadros", {})) for g in grupos_meta.values())
    return {
        "version": data.get("version"),
        "source": data.get("source"),
        "notes": data.get("notes", []),
        "path": str(_RESERVORIO_PATH),
        "total_cuadros": total,
        "cuadros_por_grupo": {
            grp: len(info.get("cuadros", {}))
            for grp, info in grupos_meta.items()
        },
    }


@router.get("/cuadros", summary="Lista de cuadros clínicos disponibles")
def list_cuadros(poblacion: str | None = Query(None)) -> dict[str, Any]:
    """Devuelve la lista de cuadros por grupo etario.

    Query params:
      poblacion: filtro opcional ("infantil" | "adulto" | "adulto_mayor").
                 Si no se pasa, devuelve todos los grupos.

    Cada item incluye: grupo, id, label (sin las recomendaciones completas
    para que el listado sea liviano).
    """
    data = _load_reservorio()
    grupos = data.get("grupos", {})
    out: list[dict[str, Any]] = []
    for grupo_id, grupo_info in grupos.items():
        if poblacion and poblacion != grupo_id:
            continue
        label_grupo = grupo_info.get("label", grupo_id)
        for cuadro_id, cuadro_info in grupo_info.get("cuadros", {}).items():
            out.append({
                "grupo": grupo_id,
                "grupo_label": label_grupo,
                "id": cuadro_id,
                "label": cuadro_info.get("label", cuadro_id),
                "n_recomendaciones": len(cuadro_info.get("recomendaciones", [])),
            })
    out.sort(key=lambda x: (x["grupo"], x["label"]))
    return {
        "filtro_poblacion": poblacion,
        "total": len(out),
        "cuadros": out,
    }


@router.get(
    "/cuadros/{grupo}/{cuadro_id}",
    summary="Detalle de un cuadro clínico con todas sus recomendaciones",
)
def get_cuadro(grupo: str, cuadro_id: str) -> dict[str, Any]:
    data = _load_reservorio()
    grupos = data.get("grupos", {})
    if grupo not in grupos:
        raise HTTPException(
            status_code=404,
            detail=f"Grupo '{grupo}' no existe. Disponibles: {list(grupos.keys())}",
        )
    cuadros = grupos[grupo].get("cuadros", {})
    if cuadro_id not in cuadros:
        raise HTTPException(
            status_code=404,
            detail=f"Cuadro '{cuadro_id}' no existe en '{grupo}'. "
                   f"Disponibles: {list(cuadros.keys())}",
        )
    info = cuadros[cuadro_id]
    return {
        "grupo": grupo,
        "grupo_label": grupos[grupo].get("label", grupo),
        "id": cuadro_id,
        "label": info.get("label", cuadro_id),
        "recomendaciones": info.get("recomendaciones", []),
    }


@router.get("/sugerir", summary="Sugerencia automática basada en resultados")
def sugerir_cuadros(
    resultados: str = Query(
        ..., description="JSON serializado: lista de dicts con campos "
                        "tipo_metrica, dominio_cognitivo, z_equivalente, etc.",
    ),
    poblacion: str = Query("adulto", description="infantil | adulto | adulto_mayor"),
) -> dict[str, Any]:
    """Heurística data-driven para sugerir cuadros clínicos relevantes.

    Reutiliza la misma lógica que el PDF (sugerir_cuadros_clinicos en
    report_pro.narrative) para garantizar coherencia entre el informe
    generado y las sugerencias que el clínico ve en pantalla.
    """
    try:
        resultados_list = json.loads(resultados)
        if not isinstance(resultados_list, list):
            raise ValueError("resultados debe ser una lista")
    except (json.JSONDecodeError, ValueError) as e:
        raise HTTPException(status_code=400, detail=f"resultados inválido: {e}")

    try:
        from app.infrastructure.report_pro.narrative import (
            sugerir_cuadros_clinicos,
        )
        sugerencias = sugerir_cuadros_clinicos(resultados_list, poblacion=poblacion)
    except Exception as e:  # noqa: BLE001
        logger.error("Error en sugerir_cuadros_clinicos: %s", e)
        raise HTTPException(status_code=500, detail=f"Error en sugerencia: {e}")

    # Enriquece con label + recomendaciones desde el JSON
    data = _load_reservorio()
    grupos = data.get("grupos", {})
    out: list[dict[str, Any]] = []
    for sug in sugerencias:
        sid = sug.get("cuadro_id") or sug.get("id")
        sgrupo = sug.get("grupo", poblacion)
        grupo_info = grupos.get(sgrupo, {})
        cuadro_info = grupo_info.get("cuadros", {}).get(sid, {})
        out.append({
            "id": sid,
            "grupo": sgrupo,
            "label": cuadro_info.get("label") or sug.get("label", sid),
            "relevancia": sug.get("relevancia", "media"),
            "razon": sug.get("razon", ""),
            "recomendaciones": cuadro_info.get("recomendaciones", []),
        })

    return {
        "poblacion": poblacion,
        "n_sugerencias": len(out),
        "sugerencias": out,
    }
