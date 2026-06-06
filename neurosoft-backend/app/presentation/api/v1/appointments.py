"""
app/presentation/api/v1/appointments.py
=========================================
Módulo completo de agenda y citas.

DTOs, use cases y endpoints en un solo archivo
(patrón simplificado para módulos de mediano tamaño).

Endpoints:
    POST   /agenda/                       → crear cita
    GET    /agenda/                       → listar citas con filtros
    GET    /agenda/hoy                    → citas de hoy
    GET    /agenda/semana                 → citas de la semana (próximos 7 días)
    GET    /agenda/{cita_id}              → detalle de una cita
    PATCH  /agenda/{cita_id}              → actualizar estado/notas
    DELETE /agenda/{cita_id}              → eliminar cita
    GET    /agenda/paciente/{patient_id}  → historial de citas de un paciente
"""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import desc
from sqlalchemy.orm import Session

from app.presentation.dependencies import DbSession

agenda_router = APIRouter(prefix="/agenda", tags=["Agenda y Citas"])


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────

ESTADOS_VALIDOS = ("programada", "confirmada", "atendida", "cancelada", "no_asistio")
TIPOS_VALIDOS = ("evaluacion", "devolucion", "terapia", "seguimiento", "otro")


class AppointmentCreateDTO(BaseModel):
    patient_id: str
    profesional_id: str | None = None
    fecha: date
    hora_inicio: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    hora_fin: str | None = Field(default=None, pattern=r"^\d{2}:\d{2}$")
    tipo_cita: str = Field(default="evaluacion")
    motivo: str | None = None
    notas_internas: str | None = None
    eps: str | None = None
    regimen: str | None = None
    autorizacion_no: str | None = None
    cups: str | None = None
    modalidad: str | None = Field(default="presencial")
    discapacidad: str | None = None
    contacto_telefono: str | None = None
    contacto_correo: str | None = None

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "uuid-del-paciente",
                "fecha": "2025-06-10",
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "tipo_cita": "evaluacion",
                "motivo": "Evaluación neuropsicológica WISC-IV",
            }
        }
    }


class AppointmentUpdateDTO(BaseModel):
    """Actualización parcial — solo envía los campos a cambiar."""

    fecha: date | None = None
    hora_inicio: str | None = None
    hora_fin: str | None = None
    tipo_cita: str | None = None
    motivo: str | None = None
    estado: str | None = None
    notas_internas: str | None = None
    profesional_id: str | None = None
    eps: str | None = None
    regimen: str | None = None
    autorizacion_no: str | None = None
    cups: str | None = None
    modalidad: str | None = None
    discapacidad: str | None = None
    contacto_telefono: str | None = None
    contacto_correo: str | None = None


class PatientMiniDTO(BaseModel):
    id: str
    nombre_completo: str
    numero_documento: str
    edad_display: str

    model_config = {"from_attributes": True}


class AppointmentResponseDTO(BaseModel):
    id: str
    patient_id: str
    profesional_id: str | None
    fecha: date
    hora_inicio: str
    hora_fin: str | None
    tipo_cita: str
    motivo: str | None
    estado: str
    notas_internas: str | None
    eps: str | None = None
    regimen: str | None = None
    autorizacion_no: str | None = None
    cups: str | None = None
    modalidad: str | None = None
    discapacidad: str | None = None
    contacto_telefono: str | None = None
    contacto_correo: str | None = None
    created_at: str
    updated_at: str | None
    # Datos del paciente embebidos para el calendario
    paciente_nombre: str | None = None
    paciente_doc: str | None = None
    profesional_nombre: str | None = None


class AgendaDayDTO(BaseModel):
    """Un día del calendario con sus citas."""

    fecha: date
    citas: list[AppointmentResponseDTO]
    total: int


class AgendaStatsDTO(BaseModel):
    """Estadísticas rápidas de la agenda."""

    hoy: int
    esta_semana: int
    este_mes: int
    pendientes: int  # programadas + confirmadas futuras
    atendidas_mes: int


