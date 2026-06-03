"""
tests/unit/core/test_config_invariants.py
==========================================
Verifica que `Settings.enforce_production_invariants()` aborta el arranque
cuando la configuración es insegura:
  - En desarrollo nunca aborta.
  - En producción sin SECRET_KEY → aborta.
  - En producción con SECRET_KEY de desarrollo → aborta.
  - En producción con SECRET_KEY corto (<32) → aborta.
  - En producción sin ADMIN_PASSWORD → aborta.
  - En producción con ADMIN_PASSWORD corto (<8) → aborta.
  - En producción con CORS "*" → aborta.
  - En producción con SECRET_KEY largo y ADMIN_PASSWORD fuerte → pasa.

Estos tests evitan que una regresión futura deje la app arrancando con
configuración débil en producción (regresión clásica: quitar el check por
accidente al refactorizar config).
"""
from __future__ import annotations

import importlib

import pytest

DEV_SECRET = "neurosoft-dev-secret-key-change-in-production-32chars-min"
STRONG_SECRET = "x" * 48
STRONG_PASSWORD = "correct-horse-battery-staple"


def _fresh_settings():
    """Fuerza reimport de settings con las variables de entorno actuales."""
    import app.core.config as cfg
    importlib.reload(cfg)
    return cfg.Settings()


def _set_env(monkeypatch, **kwargs):
    for k, v in kwargs.items():
        if v is None:
            monkeypatch.delenv(k, raising=False)
        else:
            monkeypatch.setenv(k, v)


@pytest.mark.unit
class TestProductionInvariants:

    def test_dev_no_aborta_aunque_falte_secret(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="development",
            NEUROSOFT_SECRET_KEY=None,
            NEUROSOFT_ADMIN_PASSWORD=None,
            NEUROSOFT_CORS_ORIGINS=None,
        )
        s = _fresh_settings()
        # En BaseSettings mode, enforce_production_invariants existe.
        # En stub mode devuelve [] siempre.
        problems = s.enforce_production_invariants()
        assert problems == []

    def test_prod_sin_secret_lanza_problema(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY="",
            NEUROSOFT_ADMIN_PASSWORD=STRONG_PASSWORD,
            NEUROSOFT_CORS_ORIGINS='["https://clinica.local"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Running in stub Settings mode (pydantic-settings no instalado)")
        problems = s.enforce_production_invariants()
        # Debe aparecer la queja por SECRET_KEY
        assert any("SECRET_KEY" in p for p in problems), problems

    def test_prod_con_secret_default_lanza_problema(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY=DEV_SECRET,
            NEUROSOFT_ADMIN_PASSWORD=STRONG_PASSWORD,
            NEUROSOFT_CORS_ORIGINS='["https://clinica.local"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Stub Settings mode")
        problems = s.enforce_production_invariants()
        assert any("SECRET_KEY" in p for p in problems), problems

    def test_prod_con_secret_corto_lanza_problema(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY="x" * 20,  # menos de 32
            NEUROSOFT_ADMIN_PASSWORD=STRONG_PASSWORD,
            NEUROSOFT_CORS_ORIGINS='["https://clinica.local"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Stub Settings mode")
        problems = s.enforce_production_invariants()
        assert any("demasiado corta" in p.lower() or "corta" in p for p in problems)

    def test_prod_con_admin_password_vacia_lanza_problema(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY=STRONG_SECRET,
            NEUROSOFT_ADMIN_PASSWORD="",
            NEUROSOFT_CORS_ORIGINS='["https://clinica.local"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Stub Settings mode")
        problems = s.enforce_production_invariants()
        assert any("ADMIN_PASSWORD" in p for p in problems)

    def test_prod_con_admin_password_corta_lanza_problema(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY=STRONG_SECRET,
            NEUROSOFT_ADMIN_PASSWORD="1234",
            NEUROSOFT_CORS_ORIGINS='["https://clinica.local"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Stub Settings mode")
        problems = s.enforce_production_invariants()
        assert any("ADMIN_PASSWORD" in p for p in problems)

    def test_prod_con_cors_wildcard_lanza_problema(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY=STRONG_SECRET,
            NEUROSOFT_ADMIN_PASSWORD=STRONG_PASSWORD,
            NEUROSOFT_CORS_ORIGINS='["*"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Stub Settings mode")
        problems = s.enforce_production_invariants()
        assert any("CORS" in p or "*" in p for p in problems), problems

    def test_prod_configuracion_fuerte_no_tiene_problemas(self, monkeypatch):
        _set_env(
            monkeypatch,
            NEUROSOFT_ENV="production",
            NEUROSOFT_SECRET_KEY=STRONG_SECRET,
            NEUROSOFT_ADMIN_PASSWORD=STRONG_PASSWORD,
            NEUROSOFT_CORS_ORIGINS='["https://clinica.local"]',
        )
        s = _fresh_settings()
        if not hasattr(s, "secret_key"):
            pytest.skip("Stub Settings mode")
        problems = s.enforce_production_invariants()
        assert problems == [], f"Config fuerte no debería dar problemas: {problems}"
