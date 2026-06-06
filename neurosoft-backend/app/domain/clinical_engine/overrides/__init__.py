"""
app/domain/clinical_engine/overrides/__init__.py
=================================================
Registro de overrides Python para pruebas con baremos heredados del Excel
VBA original que no representan clasificaciones clínicas válidas.

F7.2 — PLAN_MIGRACION_BAREMOS.md.

PROPÓSITO
---------
Algunos tests del motor (ej. AdBeck) tienen en `BD_NEURO_MAESTRA.json`
valores que NO son clasificaciones clínicas: son "Cell IDs" de un Excel
heredado. El motor los lee como si fueran baremos y devuelve
clasificaciones incorrectas.

En lugar de modificar el JSON (regla de oro: el BD es intocable salvo
consulta explícita al usuario), definimos un override Python que
intercepta `BaremosLoader.get_prueba("AdBeck")` y devuelve un baremo
correcto basado en la literatura oficial (Beck 1996, Lawton 1969, etc.).

PATRÓN
------
1. Cada override vive en su propio módulo `overrides/<test_id>.py`.
2. Cada override expone una función `get_baremo_override() -> Dict[str, Any]`
   que retorna la estructura `baremos` corregida.
3. `BaremosLoader` mantiene un dict `_OVERRIDES: Dict[str, Callable]`
   que se consulta ANTES de devolver el baremo real.
4. El módulo también expone un flag `baremo_en_revision: bool` por
   prueba, accesible vía `BaremosLoader.baremo_en_revision(test_id)`.

GARANTÍAS
---------
- BD_NEURO_MAESTRA.json NO se modifica.
- El checksum del BD cargado se preserva (es trazabilidad clínica).
- La versión del BD se preserva.
- Informes generados previamente siguen siendo reproducibles porque el
  override sólo afecta pruebas llamadas AHORA.
"""

from __future__ import annotations

from typing import Any, Callable

# Registro: test_id -> callable que retorna el dict baremos corregido.
# Añadir nuevas entradas a medida que se incorporen más overrides.
#
# F7.2 — 2026-06-03: AdBeck fue corregido directamente en
# BD_NEURO_MAESTRA.json (autorización one-time del propietario).
# El override Python ya NO se aplica por defecto. Se conserva el módulo
# `adbeck.py` como LEGACY por si en el futuro se necesita re-aplicar
# (p.ej. si la corrección del BD se revierte).
_OVERRIDES: dict[str, Callable[[], dict[str, Any]]] = {
    # "AdBeck": get_adbeck_override,  # LEGACY — BD corregido directamente
}


def get_override(test_id: str) -> dict[str, Any] | None:
    """
    Retorna el baremo override para `test_id`, o None si no hay override.

    El retorno es un dict con la estructura completa de `baremos` que
    se va a inyectar en lugar del baremo original del JSON.
    """
    factory = _OVERRIDES.get(test_id)
    if factory is None:
        return None
    return factory()


def has_override(test_id: str) -> bool:
    return test_id in _OVERRIDES


def list_overrides() -> list[str]:
    """Lista los test_ids que tienen override activo. Para diagnóstico."""
    return sorted(_OVERRIDES.keys())


__all__ = ["get_override", "has_override", "list_overrides"]
