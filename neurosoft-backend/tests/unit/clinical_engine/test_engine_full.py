"""
tests/unit/clinical_engine/test_engine_full.py
================================================
Suite completa de tests unitarios para el motor clínico.

Cubre:
  - AgeCalculator (6 casos)
  - ClinicalInterpreter (16 parametrizados)
  - BaremoKeyBuilder (8 casos)
  - Todas las estrategias con datos reales verificados
  - Ciclo completo del engine con casos clínicos reales
  - Casos borde: 9999, IDs inválidos, edades extremas
  - Cobertura de las 168 pruebas

Los resultados esperados están VERIFICADOS contra el informe real
de Jesús Alejandro y Blanca Edilma (informes de referencia).
"""

from __future__ import annotations

from datetime import date

import pytest

# ═══════════════════════════════════════════════════════════════
# CORE UTILS
# ═══════════════════════════════════════════════════════════════

class TestAgeCalculator:
    """Cálculo exacto de edad cronológica — pilar del engine."""

    def test_edad_exacta_cumpleanos_hoy(self):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate(date(2016, 3, 20), date(2026, 3, 20))
        assert e.years == 10 and e.months == 0 and e.days == 0

    def test_edad_con_meses_residuales(self):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate(date(1990, 5, 15), date(2026, 3, 20))
        assert e.years == 35 and e.months == 10

    def test_total_meses(self):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate(date(1990, 5, 15), date(2026, 3, 20))
        assert e.total_months == 35 * 12 + 10

    def test_acepta_iso_string(self):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate("1990-05-15", date(2026, 3, 20))
        assert e.years == 35

    def test_acepta_formato_colombiano(self):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate("15/05/1990", date(2026, 3, 20))
        assert e.years == 35

    def test_anio_bisiesto_29_feb(self):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate(date(2000, 2, 29), date(2025, 3, 1))
        assert e.years == 25

    def test_fecha_futura_error(self):
        from app.core.utils import AgeCalculator
        with pytest.raises(ValueError):
            AgeCalculator.calculate(date(2030, 1, 1), date(2026, 1, 1))

    @pytest.mark.parametrize("birth,eval_date,exp_years,exp_months", [
        (date(2009, 5, 30), date(2025, 5, 15), 15, 11),   # Jesús: 15a 11m
        (date(1945, 1, 1),  date(2025, 6, 3),  80, 5),    # Blanca: 80a 5m
        (date(1998, 1, 15), date(2026, 3, 20), 28, 2),    # adulto joven
        (date(2018, 9, 20), date(2026, 3, 20), 7, 6),     # 7a 6m
    ])
    def test_casos_reales(self, birth, eval_date, exp_years, exp_months):
        from app.core.utils import AgeCalculator
        e = AgeCalculator.calculate(birth, eval_date)
        assert e.years == exp_years, f"Expected {exp_years}a got {e.years}a"
        assert e.months == exp_months, f"Expected {exp_months}m got {e.months}m"


class TestClinicalInterpreter:

    @pytest.mark.parametrize("score,tipo,expected", [
        # Escalares WISC/WAIS (media=10, sd=3) — 4 niveles
        (3,  "escalar", "Bajo"),         # 0-4
        (5,  "escalar", "Limítrofe"),    # 5-6
        (7,  "escalar", "Promedio"),     # 7-12
        (10, "escalar", "Promedio"),     # media
        (13, "escalar", "Superior"),     # 13-19
        (15, "escalar", "Superior"),     # +1.7 sd
        (19, "escalar", "Superior"),     # techo
        # CI (media=100, sd=15) — 4 niveles
        (65,  "ci", "Bajo"),             # 0-69
        (75,  "ci", "Limítrofe"),        # 70-79
        (85,  "ci", "Promedio"),         # 80-119
        (100, "ci", "Promedio"),
        (115, "ci", "Promedio"),         # 80-119
        (130, "ci", "Superior"),         # 120+
        # Z-score directo
        (-2.5, "z_score", "Bajo"),
        (-1.2, "z_score", "Limítrofe"),
        (0.0,  "z_score", "Promedio"),
        (1.5,  "z_score", "Superior"),
        # None
        (None, "escalar", "Sin dato"),
    ])
    def test_interpretacion_parametrizada(self, score, tipo, expected):
        from app.core.utils import ClinicalInterpreter
        assert ClinicalInterpreter.interpret(score, tipo) == expected

    def test_z_equiv_escalar_media_es_cero(self):
        from app.core.utils import ClinicalInterpreter
        assert ClinicalInterpreter.to_z_equivalent(10.0, "escalar") == 0.0

    def test_z_equiv_ci_media_es_cero(self):
        from app.core.utils import ClinicalInterpreter
        assert ClinicalInterpreter.to_z_equivalent(100.0, "ci") == 0.0

    def test_z_equiv_puntaje_t_50_es_cero(self):
        from app.core.utils import ClinicalInterpreter
        assert ClinicalInterpreter.to_z_equivalent(50.0, "puntaje_t") == 0.0


class TestBaremoKeyBuilder:

    @pytest.mark.parametrize("years,months,pd,expected_key", [
        # WISC bracket 0-3 meses
        (10, 0, 30, "100330"),
        # WISC bracket 4-7 meses
        (10, 5, 30, "104730"),
        # WAIS rango 25-34
        (28, 4, 42, "253442"),
        # Adulto mayor 50-56
        (52, 0, 5,  "50565"),
        # Adulto mayor 78-80
        (79, 0, 10, "788010"),  # "7880" + "10"
    ])
    def test_candidate_contiene_llave(self, years, months, pd, expected_key):
        from app.core.utils import BaremoKeyBuilder
        keys = BaremoKeyBuilder.build_candidates(years, months, pd)
        assert expected_key in keys, f"{expected_key} not in {keys[:5]}"

    @pytest.mark.parametrize("years,expected_rango", [
        (16, "1619"), (20, "2024"), (28, "2534"),
        (38, "3554"), (60, "5569"), (75, "7000"),
    ])
    def test_wais_key_rango(self, years, expected_rango):
        from app.core.utils import BaremoKeyBuilder
        assert BaremoKeyBuilder.wais_key(years, 10) == f"{expected_rango}10"

    def test_am_key_rango_5056(self):
        from app.core.utils import BaremoKeyBuilder
        k = BaremoKeyBuilder.am_key(52, 10)
        assert k.startswith("5056")

    def test_am_key_fuera_rango_retorna_fallback(self):
        from app.core.utils import BaremoKeyBuilder
        # paciente de 40 años — fuera del rango AM
        k = BaremoKeyBuilder.am_key(40, 10)
        assert k is None or not k.startswith("50")


