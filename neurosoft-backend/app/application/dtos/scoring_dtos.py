"""
app/application/dtos/scoring_dtos.py
=====================================
DTOs para el motor de calificación y generación de reportes.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.core.validators import OptionalUUIDStr, UUIDStr

# ============================================================
# SCORING REQUEST / RESPONSE
# ============================================================

class ScoringRequestDTO(BaseModel):
    """
    Request al motor de calificación.
    POST /api/v1/scores/
    """
    patient_id: UUIDStr = Field(..., description="UUID del paciente registrado.")
    protocolo: str | None = Field(
        default=None,
        description="Nombre del protocolo clínico. Ej: 'WISC-IV Niños'.",
    )
    puntajes: dict[str, Any] = Field(
        ...,
        description=(
            "Diccionario {test_id: puntaje_bruto}. "
            "Usar 9999 para pruebas no realizadas."
        ),
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "patient_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "protocolo": "WISC-IV Niños 6-16",
                "puntajes": {
                    "NiWiscDC": 42,
                    "NiWiscSem": 30,
                    "NiWiscVoc": 35,
                    "NiWISCIndComVer": 25,
                    "NiWISCTot": 86,
                    "NiCDI": 9999,
                },
            }
        }
    }


class ResultadoPruebaDTO(BaseModel):
    """Un resultado estandarizado individual."""
    test_id:          str
    test_nombre:      str
    dominio_cognitivo: str
    puntaje_bruto:    float | None
    puntaje_escalar:  float | None
    tipo_metrica:     str
    interpretacion:   str
    z_equivalente:    float | None
    llave_baremo:     str | None = None
    metadata:         dict[str, Any] = Field(default_factory=dict)


class ScoringResponseDTO(BaseModel):
    """Respuesta completa del motor de calificación."""
    patient_id:         str
    protocolo:          str | None
    poblacion:          str
    edad_display:       str
    fecha_calculo:      str
    resultados:         list[ResultadoPruebaDTO]
    total_pruebas:      int
    pruebas_realizadas: int
    pruebas_sin_dato:   int
    advertencias:       list[str] = Field(default_factory=list)

    # ID del registro persistido en BD (None si no se guardó)
    evaluation_id:      str | None = None

    # Resumen clínico
    puntos_debiles:     list[str] = Field(default_factory=list)
    puntos_fuertes:     list[str] = Field(default_factory=list)


class SingleScoreRequestDTO(BaseModel):
    """Calificación rápida de una prueba individual. POST /api/v1/scores/preview"""
    test_id:        str
    puntaje_bruto:  float
    patient_id:     UUIDStr


# ============================================================
# OBSERVATION DTOs
# ============================================================

class ObservationUpsertDTO(BaseModel):
    """Crear o actualizar observación de un dominio. POST /api/v1/observations"""
    patient_id:    UUIDStr
    evaluation_id: OptionalUUIDStr = None
    dominio:       str = Field(..., description=(
        "apariencia_conducta | atencion_concentracion | memoria | lenguaje | "
        "funciones_ejecutivas | habilidades_visoespaciales | socio_emocional | "
        "impresion_diagnostica | recomendaciones | antecedentes"
    ))
    texto:         str = Field(..., min_length=1, max_length=6000)


class ObservationResponseDTO(BaseModel):
    id:            str
    patient_id:    str
    evaluation_id: str | None
    dominio:       str
    texto:         str
    updated_at:    str


class ObservationsCompleteDTO(BaseModel):
    """Todas las observaciones de un paciente, agrupadas por dominio."""
    patient_id:    str
    evaluation_id: str | None
    observaciones: dict[str, str]


# ============================================================
# REPORT DTOs
# ============================================================

class ReportRequestDTO(BaseModel):
    """
    Solicitud de generación de informe.
    POST /api/v1/reports/word  |  /api/v1/reports/pdf
    """
    patient_id:     UUIDStr
    evaluation_id:  OptionalUUIDStr = None
    formato:        str = Field(default="pdf", description="pdf | docx")
    profesional_id: OptionalUUIDStr = None


class TestInfoDTO(BaseModel):
    """Información de una prueba disponible."""
    test_id:       str
    nombre:        str
    tipo_calculo:  str
    tipo_metrica:  str
    poblacion:     str


# ============================================================
# EVALUATION HISTORY DTOs
# ============================================================

class EvaluationSummaryDTO(BaseModel):
    """Resumen de una evaluación guardada (para listados/panel)."""
    evaluation_id:      str
    protocolo:          str | None
    fecha:              str              # ISO date
    poblacion:          str | None
    edad_display:       str | None
    pruebas_realizadas: int
    pruebas_sin_dato:   int
    is_latest:          bool
    created_at:         str              # ISO datetime

    # Resumen rápido para mostrar en panel
    puntos_debiles:     list[str] = Field(default_factory=list)
    puntos_fuertes:     list[str] = Field(default_factory=list)
    advertencias:       list[str] = Field(default_factory=list)

    # Workflow de firma (Res. 2654 MinSalud: la firma digital cierra la HC).
    # Si `signed_at` no es None, la evaluación está bloqueada.
    signed_at:          str | None = None       # ISO datetime
    signed_by:          str | None = None       # user_id
    signed_by_label:    str | None = None       # nombre visible
    signature_sha256:   str | None = None       # hash del payload firmado


# ============================================================
# SIGNING WORKFLOW
# ============================================================

class SignEvaluationDTO(BaseModel):
    """
    Firma clínica de una evaluación. POST /evaluations/detail/{id}/sign

    Tras firmar:
      - No se puede re-calificar (el use case debe rechazar con 409).
      - No se puede archivar la evaluación (si se implementa).
      - El hash del payload se recalcula al firmar y se guarda como
        prueba de integridad — si alguien edita la BD a mano, el hash
        deja de cuadrar y el frontend muestra "firma inválida".
    """
    model_config = {"extra": "forbid"}

    # La identidad del clínico se toma de request.state.user_id;
    # aquí sólo pedimos una confirmación explícita.
    confirm: bool = Field(
        ...,
        description="Debe ser True. Previene firmar por accidente.",
    )
    note: str | None = Field(
        default=None,
        max_length=500,
        description="Nota opcional al firmar (ej. 'validado por supervisor').",
    )


class SignatureStatusDTO(BaseModel):
    """Estado de firma de una evaluación — para el frontend."""
    evaluation_id:    str
    signed:           bool
    signed_at:        str | None = None
    signed_by:        str | None = None
    signed_by_label:  str | None = None
    signature_sha256: str | None = None
    valid:            bool | None = None      # True si el hash recalculado coincide
    note:             str | None = None


class EvaluationDetailDTO(EvaluationSummaryDTO):
    """Detalle completo de una evaluación (con resultados y puntajes)."""
    patient_id:         str
    puntajes_brutos:    dict[str, Any] = Field(default_factory=dict)
    resultados:         list[ResultadoPruebaDTO] = Field(default_factory=list)


class PatientEvaluationsDTO(BaseModel):
    """Historial de evaluaciones de un paciente."""
    patient_id:         str
    total_evaluaciones: int
    evaluaciones:       list[EvaluationSummaryDTO]
