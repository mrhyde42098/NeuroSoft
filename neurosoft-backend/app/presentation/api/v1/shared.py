"""
app/presentation/api/v1/shared.py
==================================
Telemedicina / Compartir informes — Fase H-bis del ROADMAP.

Permite que el clínico genere un link público con token opaco para
compartir un informe con el paciente, un remitente o un colega. El
link vence en X horas/días y puede protegerse con contraseña bcrypt.

Endpoints protegidos (requieren Bearer token del clínico):
    POST   /shared                          → crear share token
    GET    /shared                          → listar shares del usuario
    DELETE /shared/{token}                  → revocar share

Endpoint público (sin auth — _PUBLIC_PATHS prefix en middleware):
    GET    /shared/view/{token}             → resolver contenido del share
    POST   /shared/view/{token}/verify      → verificar contraseña (si aplica)

Autor: NeuroSoft — 2026
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

from app.infrastructure.auth.auth_service import (
    hash_password as _bcrypt_hash,
)
from app.infrastructure.auth.auth_service import (
    verify_password as _bcrypt_verify,
)
from app.infrastructure.database.orm_models import (
    EvaluationORM,
    PatientORM,
    SharedReportORM,
)
from app.presentation.api.v1.auth import CurrentUser, get_evaluation_for_user
from app.presentation.dependencies import DbSession

logger = logging.getLogger("neurosoft.shared")

shared_router = APIRouter(prefix="/shared", tags=["Telemedicina"])
shared_public_router = APIRouter(prefix="/shared/view", tags=["Telemedicina (público)"])


# ═══════════════════════════════════════════════════════════════════════
# DTOs
# ═══════════════════════════════════════════════════════════════════════
VALID_SCOPES = ("summary", "full", "iq_only")


class CreateShareIn(BaseModel):
    evaluation_id: str
    scope: str = Field("summary", pattern="^(summary|full|iq_only)$")
    ttl_hours: int = Field(72, ge=1, le=24 * 30)  # máximo 30 días
    password: str | None = None


class ShareOut(BaseModel):
    id: str
    token: str
    evaluation_id: str
    patient_id: str
    scope: str
    expires_at: datetime
    revoked: bool
    viewed_count: int
    last_viewed_at: datetime | None = None
    created_at: datetime
    has_password: bool
    public_url: str


class VerifyIn(BaseModel):
    password: str


# ═══════════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════════
def _utc_now() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


def _hash_password(raw: str) -> str:
    """
    Hashea la contraseña de un share con bcrypt (misma lib que auth_service).
    Los hashes legacy SHA-256 (formato `salt$hex`) se verifican igualmente
    para no romper shares creados antes de esta migración, pero los nuevos
    se generan en bcrypt.
    """
    return _bcrypt_hash(raw)


def _verify_password(raw: str, hashed: str) -> bool:
    """
    Verifica contra bcrypt (nuevos) o SHA-256 (legacy).
    Los hashes bcrypt empiezan con '$2a$', '$2b$' o '$2y$'.
    """
    if not hashed:
        return False
    # bcrypt → delegar en passlib
    if hashed.startswith(("$2a$", "$2b$", "$2y$")):
        return _bcrypt_verify(raw, hashed)
    # Legacy SHA-256 con salt (`salt$hex`)
    try:
        salt, h = hashed.split("$", 1)
        return hashlib.sha256((salt + raw).encode("utf-8")).hexdigest() == h
    except Exception:
        return False


def _row_to_out(row: SharedReportORM) -> ShareOut:
    return ShareOut(
        id=row.id,
        token=row.token,
        evaluation_id=row.evaluation_id,
        patient_id=row.patient_id,
        scope=row.scope or "summary",
        expires_at=row.expires_at,
        revoked=bool(row.revoked),
        viewed_count=row.viewed_count or 0,
        last_viewed_at=row.last_viewed_at,
        created_at=row.created_at,
        has_password=bool(row.password_hash),
        public_url=f"/shared/view/{row.token}",
    )


def _safe_json_list(raw: str | None) -> list:
    try:
        parsed = json.loads(raw or "[]")
        return parsed if isinstance(parsed, list) else []
    except Exception:
        logger.warning("JSON inválido en share (campos de evaluación)")
        return []


def _build_public_payload(row: SharedReportORM, ev: EvaluationORM, pt: PatientORM | None) -> dict:
    """
    Serializa el informe SIN PHI (ni nombre, ni documento) para el viewer
    público. El clínico decide 'scope' al crear el share.
    """
    payload: dict = {
        "token": row.token,
        "scope": row.scope or "summary",
        "created_at": row.created_at.isoformat() if row.created_at else None,
        "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        "evaluation": {
            "protocolo": ev.protocolo,
            "fecha": ev.fecha.isoformat() if ev.fecha else None,
            "poblacion": ev.poblacion,
            "edad": ev.edad_display,
            "pruebas_realizadas": ev.pruebas_realizadas,
        },
        "patient_alias": (pt.iniciales if pt and getattr(pt, "iniciales", None) else "Paciente"),
    }

    # El scope regula qué partes viajan
    try:
        resultados = json.loads(ev.resultados_json or "[]")
    except Exception:
        resultados = []

    if row.scope == "summary":
        payload["puntos_fuertes"] = _safe_json_list(ev.puntos_fuertes_json)
        payload["puntos_debiles"] = _safe_json_list(ev.puntos_debiles_json)
        payload["advertencias"] = _safe_json_list(ev.advertencias_json)
    elif row.scope == "iq_only":
        # Filtrar sólo compuestos WISC/WAIS si están en resultados
        payload["iq"] = [
            r
            for r in resultados
            if isinstance(r, dict) and str(r.get("test_id", "")).upper().startswith(("ICV", "IRP", "IMT", "IVP", "CIT"))
        ]
    else:  # full
        payload["resultados"] = resultados
        payload["puntos_fuertes"] = _safe_json_list(ev.puntos_fuertes_json)
        payload["puntos_debiles"] = _safe_json_list(ev.puntos_debiles_json)
        payload["advertencias"] = _safe_json_list(ev.advertencias_json)

    return payload


# ═══════════════════════════════════════════════════════════════════════
# Endpoints protegidos (clínico autenticado)
# ═══════════════════════════════════════════════════════════════════════
@shared_router.post("", response_model=ShareOut)
def create_share(
    payload: CreateShareIn,
    request: Request,
    db: DbSession,
    user: CurrentUser,
):
    user_id = getattr(request.state, "user_id", "default")

    ev = get_evaluation_for_user(payload.evaluation_id, db, user)

    token = secrets.token_urlsafe(24)
    expires = _utc_now() + timedelta(hours=payload.ttl_hours)
    row = SharedReportORM(
        id=str(uuid4()),
        token=token,
        evaluation_id=ev.id,
        patient_id=ev.patient_id,
        created_by=user_id,
        scope=payload.scope,
        password_hash=_hash_password(payload.password) if payload.password else None,
        expires_at=expires,
        revoked=False,
        viewed_count=0,
        created_at=_utc_now(),
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    logger.info(
        "share_created id=%s token=%s expires=%s scope=%s", row.id, token[:8] + "…", expires.isoformat(), payload.scope
    )
    return _row_to_out(row)


@shared_router.get("", response_model=list[ShareOut])
def list_my_shares(request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    rows = (
        db.query(SharedReportORM)
        .filter_by(created_by=user_id)
        .order_by(SharedReportORM.created_at.desc())
        .limit(200)
        .all()
    )
    return [_row_to_out(r) for r in rows]


@shared_router.delete("/{token}")
def revoke_share(token: str, request: Request, db: DbSession):
    user_id = getattr(request.state, "user_id", "default")
    row = db.query(SharedReportORM).filter_by(token=token).first()
    if not row:
        raise HTTPException(404, "Share no encontrado")
    if row.created_by != user_id:
        raise HTTPException(403, "No puedes revocar un share ajeno")
    row.revoked = True
    db.commit()
    logger.info("share_revoked token=%s by=%s", token[:8] + "…", user_id)
    return {"ok": True, "revoked": True}


# ═══════════════════════════════════════════════════════════════════════
# Endpoints públicos (paciente / remitente — sin Bearer)
# ═══════════════════════════════════════════════════════════════════════
@shared_public_router.get("/{token}")
def public_view(token: str, request: Request, db: DbSession):
    """
    Devuelve metadatos del share. Si está protegido con contraseña, sólo
    responde { requires_password: true } hasta que se llame /verify.
    """
    row = db.query(SharedReportORM).filter_by(token=token).first()
    if not row:
        raise HTTPException(404, "Link no válido")
    if row.revoked:
        raise HTTPException(410, "Link revocado por el profesional")
    if row.expires_at and row.expires_at < _utc_now():
        raise HTTPException(410, "Link expirado")

    if row.password_hash:
        return {
            "requires_password": True,
            "scope": row.scope,
            "expires_at": row.expires_at.isoformat() if row.expires_at else None,
        }

    # Registrar vista y devolver contenido
    row.viewed_count = (row.viewed_count or 0) + 1
    row.last_viewed_at = _utc_now()
    ev = db.query(EvaluationORM).filter_by(id=row.evaluation_id).first()
    pt = db.query(PatientORM).filter_by(id=row.patient_id).first() if ev else None
    if not ev:
        raise HTTPException(404, "Informe subyacente no disponible")
    db.commit()
    return _build_public_payload(row, ev, pt)


@shared_public_router.post("/{token}/verify")
def public_verify(token: str, body: VerifyIn, request: Request, db: DbSession):
    row = db.query(SharedReportORM).filter_by(token=token).first()
    if not row:
        raise HTTPException(404, "Link no válido")
    if row.revoked:
        raise HTTPException(410, "Link revocado")
    if row.expires_at and row.expires_at < _utc_now():
        raise HTTPException(410, "Link expirado")

    if not row.password_hash or not _verify_password(body.password, row.password_hash):
        raise HTTPException(401, "Contraseña incorrecta")

    row.viewed_count = (row.viewed_count or 0) + 1
    row.last_viewed_at = _utc_now()
    ev = db.query(EvaluationORM).filter_by(id=row.evaluation_id).first()
    pt = db.query(PatientORM).filter_by(id=row.patient_id).first() if ev else None
    if not ev:
        raise HTTPException(404, "Informe no disponible")
    db.commit()
    return _build_public_payload(row, ev, pt)
