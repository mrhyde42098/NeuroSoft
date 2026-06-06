"""
app/domain/clinical_engine/overrides/adbeck.py
===============================================
Override Python para AdBeck (BDI-II — Beck Depression Inventory-II).

FUENTE
------
Beck, A. T., Steer, R. A., & Brown, G. K. (1996). Manual for the Beck
Depression Inventory-II. San Antonio, TX: Psychological Corporation.

PUNTUACIÓN BDI-II (21 ítems, cada uno 0-3)
-------------------------------------------
- 0–13  → Mínima
- 14–19 → Leve
- 20–28 → Moderada
- 29–63 → Severa

Punto de corte clínico: ≥ 14 (Beck 1996, cap. 4).
Consistente con APA Handbook of Psychological Disorders (2023) y con
el sistema de clasificación estándar en Colombia (uso clínico
consolidado en la práctica psicológica colombiana).

PROBLEMA EN BD
--------------
Las 6 keys `16190..16195` en `BD_NEURO_MAESTRA.json` no son
clasificaciones clínicas: son Cell IDs del Excel original
(`SistemaHC_Prac Johan_Sebastian_Salgado.xlsm`). El motor las lee y
devuelve valores inválidos.

SOLUCIÓN
--------
Este override expone el baremo BDI-II correcto SIN modificar el JSON.
El `BaremosLoader` consulta este override antes de devolver `get_prueba("AdBeck")`.

ESTRUCTURA
----------
`tipo_calculo: "clasificacion_fija"` con `baremos: {Rango: [...], "0": ..., "14": ..., ...}`
Siguiendo el patrón del resto de clasificaciones_fijas del motor
(p.ej. EscKertesz, EscYesavage), las keys son los **puntos de corte
inferiores** de cada banda. El strategy ya sabe cómo buscar la
banda que contiene el puntaje.
"""

from __future__ import annotations

from typing import Any

# Tabla BDI-II (Beck, Steer & Brown, 1996, Manual cap. 4)
# Cada key es el límite INFERIOR (inclusivo) de la banda.
_BDI_II_BANDAS: dict[str, str] = {
    "0": "Mínima",
    "14": "Leve",
    "20": "Moderada",
    "29": "Severa",
}

# Rango: par (mínimo, máximo) de la suma posible. 21 ítems × 0-3 = 0-63.
_BDI_II_RANGO: list = [0, 63]

# Punto de corte clínico (Beck 1996): ≥ 14 indica presencia de
# sintomatología depresiva que requiere evaluación profesional.
_BDI_II_CORTE_CLINICO: int = 14

# Fuente bibliográfica
_BDI_II_FUENTE: str = "Beck, Steer & Brown (1996). BDI-II Manual. Psychological Corporation."


def get_adbeck_override() -> dict[str, Any]:
    """
    Retorna el dict `baremos` correcto para AdBeck (BDI-II).

    Shape:
        {
            "Rango": [0, 63],
            "0":    "Mínima",
            "14":   "Leve",
            "20":   "Moderada",
            "29":   "Severa",
        }
    """
    return {
        "Rango": _BDI_II_RANGO,
        **_BDI_II_BANDAS,
    }


def get_adbeck_metadata() -> dict[str, Any]:
    """
    Metadata clínico-administrativa de la override AdBeck.

    Útil para que el motor / informes / UI reporten:
        - Punto de corte clínico
        - Fuente bibliográfica
        - Versión del override
        - Fecha de aplicación
    """
    return {
        "fuente": _BDI_II_FUENTE,
        "corte_clinico": _BDI_II_CORTE_CLINICO,
        "rango_puntaje": _BDI_II_RANGO,
        "bandas": _BDI_II_BANDAS,
        "override_version": "1.0.0",
        "aplicado_en": "2026-06-03",
    }


__all__ = ["get_adbeck_override", "get_adbeck_metadata"]
