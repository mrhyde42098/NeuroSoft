"""
F19 — Tests del sistema de identidad configurable.
"""
import json
import os
import pytest
import sqlite3
import tempfile
from pathlib import Path

from app.core.config_institucion import (
    InstitucionConfig,
    demo_data,
    get_config_institucion,
    save_institucion_config,
    load_institucion_config,
    invalidate_cache,
)


class TestInstitucionConfig:
    def test_defaults_son_vacios(self):
        cfg = InstitucionConfig()
        assert cfg.nombre_completo == ""
        assert cfg.tarjeta_profesional == ""
        assert cfg.institucion_nit == ""
        # Ningún campo con valor por defecto que no sea vacío
        for f in cfg.to_dict().values():
            assert f == "", f"Default de {f!r} no es vacío"

    def test_campos_obligatorios_completos_false_con_defaults(self):
        cfg = InstitucionConfig()
        assert cfg.campos_obligatorios_completos() is False

    def test_campos_obligatorios_completos_true_con_datos(self):
        cfg = InstitucionConfig(
            nombre_completo="Ps. Johan Salgado",
            tarjeta_profesional="TP-12345",
        )
        assert cfg.campos_obligatorios_completos() is True

    def test_campos_obligatorios_completos_false_solo_con_nombre(self):
        cfg = InstitucionConfig(nombre_completo="Ps. X")
        assert cfg.campos_obligatorios_completos() is False

    def test_campos_obligatorios_completos_false_solo_con_tarjeta(self):
        cfg = InstitucionConfig(tarjeta_profesional="TP-12345")
        assert cfg.campos_obligatorios_completos() is False

    def test_puede_generar_rips_false_sin_nit(self):
        cfg = InstitucionConfig(
            nombre_completo="Ps. X",
            tarjeta_profesional="TP-12345",
        )
        assert cfg.puede_generar_rips() is False

    def test_puede_generar_rips_true_con_todo(self):
        cfg = InstitucionConfig(
            nombre_completo="Ps. X",
            tarjeta_profesional="TP-12345",
            institucion_nit="900.123.456-7",
        )
        assert cfg.puede_generar_rips() is True

    def test_placeholders_rellenan_campos_vacios(self):
        cfg = InstitucionConfig(nombre_completo="Ps. Real")
        ph = cfg.placeholders()
        assert ph["nombre_completo"] == "Ps. Real"
        assert ph["tarjeta_profesional"] == "[TARJETA PROFESIONAL]"
        assert ph["institucion_nit"] == "[NIT]"
        assert ph["codigo_habilitacion"] == "[CÓDIGO HABILITACIÓN]"

    def test_from_dict_ignora_claves_desconocidas(self):
        cfg = InstitucionConfig.from_dict(
            {"nombre_completo": "Ps. X", "campo_inventado": "ignorar"}
        )
        assert cfg.nombre_completo == "Ps. X"

    def test_to_dict_incluye_los_14_campos(self):
        cfg = InstitucionConfig()
        d = cfg.to_dict()
        assert len(d) == 14
        # Verifica que los nombres del F19.1 están presentes
        for f in [
            "nombre_completo", "tarjeta_profesional", "universidad", "fecha_tarjeta",
            "resolucion", "institucion_nombre", "institucion_nit",
            "institucion_direccion", "institucion_telefono", "institucion_correo",
            "institucion_logo_path", "pie_pagina_pdf", "codigo_habilitacion",
            "sello_digital_path",
        ]:
            assert f in d, f"Falta campo {f}"


class TestDemoData:
    def test_demo_marca_todos_los_campos_como_demo(self):
        cfg = demo_data()
        # Todos los campos con valor deben llevar marca [DEMO]
        for k, v in cfg.to_dict().items():
            if v:
                assert v.startswith("[DEMO]"), f"{k}={v!r} no es DEMO"

    def test_demo_cumple_obligatorios(self):
        """Aunque los datos sean demo, debe poder 'simular' generación de informes."""
        cfg = demo_data()
        assert cfg.campos_obligatorios_completos() is True
        assert cfg.puede_generar_rips() is True


class TestPersistenciaBD:
    def test_save_y_load_roundtrip(self, tmp_path, monkeypatch):
        """Persiste y recupera los datos correctamente."""
        # Crear BD vacía
        db_path = tmp_path / "test.db"
        monkeypatch.setenv("NEUROSOFT_DB_PATH", str(db_path))
        invalidate_cache()

        cfg = InstitucionConfig(
            nombre_completo="Ps. Test",
            tarjeta_profesional="TP-99999",
            institucion_nit="900.111.222-3",
            institucion_nombre="Consultorio X",
        )
        save_institucion_config(cfg)

        # Invalidar caché y volver a cargar
        invalidate_cache()
        loaded = load_institucion_config()
        assert loaded.nombre_completo == "Ps. Test"
        assert loaded.tarjeta_profesional == "TP-99999"
        assert loaded.institucion_nit == "900.111.222-3"

    def test_load_retorna_defaults_si_bd_no_existe(self, tmp_path, monkeypatch):
        monkeypatch.setenv("NEUROSOFT_DB_PATH", str(tmp_path / "nonexistent.db"))
        invalidate_cache()
        cfg = load_institucion_config()
        assert cfg.nombre_completo == ""

    def test_save_actualiza_registro_existente(self, tmp_path, monkeypatch):
        db_path = tmp_path / "test.db"
        monkeypatch.setenv("NEUROSOFT_DB_PATH", str(db_path))
        invalidate_cache()

        cfg1 = InstitucionConfig(nombre_completo="Primero")
        save_institucion_config(cfg1)

        cfg2 = InstitucionConfig(nombre_completo="Segundo")
        save_institucion_config(cfg2)

        invalidate_cache()
        loaded = load_institucion_config()
        assert loaded.nombre_completo == "Segundo"


class TestSinAtribucionTerceros:
    """F19 — Garantizar que NUNCA se asigne automáticamente un autor tercero."""

    def test_defaults_no_contienen_nombres_de_terceros(self):
        cfg = InstitucionConfig()
        forbidden = ["in&s", "salgado", "therapyside", "psicologia ltda"]
        for k, v in cfg.to_dict().items():
            if v:
                vl = v.lower()
                for f in forbidden:
                    assert f not in vl, f"{k}={v!r} contiene nombre prohibido {f!r}"

    def test_demo_data_no_contiene_datos_reales(self):
        cfg = demo_data()
        # Los demo data no deben parecerse a datos reales
        for v in cfg.to_dict().values():
            if v:
                assert v.startswith("[DEMO]"), f"demo data sin marca [DEMO]: {v!r}"
