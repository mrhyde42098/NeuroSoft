"""Casos de uso de agenda y citas."""

from __future__ import annotations

from datetime import date

from app.application.dtos.appointment_dtos import (
    AgendaDayDTO,
    AgendaStatsDTO,
    AppointmentCreateDTO,
    AppointmentResponseDTO,
    AppointmentUpdateDTO,
)
from app.infrastructure.repositories.appointment_repo import AppointmentRepository


class CreateAppointmentUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, dto: AppointmentCreateDTO) -> AppointmentResponseDTO:
        return self._repo.create(dto)


class GetTodayAppointmentsUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, profesional_id: str | None = None) -> AgendaDayDTO:
        return self._repo.get_today(profesional_id)


class GetWeekAppointmentsUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, desde: date | None, profesional_id: str | None = None) -> list[AgendaDayDTO]:
        return self._repo.get_week(desde, profesional_id)


class GetAgendaStatsUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, profesional_id: str | None = None) -> AgendaStatsDTO:
        return self._repo.get_stats(profesional_id)


class ListAppointmentsUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(
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
        return self._repo.list_appointments(
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            estado=estado,
            tipo_cita=tipo_cita,
            profesional_id=profesional_id,
            limit=limit,
            offset=offset,
        )


class ListPatientAppointmentsUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, patient_id: str, *, solo_futuras: bool = False) -> list[AppointmentResponseDTO]:
        return self._repo.list_by_patient(patient_id, solo_futuras=solo_futuras)


class GetAppointmentUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, cita_id: str) -> AppointmentResponseDTO:
        return self._repo.get_by_id(cita_id)


class UpdateAppointmentUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, cita_id: str, dto: AppointmentUpdateDTO) -> AppointmentResponseDTO:
        return self._repo.update(cita_id, dto)


class DeleteAppointmentUseCase:
    def __init__(self, repo: AppointmentRepository):
        self._repo = repo

    def execute(self, cita_id: str) -> None:
        self._repo.delete(cita_id)
