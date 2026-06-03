"""
tests/integration/test_rehab_pdf.py
=====================================
Cobertura del endpoint POST /api/v1/rehab/plans/{id}/pdf y del generador
en `app/infrastructure/rehab_pdf_service.py`.

Casos:
  1. Plan firmado → 200 + bytes PDF (signature: %PDF-).
  2. Plan en borrador → 409 Conflict.
  3. Plan inexistente → 404.
  4. Generador acepta plan firmado y rechaza borrador (ValueError).
"""
from __future__ import annotations

import uuid
from datetime import UTC, date, datetime

import pytest

# ─────────────────────────────────────────────────────────────
# Helpers (replicados de test_rehab.py para mantener
# independencia de fixtures cruzadas)
# ─────────────────────────────────────────────────────────────

def _make_patient(db, doc="REHABPDF1", first="Lucia"):
    from app.infrastructure.database.orm_models import PatientORM
    p = PatientORM(
        id=str(uuid.uuid4()),
        numero_documento=doc,
        tipo_documento="CC",
        primer_nombre=first,
        primer_apellido="Test",
        fecha_nacimiento=date(2010, 1, 1),
        sexo="M",
        escolaridad="Primaria Incompleta",
        lateralidad="Diestro",
        fecha_atencion=date(2026, 3, 20),
        is_active=True,
        created_at=datetime.now(UTC),
    )
    db.add(p)
    db.flush()
    return p


def _create_and_sign_plan(db, patient_id):
    from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
    from app.application.use_cases.rehab_use_cases import (
        CreateRehabPlanUseCase,
        SignRehabPlanUseCase,
        seed_activity_catalog,
    )
    seed_activity_catalog(db)
    dto = RehabPlanCreateDTO(
        patient_id=patient_id,
        fecha_inicio=date(2026, 4, 1),
        frecuencia_semanal=3,
        objetivos="Mejorar atención sostenida y memoria de trabajo",
        dominios=["atencion", "memoria_trabajo"],
        actividades=[
            {"slug": "stroop", "dificultad": 2},
            {"slug": "n_back", "dificultad": 1, "parametros": {"n": 1}},
        ],
        notas="Sesiones de 30 minutos en horario vespertino.",
    )
    plan = CreateRehabPlanUseCase(db).execute(dto)
    db.commit()
    signed = SignRehabPlanUseCase(db).execute(
        plan_id=plan["id"], actor_id="prof-01", actor_label="Dra. Prueba",
    )
    db.commit()
    return signed


def _create_unsigned_plan(db, patient_id):
    from app.application.dtos.rehab_dtos import RehabPlanCreateDTO
    from app.application.use_cases.rehab_use_cases import (
        CreateRehabPlanUseCase,
        seed_activity_catalog,
    )
    seed_activity_catalog(db)
    dto = RehabPlanCreateDTO(
        patient_id=patient_id,
        fecha_inicio=date(2026, 4, 1),
        objetivos="Borrador inicial",
        dominios=["atencion"],
    )
    plan = CreateRehabPlanUseCase(db).execute(dto)
    db.commit()
    return plan


# ─────────────────────────────────────────────────────────────
# Tests del generador puro (sin HTTP)
# ─────────────────────────────────────────────────────────────