# ─────────────────────────────────────────────────────────────
# Use Cases (inline — módulo pequeño)
# ─────────────────────────────────────────────────────────────


def _orm_to_dto(orm) -> AppointmentResponseDTO:
    paciente_nombre = None
    paciente_doc = None
    prof_nombre = None

    if orm.patient:
        p = orm.patient
        paciente_nombre = " ".join(
            filter(
                None,
                [
                    p.primer_nombre,
                    p.segundo_nombre,
                    p.primer_apellido,
                    p.segundo_apellido,
                ],
            )
        )
        paciente_doc = p.numero_documento

    if orm.profesional:
        prof_nombre = orm.profesional.nombre_completo

    return AppointmentResponseDTO(
        id=orm.id,
        patient_id=orm.patient_id,
        profesional_id=orm.profesional_id,
        fecha=orm.fecha,
        hora_inicio=orm.hora_inicio,
        hora_fin=orm.hora_fin,
        tipo_cita=orm.tipo_cita or "evaluacion",
        motivo=orm.motivo,
        estado=orm.estado or "programada",
        notas_internas=orm.notas_internas,
        eps=getattr(orm, "eps", None),
        regimen=getattr(orm, "regimen", None),
        autorizacion_no=getattr(orm, "autorizacion_no", None),
        cups=getattr(orm, "cups", None),
        modalidad=getattr(orm, "modalidad", None),
        discapacidad=getattr(orm, "discapacidad", None),
        contacto_telefono=getattr(orm, "contacto_telefono", None),
        contacto_correo=getattr(orm, "contacto_correo", None),
        created_at=orm.created_at.isoformat() if orm.created_at else "",
        updated_at=orm.updated_at.isoformat() if orm.updated_at else None,
        paciente_nombre=paciente_nombre,
        paciente_doc=paciente_doc,
        profesional_nombre=prof_nombre,
    )


def _get_or_404(db: Session, cita_id: str):
    from app.infrastructure.database.orm_models import AppointmentORM

    orm = db.get(AppointmentORM, cita_id)
    if orm is None:
        raise HTTPException(status_code=404, detail=f"Cita '{cita_id}' no encontrada.")
    return orm


# ─────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────


@agenda_router.post(
    "/",
    response_model=AppointmentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita",
    description="Agenda una cita para un paciente. El estado inicial es 'programada'.",
)
def create_appointment(dto: AppointmentCreateDTO, db: DbSession):
    from app.infrastructure.database.orm_models import AppointmentORM, PatientORM

    # Verificar que el paciente existe
    patient = db.get(PatientORM, dto.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente no encontrado.")

    if dto.tipo_cita not in TIPOS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"tipo_cita inválido. Válidos: {TIPOS_VALIDOS}")

    orm = AppointmentORM(
        id=str(uuid.uuid4()),
        patient_id=dto.patient_id,
        profesional_id=dto.profesional_id,
        fecha=dto.fecha,
        hora_inicio=dto.hora_inicio,
        hora_fin=dto.hora_fin,
        tipo_cita=dto.tipo_cita,
        motivo=dto.motivo,
        estado="programada",
        notas_internas=dto.notas_internas,
        eps=dto.eps,
        regimen=dto.regimen,
        autorizacion_no=dto.autorizacion_no,
        cups=dto.cups,
        modalidad=dto.modalidad,
        discapacidad=dto.discapacidad,
        contacto_telefono=dto.contacto_telefono,
        contacto_correo=dto.contacto_correo,
        created_at=datetime.now(UTC),
        updated_at=datetime.now(UTC),
    )
    db.add(orm)
    db.flush()
    db.refresh(orm)
    return _orm_to_dto(orm)


@agenda_router.get(
    "/hoy",
    response_model=AgendaDayDTO,
    summary="Citas de hoy",
)
def get_today(
    profesional_id: str | None = Query(default=None),
    db: DbSession = None,
):
    from sqlalchemy.orm import joinedload

    from app.infrastructure.database.orm_models import AppointmentORM

    hoy = date.today()
    q = (
        db.query(AppointmentORM)
        .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
        .filter(AppointmentORM.fecha == hoy)
    )
    if profesional_id:
        q = q.filter(AppointmentORM.profesional_id == profesional_id)
    citas = q.order_by(AppointmentORM.hora_inicio).all()
    items = [_orm_to_dto(c) for c in citas]
    return AgendaDayDTO(fecha=hoy, citas=items, total=len(items))


