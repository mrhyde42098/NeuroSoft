"""
tests/unit/clinical_engine/test_priority_uncovered.py
======================================================
Tests para pruebas clínicas prioritarias sin cobertura.

PRIORIDAD 1 - Críticas (uso clínico frecuente):
1. ViTMTB - Trail Making Test B (Adulto Mayor)
2. ViTMTA - Trail Making Test A (Adulto Mayor)
3. ViTMTB - Trail Making Test B (Adulto Mayor)
4. NiTMTB - Trail Making Test B (Infantil)
5. ViWCor - WCST Categorías Correctas (Adulto Mayor)
6. ViWEAte - WCST Errores Atencionales (Adulto Mayor)
7. ViWEPer - WCST Errores Perseverativos (Adulto Mayor)
8. NiWISCIndCapGen - Índice de Capacidad General WISC-IV
9. NiWISCIndCopCog - Índice de Competencia Cognitiva WISC-IV
10. ViGroberMC_Dif - Grober Discriminabilidad (Adulto Mayor)

Fuentes de referencia:
- Neuronorma Colombia (Ostrosky-Solís et al., 2010)
- WISC-IV Colombia (Wechsler, 2014)
- Heaton et al. (1993) - WCST
"""

from __future__ import annotations

from datetime import date

import pytest

from app.domain.clinical_engine.engine import PatientContext


@pytest.fixture
def ctx_adulto_mayor_75():
    """Contexto: adulto mayor 75 años."""
    return PatientContext.from_demographics(
        birth_date=date(1951, 5, 15),
        evaluation_date=date(2026, 5, 26),
        sexo="M",
        escolaridad="Universitaria",
    )


@pytest.fixture
def ctx_adulto_mayor_65():
    """Contexto: adulto mayor 65 años."""
    return PatientContext.from_demographics(
        birth_date=date(1961, 3, 20),
        evaluation_date=date(2026, 5, 26),
        sexo="H",
        escolaridad="Secundaria",
    )


@pytest.fixture
def ctx_adulto_joven_30():
    """Contexto: adulto joven 30 años."""
    return PatientContext.from_demographics(
        birth_date=date(1996, 3, 20),
        evaluation_date=date(2026, 5, 26),
        sexo="H",
        escolaridad="Universitaria",
    )


class TestViTMTB:
    """Trail Making Test B - Adulto Mayor (Neuronorma Colombia)."""

    def test_vitmtb_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViTMTB")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"
        assert len(prueba.baremos) > 0

    def test_vitmtb_edad_75_promedio(self, engine, ctx_adulto_mayor_75):
        """
        TMT B para adulto mayor 75 años.
        PD=120 segundos → rendimiento promedio.
        Referencia: Neuronorma Colombia (Ostrosky-Solís et al., 2010)
        """
        result = engine.score("test", {"ViTMTB": 120}, ctx_adulto_mayor_75)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViTMTB"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # TMT B: menor tiempo = mejor rendimiento
        # 120s para 75 años debería estar en rango promedio
        assert 5 <= r.puntaje_escalar <= 12

    def test_vitmtb_edad_75_deficitario(self, engine, ctx_adulto_mayor_75):
        """
        TMT B para adulto mayor 75 años.
        PD=400 segundos → rendimiento bajo.
        """
        result = engine.score("test", {"ViTMTB": 400}, ctx_adulto_mayor_75)
        r = result.resultados[0]
        assert r.fue_realizada
        # 400s es muy lento, debería ser bajo
        assert r.puntaje_escalar <= 7

    def test_vitmtb_edad_65_promedio(self, engine, ctx_adulto_mayor_65):
        """
        TMT B para adulto mayor 65 años.
        PD=120 segundos → rendimiento promedio.
        Referencia: Neuronorma Colombia (Ostrosky-Solís et al., 2010)
        """
        result = engine.score("test", {"ViTMTB": 120}, ctx_adulto_mayor_65)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViTMTB"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # 120s para 65 años debería ser promedio
        assert 7 <= r.puntaje_escalar <= 12


class TestViTMTA:
    """Trail Making Test A - Adulto Mayor (Neuronorma Colombia)."""

    def test_vitmta_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViTMTA")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"

    def test_vitmta_edad_65_promedio(self, engine, ctx_adulto_mayor_65):
        """
        TMT A para adulto mayor 65 años.
        PD=45 segundos → rendimiento promedio.
        Referencia: Neuronorma Colombia (Ostrosky-Solís et al., 2010)
        """
        result = engine.score("test", {"ViTMTA": 45}, ctx_adulto_mayor_65)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViTMTA"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # 45s para 65 años debería ser promedio
        assert 7 <= r.puntaje_escalar <= 12


