"""
app/presentation/api/v1/retencion.py
====================================
S5.2 (Frente 5): Endpoint de cumplimiento de retención de HC.

Permite al clínico/administrador consultar el estado de retención de
las Historias Clínicas según la Resolución 1995 de 1999, art. 28.

  GET /api/v1/admin/retencion
    → Resumen general: cuántas vigentes/caducadas/próximas.
  GET /api/v1/admin/retencion/paciente/{id}
    → Estado individual de un paciente específico.

Solo accesible para usuarios con rol 'admin' (gating por rol actual).
"""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.infrastructure.database.orm_models import PatientORM
from app.infrastructure.retencion import (
    estado_retencion,
    resumen_inventario,
)
from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

router = APIRouter(prefix="/admin/retencion", tags=["🛡️ Admin · Retención HC"])


@router.get(
    "",
    summary="Resumen del estado de retención de las HCs",
    description=(
        "Devuelve estadísticas agregadas del estado de retención de las "
        "Historias Clínicas conforme a la Resolución 1995 de 1999, art. 28. "
        "Estados: 'vigente', 'proximo_a_caducar' (≤2 años), 'caducada'."
    ),
)
def resumen_retencion(
    db: DbSession,
    admin=Depends(require_admin),
) -> dict[str, Any]:
    patients = db.query(PatientORM).filter(PatientORM.is_active == True).all()  # noqa: E712
    return resumen_inventario(patients, date.today())


@router.get(
    "/paciente/{patient_id}",
    summary="Estado de retención de un paciente específico",
    description="Calcula la fecha de caducidad de la HC de un paciente.",
)
def retencion_paciente(
    patient_id: str,
    db: DbSession,
    admin=Depends(require_admin),
) -> dict[str, Any]:
    p = db.query(PatientORM).filter(PatientORM.id == patient_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Paciente no encontrado")
    e = estado_retencion(p.fecha_atencion, p.fecha_nacimiento, date.today())
    return {
        "patient_id": p.id,
        "paciente": f"{p.primer_nombre} {p.primer_apellido}",
        "documento": p.numero_documento,
        **e.to_dict(),
    }