@agenda_router.get(
    "/semana",
    response_model=list[AgendaDayDTO],
    summary="Citas de los próximos 7 días",
    description="Retorna la agenda agrupada por día para los próximos 7 días.",
)
def get_week(
    desde: str | None = Query(default=None, description="YYYY-MM-DD. Default: hoy"),
    profesional_id: str | None = Query(default=None),
    db: DbSession = None,
):
    from sqlalchemy.orm import joinedload

    from app.infrastructure.database.orm_models import AppointmentORM

    inicio = date.fromisoformat(desde) if desde else date.today()
    fin = inicio + timedelta(days=6)

    q = (
        db.query(AppointmentORM)
        .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
        .filter(
            AppointmentORM.fecha >= inicio,
            AppointmentORM.fecha <= fin,
        )
    )
    if profesional_id:
        q = q.filter(AppointmentORM.profesional_id == profesional_id)

    citas = q.order_by(AppointmentORM.fecha, AppointmentORM.hora_inicio).all()

    # Agrupar por día
    dias: dict = {}
    for d in range(7):
        dia = inicio + timedelta(days=d)
        dias[dia] = []
    for c in citas:
        if c.fecha in dias:
            dias[c.fecha].append(_orm_to_dto(c))

    return [AgendaDayDTO(fecha=dia, citas=items, total=len(items)) for dia, items in sorted(dias.items())]


@agenda_router.get(
    "/stats",
    response_model=AgendaStatsDTO,
    summary="Estadísticas de la agenda",
)
def get_agenda_stats(
    profesional_id: str | None = Query(default=None),
    db: DbSession = None,
):
    from sqlalchemy import func

    from app.infrastructure.database.orm_models import AppointmentORM

    hoy = date.today()
    mes_inicio = date(hoy.year, hoy.month, 1)
    semana_fin = hoy + timedelta(days=6)

    def _base(q):
        if profesional_id:
            q = q.filter(AppointmentORM.profesional_id == profesional_id)
        return q

    hoy_count = _base(db.query(func.count(AppointmentORM.id)).filter(AppointmentORM.fecha == hoy)).scalar() or 0

    semana_count = (
        _base(
            db.query(func.count(AppointmentORM.id)).filter(
                AppointmentORM.fecha >= hoy, AppointmentORM.fecha <= semana_fin
            )
        ).scalar()
        or 0
    )

    mes_count = _base(db.query(func.count(AppointmentORM.id)).filter(AppointmentORM.fecha >= mes_inicio)).scalar() or 0

    pendientes = (
        _base(
            db.query(func.count(AppointmentORM.id)).filter(
                AppointmentORM.fecha >= hoy,
                AppointmentORM.estado.in_(["programada", "confirmada"]),
            )
        ).scalar()
        or 0
    )

    atendidas_mes = (
        _base(
            db.query(func.count(AppointmentORM.id)).filter(
                AppointmentORM.fecha >= mes_inicio,
                AppointmentORM.estado == "atendida",
            )
        ).scalar()
        or 0
    )

    return AgendaStatsDTO(
        hoy=hoy_count,
        esta_semana=semana_count,
        este_mes=mes_count,
        pendientes=pendientes,
        atendidas_mes=atendidas_mes,
    )


