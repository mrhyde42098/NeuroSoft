"""Regresión: reactivos Pearson sincronizados desde protocolos WISC/WAIS."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GENERATED = ROOT / "neurosoft-frontend" / "src" / "data" / "reactivosPearson.generated.js"
SYNC_SCRIPT = ROOT / "docs" / "scripts" / "sync_reactivos_from_protocol.py"


def _extract_pearson_json() -> dict:
 text = GENERATED.read_text(encoding="utf-8")
 start = text.index("export const REACTIVOS_PEARSON = ") + len("export const REACTIVOS_PEARSON = ")
 end = text.rindex(";\n")
 return json.loads(text[start:end])


def test_generated_file_exists():
 assert GENERATED.exists(), "Ejecute: python docs/scripts/sync_reactivos_from_protocol.py"


def test_niwiscsem_par_1_from_protocol():
 data = _extract_pearson_json()
 sem = data["NiWiscSem"]["items"]
 item1 = next(x for x in sem if x["n"] == 1)
 assert item1["pair"] == "Leche — Agua"


def test_item_counts_match_protocol():
 data = _extract_pearson_json()
 assert len(data["NiWiscVoc"]["items"]) == 36
 assert len(data["NiWiscMat"]["items"]) == 35
 assert len(data["NiWiscLN"]["items"]) == 10
 assert data["NiWiscLN"]["type"] == "ln_sequences"
 assert data["NiWiscMat"]["type"] == "visual_cuadernillo"
 assert len(data["AdSemWais"]["items"]) == 19
 ad1 = next(x for x in data["AdSemWais"]["items"] if x["n"] == 1)
 assert ad1["pair"] == "Naranja — Pera"


def test_sync_script_runs():
 r = subprocess.run(
 [sys.executable, str(SYNC_SCRIPT), "--check"],
 cwd=str(ROOT),
 capture_output=True,
 text=True,
 check=False,
 )
 assert r.returncode == 0, r.stderr or r.stdout
