#!/usr/bin/env python3
"""
docs/scripts/split_baremos_poblacion.py
=========================================
Genera shards de BD_NEURO_MAESTRA.json por población para cold-start con menos RAM.

Salida (junto al JSON maestro):
    data/baremos_shards/
        _meta.json
        manifest.json
        infantil.json
        adulto_joven.json
        adulto_mayor.json

Uso:
    python docs/scripts/split_baremos_poblacion.py
    python docs/scripts/split_baremos_poblacion.py --input neurosoft-backend/data/BD_NEURO_MAESTRA.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def split_baremos(input_path: Path, output_dir: Path | None = None) -> Path:
    raw_bytes = input_path.read_bytes()
    data = json.loads(raw_bytes.decode("utf-8"))
    checksum = hashlib.sha256(raw_bytes).hexdigest()

    out = output_dir or (input_path.parent / "baremos_shards")
    out.mkdir(parents=True, exist_ok=True)

    meta = data.get("_meta", {})
    (out / "_meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    baterias = data.get("baterias", {})
    manifest: dict = {
        "source": input_path.name,
        "checksum_master": checksum,
        "version": meta.get("version") or meta.get("revision") or input_path.stem,
        "poblaciones": {},
    }

    ajustes = {}
    for poblacion, tests in baterias.items():
        shard_tests: dict = {}
        test_ids: list[str] = []
        for test_id, test_data in tests.items():
            if test_id == "_ajustes_escolaridad":
                ajustes = test_data
                continue
            shard_tests[test_id] = test_data
            test_ids.append(test_id)

        shard_path = out / f"{poblacion}.json"
        shard_path.write_text(
            json.dumps(shard_tests, ensure_ascii=False, separators=(",", ":")),
            encoding="utf-8",
        )
        manifest["poblaciones"][poblacion] = {
            "file": shard_path.name,
            "test_ids": sorted(test_ids),
            "n_tests": len(test_ids),
        }

    if ajustes:
        manifest["_ajustes_escolaridad"] = ajustes

    (out / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"OK Shards en {out} ({len(manifest['poblaciones'])} poblaciones)")
    for pop, info in manifest["poblaciones"].items():
        print(f"   - {pop}: {info['n_tests']} pruebas -> {info['file']}")
    return out


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    default_input = root / "neurosoft-backend" / "data" / "BD_NEURO_MAESTRA.json"
    parser = argparse.ArgumentParser(description="Split baremos JSON por población")
    parser.add_argument("--input", type=Path, default=default_input)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    if not args.input.exists():
        raise SystemExit(f"No existe: {args.input}")
    split_baremos(args.input, args.output)


if __name__ == "__main__":
    main()
