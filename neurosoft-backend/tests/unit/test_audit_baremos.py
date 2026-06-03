"""
S5.x — Tests del auditor de baremos (F7).
"""
import json
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
            capture_output=True, text=True, timeout=30, encoding="utf-8",
        )
        assert result.returncode == 0, f"Falla: {result.stderr}"
        assert "# Auditoría" in result.stdout
        assert "## 1. Resumen ejecutivo" in result.stdout
        assert "## 2. Detalle por prueba" in result.stdout
        assert "## 4. Recomendaciones" in result.stdout

    def test_baremos_path_invalido_falla(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--baremos", "/nonexistent.json"],
            capture_output=True, text=True, timeout=10, encoding="utf-8", errors="replace",
        )
        assert result.returncode != 0
        assert result.stderr is not None
        assert "ERROR" in result.stderr or "No such file" in result.stderr

    def test_reporte_tiene_tabla_y_metricas(self):
        if not BAREMOS.exists():
            pytest.skip(f"BD_NEURO_MAESTRA.json no encontrada en {BAREMOS}")
        result = subprocess.run(
            [sys.executable, str(SCRIPT)],
            capture_output=True, text=True, timeout=30, encoding="utf-8",
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
            capture_output=True, text=True, timeout=30, encoding="utf-8",
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
