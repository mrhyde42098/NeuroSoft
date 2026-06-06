"""
app/presentation/api/v1/audit.py
=================================
Consulta de la bitácora de auditoría.

Endpoints:
    GET /audit/                 → listar con filtros (action, entity_type, actor_id, entity_id, fechas)
    GET /audit/summary          → conteo por acción en ventana de tiempo
    GET /audit/entity/{type}/{id} → historial completo de una entidad
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.infrastructure.database.orm_models import AuditLogORM
from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

audit_router = APIRouter(prefix="/audit", tags=["Auditoría"])


class AuditEntryDTO(BaseModel):
    id: int
    ts: datetime
    actor_id: str | None = None
    actor_label: str | None = None
    action: str
    entity_type: str
    entity_id: str | None = None
    summary: str | None = None
    changes: str | None = None
    ip: str | None = None


class AuditSummaryDTO(BaseModel):
    desde: datetime
    hasta: datetime
    total: int
    por_accion: dict
    por_entidad: dict


def _to_dto(o: AuditLogORM) -> AuditEntryDTO:
    return AuditEntryDTO(
        id=o.id,
        ts=o.ts,
        actor_id=o.actor_id,
        actor_label=o.actor_label,
        action=o.action,
        entity_type=o.entity_type,
        entity_id=o.entity_id,
        summary=o.summary,
        changes=o.changes,
        ip=o.ip,
    )


@audit_router.get("/", response_model=list[AuditEntryDTO])
def listar_audit(
    db: DbSession,
    admin=Depends(require_admin),
    action: str | None = None,
    entity_type: str | None = None,
    entity_id: str | None = None,
    actor_id: str | None = None,
    desde: datetime | None = None,
    hasta: datetime | None = None,
    limit: int = 200,
):
    q = db.query(AuditLogORM)
    if action:
        q = q.filter(AuditLogORM.action == action)
    if entity_type:
        q = q.filter(AuditLogORM.entity_type == entity_type)
    if entity_id:
        q = q.filter(AuditLogORM.entity_id == entity_id)
    if actor_id:
        q = q.filter(AuditLogORM.actor_id == actor_id)
    if desde:
        q = q.filter(AuditLogORM.ts >= desde)
    if hasta:
        q = q.filter(AuditLogORM.ts <= hasta)
    q = q.order_by(AuditLogORM.ts.desc()).limit(max(1, min(1000, limit)))
    return [_to_dto(o) for o in q.all()]


@audit_router.get("/summary", response_model=AuditSummaryDTO)
def resumen_audit(db: DbSession, dias: int = 30, admin=Depends(require_admin)):
    dias = max(1, min(365, dias))
    ahora = datetime.now(UTC)
    desde = ahora - timedelta(days=dias)
    items = db.query(AuditLogORM).filter(AuditLogORM.ts >= desde).all()
    por_accion: dict = {}
    por_entidad: dict = {}
    for i in items:
        por_accion[i.action] = por_accion.get(i.action, 0) + 1
        por_entidad[i.entity_type] = por_entidad.get(i.entity_type, 0) + 1
    return AuditSummaryDTO(
        desde=desde,
        hasta=ahora,
        total=len(items),
        por_accion=por_accion,
        por_entidad=por_entidad,
    )


@audit_router.get("/entity/{entity_type}/{entity_id}", response_model=list[AuditEntryDTO])
def historial_entidad(
    entity_type: str,
    entity_id: str,
    db: DbSession,
    admin=Depends(require_admin),
):
    q = db.query(AuditLogORM).filter_by(entity_type=entity_type, entity_id=entity_id).order_by(AuditLogORM.ts.desc())
    return [_to_dto(o) for o in q.all()]


# ═══════════════════════════════════════════════════════════════════
# S2.6: Endpoint de auditoría de acceso a ítems verbatim
# ═══════════════════════════════════════════════════════════════════


class ClinicalAccessDTO(BaseModel):
    test_id: str
    item_index: int | None = None
    action: str = "view_verbatim_item"
    patient_id: str | None = None
    timestamp: str | None = None
    context: dict | None = None


@audit_router.post("/clinical-access", status_code=204)
def registrar_acceso_clinico(
    body: ClinicalAccessDTO,
    db: DbSession,
    user=Depends(__import__("app.presentation.api.v1.auth", fromlist=["get_current_user"]).get_current_user),
):
    """
    Registra un acceso a material con copyright (ítem verbatim WISC-IV / WAIS-III)
    para cumplir la Resolución 1995/1999 + Ley 1090/2006 (trazabilidad clínica).

    No retorna contenido; solo persiste el log de auditoría.
    """
    from app.infrastructure.audit import record_event

    record_event(
        db,
        action=body.action,
        entity_type="clinical_item",
        entity_id=body.test_id + (f":{body.item_index}" if body.item_index is not None else ""),
        actor_id=user.id if hasattr(user, "id") else None,
        actor_label=user.username if hasattr(user, "username") else None,
        summary=(f"Acceso a ítem verbatim de '{body.test_id}' (paciente={body.patient_id or 'N/A'})"),
    )
    db.commit()
    return None
