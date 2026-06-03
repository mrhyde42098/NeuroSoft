"""
tests/integration/test_casos_ground_truth.py
=============================================
§P2 (mayo 2026) — Test de regresión clínica usando snapshots ground truth.

Itera los 15 fixtures en `tests/fixtures/casos_ground_truth/` y verifica que
el motor de scoring produce los escalares esperados para cada caso.

Si este test falla, hay regresión clínica: algún baremo, estrategia o
ajuste cambió respecto al snapshot validado. Antes de marcar como "fix"
revisar:
    1. ¿Hubo modificación intencional en BD_NEURO_MAESTRA.json?
    2. ¿Se tocó strategies.py o engine.py?
    3. ¿La actualización del fixture es legítima?

Para regenerar fixtures tras un cambio intencional:
    cd D:\\NeuroSoftApp
    venv/Scripts/python docs/casos-clinicos/validar_casos.py
    # luego: re-correr el script que generó fixtures (ver §P2 sprint mayo 2026)
"""
from __future__ import annotations

import json
from datetime import date
from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures" / "casos_ground_truth"


def _iter_fixtures():
    for path in sorted(FIXTURES_DIR.glob("caso_*.json")):
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        yield pytest.param(data, id=f"caso_{data['caso_id']:02d}_{data['nombre_paciente'].split()[0]}")


@pytest.mark.integration
@pytest.mark.parametrize("fixture", list(_iter_fixtures()))
def test_caso_ground_truth(fixture):
    """Valida que el motor reproduce los escalares esperados del snapshot."""
    from app.core.config import settings
    from app.domain.clinical_engine.baremos_loader import BaremosLoader
    from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext

    loader = BaremosLoader.load(settings.baremo_path)
    engine = ClinicalEngine(loader)

    fn = date.fromisoformat(fixture["fecha_nacimiento"])
    fe = date.fromisoformat(fixture["fecha_evaluacion"])
    ctx = PatientContext.from_demographics(
        birth_date=fn, evaluation_date=fe,
        sexo=fixture["sexo"], escolaridad=fixture["escolaridad"],
    )

    result = engine.score(
        paciente_id=f"caso_{fixture['caso_id']}",
        puntajes=fixture["puntajes_input"],
        patient_context=ctx,
    )

    # Indexar resultados por test_id
    actuales = {r.test_id: r.puntaje_escalar for r in result.resultados}
    esperados = fixture["escalares_esperados"]

    # Verificar que TODOS los esperados están presentes y coinciden
    fallos = []
    for tid, esc_esperado in esperados.items():
        actual = actuales.get(tid)
        if actual is None:
            fallos.append(f"  - {tid}: esperado {esc_esperado}, motor devolvió None (sin_norma/out_of_baremo)")
        elif abs(float(actual) - float(esc_esperado)) > 0.01:
            fallos.append(f"  - {tid}: esperado {esc_esperado}, motor devolvió {actual}")

    if fallos:
        msg = (
            f"\n=== Regresión clínica en caso {fixture['caso_id']} ({fixture['nombre_paciente']}, {fixture['perfil_clinico']}) ===\n"
            + "\n".join(fallos)
            + f"\n\nTotal escalares esperados: {len(esperados)} | Fallos: {len(fallos)}"
            + "\n\nSi el cambio fue intencional, regenerar fixtures con validar_casos.py + script §P2."
        )
        pytest.fail(msg)


@pytest.mark.integration
def test_fixtures_existen_15_casos():
    """Verificación meta: hay exactamente 15 fixtures (no se borró ni añadió ninguno)."""
    files = list(FIXTURES_DIR.glob("caso_*.json"))
    assert len(files) == 15, f"Se esperaban 15 fixtures, hay {len(files)}"


@pytest.mark.integration
def test_fixtures_cubren_todas_poblaciones():
    """Los 15 casos deben cubrir infantil + adulto_joven + adulto_mayor."""
    poblaciones_esperadas = {"infantil", "adulto_joven", "adulto_mayor"}
    poblaciones_vistas = set()
    for path in FIXTURES_DIR.glob("caso_*.json"):
        with open(path, encoding="utf-8") as f:
            fx = json.load(f)
        fn = date.fromisoformat(fx["fecha_nacimiento"])
        fe = date.fromisoformat(fx["fecha_evaluacion"])
        edad = fe.year - fn.year - ((fe.month, fe.day) < (fn.month, fn.day))
        pob = "infantil" if edad < 18 else "adulto_joven" if edad < 50 else "adulto_mayor"
        poblaciones_vistas.add(pob)
    faltantes = poblaciones_esperadas - poblaciones_vistas
    assert not faltantes, f"Faltan poblaciones en los fixtures: {faltantes}"
