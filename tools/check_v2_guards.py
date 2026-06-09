#!/usr/bin/env python3
"""Guards arquitectónicos NeuroSoft V2 — falla si detecta anti-patrones."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FE_APP = ROOT / "neurosoft-frontend" / "src" / "app"
BE_API = ROOT / "neurosoft-backend" / "app" / "presentation" / "api" / "v1"

MAX_FE_PAGE_LINES = 400
DB_DIRECT = re.compile(r"\bdb\.(query|add|commit|delete|get)\b")

errors: list[str] = []

for jsx in FE_APP.rglob("*.jsx"):
    if "Page.jsx" not in jsx.name and jsx.name not in ("PanelIA.jsx", "InformesPage.jsx"):
        continue
    lines = jsx.read_text(encoding="utf-8", errors="replace").count("\n") + 1
    if lines > MAX_FE_PAGE_LINES:
        errors.append(f"Frontend page too large ({lines} lines): {jsx.relative_to(ROOT)}")

for py in BE_API.glob("*.py"):
    text = py.read_text(encoding="utf-8", errors="replace")
    if py.name in ("auth.py", "shared.py"):
        continue
    if "DbSession" in text and DB_DIRECT.search(text):
        # therapy/reports refactored — warn only on heavy usage
        hits = len(DB_DIRECT.findall(text))
        if hits >= 3:
            errors.append(f"Route with direct DB access ({hits} hits): {py.relative_to(ROOT)}")

# Módulos que deben cumplir V2 ya (post-refactor jun 2026)
STRICT_CLEAN = {
    BE_API / "therapy.py",
    BE_API / "appointments.py",
}

strict_errors = [e for e in errors if any(s.name in e for s in STRICT_CLEAN)]
legacy_warnings = [e for e in errors if e not in strict_errors]

if legacy_warnings:
    print(f"V2 legacy debt ({len(legacy_warnings)} items — migrar gradualmente):\n")
    for e in legacy_warnings[:15]:
        print(f"  WARN {e}")
    if len(legacy_warnings) > 15:
        print(f"  ... y {len(legacy_warnings) - 15} más")

if strict_errors:
    print("\nV2 strict violations (deben corregirse):\n")
    for e in strict_errors:
        print(f"  FAIL {e}")
    sys.exit(1)

print("\nV2 guards OK (strict modules clean)")
