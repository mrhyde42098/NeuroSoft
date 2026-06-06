"""
app/presentation/api/v1/scores.py
====================================
Endpoints del Motor de Calificación.

Endpoints:
    POST   /scores/          → Calificar evaluación completa
    POST   /scores/preview   → Calificar una prueba individual (debug/UX)
    GET    /scores/tests      → Catálogo de pruebas disponibles
    POST   /observations/     → Guardar observación clínica
    GET    /observations/{id} → Obtener observaciones de un paciente
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, status

from app.application.dtos.scoring_dtos import (
    ObservationResponseDTO,
    ObservationsCompleteDTO,
    ObservationUpsertDTO,
    ResultadoPruebaDTO,
    ScoringRequestDTO,
    ScoringResponseDTO,
    SingleScoreRequestDTO,
    TestInfoDTO,
)
from app.core.exceptions import (
    ApplicationError,
    BaremoDatabaseNotLoadedError,
    DomainError,
    PatientNotFoundError,
)
from app.presentation.api.v1.auth import CurrentUser, get_patient_for_user
from app.presentation.dependencies import (
    DbSession,
    GetObsUC,
    ListTestsUC,
    ScoreEvalUC,
    ScorePreviewUC,
    UpsertObsUC,
)

scores_router = APIRouter(prefix="/scores", tags=["Motor de Calificación"])
observations_router = APIRouter(prefix="/observations", tags=["Observaciones Clínicas"])


def _handle(e: Exception):
    if isinstance(e, PatientNotFoundError):
        raise HTTPException(status_code=404, detail=e.to_dict())
    if isinstance(e, BaremoDatabaseNotLoadedError):
        raise HTTPException(status_code=503, detail=e.to_dict())
    if isinstance(e, (DomainError, ApplicationError)):
        raise HTTPException(status_code=422, detail=e.to_dict())
    raise e


# ──────────────────────────────────────────────────────────────
# MOTOR DE BAREMOS
# ──────────────────────────────────────────────────────────────


@scores_router.post(
    "/",
    response_model=ScoringResponseDTO,
    summary="Calificar evaluación neuropsicológica completa",
    description=(
        "Recibe los puntajes brutos (PD) y devuelve puntajes estandarizados "
        "(PE, CI, T, Z), interpretaciones cualitativas y perfil Z. "
        "Usa 9999 para pruebas no realizadas."
    ),
)
def score_evaluation(
    dto: ScoringRequestDTO,
    uc: ScoreEvalUC,
    db: DbSession,
    user: CurrentUser,
) -> ScoringResponseDTO:
    get_patient_for_user(dto.patient_id, db, user)
    try:
        return uc.execute(dto)
    except Exception as e:
        _handle(e)


@scores_router.post(
    "/preview",
    response_model=Optional[ResultadoPruebaDTO],
    summary="Calificar una prueba individual",
    description=(
        "Califica un solo test sin persistir. Útil para el frontend reactivo "
        "(mostrar el puntaje estandarizado mientras el clínico escribe el PD)."
    ),
)
def score_preview(
    dto: SingleScoreRequestDTO,
    uc: ScorePreviewUC,
    db: DbSession,
    user: CurrentUser,
) -> ResultadoPruebaDTO | None:
    get_patient_for_user(dto.patient_id, db, user)
    try:
        return uc.execute(dto)
    except Exception as e:
        _handle(e)


@scores_router.get(
    "/tests",
    response_model=list[TestInfoDTO],
    summary="Catálogo de pruebas disponibles",
    description="Devuelve todas las pruebas del sistema, filtrable por población clínica.",
)
def list_tests(
    poblacion: str | None = Query(
        default=None,
        description="infantil | adulto_joven | adulto_mayor",
    ),
    uc: ListTestsUC = ...,
) -> list[TestInfoDTO]:
    try:
        return uc.execute(poblacion)
    except Exception as e:
        _handle(e)


# ──────────────────────────────────────────────────────────────
# OBSERVACIONES CLÍNICAS
# ──────────────────────────────────────────────────────────────


@observations_router.post(
    "/",
    response_model=ObservationResponseDTO,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar observación clínica",
    description=(
        "Guarda o sobreescribe el texto de un dominio cognitivo. Un paciente tiene un texto por dominio por evaluación."
    ),
)
def upsert_observation(
    dto: ObservationUpsertDTO,
    uc: UpsertObsUC,
    db: DbSession,
    user: CurrentUser,
) -> ObservationResponseDTO:
    get_patient_for_user(dto.patient_id, db, user)
    try:
        return uc.execute(dto)
    except Exception as e:
        _handle(e)


@observations_router.get(
    "/{patient_id}",
    response_model=ObservationsCompleteDTO,
    summary="Obtener observaciones de un paciente",
    description="Retorna todas las observaciones agrupadas por dominio. Listas para el informe.",
)
def get_observations(
    patient_id: str,
    user: CurrentUser,
    db: DbSession,
    evaluation_id: str | None = Query(default=None),
    uc: GetObsUC = ...,
) -> ObservationsCompleteDTO:
    get_patient_for_user(patient_id, db, user)
    return uc.execute(patient_id, evaluation_id)


# ── CURVA DE MEMORIA GROBER ───────────────────────────────────


@scores_router.get(
    "/grober-curve/{patient_id}",
    summary="Curva de Memoria Grober",
    description=(
        "Retorna los datos de la curva de aprendizaje y memoria Grober "
        "para un paciente, usando su última evaluación disponible. "
        "Incluye valores del paciente y valores normativos de control "
        "para graficar LE1→LE2→LE3→ML→CE1→CE2→CE3→MC→Rcto."
    ),
)
def get_grober_curve(
    patient_id: str,
    db: DbSession,
    user: CurrentUser,
):
    """
    Construye la curva de memoria Grober para el frontend.
    Busca la última evaluación del paciente con pruebas Grober.
    """
    import json

    from sqlalchemy import desc

    from app.infrastructure.database.orm_models import EvaluationORM

    get_patient_for_user(patient_id, db, user)

    # Pruebas Grober en orden de la curva
    GROBER_SEQUENCE = [
        ("ViGroberRLT", "LE1", "Libre Ensayo 1"),
        ("ViGroberLE2", "LE2", "Libre Ensayo 2"),
        ("ViGroberLE3", "LE3", "Libre Ensayo 3"),
        ("ViGroberML_Tot", "ML", "Memoria Libre"),
        ("ViGroberCE1", "CE1", "Clave Ensayo 1"),
        ("ViGroberCE2", "CE2", "Clave Ensayo 2"),
        ("ViGroberCE3", "CE3", "Clave Ensayo 3"),
        ("ViGroberMC_Tot", "MC", "Memoria por Claves"),
        ("ViGroberRco", "Rcto", "Reconocimiento"),
    ]

    # Rango normal (percentil 50, sujetos controles adultos mayor)
    # Basado en normativa Grober & Buschke Colombia
    GROBER_CONTROL = {"LE1": 9, "LE2": 11, "LE3": 13, "ML": 13, "CE1": 13, "CE2": 15, "CE3": 15, "MC": 15, "Rcto": 16}

    # Buscar última evaluación del paciente con pruebas Grober
    evaluations = (
        db.query(EvaluationORM)
        .filter(EvaluationORM.patient_id == patient_id)
        .order_by(desc(EvaluationORM.fecha), desc(EvaluationORM.created_at))
        .limit(10)
        .all()
    )

    patient_values = {}
    eval_used = None

    for ev in evaluations:
        try:
            puntajes = json.loads(ev.puntajes_brutos_json or "{}")
            if any(tid in puntajes for tid, _, _ in GROBER_SEQUENCE):
                patient_values = puntajes
                eval_used = ev
                break
        except Exception:
            continue

    # Construir puntos de la curva
    puntos_paciente = []
    puntos_control = []

    resultados_map = {}
    if eval_used:
        try:
            resultados = json.loads(eval_used.resultados_json or "[]")
            resultados_map = {r.get("test_id"): r for r in resultados}
        except (json.JSONDecodeError, TypeError, AttributeError):
            # resultados_json corrupto o ausente — usar dict vacio
            pass

    for tid, abrev, nombre in GROBER_SEQUENCE:
        pd_val = patient_values.get(tid)
        ctrl = GROBER_CONTROL[abrev]
        res = resultados_map.get(tid, {})
        esc = res.get("puntaje_escalar")

        puntos_paciente.append(
            {
                "punto": abrev,
                "nombre": nombre,
                "pd": pd_val,
                "escalar": esc,
                "interpretacion": res.get("interpretacion", "Sin dato"),
            }
        )
        puntos_control.append({"punto": abrev, "valor": ctrl})

    return {
        "patient_id": patient_id,
        "eval_id": eval_used.id if eval_used else None,
        "fecha": eval_used.fecha.isoformat() if eval_used and eval_used.fecha else None,
        "tiene_datos": eval_used is not None,
        "secuencia": [a for _, a, _ in GROBER_SEQUENCE],
        "paciente": puntos_paciente,
        "control": puntos_control,
        "nota": (
            "Curva de aprendizaje: LE1→LE2→LE3 (ensayos libres), ML (memoria libre inmediata), "
            "CE1→CE2→CE3 (ensayos por claves), MC (memoria por claves), Rcto (reconocimiento)."
        ),
    }
