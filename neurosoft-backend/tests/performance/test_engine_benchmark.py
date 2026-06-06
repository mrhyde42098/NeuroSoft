"""
tests/performance/test_engine_benchmark.py
===========================================
Benchmark del motor de baremos: mide rendimiento con cargas realistas.

Uso:
    python -m pytest tests/performance/test_engine_benchmark.py -v -s
"""

import json
import time
from datetime import date, timedelta
from pathlib import Path

import pytest


def _load_engine():
    from app.domain.clinical_engine.baremos_loader import BaremosLoader
    from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext

    baremo_path = Path("data") / "BD_NEURO_MAESTRA.json"
    if not baremo_path.exists():
        pytest.skip("BD_NEURO_MAESTRA.json no encontrada")

    loader = BaremosLoader.load(baremo_path)
    engine = ClinicalEngine(loader)

    # Cargar casos ground truth para usar puntajes realistas
    fixtures_dir = Path("tests") / "fixtures" / "casos_ground_truth"
    puntajes_list = []
    if fixtures_dir.exists():
        for f in sorted(fixtures_dir.glob("*.json"))[:5]:
            case = json.loads(f.read_text(encoding="utf-8"))
            if case.get("puntajes"):
                puntajes_list.append(
                    {
                        "puntajes": case["puntajes"],
                        "edad": case.get("edad", 45),
                        "sexo": case.get("sexo", "H"),
                        "escolaridad": case.get("escolaridad", "Profesional"),
                    }
                )

    if not puntajes_list:
        # Fallback: caso sintetico
        puntajes_list = [
            {
                "puntajes": {"NiWiscDC": 30, "NiWiscSem": 18, "NiWiscRDD": 14},
                "edad": 10,
                "sexo": "M",
                "escolaridad": "Primaria",
            }
        ]

    return engine, PatientContext, puntajes_list


@pytest.mark.benchmark
def test_benchmark_single_score():
    """Mide cuantas calificaciones por segundo puede hacer el motor."""
    engine, PatientContext, casos = _load_engine()
    puntajes = casos[0]["puntajes"]

    # Warmup
    today = date.today()
    birth = today - timedelta(days=casos[0]["edad"] * 365)
    for _ in range(5):
        ctx = PatientContext.from_demographics(
            birth_date=birth,
            evaluation_date=today,
            sexo=casos[0]["sexo"],
            escolaridad=casos[0]["escolaridad"],
        )
        engine.score("bench-1", puntajes, ctx)

    # Benchmark
    tiempos = []
    for _ in range(100):
        ctx = PatientContext.from_demographics(
            birth_date=birth,
            evaluation_date=today,
            sexo=casos[0]["sexo"],
            escolaridad=casos[0]["escolaridad"],
        )
        t0 = time.perf_counter()
        engine.score("bench-1", puntajes, ctx)
        tiempos.append(time.perf_counter() - t0)

    avg = sum(tiempos) / len(tiempos) * 1000
    per_second = 1 / (sum(tiempos) / len(tiempos))

    print(f"\n  Motor benchmark: {len(tiempos)} iteraciones")
    print(f"  Promedio:   {avg:.2f} ms por evaluacion")
    print(f"  Throughput: {per_second:.0f} evaluaciones/segundo")
    print(f"  Min: {min(tiempos) * 1000:.2f} ms  Max: {max(tiempos) * 1000:.2f} ms")

    assert avg < 500, f"Motor demasiado lento: {avg:.0f}ms (limite 500ms)"


def test_benchmark_1000_patients():
    """Simula calificar 1000 pacientes en secuencia."""
    engine, PatientContext, casos = _load_engine()

    today = date.today()
    birth = today - timedelta(days=45 * 365)  # ~45 anhos

    t0 = time.perf_counter()
    for i in range(1000):
        caso = casos[i % len(casos)]
        ctx = PatientContext.from_demographics(
            birth_date=birth,
            evaluation_date=today,
            sexo=caso["sexo"],
            escolaridad=caso["escolaridad"],
        )
        engine.score(f"bench-{i}", caso["puntajes"], ctx)
    elapsed = time.perf_counter() - t0

    per_second = 1000 / elapsed
    print(f"\n  1000 pacientes calificados en {elapsed:.2f}s ({per_second:.0f} pac/s)")

    assert elapsed < 60, f"1000 pacientes tomaron {elapsed:.1f}s (limite 60s)"
