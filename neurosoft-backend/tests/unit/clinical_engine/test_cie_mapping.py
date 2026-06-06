"""Tests del servicio de mapeo CIE-10 → CIE-11."""
from app.domain.clinical_engine.cie_mapping_service import (
    map_cie10_to_cie11,
    resolve_cie11_code,
)


def test_map_cie10_direct():
    r = map_cie10_to_cie11("F32")
    assert r is not None
    assert r["cie11"] == "6A70"


def test_map_cie10_base_fallback():
    r = map_cie10_to_cie11("F321")
    assert r is not None
    assert r["cie11"].startswith("6A70")


def test_map_unknown_returns_none():
    assert map_cie10_to_cie11("Z999") is None


def test_resolve_cie11_code():
    assert resolve_cie11_code("F90") == "6A05"
