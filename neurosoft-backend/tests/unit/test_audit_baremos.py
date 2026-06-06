"""
S5.x — Tests del auditor de baremos (F7).
"""

import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
SCRIPT = ROOT / "scripts" / "audit_baremos_18.py"
BAREMOS = ROOT / "data" / "BD_NEURO_MAESTRA.json"


class TestAuditScript:
    def test_script_existe(self):
        assert SCRIPT.exists(), f"No se encontró {SCRIPT}"

    def test_script_ejecuta_y_genera_md_en_stdout(self):
        if not BAREMOS.exists():
            pytest.skip(f"BD_NEURO_MAESTRA.json no encontrada en {BAREMOS}")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        assert result.returncode == 0, f"Falla: {result.stderr}"
        assert "# Auditoría" in result.stdout
        assert "## 1. Resumen ejecutivo" in result.stdout
        assert "## 2. Detalle por prueba" in result.stdout
        # F7.2 post-migración: sección revisión sólo aparece si hay tests
        # en BAREMOS_EN_REVISION (vacío por ahora). El header se reordena.
        assert "## 5. Recomendaciones" in result.stdout

    def test_baremos_path_invalido_falla(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--baremos", "/nonexistent.json"],
            capture_output=True,
            text=True,
            timeout=10,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode != 0
        assert result.stderr is not None
        assert "ERROR" in result.stderr or "No such file" in result.stderr

    def test_reporte_tiene_tabla_y_metricas(self):
        if not BAREMOS.exists():
            pytest.skip(f"BD_NEURO_MAESTRA.json no encontrada en {BAREMOS}")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        md = result.stdout
        # Debe tener formato de tabla markdown
        assert "| Test ID" in md
        assert "| `AdWAISCC`" in md
        assert "Anomalías" in md

    def test_reporte_no_modifica_bd(self):
        """Verifica que la auditoría es de sólo lectura."""
        if not BAREMOS.exists():
            pytest.skip(f"BD_NEURO_MAESTRA.json no encontrada en {BAREMOS}")
        # Capturar mtime antes
        mtime_before = BAREMOS.stat().st_mtime
        size_before = BAREMOS.stat().st_size
        # Correr auditoría
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--out", str(ROOT / "test_audit_tmp.md")],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        assert result.returncode == 0
        # Verificar mtime no cambió
        mtime_after = BAREMOS.stat().st_mtime
        size_after = BAREMOS.stat().st_size
        assert mtime_before == mtime_after, "BD_NEURO_MAESTRA.json fue modificada"
        assert size_before == size_after, "Tamaño de BD_NEURO_MAESTRA.json cambió"
        # Limpiar
        out_tmp = ROOT / "test_audit_tmp.md"
        if out_tmp.exists():
            out_tmp.unlink()

    def test_f7_2_post_migracion_adbeck_bdi_ii_en_bd(self):
        """F7.2 (post-migración) — AdBeck debe aparecer con baremo BDI-II
        (4 bandas: Mínima/Leve/Moderada/Severa) en la tabla, SIN marca
        de revisión (el BD ya está corregido)."""
        if not BAREMOS.exists():
            pytest.skip(f"BD_NEURO_MAESTRA.json no encontrada en {BAREMOS}")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        assert result.returncode == 0
        md = result.stdout
        # AdBeck presente
        assert "`AdBeck`" in md
        # F7.2: ya NO tiene keys 16190..16195 (Excel heredado)
        assert "16190" not in md
        assert "16195" not in md
        # Y NO debe tener anomalía de valor_maximo_atipico
        # (porque el valor 1619 ya no está en el baremo)
        adbeck_lines = [l for l in md.splitlines() if "`AdBeck`" in l]
        assert len(adbeck_lines) == 1
        adbeck_line = adbeck_lines[0]
        assert "valor_maximo_atipico" not in adbeck_line, f"AdBeck sigue con anomalía tras F7.2: {adbeck_line}"

    def test_f7_2_short_form_whitelist_no_marca_anomalia(self):
        """F7.2 — EscKertesz, EscLawton, EscYesavage, MMSE están en
        SHORT_FORM_BAREMOS y NO deben aparecer como anomalía cobertura_baja
        (tienen baremo discreto por diseño)."""
        if not BAREMOS.exists():
            pytest.skip(f"BD_NEURO_MAESTRA.json no encontrada en {BAREMOS}")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True,
            text=True,
            timeout=30,
            encoding="utf-8",
        )
        assert result.returncode == 0
        md = result.stdout
        # Verificar que EscKertesz/EscLawton/EscYesavage/MMSE están en la tabla
        for tid in ("EscKertesz", "EscLawton", "EscYesavage", "MMSE"):
            assert tid in md, f"{tid} no aparece en el reporte"
        # El short-form ✔ debe aparecer
        assert "short-form" in md
        # Y la columna Anomalías de estos tests debe ser "—" (vacía)
        # (no debe decir "cobertura_baja" junto a ellos)
        for line in md.splitlines():
            if "`EscKertesz`" in line or "`EscLawton`" in line or "`EscYesavage`" in line or "`MMSE`" in line:
                assert "cobertura_baja" not in line, f"short-form marcado como cobertura_baja: {line}"
