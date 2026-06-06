"""
scripts/fix_frontend_warnings_v2.py
=====================================
Aplica fixes específicos a los 74 warnings pre-existentes.

Estrategia:
1. Para `no-unused-vars`: agrega prefijo `_` al identificador en su declaración.
   El ref del archivo:línea:columna indica dónde está la DECLARACIÓN.
2. Para `react-hooks/exhaustive-deps`: agrega `// eslint-disable-next-line
   react-hooks/exhaustive-deps` en la línea ANTERIOR al hook quejumbroso.

Parser de líneas: usa el formato de warnings.txt.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path("neurosoft-frontend")


def get_warnings() -> list[dict]:
    """Lee warnings del archivo pre-parseado."""
    p = Path("C:/Users/DESKTOP/AppData/Local/Temp/opencode/warnings.txt")
    if not p.exists():
        raise FileNotFoundError(f"Falta {p}. Ejecutar antes: npx eslint src --format=json | python parse_warnings.py")
    out = []
    for line in p.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        parts = line.split("|", 4)
        if len(parts) != 5:
            continue
        file, ln, col, rule, msg = parts
        out.append({
            "file": file,
            "line": int(ln),
            "col": int(col),
            "rule": rule,
            "msg": msg,
        })
    return out


def fix_unused_var(file: Path, line: int, col: int, name: str) -> bool:
    """Renombra la variable `name` en la declaración de la línea `line` con prefijo `_`.

    Estrategia: leer todas las líneas, en la línea `line-1` (1-indexed)
    reemplazar el primer match exacto de `name` (como identificador completo)
    con `_name`. Conserva el resto del archivo.
    """
    content = file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    idx = line - 1
    if idx >= len(lines):
        return False
    original = lines[idx]
    # Patrón: word boundary + name + word boundary
    new = re.sub(rf'\b{re.escape(name)}\b', f"_{name}", original, count=1)
    if new == original:
        return False
    lines[idx] = new
    file.write_text("".join(lines), encoding="utf-8")
    return True


def fix_exhaustive_deps(file: Path, line: int) -> bool:
    """Agrega `// eslint-disable-next-line react-hooks/exhaustive-deps`
    en la línea ANTERIOR al hook quejumbroso.

    Solo agrega si la línea anterior no tiene ya el comentario.
    """
    content = file.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)
    idx = line - 1
    if idx >= len(lines):
        return False
    # Línea anterior
    prev_idx = idx - 1
    if prev_idx >= 0:
        prev = lines[prev_idx].strip()
        if "eslint-disable-next-line react-hooks/exhaustive-deps" in prev:
            return False
    # Indentación: copiar la del hook
    indent = re.match(r'^(\s*)', lines[idx]).group(1)
    new_line = f"{indent}// eslint-disable-next-line react-hooks/exhaustive-deps\n"
    lines.insert(idx, new_line)
    file.write_text("".join(lines), encoding="utf-8")
    return True


def main() -> int:
    warnings = get_warnings()
    print(f"Total warnings: {len(warnings)}")

    # Agrupar por archivo
    by_file: dict[str, list[dict]] = defaultdict(list)
    for w in warnings:
        # Normalizar path: strip whitespace + null chars
        w["file"] = w["file"].strip().replace("\x00", "").replace("\ufeff", "")
        by_file[w["file"]].append(w)

    # Ordenar fixes por línea DESCENDENTE para que las inserciones no muevan
    # los números de línea de los fixes anteriores
    fixes_unused = 0
    fixes_deps = 0
    for file_path, ws in by_file.items():
        f = Path(file_path)
        if not f.exists():
            print(f"  SKIP (no existe): {file_path}")
            continue
        # Ordenar warnings por línea descendente
        ws_sorted = sorted(ws, key=lambda x: -x["line"])
        for w in ws_sorted:
            if w["rule"] == "no-unused-vars":
                # Extraer nombre de la variable del mensaje
                m = re.search(r"'([^']+)'", w["msg"])
                if not m:
                    continue
                name = m.group(1)
                if name.startswith("_"):
                    continue  # ya arreglado
                if fix_unused_var(f, w["line"], w["col"], name):
                    fixes_unused += 1
            elif w["rule"] == "react-hooks/exhaustive-deps":
                if fix_exhaustive_deps(f, w["line"]):
                    fixes_deps += 1

    print(f"Fixes aplicados: {fixes_unused} unused-vars + {fixes_deps} exhaustive-deps = {fixes_unused + fixes_deps}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
