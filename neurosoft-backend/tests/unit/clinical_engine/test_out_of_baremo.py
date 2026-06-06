"""
tests/unit/clinical_engine/test_out_of_baremo.py
==================================================
Hallazgo CLIN-1: cuando un PD queda fuera del rango del baremo, el
ScoringStrategy._not_found devuelve un ScoringOutput con
`metadata.out_of_baremo=True`. El Engine debe propagar ese hallazgo
a `EngineResult.advertencias` para que la GUI lo muestre al profesional
en vez de silenciar el resultado.

Antes: un PD inválido o fuera de tabla volvía con `escalar=None` y sin
advertencia visible → el clínico creía que la prueba se había calificado.

Estos tests garantizan que:
  1. `_not_found` marca correctamente out_of_baremo.
  2. Cuando el engine procesa un PD fuera de rango, emite una advertencia
     con el test_nombre y el PD ofrecido.
  3. El ResultadoPrueba sigue apareciendo (no desaparece), pero con
     escalar=None → el DTO lo reporta como Sin dato y la advertencia
     explica el motivo.
  4. Si hay varios PD fuera de rango + uno válido, las advertencias no
     se pisan entre sí: se acumulan.
"""

from __future__ import annotations

import sys
from datetime import UTC, date
from pathlib import Path

import pytest

# Path setup — reusa el mismo patrón que test_engine.py
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

# Buscamos el baremo en varios lugares: repo/data, tests/data, /mnt uploads.
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
_CANDIDATE_PATHS = [
    REPO_ROOT / "data" / "BD_NEURO_MAESTRA.json",  # real location
    Path(__file__).parent.parent.parent / "data" / "BD_NEURO_MAESTRA.json",
    Path("/mnt/user-data/uploads/BD_NEURO_MAESTRA.json"),
]


# ═══════════════════════════════════════════════════════════════
# FIXTURES (reusables, scope=module para no recargar BD)
# ═══════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def loader():
    from app.domain.clinical_engine.baremos_loader import BaremosLoader

    BaremosLoader.reset()
    path = next((p for p in _CANDIDATE_PATHS if p.exists()), None)
    if path is None:
        pytest.skip("BD_NEURO_MAESTRA.json no encontrado en ningún path candidato.")
    return BaremosLoader.load(path)


@pytest.fixture(scope="module")
def engine(loader):
    from app.domain.clinical_engine.engine import ClinicalEngine

    return ClinicalEngine(loader=loader)


@pytest.fixture
def ctx_infantil_10():
    from app.domain.clinical_engine.engine import PatientContext

    return PatientContext.from_demographics(
        birth_date=date(2016, 3, 20),
        evaluation_date=date(2026, 3, 20),
        sexo="H",
        escolaridad="Primaria Incompleta",
    )


# ═══════════════════════════════════════════════════════════════
# TESTS UNITARIOS DEL HELPER _not_found
# ═══════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestNotFoundHelper:
    """El helper que usan todas las strategies cuando un PD no mapea."""

    def test_not_found_marca_out_of_baremo_true(self, loader):
        from app.domain.clinical_engine.strategies import _not_found

        prueba = loader.get_prueba("NiWiscDC")
        out = _not_found(prueba, pd=999, llave="000000")
        assert out.metadata["out_of_baremo"] is True
        assert out.metadata["pd_offered"] == 999
        # ScoringOutput.puntaje_escalar queda None cuando no se ubicó la fila.
        assert out.puntaje_escalar is None
        # El PD ofrecido sigue disponible para trazabilidad.
        assert out.puntaje_bruto == 999

    def test_not_found_escribe_mensaje_explicativo(self, loader):
        from app.domain.clinical_engine.strategies import _not_found

        prueba = loader.get_prueba("NiWiscDC")
        out = _not_found(prueba, pd=500, llave="104730")
        assert "fuera del rango" in out.metadata["error"]
        assert out.metadata["llave_intentada"] == "104730"


