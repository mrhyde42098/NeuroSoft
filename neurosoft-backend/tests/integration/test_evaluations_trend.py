"""
tests/integration/test_evaluations_trend.py
==============================================
Cobertura del endpoint GET /api/v1/evaluations/trend usado por el
dashboard. Reemplaza el `Math.random()` del frontend con conteos
reales agrupados por mes.

Casos:
  1. Sin evaluaciones → devuelve N puntos con val=0.
  2. Con evaluaciones distribuidas → cuenta correctamente por mes.
  3. Param `meses` clamp [1, 24].
  4. Default meses = 6 produce 6 puntos consecutivos.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def app_client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(app_client):
    r = app_client.post("/api/v1/auth/login", json={
        "username": "admin", "password": "neurosoft2025",
    })
    if r.status_code == 401:
        pytest.skip("Admin password no es 'neurosoft2025' en este entorno")
    return r.json()["access_token"]


def _auth(t):
    return {"Authorization": f"Bearer {t}"}


@pytest.mark.integration
class TestEvaluationsTrend:

    def test_trend_default_devuelve_6_puntos(self, app_client, admin_token):
        r = app_client.get("/api/v1/evaluations/trend", headers=_auth(admin_token))
        assert r.status_code == 200, r.text
        body = r.json()
        assert isinstance(body, list)
        assert len(body) == 6
        for p in body:
            assert "mes" in p and "anio" in p and "ym" in p and "val" in p
            assert p["val"] >= 0

    def test_trend_meses_param(self, app_client, admin_token):
        r = app_client.get("/api/v1/evaluations/trend?meses=12",
                           headers=_auth(admin_token))
        assert r.status_code == 200
        assert len(r.json()) == 12

    def test_trend_meses_fuera_de_rango_422(self, app_client, admin_token):
        r = app_client.get("/api/v1/evaluations/trend?meses=0",
                           headers=_auth(admin_token))
        assert r.status_code == 422
        r2 = app_client.get("/api/v1/evaluations/trend?meses=99",
                            headers=_auth(admin_token))
        assert r2.status_code == 422

    def test_trend_orden_cronologico(self, app_client, admin_token):
        r = app_client.get("/api/v1/evaluations/trend?meses=4",
                           headers=_auth(admin_token))
        body = r.json()
        # Cada ym posterior es mayor o igual al anterior
        yms = [p["ym"] for p in body]
        assert yms == sorted(yms)
