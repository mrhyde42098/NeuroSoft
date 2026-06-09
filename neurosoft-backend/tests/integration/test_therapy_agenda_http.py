"""HTTP integration — therapy sessions y agenda (jun 2026)."""

from __future__ import annotations

import uuid
from datetime import date

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client):
    import os

    from app.infrastructure.auth.auth_service import UserRepository, hash_password
    from app.infrastructure.database.engine import SessionLocal
    from app.infrastructure.database.orm_models import UserORM

    password = os.getenv("NEUROSOFT_ADMIN_PASSWORD", "neurosoft2025")
    with SessionLocal() as db:
        admin = db.query(UserORM).filter_by(username="admin").first()
        if admin is None:
            UserRepository(db).create(
                username="admin",
                password_plain=password,
                nombre_completo="Administrador",
                role="admin",
            )
            db.commit()
        else:
            admin.hashed_password = hash_password(password)
            admin.is_active = True
            db.commit()
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": password})
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _create_patient(client, token, doc: str | None = None) -> str:
    doc = doc or f"TA{uuid.uuid4().hex[:8]}"
    r = client.post(
        "/api/v1/patients/",
        headers=_auth(token),
        json={
            "tipo_documento": "CC",
            "numero_documento": doc,
            "primer_nombre": "Test",
            "primer_apellido": "Agenda",
            "fecha_nacimiento": "2010-05-01",
            "sexo": "H",
            "escolaridad": "Primaria Incompleta",
            "lateralidad": "Diestro",
            "fecha_atencion": str(date.today()),
        },
    )
    assert r.status_code in (200, 201), r.text
    return r.json()["id"]


@pytest.mark.integration
class TestTherapyHttp:
    def test_sessions_list_requires_auth(self, client):
        r = client.get("/api/v1/therapy/sessions?patient_id=x")
        assert r.status_code == 401

    def test_patch_session_modalidad_duracion(self, client, admin_token):
        pid = _create_patient(client, admin_token)
        create = client.post(
            "/api/v1/therapy/sessions",
            headers=_auth(admin_token),
            json={
                "patient_id": pid,
                "fecha": str(date.today()),
                "modalidad": "presencial",
                "duracion_min": 50,
            },
        )
        assert create.status_code == 201, create.text
        sid = create.json()["id"]
        patch = client.patch(
            f"/api/v1/therapy/sessions/{sid}",
            headers=_auth(admin_token),
            json={"modalidad": "telepsicologia", "duracion_min": 45},
        )
        assert patch.status_code == 200, patch.text
        body = patch.json()
        assert body["modalidad"] == "telepsicologia"
        assert body["duracion_min"] == 45


@pytest.mark.integration
class TestAgendaHttp:
    def test_create_and_list_appointment(self, client, admin_token):
        pid = _create_patient(client, admin_token)
        today = str(date.today())
        create = client.post(
            "/api/v1/agenda/",
            headers=_auth(admin_token),
            json={
                "patient_id": pid,
                "fecha": today,
                "hora_inicio": "09:00",
                "hora_fin": "10:00",
                "tipo_cita": "evaluacion",
                "modalidad": "presencial",
            },
        )
        assert create.status_code == 201, create.text
        listed = client.get(
            f"/api/v1/agenda/?fecha_desde={today}&fecha_hasta={today}",
            headers=_auth(admin_token),
        )
        assert listed.status_code == 200, listed.text
        ids = {a["id"] for a in listed.json()}
        assert create.json()["id"] in ids


@pytest.mark.integration
class TestEvaluationSignHttp:
    def test_sign_and_signature_status(self, client, admin_token):
        pid = _create_patient(client, admin_token)
        score = client.post(
            "/api/v1/scores/",
            headers=_auth(admin_token),
            json={
                "patient_id": pid,
                "protocolo": "WISC-IV",
                "puntajes": {"NiWiscDC": 42},
            },
        )
        assert score.status_code == 200, score.text
        eid = score.json()["evaluation_id"]
        before = client.get(
            f"/api/v1/evaluations/detail/{eid}/signature",
            headers=_auth(admin_token),
        )
        assert before.status_code == 200
        assert before.json()["signed"] is False
        sign = client.post(
            f"/api/v1/evaluations/detail/{eid}/sign",
            headers=_auth(admin_token),
            json={"confirm": True},
        )
        assert sign.status_code == 200, sign.text
        assert sign.json()["signed"] is True
        after = client.get(
            f"/api/v1/evaluations/detail/{eid}/signature",
            headers=_auth(admin_token),
        )
        assert after.json()["signed"] is True
        assert after.json()["valid"] is True
