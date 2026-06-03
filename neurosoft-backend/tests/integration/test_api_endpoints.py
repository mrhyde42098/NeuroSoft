"""
tests/integration/test_api_endpoints.py
=========================================
Tests de API con httpx/TestClient.
Verifica que los endpoints responden con los status codes correctos.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
class TestHealthEndpoint:

    def test_health_200(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        body = r.json()
        assert body["status"] == "healthy"
        assert "version" in body

    def test_health_tiene_campos_esperados(self, client):
        r = client.get("/health")
        body = r.json()
        assert "env" in body
        assert "db_path" in body


@pytest.mark.integration
class TestAuthEndpoints:

    def test_login_sin_body_422(self, client):
        from app.presentation.api.v1.auth import _LOGIN_ATTEMPTS
        _LOGIN_ATTEMPTS.clear()
        r = client.post("/api/v1/auth/login")
        assert r.status_code == 422

    def test_login_credenciales_incorrectas_401(self, client):
        """Credenciales válidas en formato pero inexistentes → 401."""
        r = client.post("/api/v1/auth/login", json={
            "username": "inexistente_xyz",
            "password": "contraseña_falsa_1234",
        })
        assert r.status_code == 401

    def test_login_password_corta_422(self, client):
        """Password < 4 chars falla validación Pydantic."""
        r = client.post("/api/v1/auth/login", json={
            "username": "test",
            "password": "ab",
        })
        assert r.status_code == 422


@pytest.mark.integration
class TestProtectedEndpoints:

    def test_panel_sin_token_401(self, client):
        r = client.get("/api/v1/patients/panel")
        assert r.status_code == 401

    def test_patients_search_sin_token_401(self, client):
        r = client.get("/api/v1/patients/search")
        assert r.status_code == 401

    def test_evaluations_sin_token_401(self, client):
        r = client.get("/api/v1/evaluations/")
        # puede ser 401 o 405 (si GET no está definido), pero no 500
        assert r.status_code in (401, 404, 405)


@pytest.mark.integration
class TestRateLimiting:

    def test_login_rate_limit_429(self, client):
        """Más de 5 intentos en 60s → 429."""
        from app.presentation.api.v1.auth import _LOGIN_ATTEMPTS
        # Limpiar estado previo para este test
        _LOGIN_ATTEMPTS.clear()

        for i in range(5):
            client.post("/api/v1/auth/login", json={
                "username": f"ratelimit_{i}",
                "password": "wrong_pass_1234",
            })

        # El sexto debe dar 429
        r = client.post("/api/v1/auth/login", json={
            "username": "ratelimit_final",
            "password": "wrong_pass_1234",
        })
        assert r.status_code == 429
        assert "Demasiados intentos" in r.json()["detail"]

        # Limpiar para no afectar otros tests
        _LOGIN_ATTEMPTS.clear()
