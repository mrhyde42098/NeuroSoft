#!/usr/bin/env python3
"""One-off: quitar referencias explícitas IN&S del repo (texto, no baremos)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", "dist", "build", "venv", "__pycache__", ".cursor", "mcps"}
EXTS = {".py", ".js", ".jsx", ".md", ".json", ".txt", ".yml", ".yaml", ".sh"}

REPLACEMENTS = [
    ("IN&S+Pro", "NPS+Pro"),
    ("IN&S + Pro", "layout clínico + Pro"),
    ("estándar IN&S+Pro", "estándar NPS+Pro"),
    ("estilo IN&S", "estilo ficha clínica NPS"),
    ("formato IN&S", "formato informe NPS"),
    ("Estándar IN&S", "Estándar informes NPS"),
    ("estándar IN&S", "estándar informes NPS"),
    ("visual IN&S", "layout clínico"),
    ("ficha IN&S", "ficha clínica NPS"),
    ("Línea funcional IN&S", "Línea funcional del informe"),
    ("cuadernillo IN&S", "cuadernillo licenciado"),
    ("protocolos IN&S", "protocolos WISC/WAIS"),
    ("PDF IN&S", "PDF de protocolo"),
    ("Material IN&S", "Material de capacitación"),
    ("material IN&S", "material de capacitación"),
    ("sin material IN&S", "sin material con copyright de terceros"),
    ("Sanitización IN&S", "Sanitización de referencias comerciales"),
    ("sanitización IN&S", "sanitización de referencias comerciales"),
    ('referencias "IN&S"', "referencias comerciales explícitas"),
    ("IN&S en protocolos", "marcas comerciales en protocolos"),
    ("IN&S en nombres", "marcas comerciales en nombres"),
    ("IN&S en código", "marcas comerciales en código"),
    ("desde protocolos IN&S", "desde protocolos JSON"),
    ("Anatomía IN&S", "Anatomía del informe de referencia"),
    ("Híbrido **IN&S", "Híbrido **layout clínico"),
    ("del formato IN&S", "del formato informe NPS"),
    ("# Material interno IN&S", "# Material interno de capacitación"),
    ("VERIFICACION_INS_PDF", "VERIFICACION_PROTOCOLO_PDF"),
    ("verify_ins_vs_json", "verify_protocolo_vs_json"),
    ("extract_ins_pdfs", "extract_protocol_pdfs"),
    ("IN&S_WISC_guia.pdf", "guia_informe_wisc.pdf"),
    ("Compare IN&S PDF", "Compare protocol PDF"),
    ("PDF IN&S vs", "PDF protocolo vs"),
    ("manual IN&S", "manual de protocolo"),
    ("IN&S 2024", "protocolo 2024"),
    ("IN&S", ""),
]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def sanitize_manifest() -> None:
    manifest = ROOT / "neurosoft-backend/data/stimuli_assets/stimuli_manifest.json"
    if not manifest.is_file():
        return
    text = manifest.read_text(encoding="utf-8")
    for old, new in [
        ("WAIS III IN&S", "WAIS III"),
        ("WISC IV IN&S", "WISC IV"),
        (" IN&S", ""),
        ("IN&S", ""),
    ]:
        text = text.replace(old, new)
    manifest.write_text(text, encoding="utf-8")


def main() -> None:
    sanitize_manifest()
    changed: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix.lower() not in EXTS and path.name != ".gitignore":
            continue
        if path.name == "sanitize_ins_refs.py":
            continue
        try:
            orig = path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if "IN&S" not in orig:
            continue
        new = orig
        for old, new_val in REPLACEMENTS:
            new = new.replace(old, new_val)
        if new != orig:
            path.write_text(new, encoding="utf-8")
            changed.append(str(path.relative_to(ROOT)))
    print(f"Updated {len(changed)} files")
    remaining = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or should_skip(path):
            continue
        if path.suffix.lower() not in EXTS:
            continue
        try:
            if "IN&S" in path.read_text(encoding="utf-8"):
                remaining.append(str(path.relative_to(ROOT)))
        except (OSError, UnicodeDecodeError):
            pass
    print(f"Remaining IN&S: {len(remaining)}")
    for r in remaining[:25]:
        print(" ", r)


if __name__ == "__main__":
    main()
