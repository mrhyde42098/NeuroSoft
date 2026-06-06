"""
app/application/dtos/rehab_dtos.py
====================================
DTOs del módulo de rehabilitación neuropsicológica.

Cubren:
  - Catálogo de actividades disponibles
  - Plan de intervención (CRUD + firma)
  - Sesiones registradas por el paciente o el clínico
  - Links públicos para que el paciente practique en casa
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any

from pydantic import BaseModel, Field

# ─────────────────────────────────────────────────────────────
# CATÁLOGO
# ─────────────────────────────────────────────────────────────


class RehabActivityDTO(BaseModel):
    id: str
    slug: str
    nombre: str
    dominio: str
    dificultad_default: int
    duracion_min: int
    descripcion: str | None = None
    instrucciones: str | None = None
    parametros_default: dict[str, Any] | None = None
    provider: str = "internal"
    external_url: str | None = None
    activo: bool = True
    orden: int = 0


# ─────────────────────────────────────────────────────────────
# PLAN
# ─────────────────────────────────────────────────────────────


class RehabPlanCreateDTO(BaseModel):
    """Crea un plan en estado 'borrador' (modificable hasta firmarse)."""

    patient_id: str
    evaluation_id: str | None = None
    profesional_id: str | None = None
    fecha_inicio: date
    fecha_fin_estimada: date | None = None
    frecuencia_semanal: int = Field(default=2, ge=1, le=14)
    objetivos: str | None = Field(default=None, max_length=2000)
    dominios: list[str] = Field(default_factory=list)
    actividades: list[dict[str, Any]] = Field(default_factory=list)
    notas: str | None = Field(default=None, max_length=2000)


class RehabPlanUpdateDTO(BaseModel):
    """Edición parcial del plan mientras NO esté firmado."""

    fecha_fin_estimada: date | None = None
    frecuencia_semanal: int | None = Field(default=None, ge=1, le=14)
    objetivos: str | None = None
    dominios: list[str] | None = None
    actividades: list[dict[str, Any]] | None = None
    notas: str | None = None
    estado: str | None = None  # activo | pausado | finalizado


class RehabPlanResponseDTO(BaseModel):
    id: str
    patient_id: str
    evaluation_id: str | None = None
    profesional_id: str | None = None
    fecha_inicio: date
    fecha_fin_estimada: date | None = None
    frecuencia_semanal: int
    objetivos: str | None = None
    dominios: list[str] = Field(default_factory=list)
    actividades: list[dict[str, Any]] = Field(default_factory=list)
    notas: str | None = None
    estado: str
    created_at: datetime
    updated_at: datetime | None = None
    signed_at: datetime | None = None
    signed_by: str | None = None
    signed_by_label: str | None = None
    signature_sha256: str | None = None


class RehabSignDTO(BaseModel):
    confirm: bool = Field(..., description="Confirmar la firma con true.")
    note: str | None = Field(default=None, max_length=500)


# ─────────────────────────────────────────────────────────────
# SESIÓN
# ─────────────────────────────────────────────────────────────


class RehabSessionCreateDTO(BaseModel):
    plan_id: str | None = None
    activity_slug: str
    patient_id: str
    parametros: dict[str, Any] | None = None
    resultado: dict[str, Any]  # score, aciertos, errores, RT, etc.
    duracion_seg: int | None = None
    modo: str = Field(default="en_consulta")
    notas_clinico: str | None = Field(default=None, max_length=1000)


class RehabSessionResponseDTO(BaseModel):
    id: str
    plan_id: str | None = None
    activity_id: str
    activity_slug: str
    patient_id: str
    ts_inicio: datetime
    ts_fin: datetime | None = None
    duracion_seg: int | None = None
    score: int | None = None
    aciertos: int | None = None
    errores: int | None = None
    parametros: dict[str, Any] | None = None
    resultado: dict[str, Any] | None = None
    modo: str
    origen_token: str | None = None


# ─────────────────────────────────────────────────────────────
# COMPARTIR (link público para tarea-casa)
# ─────────────────────────────────────────────────────────────


class RehabShareCreateDTO(BaseModel):
    plan_id: str
    expires_in_days: int = Field(default=14, ge=1, le=180)


class RehabShareResponseDTO(BaseModel):
    id: str
    token: str
    plan_id: str
    patient_id: str
    expires_at: datetime
    revoked: bool
    sessions_count: int
    public_url: str  # URL relativa para compartir con el paciente


# ─────────────────────────────────────────────────────────────
# VISTA PÚBLICA (lo que ve el paciente)
# ─────────────────────────────────────────────────────────────


class RehabPublicPlanDTO(BaseModel):
    """
    Lo MÍNIMO que necesita el paciente para realizar las actividades.
    Se omite info clínica sensible (objetivos terapéuticos, evaluación,
    diagnósticos). Solo el set de actividades y sus parámetros.
    """

    plan_id: str
    patient_first_name: str | None = None
    actividades: list[dict[str, Any]]
    expires_at: datetime


class RehabPublicResultDTO(BaseModel):
    """Resultado que envía el paciente desde el viewer público."""

    activity_slug: str
    parametros: dict[str, Any] | None = None
    resultado: dict[str, Any]
    duracion_seg: int | None = None