@pytest.mark.integration
class TestRehabPDFGenerator:

    def test_generator_devuelve_bytes_pdf_para_plan_firmado(self, in_memory_db):
        from app.infrastructure.database.orm_models import PatientORM, RehabPlanORM
        from app.infrastructure.rehab_pdf_service import generate_rehab_plan_pdf

        p = _make_patient(in_memory_db)
        in_memory_db.commit()
        signed = _create_and_sign_plan(in_memory_db, p.id)

        plan_orm = in_memory_db.get(RehabPlanORM, signed["id"])
        patient_orm = in_memory_db.get(PatientORM, p.id)

        pdf = generate_rehab_plan_pdf(plan=plan_orm, patient=patient_orm)
        assert isinstance(pdf, bytes)
        assert pdf.startswith(b"%PDF-"), "el output debe empezar con la firma PDF"
        assert len(pdf) > 1000, "un PDF mínimo de 1 página debe pesar > 1 KB"

    def test_generator_rechaza_plan_borrador(self, in_memory_db):
        from app.infrastructure.database.orm_models import PatientORM, RehabPlanORM
        from app.infrastructure.rehab_pdf_service import generate_rehab_plan_pdf

        p = _make_patient(in_memory_db, doc="REHABPDF2", first="Carlos")
        in_memory_db.commit()
        plan = _create_unsigned_plan(in_memory_db, p.id)
        plan_orm = in_memory_db.get(RehabPlanORM, plan["id"])
        patient_orm = in_memory_db.get(PatientORM, p.id)

        with pytest.raises(ValueError, match="no está firmado"):
            generate_rehab_plan_pdf(plan=plan_orm, patient=patient_orm)


# ─────────────────────────────────────────────────────────────
# Tests del endpoint vía TestClient
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app_client():
    from fastapi.testclient import TestClient

    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(app_client):
    """Reutiliza el admin sembrado en el startup de la app."""
    r = app_client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "neurosoft2025",
    })
    if r.status_code == 401:
        pytest.skip("Admin password no es 'neurosoft2025' en este entorno")
    assert r.status_code == 200, r.text
    return r.json()["access_token"]


def _auth(token):
    return {"Authorization": f"Bearer {token}"}


def _seed_via_api(client, token, signed=True):
    """Crea un paciente + plan vía HTTP. Devuelve (patient_id, plan_id)."""
    pat = client.post("/api/v1/patients/", headers=_auth(token), json={
        "numero_documento": f"PDF{uuid.uuid4().hex[:6].upper()}",
        "tipo_documento": "CC",
        "primer_nombre": "Test",
        "primer_apellido": "PDFRehab",
        "fecha_nacimiento": "2010-01-01",
        "sexo": "M",
        "escolaridad": "Primaria Incompleta",
        "lateralidad": "Diestro",
        "fecha_atencion": "2026-03-20",
    })
    assert pat.status_code in (200, 201), pat.text
    pid = pat.json()["id"]

    plan = client.post("/api/v1/rehab/plans", headers=_auth(token), json={
        "patient_id": pid,
        "fecha_inicio": "2026-04-01",
        "frecuencia_semanal": 2,
        "objetivos": "Atención sostenida",
        "dominios": ["atencion"],
        "actividades": [{"slug": "stroop", "dificultad": 1}],
    })
    assert plan.status_code in (200, 201), plan.text
    plan_id = plan.json()["id"]

    if signed:
        s = client.post(
            f"/api/v1/rehab/plans/{plan_id}/sign",
            headers=_auth(token),
            json={"confirm": True, "note": "Firma de prueba"},
        )
        assert s.status_code == 200, s.text
    return pid, plan_id


@pytest.mark.integration
class TestRehabPDFEndpoint:

    def test_plan_firmado_devuelve_pdf_200(self, app_client, admin_token):
        _, plan_id = _seed_via_api(app_client, admin_token, signed=True)
        r = app_client.post(
            f"/api/v1/rehab/plans/{plan_id}/pdf",
            headers=_auth(admin_token),
        )
        assert r.status_code == 200, r.text
        assert r.headers["content-type"].startswith("application/pdf")
        body = r.content
        assert body.startswith(b"%PDF-")
        assert len(body) > 1000

    def test_plan_borrador_devuelve_409(self, app_client, admin_token):
        _, plan_id = _seed_via_api(app_client, admin_token, signed=False)
        r = app_client.post(
            f"/api/v1/rehab/plans/{plan_id}/pdf",
            headers=_auth(admin_token),
        )
        assert r.status_code == 409, r.text
        assert "borrador" in r.json()["detail"].lower()

    def test_plan_inexistente_devuelve_404(self, app_client, admin_token):
        r = app_client.post(
            f"/api/v1/rehab/plans/{uuid.uuid4()}/pdf",
            headers=_auth(admin_token),
        )
        assert r.status_code == 404
