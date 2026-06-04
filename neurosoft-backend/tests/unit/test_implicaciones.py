"""
Tests para el módulo de implicaciones para la vida diaria.
"""
import pytest

from app.infrastructure.report_pro.implicaciones import (
    IMPLICACIONES_POR_DOMINIO,
    Z_DEBIL,
    Z_MUY_DEBIL,
    _normalizar_dominio,
    dominios_con_implicaciones,
    texto_implicaciones_para_familia,
)


class TestImplicaciones:
    def test_dominio_normalizado_aliases(self):
        assert _normalizar_dominio("atencion") == "Atención"
        assert _normalizar_dominio("ATENCIÓN") == "Atención"
        assert _normalizar_dominio("ff.ee.") == "Funciones Ejecutivas"
        assert _normalizar_dominio("vp") == "Velocidad de Procesamiento"
        assert _normalizar_dominio("MT") == "Memoria de Trabajo"
        assert _normalizar_dominio("Otro Dominio") == "Otro Dominio"  # sin alias

    def test_dominios_debiles_retornan_implicaciones(self):
        resultados = [
            {"dominio_cognitivo": "Memoria", "z_equivalente": -1.5, "tipo_metrica": "escalar"},
            {"dominio_cognitivo": "Memoria", "z_equivalente": -1.0, "tipo_metrica": "escalar"},
            {"dominio_cognitivo": "Atención", "z_equivalente": -0.5, "tipo_metrica": "escalar"},
        ]
        items = dominios_con_implicaciones(resultados)
        # Memoria Z̄=-1.25 → incluye. Atención Z̄=-0.5 → NO incluye.
        assert len(items) == 1
        assert items[0]["dominio"] == "Memoria"
        assert items[0]["nivel"] == "moderado"
        assert len(items[0]["ejemplos"]) >= 1
        assert len(items[0]["estrategias"]) >= 1

    def test_dominio_muy_debil_es_severo(self):
        resultados = [
            {"dominio_cognitivo": "Atención", "z_equivalente": -2.5, "tipo_metrica": "escalar"},
            {"dominio_cognitivo": "Atención", "z_equivalente": -2.0, "tipo_metrica": "escalar"},
        ]
        items = dominios_con_implicaciones(resultados)
        assert len(items) == 1
        assert items[0]["nivel"] == "severo"

    def test_dominios_normales_no_incluidos(self):
        resultados = [
            {"dominio_cognitivo": "Memoria", "z_equivalente": 0.5, "tipo_metrica": "escalar"},
            {"dominio_cognitivo": "Lenguaje", "z_equivalente": 1.2, "tipo_metrica": "escalar"},
        ]
        items = dominios_con_implicaciones(resultados)
        assert items == []

    def test_ci_no_se_considera_para_implicaciones(self):
        resultados = [
            {"dominio_cognitivo": "CIT", "z_equivalente": -2.0, "tipo_metrica": "ci"},
            {"dominio_cognitivo": "Memoria", "z_equivalente": 0.5, "tipo_metrica": "escalar"},
        ]
        items = dominios_con_implicaciones(resultados)
        # CIT es tipo ci, no se considera. Memoria es normal. Lista vacía.
        assert items == []

    def test_orden_por_z_mas_debil_primero(self):
        resultados = [
            {"dominio_cognitivo": "Memoria", "z_equivalente": -1.5, "tipo_metrica": "escalar"},
            {"dominio_cognitivo": "Atención", "z_equivalente": -2.5, "tipo_metrica": "escalar"},
            {"dominio_cognitivo": "Lenguaje", "z_equivalente": -1.2, "tipo_metrica": "escalar"},
        ]
        items = dominios_con_implicaciones(resultados)
        assert len(items) == 3
        # Atención más débil primero
        assert items[0]["dominio"] == "Atención"
        assert items[1]["dominio"] == "Memoria"
        assert items[2]["dominio"] == "Lenguaje"

    def test_texto_para_familia_incluye_dominios(self):
        resultados = [
            {"dominio_cognitivo": "Memoria", "z_equivalente": -1.5, "tipo_metrica": "escalar"},
        ]
        texto = texto_implicaciones_para_familia(resultados)
        assert "vida diaria" in texto.lower()
        assert "memoria" in texto.lower()

    def test_texto_vacio_si_sin_debiles(self):
        resultados = [
            {"dominio_cognitivo": "Memoria", "z_equivalente": 0.5, "tipo_metrica": "escalar"},
        ]
        assert texto_implicaciones_para_familia(resultados) == ""

    def test_dominio_desconocido_tiene_implicaciones_genericas(self):
        resultados = [
            {"dominio_cognitivo": "Habilidades Académicas", "z_equivalente": -1.5, "tipo_metrica": "escalar"},
        ]
        items = dominios_con_implicaciones(resultados)
        assert len(items) == 1
        # No hay entry específica → cae en fallback genérico
        assert len(items[0]["ejemplos"]) >= 1
        assert len(items[0]["estrategias"]) >= 1

    def test_estructura_cada_dominio_tiene_campos_completos(self):
        """Todos los dominios canónicos deben tener ejemplos y estrategias."""
        canonicos = [
            "Atención", "Memoria", "Lenguaje", "Funciones Ejecutivas",
            "Razonamiento Perceptual", "Visoconstrucción",
            "Velocidad de Procesamiento", "Comprensión Verbal",
            "Memoria de Trabajo",
        ]
        for dom in canonicos:
            assert dom in IMPLICACIONES_POR_DOMINIO, f"Falta {dom}"
            assert "ejemplos" in IMPLICACIONES_POR_DOMINIO[dom]
            assert "estrategias" in IMPLICACIONES_POR_DOMINIO[dom]
            assert len(IMPLICACIONES_POR_DOMINIO[dom]["ejemplos"]) >= 2
            assert len(IMPLICACIONES_POR_DOMINIO[dom]["estrategias"]) >= 1
