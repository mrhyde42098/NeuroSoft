"""Tests para módulo de validez de síntomas en informes médico-legales."""

from app.infrastructure.report_pro.validez import (
    construir_texto_validez_pdf,
    evaluar_validez_desde_resultados,
    extraer_puntuaciones_validez,
)

VALIDEZ_TEMPLATE = "Sin pruebas de validez."


class TestValidezExtraccion:
    def test_extrae_rey15_y_tomm(self):
        resultados = [
            {"test_id": "REY15", "puntaje_bruto": 7},
            {"test_id": "TOMM", "puntaje_bruto": 42, "metadata": {"trial": 2}},
        ]
        scores = extraer_puntuaciones_validez(resultados)
        assert scores["rey15"] == 7
        assert scores["tomm_trial2"] == 42

    def test_rey15_suboptimo_tomm_valido(self):
        resultados = [
            {"test_id": "REY15", "puntaje_bruto": 6},
            {"test_id": "TOMM", "puntaje_bruto": 48},
        ]
        ev = evaluar_validez_desde_resultados(resultados)
        assert "Rey 15-Item" in ev["svt_fallidas"]
        assert "TOMM Trial 2" not in ev["svt_fallidas"]
        assert ev["reserva_interpretativa"]

    def test_ambas_validas_sin_reserva(self):
        resultados = [
            {"test_id": "REY15", "puntaje_bruto": 12},
            {"test_id": "TOMM", "puntaje_bruto": 47},
        ]
        ev = evaluar_validez_desde_resultados(resultados)
        assert ev["svt_fallidas"] == []
        assert not ev["reserva_interpretativa"]

    def test_sin_pruebas_usa_template(self):
        cuerpo, titulo, alerta = construir_texto_validez_pdf(
            [],
            template_sin_pruebas=VALIDEZ_TEMPLATE,
        )
        assert cuerpo == VALIDEZ_TEMPLATE
        assert alerta is True

    def test_con_pruebas_no_usa_template_negacion(self):
        resultados = [{"test_id": "REY15", "puntaje_bruto": 11}]
        cuerpo, titulo, alerta = construir_texto_validez_pdf(
            resultados,
            template_sin_pruebas=VALIDEZ_TEMPLATE,
        )
        assert "No se incluyeron" not in cuerpo
        assert "Rey 15-Item: 11/15" in cuerpo
        assert alerta is False
