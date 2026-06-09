"""Endpoints de agenda y citas — thin controller."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Query, status

from app.application.dtos.appointment_dtos import (
    AgendaDayDTO,
    AgendaStatsDTO,
    AppointmentCreateDTO,
    AppointmentResponseDTO,
    AppointmentUpdateDTO,
)
from app.presentation.api.v1.auth import CurrentUser
from app.presentation.dependencies import (
    CreateAppointmentUC,
    DeleteAppointmentUC,
    GetAgendaStatsUC,
    GetAppointmentUC,
    GetTodayAppointmentsUC,
    GetWeekAppointmentsUC,
    ListAppointmentsUC,
    ListPatientAppointmentsUC,
    UpdateAppointmentUC,
)

agenda_router = APIRouter(prefix="/agenda", tags=["Agenda y Citas"])


@agenda_router.post(
    "/",
    response_model=AppointmentResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Crear nueva cita",
)
def create_appointment(dto: AppointmentCreateDTO, uc: CreateAppointmentUC, user: CurrentUser):
    if user.profesional_id and not dto.profesional_id:
        dto.profesional_id = user.profesional_id
    return uc.execute(dto)


@agenda_router.get("/hoy", response_model=AgendaDayDTO, summary="Citas de hoy")
def get_today(
    uc: GetTodayAppointmentsUC,
    profesional_id: str | None = Query(default=None),
):
    return uc.execute(profesional_id)


@agenda_router.get("/semana", response_model=list[AgendaDayDTO], summary="Citas de los próximos 7 días")
def get_week(
    uc: GetWeekAppointmentsUC,
    desde: str | None = Query(default=None, description="YYYY-MM-DD. Default: hoy"),
    profesional_id: str | None = Query(default=None),
):
    inicio = date.fromisoformat(desde) if desde else None
    return uc.execute(inicio, profesional_id)


@agenda_router.get("/stats", response_model=AgendaStatsDTO, summary="Estadísticas de la agenda")
def get_agenda_stats(
    uc: GetAgendaStatsUC,
    profesional_id: str | None = Query(default=None),
):
    return uc.execute(profesional_id)


@agenda_router.get("/", response_model=list[AppointmentResponseDTO], summary="Listar citas con filtros")
def list_appointments(
    uc: ListAppointmentsUC,
    fecha_desde: str | None = Query(default=None, description="YYYY-MM-DD"),
    fecha_hasta: str | None = Query(default=None, description="YYYY-MM-DD"),
    estado: str | None = Query(default=None),
    tipo_cita: str | None = Query(default=None),
    profesional_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
):
    return uc.execute(
        fecha_desde=date.fromisoformat(fecha_desde) if fecha_desde else None,
        fecha_hasta=date.fromisoformat(fecha_hasta) if fecha_hasta else None,
        estado=estado,
        tipo_cita=tipo_cita,
        profesional_id=profesional_id,
        limit=limit,
        offset=offset,
    )


@agenda_router.get(
    "/paciente/{patient_id}",
    response_model=list[AppointmentResponseDTO],
    summary="Historial de citas de un paciente",
)
def get_patient_appointments(
    patient_id: str,
    uc: ListPatientAppointmentsUC,
    solo_futuras: bool = Query(default=False),
):
    return uc.execute(patient_id, solo_futuras=solo_futuras)


@agenda_router.get("/{cita_id}", response_model=AppointmentResponseDTO, summary="Detalle de una cita")
def get_appointment(cita_id: str, uc: GetAppointmentUC):
    return uc.execute(cita_id)


@agenda_router.patch("/{cita_id}", response_model=AppointmentResponseDTO, summary="Actualizar cita")
def update_appointment(cita_id: str, dto: AppointmentUpdateDTO, uc: UpdateAppointmentUC):
    return uc.execute(cita_id, dto)


@agenda_router.delete("/{cita_id}", status_code=204, summary="Eliminar cita")
def delete_appointment(cita_id: str, uc: DeleteAppointmentUC):
    uc.execute(cita_id)
    return None
