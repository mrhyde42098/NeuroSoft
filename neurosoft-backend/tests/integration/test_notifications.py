"""
tests/integration/test_notifications.py
==========================================
Smoke tests para Sprint 10 (notificaciones telerehab) y overlays
extendidos del Sprint 9.
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
    r = client.post(
        "/api/v1/auth/login",
        json={
            "username": "admin",
            "password": "neurosoft2025",
        },
    )
    if r.status_code == 401:
        pytest.skip("Admin password no es 'neurosoft2025' en este entorno")
    return r.json()["access_token"]


def _auth(t):
    return {"Authorization": f"Bearer {t}"}


@pytest.mark.integration
class TestNotifications:
    def test_rutas_registradas(self, client):
        from app.main import app

        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/notifications" in paths
        assert "/api/v1/notifications/count" in paths
        assert "/api/v1/notifications/adherence/summary" in paths

    def test_list_requiere_token(self, client):
        r = client.get("/api/v1/notifications")
        assert r.status_code == 401

    def test_count_requiere_token(self, client):
        r = client.get("/api/v1/notifications/count")
        assert r.status_code == 401

    def test_adherence_requiere_token(self, client):
        r = client.get("/api/v1/notifications/adherence/summary")
        assert r.status_code == 401

    def test_list_devuelve_array(self, client, admin_token):
        r = client.get("/api/v1/notifications", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)

    def test_count_estructura(self, client, admin_token):
        r = client.get("/api/v1/notifications/count?dias=7", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert "count" in body
        assert "cutoff" in body
        assert isinstance(body["count"], int)

    def test_count_con_since(self, client, admin_token):
        r = client.get("/api/v1/notifications/count?since=2025-01-01T00:00:00Z", headers=_auth(admin_token))
        assert r.status_code == 200

    def test_adherence_summary_estructura(self, client, admin_token):
        r = client.get("/api/v1/notifications/adherence/summary?dias=14", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert "periodo_dias" in body
        assert "total_pacientes" in body
        assert "promedio_adherencia" in body
        assert "pacientes" in body
        assert isinstance(body["pacientes"], list)

    def test_dias_param_validation(self, client, admin_token):
        r = client.get("/api/v1/notifications?dias=200", headers=_auth(admin_token))
        # Max 90 días
        assert r.status_code == 422


@pytest.mark.integration
class TestBaremosOverlays:
    def test_overlays_route_registered(self, client):
        from app.main import app

        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/baremos/overlays" in paths

    def test_overlays_requiere_token(self, client):
        r = client.get("/api/v1/baremos/overlays")
        assert r.status_code == 401

    def test_overlays_devuelve_lista(self, client, admin_token):
        r = client.get("/api/v1/baremos/overlays", headers=_auth(admin_token))
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body, list)
        # Los overlays pueden estar vacíos (la carpeta sólo tiene README)
        # pero el endpoint debe responder OK.

    def test_overlays_module_works_standalone(self):
        """Verifica que el helper de discovery funciona."""
        from pathlib import Path

        from app.domain.clinical_engine.baremos_overlays import discover_overlays

        # Carpeta inexistente → []
        result = discover_overlays(Path("/no/existe"))
        assert result == []

    def test_baremos_info_incluye_overlays(self, client, admin_token):
        r = client.get("/api/v1/baremos/info", headers=_auth(admin_token))
        # Puede ser 503 si loader no cargó
        if r.status_code == 200:
            body = r.json()
            assert "overlays_disponibles" in body
            assert "overlay_count" in body
            assert isinstance(body["overlay_count"], int)
