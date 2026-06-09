#!/usr/bin/env python3
"""
Renderiza láminas del Cuadernillo de Estímulos WISC/WAIS → PNG + manifest para seed.

Los PDFs de protocolo de puntuación (WISC IV .pdf / WAIS III .pdf) NO contienen las
láminas de Matrices/Conceptos — solo hojas de registro. Este script espera el
**Cuadernillo de Estímulos** escaneado o el PDF licenciado del kit Pearson.

Uso:
  pip install pymupdf
  python docs/scripts/map_pearson_visual_stimuli.py --wisc-pdf "ruta/Cuadernillo WISC-IV.pdf"
  python docs/scripts/map_pearson_visual_stimuli.py --wais-pdf "ruta/Cuadernillo WAIS-III.pdf"
  python docs/scripts/map_pearson_visual_stimuli.py --wisc-pdf ... --seed
  python docs/scripts/map_pearson_visual_stimuli.py --dry-run --wisc-pdf ...

Mapeo de páginas: docs/stimuli/wisc_wais_lamina_map.json (ajustar page_start si hay portada).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAP_FILE = ROOT / "docs" / "stimuli" / "wisc_wais_lamina_map.json"
OUT_DIR = ROOT / "neurosoft-backend" / "data" / "stimuli_assets" / "pearson_visual"
MANIFEST = ROOT / "neurosoft-backend" / "data" / "stimuli_assets" / "stimuli_manifest.json"
SEED_SCRIPT = ROOT / "docs" / "scripts" / "seed_estimulos_from_manifest.py"


def _fitz():
    try:
        import fitz  # noqa: PLC0415
        return fitz
    except ImportError:
        print("Instale PyMuPDF: pip install pymupdf", file=sys.stderr)
        sys.exit(1)


def _load_map() -> dict:
    return json.loads(MAP_FILE.read_text(encoding="utf-8"))


def _render_pages(
    pdf_path: Path,
    block_key: str,
    *,
    zoom: float,
    dry_run: bool,
) -> list[dict]:
    fitz = _fitz()
    cfg = _load_map()[block_key]
    doc = fitz.open(pdf_path)
    page = int(cfg.get("page_start", 1)) - 1
    entries: list[dict] = []
    rel_root = f"pearson_visual/{block_key}"

    for sec in cfg.get("sections", []):
        test_id = sec["test_id"]
        count = int(sec["count"])
        item_from = int(sec.get("item_id_from", 1))
        if sec.get("skip_sample_page") and page < len(doc):
            page += 1

        for i in range(count):
            item_id = str(item_from + i)
            if page >= len(doc):
                print(f"WARN: PDF agotado en {test_id} item {item_id}", file=sys.stderr)
                break
            rel = f"{rel_root}/{test_id}/item_{item_id}.png"
            entry = {
                "test_id": test_id,
                "item_id": item_id,
                "file": rel,
                "page": page + 1,
                "source_pdf": pdf_path.name,
                "nombre": f"{test_id} lámina {item_id}",
            }
            entries.append(entry)
            if not dry_run:
                out_path = OUT_DIR.parent / rel
                out_path.parent.mkdir(parents=True, exist_ok=True)
                pix = doc[page].get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
                pix.save(str(out_path))
            page += 1

    doc.close()
    return entries


def _merge_manifest(new_entries: list[dict], dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] {len(new_entries)} entradas pearson_visual")
        return
    existing: dict = {"version": 1, "entries": []}
    if MANIFEST.is_file():
        existing = json.loads(MANIFEST.read_text(encoding="utf-8"))
    kept = [
        e
        for e in existing.get("entries", [])
        if not (e.get("file") or "").startswith("pearson_visual/")
    ]
    merged = kept + new_entries
    existing["entries"] = merged
    existing["pearson_visual_updated"] = str(MAP_FILE.name)
    MANIFEST.write_text(json.dumps(existing, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest actualizado: {len(new_entries)} láminas pearson_visual ({MANIFEST})")


def main() -> int:
    ap = argparse.ArgumentParser(description="Mapea cuadernillo Pearson → estimulos SQLite")
    ap.add_argument("--wisc-pdf", type=Path, help="PDF Cuadernillo de estímulos WISC-IV")
    ap.add_argument("--wais-pdf", type=Path, help="PDF Cuadernillo de estímulos WAIS-III")
    ap.add_argument("--zoom", type=float, default=2.0, help="Factor render página completa")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--seed", action="store_true", help="Ejecutar seed_estimulos_from_manifest.py")
    args = ap.parse_args()

    if not args.wisc_pdf and not args.wais_pdf:
        print("Indique --wisc-pdf y/o --wais-pdf (Cuadernillo de Estímulos, no protocolo de registro).", file=sys.stderr)
        return 1

    all_entries: list[dict] = []
    if args.wisc_pdf:
        if not args.wisc_pdf.is_file():
            print(f"No existe: {args.wisc_pdf}", file=sys.stderr)
            return 1
        print(f"WISC cuadernillo: {args.wisc_pdf.name}")
        all_entries.extend(
            _render_pages(args.wisc_pdf, "wisc_cuadernillo", zoom=args.zoom, dry_run=args.dry_run)
        )
    if args.wais_pdf:
        if not args.wais_pdf.is_file():
            print(f"No existe: {args.wais_pdf}", file=sys.stderr)
            return 1
        print(f"WAIS cuadernillo: {args.wais_pdf.name}")
        all_entries.extend(
            _render_pages(args.wais_pdf, "wais_cuadernillo", zoom=args.zoom, dry_run=args.dry_run)
        )

    _merge_manifest(all_entries, args.dry_run)
    print(f"Total láminas: {len(all_entries)}")

    if args.seed and not args.dry_run:
        r = subprocess.run(
            [sys.executable, str(SEED_SCRIPT)],
            cwd=str(ROOT),
            check=False,
        )
        return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
