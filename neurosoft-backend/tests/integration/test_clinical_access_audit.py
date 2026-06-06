"""
S2.6: Tests del endpoint POST /audit/clinical-access.

Registra accesos a material con copyright (ítem verbatim WISC-IV / WAIS-III)
para cumplir Resolución 1995/1999 + Ley 1090/2006.
"""

import uuid

from fastapi.testclient import TestClient

from app.infrastructure.database.engine import SessionLocal
from app.infrastructure.database.orm_models import AuditLogORM
from app.main import app


def _ensure_admin(db, user_id: str) -> None:
    from app.infrastructure.auth.auth_service import hash_password
    from app.infrastructure.database.orm_models import UserORM

    if db.get(UserORM, user_id) is None:
        u = UserORM(
            id=user_id,
            username=f"ca-admin-{user_id[:6]}",
            hashed_password=hash_password("CAtest123!"),
            nombre_completo="Dr. CA Admin",
            role="admin",
            profesional_id=None,
            is_active=True,
        )
        db.add(u)
        db.commit()


def _make_token(user_id: str, role: str = "admin") -> str:
    from datetime import UTC, datetime, timedelta

    from jose import jwt

    from app.infrastructure.auth.auth_service import ALGORITHM, SECRET_KEY

    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "jti": f"ca-{uuid.uuid4().hex[:8]}",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "username": f"ca-user-{role}",
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def _contar_accesos(test_id: str, item_index) -> int:
    sid = test_id + (f":{item_index}" if item_index is not None else "")
    db = SessionLocal()
    try:
        return db.query(AuditLogORM).filter_by(entity_type="clinical_item", entity_id=sid).count()
    finally:
        db.close()


def test_clinical_access_sin_auth_devuelve_401():
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/audit/clinical-access",
            json={"test_id": "AdWAISCC", "item_index": 5},
        )
        assert r.status_code == 401


def test_clinical_access_con_auth_persiste_registro():
    from app.main import _RL_BUCKETS
    from app.presentation.api.v1.auth import _LOGIN_ATTEMPTS

    _RL_BUCKETS.clear()
    _LOGIN_ATTEMPTS.clear()

    user_id = str(uuid.uuid4())
    with SessionLocal() as db:
        _ensure_admin(db, user_id)

    test_id = f"AdWAISCC_TEST_{uuid.uuid4().hex[:8]}"
    item_idx = 5

    antes = _contar_accesos(test_id, item_idx)

    token = _make_token(user_id, "admin")
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/audit/clinical-access",
            json={"test_id": test_id, "item_index": item_idx, "patient_id": "pac-test"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 204, r.text

    despues = _contar_accesos(test_id, item_idx)
    assert despues == antes + 1


def test_clinical_access_sin_item_index_sigue_persiste():
    from app.main import _RL_BUCKETS
    from app.presentation.api.v1.auth import _LOGIN_ATTEMPTS

    _RL_BUCKETS.clear()
    _LOGIN_ATTEMPTS.clear()

    user_id = str(uuid.uuid4())
    with SessionLocal() as db:
        _ensure_admin(db, user_id)

    test_id = f"NiWiscVoc_TEST_{uuid.uuid4().hex[:8]}"

    token = _make_token(user_id, "admin")
    with TestClient(app) as client:
        r = client.post(
            "/api/v1/audit/clinical-access",
            json={"test_id": test_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert r.status_code == 204

    db = SessionLocal()
    try:
        row = db.query(AuditLogORM).filter_by(entity_type="clinical_item", entity_id=test_id).first()
        assert row is not None
        assert test_id in (row.summary or "")
    finally:
        db.close()