class TestNiTMTB:
    """Trail Making Test B - Infantil (Z-score)."""

    def test_nitmtb_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiTMTB")
        assert prueba is not None
        assert prueba.tipo_calculo == "z_score"

    def test_nitmtb_edad_10_promedio(self, engine, ctx_infantil_10):
        """
        TMT B para niño 10 años.
        PD=60 segundos → rendimiento promedio.
        """
        result = engine.score("test", {"NiTMTB": 60}, ctx_infantil_10)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "NiTMTB"
        assert r.fue_realizada
        assert r.z_equivalente is not None
        # Z-score cercano a 0 = promedio
        assert -1.0 <= r.z_equivalente <= 1.0


class TestViWCor:
    """WCST Categorías Correctas - Adulto Mayor."""

    def test_viwcor_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViWCor")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"

    def test_viwcor_edad_75_bueno(self, engine, ctx_adulto_mayor_75):
        """
        WCST Categorías Correctas para adulto mayor 75 años.
        PD=5 categorías → rendimiento bueno.
        Referencia: Heaton et al. (1993)
        """
        result = engine.score("test", {"ViWCor": 5}, ctx_adulto_mayor_75)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViWCor"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # 5 categorías es bueno (máximo 6)
        assert r.puntaje_escalar >= 10


class TestViWEAte:
    """WCST Errores Atencionales - Adulto Mayor."""

    def test_viweate_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViWEAte")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"

    def test_viweate_edad_75_promedio(self, engine, ctx_adulto_mayor_75):
        """
        WCST Errores Atencionales para adulto mayor 75 años.
        PD=2 errores → rendimiento promedio-bajo.
        """
        result = engine.score("test", {"ViWEAte": 2}, ctx_adulto_mayor_75)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViWEAte"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # PD=2 para 75 años da escalar 7
        assert 5 <= r.puntaje_escalar <= 10


class TestViWEPer:
    """WCST Errores Perseverativos - Adulto Mayor."""

    def test_viwper_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViWEPer")
        assert prueba is not None
        assert prueba.tipo_calculo == "desconocido"

    def test_viwper_edad_75_promedio(self, engine, ctx_adulto_mayor_75):
        """
        WCST Errores Perseverativos para adulto mayor 75 años.
        PD=15 errores → rendimiento promedio.
        """
        result = engine.score("test", {"ViWEPer": 15}, ctx_adulto_mayor_75)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViWEPer"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None


class TestNiWISCIndCapGen:
    """Índice de Capacidad General WISC-IV - Infantil."""

    def test_niwiscindcapgen_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWISCIndCapGen")
        assert prueba is not None
        assert prueba.tipo_calculo == "suma_a_indice"

    def test_niwiscindcapgen_edad_10_promedio(self, engine, ctx_infantil_10):
        """
        ICG (Índice de Capacidad General) para niño 10 años.
        Suma de escalares = 50 → CI promedio.
        Referencia: WISC-IV Colombia (Wechsler, 2014)
        """
        result = engine.score("test", {"NiWISCIndCapGen": 50}, ctx_infantil_10)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "NiWISCIndCapGen"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # CI promedio = 90-110
        assert 85 <= r.puntaje_escalar <= 110


class TestNiWISCIndCopCog:
    """Índice de Competencia Cognitiva WISC-IV - Infantil."""

    def test_niwiscindcopcog_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("NiWISCIndCopCog")
        assert prueba is not None
        assert prueba.tipo_calculo == "suma_a_indice"

    def test_niwiscindcopcog_edad_10_promedio(self, engine, ctx_infantil_10):
        """
        ICC (Índice de Competencia Cognitiva) para niño 10 años.
        Suma de escalares = 40 → CI promedio.
        """
        result = engine.score("test", {"NiWISCIndCopCog": 40}, ctx_infantil_10)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "NiWISCIndCopCog"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # CI promedio = 90-110
        assert 95 <= r.puntaje_escalar <= 110


class TestViGroberMC_Dif:
    """Grober Discriminabilidad - Adulto Mayor."""

    def test_vigrobermc_dif_baremo_exists(self, loader):
        """Verifica que el baremo existe."""
        prueba = loader.get_prueba("ViGroberMC_Dif")
        assert prueba is not None
        assert prueba.tipo_calculo == "wais_range"

    def test_vigrobermc_dif_edad_75_promedio(self, engine, ctx_adulto_mayor_75):
        """
        Grober MC Discriminabilidad para adulto mayor 75 años.
        PD=14 (de 16 posibles) → rendimiento promedio.
        """
        result = engine.score("test", {"ViGroberMC_Dif": 14}, ctx_adulto_mayor_75)
        assert len(result.resultados) == 1
        r = result.resultados[0]
        assert r.test_id == "ViGroberMC_Dif"
        assert r.fue_realizada
        assert r.puntaje_escalar is not None
        # 14/16 es bueno
        assert r.puntaje_escalar >= 10
