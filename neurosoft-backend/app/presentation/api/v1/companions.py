"""
app/presentation/api/v1/companions.py
=======================================
§M-7 — CRUD de acompañantes (familiares/cuidadores) por paciente.

Reemplaza el texto libre que antes vivía en HC con una entidad
gestionable: contacto directo, autorización para responder escalas
proxy, trazabilidad legal de acompañantes que firmaron consentimientos
o recibieron resultados.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.presentation.dependencies import DbSession

companions_router = APIRouter(prefix="/companions", tags=["Acompañantes"])

_RELACIONES_VALIDAS = ("madre", "padre", "hermano", "conyuge", "hijo", "cuidador", "tutor", "otro")


class CompanionDTO(BaseModel):
    nombre_completo: str = Field(..., min_length=2, max_length=200)
    relacion: str | None = Field(default=None, max_length=50)
    documento: str | None = Field(default=None, max_length=30)
    telefono: str | None = Field(default=None, max_length=50)
    email: str | None = Field(default=None, max_length=100)
    autoriza_escalas: bool = False
    autoriza_contacto: bool = True
    es_principal: bool = False
    notas: str | None = None


class CompanionResponseDTO(CompanionDTO):
    id: str
    patient_id: str


@companions_router.get("", response_model=list[CompanionResponseDTO], summary="Listar acompañantes de un paciente")
def list_companions(patient_id: str = Query(...), db: DbSession = None):
    from app.infrastructure.database.orm_models import CompanionORM

    rows = (
        db.query(CompanionORM)
        .filter_by(patient_id=patient_id)
        .order_by(CompanionORM.es_principal.desc(), CompanionORM.created_at.desc())
        .all()
    )
    return [_row_to_dto(r) for r in rows]


@companions_router.post("", response_model=CompanionResponseDTO, status_code=201, summary="Crear acompañante")
def create_companion(patient_id: str, dto: CompanionDTO, db: DbSession):
    from app.infrastructure.database.orm_models import CompanionORM, PatientORM

    pat = db.get(PatientORM, patient_id)
    if not pat:
        raise HTTPException(404, detail="Paciente no encontrado")

    if dto.relacion and dto.relacion not in _RELACIONES_VALIDAS:
        raise HTTPException(400, detail=f"Relación inválida. Valores aceptados: {', '.join(_RELACIONES_VALIDAS)}")

    # Si se marca como principal, desmarcar los otros del paciente
    if dto.es_principal:
        for r in db.query(CompanionORM).filter_by(patient_id=patient_id).all():
            r.es_principal = False

    row = CompanionORM(
        id=str(uuid.uuid4()),
        patient_id=patient_id,
        **dto.model_dump(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return _row_to_dto(row)


@companions_router.put("/{companion_id}", response_model=CompanionResponseDTO, summary="Actualizar acompañante")
def update_companion(companion_id: str, dto: CompanionDTO, db: DbSession):
    from app.infrastructure.database.orm_models import CompanionORM

    row = db.get(CompanionORM, companion_id)
    if not row:
        raise HTTPException(404, detail="Acompañante no encontrado")
    if dto.relacion and dto.relacion not in _RELACIONES_VALIDAS:
        raise HTTPException(400, detail="Relación inválida")
    # Si se marca principal, desmarcar los otros
    if dto.es_principal and not row.es_principal:
        for r in db.query(CompanionORM).filter_by(patient_id=row.patient_id).all():
            r.es_principal = False
    for k, v in dto.model_dump().items():
        setattr(row, k, v)
    db.commit()
    db.refresh(row)
    return _row_to_dto(row)


@companions_router.delete("/{companion_id}", summary="Eliminar acompañante")
def delete_companion(companion_id: str, db: DbSession):
    from app.infrastructure.database.orm_models import CompanionORM

    row = db.get(CompanionORM, companion_id)
    if not row:
        raise HTTPException(404, detail="Acompañante no encontrado")
    db.delete(row)
    db.commit()
    return {"ok": True}


def _row_to_dto(row):
    return CompanionResponseDTO(
        id=row.id,
        patient_id=row.patient_id,
        nombre_completo=row.nombre_completo,
        relacion=row.relacion,
        documento=row.documento,
        telefono=row.telefono,
        email=row.email,
        autoriza_escalas=bool(row.autoriza_escalas),
        autoriza_contacto=bool(row.autoriza_contacto),
        es_principal=bool(row.es_principal),
        notas=row.notas,
    )
