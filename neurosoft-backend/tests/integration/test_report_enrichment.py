"""
tests/integration/test_report_enrichment.py
============================================
Tests del motor de enriquecimiento de informe
(`app/application/use_cases/report_enrichment.py`).

No toca la base de datos — llama directamente a las helpers públicas
para validar:
  • Cálculo de edad (`_edad_anos`)
  • Mapeo edad → grupo del reservorio (`_grupo_reservorio`)
  • Registro de la ruta `/reports/enrichment/{eval_id}` en el router
  • Auth gate del endpoint
"""
from __future__ import annotations

from datetime import date

import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c


@pytest.mark.integration
class TestRutaEnrichment:

    def test_ruta_enrichment_registrada(self, client):
        from app.main import app
        paths = {getattr(r, "path", "") for r in app.routes}
        assert "/api/v1/reports/enrichment/{eval_id}" in paths

    def test_enrichment_requiere_token(self, client):
        r = client.get("/api/v1/reports/enrichment/fake-id")
        assert r.status_code == 401


@pytest.mark.integration
class TestEdadYGrupo:

    def test_edad_anos_basico(self):
        from app.application.use_cases.report_enrichment import _edad_anos
        ref = date(2025, 1, 1)
        assert _edad_anos(date(2000, 1, 1), ref) == 25
        # Cumple después de la fecha de referencia
        assert _edad_anos(date(2000, 6, 1), ref) == 24

    def test_edad_con_fecha_nacimiento_none(self):
        from app.application.use_cases.report_enrichment import _edad_anos
        assert _edad_anos(None) is None

    def test_edad_no_negativa(self):
        from app.application.use_cases.report_enrichment import _edad_anos
        # Si la fecha de nacimiento es futura, devuelve 0 (no negativo)
        ref = date(2020, 1, 1)
        assert _edad_anos(date(2025, 1, 1), ref) == 0

    def test_grupo_reservorio_infantil(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(5) == "infantil"
        assert _grupo_reservorio(17) == "infantil"

    def test_grupo_reservorio_adulto(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(18) == "adulto"
        assert _grupo_reservorio(49) == "adulto"

    def test_grupo_reservorio_adulto_mayor(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(50) == "adulto_mayor"
        assert _grupo_reservorio(85) == "adulto_mayor"

    def test_grupo_reservorio_none(self):
        from app.application.use_cases.report_enrichment import _grupo_reservorio
        assert _grupo_reservorio(None) is None


@pytest.mark.integration
class TestMapeoCIE10:

    def test_cie10_to_cuadro_mapping_existe(self):
        from app.application.use_cases.report_enrichment import CIE10_TO_CUADRO
        assert isinstance(CIE10_TO_CUADRO, dict)
        # Tres grupos esperados
        assert "infantil" in CIE10_TO_CUADRO
        # F900 (TDAH combinado) debe mapear a "tdah" para infantil
        assert CIE10_TO_CUADRO["infantil"].get("F900") == "tdah"


@pytest.mark.integration
class TestBuildReportEnrichment:

    def test_build_devuelve_dict_con_keys_minimas(self):
        from app.application.use_cases.report_enrichment import build_report_enrichment
        result = build_report_enrichment(
            eval_id="test-eval-1",
            patient_id="test-pat-1",
            fecha_nacimiento=date(1990, 1, 1),
            codigo_cie10="F411",
        )
        # EnrichmentResult dataclass — se serializa con .__dict__ o asdict
        d = result if isinstance(result, dict) else getattr(result, "__dict__", {})
        if not d:
            from dataclasses import asdict, is_dataclass
            if is_dataclass(result):
                d = asdict(result)
        assert isinstance(d, dict)
        # Campos esperables del dataclass EnrichmentResult
        assert "edad" in d
        assert "cuadro_detectado" in d

    def test_build_sin_fecha_nacimiento_no_explota(self):
        from app.application.use_cases.report_enrichment import build_report_enrichment
        result = build_report_enrichment(
            eval_id="test-eval-2",
            patient_id="test-pat-2",
            fecha_nacimiento=None,
            codigo_cie10=None,
        )
        assert result is not None
        d = result if isinstance(result, dict) else getattr(result, "__dict__", {})
        if not d:
            from dataclasses import asdict, is_dataclass
            if is_dataclass(result):
                d = asdict(result)
        assert d.get("edad") is None
