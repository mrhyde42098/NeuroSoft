"""
tests/integration/test_e2e_multi_tenant.py
===========================================
S0.7 del PLAN_MAESTRO: E2E multi-tenant end-to-end.

Simula el flujo completo de un ataque cross-tenant:
  1. Profesional A crea un paciente.
  2. Profesional B intenta acceder al paciente de A → 403 + audit.
  3. Profesional B intenta EXPORTAR los datos de A → 403 + audit.
  4. Profesional B intenta MODIFICAR el paciente de A → 403 + audit.
  5. Profesional B intenta ARCHIVAR el paciente de A → 403 + audit.
  6. Admin (super-user) SI puede ver/modificar todo.
  7. Profesional C (sin vinculo) solo ve pacientes huerfanos.

Este test es el "smoke test" de toda la cadena de seguridad
(autenticacion -> autorizacion -> audit log).
"""

from __future__ import annotations

import uuid

import pytest

# ═══════════════════════════════════════════════════════════════════
# Fixtures locales (no se reutiliza conftest.client para mantener aislado)
# ═══════════════════════════════════════════════════════════════════


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session_factory():
    from app.infrastructure.database.engine import SessionLocal

    return SessionLocal


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _ensure_professional(db, prof_id: str, suffix: str = ""):
    from app.infrastructure.database.orm_models import ProfessionalORM

    p = db.get(ProfessionalORM, prof_id)
    if p is None:
        p = ProfessionalORM(
            id=prof_id,
            nombre_completo=f"Dr. E2E {suffix}",
            titulo="Psicólogo",
            especialidad="Neuropsicología",
            activo=True,
        )
        db.add(p)
        db.commit()
    return p


def _create_patient(db, prof_id: str, doc: str):
    from datetime import date

    from app.infrastructure.database.orm_models import PatientORM

    p = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=doc,
        tipo_documento="CC",
        primer_nombre="E2E",
        primer_apellido="MultiTenant",
        fecha_nacimiento=date(2010, 1, 1),
        sexo="M",
        escolaridad="Primaria",
        lateralidad="Diestro",
        fecha_atencion=date(2026, 6, 1),
        profesional_id=prof_id,
        is_active=True,
    )
    db.add(p)
    db.commit()
    return p


def _create_user(db, user_id: str, prof_id: str | None, role: str = "profesional") -> str:
    """Crea un user real (no solo profesional) y devuelve su id."""
    from app.infrastructure.auth.auth_service import hash_password
    from app.infrastructure.database.orm_models import UserORM

    u = UserORM(
        id=user_id,
        username=f"e2e-{user_id[:8]}",
        hashed_password=hash_password("E2Etest123!"),
        nombre_completo=f"Dr. E2E {user_id[:6]}",
        role=role,
        profesional_id=prof_id,
        is_active=True,
    )
    db.add(u)
    db.commit()
    return u.id


