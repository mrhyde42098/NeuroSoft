from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

ESTADOS_VALIDOS = ("programada", "confirmada", "atendida", "cancelada", "no_asistio")
TIPOS_VALIDOS = ("evaluacion", "devolucion", "terapia", "seguimiento", "entrevista", "otro")


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


class AppointmentUpdateDTO(BaseModel):
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
    paciente_nombre: str | None = None
    paciente_doc: str | None = None
    profesional_nombre: str | None = None


class AgendaDayDTO(BaseModel):
    fecha: date
    citas: list[AppointmentResponseDTO]
    total: int


class AgendaStatsDTO(BaseModel):
    hoy: int
    esta_semana: int
    este_mes: int
    pendientes: int
    atendidas_mes: int