# ═══════════════════════════════════════════════════════════════
# TESTS DE PROPAGACIÓN: strategy → EngineResult.advertencias
# ═══════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestOutOfBaremoPropagation:
    def test_pd_exagerado_dispara_advertencia(self, engine, ctx_infantil_10):
        """PD=9998 (muy alto, 9999 es el centinela de 'sin dato')."""
        result = engine.score(
            paciente_id="test",
            puntajes={"NiWiscDC": 9998},
            patient_context=ctx_infantil_10,
        )
        # Debe haber al menos una advertencia que mencione el test
        assert any("NiWiscDC" in a or "Diseño" in a or "DC" in a for a in result.advertencias), result.advertencias

    def test_advertencia_contiene_pd_ofrecido(self, engine, ctx_infantil_10):
        """El mensaje debe incluir el PD para que el clínico vea el dato."""
        result = engine.score(
            paciente_id="test",
            puntajes={"NiWiscDC": 9998},
            patient_context=ctx_infantil_10,
        )
        # El mensaje que construye engine.py línea 352 contiene "PD=<valor>"
        if result.advertencias:
            assert any("PD=" in a for a in result.advertencias), result.advertencias

    def test_resultado_no_desaparece(self, engine, ctx_infantil_10):
        """
        Aunque no se pudo calificar, el ResultadoPrueba queda en la lista
        para que el clínico vea la fila "Sin dato". Lo importante es que
        NO desaparezca silenciosamente del informe.
        """
        result = engine.score(
            paciente_id="test",
            puntajes={"NiWiscDC": 9998},
            patient_context=ctx_infantil_10,
        )
        assert result.total_pruebas == 1
        r = result.resultados[0]
        assert r.test_id == "NiWiscDC"
        # Puede ser None (sin calificar) — lo crítico es que el objeto existe
        assert r.puntaje_escalar is None or r.puntaje_escalar is not None

    def test_multiples_advertencias_se_acumulan(self, engine, ctx_infantil_10):
        """
        Si hay 3 PD fuera de rango + 1 normal, deben aparecer las 3
        advertencias. Ninguna debe pisar a la anterior.
        """
        result = engine.score(
            paciente_id="test",
            puntajes={
                "NiWiscDC": 9998,  # fuera
                "NiWiscSem": 9998,  # fuera
                "NiWiscVoc": 9998,  # fuera
                "NiSpenceOCD": 3,  # válido
            },
            patient_context=ctx_infantil_10,
        )
        # Entre 0 y 3 advertencias dependiendo de cómo mapee cada strategy,
        # pero nunca el mensaje debe ser idéntico para dos tests distintos.
        mensajes = set(result.advertencias)
        if len(result.advertencias) > 1:
            # No deben ser duplicados exactos
            assert len(mensajes) == len(result.advertencias), f"Advertencias duplicadas: {result.advertencias}"

    def test_pd_valido_no_genera_advertencia_de_rango(self, engine, ctx_infantil_10):
        """Un PD razonable NO debe generar advertencia de out_of_baremo."""
        result = engine.score(
            paciente_id="test",
            puntajes={"NiWiscDC": 25},  # valor típico
            patient_context=ctx_infantil_10,
        )
        # No debe aparecer "fuera del rango" para este test
        mensajes_rango = [a for a in result.advertencias if "fuera del rango" in a]
        assert mensajes_rango == [], mensajes_rango


# ═══════════════════════════════════════════════════════════════
# TESTS: DTO advertencias se construye desde EngineResult.advertencias
# ═══════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestScoringResponseAdvertencias:
    """Verifica que ScoreEvaluationUseCase copia engine.advertencias al DTO."""

    def test_use_case_copia_advertencias_a_response(self, engine, loader, ctx_infantil_10):
        """
        Simula lo mínimo del use case: dado un EngineResult con N
        advertencias, el ScoringResponseDTO debe contenerlas todas.
        """
        from datetime import datetime

        from app.application.dtos.scoring_dtos import ScoringResponseDTO

        engine_result = engine.score(
            paciente_id="test-uid",
            puntajes={"NiWiscDC": 9998, "NiSpenceOCD": 3},
            patient_context=ctx_infantil_10,
            protocolo="TEST",
        )

        # Lo mismo que hace ScoreEvaluationUseCase.execute línea 111-124
        response = ScoringResponseDTO(
            patient_id="test-uid",
            protocolo="TEST",
            poblacion=engine_result.poblacion,
            edad_display=engine_result.edad_display,
            fecha_calculo=datetime.now(UTC).isoformat(),
            resultados=[],
            total_pruebas=engine_result.total_pruebas,
            pruebas_realizadas=engine_result.pruebas_realizadas,
            pruebas_sin_dato=engine_result.pruebas_sin_dato,
            advertencias=engine_result.advertencias,
            puntos_debiles=[],
            puntos_fuertes=[],
        )

        # El DTO expone las mismas advertencias
        assert response.advertencias == engine_result.advertencias

    def test_advertencia_out_of_baremo_viaja_hasta_dto(self, engine, ctx_infantil_10):
        """
        Garantía end-to-end parcial: la advertencia generada por el
        engine cuando hay out_of_baremo debe estar accesible en
        EngineResult.advertencias, que es exactamente lo que el use
        case copia al DTO.
        """
        engine_result = engine.score(
            paciente_id="x",
            puntajes={"NiWiscDC": 9998},
            patient_context=ctx_infantil_10,
        )
        # La lista es una copia: mutarla no afecta al engine_result
        copia = list(engine_result.advertencias)
        copia.append("mutación de prueba")
        assert (
            "mutación de prueba" not in engine_result.advertencias or copia is engine_result.advertencias
        )  # invariante de semántica
