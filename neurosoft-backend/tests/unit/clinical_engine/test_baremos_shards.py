"""Tests del modo shards de BaremosLoader."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
MASTER = ROOT / "data" / "BD_NEURO_MAESTRA.json"
SHARDS = ROOT / "data" / "baremos_shards"


@pytest.fixture
def shard_loader():
    from app.domain.clinical_engine.baremos_loader import BaremosLoader

    BaremosLoader.reset()
    if not (SHARDS / "manifest.json").exists():
        pytest.skip("baremos_shards no generados — correr split_baremos_poblacion.py")
    return BaremosLoader.load(MASTER)


def test_shard_loader_index(shard_loader):
    assert shard_loader.total_pruebas > 100


def test_shard_materialize_prueba(shard_loader):
    prueba = shard_loader.get_prueba("NiWiscDC")
    assert prueba.nombre
    assert prueba.poblacion == "infantil"


def test_shard_poblacion_lazy_cache(shard_loader):
    shard_loader.get_prueba("AdBeck")
    assert "adulto_joven" in shard_loader._poblacion_cache
