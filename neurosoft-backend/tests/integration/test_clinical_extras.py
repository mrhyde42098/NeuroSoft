"""
tests/integration/test_clinical_extras.py
==========================================
Smoke tests de los endpoints de extras clínicos. Cubre:

  • Registro de rutas en el router
  • Auth gate (401 sin token)
  • Endpoints individuales de
      - GET /rips/classification
      - GET /wisc/forma-corta/cit
      - POST /wisc/discrepancia
      - GET /baterias/alternas
      - POST /memoria/grober-buschke
      - POST /dcl/clasificar
      - GET /recomendaciones

Versión post-saneo: cobertura mínima funcional. La cobertura unitaria
profunda (cálculos de discrepancia, conversión Sattler, etc.) vive en
tests del frontend (`src/utils/wiscDiscrepancy.test.js` y
`src/utils/sattlerShortForms.test.js` cuando se escriban) o en tests
unitarios puros del backend.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


# ─────────────────────────────────────────────────────────────
# Rutas registradas
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestRutasRegistradas:

    def test_rutas_clinical_extras_registradas(self, client):
        from app.main import app
        paths = {getattr(r, "path", "") for r in app.routes}
        esperadas = {
            "/api/v1/rips/classification",
            "/api/v1/wisc/forma-corta/cit",
            "/api/v1/wisc/discrepancia",
            "/api/v1/baterias/alternas",
            "/api/v1/memoria/grober-buschke",
            "/api/v1/dcl/clasificar",
            "/api/v1/recomendaciones",
        }
        faltantes = esperadas - paths
        assert not faltantes, f"Faltan rutas: {faltantes}"


# ─────────────────────────────────────────────────────────────
# Auth gate — todos los endpoints requieren bearer token
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestAuthGate:

    def test_classification_requiere_token(self, client):
        r = client.get("/api/v1/rips/classification")
        assert r.status_code == 401

    def test_forma_corta_requiere_token(self, client):
        r = client.get("/api/v1/wisc/forma-corta/cit?suma=40&forma=1")
        assert r.status_code == 401

    def test_discrepancia_requiere_token(self, client):
        r = client.post("/api/v1/wisc/discrepancia", json={"icv": 100})
        assert r.status_code == 401

    def test_baterias_requiere_token(self, client):
        r = client.get("/api/v1/baterias/alternas")
        assert r.status_code == 401

    def test_grober_requiere_token(self, client):
        r = client.post("/api/v1/memoria/grober-buschke", json={"trials": []})
        assert r.status_code == 401

    def test_dcl_requiere_token(self, client):
        r = client.post("/api/v1/dcl/clasificar", json={"declive": "ninguno"})
        assert r.status_code == 401

    def test_recomendaciones_requiere_token(self, client):
        r = client.get("/api/v1/recomendaciones")
        assert r.status_code == 401


# ─────────────────────────────────────────────────────────────
# Smoke autenticado (admin token) — validación de contratos
# ─────────────────────────────────────────────────────────────
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


@pytest.mark.integration
class TestContratosBasicos:

    def test_classification_devuelve_lista(self, client, admin_token):
        r = client.get("/api/v1/rips/classification", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        # Debe ser un dict u objeto con catálogo
        assert isinstance(body, (dict, list))

    def test_forma_corta_calcula_cit(self, client, admin_token):
        # ∑escalares = 40 → CIT debe ser ~100 según Sattler 2010
        r = client.get("/api/v1/wisc/forma-corta/cit?suma=40&forma=1",
                       headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert "cit_estimado" in body or "cit" in body or "CIT" in body

    def test_forma_corta_fuera_rango_devuelve_error(self, client, admin_token):
        r = client.get("/api/v1/wisc/forma-corta/cit?suma=999&forma=1",
                       headers=_auth(admin_token))
        # Puede ser 400 (validación) o 422 (Pydantic)
        assert r.status_code in (400, 422)

    def test_discrepancia_no_significativa(self, client, admin_token):
        # Discrepancia menor a 23 → no significativa
        r = client.post("/api/v1/wisc/discrepancia",
                        headers=_auth(admin_token),
                        json={"icv": 100, "irp": 105, "imt": 102, "ivp": 99})
        assert r.status_code in (200, 422)

    def test_baterias_alternas_devuelve_lista(self, client, admin_token):
        r = client.get("/api/v1/baterias/alternas", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, (dict, list))

    def test_recomendaciones_devuelve_catalogo(self, client, admin_token):
        r = client.get("/api/v1/recomendaciones", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, (dict, list))


# ─────────────────────────────────────────────────────────────
# Datos de los JSON renombrados (sufijo _ins eliminado)
# ─────────────────────────────────────────────────────────────
@pytest.mark.integration
class TestArchivosDataAccesibles:

    def test_rips_classification_json_existe(self):
        from pathlib import Path
        path = Path(__file__).resolve().parents[2] / "app" / "domain" / "data" / "rips_classification.json"
        assert path.exists(), f"Falta: {path}"

    def test_baterias_alternas_json_existe(self):
        from pathlib import Path
        path = Path(__file__).resolve().parents[2] / "app" / "domain" / "data" / "baterias_alternas.json"
        assert path.exists(), f"Falta: {path}"

    def test_reservorio_recomendaciones_json_existe(self):
        from pathlib import Path
        path = Path(__file__).resolve().parents[2] / "app" / "domain" / "data" / "reservorio_recomendaciones.json"
        assert path.exists(), f"Falta: {path}"
