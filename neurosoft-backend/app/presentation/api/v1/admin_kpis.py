"""
app/presentation/api/v1/admin_kpis.py
=======================================
KPIs administrativos para coordinación clínica (Sprint 11).

Endpoints:
  GET /api/v1/admin/kpis           → métricas globales del sistema
  GET /api/v1/admin/kpis/professional  → producción por profesional
  GET /api/v1/admin/kpis/diagnoses     → distribución diagnóstica top-N

Todos los endpoints requieren bearer token (admin gate por rol futuro).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func

from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

admin_kpis_router = APIRouter(prefix="/admin/kpis", tags=["🛡️ Admin · KPIs"])


# ─────────────────────────────────────────────────────────────
# KPIs globales
# ─────────────────────────────────────────────────────────────
@admin_kpis_router.get(
    "",
    summary="KPIs globales del sistema",
    description=(
        "Métricas agregadas: total de pacientes, evaluaciones, planes "
        "de rehabilitación, citas agendadas. Útil para tablero de "
        "coordinación clínica."
    ),
)
def kpis_globales(db: DbSession, admin=Depends(require_admin)) -> dict[str, Any]:
    from app.infrastructure.database.orm_models import (
        AppointmentORM,
        ClinicalHistoryORM,
        EvaluationORM,
        PatientORM,
        RehabPlanORM,
        RehabSessionORM,
    )

    now = datetime.now(UTC)
    inicio_mes = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    hace_30 = now - timedelta(days=30)
    hace_7 = now - timedelta(days=7)

    # SQL counts
    def _count(model, *filters):
        q = db.query(func.count(model.id))
        for f in filters:
            q = q.filter(f)
        return int(q.scalar() or 0)

    return {
        "pacientes": {
            "total": _count(PatientORM),
            "nuevos_30d": _count(PatientORM, PatientORM.created_at >= hace_30),
            "nuevos_7d": _count(PatientORM, PatientORM.created_at >= hace_7),
        },
        "evaluaciones": {
            "total": _count(EvaluationORM),
            "este_mes": _count(EvaluationORM, EvaluationORM.created_at >= inicio_mes),
            "ultimos_30d": _count(EvaluationORM, EvaluationORM.created_at >= hace_30),
            "firmadas": _count(EvaluationORM, EvaluationORM.signed_at.isnot(None)),
        },
        "rehabilitacion": {
            "planes_total": _count(RehabPlanORM),
            "planes_activos": _count(RehabPlanORM, RehabPlanORM.estado == "activo"),
            "planes_firmados": _count(RehabPlanORM, RehabPlanORM.signed_at.isnot(None)),
            "sesiones_30d": _count(RehabSessionORM, RehabSessionORM.created_at >= hace_30),
        },
        "agenda": {
            "citas_total": _count(AppointmentORM),
            "esta_semana": _count(AppointmentORM, AppointmentORM.fecha >= hace_7.date()),
        },
        "historia_clinica": {
            "total": _count(ClinicalHistoryORM),
        },
        "timestamp": now.isoformat(),
    }


# ─────────────────────────────────────────────────────────────
# Producción por profesional
# ─────────────────────────────────────────────────────────────
@admin_kpis_router.get(
    "/professional",
    summary="Producción de informes por profesional",
    description=(
        "Para cada profesional registrado, calcula: pacientes "
        "asignados, evaluaciones realizadas, planes de rehab firmados "
        "y carga del último mes."
    ),
)
def kpis_por_profesional(
    db: DbSession,
    dias: int = Query(30, ge=1, le=365),
    admin=Depends(require_admin),
) -> list[dict[str, Any]]:
    from app.infrastructure.database.orm_models import (
        EvaluationORM,
        PatientORM,
        ProfessionalORM,
        RehabPlanORM,
    )

    cutoff = datetime.now(UTC) - timedelta(days=dias)
    profs = db.query(ProfessionalORM).all()
    out: list[dict[str, Any]] = []
    for p in profs:
        pacientes = (
            db.query(func.count(PatientORM.id))
            .filter(
                PatientORM.profesional_id == p.id,
            )
            .scalar()
            or 0
        )
        evals_total = (
            db.query(func.count(EvaluationORM.id))
            .join(
                PatientORM,
                PatientORM.id == EvaluationORM.patient_id,
            )
            .filter(PatientORM.profesional_id == p.id)
            .scalar()
            or 0
        )
        evals_periodo = (
            db.query(func.count(EvaluationORM.id))
            .join(
                PatientORM,
                PatientORM.id == EvaluationORM.patient_id,
            )
            .filter(
                PatientORM.profesional_id == p.id,
                EvaluationORM.created_at >= cutoff,
            )
            .scalar()
            or 0
        )
        planes_firmados = (
            db.query(func.count(RehabPlanORM.id))
            .filter(
                RehabPlanORM.profesional_id == p.id,
                RehabPlanORM.signed_at.isnot(None),
            )
            .scalar()
            or 0
        )
        out.append(
            {
                "profesional_id": p.id,
                "nombre": p.nombre_completo,
                "titulo": getattr(p, "titulo", None),
                "pacientes": int(pacientes),
                "evaluaciones_total": int(evals_total),
                f"evaluaciones_{dias}d": int(evals_periodo),
                "planes_firmados": int(planes_firmados),
            }
        )
    # Ordenar por producción reciente
    out.sort(key=lambda x: x[f"evaluaciones_{dias}d"], reverse=True)
    return out


# ─────────────────────────────────────────────────────────────
# Distribución diagnóstica top-N
# ─────────────────────────────────────────────────────────────
@admin_kpis_router.get(
    "/diagnoses",
    summary="Distribución diagnóstica (top N CIE-10)",
    description=(
        "Cuenta los códigos CIE-10 más frecuentes en las historias "
        "clínicas. Útil para perfilar la población clínica atendida."
    ),
)
def kpis_diagnosticos(
    db: DbSession,
    top: int = Query(20, ge=5, le=100),
    admin=Depends(require_admin),
) -> list[dict[str, Any]]:
    from app.infrastructure.database.orm_models import ClinicalHistoryORM

    rows = (
        db.query(
            ClinicalHistoryORM.codigo_cie10,
            func.count(ClinicalHistoryORM.id).label("n"),
        )
        .filter(ClinicalHistoryORM.codigo_cie10.isnot(None))
        .group_by(ClinicalHistoryORM.codigo_cie10)
        .order_by(func.count(ClinicalHistoryORM.id).desc())
        .limit(top)
        .all()
    )
    return [{"cie10": cod, "n": int(n)} for cod, n in rows if cod]
