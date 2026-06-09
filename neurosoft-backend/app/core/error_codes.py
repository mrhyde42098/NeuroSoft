"""
Mapeo único código de error NeuroSoft → HTTP status.
Usado por el handler global en main.py.
"""

from __future__ import annotations

from app.core.exceptions import ApplicationError, DomainError, InfrastructureError, NeuroSoftError

HTTP_STATUS_BY_CODE: dict[str, int] = {
    "PATIENT_ALREADY_EXISTS": 409,
    "PATIENT_NOT_FOUND": 404,
    "EVALUATION_NOT_FOUND": 404,
    "EVALUATION_ALREADY_SIGNED": 409,
    "EVALUATION_NOT_SIGNED": 409,
    "CONCURRENCY_CONFLICT": 409,
    "BAREMO_NOT_FOUND": 404,
    "INVALID_PROTOCOL": 422,
    "INVALID_SCORE": 422,
    "AGE_OUT_OF_RANGE": 422,
    "GHOST_FORMULA_ERROR": 422,
    "UNSUPPORTED_STRATEGY": 422,
    "BAREMO_DB_NOT_LOADED": 503,
    "DATABASE_ERROR": 503,
    "REPORT_GENERATION_ERROR": 500,
}

# Mensajes legibles para el frontend (español)
USER_MESSAGES_ES: dict[str, str] = {
    "PATIENT_ALREADY_EXISTS": "Ya existe un paciente con ese documento en la fecha indicada.",
    "PATIENT_NOT_FOUND": "Paciente no encontrado.",
    "EVALUATION_NOT_FOUND": "Evaluación no encontrada.",
    "EVALUATION_ALREADY_SIGNED": "La evaluación ya está firmada y no puede modificarse.",
    "EVALUATION_NOT_SIGNED": "La evaluación aún no ha sido firmada.",
    "CONCURRENCY_CONFLICT": "Otro usuario modificó este registro. Recargue e intente de nuevo.",
    "BAREMO_NOT_FOUND": "No hay baremo disponible para esta prueba.",
    "INVALID_SCORE": "Puntaje inválido para esta prueba.",
    "AGE_OUT_OF_RANGE": "La edad del paciente está fuera del rango normativo.",
    "BAREMO_DB_NOT_LOADED": "Base de baremos no cargada. Reinicie el servidor.",
    "DATABASE_ERROR": "Error de base de datos. Intente de nuevo.",
    "REPORT_GENERATION_ERROR": "No se pudo generar el informe.",
}


def resolve_http_status(exc: NeuroSoftError) -> int:
    explicit = getattr(exc, "http_status", None)
    if explicit is not None and explicit != 500:
        return explicit
    mapped = HTTP_STATUS_BY_CODE.get(exc.code)
    if mapped is not None:
        return mapped
    if isinstance(exc, InfrastructureError):
        return 503
    if isinstance(exc, (DomainError, ApplicationError)):
        return 422
    return 500
