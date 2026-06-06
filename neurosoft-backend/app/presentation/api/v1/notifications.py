"""
app/presentation/api/v1/notifications.py
==========================================
Sprint 10 — Sistema de notificaciones del clínico para telerehab.

Implementación sin tabla nueva: deriva las notificaciones dinámicamente
desde `RehabSessionORM` filtrando sesiones recientes con
`modo == 'tarea_casa'` (paciente completó actividad desde casa).

Endpoints:
  GET /api/v1/notifications       → lista de notificaciones recientes
  GET /api/v1/notifications/count → contador de no-leídas (para badge)

El estado "leída" se persiste en localStorage del frontend
(timestamp del último check). El backend no almacena ese estado para
evitar añadir tablas en una iteración inicial.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, Query

from app.presentation.dependencies import DbSession

notifications_router = APIRouter(prefix="/notifications", tags=["🔔 Notificaciones"])


def _build_notification(session, paciente_nombre: str) -> dict[str, Any]:
    return {
        "id": session.id,
        "tipo": "rehab_tarea_casa",
        "mensaje": f"{paciente_nombre} completó una sesión de rehabilitación desde casa.",
        "patient_id": session.patient_id,
        "paciente_nombre": paciente_nombre,
        "plan_id": getattr(session, "plan_id", None),
        "activity_slug": getattr(session, "activity_slug", None),
        "score": getattr(session, "score", None),
        "modo": getattr(session, "modo", "tarea_casa"),
        "created_at": session.created_at.isoformat() if session.created_at else None,
        "icon": "fitness_center",
        "color": "#0d9488",
    }


@notifications_router.get(
    "",
    summary="Notificaciones recientes del clínico",
    description=(
        "Lista actividades de rehabilitación completadas desde casa "
        "(`modo == 'tarea_casa'`) en los últimos N días. Ordenadas por "
        "fecha descendente. El frontend marca como 'leídas' las que "
        "tengan `created_at <= last_seen_at` (persistido en localStorage)."
    ),
)
def list_notifications(
    db: DbSession,
    dias: int = Query(7, ge=1, le=90),
    limit: int = Query(50, ge=1, le=200),
) -> list[dict[str, Any]]:
    from app.infrastructure.database.orm_models import PatientORM, RehabSessionORM

    cutoff = datetime.now(UTC) - timedelta(days=dias)
    sessions = (
        db.query(RehabSessionORM)
        .filter(RehabSessionORM.modo == "tarea_casa")
        .filter(RehabSessionORM.created_at >= cutoff)
        .order_by(RehabSessionORM.created_at.desc())
        .limit(limit)
        .all()
    )
    # Resolver nombre paciente
    pids = {s.patient_id for s in sessions if s.patient_id}
    name_by_id: dict[str, str] = {}
    if pids:
        for p in db.query(PatientORM).filter(PatientORM.id.in_(pids)).all():
            name_by_id[p.id] = (
                getattr(p, "nombre_completo", None)
                or f"{p.primer_nombre or ''} {p.primer_apellido or ''}".strip()
                or "Paciente"
            )
    return [_build_notification(s, name_by_id.get(s.patient_id, "Paciente")) for s in sessions]


@notifications_router.get(
    "/count",
    summary="Contador de notificaciones recientes (badge)",
    description=(
        "Devuelve el conteo de sesiones tarea-casa de los últimos N días. "
        "El frontend pasa opcionalmente `since` (ISO timestamp del último "
        "vistazo) para calcular sólo las nuevas."
    ),
)
def count_notifications(
    db: DbSession,
    dias: int = Query(7, ge=1, le=90),
    since: str | None = Query(None, description="ISO timestamp opcional"),
) -> dict[str, Any]:
    from sqlalchemy import func

    from app.infrastructure.database.orm_models import RehabSessionORM

    cutoff = datetime.now(UTC) - timedelta(days=dias)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00"))
            if since_dt > cutoff:
                cutoff = since_dt
        except (ValueError, AttributeError):
            # Formato ISO invalido — usar cutoff por defecto
            pass

    n = (
        db.query(func.count(RehabSessionORM.id))
        .filter(RehabSessionORM.modo == "tarea_casa")
        .filter(RehabSessionORM.created_at >= cutoff)
        .scalar()
        or 0
    )
    return {
        "count": int(n),
        "cutoff": cutoff.isoformat(),
        "label": "tarea_casa",
    }


@notifications_router.get(
    "/adherence/summary",
    summary="Resumen de adherencia de pacientes con plan activo",
    description=(
        "Para los pacientes con plan de rehabilitación firmado, calcula "
        "adherencia agregada del último periodo. Alimenta el dashboard."
    ),
)
def adherence_summary(db: DbSession, dias: int = Query(14, ge=7, le=90)) -> dict[str, Any]:
    from sqlalchemy import func

    from app.infrastructure.database.orm_models import (
        PatientORM,
        RehabPlanORM,
        RehabSessionORM,
    )

    cutoff = datetime.now(UTC) - timedelta(days=dias)
    planes = (
        db.query(RehabPlanORM).filter(RehabPlanORM.estado == "activo").filter(RehabPlanORM.signed_at.isnot(None)).all()
    )
    rows: list[dict[str, Any]] = []
    for plan in planes:
        sesiones = (
            db.query(func.count(RehabSessionORM.id))
            .filter(RehabSessionORM.plan_id == plan.id)
            .filter(RehabSessionORM.created_at >= cutoff)
            .scalar()
            or 0
        )
        esperadas = (plan.frecuencia_semanal or 2) * (dias / 7)
        pct = int(round(min(1.5, (sesiones / esperadas if esperadas else 0)) * 100))
        pac = db.get(PatientORM, plan.patient_id) if plan.patient_id else None
        rows.append(
            {
                "plan_id": plan.id,
                "patient_id": plan.patient_id,
                "paciente_nombre": (
                    getattr(pac, "nombre_completo", None)
                    or (f"{pac.primer_nombre or ''} {pac.primer_apellido or ''}".strip() if pac else "—")
                ),
                "sesiones": int(sesiones),
                "esperadas": round(esperadas, 1),
                "adherencia_pct": pct,
                "estado": "verde" if pct >= 80 else "amarillo" if pct >= 50 else "rojo",
            }
        )
    rows.sort(key=lambda r: r["adherencia_pct"])
    return {
        "periodo_dias": dias,
        "total_pacientes": len(rows),
        "promedio_adherencia": int(sum(r["adherencia_pct"] for r in rows) / len(rows)) if rows else 0,
        "pacientes": rows,
    }
