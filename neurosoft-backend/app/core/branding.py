"""
app/core/branding.py
====================
Fuente única de verdad para el nombre/marca clínica mostrado al usuario
final (informes, notas, advertencias, prompts IA).

`clinical_brand()` devuelve el valor configurado en settings y se
interpola donde haga falta.

Cambiar la marca:
    export NEUROSOFT_CLINICAL_BRAND="Mi Clínica"
    export NEUROSOFT_CLINICAL_BRAND_SUBTITLE="Evaluación neuropsicológica"

Por defecto se usa "NeuroSoft" para que el software sea neutral al ser
compartido con cualquier institución.
"""

from __future__ import annotations

from functools import lru_cache


@lru_cache(maxsize=1)
def clinical_brand() -> str:
    """Nombre corto de la marca. Ej: 'NeuroSoft', 'Mi Clínica'."""
    try:
        from app.core.config import settings

        return (settings.clinical_brand or "NeuroSoft").strip()
    except Exception:
        return "NeuroSoft"


@lru_cache(maxsize=1)
def clinical_brand_subtitle() -> str:
    """Descripción corta de la marca (subtítulo/tagline)."""
    try:
        from app.core.config import settings

        return (settings.clinical_brand_subtitle or "Plataforma de evaluación neuropsicológica").strip()
    except Exception:
        return "Plataforma de evaluación neuropsicológica"


def reset_cache() -> None:
    """Solo para tests: invalida la caché del nombre."""
    clinical_brand.cache_clear()
    clinical_brand_subtitle.cache_clear()
