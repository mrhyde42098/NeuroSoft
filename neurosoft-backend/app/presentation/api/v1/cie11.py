"""
Endpoints CIE-11 — mapeo dual CIE-10/CIE-11 (backend autoritativo).
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query

from app.domain.clinical_engine.cie_mapping_service import (
    list_all_mappings,
    map_cie10_to_cie11,
)

cie11_router = APIRouter(prefix="/cie11", tags=["CIE-11"])


@cie11_router.get(
    "/map",
    summary="Mapear código CIE-10 a CIE-11",
    description="Retorna el equivalente CIE-11 para un código CIE-10 conocido.",
)
def map_cie11(codigo10: str = Query(..., min_length=1, description="Código CIE-10")) -> dict[str, Any]:
    mapped = map_cie10_to_cie11(codigo10)
    if not mapped:
        raise HTTPException(
            status_code=404,
            detail=f"Sin mapeo CIE-11 para código '{codigo10}'",
        )
    return {"codigo10": codigo10.strip().upper(), **mapped}


@cie11_router.get(
    "/",
    summary="Tabla completa de mapeos CIE-10 → CIE-11",
)
def list_cie11_mappings() -> list[dict[str, Any]]:
    return list_all_mappings()
