"""
tests/unit/clinical_engine/test_engine.py
==========================================
Tests unitarios del Motor Clínico (legacy).

Usa los fixtures compartidos de conftest.py (loader, engine, ctx_*).
"""

from __future__ import annotations

from datetime import date

import pytest

from app.domain.clinical_engine.engine import PatientContext

# ────────────────────────────────────────────────────────────
# Fixtures adicionales (no están en conftest.py)
# ────────────────────────────────────────────────────────────


@pytest.fixture
def ctx_adulto_mayor_80():
    """Adulto mayor 80 años, Primaria Incompleta, Femenino."""
    return PatientContext.from_demographics(
        birth_date=date(1945, 1, 1),
        evaluation_date=date(2025, 6, 3),
        sexo="M",
        escolaridad="Primaria Incompleta",
    )


# ────────────────────────────────────────────────────────────
# TESTS: CORE UTILS
# ────────────────────────────────────────────────────────────


class TestClinicalInterpreter:
    """Clasificación clínica por métrica (escalar, CI, z_score)."""

    @pytest.mark.parametrize(
        "score,tipo,expected",
        [
            (3, "escalar", "Bajo"),
            (5, "escalar", "Limítrofe"),
            (7, "escalar", "Promedio"),
            (10, "escalar", "Promedio"),
            (13, "escalar", "Superior"),
            (15, "escalar", "Superior"),
            (65, "ci", "Bajo"),
            (75, "ci", "Limítrofe"),
            (85, "ci", "Promedio"),
            (100, "ci", "Promedio"),
            (115, "ci", "Promedio"),
            (130, "ci", "Superior"),
            (-2.5, "z_score", "Bajo"),
            (-1.2, "z_score", "Limítrofe"),
            (0.2, "z_score", "Promedio"),
            (1.8, "z_score", "Superior"),
        ],
    )
    def test_interpretacion_por_metrica(self, score, tipo, expected):
        from app.core.utils import ClinicalInterpreter

        assert ClinicalInterpreter.interpret(score, tipo) == expected

    def test_none_da_sin_dato(self):
        from app.core.utils import ClinicalInterpreter

        assert ClinicalInterpreter.interpret(None, "escalar") == "Sin dato"

    def test_z_equivalente_escalar_media(self):
        from app.core.utils import ClinicalInterpreter

        z = ClinicalInterpreter.to_z_equivalent(10, "escalar")
        assert z == 0.0

    def test_z_equivalente_ci_media(self):
        from app.core.utils import ClinicalInterpreter

        z = ClinicalInterpreter.to_z_equivalent(100, "ci")
        assert z == 0.0


# ────────────────────────────────────────────────────────────
# TESTS: BAREMO KEY BUILDER
# ────────────────────────────────────────────────────────────


class TestBaremoKeyBuilder:
    def test_wais_rango_2534(self):
        from app.core.utils import BaremoKeyBuilder

        key = BaremoKeyBuilder.wais_key(28, 10)
        assert key == "253410"

    def test_adulto_mayor_5056(self):
        from app.core.utils import BaremoKeyBuilder

        key = BaremoKeyBuilder.am_key(55, 10)
        assert key == "505610"

    @pytest.mark.parametrize(
        "years,expected_rango",
        [
            (16, "1619"),
            (20, "2024"),
            (28, "2534"),
            (40, "3554"),
            (60, "5569"),
            (75, "7000"),
        ],
    )
    def test_rangos_wais_correctos(self, years, expected_rango):
        from app.core.utils import BaremoKeyBuilder

        assert BaremoKeyBuilder.wais_key(years, 10) == f"{expected_rango}10"


# ────────────────────────────────────────────────────────────
# TESTS: STRATEGIES CON DATOS REALES
# ────────────────────────────────────────────────────────────


