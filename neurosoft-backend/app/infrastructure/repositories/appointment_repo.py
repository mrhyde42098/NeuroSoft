"""Repositorio de citas / agenda."""

from __future__ import annotations

import uuid
from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import desc, func
from sqlalchemy.orm import Session, joinedload

from app.application.dtos.appointment_dtos import (
    ESTADOS_VALIDOS,
    TIPOS_VALIDOS,
    AgendaDayDTO,
    AgendaStatsDTO,
    AppointmentCreateDTO,
    AppointmentResponseDTO,
    AppointmentUpdateDTO,
)
from app.infrastructure.database.orm_models import AppointmentORM, PatientORM


def orm_to_dto(orm: AppointmentORM) -> AppointmentResponseDTO:
    paciente_nombre = None
    paciente_doc = None
    prof_nombre = None

    if orm.patient:
        p = orm.patient
        paciente_nombre = " ".join(
            filter(
                None,
                [p.primer_nombre, p.segundo_nombre, p.primer_apellido, p.segundo_apellido],
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


class AppointmentRepository:
    def __init__(self, session: Session):
        self._db = session

    def create(self, dto: AppointmentCreateDTO) -> AppointmentResponseDTO:
        patient = self._db.get(PatientORM, dto.patient_id)
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
        self._db.add(orm)
        self._db.flush()
        self._db.refresh(orm)
        return orm_to_dto(orm)

    def get_today(self, profesional_id: str | None = None) -> AgendaDayDTO:
        hoy = date.today()
        q = (
            self._db.query(AppointmentORM)
            .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
            .filter(AppointmentORM.fecha == hoy)
        )
        if profesional_id:
            q = q.filter(AppointmentORM.profesional_id == profesional_id)
        citas = q.order_by(AppointmentORM.hora_inicio).all()
        items = [orm_to_dto(c) for c in citas]
        return AgendaDayDTO(fecha=hoy, citas=items, total=len(items))

    def get_week(self, desde: date | None, profesional_id: str | None = None) -> list[AgendaDayDTO]:
        inicio = desde or date.today()
        fin = inicio + timedelta(days=6)

        q = (
            self._db.query(AppointmentORM)
            .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
            .filter(AppointmentORM.fecha >= inicio, AppointmentORM.fecha <= fin)
        )
        if profesional_id:
            q = q.filter(AppointmentORM.profesional_id == profesional_id)

        citas = q.order_by(AppointmentORM.fecha, AppointmentORM.hora_inicio).all()
        dias: dict[date, list] = {}
        for d in range(7):
            dia = inicio + timedelta(days=d)
            dias[dia] = []
        for c in citas:
            if c.fecha in dias:
                dias[c.fecha].append(orm_to_dto(c))

        return [AgendaDayDTO(fecha=dia, citas=items, total=len(items)) for dia, items in sorted(dias.items())]

    def get_stats(self, profesional_id: str | None = None) -> AgendaStatsDTO:
        hoy = date.today()
        mes_inicio = date(hoy.year, hoy.month, 1)
        semana_fin = hoy + timedelta(days=6)

        def _base(q):
            if profesional_id:
                q = q.filter(AppointmentORM.profesional_id == profesional_id)
            return q

        hoy_count = (
            _base(self._db.query(func.count(AppointmentORM.id)).filter(AppointmentORM.fecha == hoy)).scalar() or 0
        )
        semana_count = (
            _base(
                self._db.query(func.count(AppointmentORM.id)).filter(
                    AppointmentORM.fecha >= hoy, AppointmentORM.fecha <= semana_fin
                )
            ).scalar()
            or 0
        )
        mes_count = (
            _base(self._db.query(func.count(AppointmentORM.id)).filter(AppointmentORM.fecha >= mes_inicio)).scalar()
            or 0
        )
        pendientes = (
            _base(
                self._db.query(func.count(AppointmentORM.id)).filter(
                    AppointmentORM.fecha >= hoy,
                    AppointmentORM.estado.in_(["programada", "confirmada"]),
                )
            ).scalar()
            or 0
        )
        atendidas_mes = (
            _base(
                self._db.query(func.count(AppointmentORM.id)).filter(
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

    def list_appointments(
        self,
        *,
        fecha_desde: date | None = None,
        fecha_hasta: date | None = None,
        estado: str | None = None,
        tipo_cita: str | None = None,
        profesional_id: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[AppointmentResponseDTO]:
        q = self._db.query(AppointmentORM).options(
            joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional)
        )
        if fecha_desde:
            q = q.filter(AppointmentORM.fecha >= fecha_desde)
        if fecha_hasta:
            q = q.filter(AppointmentORM.fecha <= fecha_hasta)
        if estado:
            q = q.filter(AppointmentORM.estado == estado)
        if tipo_cita:
            q = q.filter(AppointmentORM.tipo_cita == tipo_cita)
        if profesional_id:
            q = q.filter(AppointmentORM.profesional_id == profesional_id)

        citas = q.order_by(AppointmentORM.fecha.desc(), AppointmentORM.hora_inicio).limit(limit).offset(offset).all()
        return [orm_to_dto(c) for c in citas]

    def list_by_patient(self, patient_id: str, *, solo_futuras: bool = False) -> list[AppointmentResponseDTO]:
        q = (
            self._db.query(AppointmentORM)
            .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
            .filter(AppointmentORM.patient_id == patient_id)
        )
        if solo_futuras:
            q = q.filter(AppointmentORM.fecha >= date.today())
        citas = q.order_by(desc(AppointmentORM.fecha), AppointmentORM.hora_inicio).all()
        return [orm_to_dto(c) for c in citas]

    def get_by_id(self, cita_id: str) -> AppointmentResponseDTO:
        orm = (
            self._db.query(AppointmentORM)
            .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
            .filter(AppointmentORM.id == cita_id)
            .first()
        )
        if orm is None:
            raise HTTPException(status_code=404, detail="Cita no encontrada.")
        return orm_to_dto(orm)

    def update(self, cita_id: str, dto: AppointmentUpdateDTO) -> AppointmentResponseDTO:
        orm = self._db.get(AppointmentORM, cita_id)
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
        self._db.flush()

        orm2 = (
            self._db.query(AppointmentORM)
            .options(joinedload(AppointmentORM.patient), joinedload(AppointmentORM.profesional))
            .filter(AppointmentORM.id == cita_id)
            .first()
        )
        return orm_to_dto(orm2)

    def delete(self, cita_id: str) -> None:
        orm = self._db.get(AppointmentORM, cita_id)
        if orm is None:
            raise HTTPException(status_code=404, detail="Cita no encontrada.")
        self._db.delete(orm)