def _make_token(user_id: str, prof_id: str | None, role: str = "profesional") -> str:
    from datetime import UTC, datetime, timedelta

    from jose import jwt

    from app.infrastructure.auth.auth_service import ALGORITHM, SECRET_KEY

    now = datetime.now(UTC)
    payload = {
        "sub": user_id,
        "role": role,
        "type": "access",
        "jti": f"e2e-{uuid.uuid4().hex[:8]}",
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
        "username": f"e2e-user-{role}",
        "profesional_id": prof_id,
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# ═══════════════════════════════════════════════════════════════════
# Test class
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestE2EMultiTenant:
    def test_flujo_completo_ataque_cross_tenant(
        self,
        client,
        db_session_factory,
    ):
        """
        Simula el ataque completo de un profesional B contra
        los datos de un profesional A.
        """
        from app.infrastructure.database.orm_models import AuditLogORM

        # ─────────────────────────────────────────────────
        # SETUP
        # ─────────────────────────────────────────────────
        prof_a_id = str(uuid.uuid4())
        prof_b_id = str(uuid.uuid4())
        prof_c_id = str(uuid.uuid4())  # sin vinculo
        user_a_id = str(uuid.uuid4())
        user_b_id = str(uuid.uuid4())
        user_c_id = str(uuid.uuid4())
        user_admin_id = str(uuid.uuid4())

        with db_session_factory() as db:
            _ensure_professional(db, prof_a_id, "A")
            _ensure_professional(db, prof_b_id, "B")
            _ensure_professional(db, prof_c_id, "C-orphan")
            _create_user(db, user_a_id, prof_a_id, "profesional")
            _create_user(db, user_b_id, prof_b_id, "profesional")
            _create_user(db, user_c_id, None, "profesional")
            _create_user(db, user_admin_id, None, "admin")
            patient_a = _create_patient(db, prof_a_id, f"E2E-A-{uuid.uuid4().hex[:6]}")
            patient_orphan = _create_patient(
                db,
                prof_a_id,
                f"E2E-ORPHAN-{uuid.uuid4().hex[:6]}",
            )
            # Forzar el paciente orphan a profesional_id = None
            patient_orphan.profesional_id = None
            db.commit()
            patient_a_id = patient_a.id
            patient_orphan_id = patient_orphan.id

        token_a = _make_token(user_a_id, prof_a_id, "profesional")
        token_b = _make_token(user_b_id, prof_b_id, "profesional")
        token_c = _make_token(user_c_id, None, "profesional")
        token_admin = _make_token(user_admin_id, None, "admin")

        # ─────────────────────────────────────────────────
        # 1. Profesional A puede ver SU paciente
        # ─────────────────────────────────────────────────
        r = client.get(
            f"/api/v1/patients/{patient_a_id}",
            headers={"Authorization": f"Bearer {token_a}"},
        )
        assert r.status_code == 200, f"A debe ver su paciente: {r.text}"

        # ─────────────────────────────────────────────────
        # 2. Profesional B NO puede ver el paciente de A
        # ─────────────────────────────────────────────────
        r = client.get(
            f"/api/v1/patients/{patient_a_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 403, f"B NO debe ver paciente de A: {r.status_code}"

        # ─────────────────────────────────────────────────
        # 3. Profesional B NO puede MODIFICAR el paciente de A
        # ─────────────────────────────────────────────────
        r = client.patch(
            f"/api/v1/patients/{patient_a_id}",
            json={"primer_nombre": "HACKED"},
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 403

        # ─────────────────────────────────────────────────
        # 4. Profesional B NO puede ARCHIVAR el paciente de A
        # ─────────────────────────────────────────────────
        r = client.delete(
            f"/api/v1/patients/{patient_a_id}",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 403

        # ─────────────────────────────────────────────────
        # 5. Profesional B NO puede EXPORTAR el paciente de A
        # ─────────────────────────────────────────────────
        r = client.get(
            f"/api/v1/patients/{patient_a_id}/export",
            headers={"Authorization": f"Bearer {token_b}"},
        )
        assert r.status_code == 403

        # ─────────────────────────────────────────────────
        # 6. Admin SI puede ver/modificar todo
        # ─────────────────────────────────────────────────
        r = client.get(
            f"/api/v1/patients/{patient_a_id}",
            headers={"Authorization": f"Bearer {token_admin}"},
        )
        assert r.status_code == 200, f"Admin debe ver cualquier paciente: {r.text}"

        # ─────────────────────────────────────────────────
        # 7. Profesional C (sin vinculo) ve pacientes huerfanos
        #    pero NO los de A
        # ─────────────────────────────────────────────────
        r = client.get(
            f"/api/v1/patients/{patient_orphan_id}",
            headers={"Authorization": f"Bearer {token_c}"},
        )
        assert r.status_code == 200, f"C debe ver paciente huerfano: {r.text}"

        r = client.get(
            f"/api/v1/patients/{patient_a_id}",
            headers={"Authorization": f"Bearer {token_c}"},
        )
        assert r.status_code == 403, f"C NO debe ver paciente de A (no es huerfano): {r.text}"

        # ─────────────────────────────────────────────────
        # 8. Audit: cada intento cross-tenant debe estar registrado
        # ─────────────────────────────────────────────────
        with db_session_factory() as db:
            denied_logs = (
                db.query(AuditLogORM)
                .filter(
                    AuditLogORM.action.in_(["access_denied", "update", "delete", "export"]),
                    AuditLogORM.entity_id == patient_a_id,
                )
                .all()
            )
            # Minimo esperado: 4 intentos de B bloqueados
            assert len(denied_logs) >= 4, f"Se esperaban >=4 logs cross-tenant, hay {len(denied_logs)}"

    def test_jwt_invalido_es_rechazado_en_todos_los_endpoints(
        self,
        client,
        db_session_factory,
    ):
        """Un JWT con firma incorrecta debe ser 401 en TODOS los endpoints."""
        from datetime import UTC, datetime, timedelta

        from jose import jwt

        user_id = str(uuid.uuid4())
        now = datetime.now(UTC)
        payload = {
            "sub": user_id,
            "role": "profesional",
            "type": "access",
            "jti": "fake-jti",
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(hours=1)).timestamp()),
            "username": "fake",
        }
        # Firmar con un secret incorrecto
        bad_token = jwt.encode(payload, "wrong-secret-key", algorithm="HS256")

        r = client.get(
            "/api/v1/patients/",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert r.status_code == 401

        r = client.get(
            f"/api/v1/patients/{uuid.uuid4()}",
            headers={"Authorization": f"Bearer {bad_token}"},
        )
        assert r.status_code == 401

    def test_sin_authorization_es_rechazado(
        self,
        client,
        db_session_factory,
    ):
        """Sin header Authorization, los endpoints devuelven 401."""
        r = client.get("/api/v1/patients/")
        assert r.status_code == 401

        r = client.get(f"/api/v1/patients/{uuid.uuid4()}")
        assert r.status_code == 401

        r = client.post(
            f"/api/v1/patients/{uuid.uuid4()}/export",
        )
        assert r.status_code == 401

    def test_authorization_malformado_es_rechazado(
        self,
        client,
        db_session_factory,
    ):
        """Headers Authorization malformados no bypassean la auth."""
        malformed = [
            "Bearer",
            "Bearer ",
            "bearer token-lowercase",
            "Token abc",
            "Basic " + "x" * 100,
            "Negotiate spnego",
        ]
        for header in malformed:
            r = client.get(
                "/api/v1/patients/",
                headers={"Authorization": header},
            )
            assert r.status_code == 401, f"'{header}' debe ser 401, dio {r.status_code}"
