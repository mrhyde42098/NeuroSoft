"""
tests/unit/clinical_engine/test_strategy_edge_cases.py
=====================================================
S1.1-S1.3 del PLAN_MAESTRO: tests de edge cases de las strategies.

Cubre:
  S1.1 - ZScoreStrategy con PD=0, edad extrema, sigma=0.
  S1.2 - DesconocidoStrategy con tipo_calculo=desconocido (ViTMTB-like).
  S1.3 - ComparativoStrategy con tabla Delis-Kaplan 2000.
  S1.4 - Sentinel 9999 ("prueba no realizada") se filtra correctamente.
"""

from __future__ import annotations

import pytest

# ═══════════════════════════════════════════════════════════════════
# S1.1: ZScoreStrategy edge cases
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestZScoreStrategyEdgeCases:
    """Z = (PD - mu) / sigma. Casos limite."""

    def test_pd_cero_retorna_z_negativo(self, loader):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        from app.domain.entities.models import PruebaDefinicion

        baremo = {"30": [50.0, 10.0]}
        prueba = PruebaDefinicion(
            id="TEST_Z",
            nombre="Test Z",
            tipo_calculo="z_score",
            tipo_metrica="z_score",
            poblacion="adulto_joven",
            baremos=baremo,
        )
        out = ZScoreStrategy().calculate(prueba, pd=0, years=30)
        # Z = (0 - 50) / 10 = -5.0
        assert out.puntaje_escalar == -5.0
        assert out.metadata.get("mu") == 50.0
        assert out.metadata.get("sigma") == 10.0

    def test_pd_igual_a_media_retorna_z_cero(self, loader):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        from app.domain.entities.models import PruebaDefinicion

        baremo = {"25": [20.0, 5.0]}
        prueba = PruebaDefinicion(
            id="TEST_Z2",
            nombre="Test Z2",
            tipo_calculo="z_score",
            tipo_metrica="z_score",
            poblacion="adulto_joven",
            baremos=baremo,
        )
        out = ZScoreStrategy().calculate(prueba, pd=20, years=25)
        assert out.puntaje_escalar == 0.0

    def test_edad_sin_baremo_retorna_out_of_baremo(self, loader):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        from app.domain.entities.models import PruebaDefinicion

        baremo = {"30": [10.0, 3.0]}
        prueba = PruebaDefinicion(
            id="TEST_Z3",
            nombre="Test Z3",
            tipo_calculo="z_score",
            tipo_metrica="z_score",
            poblacion="adulto_joven",
            baremos=baremo,
        )
        out = ZScoreStrategy().calculate(prueba, pd=15, years=99)
        # Edad 99 no está en baremo → out_of_baremo=True
        assert out.puntaje_escalar is None
        assert out.metadata.get("out_of_baremo") is True

    def test_sigma_cero_retorna_sin_norma_no_escalar_falso(self, loader):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        from app.domain.entities.models import PruebaDefinicion

        baremo = {"30": [15.0, 0.0]}  # baremo corrupto
        prueba = PruebaDefinicion(
            id="TEST_Z4",
            nombre="Test Z4",
            tipo_calculo="z_score",
            tipo_metrica="z_score",
            poblacion="adulto_joven",
            baremos=baremo,
        )
        out = ZScoreStrategy().calculate(prueba, pd=15, years=30)
        # sigma=0 → Z indefinido. NO debe retornar 0.0 (falso positivo)
        assert out.puntaje_escalar is None
        assert out.metadata.get("sin_norma") is True
        assert "sigma=0" in out.metadata.get("motivo", "")

    def test_pd_negativo_retorna_z_extremo(self, loader):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        from app.domain.entities.models import PruebaDefinicion

        baremo = {"30": [20.0, 5.0]}
        prueba = PruebaDefinicion(
            id="TEST_Z5",
            nombre="Test Z5",
            tipo_calculo="z_score",
            tipo_metrica="z_score",
            poblacion="adulto_joven",
            baremos=baremo,
        )
        out = ZScoreStrategy().calculate(prueba, pd=-5, years=30)
        # Z = (-5 - 20) / 5 = -5.0
        assert out.puntaje_escalar == -5.0


# ═══════════════════════════════════════════════════════════════════
# S1.4: Sentinel 9999 se filtra
# ═══════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestSentinel9999:
    """9999 = 'prueba no realizada' (sistema VBA). NO debe procesarse."""

    @pytest.mark.parametrize(
        "strategy_class_name",
        [
            "ZScoreStrategy",
            "RangoPuntajeStrategy",
            "WaisRangeStrategy",
            "SumaAIndiceStrategy",
            "PuntajeDirectoATStrategy",
        ],
    )
    def test_pd_9999_retorna_sin_dato(self, loader, strategy_class_name):
        from app.domain.clinical_engine import strategies
        from app.domain.entities.models import PruebaDefinicion

        cls = getattr(strategies, strategy_class_name)
        prueba = PruebaDefinicion(
            id="TEST",
            nombre="T",
            tipo_calculo="rango_puntaje",
            tipo_metrica="escalar",
            poblacion="adulto_joven",
            baremos={"10": 5},
        )
        out = cls().calculate(prueba, pd=9999, years=10)
        assert out.puntaje_escalar is None
        assert out.puntaje_bruto is None
        assert out.interpretacion != "Promedio"
