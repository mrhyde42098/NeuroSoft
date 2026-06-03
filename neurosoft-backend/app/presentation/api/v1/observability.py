"""
S4.2: Endpoint de observabilidad / métricas (opt-in).

Devuelve un snapshot de las métricas en memoria. Solo accesible para admin.
Solo retorna datos si NEUROSOFT_METRICS_ENABLED=1.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.infrastructure.observability import metrics
from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession


router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/metrics", summary="Snapshot de métricas (admin, opt-in)")
def get_metrics(
    db: Session = Depends(DbSession),
    admin=Depends(require_admin),
) -> dict:
    """
    Devuelve el estado actual de las métricas en memoria.
    Solo retorna datos si `NEUROSOFT_METRICS_ENABLED=1`; de lo contrario,
    devuelve `{"enabled": false}`.
    """
    return metrics.snapshot()


@router.post("/metrics/flush", summary="Forzar envío al DSN (admin, opt-in)")
def flush_metrics(
    db: Session = Depends(DbSession),
    admin=Depends(require_admin),
) -> dict:
    """
    Fuerza el envío del snapshot al DSN configurado en
    `NEUROSOFT_METRICS_DSN`. Devuelve `sent=true/false`.
    """
    sent = metrics.flush_to_dsn()
    return {"sent": sent, "enabled": metrics._is_enabled()}
