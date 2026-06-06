"""Regresión audit 2026-06: advertencias etarias + fuera de baremo coexisten."""

from __future__ import annotations

from datetime import date

import pytest

from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext


@pytest.fixture
def ctx_adulto_mayor_65():
    return PatientContext.from_demographics(
        birth_date=date(1960, 6, 1),
        evaluation_date=date(2026, 6, 1),
        sexo="H",
        escolaridad="Profesional",
    )


@pytest.mark.unit
def test_advertencia_edad_y_out_of_baremo_coexisten(engine: ClinicalEngine, ctx_adulto_mayor_65):
    result = engine.score(
        paciente_id="test",
        puntajes={"NiWiscSem": 9998},
        patient_context=ctx_adulto_mayor_65,
    )
    edad = [a for a in result.advertencias if "baremado para" in a]
    baremo = [a for a in result.advertencias if "fuera del rango del baremo" in a]
    assert len(edad) >= 1, result.advertencias
    assert len(baremo) >= 1, result.advertencias
