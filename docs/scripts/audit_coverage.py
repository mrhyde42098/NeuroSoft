#!/usr/bin/env python3
"""Inventario de cobertura para AUDIT_FULL — solo lectura."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {
    "node_modules", ".git", "dist", "build", "__pycache__", ".pytest_cache",
    ".venv", "venv", ".cursor", "agent-transcripts", ".mypy_cache",
}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".json", ".md", ".spec"}


def should_skip(p: Path) -> bool:
    return any(part in SKIP_DIRS for part in p.parts)


def scan(base: Path, exts: set[str]) -> list[dict]:
    rows = []
    for f in base.rglob("*"):
        if not f.is_file() or should_skip(f):
            continue
        if f.suffix.lower() not in exts:
            continue
        try:
            lines = len(f.read_text(encoding="utf-8", errors="replace").splitlines())
        except OSError:
            lines = 0
        rows.append({"path": str(f.relative_to(ROOT)).replace("\\", "/"), "lines": lines})
    return rows


def main() -> None:
    domains = {
        "backend_app": ROOT / "neurosoft-backend" / "app",
        "backend_tests": ROOT / "neurosoft-backend" / "tests",
        "frontend_src": ROOT / "neurosoft-frontend" / "src",
        "docs": ROOT / "docs",
        "protocolos": ROOT / "Capacitaciones Clínicas" / "protocolos",
        "frontend_protocols": ROOT / "neurosoft-frontend" / "src" / "data" / "protocols",
    }
    out = {"generated": "2026-06-06", "domains": {}}
    total_files = 0
    total_lines = 0
    for name, path in domains.items():
        if not path.is_dir():
            out["domains"][name] = {"files": 0, "lines": 0, "missing": True}
            continue
        exts = CODE_EXT if name != "docs" else {".md", ".py", ".json"}
        rows = scan(path, exts)
        fl = sum(r["lines"] for r in rows)
        total_files += len(rows)
        total_lines += fl
        out["domains"][name] = {
            "files": len(rows),
            "lines": fl,
            "top_by_lines": sorted(rows, key=lambda x: -x["lines"])[:15],
        }
    out["totals"] = {"files": total_files, "lines": total_lines}
    dest = ROOT / "docs" / "historico" / "audits" / "audit_coverage_2026-06-06.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {dest} — {total_files} files, {total_lines} lines")


if __name__ == "__main__":
    main()
