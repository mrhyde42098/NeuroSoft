"""
tests/unit/clinical_engine/test_gads_cdi_strategies.py
=========================================================
§N3 (mayo 2026) — Tests específicos de estrategias menos cubiertas.

Cubre:
    • PuntajeDoblResultadoStrategy → NiGADSCTAs (GADS-CTAs Asperger)
    • EdadSexoStrategy → NiCDI (Inventario Depresión Infantil)

Ambas estrategias tenían cobertura mínima hasta ahora. Estos tests
verifican comportamiento en casos representativos + edge cases.
"""
from __future__ import annotations

import pytest

from app.core.config import settings
from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.engine import ClinicalEngine
from app.domain.clinical_engine.factory import ScoringStrategyFactory


def get_strategy(tipo_calculo):
    """Shim para tests — devuelve strategy del factory."""
    return ScoringStrategyFactory._REGISTRY[tipo_calculo]


@pytest.fixture(scope="module")
def loader():
    return BaremosLoader.load(settings.baremo_path)


# ═══════════════════════════════════════════════════════════════════
# NiGADSCTAs — puntaje_doble_resultado
# ═══════════════════════════════════════════════════════════════════

class TestNiGADSCTAs:
    """GADS Coeficiente Trastorno Asperger.
    Schema: baremo[str(pd)] = {"CTAS": t_score, "Percentil": pc}
    """

    def test_pd_4_es_t_40_percentil_1(self, loader):
        prueba = loader.get_prueba("NiGADSCTAs")
        assert prueba.tipo_calculo == "puntaje_doble_resultado"
        strategy = get_strategy(prueba.tipo_calculo)
        out = strategy.calculate(prueba, pd=4, years=8, months=0)
        assert out.puntaje_escalar == 40, f"esperado 40, recibido {out.puntaje_escalar}"
        assert out.metadata.get("percentil") == 1
        assert out.llave_usada == "4"

    def test_pd_alto_genera_t_clinico(self, loader):
        prueba = loader.get_prueba("NiGADSCTAs")
        strategy = get_strategy(prueba.tipo_calculo)
        # Probamos algunos PD altos típicos de TEA
        for pd in [30, 40, 50]:
            out = strategy.calculate(prueba, pd=pd, years=10, months=0)
            assert out.puntaje_escalar is not None, f"PD={pd} debería tener escalar"
            # T puede ser >100 en casos clínicos extremos (GADS llega hasta ~120)
            assert 30 <= out.puntaje_escalar <= 130, f"T fuera de rango razonable: {out.puntaje_escalar}"
            # PD alto debe correlacionar con percentil alto
            assert out.metadata["percentil"] >= 10, f"PD={pd}, percentil esperado mayor: {out.metadata}"

    def test_pd_fuera_de_rango_marca_not_found(self, loader):
        prueba = loader.get_prueba("NiGADSCTAs")
        strategy = get_strategy(prueba.tipo_calculo)
        # PD=999 NO está en el baremo (máx ~60)
        out = strategy.calculate(prueba, pd=999, years=10, months=0)
        assert out.puntaje_escalar is None
        assert out.metadata.get("out_of_baremo") is True

    def test_pd_es_9999_sin_dato(self, loader):
        """9999 es la convención VBA para 'prueba no realizada'."""
        prueba = loader.get_prueba("NiGADSCTAs")
        strategy = get_strategy(prueba.tipo_calculo)
        out = strategy.calculate(prueba, pd=9999, years=8, months=0)
        assert out.puntaje_bruto is None
        assert out.puntaje_escalar is None


# ═══════════════════════════════════════════════════════════════════
# NiCDI — edad_sexo
# ═══════════════════════════════════════════════════════════════════

