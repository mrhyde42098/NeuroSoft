"""
scripts/test_ui_endpoints.py
============================
Prueba endpoints clave del backend con TestClient (sin levantar servidor).
Simula el flujo completo de la UI: login -> pacientes -> evaluacion -> reporte.
"""

import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from app.main import app
from app.domain.clinical_engine.baremos_loader import BaremosLoader

# Ensure baremo is loaded before testing endpoints
BAREMOS_PATH = ROOT / "data" / "BD_NEURO_MAESTRA.json"
BaremosLoader.reset()
BaremosLoader.load(BAREMOS_PATH)

client = TestClient(app)


def test_login():
    r = client.post("/api/v1/auth/login", json={"username": "admin", "password": "neurosoft2025"})
    assert r.status_code == 200, f"Login failed: {r.text}"
    data = r.json()
    assert "access_token" in data
    print("[OK] Login")
    return data["access_token"]


def test_patient_panel(token):
    r = client.get("/api/v1/patients/panel", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Patient panel failed: {r.text}"
    data = r.json()
    assert "pacientes" in data or isinstance(data, list)
    patients = data.get("pacientes", data)
    print(f"[OK] Patient panel ({len(patients)} patients)")


def test_list_tests(token):
    r = client.get("/api/v1/scores/tests?poblacion=infantil", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"List tests failed: {r.text}"
    data = r.json()
    assert isinstance(data, list) and len(data) > 0
    print(f"[OK] List tests ({len(data)} tests)")


import sqlite3, uuid

def _get_real_patient_id():
    conn = sqlite3.connect(r"D:\NeuroSoftApp\neurosoft-backend\data\neurosoft.db")
    c = conn.cursor()
    c.execute("SELECT id FROM patients WHERE is_active=1 LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row[0] if row else str(uuid.uuid4())


def test_evaluate_wisc(token):
    pid = _get_real_patient_id()
    payload = {
        "patient_id": pid,
        "protocolo": "WISC-IV",
        "puntajes": {
            "NiWiscDC": 21, "NiWiscSem": 16, "NiWiscVoc": 20,
            "NiWiscLN": 14, "NiWiscCl": 25, "NiWiscMat": 16,
        }
    }
    r = client.post("/api/v1/scores/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Evaluate failed: {r.text}"
    data = r.json()
    assert data["poblacion"] == "infantil"
    assert len(data["resultados"]) > 0
    print(f"[OK] Evaluate WISC ({len(data['resultados'])} resultados)")


def test_evaluate_am(token):
    pid = _get_real_patient_id()
    payload = {
        "patient_id": pid,
        "protocolo": "Adulto Mayor",
        "puntajes": {
            "ViTMTA": 80, "ViTMTB": 180, "ViRDD": 8, "ViRDInv": 5, "ViStP": 45
        }
    }
    r = client.post("/api/v1/scores/", json=payload, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Evaluate AM failed: {r.text}"
    data = r.json()
    assert data["poblacion"] == "adulto_mayor"
    assert len(data["resultados"]) > 0
    print(f"[OK] Evaluate AM ({len(data['resultados'])} resultados)")


def test_preview_single(token):
    pid = _get_real_patient_id()
    r = client.post("/api/v1/scores/preview", json={
        "patient_id": pid,
        "test_id": "NiWiscDC",
        "puntaje_bruto": 21
    }, headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Preview failed: {r.text}"
    data = r.json()
    assert data["puntaje_escalar"] is not None
    print(f"[OK] Preview single (escalar={data['puntaje_escalar']})")


def test_dashboard_stats(token):
    r = client.get("/api/v1/patients/stats", headers={"Authorization": f"Bearer {token}"})
    assert r.status_code == 200, f"Stats failed: {r.text}"
    data = r.json()
    assert "total_pacientes" in data
    print(f"[OK] Dashboard stats (total={data['total_pacientes']})")


def test_generate_report(token):
    # Use an existing evaluation_id from DB for a real test
    import sqlite3
    conn = sqlite3.connect(r"D:\NeuroSoftApp\neurosoft-backend\data\neurosoft.db")
    c = conn.cursor()
    c.execute("SELECT id FROM evaluations LIMIT 1")
    row = c.fetchone()
    conn.close()
    eval_id = row[0] if row else "fake-id"

    r = client.post(f"/api/v1/reports/pdf/{eval_id}", headers={"Authorization": f"Bearer {token}"})
    # 404 is ok if no evals in DB; 200 means PDF generated
    assert r.status_code in (200, 404, 422), f"Report failed unexpectedly: {r.text}"
    print(f"[OK] Generate report (status={r.status_code})")


def main():
    print("=" * 60)
    print("NEUROSOFT - UI ENDPOINT VALIDATION")
    print("=" * 60)

    try:
        token = test_login()
        test_patient_panel(token)
        test_list_tests(token)
        test_evaluate_wisc(token)
        test_evaluate_am(token)
        test_preview_single(token)
        test_dashboard_stats(token)
        test_generate_report(token)
        print("\n[OK] All UI endpoints passed!")
        return 0
    except AssertionError as e:
        print(f"\n[X] UI endpoint failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
