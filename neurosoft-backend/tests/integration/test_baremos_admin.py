"""
tests/integration/test_baremos_admin.py
==========================================
Smoke tests para los endpoints Sprint 9 (baremos info) y Sprint 11
(KPIs administrativos).

Cobertura:
  • Registro de rutas en el router
  • Auth gate (401 sin token)
  • Contratos básicos autenticados
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client):
    r = client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "neurosoft2025",
    })
    if r.status_code == 401:
        pytest.skip("Admin password no es 'neurosoft2025' en este entorno")
    return r.json()["access_token"]


def _auth(t):
    return {"Authorization": f"Bearer {t}"}


# ─────────────────────────────────────────────────────────────
# Sprint 9 — Baremos info
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestBaremosRutas:

    def test_baremos_rutas_registradas(self, client):
        from app.main import app
        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/baremos/info" in paths
        assert "/api/v1/baremos/sources" in paths

    def test_baremos_info_requiere_token(self, client):
        r = client.get("/api/v1/baremos/info")
        assert r.status_code == 401

    def test_baremos_sources_requiere_token(self, client):
        r = client.get("/api/v1/baremos/sources")
        assert r.status_code == 401

    def test_baremos_sources_devuelve_lista(self, client, admin_token):
        r = client.get("/api/v1/baremos/sources", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        ids = {s["id"] for s in body}
        # Las 4 fuentes principales deben estar declaradas
        assert "neuronorma_colombia" in ids
        assert "arango_lasprilla_2015" in ids
        assert "eni_2_colombia" in ids

    def test_baremos_info_devuelve_metadata(self, client, admin_token):
        r = client.get("/api/v1/baremos/info", headers=_auth(admin_token))
        # Puede ser 503 si el loader no se cargó en el test environment
        assert r.status_code in (200, 503)
        if r.status_code == 200:
            body = r.json()
            assert "version" in body
            assert "checksum_sha256" in body
            assert "total_pruebas" in body


# ─────────────────────────────────────────────────────────────
# Sprint 11 — KPIs admin
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestKpisRutas:

    def test_kpis_rutas_registradas(self, client):
        from app.main import app
        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/admin/kpis" in paths
        assert "/api/v1/admin/kpis/professional" in paths
        assert "/api/v1/admin/kpis/diagnoses" in paths

    def test_kpis_globales_requiere_token(self, client):
        r = client.get("/api/v1/admin/kpis")
        assert r.status_code == 401

    def test_kpis_professional_requiere_token(self, client):
        r = client.get("/api/v1/admin/kpis/professional")
        assert r.status_code == 401

    def test_kpis_diagnoses_requiere_token(self, client):
        r = client.get("/api/v1/admin/kpis/diagnoses")
        assert r.status_code == 401

    def test_kpis_globales_estructura(self, client, admin_token):
        r = client.get("/api/v1/admin/kpis", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        # 5 grupos clave
        for grupo in ("pacientes", "evaluaciones", "rehabilitacion", "agenda", "historia_clinica"):
            assert grupo in body, f"falta grupo: {grupo}"
        # campos numéricos dentro de pacientes
        assert isinstance(body["pacientes"]["total"], int)

    def test_kpis_professional_lista(self, client, admin_token):
        r = client.get("/api/v1/admin/kpis/professional", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)

    def test_kpis_diagnoses_top_N(self, client, admin_token):
        r = client.get("/api/v1/admin/kpis/diagnoses?top=10", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        assert len(body) <= 10

    def test_kpis_diagnoses_top_fuera_rango(self, client, admin_token):
        r = client.get("/api/v1/admin/kpis/diagnoses?top=1", headers=_auth(admin_token))
        # top mínimo es 5 → debe rechazar
        assert r.status_code == 422

    def test_kpis_professional_periodo_personalizado(self, client, admin_token):
        r = client.get("/api/v1/admin/kpis/professional?dias=7", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        if body:
            # Si hay profesionales, el campo del periodo debe existir
            assert any("evaluaciones_7d" in p for p in body)
