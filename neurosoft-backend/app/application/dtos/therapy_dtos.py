from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

# ═════════════════════════════════════════════════════════════
# DTOs — Plan terapéutico
# ═════════════════════════════════════════════════════════════


class ObjectiveCreateDTO(BaseModel):
    descripcion: str = Field(..., min_length=3)
    criterios_medibles: str | None = None
    fecha_meta: datetime | None = None
    orden: int = 0


class ObjectiveResponseDTO(BaseModel):
    id: str
    plan_id: str
    descripcion: str
    criterios_medibles: str | None
    fecha_inicio: datetime
    fecha_meta: datetime | None
    estado: str
    progreso_pct: int
    orden: int


class TherapyPlanCreateDTO(BaseModel):
    patient_id: str
    profesional_id: str | None = None
    enfoque_principal: str | None = None
    diagnostico_principal: str | None = None
    diagnostico_secundario: str | None = None
    codigo_cie11: str | None = None
    motivo_consulta: str | None = None
    duracion_estimada_sesiones: int | None = None
    fecha_revision: datetime | None = None
    objetivos: list[ObjectiveCreateDTO] = []


class TherapyPlanResponseDTO(BaseModel):
    id: str
    patient_id: str
    profesional_id: str | None
    enfoque_principal: str | None
    diagnostico_principal: str | None
    diagnostico_secundario: str | None
    codigo_cie11: str | None = None
    motivo_consulta: str | None
    duracion_estimada_sesiones: int | None
    fecha_inicio: datetime
    fecha_revision: datetime | None
    fecha_cierre: datetime | None
    motivo_cierre: str | None
    estado: str
    objetivos: list[ObjectiveResponseDTO] = []


class TherapyPlanUpdateDTO(BaseModel):
    """Solo campos modificables después de creado."""

    fecha_revision: datetime | None = None
    fecha_cierre: datetime | None = None
    motivo_cierre: Literal["alta", "abandono", "derivacion", "cambio_terapeuta"] | None = None
    nota_cierre: str | None = None
    estado: Literal["activo", "pausado", "cerrado"] | None = None
    duracion_estimada_sesiones: int | None = None


# ═════════════════════════════════════════════════════════════
# DTOs — Sesión terapéutica
# ═════════════════════════════════════════════════════════════


class TherapySessionCreateDTO(BaseModel):
    patient_id: str
    plan_id: str | None = None
    profesional_id: str | None = None
    fecha: datetime | None = None
    duracion_min: int = 50
    modalidad: Literal["presencial", "telepsicologia", "telefonica"] = "presencial"
    enfoque_sesion: str | None = None
    soap_subjetivo: str | None = None
    soap_objetivo: str | None = None
    soap_analisis: str | None = None
    soap_plan: str | None = None
    objetivos_trabajados: str | None = None
    tareas_asignadas: str | None = None
    medicacion_actual: str | None = None
    riesgo_suicida: Literal["ninguno", "ideacion_pasiva", "ideacion_activa", "plan", "intento_reciente"] = "ninguno"
    riesgo_observaciones: str | None = None
    alianza_terapeutica: int | None = Field(None, ge=1, le=5)
    estado_emocional_ini: int | None = Field(None, ge=0, le=10)
    estado_emocional_fin: int | None = Field(None, ge=0, le=10)


class TherapySessionResponseDTO(BaseModel):
    id: str
    plan_id: str | None
    patient_id: str
    profesional_id: str | None
    fecha: datetime
    duracion_min: int
    modalidad: str
    enfoque_sesion: str | None
    soap_subjetivo: str | None
    soap_objetivo: str | None
    soap_analisis: str | None
    soap_plan: str | None
    objetivos_trabajados: str | None
    tareas_asignadas: str | None
    medicacion_actual: str | None
    riesgo_suicida: str
    riesgo_observaciones: str | None
    alianza_terapeutica: int | None
    estado_emocional_ini: int | None
    estado_emocional_fin: int | None
    locked_at: datetime | None
    locked_by: str | None
    created_at: datetime
    updated_at: datetime


