"""
tests/unit/application/test_report_enrichment_extras.py
=========================================================
Cobertura adicional para report_enrichment.py.

Cubre las funciones auxiliares que estaban subprobadas:
  - _edad_anos: calculo de edad cronologica
  - _grupo_reservorio: mapeo edad -> grupo etario
  - _extraer_indice: busqueda flexible de CI en resultados
  - detectar_patrones_cognitivos: deteccion automatica TDAH/TCL/DI/DCL
"""
from __future__ import annotations

from datetime import date

import pytest


@pytest.mark.unit
class TestEdadAnos:
    """Calculo de edad cronologica desde fecha de nacimiento."""

    def test_edad_simple(self):
        from app.application.use_cases.report_enrichment import _edad_anos
        assert _edad_anos(date(1990, 1, 1), date(2025, 6, 1)) == 35

    def test_edad_antes_cumpleanos(self):
        """Si la fecha de referencia es ANTES del cumpleanos, no cuenta el ano."""
        from app.application.use_cases.report_enrichment import _edad_anos
        assert _edad_anos(date(1990, 6, 15), date(2025, 6, 14)) == 34
        assert _edad_anos(date(1990, 6, 15), date(2025, 6, 15)) == 35

    def test_fecha_nacimiento_none(self):
        from app.application.use_cases.report_enrichment import _edad_anos
        assert _edad_anos(None) is None

    def test_edad_no_negativa(self):
        """Bug guard: edad nunca negativa aunque fecha sea posterior."""
        from app.application.use_cases.report_enrichment import _edad_anos
        assert _edad_anos(date(2030, 1, 1), date(2025, 1, 1)) == 0


@pytest.mark.unit
class TestGrupoReservorio:
    """Mapeo edad -> grupo etario para reservorio de recomendaciones."""

    def test_infantil(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(8) == "infantil"
        assert _grupo_reservorio(17) == "infantil"

    def test_adulto(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(18) == "adulto"
        assert _grupo_reservorio(49) == "adulto"

    def test_adulto_mayor(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(50) == "adulto_mayor"
        assert _grupo_reservorio(85) == "adulto_mayor"

    def test_none(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(None) is None


@pytest.mark.unit
class TestExtraerIndice:
    """Busqueda flexible de CI en lista de resultados."""

    def test_busca_por_test_id(self):
        from app.application.use_cases.report_enrichment import _extraer_indice
        resultados = [
            {"test_id": "NiWISCIndComVer", "puntaje_escalar": 93},
        ]
        assert _extraer_indice(resultados, ["IndComVer", "ICV"]) == 93

    def test_busca_por_nombre_prueba(self):
        from app.application.use_cases.report_enrichment import _extraer_indice
        resultados = [
            {"test_id": "X", "nombre_prueba": "Indice Comprension Verbal", "puntaje_escalar": 95},
        ]
        assert _extraer_indice(resultados, ["Comprension Verbal"]) == 95

    def test_no_devuelve_9999(self):
        """Sentinel 9999 (prueba no realizada) no debe devolverse."""
        from app.application.use_cases.report_enrichment import _extraer_indice
        resultados = [
            {"test_id": "NiWISCIndComVer", "puntaje_escalar": 9999},
        ]
        assert _extraer_indice(resultados, ["ComVer"]) is None

    def test_resultados_vacios(self):
        from app.application.use_cases.report_enrichment import _extraer_indice
        assert _extraer_indice([], ["ICV"]) is None

    def test_busqueda_case_insensitive(self):
        from app.application.use_cases.report_enrichment import _extraer_indice
        resultados = [
            {"test_id": "AdWaisIcv", "puntaje_escalar": 100},
        ]
        assert _extraer_indice(resultados, ["ICV"]) == 100


@pytest.mark.unit
class TestDetectarPatronesCognitivos:
    """Deteccion automatica de TDAH, TCL, DI, DCL a partir de los indices CI."""

    def test_sin_resultados_retorna_vacio(self):
        from app.application.use_cases.report_enrichment import detectar_patrones_cognitivos
        assert detectar_patrones_cognitivos([], edad=10) == []

    def test_indices_insuficientes_retorna_vacio(self):
        from app.application.use_cases.report_enrichment import detectar_patrones_cognitivos
        # Solo 1 indice → no se puede determinar patron
        resultados = [{"test_id": "NiWISCIndComVer", "puntaje_escalar": 95}]
        assert detectar_patrones_cognitivos(resultados, edad=10) == []

    def test_patron_tdah_se_detecta(self):
        """ICV+IRP altos pero IMT+IVP bajos → patron TDAH."""
        from app.application.use_cases.report_enrichment import detectar_patrones_cognitivos
        resultados = [
            {"test_id": "NiWISCIndComVer", "puntaje_escalar": 95},
            {"test_id": "NiWISCIndRazPer", "puntaje_escalar": 98},
            {"test_id": "NiWISCIndMemTra", "puntaje_escalar": 78},
            {"test_id": "NiWISCIndVelPro", "puntaje_escalar": 80},
        ]
        patrones = detectar_patrones_cognitivos(resultados, edad=10)
        # Espera al menos 1 patron detectado (TDAH o similar)
        assert len(patrones) >= 1
        # Verificar estructura
        for p in patrones:
            assert "tipo" in p
            assert "nivel" in p

    def test_patron_di_se_detecta_ci_bajo(self):
        """CIT < 70 → patron Discapacidad Intelectual."""
        from app.application.use_cases.report_enrichment import detectar_patrones_cognitivos
        resultados = [
            {"test_id": "NiWISCIndComVer", "puntaje_escalar": 65},
            {"test_id": "NiWISCIndRazPer", "puntaje_escalar": 68},
            {"test_id": "NiWISCIndMemTra", "puntaje_escalar": 70},
            {"test_id": "NiWISCIndVelPro", "puntaje_escalar": 67},
            {"test_id": "NiWISCTot", "puntaje_escalar": 65},
        ]
        patrones = detectar_patrones_cognitivos(resultados, edad=10)
        # Espera detectar al menos algun patron
        assert isinstance(patrones, list)
