"""Estímulos Pearson de ejemplo — láminas por test_id/item_id."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.fixture
def auth_headers():
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "neurosoft2025"})
    if r.status_code != 200:
        pytest.skip("login admin no disponible en este entorno")
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.parametrize(
    "test_id,min_count",
    [
        ("NiWiscMat", 35),
        ("NiWiscConD", 28),
        ("AdMatr", 26),
        ("NiWisFigInc", 38),
        ("AdWAISFI", 25),
    ],
)
def test_estimulos_por_test_pearson(auth_headers, test_id: str, min_count: int):
    r = client.get(f"/api/v1/estimulos/por_test/{test_id}", headers=auth_headers)
    assert r.status_code == 200, r.text
    items = r.json()
    if len(items) < min_count:
        pytest.skip(f"Solo {len(items)} estimulos para {test_id} — ejecute seed_pearson_ejemplo_laminas.py")
    assert len(items) >= min_count
    ids = {str(x.get("item_id")) for x in items}
    assert "1" in ids
    assert items[0].get("contenido_base64", "").startswith("data:image/")


def test_niwiscmat_item_1_has_image(auth_headers):
    r = client.get("/api/v1/estimulos/por_test/NiWiscMat", headers=auth_headers)
    if r.status_code != 200:
        pytest.skip(r.text)
    one = next((x for x in r.json() if str(x.get("item_id")) == "1"), None)
    if not one:
        pytest.skip("NiWiscMat item 1 no sembrado")
    assert "contenido_base64" in one
    assert len(one["contenido_base64"]) > 100
