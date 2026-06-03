"""
app/core/exceptions.py
======================
Jerarquía centralizada de excepciones de dominio.

Principio: cada capa del sistema lanza sus propias excepciones de dominio,
nunca excepciones genéricas de Python. La capa de presentación las captura
y las convierte en respuestas HTTP con el código correcto.

Árbol de excepciones:
    NeuroSoftError (base)
    ├── DomainError
    │   ├── InvalidScoreError        → 422 Unprocessable Entity
    │   ├── PatientAgeOutOfRangeError → 422
    │   ├── BaremoNotFoundError      → 404 Not Found
    │   └── GhostFormulaError        → 422
    ├── ApplicationError
    │   ├── PatientAlreadyExistsError → 409 Conflict
    │   ├── PatientNotFoundError      → 404 Not Found
    │   ├── EvaluationNotFoundError   → 404
    │   └── InvalidProtocolError      → 422
    └── InfrastructureError
        ├── BaremoDatabaseNotLoadedError → 503 Service Unavailable
        ├── ReportGenerationError        → 500 Internal Server Error
        └── DatabaseConnectionError      → 503
"""

from __future__ import annotations

from typing import Any

# ============================================================
# BASE
# ============================================================

class NeuroSoftError(Exception):
    """Base de todas las excepciones del sistema NeuroSoft."""

    def __init__(
        self,
        message: str,
        code: str = "NEUROSOFT_ERROR",
        context: dict[str, Any] | None = None,
        http_status: int = 500,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.context = context or {}
        self.http_status = http_status

    def to_dict(self) -> dict[str, Any]:
        """Serializa la excepción para la respuesta HTTP."""
        return {
            "error": self.code,
            "message": self.message,
            "context": self.context,
        }


# ============================================================
# CAPA DE DOMINIO — Reglas de negocio violadas
# ============================================================

class DomainError(NeuroSoftError):
    """Violación de una regla del dominio clínico."""
    pass


class InvalidScoreError(DomainError):
    """
    El puntaje bruto no es válido para el baremo de la prueba.

    Contexto típico: PD fuera del rango del baremo, tipo de dato incorrecto
    o combinación edad-prueba no soportada.
    """
    def __init__(self, test_id: str, pd: Any, reason: str = ""):
        super().__init__(
            message=f"Puntaje inválido para '{test_id}': PD={pd}. {reason}".strip(),
            code="INVALID_SCORE",
            context={"test_id": test_id, "pd": pd, "reason": reason},
        )


class PatientAgeOutOfRangeError(DomainError):
    """La edad del paciente está fuera del rango soportado por el baremo."""
    def __init__(self, test_id: str, age_years: int, supported_range: str = ""):
        super().__init__(
            message=(
                f"La edad de {age_years} años no está dentro del rango normativo "
                f"de '{test_id}'. Rango soportado: {supported_range or 'no especificado'}"
            ),
            code="AGE_OUT_OF_RANGE",
            context={"test_id": test_id, "age_years": age_years},
        )


class BaremoNotFoundError(DomainError):
    """No se encontró baremo para el test_id solicitado."""
    def __init__(self, test_id: str):
        super().__init__(
            message=f"No existe baremo para la prueba '{test_id}' en BD_NEURO_MAESTRA.json.",
            code="BAREMO_NOT_FOUND",
            context={"test_id": test_id},
        )


class GhostFormulaError(DomainError):
    """Error en el cálculo de una prueba fantasma (TONI-2, Frostig, MIDE)."""
    def __init__(self, test_code: str, reason: str):
        super().__init__(
            message=f"Error en fórmula fantasma '{test_code}': {reason}",
            code="GHOST_FORMULA_ERROR",
            context={"test_code": test_code, "reason": reason},
        )


class UnsupportedStrategyError(DomainError):
    """El tipo de cálculo del baremo no tiene strategy implementada."""
    def __init__(self, tipo_calculo: str):
        super().__init__(
            message=f"No existe strategy para tipo_calculo='{tipo_calculo}'.",
            code="UNSUPPORTED_STRATEGY",
            context={"tipo_calculo": tipo_calculo},
        )


# ============================================================
# CAPA DE APLICACIÓN — Casos de uso fallidos
# ============================================================

class ApplicationError(NeuroSoftError):
    """Error en la orquestación de un caso de uso."""
    pass


class PatientAlreadyExistsError(ApplicationError):
    """Intento de registrar un paciente que ya existe en esa fecha de atención."""
    def __init__(self, numero_documento: str, fecha_atencion: str):
        super().__init__(
            message=(
                f"Ya existe un registro para el documento '{numero_documento}' "
                f"en la fecha {fecha_atencion}. Use el endpoint de edición."
            ),
            code="PATIENT_ALREADY_EXISTS",
            context={"numero_documento": numero_documento, "fecha_atencion": fecha_atencion},
        )


class PatientNotFoundError(ApplicationError):
    """Paciente no encontrado en la base de datos."""
    def __init__(self, identifier: str):
        super().__init__(
            message=f"Paciente '{identifier}' no encontrado.",
            code="PATIENT_NOT_FOUND",
            context={"identifier": identifier},
        )


class EvaluationNotFoundError(ApplicationError):
    """Evaluación no encontrada."""
    def __init__(self, evaluation_id: str):
        super().__init__(
            message=f"Evaluación '{evaluation_id}' no encontrada.",
            code="EVALUATION_NOT_FOUND",
            context={"evaluation_id": evaluation_id},
        )


class InvalidProtocolError(ApplicationError):
    """El protocolo clínico seleccionado no es válido para la población del paciente."""
    def __init__(self, protocol: str, poblacion: str):
        super().__init__(
            message=f"El protocolo '{protocol}' no es válido para población '{poblacion}'.",
            code="INVALID_PROTOCOL",
            context={"protocol": protocol, "poblacion": poblacion},
        )


class EvaluationAlreadySignedError(ApplicationError):
    """
    Se intentó firmar, editar o eliminar una evaluación ya firmada.
    La firma digital cierra la historia clínica (Res. 2654 MinSalud) y
    la evaluación queda inmutable. Para invalidarla hay que crear una
    nueva evaluación del mismo protocolo (no sobreescribir la firmada).
    """
    def __init__(self, evaluation_id: str, signed_at: str | None = None):
        super().__init__(
            message=(
                f"La evaluación '{evaluation_id}' ya fue firmada digitalmente "
                f"{f'el {signed_at}' if signed_at else ''} y no puede modificarse. "
                "Cree una evaluación nueva si necesita re-calificar."
            ).strip(),
            code="EVALUATION_ALREADY_SIGNED",
            context={"evaluation_id": evaluation_id, "signed_at": signed_at},
            http_status=409,
        )


class EvaluationNotSignedError(ApplicationError):
    """Operación que requiere firma previa sobre una evaluación no firmada."""
    def __init__(self, evaluation_id: str):
        super().__init__(
            message=f"La evaluación '{evaluation_id}' no ha sido firmada todavía.",
            code="EVALUATION_NOT_SIGNED",
            context={"evaluation_id": evaluation_id},
            http_status=409,
        )


# ============================================================
# CAPA DE INFRAESTRUCTURA — Fallas externas
# ============================================================

class InfrastructureError(NeuroSoftError):
    """Error en una dependencia externa (BD, sistema de archivos)."""
    pass


class BaremoDatabaseNotLoadedError(InfrastructureError):
    """El JSON de baremos no pudo ser cargado al iniciar la aplicación."""
    def __init__(self, path: str):
        super().__init__(
            message=(
                f"BD_NEURO_MAESTRA.json no encontrado en '{path}'. "
                "Copia el archivo a la carpeta 'data/' y reinicia el servidor."
            ),
            code="BAREMO_DB_NOT_LOADED",
            context={"path": path},
        )


class ReportGenerationError(InfrastructureError):
    """Error al generar un reporte PDF o Word."""
    def __init__(self, format_: str, reason: str):
        super().__init__(
            message=f"Error al generar reporte {format_.upper()}: {reason}",
            code="REPORT_GENERATION_ERROR",
            context={"format": format_, "reason": reason},
        )


class DatabaseConnectionError(InfrastructureError):
    """Error de conexión con la base de datos SQLite."""
    def __init__(self, reason: str):
        super().__init__(
            message=f"Error de base de datos: {reason}",
            code="DATABASE_ERROR",
            context={"reason": reason},
        )


class ConcurrencyError(ApplicationError):
    """
    Optimistic locking conflict.
    Ocurre cuando dos usuarios intentan guardar el mismo registro simultáneamente.
    El cliente debe recargar los datos y reintentar.
    """
    def __init__(self, resource: str = "registro", client_version: int = 0, server_version: int = 0):
        super().__init__(
            message=(
                f"El {resource} fue modificado por otro usuario. "
                f"Tu versión: {client_version}, versión actual: {server_version}. "
                "Recarga la página y vuelve a intentarlo."
            ),
            code="CONCURRENCY_CONFLICT",
            http_status=409,
        )
        self.client_version = client_version
        self.server_version = server_version