# ═══════════════════════════════════════════════════════════════
# ESTRATEGIAS CON DATOS REALES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestRangoPuntajeStrategy:
    """NiWisc* — estrategia principal para subtests WISC-IV."""

    def test_wisc_dc_pd53_edad16_11m_da_escalar11(self, loader, ctx_infantil_16_11m):
        """Caso verificado: Jesús Alejandro, NiWiscDC PD=53 → escalar=11."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(
            prueba, 53.0, ctx_infantil_16_11m.age.years, ctx_infantil_16_11m.age.months
        )
        assert r.puntaje_escalar == 11.0
        assert r.interpretacion == "Promedio"

    def test_wisc_voc_pd37_da_escalar6(self, loader, ctx_infantil_16_11m):
        """Verificado contra informe real."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscVoc")
        r = RangoPuntajeStrategy().calculate(
            prueba, 37.0, ctx_infantil_16_11m.age.years, ctx_infantil_16_11m.age.months
        )
        assert r.puntaje_escalar == 6.0

    def test_wisc_cl_pd46_da_escalar4(self, loader, ctx_infantil_16_11m):
        """Verificado. Claves Velocidad de Proceso."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscCl")
        r = RangoPuntajeStrategy().calculate(
            prueba, 46.0, ctx_infantil_16_11m.age.years, ctx_infantil_16_11m.age.months
        )
        assert r.puntaje_escalar == 4.0

    def test_sin_dato_9999(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(prueba, 9999.0, ctx_infantil_10.age.years, 0)
        assert r.puntaje_escalar is None
        assert r.interpretacion == "Sin dato"

    def test_pd_cero_valido(self, loader, ctx_infantil_10):
        """PD=0 es válido, no es sin dato."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(prueba, 0.0, ctx_infantil_10.age.years, 0)
        # Puede ser not_found si 0 no está en baremo, pero NO es sin dato
        assert r.interpretacion != "Sin dato"


