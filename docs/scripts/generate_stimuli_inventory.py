#!/usr/bin/env python3
"""Genera docs/stimuli/STIMULI_INVENTORY.md desde protocolos + clinical.js REACTIVOS."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PROTO_DIRS = [
    ROOT / "Capacitaciones Clínicas" / "protocolos",
    ROOT / "neurosoft-frontend" / "src" / "data" / "protocols",
]
CLINICAL_JS = ROOT / "neurosoft-frontend" / "src" / "data" / "clinical.js"
OUT = ROOT / "docs" / "stimuli" / "STIMULI_INVENTORY.md"
PDF_HINT = ROOT / "Capacitaciones Clínicas" / "drive-download-20260322T041708Z-3-001"


def load_reactivos() -> dict[str, int]:
    text = CLINICAL_JS.read_text(encoding="utf-8")
    counts: dict[str, int] = {}
    for m in re.finditer(
        r"^\s{2}([A-Za-z0-9_+ ]+):\{type:\"([^\"]+)\"",
        text,
        re.MULTILINE,
    ):
        tid = m.group(1).strip()
        if "+" in tid:
            tid = tid.split("+")[0].strip()
        block = text[m.start() : m.start() + 8000]
        items = len(re.findall(r"\{n:\d+", block))
        counts[tid] = items
    return counts


def load_protocol_tests() -> dict[str, set[str]]:
    tests: dict[str, set[str]] = {}
    for d in PROTO_DIRS:
        if not d.is_dir():
            continue
        for fp in d.glob("*.json"):
            try:
                data = json.loads(fp.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, OSError):
                continue
            for block in data.get("bloques", data.get("tests", [])) or []:
                if isinstance(block, dict):
                    for t in block.get("pruebas", block.get("tests", [])) or []:
                        if isinstance(t, dict) and t.get("test_id"):
                            tests.setdefault(fp.stem, set()).add(t["test_id"])
                        elif isinstance(t, str):
                            tests.setdefault(fp.stem, set()).add(t)
    return tests


def main() -> None:
    reactivos = load_reactivos()
    protos = load_protocol_tests()
    wisc_wais = sorted(
        k for k in reactivos
        if k.startswith(("NiWisc", "NiWis", "AdW", "AdSem", "AdMat", "AdDDir", "AdBus", "AdSD"))
    )
    lines = [
        "# Inventario de estímulos — NeuroSoft",
        "",
        "**Generado:** 2026-06-06 (`generate_stimuli_inventory.py`)",
        "",
        "## Fuentes",
        "",
        f"- PDFs locales: `{PDF_HINT}` " + ("(presente)" if PDF_HINT.is_dir() else "(no encontrado — copiar antes de extraer)"),
        "- REACTIVOS: `neurosoft-frontend/src/data/clinical.js`",
        "- Protocolos JSON: `Capacitaciones Clínicas/protocolos/` + espejo frontend",
        "- BD SQLite tabla `estimulos` vía API `/api/v1/estimulos/`",
        "",
        "## WISC-IV / WAIS-III (prioridad extracción PDF)",
        "",
        "| test_id | ítems REACTIVOS | estado | notas |",
        "|---------|----------------:|--------|-------|",
    ]
    for tid in wisc_wais:
        n = reactivos.get(tid, 0)
        estado = "SVG cubos/FCRO" if tid in ("NiWiscDC", "AdWAISCC", "NiFCROCop", "AdFCRO_Rey") else "pendiente PDF"
        lic = "Pearson" if tid.startswith(("NiWisc", "NiWis", "AdW")) else ""
        lines.append(f"| `{tid}` | {n} | {estado} | {lic} |")

    lines += [
        "",
        "## Validez / peritajes",
        "",
        "| test_id | ítems | estado |",
        "|---------|------:|--------|",
        f"| `TOMM` | {reactivos.get('TOMM', 3)} | requiere 50 estímulos visuales por trial |",
        f"| `REY15` | grid validez | dominio público |",
        "",
        "## Protocolos → test_ids",
        "",
    ]
    for pname, tids in sorted(protos.items()):
        lines.append(f"### {pname}")
        for t in sorted(tids):
            lines.append(f"- `{t}` ({reactivos.get(t.split()[0], '?')} ítems en REACTIVOS)")
        lines.append("")

    lines += [
        "## Leyenda estado",
        "",
        "- **extraído**: en `data/stimuli_assets/` + seed SQLite",
        "- **SVG nativo**: `PatronesCubos.jsx` / `stimuli.jsx`",
        "- **pendiente PDF**: requiere `extract_stimuli_from_pdfs.py`",
        "",
    ]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
