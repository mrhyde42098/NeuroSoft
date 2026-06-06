"""
app/presentation/api/v1/inconclusos.py
=========================================
Módulo de informes inconclusos / casos que requieren seguimiento.

Permite marcar un caso como inconcluso (y su motivo) para recordar
al profesional que debe volver a él: ya sea porque la evaluación
quedó incompleta, porque se necesita una segunda orden, porque el
paciente no continuó el proceso, o porque traía evaluación vigente
de otro prestador.

Endpoints:
    POST   /inconclusos/                → crear informe inconcluso
    GET    /inconclusos/                → listar (filtro por estado y patient_id)
    GET    /inconclusos/stats           → conteo por estado
    PATCH  /inconclusos/{id}            → actualizar (incluye resolver)
    DELETE /inconclusos/{id}            → eliminar
"""

from __future__ import annotations

import uuid
from datetime import date, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.infrastructure.database.orm_models import InformeInconclusoORM, PatientORM
from app.presentation.dependencies import DbSession

inconclusos_router = APIRouter(prefix="/inconclusos", tags=["Informes Inconclusos"])


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────

MOTIVOS_VALIDOS = (
    "bateria_mas_segunda_orden",
    "evaluacion_incompleta",
    "evaluacion_reciente",
    "cancelado_paciente",
    "otro",
)

ESTADOS_VALIDOS = ("abierto", "resuelto", "cerrado")


class InconclusoCreateDTO(BaseModel):
    patient_id: str
    evaluation_id: str | None = None
    profesional_id: str | None = None
    motivo_id: str
    motivo_titulo: str | None = None
    descripcion: str | None = None
    accion_sugerida: str | None = None
    plazo_dias: int = 15


class InconclusoUpdateDTO(BaseModel):
    estado: str | None = None
    notas_resolucion: str | None = None
    accion_sugerida: str | None = None


class InconclusoResponseDTO(BaseModel):
    id: str
    patient_id: str
    paciente_nombre: str | None = None
    evaluation_id: str | None = None
    profesional_id: str | None = None
    motivo_id: str
    motivo_titulo: str | None = None
    descripcion: str | None = None
    accion_sugerida: str | None = None
    plazo_dias: int
    fecha_creacion: date
    fecha_limite: date | None = None
    estado: str
    resuelto_en: date | None = None
    notas_resolucion: str | None = None
    dias_restantes: int | None = None


class InconclusoStatsDTO(BaseModel):
    total: int
    abiertos: int
    resueltos: int
    cerrados: int
    vencidos: int


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _orm_to_dto(orm: InformeInconclusoORM, db: Session) -> InconclusoResponseDTO:
    # Paciente nombre
    pat_nombre = None
    pat = db.query(PatientORM).filter_by(id=orm.patient_id).first()
    if pat:
        partes = [pat.primer_nombre, pat.segundo_nombre, pat.primer_apellido, pat.segundo_apellido]
        pat_nombre = " ".join([p for p in partes if p])

    dias_rest = None
    if orm.fecha_limite and orm.estado == "abierto":
        dias_rest = (orm.fecha_limite - date.today()).days

    return InconclusoResponseDTO(
        id=orm.id,
        patient_id=orm.patient_id,
        paciente_nombre=pat_nombre,
        evaluation_id=orm.evaluation_id,
        profesional_id=orm.profesional_id,
        motivo_id=orm.motivo_id,
        motivo_titulo=orm.motivo_titulo,
        descripcion=orm.descripcion,
        accion_sugerida=orm.accion_sugerida,
        plazo_dias=orm.plazo_dias or 15,
        fecha_creacion=orm.fecha_creacion,
        fecha_limite=orm.fecha_limite,
        estado=orm.estado or "abierto",
        resuelto_en=orm.resuelto_en,
        notas_resolucion=orm.notas_resolucion,
        dias_restantes=dias_rest,
    )


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────