@agenda_router.get(
    "/",
    response_model=list[AppointmentResponseDTO],
    summary="Listar citas con filtros",
)
def list_appointments(
    fecha_desde: str | None = Query(default=None, description="YYYY-MM-DD"),
    fecha_hasta: str | None = Query(default=None, description="YYYY-MM-DD"),
    estado: str | None = Query(default=None),
    tipo_cita: str | None = Query(default=None),
    profesional_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: DbSession = None,
):
    from sqlalchemy.orm import joinedload

    from app.infrastructure.database.orm_models import AppointmentORM

    q = db.query(AppointmentORM).options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
    if fecha_desde:
        q = q.filter(AppointmentORM.fecha >= date.fromisoformat(fecha_desde))
    if fecha_hasta:
        q = q.filter(AppointmentORM.fecha <= date.fromisoformat(fecha_hasta))
    if estado:
        q = q.filter(AppointmentORM.estado == estado)
    if tipo_cita:
        q = q.filter(AppointmentORM.tipo_cita == tipo_cita)
    if profesional_id:
        q = q.filter(AppointmentORM.profesional_id == profesional_id)

    citas = q.order_by(AppointmentORM.fecha.desc(), AppointmentORM.hora_inicio).limit(limit).offset(offset).all()
    return [_orm_to_dto(c) for c in citas]


@agenda_router.get(
    "/paciente/{patient_id}",
    response_model=list[AppointmentResponseDTO],
    summary="Historial de citas de un paciente",
)
def get_patient_appointments(
    patient_id: str,
    solo_futuras: bool = Query(default=False),
    db: DbSession = None,
):
    from sqlalchemy.orm import joinedload

    from app.infrastructure.database.orm_models import AppointmentORM

    q = (
        db.query(AppointmentORM)
        .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
        .filter(AppointmentORM.patient_id == patient_id)
    )
    if solo_futuras:
        q = q.filter(AppointmentORM.fecha >= date.today())

    citas = q.order_by(desc(AppointmentORM.fecha), AppointmentORM.hora_inicio).all()
    return [_orm_to_dto(c) for c in citas]


@agenda_router.get(
    "/{cita_id}",
    response_model=AppointmentResponseDTO,
    summary="Detalle de una cita",
)
def get_appointment(cita_id: str, db: DbSession):
    from sqlalchemy.orm import joinedload

    from app.infrastructure.database.orm_models import AppointmentORM

    orm = (
        db.query(AppointmentORM)
        .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
        .filter(AppointmentORM.id == cita_id)
        .first()
    )
    if orm is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")
    return _orm_to_dto(orm)


@agenda_router.patch(
    "/{cita_id}",
    response_model=AppointmentResponseDTO,
    summary="Actualizar cita (estado, notas, hora, etc.)",
)
def update_appointment(cita_id: str, dto: AppointmentUpdateDTO, db: DbSession):
    from sqlalchemy.orm import joinedload

    from app.infrastructure.database.orm_models import AppointmentORM

    orm = db.get(AppointmentORM, cita_id)
    if orm is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")

    if dto.estado and dto.estado not in ESTADOS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"estado inválido. Válidos: {ESTADOS_VALIDOS}")
    if dto.tipo_cita and dto.tipo_cita not in TIPOS_VALIDOS:
        raise HTTPException(status_code=422, detail=f"tipo_cita inválido. Válidos: {TIPOS_VALIDOS}")

    fields = [
        "fecha",
        "hora_inicio",
        "hora_fin",
        "tipo_cita",
        "motivo",
        "estado",
        "notas_internas",
        "profesional_id",
        "eps",
        "regimen",
        "autorizacion_no",
        "cups",
        "modalidad",
        "discapacidad",
        "contacto_telefono",
        "contacto_correo",
    ]
    for field in fields:
        val = getattr(dto, field, None)
        if val is not None:
            setattr(orm, field, val)
    orm.updated_at = datetime.now(UTC)
    db.flush()

    # Reload with joins
    orm2 = (
        db.query(AppointmentORM)
        .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
        .filter(AppointmentORM.id == cita_id)
        .first()
    )
    return _orm_to_dto(orm2)


@agenda_router.delete(
    "/{cita_id}",
    status_code=204,
    summary="Eliminar cita",
)
def delete_appointment(cita_id: str, db: DbSession):
    from app.infrastructure.database.orm_models import AppointmentORM

    orm = db.get(AppointmentORM, cita_id)
    if orm is None:
        raise HTTPException(status_code=404, detail="Cita no encontrada.")
    db.delete(orm)
