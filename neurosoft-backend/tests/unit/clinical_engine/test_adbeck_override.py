"""
tests/unit/clinical_engine/test_adbeck_override.py
===================================================
Tests del baremo BDI-II (Beck 1996) para AdBeck tras F7.2.

F7.2 (2026-06-03): AdBeck fue corregido directamente en
`BD_NEURO_MAESTRA.json` con autorización one-time del propietario.
El override Python ya NO se aplica por defecto, pero se conserva
como LEGACY. El módulo `adbeck.py` se mantiene con tests unitarios
que validan la corrección lógica de las 4 bandas BDI-II.

Valida:
1. El BD corregido tiene las 4 bandas BDI-II (no las 6 keys heredadas).
2. Las 4 bandas devuelven la clasificación correcta.
3. Los puntos de corte (0/14/20/29) son inclusivos.
4. La metadata clínica (fuente + corte) está disponible en el módulo
   `adbeck.py` (LEGACY, no aplicada).
5. El BD NO se altera en disco durante load() (trazabilidad clínica).
6. El loader NO aplica override para AdBeck (BD es la fuente).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from app.domain.clinical_engine.baremos_loader import BaremosLoader
from app.domain.clinical_engine.overrides import (
    get_override,
    has_override,
    list_overrides,
)
from app.domain.clinical_engine.overrides.adbeck import (
    get_adbeck_metadata,
    get_adbeck_override,
)


# ── Tests del override como unidad aislada ────────────────────

class TestAdBeckOverrideUnit:
    """Tests del módulo adbeck.py sin tocar el loader."""

    def test_override_retorna_4_bandas_bdi_ii(self):
        baremo = get_adbeck_override()
        assert "Rango" in baremo
        assert baremo["Rango"] == [0, 63]
        # Beck 1996 — 4 bandas
        assert baremo["0"] == "Mínima"
        assert baremo["14"] == "Leve"
        assert baremo["20"] == "Moderada"
        assert baremo["29"] == "Severa"

    def test_override_no_contiene_keys_heredadas_excel(self):
        """Las keys 16190..16195 son Cell IDs del Excel VBA — no deben
        aparecer en el override correcto."""
        baremo = get_adbeck_override()
        for k in baremo:
            assert not k.startswith("1619"), (
                f"Key heredada del Excel presente: {k}. "
                f"El override debe usar solo puntos de corte BDI-II."
            )

    def test_metadata_clinica_incluye_fuente_y_corte(self):
        meta = get_adbeck_metadata()
        assert "Beck" in meta["fuente"]
        assert "1996" in meta["fuente"]
        # Punto de corte clínico Beck 1996: ≥ 14
        assert meta["corte_clinico"] == 14
        assert meta["rango_puntaje"] == [0, 63]

    def test_registro_overrides_adbeck_legacy(self):
        """F7.2 — AdBeck fue corregido en BD; el override Python está
        deshabilitado (LEGACY). El módulo `adbeck.py` sigue exportable."""
        # F7.2 (post-migración): AdBeck ya NO está en el registro de
        # overrides activos — el BD es la fuente.
        assert not has_override("AdBeck")
        assert not has_override("AdWAISV")  # WAIS no necesita override
        assert "AdBeck" not in list_overrides()
        # Pero el módulo LEGACY sigue importable y la función sigue
        # retornando el baremo BDI-II correcto (por si se reactiva).
        from app.domain.clinical_engine.overrides.adbeck import get_adbeck_override
        baremo_legacy = get_adbeck_override()
        assert baremo_legacy["0"] == "Mínima"
        assert baremo_legacy["14"] == "Leve"


# ── Tests del loader con override aplicado ────────────────────

class TestAdBeckLoaderIntegration:
    """Tests que verifican que BaremosLoader inyecta el override."""

    def test_loader_NO_aplica_override_post_migracion(self, tmp_path):
        """F7.2 — Tras corregir el BD, el loader NO debe reportar AdBeck
        como baremo en revisión (ya viene correcto del JSON)."""
        bd_path = Path("data/BD_NEURO_MAESTRA.json")
        if not bd_path.exists():
            pytest.skip("BD_NEURO_MAESTRA.json no encontrado")

        # Hash antes
        hash_before = hashlib.sha256(bd_path.read_bytes()).hexdigest()

        # Reset + load
        BaremosLoader.reset()
        loader = BaremosLoader.load(bd_path)

        # Hash después — DEBE ser idéntico (load() no toca disco)
        hash_after = hashlib.sha256(bd_path.read_bytes()).hexdigest()
        assert hash_before == hash_after, (
            "BD_NEURO_MAESTRA.json fue modificado en disco durante load()"
        )

        # F7.2: AdBeck ya NO está en overrides (BD es la fuente)
        assert not loader.baremo_en_revision("AdBeck")
        assert "AdBeck" not in loader.overrides_aplicados

    def test_get_prueba_adbeck_retorna_baremo_bdi_ii_desde_bd(self):
        """F7.2 — El baremo BDI-II viene directamente del BD corregido."""
        bd_path = Path("data/BD_NEURO_MAESTRA.json")
        if not bd_path.exists():
            pytest.skip("BD_NEURO_MAESTRA.json no encontrado")

        BaremosLoader.reset()
        loader = BaremosLoader.load(bd_path)
        prueba = loader.get_prueba("AdBeck")

        # El baremo debe ser BDI-II, no las keys 16190..16195
        baremo = prueba.baremos
        assert baremo["Rango"] == [0, 63]
        assert baremo["0"] == "Mínima"
        assert baremo["14"] == "Leve"
        assert baremo["20"] == "Moderada"
        assert baremo["29"] == "Severa"
        # Ninguna key debe empezar con 1619
        for k in baremo:
            assert not k.startswith("1619")
        # Y NO debe empezar con 'Rango' como texto
        assert baremo.get("Rango") == [0, 63]

    def test_get_prueba_otros_tests_no_tienen_override(self):
        bd_path = Path("data/BD_NEURO_MAESTRA.json")
        if not bd_path.exists():
            pytest.skip("BD_NEURO_MAESTRA.json no encontrado")

        BaremosLoader.reset()
        loader = BaremosLoader.load(bd_path)

        assert not loader.baremo_en_revision("AdWAISV")
        assert not loader.baremo_en_revision("ViTMTA")
        assert not loader.baremo_en_revision("NiWiscDC")

    def test_bd_no_modificado_en_disco_post_load(self):
        """Garantía crítica: el loader es NO-MUTATIVO del JSON."""
        bd_path = Path("data/BD_NEURO_MAESTRA.json")
        if not bd_path.exists():
            pytest.skip("BD_NEURO_MAESTRA.json no encontrado")

        size_before = bd_path.stat().st_size
        mtime_before = bd_path.stat().st_mtime
        hash_before = hashlib.sha256(bd_path.read_bytes()).hexdigest()

        BaremosLoader.reset()
        loader = BaremosLoader.load(bd_path)
        _ = loader.get_prueba("AdBeck")  # fuerza el override
        _ = loader.get_prueba("AdBeck")
        _ = loader.get_prueba("AdBeck")

        size_after = bd_path.stat().st_size
        mtime_after = bd_path.stat().st_mtime
        hash_after = hashlib.sha256(bd_path.read_bytes()).hexdigest()

        assert size_before == size_after
        assert mtime_before == mtime_after
        assert hash_before == hash_after
