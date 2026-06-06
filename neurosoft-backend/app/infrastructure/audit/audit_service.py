"""
app/infrastructure/audit/audit_service.py
==========================================
Servicio de auditoría.

Registra eventos relevantes sobre entidades clínicas y de seguridad.
Uso principal:

    from app.infrastructure.audit import record_event
    record_event(db, actor_id=pro.id, action="update",
                 entity_type="patient", entity_id=pat.id,
                 summary="Actualización datos de contacto",
                 changes={"telefono": ["vieja","nueva"]}, request=request)

También expone un decorador `audit_action` para envolver handlers FastAPI.
Los errores durante el registro NO deben tumbar la operación clínica —
por eso se capturan silenciosamente y se loggean.
"""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from functools import wraps
from typing import Any

from fastapi import Request
from sqlalchemy.orm import Session

from app.infrastructure.database.orm_models import AuditLogORM

_log = logging.getLogger("neurosoft.audit")


def _safe_json(obj: Any) -> str | None:
    try:
        return json.dumps(obj, default=str, ensure_ascii=False)[:20000]
    except Exception:
        return None


def record_event(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: str | None = None,
    actor_id: str | None = None,
    actor_label: str | None = None,
    summary: str | None = None,
    changes: Mapping[str, Any] | None = None,
    request: Request | None = None,
    commit: bool = True,
) -> None:
    """Registra un evento de auditoría.

    `commit`: si True hace commit inmediato. En triggers dentro de una
    transacción en curso pasa `commit=False` para adjuntar al commit padre.
    """
    try:
        ip = None
        ua = None
        rid = None
        if request is not None:
            try:
                ip = request.client.host if request.client else None
                ua = (request.headers.get("user-agent", "") or "")[:400]
                # Correlación con logs del proceso (X-Request-ID)
                rid = getattr(request.state, "request_id", None)
            except (AttributeError, KeyError, UnicodeDecodeError):
                # request.client puede ser None; headers con UTF-8 raros.
                # No bloqueamos el asiento de auditoría por metadatos.
                pass
        # Fallback: si nadie nos pasó request, intentamos un contextvar global
        if not rid or not isinstance(rid, str):
            try:
                from app.core.request_context import current_request_id

                cv = current_request_id.get()
                rid = cv if isinstance(cv, str) and cv else None
            except Exception:
                rid = None
        # Coerción final: si no es un string razonable, descartamos
        if rid is not None and not isinstance(rid, str):
            rid = None
        if rid is not None:
            rid = rid[:64]
        # Defensa contra IPs / UAs no-string (mocks de test, etc.)
        if ip is not None and not isinstance(ip, str):
            ip = None
        if ua is not None and not isinstance(ua, str):
            ua = None
        entry = AuditLogORM(
            actor_id=actor_id or "system",
            actor_label=(actor_label or "")[:120],
            action=action[:40],
            entity_type=entity_type[:40],
            entity_id=(entity_id or "")[:36] or None,
            summary=(summary or "")[:300] or None,
            changes=_safe_json(dict(changes)) if changes else None,
            ip=ip,
            user_agent=ua,
            request_id=(rid or None),
        )
        db.add(entry)
        if commit:
            db.commit()
    except Exception as exc:
        # Nunca romper el flujo clínico por un fallo de auditoría
        try:
            db.rollback()
        except Exception:
            pass
        _log.warning("Audit log failed: %s", exc)


def audit_action(entity_type: str, action: str, summary: str | None = None):
    """Decorador para endpoints FastAPI.

    Requiere que el endpoint reciba una `Session` por DI y `Request`.
    Extrae actor_id desde `request.state.user` si existe.
    """

    def deco(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            result = fn(*a, **kw)
            try:
                db = kw.get("db")
                req: Request | None = kw.get("request")
                actor_id, actor_label = None, None
                if req is not None and hasattr(req.state, "user"):
                    u = req.state.user
                    actor_id = getattr(u, "id", None) or u.get("id") if isinstance(u, dict) else None
                    actor_label = getattr(u, "username", None) or (u.get("username") if isinstance(u, dict) else None)
                ent_id = None
                try:
                    ent_id = getattr(result, "id", None) or (result.get("id") if isinstance(result, dict) else None)
                except (AttributeError, TypeError):
                    # `result` no expone .id ni es dict → ent_id queda None
                    pass
                if db is not None:
                    record_event(
                        db,
                        action=action,
                        entity_type=entity_type,
                        entity_id=ent_id,
                        actor_id=actor_id,
                        actor_label=actor_label,
                        summary=summary,
                        request=req,
                    )
            except Exception as exc:
                _log.warning("audit_action decorator error: %s", exc)
            return result

        return wrapper

    return deco