class TestNiCDI:
    """Inventario de Depresión Infantil de Kovacs.
    Schema: baremo["{rango_edad}{sexo}"] = [sexo, rango, media, sd]
    Rangos: 78 (7-8a), 910 (9-10a), 1115 (11-15a)
    Calcula Z = (PD - media) / sd
    """

    def test_pd_alto_nino_masculino(self, loader):
        prueba = loader.get_prueba("NiCDI")
        assert prueba.tipo_calculo == "edad_sexo"
        strategy = get_strategy(prueba.tipo_calculo)
        # Niño 8a M, PD=20 (depresión moderada)
        # Baremo 78H: [H, 78, 9.69, 9.05] → Z = (20-9.69)/9.05 = 1.14
        out = strategy.calculate(prueba, pd=20, years=8, months=0, sexo="H")
        assert out.puntaje_escalar is not None
        assert abs(out.puntaje_escalar - 1.14) < 0.05
        assert out.llave_usada == "78H"

    def test_pd_promedio_nina_femenina(self, loader):
        prueba = loader.get_prueba("NiCDI")
        strategy = get_strategy(prueba.tipo_calculo)
        # Niña 9a F, PD=10 (cerca de la media 10.36)
        # Baremo 910M: [M, 910, 10.36, 5.69] → Z = (10-10.36)/5.69 = -0.06
        out = strategy.calculate(prueba, pd=10, years=9, months=0, sexo="M")
        assert out.puntaje_escalar is not None
        assert abs(out.puntaje_escalar - (-0.06)) < 0.05
        assert out.llave_usada == "910M"

    def test_pd_alto_adolescente_femenina(self, loader):
        prueba = loader.get_prueba("NiCDI")
        strategy = get_strategy(prueba.tipo_calculo)
        # Adolescente 14a F, PD=25 (clínico)
        # Baremo 1115M: [M, 1115, 12.52, 6.46] → Z = (25-12.52)/6.46 = 1.93
        out = strategy.calculate(prueba, pd=25, years=14, months=0, sexo="M")
        assert out.puntaje_escalar is not None
        assert abs(out.puntaje_escalar - 1.93) < 0.05
        assert out.llave_usada == "1115M"

    def test_edad_6_fuera_de_rango(self, loader):
        """CDI cubre 7-15 años. Niño 6a no aplica."""
        prueba = loader.get_prueba("NiCDI")
        strategy = get_strategy(prueba.tipo_calculo)
        out = strategy.calculate(prueba, pd=10, years=6, months=0, sexo="H")
        # Debe marcar not_found porque edad 6 no encaja en ningún rango (78/910/1115)
        assert out.puntaje_escalar is None
        assert out.metadata.get("out_of_baremo") is True

    def test_edad_16_fuera_de_rango(self, loader):
        """CDI cubre hasta 15a. Adolescente 16a no aplica."""
        prueba = loader.get_prueba("NiCDI")
        strategy = get_strategy(prueba.tipo_calculo)
        out = strategy.calculate(prueba, pd=10, years=16, months=0, sexo="M")
        assert out.puntaje_escalar is None

    def test_sexo_invalido_se_intenta_aun_asi(self, loader):
        """Si sexo='X', el lookup fallará pero el motor no debe lanzar excepción."""
        prueba = loader.get_prueba("NiCDI")
        strategy = get_strategy(prueba.tipo_calculo)
        out = strategy.calculate(prueba, pd=10, years=10, months=0, sexo="X")
        # Llave construida sería "910X" que no existe
        assert out.puntaje_escalar is None
        assert out.metadata.get("out_of_baremo") is True


# ═══════════════════════════════════════════════════════════════════
# Integración con engine completo
# ═══════════════════════════════════════════════════════════════════

class TestIntegracionEngine:
    """Verificación end-to-end pasando por engine.score()."""

    def test_engine_score_gads_y_cdi_juntos(self, loader):
        from datetime import date

        from app.domain.clinical_engine.engine import PatientContext

        engine = ClinicalEngine(loader)
        ctx = PatientContext.from_demographics(
            birth_date=date(2016, 1, 15),       # 9 años en 2025
            evaluation_date=date(2025, 5, 15),
            sexo="H", escolaridad="Primaria",
        )
        result = engine.score(
            paciente_id="test_n3",
            puntajes={"NiGADSCTAs": 25, "NiCDI": 15},
            patient_context=ctx,
        )
        ids = {r.test_id: r for r in result.resultados}
        assert "NiGADSCTAs" in ids
        assert "NiCDI" in ids
        assert ids["NiGADSCTAs"].puntaje_escalar is not None
        assert ids["NiCDI"].puntaje_escalar is not None
        # Ambos devuelven Z-score / T-score válidos
        # CDI baremo 910H: [H, 910, 9.93, 6.38] → Z = (15-9.93)/6.38 = 0.79
        assert abs(ids["NiCDI"].puntaje_escalar - 0.79) < 0.05
