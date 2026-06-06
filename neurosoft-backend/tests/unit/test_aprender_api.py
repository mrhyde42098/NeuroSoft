"""Tests para API Centro de Aprendizaje (/api/v1/aprender/)."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app

    return TestClient(app)


def test_aprender_stats(client):
    r = client.get("/api/v1/aprender/stats")
    assert r.status_code == 200
    data = r.json()
    assert data["glosario_count"] >= 120
    assert data["articulos_count"] >= 11
    assert data["paths_count"] >= 4
    assert "version" in data


def test_aprender_paths(client):
    r = client.get("/api/v1/aprender/paths")
    assert r.status_code == 200
    data = r.json()
    assert data["total"] >= 4
    assert isinstance(data["paths"], list)
    first = data["paths"][0]
    assert "id" in first
    assert "pasos" in first
    assert len(first["pasos"]) >= 1


def test_openapi_aprender_paths():
    from app.main import app

    schema = app.openapi()
    assert "/api/v1/aprender/stats" in schema["paths"]
    assert "/api/v1/aprender/paths" in schema["paths"]
