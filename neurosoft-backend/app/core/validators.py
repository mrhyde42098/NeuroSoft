"""
app/core/validators.py
=======================
Validadores y type aliases reusables para DTOs Pydantic.

Nota: conservamos `str` como tipo base (no `uuid.UUID`) porque muchas
rutas de FastAPI reciben IDs como path params tipados `str` y porque el
ORM guarda los UUIDs como texto (SQLite carece de tipo UUID nativo). Los
validadores simplemente garantizan que, si el campo se expone en el API,
el valor tenga forma de UUID canónica antes de tocar la base.
"""
from __future__ import annotations

import uuid
from typing import Annotated

from pydantic import AfterValidator


def _check_uuid(value: str) -> str:
    """Rechaza cualquier cadena que no sea un UUID canónico."""
    if not isinstance(value, str):
        raise ValueError("Debe ser un UUID en formato cadena.")
    v = value.strip()
    if not v:
        raise ValueError("UUID no puede estar vacío.")
    try:
        # uuid.UUID acepta formas con/sin guiones y hex plano: normalizamos.
        parsed = uuid.UUID(v)
    except (ValueError, AttributeError, TypeError) as exc:
        raise ValueError(f"No es un UUID válido: {v!r}") from exc
    return str(parsed)


def _check_optional_uuid(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    return _check_uuid(value)


# Type aliases reutilizables en DTOs:
#   from app.core.validators import UUIDStr, OptionalUUIDStr
#   class Foo(BaseModel):
#       patient_id: UUIDStr
UUIDStr = Annotated[str, AfterValidator(_check_uuid)]
OptionalUUIDStr = Annotated[str | None, AfterValidator(_check_optional_uuid)]


__all__ = ["UUIDStr", "OptionalUUIDStr"]
