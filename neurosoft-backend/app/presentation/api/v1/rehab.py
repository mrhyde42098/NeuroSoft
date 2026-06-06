"""
app/presentation/api/v1/rehab.py
==================================
Endpoints del módulo de rehabilitación neuropsicológica.

Bloques:
  • /rehab/activities                       — catálogo
  • /rehab/plans, /rehab/plans/{id}         — CRUD del plan
  • /rehab/plans/{id}/sign                  — firma del plan
  • /rehab/plans/{id}/share                 — generar link público
  • /rehab/sessions                         — registrar sesión (clínica)
  • /rehab/sessions/by-patient/{patient_id} — listado de sesiones

Endpoints públicos (sin auth, viven en otro router para que el
middleware auth NO los proteja):
  • GET  /api/v1/public/rehab/{token}
  • POST /api/v1/public/rehab/{token}/result
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from app.application.dtos.rehab_dtos import (
    RehabActivityDTO,
    RehabPlanCreateDTO,
    RehabPlanResponseDTO,
    RehabPlanUpdateDTO,
    RehabPublicPlanDTO,
    RehabPublicResultDTO,
    RehabSessionCreateDTO,
    RehabSessionResponseDTO,
    RehabShareCreateDTO,
    RehabShareResponseDTO,
    RehabSignDTO,
)
from app.core.exceptions import (
    ApplicationError,
    EvaluationAlreadySignedError,
    PatientNotFoundError,
)
from app.presentation.dependencies import DbSession

rehab_router = APIRouter(prefix="/rehab", tags=["♻️ Rehabilitación"])


def _handle(e: Exception):
    if isinstance(e, EvaluationAlreadySignedError):
        raise HTTPException(status_code=409, detail=e.to_dict())
    if isinstance(e, PatientNotFoundError):
        raise HTTPException(status_code=404, detail=e.to_dict())
    if isinstance(e, ApplicationError):
        raise HTTPException(status_code=e.http_status or 422, detail=e.to_dict())
    raise e


# ─────────────────────────────────────────────────────────────
# CATÁLOGO
# ─────────────────────────────────────────────────────────────


@rehab_router.get(
    "/activities",
    response_model=list[RehabActivityDTO],
    summary="Catálogo de actividades disponibles",
)
def list_activities(
    db: DbSession,
    dominio: str | None = Query(default=None),
    only_active: bool = Query(default=True),
):
    from app.application.use_cases.rehab_use_cases import ListActivitiesUseCase

    return ListActivitiesUseCase(db).execute(
        dominio=dominio,
        only_active=only_active,
    )


# ─────────────────────────────────────────────────────────────
# PLAN DE INTERVENCIÓN
# ─────────────────────────────────────────────────────────────


@rehab_router.post(
    "/plans",
    response_model=RehabPlanResponseDTO,
    status_code=201,
    summary="Crear plan de rehabilitación (estado borrador)",
)
def create_plan(dto: RehabPlanCreateDTO, db: DbSession):
    from app.application.use_cases.rehab_use_cases import CreateRehabPlanUseCase

    try:
        return CreateRehabPlanUseCase(db).execute(dto)
    except Exception as e:
        _handle(e)


@rehab_router.get(
    "/plans/by-patient/{patient_id}",
    response_model=list[RehabPlanResponseDTO],
    summary="Planes de rehabilitación de un paciente",
)
def get_plans_by_patient(
    patient_id: str,
    db: DbSession,
    include_archived: bool = Query(default=False),
):
    from app.application.use_cases.rehab_use_cases import GetRehabPlanUseCase

    return GetRehabPlanUseCase(db).by_patient(
        patient_id,
        include_archived=include_archived,
    )


@rehab_router.get(
    "/plans/{plan_id}",
    response_model=RehabPlanResponseDTO,
    summary="Detalle de un plan",
)
def get_plan(plan_id: str, db: DbSession):
    from app.application.use_cases.rehab_use_cases import GetRehabPlanUseCase

    try:
        return GetRehabPlanUseCase(db).by_id(plan_id)
    except Exception as e:
        _handle(e)


@rehab_router.patch(
    "/plans/{plan_id}",
    response_model=RehabPlanResponseDTO,
    summary="Actualizar plan (solo si no está firmado, salvo cambio de estado)",
)
def update_plan(plan_id: str, dto: RehabPlanUpdateDTO, db: DbSession):
    from app.application.use_cases.rehab_use_cases import UpdateRehabPlanUseCase

    try:
        return UpdateRehabPlanUseCase(db).execute(plan_id, dto)
    except Exception as e:
        _handle(e)


@rehab_router.post(
    "/plans/{plan_id}/sign",
    response_model=RehabPlanResponseDTO,
    summary="Firmar digitalmente el plan (cierra edición)",
)
def sign_plan(
    plan_id: str,
    body: RehabSignDTO,
    request: Request,
    db: DbSession,
):
    from app.application.use_cases.rehab_use_cases import SignRehabPlanUseCase

    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail="Debe confirmar la firma con `confirm: true`.",
        )
    actor_id = getattr(request.state, "user_id", None)
    actor_label = getattr(request.state, "user_label", None)
    try:
        return SignRehabPlanUseCase(db).execute(
            plan_id=plan_id,
            actor_id=actor_id,
            actor_label=actor_label,
            note=body.note,
        )
    except Exception as e:
        _handle(e)


@rehab_router.post(
    "/plans/{plan_id}/pdf",
    summary="Descargar el plan firmado en PDF",
    description=(
        "Genera el PDF del plan de rehabilitación. Solo planes firmados "
        "(`signed_at != null`) pueden exportarse. Los borradores devuelven "
        "**409 Conflict**.\n\nReutiliza `reportlab` (mismo motor que /reports/pdf)."
    ),
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "PDF generado.",
        },
        404: {"description": "Plan no encontrado."},
        409: {"description": "Plan en estado borrador (no firmado)."},
        500: {"description": "Error generando el PDF."},
    },
)
def download_plan_pdf(plan_id: str, db: DbSession):
    from fastapi.responses import Response

    from app.infrastructure.database.orm_models import (
        ConfigInstitucionORM,
        PatientORM,
        ProfessionalORM,
        RehabPlanORM,
    )
    from app.infrastructure.rehab_pdf_service import generate_rehab_plan_pdf

    plan = db.get(RehabPlanORM, plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail=f"Plan '{plan_id}' no encontrado.")
    if plan.signed_at is None:
        raise HTTPException(
            status_code=409,
            detail="El plan está en borrador. Firme el plan antes de exportarlo a PDF.",
        )

    patient = db.get(PatientORM, plan.patient_id)
    if patient is None:
        raise HTTPException(status_code=404, detail="Paciente del plan no encontrado.")

    institucion = db.query(ConfigInstitucionORM).first()
    profesional = db.get(ProfessionalORM, plan.profesional_id) if plan.profesional_id else None

    try:
        pdf_bytes = generate_rehab_plan_pdf(
            plan=plan,
            patient=patient,
            institucion=institucion,
            profesional=profesional,
        )
    except RuntimeError as e:  # reportlab missing
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:  # plan no firmado (defensivo)
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando PDF: {e}")

    nombre = f"PlanRehab_{patient.primer_apellido or 'paciente'}_{patient.numero_documento}_{plan.id[:8]}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Content-Length": str(len(pdf_bytes)),
        },
    )


@rehab_router.post(
    "/plans/{plan_id}/share",
    response_model=RehabShareResponseDTO,
    summary="Generar link público para tarea-casa",
)
def share_plan(plan_id: str, body: RehabShareCreateDTO, request: Request, db: DbSession):
    from app.application.use_cases.rehab_use_cases import CreateRehabShareUseCase

    actor_id = getattr(request.state, "user_id", None) or "system"
    body.plan_id = plan_id  # asegurar consistencia
    try:
        return CreateRehabShareUseCase(db).execute(body, created_by=actor_id)
    except Exception as e:
        _handle(e)


# ─────────────────────────────────────────────────────────────
# SESIONES
# ─────────────────────────────────────────────────────────────


@rehab_router.post(
    "/sessions",
    response_model=RehabSessionResponseDTO,
    status_code=201,
    summary="Registrar una sesión de rehabilitación realizada en consulta",
)
def create_session(dto: RehabSessionCreateDTO, db: DbSession):
    from app.application.use_cases.rehab_use_cases import CreateRehabSessionUseCase

    try:
        return CreateRehabSessionUseCase(db).execute(dto)
    except Exception as e:
        _handle(e)


@rehab_router.get(
    "/sessions/by-patient/{patient_id}",
    response_model=list[RehabSessionResponseDTO],
    summary="Sesiones de rehabilitación de un paciente",
)
def list_sessions_by_patient(
    patient_id: str,
    db: DbSession,
    plan_id: str | None = Query(default=None),
    limit: int = Query(default=200, ge=1, le=1000),
):
    from app.application.use_cases.rehab_use_cases import ListRehabSessionsUseCase

    return ListRehabSessionsUseCase(db).by_patient(
        patient_id,
        plan_id=plan_id,
        limit=limit,
    )


# ─────────────────────────────────────────────────────────────
# EVOLUCIÓN / ADHERENCIA / SUGERENCIA
# ─────────────────────────────────────────────────────────────


@rehab_router.get(
    "/evolution/{patient_id}",
    summary="Evolución longitudinal por dominio cognitivo",
    description=(
        "Devuelve series temporales agrupadas por semana ISO y por "
        "dominio cognitivo. Útil para graficar evolución del paciente "
        "a lo largo del programa de rehabilitación."
    ),
)
def get_evolution(
    patient_id: str,
    db: DbSession,
    plan_id: str | None = Query(default=None),
):
    from app.application.use_cases.rehab_use_cases import GetEvolutionUseCase

    return GetEvolutionUseCase(db).execute(patient_id, plan_id=plan_id)


@rehab_router.get(
    "/adherence/{patient_id}",
    summary="Adherencia al plan (sesiones realizadas vs. esperadas)",
    description=(
        "Calcula adherencia del paciente a su plan activo. Devuelve "
        "porcentaje global y conteo de la semana en curso. Si el "
        "paciente no tiene plan activo, `has_plan` es false."
    ),
)
def get_adherence(patient_id: str, db: DbSession):
    from app.application.use_cases.rehab_use_cases import GetAdherenceUseCase

    return GetAdherenceUseCase(db).execute(patient_id)


@rehab_router.get(
    "/suggest/{evaluation_id}",
    summary="Sugerencia de plan a partir de una evaluación",
    description=(
        "Analiza los Z-scores e interpretaciones de la evaluación y "
        "sugiere dominios cognitivos a intervenir + actividades del "
        "catálogo correspondientes. NO crea el plan: lo devuelve para "
        "que el clínico lo revise y edite."
    ),
)
def suggest_plan(evaluation_id: str, db: DbSession):
    from app.application.use_cases.rehab_use_cases import (
        SuggestPlanFromEvaluationUseCase,
    )

    try:
        return SuggestPlanFromEvaluationUseCase(db).execute(evaluation_id)
    except Exception as e:
        _handle(e)


# ═══════════════════════════════════════════════════════════════
# ENDPOINTS PÚBLICOS (sin auth) — viewer del paciente
# Se montan en un router APARTE para que el auth_middleware los
# excluya vía _PUBLIC_PREFIXES en main.py.
# ═══════════════════════════════════════════════════════════════

rehab_public_router = APIRouter(
    prefix="/public/rehab",
    tags=["♻️ Rehabilitación · Público"],
)


@rehab_public_router.get(
    "/{token}",
    response_model=RehabPublicPlanDTO,
    summary="Vista pública del plan (sin auth, vía link de tarea-casa)",
)
def public_get_plan(token: str, db: DbSession):
    from app.application.use_cases.rehab_use_cases import GetPublicRehabPlanUseCase

    try:
        return GetPublicRehabPlanUseCase(db).execute(token)
    except ApplicationError as e:
        raise HTTPException(status_code=e.http_status or 404, detail=e.to_dict())


@rehab_public_router.post(
    "/{token}/result",
    response_model=RehabSessionResponseDTO,
    summary="El paciente envía el resultado de una actividad",
)
def public_submit_result(token: str, dto: RehabPublicResultDTO, db: DbSession):
    from app.application.use_cases.rehab_use_cases import (
        SubmitPublicRehabResultUseCase,
    )

    try:
        return SubmitPublicRehabResultUseCase(db).execute(token, dto)
    except ApplicationError as e:
        raise HTTPException(status_code=e.http_status or 404, detail=e.to_dict())
