#!/usr/bin/env python3
"""
Extrae imágenes de PDFs de capacitación → WebP + stimuli_manifest.json.

Uso:
  pip install pymupdf pillow
  python docs/scripts/extract_stimuli_from_pdfs.py --pdf-dir "Capacitaciones Clínicas/..."
  python docs/scripts/extract_stimuli_from_pdfs.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PDF = ROOT / "Capacitaciones Clínicas" / "drive-download-20260322T041708Z-3-001"
OUT_DIR = ROOT / "neurosoft-backend" / "data" / "stimuli_assets"
MANIFEST = OUT_DIR / "stimuli_manifest.json"

# Mapeo heurístico nombre PDF → prefijo test_id
PDF_TEST_PREFIX = {
    "WISC": "NiWisc",
    "WAIS": "Ad",
    "wisc": "NiWisc",
    "wais": "Ad",
}


def try_import_fitz():
    try:
        import fitz  # PyMuPDF
        return fitz
    except ImportError:
        print("Instale PyMuPDF: pip install pymupdf pillow", file=sys.stderr)
        sys.exit(1)


def extract_images(pdf_path: Path, fitz, dry_run: bool) -> list[dict]:
    entries: list[dict] = []
    doc = fitz.open(pdf_path)
    stem = pdf_path.stem
    prefix = "NiWisc" if "wisc" in stem.lower() else "Ad" if "wais" in stem.lower() else stem[:8]
    for page_i in range(len(doc)):
        page = doc[page_i]
        imgs = page.get_images(full=True)
        for img_i, img in enumerate(imgs):
            xref = img[0]
            try:
                pix = fitz.Pixmap(doc, xref)
                if pix.n - pix.alpha > 3:
                    pix = fitz.Pixmap(fitz.csRGB, pix)
            except Exception:
                continue
            item_n = img_i + 1
            test_id = f"{prefix}Stim_p{page_i + 1}_{item_n}"
            rel = f"{stem}/p{page_i + 1:03d}_{img_i:02d}.png"
            entry = {
                "test_id": test_id,
                "item_id": str(item_n),
                "file": rel,
                "page": page_i + 1,
                "source_pdf": pdf_path.name,
                "nombre": f"{stem} p{page_i + 1} img {img_i + 1}",
            }
            entries.append(entry)
            if not dry_run:
                out_path = OUT_DIR / rel
                out_path.parent.mkdir(parents=True, exist_ok=True)
                pix.save(str(out_path))
            pix = None
    doc.close()
    return entries


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pdf-dir", type=Path, default=DEFAULT_PDF)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    fitz = try_import_fitz()
    pdf_dir: Path = args.pdf_dir
    if not pdf_dir.is_dir():
        print(f"Directorio PDF no encontrado: {pdf_dir}", file=sys.stderr)
        print("Copie los PDFs o pase --pdf-dir", file=sys.stderr)
        # Manifest vacío para pipeline
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        MANIFEST.write_text(
            json.dumps({"version": 1, "entries": [], "note": "sin PDFs"}, indent=2),
            encoding="utf-8",
        )
        sys.exit(0)

    all_entries: list[dict] = []
    for pdf in sorted(pdf_dir.glob("*.pdf")):
        print(f"Procesando {pdf.name}...")
        all_entries.extend(extract_images(pdf, fitz, args.dry_run))

    manifest = {
        "version": 1,
        "generated_from": str(pdf_dir),
        "entries": all_entries,
    }
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Manifest: {MANIFEST} ({len(all_entries)} entradas)")


if __name__ == "__main__":
    main()
