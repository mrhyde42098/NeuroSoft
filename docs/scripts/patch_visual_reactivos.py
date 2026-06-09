"""Patch clinical.js — convert Matrices/Conceptos to visual_cuadernillo."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
path = ROOT / "neurosoft-frontend" / "src" / "data" / "clinical.js"
text = path.read_text(encoding="utf-8")

mat_block = (
    '  /* ── MATRICES (WISC-IV) — visual_cuadernillo 0-1 ── */\n'
    '  NiWiscMat:{type:"visual_cuadernillo",label:"Matrices",scoring:[0,1],opciones:5,'
    'manualRef:"Libreta de estímulos WISC-IV",requires_license:true,'
    'license_publisher:"Pearson / Editorial Manual Moderno",'
    'items:_buildVisualItems("NiWiscMat",35,'
    '"Mira el diseño incompleto y señale cuál de las 5 opciones lo completa (lámina {n}).")},'
)

cond_block = (
    '  /* ── CONCEPTOS CON DIBUJOS — visual_cuadernillo 0-1 ── */\n'
    '  NiWiscConD:{type:"visual_cuadernillo",label:"Conceptos con Dibujos",scoring:[0,1],opciones:0,'
    'manualRef:"Libreta de estímulos WISC-IV",requires_license:true,'
    'license_publisher:"Pearson / Editorial Manual Moderno",'
    'items:_buildVisualItems("NiWiscConD",28,'
    '"Señale un dibujo de cada fila que va junto o forma un grupo con los de arriba (lámina {n}).")},'
)

adm_block = (
    '  AdMatr:{type:"visual_cuadernillo",label:"Matrices WAIS-III",scoring:[0,1],opciones:5,'
    'manualRef:"Cuadernillo de estímulos WAIS-III",requires_license:true,'
    'license_publisher:"Pearson / Editorial Manual Moderno",'
    'items:_buildVisualItems("AdMatr",26,'
    '"Observe la figura incompleta y señale cuál de las 5 opciones la completa (lámina {n}).")},'
)

text, n1 = re.subn(
    r"  /\* ── MATRICES \(WISC-IV\).*?  \]\},\n  /\* ── CONCEPTOS",
    mat_block + "\n  /* ── CONCEPTOS",
    text,
    count=1,
    flags=re.S,
)
text, n2 = re.subn(
    r"  /\* ── CONCEPTOS CON DIBUJOS.*?\]\},\n  /\* ── INFORMACIÓN",
    cond_block + "\n  /* ── INFORMACIÓN",
    text,
    count=1,
    flags=re.S,
)
text, n3 = re.subn(
    r'  AdMatr:\{type:"scored_items".*?  \]\},\n  AdWAISA:',
    adm_block + "\n  AdWAISA:",
    text,
    count=1,
    flags=re.S,
)
if not (n1 and n2 and n3):
    raise SystemExit(f"patch failed: mat={n1} cond={n2} adm={n3}")
path.write_text(text, encoding="utf-8")
print("patched clinical.js visual reactivos")