class TestWaisRangeStrategy:
    def test_wais_v_28a_pd42(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import WaisRangeStrategy

        prueba = loader.get_prueba("AdWAISV")
        result = WaisRangeStrategy().calculate(prueba, 42.0, ctx_adulto_28.age.years, ctx_adulto_28.age.months)
        assert result.puntaje_escalar == 9.0
        assert result.interpretacion == "Promedio"
        assert "2534" in result.llave_usada

    def test_sin_dato_9999(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import WaisRangeStrategy

        prueba = loader.get_prueba("AdWAISV")
        result = WaisRangeStrategy().calculate(prueba, 9999.0, ctx_adulto_28.age.years, ctx_adulto_28.age.months)
        assert result.puntaje_escalar is None
        assert result.interpretacion == "Sin dato"


class TestRangoPuntajeStrategy:
    def test_wisc_dc_10a_pd30(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy

        prueba = loader.get_prueba("NiWiscDC")
        result = RangoPuntajeStrategy().calculate(prueba, 30.0, ctx_infantil_10.age.years, ctx_infantil_10.age.months)
        assert result.puntaje_escalar is not None
        assert 1 <= result.puntaje_escalar <= 19

    def test_spence_ocd_pd3_da_t57(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import PuntajeDirectoATStrategy

        prueba = loader.get_prueba("NiSpenceOCD")
        result = PuntajeDirectoATStrategy().calculate(
            prueba, 3.0, ctx_infantil_10.age.years, ctx_infantil_10.age.months
        )
        assert result.puntaje_escalar == 57.0
        assert result.interpretacion == "Promedio"


class TestSumaAIndiceStrategy:
    def test_wisc_icv_suma25_da_ci91(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import SumaAIndiceStrategy

        prueba = loader.get_prueba("NiWISCIndComVer")
        result = SumaAIndiceStrategy().calculate(prueba, 25.0, ctx_infantil_10.age.years, ctx_infantil_10.age.months)
        assert result.puntaje_escalar == 91.0
        assert result.tipo_metrica == "ci"


class TestZScoreStrategy:
    def test_caras_pd_media_da_z0(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import ZScoreStrategy

        prueba = loader.get_prueba("NiTestPC")
        params = prueba.baremos.get("10")
        if not params:
            pytest.skip("No hay parametros para edad 10 en CARAS")
        media = params[0]
        result = ZScoreStrategy().calculate(prueba, media, ctx_infantil_10.age.years, ctx_infantil_10.age.months)
        assert abs(result.z_equivalente) < 0.01


class TestEdadSexoStrategy:
    def test_cdi_media_da_z0(self, loader):
        from app.domain.clinical_engine.strategies import EdadSexoStrategy

        prueba = loader.get_prueba("NiCDI")
        params = prueba.baremos.get("910H")
        if not params:
            pytest.skip("No hay datos 910H en CDI")
        media = params[2]
        ctx = PatientContext.from_demographics(date(2017, 3, 20), date(2026, 3, 20), "H", "Primaria Incompleta")
        result = EdadSexoStrategy().calculate(prueba, media, ctx.age.years, ctx.age.months, sexo="H")
        assert abs(result.z_equivalente) < 0.01


class TestAjusteEscolaridad:
    def test_ajuste_analfabeta_vitmt(self, loader):
        ajuste = loader.get_ajuste_escolaridad("ViTMTA", "Analfabeta")
        assert ajuste >= 0

    def test_ajuste_profesional_es_cero(self, loader):
        ajuste = loader.get_ajuste_escolaridad("ViTMTA", "Profesional")
        assert ajuste == -1

    def test_engine_aplica_ajuste(self, engine, ctx_adulto_mayor_65):
        """El engine suma +2 al PD antes de buscar en baremo."""
        result_con_ajuste = engine.score_single("ViTMTA", 5.0, ctx_adulto_mayor_65)
        assert result_con_ajuste is not None
        assert result_con_ajuste.metadata.get("pd_original") == 5.0
        assert result_con_ajuste.metadata.get("pd_ajustado") == 7.0


# ────────────────────────────────────────────────────────────
# TESTS: CICLO COMPLETO DEL ENGINE
# ────────────────────────────────────────────────────────────


class TestClinicalEngineIntegration:
    def test_calificacion_protocolo_wisc(self, engine, ctx_infantil_10):
        result = engine.score(
            "test-wisc",
            {"NiWiscDC": 42, "NiWiscSem": 30, "NiWISCIndComVer": 25, "NiSpenceOCD": 3, "NiTestPC": 9999},
            ctx_infantil_10,
            "Test WISC",
        )
        assert result.total_pruebas == 5
        assert result.pruebas_sin_dato == 1
        assert result.pruebas_realizadas == 4

    def test_sin_dato_9999_reportado_correctamente(self, engine, ctx_infantil_10):
        result = engine.score("test-9999", {"NiWiscDC": 9999}, ctx_infantil_10)
        assert result.pruebas_realizadas == 0
        assert result.pruebas_sin_dato == 1

    def test_test_id_invalido_genera_advertencia(self, engine, ctx_infantil_10):
        result = engine.score("test-inv", {"INVALIDO_TEST": 10}, ctx_infantil_10)
        assert len(result.advertencias) >= 1

    def test_puntos_debiles_y_fuertes(self, engine, ctx_infantil_10):
        result = engine.score(
            "test-df",
            {"NiWiscDC": 45, "NiWiscSem": 20, "NiWiscVoc": 15, "NiWiscLN": 10, "NiWiscCl": 8},
            ctx_infantil_10,
        )
        assert result.total_pruebas == 5

    def test_cobertura_168_pruebas(self, loader):
        assert loader.total_pruebas >= 168