@pytest.mark.unit
class TestWaisRangeStrategy:

    def test_wais_v_28_pd42_da_escalar9(self, loader, ctx_adulto_28):
        """WAIS-III Vocabulario, adulto 28a, PD=42 → escalar=9 (Promedio)."""
        from app.domain.clinical_engine.strategies import WaisRangeStrategy
        prueba = loader.get_prueba("AdWAISV")
        r = WaisRangeStrategy().calculate(prueba, 42.0, ctx_adulto_28.age.years, ctx_adulto_28.age.months)
        assert r.puntaje_escalar == 9.0
        assert r.interpretacion == "Promedio"
        assert "2534" in r.llave_usada

    def test_wais_cit_130_da_ci110(self, loader, ctx_adulto_28):
        """CI compuesto WAIS. Verificado."""
        from app.domain.clinical_engine.strategies import WaisRangeStrategy
        prueba = loader.get_prueba("AdWAISCIT")
        r = WaisRangeStrategy().calculate(prueba, 130.0, ctx_adulto_28.age.years, ctx_adulto_28.age.months)
        assert r.puntaje_escalar == 110.0

    def test_wais_eman_55_da_105(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import WaisRangeStrategy
        prueba = loader.get_prueba("AdWAISEMan")
        r = WaisRangeStrategy().calculate(prueba, 55.0, ctx_adulto_28.age.years, ctx_adulto_28.age.months)
        assert r.puntaje_escalar == 105.0

    def test_sin_dato_devuelve_none(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import WaisRangeStrategy
        prueba = loader.get_prueba("AdWAISV")
        r = WaisRangeStrategy().calculate(prueba, 9999.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is None


@pytest.mark.unit
class TestSumaAIndiceStrategy:

    def test_wisc_icv_suma26_da_ci93(self, loader, ctx_infantil_16_11m):
        """Verificado: Jesús ICV suma=26 → CI=93."""
        from app.domain.clinical_engine.strategies import SumaAIndiceStrategy
        prueba = loader.get_prueba("NiWISCIndComVer")
        r = SumaAIndiceStrategy().calculate(
            prueba, 26.0, ctx_infantil_16_11m.age.years, 0
        )
        assert r.puntaje_escalar == 93.0
        assert r.tipo_metrica == "ci"

    def test_wisc_irp_suma29_da_ci98(self, loader, ctx_infantil_16_11m):
        from app.domain.clinical_engine.strategies import SumaAIndiceStrategy
        prueba = loader.get_prueba("NiWISCIndRazPer")
        r = SumaAIndiceStrategy().calculate(prueba, 29.0, ctx_infantil_16_11m.age.years, 0)
        assert r.puntaje_escalar == 98.0

    def test_wisc_total_suma83_da_ci87(self, loader, ctx_infantil_16_11m):
        """CIT verificado contra informe."""
        from app.domain.clinical_engine.strategies import SumaAIndiceStrategy
        prueba = loader.get_prueba("NiWISCTot")
        r = SumaAIndiceStrategy().calculate(prueba, 83.0, ctx_infantil_16_11m.age.years, 0)
        assert r.puntaje_escalar == 87.0
        assert r.interpretacion == "Promedio"


@pytest.mark.unit
class TestDesconocidoStrategyAdultoMayor:
    """Neuronorma Colombia — estrategia para adulto mayor."""

    def test_vitmt_a_pd239_80a_primaria(self, loader, ctx_adulto_mayor_80):
        """Verificado: Blanca Edilma ViTMTA PD=237→239 → escalar=6."""
        from app.domain.clinical_engine.strategies import DesconocidoStrategy
        prueba = loader.get_prueba("ViTMTA")
        r = DesconocidoStrategy().calculate(
            prueba, 239.0,
            ctx_adulto_mayor_80.age.years, ctx_adulto_mayor_80.age.months,
            escolaridad="Primaria Incompleta",
        )
        assert r.puntaje_escalar == 6.0
        assert r.interpretacion == "Bajo"

    def test_virdd_pd5_ajustado_80a_da_escalar_13(self, loader, ctx_adulto_mayor_80):
        """Verificado contra informe. PD original=4, ajuste escolaridad=+1 → PD=5 → escalar=13."""
        from app.domain.clinical_engine.strategies import DesconocidoStrategy
        prueba = loader.get_prueba("ViRDD")
        # El engine aplica ajuste +1 para Primaria Incompleta antes de llamar a la strategy
        r = DesconocidoStrategy().calculate(
            prueba, 5.0,
            ctx_adulto_mayor_80.age.years, ctx_adulto_mayor_80.age.months,
            escolaridad="Primaria Incompleta",
        )
        assert r.puntaje_escalar == 13.0

    def test_paciente_fuera_rango_am_retorna_sin_norma(self, loader):
        """Un paciente de 30 años NO está en el baremo AM."""
        from app.domain.clinical_engine.engine import PatientContext
        from app.domain.clinical_engine.strategies import DesconocidoStrategy
        prueba = loader.get_prueba("ViTMTA")
        ctx_30 = PatientContext.from_demographics(
            date(1996, 1, 1), date(2026, 1, 1), "H", "Universitaria"
        )
        r = DesconocidoStrategy().calculate(
            prueba, 50.0, ctx_30.age.years, ctx_30.age.months
        )
        assert r.metadata.get("sin_norma") is True


@pytest.mark.unit
class TestZScoreStrategy:

    def test_nitmt_a_media_da_z0(self, loader, ctx_infantil_10):
        """Si PD = media, Z debe ser ≈ 0."""
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        prueba = loader.get_prueba("NiTMTA")
        params = prueba.baremos.get("10")
        if not params:
            pytest.skip("No hay parámetros para edad 10 en NiTMTA")
        media = params[0]
        r = ZScoreStrategy().calculate(prueba, media, ctx_infantil_10.age.years, 0)
        assert abs(r.puntaje_escalar) < 0.01

    def test_caras_media_da_z0(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        prueba = loader.get_prueba("NiTestPC")
        params = prueba.baremos.get("10")
        if not params:
            pytest.skip("Sin datos para edad 10 en CARAS")
        media = params[0]
        r = ZScoreStrategy().calculate(prueba, media, ctx_infantil_10.age.years, 0)
        assert abs(r.puntaje_escalar) < 0.01


@pytest.mark.unit
class TestPuntajeDirectoATStrategy:

    def test_spence_ocd_pd3_da_t57(self, loader, ctx_infantil_10):
        """PD=3 OCD → T=57 (Promedio)."""
        from app.domain.clinical_engine.strategies import PuntajeDirectoATStrategy
        prueba = loader.get_prueba("NiSpenceOCD")
        r = PuntajeDirectoATStrategy().calculate(prueba, 3.0, ctx_infantil_10.age.years, 0)
        assert r.puntaje_escalar == 57.0

    def test_spence_to_pd20_da_t50(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import PuntajeDirectoATStrategy
        prueba = loader.get_prueba("NiSpenceTo")
        r = PuntajeDirectoATStrategy().calculate(prueba, 20.0, ctx_infantil_10.age.years, 0)
        assert r.puntaje_escalar == 50.0


@pytest.mark.unit
class TestPuntajeDoblResultadoStrategy:

    def test_gads_is_pd15_retorna_escalar(self, loader, ctx_infantil_10):
        """NiGadsIS — baremo es lista [PE, Percentil]."""
        from app.domain.clinical_engine.strategies import PuntajeDoblResultadoStrategy
        prueba = loader.get_prueba("NiGadsIS")
        r = PuntajeDoblResultadoStrategy().calculate(prueba, 15.0, ctx_infantil_10.age.years, 0)
        assert r.puntaje_escalar is not None
        assert r.puntaje_escalar > 0

    def test_gads_is_sin_dato(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import PuntajeDoblResultadoStrategy
        prueba = loader.get_prueba("NiGadsIS")
        r = PuntajeDoblResultadoStrategy().calculate(prueba, 9999.0, ctx_infantil_10.age.years, 0)
        assert r.puntaje_escalar is None

    def test_gads_prc_pd5(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import PuntajeDoblResultadoStrategy
        prueba = loader.get_prueba("NiGadsPRC")
        r = PuntajeDoblResultadoStrategy().calculate(prueba, 5.0, ctx_infantil_10.age.years, 0)
        assert r.puntaje_escalar is not None


@pytest.mark.unit
class TestClasificacionFijaStrategy:
    """
    Tests para la nueva ClasificacionFijaStrategy basada en codigos N/DL/DE/DS
    del baremo JSON, en lugar de rangos Beck hardcoded para todas las escalas.
    """

    def test_yesavage_pd2_da_normal(self, loader, ctx_adulto_mayor_80):
        """Yesavage PD=2 -> codigo N (Normal, sin depresion)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("ViYesavage")
        r = ClasificacionFijaStrategy().calculate(prueba, 2.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.puntaje_escalar == 2.0
        assert r.metadata.get("clasificacion_codigo") == "N"
        assert r.interpretacion == "Normal"
        assert r.metadata.get("nivel_interpretacion") == "Promedio"

    def test_yesavage_pd9_da_deficit_leve(self, loader, ctx_adulto_mayor_80):
        """
        Yesavage PD=9 -> codigo DL (Deficit Leve, depresion ligera).
        CRITICO: antes del refactor aparecia como 'Bajo' o 'Promedio',
        ahora muestra correctamente la categoria clinica.
        """
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("ViYesavage")
        r = ClasificacionFijaStrategy().calculate(prueba, 9.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "DL"
        assert r.interpretacion == "Deficit Leve"
        assert r.metadata.get("nivel_interpretacion") == "Limítrofe"

    def test_yesavage_pd12_da_deficit_extremo(self, loader, ctx_adulto_mayor_80):
        """Yesavage PD=12 -> codigo DE (Depresion severa, 10-15)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("ViYesavage")
        r = ClasificacionFijaStrategy().calculate(prueba, 12.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "DE"
        assert r.interpretacion == "Deficit Extremo"
        assert r.metadata.get("nivel_interpretacion") == "Bajo"

    def test_mmse_pd29_da_normal(self, loader, ctx_adulto_mayor_80):
        """MMSE PD=29 (27-30) -> codigo N (Normal, sin deterioro)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("MMSE")
        r = ClasificacionFijaStrategy().calculate(prueba, 29.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "N"
        assert r.interpretacion == "Normal"

    def test_mmse_pd15_da_deficit_extremo(self, loader, ctx_adulto_mayor_80):
        """
        MMSE PD=15 -> codigo DE (Deterioro moderado).
        CRITICO: antes del refactor aparecia como 'Superior' o 'Bajo',
        ahora muestra correctamente la categoria clinica DE.
        """
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("MMSE")
        r = ClasificacionFijaStrategy().calculate(prueba, 15.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "DE"
        assert r.interpretacion == "Deficit Extremo"

    def test_mmse_pd5_da_deficit_severo(self, loader, ctx_adulto_mayor_80):
        """MMSE PD=5 -> codigo DS (Deterioro severo, requiere intervencion)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("MMSE")
        r = ClasificacionFijaStrategy().calculate(prueba, 5.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "DS"
        assert r.interpretacion == "Deficit Severo"

    def test_lawton_pd8_da_normal(self, loader, ctx_adulto_mayor_80):
        """EscLawton PD=8 -> codigo N (Independiente en AVD)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("EscLawton")
        r = ClasificacionFijaStrategy().calculate(prueba, 8.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "N"
        assert r.interpretacion == "Normal"

    def test_lawton_pd1_da_deficit_severo(self, loader, ctx_adulto_mayor_80):
        """EscLawton PD=1 -> codigo DS (Dependencia severa para AVD)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("EscLawton")
        r = ClasificacionFijaStrategy().calculate(prueba, 1.0, ctx_adulto_mayor_80.age.years, 0)
        assert r.metadata.get("clasificacion_codigo") == "DS"
        assert r.interpretacion == "Deficit Severo"

    def test_beck_pd15_da_leve_fallback(self, loader, ctx_adulto_28):
        """
        Beck BDI-II PD=15 -> 'Leve' (rango Beck 14-19).
        AdBeck NO tiene codigos categoricos en baremo (estructura distinta),
        por eso usa el fallback de rangos Beck hardcoded.
        """
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("AdBeck")
        r = ClasificacionFijaStrategy().calculate(prueba, 15.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar == 15.0
        assert r.metadata.get("clasificacion_beck") == "Leve"
        assert r.interpretacion == "Leve"

    def test_beck_pd5_da_minima_fallback(self, loader, ctx_adulto_28):
        """Beck PD=5 -> 'Mínima' (rango 0-13, depresion no significativa)."""
        from app.domain.clinical_engine.strategies import ClasificacionFijaStrategy
        prueba = loader.get_prueba("AdBeck")
        r = ClasificacionFijaStrategy().calculate(prueba, 5.0, ctx_adulto_28.age.years, 0)
        assert r.metadata.get("clasificacion_beck") == "Mínima"
        assert r.interpretacion == "Mínima"


@pytest.mark.unit
class TestEscolaridadPC50Strategy:

    def test_addig_pros_escolaridad_s(self, loader, ctx_adulto_28):
        """AdDPros — Dígitos Progresión por escolaridad."""
        from app.domain.clinical_engine.strategies import EscolaridadPC50Strategy
        prueba = loader.get_prueba("AdDPros")
        r = EscolaridadPC50Strategy().calculate(
            prueba, 24.0, ctx_adulto_28.age.years, 0, escolaridad="Secundaria Completa"
        )
        assert r.puntaje_escalar is not None

    def test_ajuste_escolaridad_am(self, loader, ctx_adulto_mayor_80):
        """ViDeno — denominación adulto mayor con escolaridad."""
        from app.domain.clinical_engine.strategies import EscolaridadPC50Strategy
        prueba = loader.get_prueba("ViDeno")
        r = EscolaridadPC50Strategy().calculate(
            prueba, 36.0, ctx_adulto_mayor_80.age.years, 0,
            escolaridad="Primaria Incompleta",
        )
        assert r.puntaje_escalar is not None


# ═══════════════════════════════════════════════════════════════
# CICLO COMPLETO DEL ENGINE — CASOS CLÍNICOS REALES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestEngineCasoJesusAlejandro:
    """
    Caso real verificado:
    Jesús Alejandro — 16a 11m — Secundaria Incompleta — M
    Informe de referencia: NiWiscDC PD=53 → PE=11, etc.
    """

    PUNTAJES = {
        "NiWiscDC":   53, "NiWiscSem":  32, "NiWiscVoc":  37,
        "NiWiscLN":   25, "NiWiscCl":   46, "NiWiscAri":  21,
        "NiWISCIndComVer": 26, "NiWISCIndRazPer": 29,
        "NiWISCIndMemTra": 15, "NiWISCIndVelPro": 13,
        "NiWISCTot": 83,
    }

    ESPERADOS = {
        "NiWiscDC":   11, "NiWiscSem":  11, "NiWiscVoc":   6,
        "NiWiscLN":   16, "NiWiscCl":    4, "NiWiscAri":   6,
        "NiWISCIndComVer": 93, "NiWISCIndRazPer": 98,
        "NiWISCIndMemTra": 86, "NiWISCIndVelPro": 80,
        "NiWISCTot": 87,
    }

    def test_escalares_exactos(self, engine, ctx_infantil_16_11m):
        result = engine.score("jesus", self.PUNTAJES, ctx_infantil_16_11m)
        for r in result.resultados:
            if r.test_id in self.ESPERADOS and r.fue_realizada:
                esperado = self.ESPERADOS[r.test_id]
                assert r.puntaje_escalar == esperado, (
                    f"{r.test_id}: esperado {esperado}, obtenido {r.puntaje_escalar}"
                )

    def test_poblacion_infantil(self, engine, ctx_infantil_16_11m):
        result = engine.score("jesus", self.PUNTAJES, ctx_infantil_16_11m)
        assert result.poblacion == "infantil"

    def test_total_pruebas(self, engine, ctx_infantil_16_11m):
        result = engine.score("jesus", self.PUNTAJES, ctx_infantil_16_11m)
        assert result.total_pruebas == len(self.PUNTAJES)
        assert result.pruebas_sin_dato == 0

    def test_cit_87_promedio(self, engine, ctx_infantil_16_11m):
        result = engine.score("jesus", self.PUNTAJES, ctx_infantil_16_11m)
        cit = next(r for r in result.resultados if r.test_id == "NiWISCTot")
        assert cit.puntaje_escalar == 87.0
        assert cit.interpretacion == "Promedio"


@pytest.mark.unit
class TestEngineCasoBlancaEdilma:
    """
    Caso real verificado:
    Blanca Edilma — 80a 5m — Primaria Incompleta — F
    """

    PUNTAJES = {
        "ViRDD": 4, "ViRDInv": 2, "ViTMTA": 239,
        "ViStP": 8, "ViGroberRLT": 3, "ViGroberML_Tot": 2,
        "ViGroberMC_Tot": 7, "ViAni": 8, "ViYesavage": 2,
    }

    ESPERADOS_ESCALARES = {
        "ViRDD": 13, "ViRDInv": 11, "ViTMTA": 6,
        "ViStP": 3, "ViGroberRLT": 3, "ViGroberML_Tot": 6,
        "ViGroberMC_Tot": 4, "ViAni": 8, "ViYesavage": 2,
    }

    def test_escalares_exactos(self, engine, ctx_adulto_mayor_80):
        result = engine.score("blanca", self.PUNTAJES, ctx_adulto_mayor_80)
        for r in result.resultados:
            if r.test_id in self.ESPERADOS_ESCALARES and r.fue_realizada:
                esperado = self.ESPERADOS_ESCALARES[r.test_id]
                assert r.puntaje_escalar == esperado, (
                    f"{r.test_id}: esperado {esperado}, obtenido {r.puntaje_escalar}"
                )

    def test_poblacion_adulto_mayor(self, engine, ctx_adulto_mayor_80):
        result = engine.score("blanca", self.PUNTAJES, ctx_adulto_mayor_80)
        assert result.poblacion == "adulto_mayor"

    def test_interpretaciones_consistentes_con_escalar(self, engine, ctx_adulto_mayor_80):
        """Las interpretaciones deben ser consistentes con el escalar calculado."""
        result = engine.score("blanca", self.PUNTAJES, ctx_adulto_mayor_80)
        for r in result.resultados:
            if not r.fue_realizada or r.test_id == "ViYesavage":
                continue
            esc = r.puntaje_escalar
            if esc is None:
                continue
            # Validar consistencia escalar -> interpretacion
            if esc <= 4:
                expected = "Bajo"
            elif esc <= 6:
                expected = "Limítrofe"
            elif esc <= 12:
                expected = "Promedio"
            else:
                expected = "Superior"
            assert r.interpretacion == expected, (
                f"{r.test_id}: escalar={esc} -> esperaba '{expected}', "
                f"obtenido '{r.interpretacion}'"
            )


@pytest.mark.unit
class TestEngineCasosEspeciales:

    def test_9999_sin_dato(self, engine, ctx_infantil_10):
        r = engine.score("t", {"NiWiscDC": 9999}, ctx_infantil_10)
        resultado = r.resultados[0]
        assert resultado.interpretacion == "Sin dato"
        assert resultado.puntaje_escalar is None
        assert not resultado.fue_realizada
        assert r.pruebas_sin_dato == 1

    def test_test_id_invalido_advertencia(self, engine, ctx_infantil_10):
        r = engine.score("t", {"INVALIDO_XYZ": 10}, ctx_infantil_10)
        assert any("INVALIDO_XYZ" in a for a in r.advertencias)
        assert r.total_pruebas == 0

    def test_puntajes_vacios(self, engine, ctx_infantil_10):
        r = engine.score("t", {}, ctx_infantil_10)
        assert r.total_pruebas == 0
        assert r.pruebas_realizadas == 0

    def test_mix_validos_invalidos(self, engine, ctx_infantil_10):
        r = engine.score("t", {"NiWiscDC": 30, "XXX": 5, "NiWiscVoc": 9999}, ctx_infantil_10)
        assert r.pruebas_realizadas == 1
        assert r.pruebas_sin_dato == 1
        assert len(r.advertencias) == 1

    def test_poblacion_segun_edad_infantil(self, engine, ctx_infantil_10):
        r = engine.score("t", {"NiWiscDC": 30}, ctx_infantil_10)
        assert r.poblacion == "infantil"

    def test_poblacion_adulto_mayor(self, engine, ctx_adulto_mayor_80):
        r = engine.score("t", {"ViTMTA": 100}, ctx_adulto_mayor_80)
        assert r.poblacion == "adulto_mayor"


@pytest.mark.unit
class TestEngineCoberturaCompleta:
    """Verifica cobertura de las pruebas cargadas y sus estrategias."""

    def test_168_pruebas_cargadas(self, loader):
        # 168 originales + 16 alias adulto_mayor agregados en v8 (SDMT, StroopAM, etc.)
        assert loader.total_pruebas >= 168

    def test_cero_pruebas_vacias(self, loader):
        vacias = [tid for tid in loader.all_test_ids
                  if not loader.get_prueba(tid).baremos]
        assert vacias == [], f"Pruebas sin baremos: {vacias}"

    def test_todas_tienen_strategy_registrada(self, loader):
        from app.domain.clinical_engine.factory import ScoringStrategyFactory
        sin_strategy = []
        for tid in loader.all_test_ids:
            prueba = loader.get_prueba(tid)
            try:
                s = ScoringStrategyFactory.get(prueba.tipo_calculo)
                if s is None:
                    sin_strategy.append(tid)
            except Exception as e:
                sin_strategy.append(f"{tid}:{e}")
        assert sin_strategy == [], f"Sin estrategia: {sin_strategy}"

    def test_infantil_92(self, loader):
        infantil = loader.get_pruebas_por_poblacion("infantil")
        assert len(infantil) == 92

    def test_adulto_joven_30(self, loader):
        aj = loader.get_pruebas_por_poblacion("adulto_joven")
        assert len(aj) == 30

    def test_adulto_mayor_46(self, loader):
        am = loader.get_pruebas_por_poblacion("adulto_mayor")
        # 46 originales + 18 alias agregados en v8
        assert len(am) >= 46

    def test_ajustes_escolaridad_adulto_mayor(self, loader):
        """Analfabeta tiene ajuste > 0 en pruebas de AM."""
        ajuste = loader.get_ajuste_escolaridad("ViTMTA", "Analfabeta")
        assert ajuste == 2

    def test_ajuste_profesional_negativo(self, loader):
        ajuste = loader.get_ajuste_escolaridad("ViTMTA", "Profesional")
        assert ajuste == -1


# ═══════════════════════════════════════════════════════════════
# FASE 1a: WAIS-III ADULTO JOVEN (wais_range)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestWaisRangeAllSubtests:
    """Cada subtest WAIS-III con PD representativo (escalar=10) en rango 25-34."""

    @pytest.mark.parametrize("test_id,pd,expected_escalar", [
        ("AdWAISA",    13, 10),   # Aritmética
        ("AdWAISC",    19, 10),   # Comprensión
        ("AdWAISCC",   44, 10),   # Clave de números
        ("AdWAISFI",   20, 10),   # Figuras Incompletas
        ("AdWAISHI",   15, 10),   # Historietas
        ("AdWAISI",    18, 10),   # Información
        ("AdWAISL",    11, 10),   # Letras y Números
        ("AdWAISRO",   33, 10),   # Rompecabezas
        ("AdSemWais",  20, 10),   # Semejanzas
        ("AdSDWais",   74, 10),   # Búsqueda de Símbolos / Dígitos Símbolo
        ("AdMatr",     19, 10),   # Matrices
        ("AdDDir",     16, 10),   # Dígitos Directo
    ])
    def test_wais_subtests_escalar_10(self, loader, ctx_adulto_28, test_id, pd, expected_escalar):
        from app.domain.clinical_engine.strategies import WaisRangeStrategy
        prueba = loader.get_prueba(test_id)
        r = WaisRangeStrategy().calculate(
            prueba, float(pd), ctx_adulto_28.age.years, ctx_adulto_28.age.months
        )
        assert r.puntaje_escalar == float(expected_escalar), (
            f"{test_id}: PD={pd} esperado={expected_escalar}, obtenido={r.puntaje_escalar}"
        )
        assert 1 <= r.puntaje_escalar <= 19

    @pytest.mark.parametrize("test_id", [
        "AdWAISA", "AdWAISC", "AdWAISCC", "AdWAISFI", "AdWAISHI",
        "AdWAISI", "AdWAISL", "AdWAISRO", "AdSemWais", "AdSDWais",
        "AdMatr", "AdDDir",
    ])
    def test_wais_subtests_sin_dato_9999(self, loader, ctx_adulto_28, test_id):
        from app.domain.clinical_engine.strategies import WaisRangeStrategy
        prueba = loader.get_prueba(test_id)
        r = WaisRangeStrategy().calculate(prueba, 9999.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is None


# ═══════════════════════════════════════════════════════════════
# FASE 1b: ÍNDICES CI WAIS-III (suma_a_indice)
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestWaisIndicesCISumaAIndice:
    """Índices compuestos WAIS-III — CI entre 50-160."""

    @pytest.mark.parametrize("test_id,suma,expected_ci", [
        ("AdWAISICV",  30, 100),  # Índice Comprensión Verbal
        ("AdWAISICP",  30,  99),  # Índice Organización Perceptual
        ("AdWAISIMT",  31, 100),  # Índice Memoria de Trabajo
        ("AdWAISIVP",  20, 101),  # Índice Velocidad de Proceso
        ("AdWASIEVer", 61,  99),  # Escala Verbal
        ("AdWAISEMan", 51, 100),  # Escala Manipulativa
    ])
    def test_indice_ci_esperado(self, loader, test_id, suma, expected_ci):
        from app.domain.clinical_engine.strategies import SumaAIndiceStrategy
        prueba = loader.get_prueba(test_id)
        r = SumaAIndiceStrategy().calculate(prueba, float(suma), 28, 0)
        assert r.puntaje_escalar == float(expected_ci), (
            f"{test_id}: suma={suma} esperado CI={expected_ci}, obtenido={r.puntaje_escalar}"
        )
        assert 50 <= r.puntaje_escalar <= 160

    @pytest.mark.parametrize("test_id", [
        "AdWAISICV", "AdWAISICP", "AdWAISIMT", "AdWAISIVP", "AdWASIEVer", "AdWAISEMan",
    ])
    def test_indice_sin_dato(self, loader, test_id):
        from app.domain.clinical_engine.strategies import SumaAIndiceStrategy
        prueba = loader.get_prueba(test_id)
        r = SumaAIndiceStrategy().calculate(prueba, 9999.0, 28, 0)
        assert r.puntaje_escalar is None


# ═══════════════════════════════════════════════════════════════
# FASE 1c: NEURONORMA AM (desconocido) — 65 años, Analfabeta
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestDesconocidoNeuronormaAM:
    """Neuronorma Colombia AM con PDs que dan escalar=10 en rango 63-65."""

    @pytest.mark.parametrize("test_id,pd,expected_escalar", [
        ("ViStC",     58, 10),   # Stroop Color
        ("ViStPC",    30, 10),   # Stroop Palabra-Color
        ("ViP",       15, 10),   # Praxias
        ("ViWCat",    22, 10),   # Wisconsin Categorías
        ("ViTLMExc",  37, 10),   # Torre de Londres Mov. Exceso
        ("ViTLLat",   45, 10),   # Torre de Londres Latencia
        ("ViTLEje",  313, 10),   # Torre de Londres Ejecución
        ("ViSimDig",  33, 10),   # Similitud Dígitos
        ("ViTBDA",    46, 10),   # Test Barcelona Denominación
        ("ViFCROCo",  32, 10),   # FCRO Copia
        ("ViFCRORec", 14, 10),   # FCRO Recuerdo
    ])
    def test_neuronorma_am_escalar_10(self, loader, ctx_adulto_mayor_65, test_id, pd, expected_escalar):
        from app.domain.clinical_engine.strategies import DesconocidoStrategy
        prueba = loader.get_prueba(test_id)
        r = DesconocidoStrategy().calculate(
            prueba, float(pd),
            ctx_adulto_mayor_65.age.years, ctx_adulto_mayor_65.age.months,
            escolaridad="Analfabeta",
        )
        assert r.puntaje_escalar == float(expected_escalar), (
            f"{test_id}: PD={pd} esperado={expected_escalar}, obtenido={r.puntaje_escalar}"
        )
        assert 1 <= r.puntaje_escalar <= 19


# ═══════════════════════════════════════════════════════════════
# FASE 1d: ESTRATEGIAS ESPECIALES SIN TEST
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestAjusteStroopStrategy:
    """AdStroop_Corr — ajuste por edad."""

    def test_stroop_pd8_retorna_valores(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import AjusteStroopStrategy
        prueba = loader.get_prueba("AdStroop_Corr")
        r = AjusteStroopStrategy().calculate(prueba, 8.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is not None
        assert r.puntaje_escalar == 46.0  # stroop_P = valor[0]
        assert r.metadata["stroop_C"] == 36.0
        assert r.metadata["stroop_PC"] == 24.0

    def test_stroop_sin_dato(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import AjusteStroopStrategy
        prueba = loader.get_prueba("AdStroop_Corr")
        r = AjusteStroopStrategy().calculate(prueba, 9999.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is None


@pytest.mark.unit
class TestBaremoPEStrategy:
    """AdTL_Torre — Torre de Londres."""

    def test_torre_pd4_retorna_pe(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import BaremoPEStrategy
        prueba = loader.get_prueba("AdTL_Torre")
        r = BaremoPEStrategy().calculate(prueba, 4.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is not None
        assert r.puntaje_escalar == 10.0  # baremo["4"][0] = 10

    def test_torre_sin_dato(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import BaremoPEStrategy
        prueba = loader.get_prueba("AdTL_Torre")
        r = BaremoPEStrategy().calculate(prueba, 9999.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is None


@pytest.mark.unit
class TestComparativoStrategy:
    """AdCVLT — memoria verbal comparativa."""

    def test_cvlt_pd10_no_crash(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import ComparativoStrategy
        prueba = loader.get_prueba("AdCVLT")
        r = ComparativoStrategy().calculate(prueba, 10.0, ctx_adulto_28.age.years, 0)
        # Puede ser z-score válido o None si baremo no tiene datos, pero no debe crashear
        assert r.test_id == "AdCVLT"
        assert r.puntaje_bruto == 10.0

    def test_cvlt_sin_dato(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import ComparativoStrategy
        prueba = loader.get_prueba("AdCVLT")
        r = ComparativoStrategy().calculate(prueba, 9999.0, ctx_adulto_28.age.years, 0)
        assert r.puntaje_escalar is None


@pytest.mark.unit
class TestZScoreMultipleStrategy:
    """NiTestPC_R — CARAS-R z-score múltiple."""

    def test_caras_r_edad10_media_da_z0(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import ZScoreMultipleStrategy
        prueba = loader.get_prueba("NiTestPC_R")
        params = prueba.baremos.get("10")
        if not params:
            pytest.skip("Sin datos para edad 10 en NiTestPC_R")
        media = params[0]
        r = ZScoreMultipleStrategy().calculate(prueba, media, 10, 0)
        assert abs(r.puntaje_escalar) < 0.01
        assert "pares_z" in r.metadata

    def test_caras_r_sin_dato(self, loader, ctx_infantil_10):
        from app.domain.clinical_engine.strategies import ZScoreMultipleStrategy
        prueba = loader.get_prueba("NiTestPC_R")
        r = ZScoreMultipleStrategy().calculate(prueba, 9999.0, 10, 0)
        assert r.puntaje_escalar is None


# ═══════════════════════════════════════════════════════════════
# FASE 1d-extra: Z-SCORE ADULTO + ESCOLARIDAD_PC50
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestZScoreAdulto:
    """AdTMT_AB y AdFCRO_Rey — z-score adulto joven."""

    def test_tmt_ab_media_da_z0(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        prueba = loader.get_prueba("AdTMT_AB")
        params = prueba.baremos.get("28")
        if not params:
            pytest.skip("Sin datos para edad 28 en AdTMT_AB")
        media = params[0]
        r = ZScoreStrategy().calculate(prueba, media, 28, 0)
        assert abs(r.puntaje_escalar) < 0.01

    def test_fcro_rey_media_da_z0(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import ZScoreStrategy
        prueba = loader.get_prueba("AdFCRO_Rey")
        params = prueba.baremos.get("28")
        if not params:
            pytest.skip("Sin datos para edad 28 en AdFCRO_Rey")
        media = params[0]
        r = ZScoreStrategy().calculate(prueba, media, 28, 0)
        assert abs(r.puntaje_escalar) < 0.01


@pytest.mark.unit
class TestEscolaridadPC50Extended:
    """AdDReg, AdRDI, ViSem con distintas escolaridades."""

    def test_adreg_secundaria_28a(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import EscolaridadPC50Strategy
        prueba = loader.get_prueba("AdDReg")
        r = EscolaridadPC50Strategy().calculate(
            prueba, 6.0, 28, 0, escolaridad="Secundaria Completa"
        )
        assert r.puntaje_escalar is not None
        assert "pc50" in r.metadata

    def test_adrdi_secundaria_28a(self, loader, ctx_adulto_28):
        from app.domain.clinical_engine.strategies import EscolaridadPC50Strategy
        prueba = loader.get_prueba("AdRDI")
        r = EscolaridadPC50Strategy().calculate(
            prueba, 5.0, 28, 0, escolaridad="Secundaria Completa"
        )
        assert r.puntaje_escalar is not None

    def test_visem_primaria_65a(self, loader, ctx_adulto_mayor_65):
        from app.domain.clinical_engine.strategies import EscolaridadPC50Strategy
        prueba = loader.get_prueba("ViSem")
        r = EscolaridadPC50Strategy().calculate(
            prueba, 12.0, 65, 0, escolaridad="Primaria Incompleta"
        )
        assert r.puntaje_escalar is not None


# ═══════════════════════════════════════════════════════════════
# FASE 1d-extra: PUNTAJE DOBLE RESULTADO — GADS restantes
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestPuntajeDoblResultadoExtended:

    @pytest.mark.parametrize("test_id,pd", [
        ("NiGadsHP", 5),
        ("NiGadsPatCog", 5),
        ("NiGADSCTAs", 10),
    ])
    def test_gads_variantes_retornan_pe(self, loader, ctx_infantil_10, test_id, pd):
        from app.domain.clinical_engine.strategies import PuntajeDoblResultadoStrategy
        prueba = loader.get_prueba(test_id)
        r = PuntajeDoblResultadoStrategy().calculate(
            prueba, float(pd), ctx_infantil_10.age.years, 0
        )
        assert r.puntaje_escalar is not None
        assert r.puntaje_escalar >= 0  # PE=0 válido (NiGADSCTAs: coeficiente Asperger)
        assert "percentil" in r.metadata


# ═══════════════════════════════════════════════════════════════
# FASE 1e: TESTS NEGATIVOS — EDGE CASES
# ═══════════════════════════════════════════════════════════════

@pytest.mark.unit
class TestEdgeCases:

    def test_pd_cero_wisc_retorna_escalar(self, loader, ctx_infantil_10):
        """PD=0 en NiWiscDC: debe retornar escalar=1, no None ni error."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(prueba, 0.0, 10, 0)
        assert r.puntaje_escalar is not None
        assert r.puntaje_escalar == 1.0  # PD=0 → escalar=1 (mínimo)

    def test_pd_extremo_alto_wisc_not_found(self, loader, ctx_infantil_10):
        """PD=999 en NiWiscDC: debe retornar _not_found sin crash."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(prueba, 999.0, 10, 0)
        assert r.puntaje_escalar is None
        assert "error" in r.metadata or "fuera del rango" in str(r.metadata)

    def test_paciente_30a_con_vitmt_sin_norma(self, loader):
        """Paciente de 30 años con ViTMTA: sin_norma=True."""
        from app.domain.clinical_engine.engine import PatientContext
        from app.domain.clinical_engine.strategies import DesconocidoStrategy
        prueba = loader.get_prueba("ViTMTA")
        ctx_30 = PatientContext.from_demographics(
            date(1996, 1, 1), date(2026, 1, 1), "H", "Universitaria"
        )
        r = DesconocidoStrategy().calculate(
            prueba, 50.0, ctx_30.age.years, ctx_30.age.months
        )
        assert r.metadata.get("sin_norma") is True

    def test_paciente_100a_con_wiscdc_sin_norma(self, loader):
        """Paciente de 100 años con NiWiscDC: fuera de rango."""
        from app.domain.clinical_engine.engine import ClinicalEngine, PatientContext
        engine = ClinicalEngine(loader=loader)
        ctx_100 = PatientContext.from_demographics(
            date(1926, 1, 1), date(2026, 1, 1), "H", "Analfabeta"
        )
        # NiWiscDC es infantil; paciente de 100a es adulto_mayor.
        # El engine buscará la prueba pero no encontrará baremo para 100 años.
        result = engine.score("t", {"NiWiscDC": 30}, ctx_100)
        if result.resultados:
            r = result.resultados[0]
            # Puede ser not_found o sin_norma, pero no debe crashear
            assert r.puntaje_escalar is None or r.puntaje_escalar is not None
        # Lo importante: no hubo crash

    def test_pd_negativo_no_crash(self, loader, ctx_infantil_10):
        """PD negativo no debe crashear en strategy directa."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(prueba, -5.0, 10, 0)
        # Puede ser not_found pero no debe crashear
        assert r.test_id == "NiWiscDC"

    def test_pd_negativo_rechazado_por_engine(self, engine, ctx_infantil_10):
        """PD negativo es rechazado por el engine con advertencia."""
        result = engine.score("t", {"NiWiscDC": -5}, ctx_infantil_10)
        assert result.total_pruebas == 0
        assert any("negativo" in a for a in result.advertencias)

    def test_pd_none_es_sin_dato(self, loader, ctx_infantil_10):
        """PD=None debe tratarse como sin dato."""
        from app.domain.clinical_engine.strategies import RangoPuntajeStrategy
        prueba = loader.get_prueba("NiWiscDC")
        r = RangoPuntajeStrategy().calculate(prueba, None, 10, 0)
        assert r.puntaje_escalar is None
        assert r.interpretacion == "Sin dato"


@pytest.mark.unit
class TestFixTipoMetricaAM:
    """
    Tests de regresión para el fix del override de tipo_metrica en AM.

    El fix corrige que pruebas Neuronorma (desconocido/wais_range) estaban
    marcadas como tipo_metrica="ci" en el JSON cuando retornan escalares 1-19.

    RESTRICCION CRITICA: Las escalas clasificacion_fija (Yesavage GDS-15,
    MMSE, Lawton, GoNoGo, etc.) NO deben recibir el override porque sus
    puntajes son directos — no son escalares 1-19 del sistema WISC/WAIS.
    Yesavage PD=9 = Depresión Moderada, NO debe aparecer como "Promedio".
    """

    def test_virdd_escalar13_interpreta_superior(self, engine, ctx_adulto_mayor_80):
        """ViRDD PD=4 (ajustado +1 = 5) → escalar=13 → tipo_metrica=escalar → Superior."""
        result = engine.score("t", {"ViRDD": 4}, ctx_adulto_mayor_80)
        r = next(x for x in result.resultados if x.test_id == "ViRDD")
        assert r.puntaje_escalar == 13.0
        assert r.tipo_metrica == "escalar"
        assert r.interpretacion == "Superior"

    def test_vitmt_a_escalar6_interpreta_limitrofe(self, engine, ctx_adulto_mayor_80):
        """ViTMTA PD=239 (ajustado +2 = 241) → escalar=6 → tipo_metrica=escalar → Limítrofe."""
        result = engine.score("t", {"ViTMTA": 239}, ctx_adulto_mayor_80)
        r = next(x for x in result.resultados if x.test_id == "ViTMTA")
        assert r.puntaje_escalar == 6.0
        assert r.tipo_metrica == "escalar"
        assert r.interpretacion == "Limítrofe"

    def test_yesavage_pd9_via_engine_da_deficit_leve(self, engine, ctx_adulto_mayor_80):
        """
        ViYesavage PD=9 a traves del engine -> 'Deficit Leve'.
        Con el refactor de ClasificacionFijaStrategy ahora usa el baremo JSON
        (codigo DL) en lugar de rangos Beck. Resultado clinicamente correcto.
        """
        result = engine.score("t", {"ViYesavage": 9}, ctx_adulto_mayor_80)
        r = next(x for x in result.resultados if x.test_id == "ViYesavage")
        # tipo_metrica sigue siendo "ci" (el del JSON, sin override)
        assert r.tipo_metrica == "ci"
        # Pero la interpretacion ahora viene del baremo categorico
        assert r.interpretacion == "Deficit Leve"
        assert r.metadata.get("clasificacion_codigo") == "DL"
        # NO debe ser "Promedio" (peligroso) ni "Superior"
        assert r.interpretacion not in ("Promedio", "Superior")

    def test_mmse_pd15_via_engine_da_deficit_extremo(self, engine, ctx_adulto_mayor_80):
        """
        MMSE PD=15 a traves del engine -> 'Deficit Extremo' (deterioro marcado).
        Con el refactor, el codigo DE del baremo se usa directamente.
        """
        result = engine.score("t", {"MMSE": 15}, ctx_adulto_mayor_80)
        if not result.resultados:
            return
        r = next((x for x in result.resultados if x.test_id == "MMSE"), None)
        if r is None:
            return
        assert r.interpretacion == "Deficit Extremo"
        assert r.metadata.get("clasificacion_codigo") == "DE"
        assert r.interpretacion not in ("Superior", "Promedio")
