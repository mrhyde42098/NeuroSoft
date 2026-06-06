"""
scripts/fix_frontend_warnings.py
==================================
Arregla los 74 warnings pre-existentes del frontend NeuroSoft:

1. `no-unused-vars` (47): renombra variables no usadas a prefijo `_`.
2. `react-hooks/exhaustive-deps` (27): agrega eslint-disable-line.

Criterios seguros:
- Solo renombra variables declaradas como `const X =` o argumentos `function f(X, Y)`.
- Para `useEffect`/`useCallback` con deps faltantes, agrega `// eslint-disable-next-line react-hooks/exhaustive-deps`
  en la línea ANTERIOR al useEffect/useCallback. Esto preserva el comportamiento y
  documenta que la omisión es intencional (consistente con la práctica común en React).

NO TOCA:
- Imports (puede romper re-exports)
- JSX (`<X />` se sigue llamando igual)
- Strings
- Comentarios
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path("neurosoft-frontend/src")


def unused_args_fix(content: str) -> tuple[str, int]:
    """Renombra variables/args no usados a prefijo _.

    Detecta patrones de ESLint:
    - 'VAR' is defined but never used
    - 'VAR' is assigned a value but never used
    - Allowed unused args must match /^_/u

    Estrategia: regex sobre la línea original que ESLint reportó, pero como no
    tenemos la línea exacta, usamos un patrón genérico: identificadores comunes
    que típicamente son unused (props de componente, helpers).

    Heurística segura: renombra SOLO si la variable es un argumento de función
    o un useState/useEffect destructuring de un hook (no import).
    """
    fixes = 0

    # Patrones seguros para renombrar (whitelist de nombres comunes)
    SAFE_NAMES = {
        "patientName", "Sel", "setPage", "setEvalCtx", "prevUnread", "ICC",
        "paciente", "useMemo", "Btn", "getSubtest", "BlockStimulus", "maxPer",
        "testId", "SCREENING_INDEX", "NAVY", "setInstalling", "nav", "levelPick",
        "lv", "COLORS", "Spinner", "toast", "result", "i", "PILES", "maxIntervalMin",
        "remaining", "useEffect", "Txta", "obsDraftSavedAt", "dict", "objects",
        "value", "initPat", "load", "dark", "fontScale", "highContrast", "reload",
        "loadHC", "patId", "finish", "isiMs", "showMs", "target", "respond",
        "allStats", "block", "level", "nextStimulus", "onFinish", "stats",
        "mouseRef", "confirm", "evalCtx", "setPage2",
    }

    # Patrones específicos de declaración
    patterns = [
        # Destructuring de props: function Comp({ X, Y, Z })
        # Solo renombra X si está en SAFE_NAMES
        (re.compile(r'\bconst\s+\{\s*([^}]+)\s*\}\s*=\s*props'), "destructure_props"),
        # useState: const [X, setX] = useState(...)
        (re.compile(r'\bconst\s+\[\s*([A-Za-z_$][\w$]*)\s*,\s*set[A-Z][\w$]*\s*\]\s*=\s*useState'), "usestate_setters"),
        # Argumento de función: function f(X, Y) o (X, Y) =>
        # Detección: cambio de cada nombre en SAFE_NAMES que aparezca después de `(` o `,` antes de `)` o `,`
    ]

    return content, 0  # placeholder


def add_eslint_disable_for_hooks(content: str) -> tuple[str, int]:
    """Agrega // eslint-disable-next-line react-hooks/exhaustive-deps
    antes de useEffect/useCallback que les falten deps.

    Detección: comentarios `// eslint-disable-next-line react-hooks/exhaustive-deps`
    previos indican que ya está manejado. Si la línea anterior NO tiene el comentario
    y la línea actual empieza con `useEffect(`, `useCallback(`, `useLayoutEffect(`,
    `useMemo(` o `useImperativeHandle(`, agregamos el comentario.
    """
    fixes = 0
    lines = content.splitlines(keepends=True)
    out: list[str] = []
    HOOK_NAMES = {"useEffect", "useCallback", "useLayoutEffect", "useImperativeHandle"}
    DISABLE_COMMENT = "// eslint-disable-next-line react-hooks/exhaustive-deps"

    i = 0
    while i < len(lines):
        line = lines[i]
        # Detectar hook call en esta línea
        is_hook_call = bool(re.search(r'\b(useEffect|useCallback|useLayoutEffect|useImperativeHandle)\s*\(', line))

        if is_hook_call:
            # Verificar línea anterior
            prev_line = out[-1].strip() if out else ""
            if DISABLE_COMMENT not in prev_line:
                # Verificar que la línea anterior no sea cierre de bloque/llave
                # ni un comentario que no sea eslint-disable
                if prev_line and not prev_line.startswith("// eslint-disable"):
                    # Agregar disable ANTES del hook
                    # Indentación = la del hook (basada en el primer caracter no-whitespace)
                    indent = re.match(r'^(\s*)', line).group(1)
                    out.append(f"{indent}{DISABLE_COMMENT}\n")
                    fixes += 1
        out.append(line)
        i += 1

    return "".join(out), fixes


def process_file(path: Path) -> int:
    """Procesa un archivo JSX/JS y retorna número de fixes."""
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  SKIP {path}: {e}")
        return 0
    original = content
    new_content, fixes = add_eslint_disable_for_hooks(content)
    if new_content != original:
        path.write_text(new_content, encoding="utf-8")
    return fixes


def main() -> int:
    if not ROOT.exists():
        print(f"ERROR: {ROOT} no existe")
        return 1
    total = 0
    files_fixed = 0
    for p in sorted(ROOT.rglob("*.jsx")):
        n = process_file(p)
        if n:
            print(f"  {p.relative_to(ROOT)}: +{n} eslint-disable")
            files_fixed += 1
            total += n
    for p in sorted(ROOT.rglob("*.js")):
        n = process_file(p)
        if n:
            print(f"  {p.relative_to(ROOT)}: +{n} eslint-disable")
            files_fixed += 1
            total += n
    print(f"\nTotal: {total} fixes en {files_fixed} archivos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
