#!/usr/bin/env python3
"""
Carga stimuli_manifest.json en SQLite (tabla estimulos).

Uso (desde neurosoft-backend con venv activo):
  python ../docs/scripts/seed_estimulos_from_manifest.py
  python ../docs/scripts/seed_estimulos_from_manifest.py --db path/to/neurosoft.db
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = ROOT / "neurosoft-backend" / "data" / "stimuli_assets" / "stimuli_manifest.json"
ASSETS = MANIFEST.parent


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, default=MANIFEST)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if not args.manifest.is_file():
        print(f"No existe manifest: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(args.manifest.read_text(encoding="utf-8"))
    entries = data.get("entries", [])
    if not entries:
        print("Manifest vacío — nada que sembrar.")
        return

    sys.path.insert(0, str(ROOT / "neurosoft-backend"))
    from app.infrastructure.database.engine import SessionLocal
    from app.infrastructure.database.orm_models import EstimuloORM

    db = SessionLocal()
    created = 0
    try:
        for i, e in enumerate(entries):
            rel = e.get("file")
            if not rel:
                continue
            img_path = ASSETS / rel
            if not img_path.is_file():
                print(f"  omitido (sin archivo): {rel}")
                continue
            b64 = base64.b64encode(img_path.read_bytes()).decode("ascii")
            mime = "image/png" if rel.lower().endswith(".png") else "image/webp"
            data_url = f"data:{mime};base64,{b64}"
            test_id = e["test_id"]
            item_id = e.get("item_id")
            existing = (
                db.query(EstimuloORM)
                .filter_by(test_id=test_id, item_id=item_id, activo=True)
                .first()
            )
            if args.dry_run:
                created += 1
                continue
            if existing:
                existing.contenido_base64 = data_url
                existing.nombre = e.get("nombre", existing.nombre)
                existing.orden = i
            else:
                db.add(
                    EstimuloORM(
                        id=str(uuid.uuid4()),
                        test_id=test_id,
                        item_id=item_id,
                        nombre=e.get("nombre", rel),
                        tipo="imagen",
                        mime_type=mime,
                        contenido_base64=data_url,
                        descripcion=e.get("source_pdf"),
                        orden=i,
                        activo=True,
                    )
                )
                created += 1
        if not args.dry_run:
            db.commit()
    finally:
        db.close()
    print(f"Sembrados/actualizados: {created}")


if __name__ == "__main__":
    main()