@inconclusos_router.post("/", response_model=InconclusoResponseDTO, status_code=201)
def crear_inconcluso(dto: InconclusoCreateDTO, db: DbSession):
    if dto.motivo_id not in MOTIVOS_VALIDOS:
        raise HTTPException(422, f"motivo_id inválido. Valores válidos: {MOTIVOS_VALIDOS}")
    pat = db.query(PatientORM).filter_by(id=dto.patient_id).first()
    if not pat:
        raise HTTPException(404, "Paciente no encontrado")

    hoy = date.today()
    orm = InformeInconclusoORM(
        id=str(uuid.uuid4()),
        patient_id=dto.patient_id,
        evaluation_id=dto.evaluation_id,
        profesional_id=dto.profesional_id,
        motivo_id=dto.motivo_id,
        motivo_titulo=dto.motivo_titulo,
        descripcion=dto.descripcion,
        accion_sugerida=dto.accion_sugerida,
        plazo_dias=dto.plazo_dias,
        fecha_creacion=hoy,
        fecha_limite=hoy + timedelta(days=dto.plazo_dias or 15),
        estado="abierto",
    )
    db.add(orm)
    db.commit()
    db.refresh(orm)
    return _orm_to_dto(orm, db)


@inconclusos_router.get("/", response_model=list[InconclusoResponseDTO])
def listar_inconclusos(
    db: DbSession,
    estado: str | None = None,
    patient_id: str | None = None,
):
    q = db.query(InformeInconclusoORM)
    if estado:
        q = q.filter(InformeInconclusoORM.estado == estado)
    if patient_id:
        q = q.filter(InformeInconclusoORM.patient_id == patient_id)
    q = q.order_by(InformeInconclusoORM.fecha_creacion.desc())
    items = q.all()
    return [_orm_to_dto(o, db) for o in items]


@inconclusos_router.get("/stats", response_model=InconclusoStatsDTO)
def stats_inconclusos(db: DbSession):
    all_items = db.query(InformeInconclusoORM).all()
    hoy = date.today()
    abiertos = sum(1 for i in all_items if (i.estado or "abierto") == "abierto")
    resueltos = sum(1 for i in all_items if i.estado == "resuelto")
    cerrados = sum(1 for i in all_items if i.estado == "cerrado")
    vencidos = sum(
        1 for i in all_items if (i.estado or "abierto") == "abierto" and i.fecha_limite and i.fecha_limite < hoy
    )
    return InconclusoStatsDTO(
        total=len(all_items),
        abiertos=abiertos,
        resueltos=resueltos,
        cerrados=cerrados,
        vencidos=vencidos,
    )


@inconclusos_router.patch("/{item_id}", response_model=InconclusoResponseDTO)
def actualizar_inconcluso(item_id: str, dto: InconclusoUpdateDTO, db: DbSession):
    orm = db.query(InformeInconclusoORM).filter_by(id=item_id).first()
    if not orm:
        raise HTTPException(404, "Informe inconcluso no encontrado")

    if dto.estado is not None:
        if dto.estado not in ESTADOS_VALIDOS:
            raise HTTPException(422, f"estado inválido. Valores válidos: {ESTADOS_VALIDOS}")
        orm.estado = dto.estado
        if dto.estado in ("resuelto", "cerrado"):
            orm.resuelto_en = date.today()
    if dto.notas_resolucion is not None:
        orm.notas_resolucion = dto.notas_resolucion
    if dto.accion_sugerida is not None:
        orm.accion_sugerida = dto.accion_sugerida

    db.commit()
    db.refresh(orm)
    return _orm_to_dto(orm, db)


@inconclusos_router.delete("/{item_id}", status_code=204)
def eliminar_inconcluso(item_id: str, db: DbSession):
    orm = db.query(InformeInconclusoORM).filter_by(id=item_id).first()
    if not orm:
        raise HTTPException(404, "Informe inconcluso no encontrado")
    db.delete(orm)
    db.commit()
    return None
