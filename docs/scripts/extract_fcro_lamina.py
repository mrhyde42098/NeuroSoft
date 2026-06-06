#!/usr/bin/env python3
"""
Extrae la lámina FCRO (Figura Rey-Osterrieth) de un PDF de protocolo.

Uso:
  pip install pymupdf
  python docs/scripts/extract_fcro_lamina.py --pdf "ruta/al/protocolo.pdf"
  python docs/scripts/extract_fcro_lamina.py --pdf "..." --page 12

Salida: neurosoft-frontend/public/assets/fcro/fcro-lamina.png
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "neurosoft-frontend" / "public" / "assets" / "fcro" / "fcro-lamina.png"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", required=True, type=Path)
    parser.add_argument("--page", type=int, default=0, help="1-based; 0 = autodetect")
    parser.add_argument("--zoom", type=float, default=3.0)
    args = parser.parse_args()
    if not args.pdf.is_file():
        print(f"No existe: {args.pdf}", file=sys.stderr)
        return 1
    try:
        import fitz
    except ImportError:
        print("pip install pymupdf", file=sys.stderr)
        return 1

    doc = fitz.open(args.pdf)
    page_i = args.page - 1 if args.page > 0 else None
    if page_i is None:
        best, best_score = 0, -1
        keys = ("figura compleja", "rey-osterrieth", "rey osterrieth", "fcro", "complex figure")
        for i in range(len(doc)):
            t = doc[i].get_text().lower()
            score = sum(3 for k in keys if k in t)
            score += len(doc[i].get_drawings()) * 0.05
            if score > best_score:
                best_score, best = score, i
        page_i = best
        print(f"Página elegida: {page_i + 1} (score={best_score:.1f})")

    page = doc[page_i]
    mat = fitz.Matrix(args.zoom, args.zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(OUT))
    print(f"Guardado: {OUT} ({pix.width}x{pix.height})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