class TherapySessionUpdateDTO(BaseModel):
    """Campos modificables mientras la sesión NO esté lockeada."""

    modalidad: Literal["presencial", "telepsicologia", "telefonica"] | None = None
    duracion_min: int | None = Field(None, ge=5, le=240)
    soap_subjetivo: str | None = None
    soap_objetivo: str | None = None
    soap_analisis: str | None = None
    soap_plan: str | None = None
    objetivos_trabajados: str | None = None
    tareas_asignadas: str | None = None
    medicacion_actual: str | None = None
    riesgo_suicida: str | None = None
    riesgo_observaciones: str | None = None
    alianza_terapeutica: int | None = Field(None, ge=1, le=5)
    estado_emocional_ini: int | None = Field(None, ge=0, le=10)
    estado_emocional_fin: int | None = Field(None, ge=0, le=10)


# ═════════════════════════════════════════════════════════════
# DTOs — Evaluación de riesgo
# ═════════════════════════════════════════════════════════════


class RiskAssessmentCreateDTO(BaseModel):
    patient_id: str
    session_id: str | None = None
    profesional_id: str | None = None
    instrumento: str = "c_ssrs"
    nivel: Literal["ninguno", "leve", "moderado", "alto", "inminente"]
    ideacion_suicida: bool = False
    ideacion_con_plan: bool = False
    intento_previo: bool = False
    intento_reciente_30d: bool = False
    factores_protectores: str | None = None
    factores_riesgo: str | None = None
    plan_seguridad: str | None = None
    derivacion_emergencia: bool = False
    nota_clinica: str | None = None


class RiskAssessmentResponseDTO(BaseModel):
    id: str
    patient_id: str
    session_id: str | None
    profesional_id: str | None
    fecha: datetime
    instrumento: str
    nivel: str
    ideacion_suicida: bool
    ideacion_con_plan: bool
    intento_previo: bool
    intento_reciente_30d: bool
    factores_protectores: str | None
    factores_riesgo: str | None
    plan_seguridad: str | None
    derivacion_emergencia: bool
    nota_clinica: str | None


# ═════════════════════════════════════════════════════════════
# DTOs — Tareas terapéuticas
# ═════════════════════════════════════════════════════════════

TASK_TIPOS = Literal[
    "registro_pensamientos",
    "registro_emocional",
    "autorregistro_conducta",
    "exposicion",
    "activacion_conductual",
    "habilidades_DBT",
    "psicoeducacion",
    "libre",
]
TASK_ESTADOS = Literal["pendiente", "en_progreso", "completada", "parcial", "omitida"]
TASK_FRECUENCIAS = Literal["diaria", "varias_semana", "semanal", "unica"]


class TherapyTaskCreateDTO(BaseModel):
    patient_id: str
    plan_id: str | None = None
    session_id: str | None = None
    profesional_id: str | None = None
    objetivo_id: str | None = None
    tipo: TASK_TIPOS = "libre"
    titulo: str = Field(..., min_length=3, max_length=120)
    descripcion: str | None = None
    fecha_limite: datetime | None = None
    frecuencia: TASK_FRECUENCIAS | None = None


class TherapyTaskUpdateDTO(BaseModel):
    estado: TASK_ESTADOS | None = None
    respuesta: str | None = None
    adherencia_pct: int | None = Field(None, ge=0, le=100)
    dificultad_pct: int | None = Field(None, ge=0, le=100)
    utilidad_pct: int | None = Field(None, ge=0, le=100)
    nota_clinico: str | None = None
    revisar: bool = False
    completar: bool = False


class TherapyTaskResponseDTO(BaseModel):
    id: str
    patient_id: str
    plan_id: str | None
    session_id: str | None
    profesional_id: str | None
    objetivo_id: str | None
    tipo: str
    titulo: str
    descripcion: str | None
    fecha_asignacion: datetime
    fecha_limite: datetime | None
    frecuencia: str | None
    estado: str
    completada_en: datetime | None
    respuesta: str | None
    adherencia_pct: int | None
    dificultad_pct: int | None
    utilidad_pct: int | None
    revisada_en: datetime | None
    nota_clinico: str | None
    created_at: datetime
    updated_at: datetime | None
