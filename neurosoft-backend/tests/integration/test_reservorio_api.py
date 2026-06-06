"""
Tests para el endpoint /api/v1/reservorio.
Sprint D — expone el banco de recomendaciones clínicas como API REST.
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def admin_token(client):
    import os

    password = os.getenv("NEUROSOFT_ADMIN_PASSWORD", "test-admin-password")
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": password})
    assert r.status_code == 200, f"Login falló: {r.text}"
    return r.json()["access_token"]


@pytest.fixture
def auth_headers(admin_token):
    return {"Authorization": f"Bearer {admin_token}"}


class TestReservorioInfo:
    def test_info_sin_auth_401(self, client):
        r = client.get("/api/v1/reservorio/info")
        assert r.status_code in (401, 403)

    def test_info_con_auth(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/info", headers=auth_headers)
        assert r.status_code == 200
        j = r.json()
        assert j["total_cuadros"] >= 20
        assert "infantil" in j["cuadros_por_grupo"]
        assert "adulto_mayor" in j["cuadros_por_grupo"]
        assert j["version"]  # no vacía


class TestReservorioList:
    def test_list_todos(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros", headers=auth_headers)
        assert r.status_code == 200
        j = r.json()
        assert j["total"] >= 20
        assert j["filtro_poblacion"] is None
        # Cada cuadro tiene grupo, id, label, n_recomendaciones
        for c in j["cuadros"]:
            assert {"grupo", "id", "label", "n_recomendaciones"} <= set(c)

    def test_list_filtrado_infantil(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros?poblacion=infantil", headers=auth_headers)
        assert r.status_code == 200
        j = r.json()
        assert j["total"] >= 5
        for c in j["cuadros"]:
            assert c["grupo"] == "infantil"

    def test_list_filtrado_adulto_mayor(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros?poblacion=adulto_mayor", headers=auth_headers)
        assert r.status_code == 200
        j = r.json()
        assert j["total"] >= 8
        for c in j["cuadros"]:
            assert c["grupo"] == "adulto_mayor"

    def test_list_filtro_inexistente(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros?poblacion=extraterrestre", headers=auth_headers)
        assert r.status_code == 200
        assert r.json()["total"] == 0


class TestReservorioDetalle:
    def test_cuadro_existe(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros/infantil/tdah", headers=auth_headers)
        assert r.status_code == 200
        j = r.json()
        assert j["id"] == "tdah"
        assert j["grupo"] == "infantil"
        assert len(j["recomendaciones"]) >= 5

    def test_cuadro_no_existe_404(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros/infantil/noexiste", headers=auth_headers)
        assert r.status_code == 404
        assert "Disponibles" in r.json()["detail"]

    def test_grupo_no_existe_404(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/cuadros/marte/tdah", headers=auth_headers)
        assert r.status_code == 404


class TestReservorioSugerir:
    """Heurística data-driven de sugerencia de cuadros."""

    def test_sugerir_am_con_grober_severo(self, client, auth_headers):
        """Adulto mayor con Grober severo → Alzheimer."""
        resultados = [
            {"test_id": "ViGroberML", "tipo_metrica": "memoria", "dominio_cognitivo": "Memoria", "z_equivalente": -2.8},
            {
                "test_id": "ViGroberRLT",
                "tipo_metrica": "memoria",
                "dominio_cognitivo": "Memoria",
                "z_equivalente": -2.5,
            },
        ]
        r = client.get(
            "/api/v1/reservorio/sugerir",
            params={
                "resultados": json.dumps(resultados),
                "poblacion": "adulto_mayor",
            },
            headers=auth_headers,
        )
        assert r.status_code == 200
        j = r.json()
        assert j["n_sugerencias"] >= 1
        ids = [s["id"] for s in j["sugerencias"]]
        assert any("alzheimer" in i or "demencia" in i for i in ids)

    def test_sugerir_infantil_con_tdah_screen(self, client, auth_headers):
        """Infantil con SNAP + atencion/FEE descendidas → TDAH."""
        resultados = [
            {
                "test_id": "NiSNAP",
                "tipo_metrica": "tdah_screen",
                "dominio_cognitivo": "Atención",
                "z_equivalente": 2.0,
                "pd": 28,
            },
            {"test_id": "NiWiscDC", "tipo_metrica": "atencion", "dominio_cognitivo": "Atención", "z_equivalente": -1.8},
            {
                "test_id": "NiWiscCl",
                "tipo_metrica": "ffee",
                "dominio_cognitivo": "Funciones Ejecutivas",
                "z_equivalente": -1.5,
            },
        ]
        r = client.get(
            "/api/v1/reservorio/sugerir",
            params={
                "resultados": json.dumps(resultados),
                "poblacion": "infantil",
            },
            headers=auth_headers,
        )
        assert r.status_code == 200
        j = r.json()
        ids = [s["id"] for s in j["sugerencias"]]
        assert "tdah" in ids

    def test_sugerir_resultados_vacios(self, client, auth_headers):
        r = client.get(
            "/api/v1/reservorio/sugerir",
            params={
                "resultados": "[]",
                "poblacion": "adulto",
            },
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert r.json()["n_sugerencias"] >= 0

    def test_sugerir_json_invalido_400(self, client, auth_headers):
        r = client.get(
            "/api/v1/reservorio/sugerir",
            params={
                "resultados": "{not json",
                "poblacion": "adulto",
            },
            headers=auth_headers,
        )
        assert r.status_code == 400

    def test_sugerir_sin_param_422(self, client, auth_headers):
        r = client.get("/api/v1/reservorio/sugerir", headers=auth_headers)
        assert r.status_code == 422
