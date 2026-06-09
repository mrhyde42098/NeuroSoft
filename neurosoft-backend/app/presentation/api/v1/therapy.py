"""
Endpoints del módulo de psicología clínica (sesiones terapéuticas).
Thin controller — lógica en therapy_use_cases + therapy_repo.
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.application.dtos.therapy_dtos import (
    RiskAssessmentCreateDTO,
    RiskAssessmentResponseDTO,
    TherapyPlanCreateDTO,
    TherapyPlanResponseDTO,
    TherapyPlanUpdateDTO,
    TherapySessionCreateDTO,
    TherapySessionResponseDTO,
    TherapySessionUpdateDTO,
    TherapyTaskCreateDTO,
    TherapyTaskResponseDTO,
    TherapyTaskUpdateDTO,
)
from app.presentation.api.v1.auth import CurrentUser
from app.presentation.dependencies import (
    ArchiveTherapyTaskUC,
    CreateRiskAssessmentUC,
    CreateTherapyPlanUC,
    CreateTherapySessionUC,
    CreateTherapyTaskUC,
    GetTherapyPlanUC,
    GetTherapySessionUC,
    GetTherapyTaskUC,
    ListRiskAssessmentsUC,
    ListTherapyPlansUC,
    ListTherapySessionsUC,
    ListTherapyTasksUC,
    LockTherapySessionUC,
    TherapyTaskSummaryUC,
    UpdateTherapyPlanUC,
    UpdateTherapySessionUC,
    UpdateTherapyTaskUC,
)

therapy_router = APIRouter(prefix="/therapy", tags=["💚 Psicología Clínica"])


# ── Planes ───────────────────────────────────────────────────


@therapy_router.get(
    "/plans", response_model=list[TherapyPlanResponseDTO], summary="Listar planes terapéuticos de un paciente"
)
def list_plans(
    _u: CurrentUser,
    uc: ListTherapyPlansUC,
    patient_id: str = Query(..., description="UUID del paciente"),
):
    return uc.execute(patient_id)


@therapy_router.post(
    "/plans",
    response_model=TherapyPlanResponseDTO,
    status_code=201,
    summary="Crear plan terapéutico (con objetivos opcionales)",
)
def create_plan(dto: TherapyPlanCreateDTO, uc: CreateTherapyPlanUC, user: CurrentUser):
    return uc.execute(dto, profesional_id=user.profesional_id)


@therapy_router.get("/plans/{plan_id}", response_model=TherapyPlanResponseDTO, summary="Detalle de un plan terapéutico")
def get_plan(plan_id: str, uc: GetTherapyPlanUC, _u: CurrentUser):
    return uc.execute(plan_id)


@therapy_router.patch(
    "/plans/{plan_id}", response_model=TherapyPlanResponseDTO, summary="Actualizar plan (cerrar, cambiar estado, etc.)"
)
def update_plan(plan_id: str, dto: TherapyPlanUpdateDTO, uc: UpdateTherapyPlanUC, _u: CurrentUser):
    return uc.execute(plan_id, dto)


# ── Sesiones ─────────────────────────────────────────────────


@therapy_router.get(
    "/sessions", response_model=list[TherapySessionResponseDTO], summary="Listar sesiones terapéuticas de un paciente"
)
def list_sessions(
    _u: CurrentUser,
    uc: ListTherapySessionsUC,
    patient_id: str = Query(...),
    plan_id: str | None = Query(None),
):
    return uc.execute(patient_id, plan_id)


@therapy_router.post(
    "/sessions",
    response_model=TherapySessionResponseDTO,
    status_code=201,
    summary="Crear sesión terapéutica (notas SOAP)",
)
def create_session(dto: TherapySessionCreateDTO, uc: CreateTherapySessionUC, user: CurrentUser):
    return uc.execute(dto, profesional_id=user.profesional_id)


@therapy_router.get(
    "/sessions/{session_id}", response_model=TherapySessionResponseDTO, summary="Detalle de una sesión terapéutica"
)
def get_session_detail(session_id: str, uc: GetTherapySessionUC, _u: CurrentUser):
    return uc.execute(session_id)


@therapy_router.patch(
    "/sessions/{session_id}",
    response_model=TherapySessionResponseDTO,
    summary="Actualizar sesión (solo si NO está lockeada)",
)
def update_session(session_id: str, dto: TherapySessionUpdateDTO, uc: UpdateTherapySessionUC, _u: CurrentUser):
    return uc.execute(session_id, dto)


@therapy_router.post(
    "/sessions/{session_id}/lock",
    response_model=TherapySessionResponseDTO,
    summary="Firmar (lockear) sesión — irreversible",
)
def lock_session(session_id: str, uc: LockTherapySessionUC, user: CurrentUser):
    return uc.execute(session_id, user_id=user.id)


# ── Evaluación de riesgo ─────────────────────────────────────


@therapy_router.post(
    "/risk-assessments",
    response_model=RiskAssessmentResponseDTO,
    status_code=201,
    summary="Registrar evaluación de riesgo suicida",
)
def create_risk_assessment(dto: RiskAssessmentCreateDTO, uc: CreateRiskAssessmentUC, user: CurrentUser):
    return uc.execute(dto, profesional_id=user.profesional_id)


@therapy_router.get(
    "/risk-assessments",
    response_model=list[RiskAssessmentResponseDTO],
    summary="Historial de evaluaciones de riesgo de un paciente",
)
def list_risk_assessments(
    _u: CurrentUser,
    uc: ListRiskAssessmentsUC,
    patient_id: str = Query(...),
):
    return uc.execute(patient_id)


# ── Tareas terapéuticas ──────────────────────────────────────


@therapy_router.post(
    "/tasks", response_model=TherapyTaskResponseDTO, status_code=201, summary="Asigna una tarea terapéutica al paciente"
)
def create_task(dto: TherapyTaskCreateDTO, uc: CreateTherapyTaskUC, _u: CurrentUser):
    return uc.execute(dto)


@therapy_router.get(
    "/tasks",
    response_model=list[TherapyTaskResponseDTO],
    summary="Lista tareas de un paciente (opcionalmente filtradas)",
)
def list_tasks(
    _u: CurrentUser,
    uc: ListTherapyTasksUC,
    patient_id: str = Query(...),
    estado: str | None = Query(None, description="Filtrar por estado"),
    plan_id: str | None = Query(None),
    session_id: str | None = Query(None),
    incluir_archivadas: bool = Query(False),
):
    return uc.execute(
        patient_id,
        estado=estado,
        plan_id=plan_id,
        session_id=session_id,
        incluir_archivadas=incluir_archivadas,
    )


@therapy_router.get(
    "/tasks/{task_id}", response_model=TherapyTaskResponseDTO, summary="Detalle de una tarea terapéutica"
)
def get_task(task_id: str, uc: GetTherapyTaskUC, _u: CurrentUser):
    return uc.execute(task_id)


@therapy_router.patch(
    "/tasks/{task_id}",
    response_model=TherapyTaskResponseDTO,
    summary="Actualiza estado / respuesta / revisión clínica de una tarea",
)
def update_task(task_id: str, dto: TherapyTaskUpdateDTO, uc: UpdateTherapyTaskUC, _u: CurrentUser):
    return uc.execute(task_id, dto)


@therapy_router.delete("/tasks/{task_id}", status_code=204, summary="Archiva una tarea (soft-delete)")
def archive_task(task_id: str, uc: ArchiveTherapyTaskUC, _u: CurrentUser):
    uc.execute(task_id)
    return None


@therapy_router.get("/tasks/{patient_id}/summary", summary="Resumen de adherencia a tareas terapéuticas")
def task_summary(patient_id: str, uc: TherapyTaskSummaryUC, _u: CurrentUser):
    return uc.execute(patient_id)
