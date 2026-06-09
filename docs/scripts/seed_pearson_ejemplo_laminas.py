#!/usr/bin/env python3
"""
Genera láminas de ejemplo (licencia Pearson autorizada por clínico) y las siembra en estimulos.

Fuentes:
  - AdWAISCC ítems 1-14: mini-dibujos del protocolo WAIS III (pág. cubos).
  - NiWiscMat / NiWiscConD / AdMatr: tarjetas de referencia por número de lámina
    (sustituir por escaneo del cuadernillo cuando esté disponible).

Uso:
  python docs/scripts/seed_pearson_ejemplo_laminas.py
  python docs/scripts/seed_pearson_ejemplo_laminas.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "neurosoft-backend" / "data" / "stimuli_assets" / "pearson_ejemplo"
MANIFEST = ROOT / "neurosoft-backend" / "data" / "stimuli_assets" / "stimuli_manifest.json"
SEED = ROOT / "docs" / "scripts" / "seed_estimulos_from_manifest.py"
PROTO_FE = ROOT / "neurosoft-frontend" / "src" / "data" / "protocols"


def _caps_dir() -> Path:
    return next(p for p in ROOT.iterdir() if p.is_dir() and "Capacit" in p.name)


def _fitz():
    try:
        import fitz  # noqa: PLC0415
        return fitz
    except ImportError:
        print("pip install pymupdf pillow", file=sys.stderr)
        sys.exit(1)


def _pillow():
    try:
        from PIL import Image, ImageDraw, ImageFont  # noqa: PLC0415
        return Image, ImageDraw, ImageFont
    except ImportError:
        print("pip install pillow", file=sys.stderr)
        sys.exit(1)


def _crop_wais_cubos() -> list[dict]:
    """Recorta 14 diseños de cubos desde protocolo WAIS licenciado."""
    fitz = _fitz()
    pdf = _caps_dir() / "drive-download-20260322T041708Z-3-001" / "WAIS III IN&S.pdf"
    doc = fitz.open(pdf)
    page = doc[8]  # p9 Cubos
    zoom = 4.0
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, alpha=False)
    img_path = OUT / "_tmp_wais_cubos.png"
    OUT.mkdir(parents=True, exist_ok=True)
    pix.save(str(img_path))
    doc.close()

    Image, _, _ = _pillow()
    im = Image.open(img_path).convert("RGB")
    w, h = im.size
    # Columna "Dibujo" del protocolo WAIS (mini patrones de cubos licenciados)
    x0, x1 = int(w * 0.055), int(w * 0.19)
    y0 = int(h * 0.205)
    row_h = int((h * 0.76) / 14)
    entries: list[dict] = []
    for i in range(14):
        y1 = y0 + row_h * (i + 1) - 4
        crop = im.crop((x0, y0 + row_h * i + 2, x1, y1))
        rel = f"pearson_ejemplo/AdWAISCC/item_{i + 1}.png"
        dest = OUT.parent / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        crop.save(dest)
        entries.append({
            "test_id": "AdWAISCC",
            "item_id": str(i + 1),
            "file": rel,
            "page": 9,
            "source_pdf": pdf.name,
            "nombre": f"AdWAISCC diseño cubos {i + 1}",
        })
    img_path.unlink(missing_ok=True)
    return entries


def _draw_matrix_card(n: int, test_id: str, label: str) -> Path:
    Image, ImageDraw, ImageFont = _pillow()
    W, H = 520, 400
    im = Image.new("RGB", (W, H), "#fafafa")
    dr = ImageDraw.Draw(im)
    dr.rectangle((8, 8, W - 8, H - 8), outline="#0d9488", width=2)
    dr.text((20, 16), f"{label} — lámina {n}", fill="#134e4a")
    dr.text((20, 40), "Referencia cuadernillo licenciado (ejemplo integración)", fill="#64748b")
    # Patrón geométrico simple (no copia Pearson)
    cx, cy = W // 2, H // 2 + 20
    r = 28
    for k in range(6):
        ang = (k / 6) * 2 * math.pi + n * 0.3
        x = cx + int(math.cos(ang) * (60 + (n % 5) * 8))
        y = cy + int(math.sin(ang) * (40 + (n % 3) * 10))
        dr.ellipse((x - r, y - r, x + r, y + r), fill="#99f6e4", outline="#0f766e")
    dr.rectangle((cx - 50, cy - 35, cx + 50, cy + 35), outline="#334155", width=2)
    dr.text((cx - 8, cy - 8), "?", fill="#334155")
    rel = f"pearson_ejemplo/{test_id}/item_{n}.png"
    path = OUT.parent / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return rel


def _draw_concept_card(n: int) -> str:
    Image, ImageDraw, _ = _pillow()
    W, H = 520, 360
    im = Image.new("RGB", (W, H), "#fffbeb")
    dr = ImageDraw.Draw(im)
    dr.rectangle((8, 8, W - 8, H - 8), outline="#b45309", width=2)
    dr.text((20, 16), f"Conceptos con dibujos — lámina {n}", fill="#78350f")
    dr.text((20, 42), "Agrupe por categoría (ejemplo — sustituya por escaneo)", fill="#92400e")
    colors = ["#fca5a5", "#93c5fd", "#86efac", "#fcd34d"]
    for row in range(3):
        for col in range(4):
            idx = row * 4 + col
            x = 40 + col * 110
            y = 90 + row * 80
            dr.rounded_rectangle(
                (x, y, x + 90, y + 65),
                radius=8,
                fill=colors[(idx + n) % 4],
                outline="#57534e",
            )
    rel = f"pearson_ejemplo/NiWiscConD/item_{n}.png"
    path = OUT.parent / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return rel


def _proto_items(test_id: str, proto_name: str) -> list[dict]:
    data = json.loads((PROTO_FE / proto_name).read_text(encoding="utf-8-sig"))
    sub = data["subtests"].get(test_id) or {}
    return sub.get("items") or []


def _draw_label_card(
    test_id: str,
    n: int,
    title: str,
    subtitle: str,
    *,
    bg: str = "#f0fdfa",
    border: str = "#0d9488",
) -> str:
    Image, ImageDraw, _ = _pillow()
    W, H = 480, 320
    im = Image.new("RGB", (W, H), bg)
    dr = ImageDraw.Draw(im)
    dr.rectangle((8, 8, W - 8, H - 8), outline=border, width=2)
    dr.text((24, 20), f"{title}", fill="#134e4a")
    dr.text((24, 52), f"Item {n}", fill="#64748b")
    dr.text((24, 90), subtitle[:60], fill="#0f766e")
    dr.text((24, H - 36), "Cuadernillo licenciado (ejemplo)", fill="#94a3b8")
    rel = f"pearson_ejemplo/{test_id}/item_{n}.png"
    path = OUT.parent / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    im.save(path)
    return rel


def _build_entries() -> list[dict]:
    entries: list[dict] = []
    try:
        entries.extend(_crop_wais_cubos())
    except Exception as exc:
        print(f"WARN cubos WAIS: {exc}", file=sys.stderr)

    for n in range(1, 36):
        rel = _draw_matrix_card(n, "NiWiscMat", "Matrices WISC-IV")
        entries.append({
            "test_id": "NiWiscMat",
            "item_id": str(n),
            "file": rel,
            "source_pdf": "ejemplo_integracion",
            "nombre": f"NiWiscMat lámina {n}",
        })
    for n in range(1, 27):
        rel = _draw_matrix_card(n, "AdMatr", "Matrices WAIS-III")
        entries.append({
            "test_id": "AdMatr",
            "item_id": str(n),
            "file": rel,
            "source_pdf": "ejemplo_integracion",
            "nombre": f"AdMatr lámina {n}",
        })
    for n in range(1, 29):
        rel = _draw_concept_card(n)
        entries.append({
            "test_id": "NiWiscConD",
            "item_id": str(n),
            "file": rel,
            "source_pdf": "ejemplo_integracion",
            "nombre": f"NiWiscConD lámina {n}",
        })

    for it in _proto_items("NiWiscVoc", "wisc_iv_protocolo.json")[:4]:
        n = int(it["num"])
        word = it.get("palabra", f"Item {n}")
        rel = _draw_label_card("NiWiscVoc", n, "Vocabulario WISC-IV", word, bg="#eff6ff", border="#2563eb")
        entries.append({
            "test_id": "NiWiscVoc",
            "item_id": str(n),
            "file": rel,
            "source_pdf": "wisc_iv_protocolo.json",
            "nombre": f"NiWiscVoc {word}",
        })

    for it in _proto_items("NiWisFigInc", "wisc_iv_protocolo.json"):
        n = int(it["num"])
        obj = it.get("imagen", f"Item {n}")
        rel = _draw_label_card("NiWisFigInc", n, "Figuras incompletas WISC-IV", obj)
        entries.append({
            "test_id": "NiWisFigInc",
            "item_id": str(n),
            "file": rel,
            "source_pdf": "wisc_iv_protocolo.json",
            "nombre": f"NiWisFigInc {obj}",
        })

    for it in _proto_items("AdWAISFI", "wais_iii_protocolo.json"):
        n = int(it["num"])
        obj = it.get("imagen", f"Item {n}")
        rel = _draw_label_card("AdWAISFI", n, "Figuras incompletas WAIS-III", obj, bg="#fdf4ff", border="#9333ea")
        entries.append({
            "test_id": "AdWAISFI",
            "item_id": str(n),
            "file": rel,
            "source_pdf": "wais_iii_protocolo.json",
            "nombre": f"AdWAISFI {obj}",
        })

    return entries


def _merge_manifest(entries: list[dict], dry_run: bool) -> None:
    if dry_run:
        print(f"[dry-run] {len(entries)} entradas")
        return
    assets = MANIFEST.parent
    base = {"version": 1, "entries": []}
    if MANIFEST.is_file():
        base = json.loads(MANIFEST.read_text(encoding="utf-8"))
    prefixes = ("pearson_ejemplo/", "pearson_visual/")
    kept = []
    for e in base.get("entries", []):
        rel = e.get("file") or ""
        if rel.startswith(prefixes):
            continue
        if rel and (assets / rel).is_file():
            kept.append(e)
    base["entries"] = kept + entries
    base["pearson_ejemplo"] = True
    MANIFEST.write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest: {len(kept)} legacy + {len(entries)} pearson -> {MANIFEST}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    entries = _build_entries()
    _merge_manifest(entries, args.dry_run)
    if args.dry_run:
        return 0
    r = subprocess.run([sys.executable, str(SEED)], cwd=str(ROOT), check=False)
    return r.returncode


if __name__ == "__main__":
    raise SystemExit(main())
