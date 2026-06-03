"""
app/application/dtos/patient_dtos.py
======================================
DTOs (Data Transfer Objects) de Paciente para la capa de presentación.

Los DTOs son modelos Pydantic que validan los datos que entran y salen
de la API. Son DISTINTOS de las entidades de dominio:
    - Los DTOs saben de HTTP, JSON, validación de requests.
    - Las entidades saben de reglas de negocio clínico.

El flujo es:
    HTTP Request → DTO (validación) → Entidad (lógica) → ORM (persistencia)
    ORM (recuperación) → Entidad (lógica) → DTO Response → HTTP Response
"""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field, field_validator, model_validator

from app.core.validators import OptionalUUIDStr

# ============================================================
# REQUEST DTOs (lo que llega desde el Frontend)
# ============================================================

class PatientCreateDTO(BaseModel):
    """Datos para crear un nuevo paciente. POST /api/v1/patients"""

    # Identificación
    numero_documento:   str  = Field(..., min_length=4, max_length=20)
    tipo_documento:     str  = Field(default="CC")
    primer_nombre:      str  = Field(..., min_length=2, max_length=50)
    segundo_nombre:     str | None = Field(default=None, max_length=50)
    primer_apellido:    str  = Field(..., min_length=2, max_length=50)
    segundo_apellido:   str | None = Field(default=None, max_length=50)

    # Demografía clínica (críticos para baremos)
    fecha_nacimiento:   date = Field(..., description="Formato YYYY-MM-DD")
    sexo:               str  = Field(..., description="H=Hombre, M=Mujer")
    escolaridad:        str  = Field(...)
    lateralidad:        str  = Field(default="Diestro")

    # Datos de contacto
    telefono:           str | None = None
    correo:             str | None = Field(default=None, max_length=100)
    direccion:          str | None = None
    ciudad:             str | None = None
    localidad:          str | None = None
    estrato:            int | None = Field(default=None, ge=1, le=6)
    estado_civil:       str | None = None
    lugar_nacimiento:   str | None = None
    ocupacion:          str | None = None
    acompanante:           str | None = None
    acompanante_relacion:  str | None = None
    acompanante_telefono:  str | None = None
    grupo_etnico:          str | None = None

    # Datos de consulta
    profesional_id:     OptionalUUIDStr = None
    fecha_atencion:     date = Field(default_factory=date.today)
    motivo_consulta:    str | None = Field(default=None, max_length=500)
    remite:             str | None = None
    eps:                str | None = None
    orden_medica_no:    str | None = None
    discapacidad:       str | None = None
    codigo_rips:        str | None = Field(default=None, max_length=10)
    cups:               str | None = None
    finalidad_consulta: str | None = None
    numero_sesiones:    int = Field(default=1, ge=1)
    donante:            bool = False

    @field_validator("sexo")
    @classmethod
    def validate_sexo(cls, v: str) -> str:
        if v.upper() not in ("H", "M"):
            raise ValueError("sexo debe ser 'H' o 'M'")
        return v.upper()

    @field_validator("numero_documento")
    @classmethod
    def clean_documento(cls, v: str) -> str:
        return v.strip().replace(" ", "").replace(".", "")

    @field_validator("primer_nombre", "primer_apellido", "segundo_nombre", "segundo_apellido")
    @classmethod
    def title_case_names(cls, v: str | None) -> str | None:
        return v.strip().title() if v else v

    @field_validator(
        "profesional_id", "telefono", "correo", "direccion", "ciudad",
        "localidad", "estado_civil", "lugar_nacimiento", "ocupacion",
        "acompanante", "grupo_etnico", "motivo_consulta", "remite", "eps",
        "orden_medica_no", "discapacidad", "codigo_rips", "cups",
        "finalidad_consulta", mode="before",
    )
    @classmethod
    def empty_str_to_none(cls, v):
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @model_validator(mode="after")
    def validate_dates(self) -> PatientCreateDTO:
        if self.fecha_nacimiento >= self.fecha_atencion:
            raise ValueError("fecha_nacimiento debe ser anterior a fecha_atencion")
        return self

    model_config = {
        "json_schema_extra": {
            "example": {
                "numero_documento": "80189609",
                "tipo_documento": "CC",
                "primer_nombre": "Juan",
                "primer_apellido": "García",
                "fecha_nacimiento": "1990-05-15",
                "sexo": "H",
                "escolaridad": "Profesional",
                "fecha_atencion": "2026-03-20",
                "ciudad": "Bogotá",
                "motivo_consulta": "Dificultades de memoria reportadas por el paciente.",
                "codigo_rips": "F060",
            }
        }
    }


class PatientUpdateDTO(BaseModel):
    """Datos actualizables. PATCH /api/v1/patients/{id}"""
    primer_nombre:      str | None = None
    segundo_nombre:     str | None = None
    primer_apellido:    str | None = None
    segundo_apellido:   str | None = None
    telefono:           str | None = None
    correo:             str | None = None
    ciudad:             str | None = None
    escolaridad:        str | None = None
    motivo_consulta:    str | None = None
    codigo_rips:        str | None = None
    eps:                str | None = None


# ============================================================
# RESPONSE DTOs (lo que la API devuelve al Frontend)
# ============================================================

class AgeResponseDTO(BaseModel):
    """Edad calculada en tiempo real."""
    years:          int
    months:         int
    days:           int
    total_months:   int
    decimal_years:  float
    display:        str
    poblacion:      str
    birth_date:     str
    reference_date: str


class PatientResponseDTO(BaseModel):
    """Respuesta completa de un paciente con edad calculada."""
    id:                 str
    numero_documento:   str
    tipo_documento:     str
    nombre_completo:    str
    fecha_nacimiento:   date
    fecha_atencion:     date
    sexo:               str
    escolaridad:        str
    lateralidad:        str
    ciudad:             str | None
    motivo_consulta:    str | None
    codigo_rips:        str | None
    eps:                str | None

    # Campos calculados por el backend
    age_years:      int
    age_months:     int
    age_display:    str
    poblacion:      str

    model_config = {"from_attributes": True}



class PatientPanelItemDTO(BaseModel):
    """Un paciente en el listado del panel — incluye resumen de evaluaciones."""
    id:                 str
    numero_documento:   str
    tipo_documento:     str
    nombre_completo:    str
    fecha_nacimiento:   date
    fecha_atencion:     date
    sexo:               str
    escolaridad:        str
    ciudad:             str | None
    remite:             str | None
    profesional_id:     str | None
    acompanante:           str | None = None
    acompanante_relacion:  str | None = None
    acompanante_telefono:  str | None = None

    # Calculados
    age_display:        str
    poblacion:          str

    # Evaluaciones (JOIN con tabla evaluations)
    total_evaluaciones: int = 0
    ultima_evaluacion:  str | None = None   # ISO date de la última evaluación
    ultimo_protocolo:   str | None = None   # Ej: "WISC-IV"


class PatientPanelResponseDTO(BaseModel):
    """Respuesta paginada del panel de pacientes."""
    total:      int
    pagina:     int
    por_pagina: int
    pacientes:  list[PatientPanelItemDTO]


class PatientStatsDTO(BaseModel):
    """Estadísticas del dashboard."""
    total_pacientes:       int
    masculino:             int
    femenino:              int
    atendidos_este_mes:    int
    atendidos_este_anio:   int
    total_evaluaciones:    int = 0
    evaluaciones_sin_informe: int = 0
    infantil:              int = 0
    adulto_joven:          int = 0
    adulto_mayor:          int = 0
