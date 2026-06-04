"""
fix_reservorio_encoding.py
==========================
Repara errores de codificación / espacios perdidos en el reservorio de
recomendaciones. El archivo original tiene patrones como:
  - "Higieneueño" en lugar de "Higiene del sueño"
  - "enguaje" en lugar de "del lenguaje"
  - "TDAHdulto" en lugar de "TDAH adulto"
  - "ueño" en lugar de "sueño"
  - "ueldo" en lugar de "sueño" (parece)
  - "recomendacionesdulto" en lugar de "recomendaciones adulto"

Estos errores se autocorrigen con reemplazos contextuales cuidadosos.
"""
import json
import re
import sys
from pathlib import Path

PATH = Path(r"D:\NeuroSoftApp\neurosoft-backend\app\domain\data\reservorio_recomendaciones.json")
BACKUP = Path(r"D:\NeuroSoftApp\neurosoft-backend\app\domain\data\reservorio_recomendaciones.backup-pre-fix-encoding.json")

# Cargar
data = json.loads(PATH.read_text(encoding="utf-8"))

# Backup defensivo
if not BACKUP.exists():
    BACKUP.write_text(PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Backup creado: {BACKUP}")

# Reemplazos ordenados (más específicos primero para evitar conflictos)
REPLACEMENTS = [
    # "Higieneueño" → "Higiene del sueño" (infantil TDAH, ansiedad)
    ("Higieneueño", "Higiene del sueño"),
    # "Higienedultodel sueño" → "Higiene del sueño" (con "adulto" colgando)
    ("Higienedultodel sueño", "Higiene del sueño"),
    # "Higienedultodel sueño" - ya cubierto
    # "ueño sueldo" o "apneaueño" → "apnea del sueño"
    ("apneaueño", "apnea del sueño"),
    # "estrés y apneaueño" → "estrés y apnea del sueño"
    # En "Manejo del estrés y apneaueño"
    # "estrés y apneaueño" → "estrés y apnea del sueño"
    ("estrés y apneaueño", "estrés y apnea del sueño"),
    # "enguaje" aparece donde debería decir "del lenguaje" o "en el lenguaje"
    ("compromisoenguaje", "compromiso del lenguaje"),
    ("específicoenguaje", "específico del lenguaje"),
    ("Estimulaciónenguaje", "Estimulación del lenguaje"),
    ("si hay compromisoenguaje", "si hay compromiso del lenguaje"),
    # "TDAHdulto" → "TDAH adulto" (depresión/ansiedad/TDAHdulto)
    ("depresión/TDAHdulto", "depresión/TDAH adulto"),
    ("ansiedad/TDAHdulto", "ansiedad/TDAH adulto"),
    ("TDAHdulto (", "TDAH adulto ("),
    # "ompradulto" aparece donde "del adulto" se partió
    ("ompradulto", "del adulto"),
    # "Discapacidad intelectualdulto" → "Discapacidad intelectual adulto"
    ("intelectualdulto", "intelectual adulto"),
    # "trastornos motoresdulto" → "trastornos motores adulto"
    ("motoresdulto", "motores adulto"),
    # "Desgasteuidador" → "Desgaste del cuidador" (encabezado)
    ("Desgasteuidador", "Desgaste del cuidador"),
    # "Higieneueño y reducción" - ya cubierto por Higieneueño
    # "del sueño" suelto queda OK tras los reemplazos
    # "ueldo" en autocuidadouidador → "del cuidador"
    ("autocuidadouidador", "autocuidado del cuidador"),
    # "Niño" con caracteres perdidos
    ("participacióniño", "participación del niño"),
    # "consumo" perdido "de c" → "consumo de c"
    ("Reducciónonsumo", "Reducción del consumo"),
    # "Organización" perdido "del t" → "Organización del t"
    ("Organizaciónrabajo", "Organización del trabajo"),
    # "icas familiar" → "icas a la familia"
    # Lo dejamos por ahora; ver caso por caso
    # "icas en el colegio" / "icas familiares" -> "indicaciones"
    # "icas de" - hmm
    # "pr omiso" → "compromiso"
    ("pr omiso", "compromiso"),
    # "delenn" / "penn" sueltos
    # "sueño" suelto (sin "del" antes)
    # ya cubierto por Higieneueño → Higiene del sueño
    # Caso "síntomas" sin espacio
    # "recomendacionesdulto" → "recomendaciones adulto"
    ("recomendacionesdulto", "recomendaciones adulto"),
    # Doble espacio al final de algunas recomendaciones
    # "  " → " " aplicado después
    ("absolutoabaquismo", "absoluto de tabaquismo"),
]

count_changes = 0


def fix_text(text: str) -> str:
    global count_changes
    for old, new in REPLACEMENTS:
        if old in text:
            n = text.count(old)
            text = text.replace(old, new)
            count_changes += n
    # Colapsar dobles espacios y espacios antes de puntuación
    new_text = re.sub(r" {2,}", " ", text)
    new_text = re.sub(r" +([.,;:])", r"\1", new_text)
    if new_text != text:
        count_changes += 1
    return new_text


def walk_and_fix(obj):
    if isinstance(obj, str):
        return fix_text(obj)
    if isinstance(obj, list):
        return [walk_and_fix(x) for x in obj]
    if isinstance(obj, dict):
        return {k: walk_and_fix(v) for k, v in obj.items()}
    return obj


fixed = walk_and_fix(data)

if count_changes == 0:
    print("No se encontraron errores que reparar.")
    sys.exit(0)

# Guardar
PATH.write_text(json.dumps(fixed, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Aplicados {count_changes} reemplazos en {PATH.name}.")
print(f"Backup: {BACKUP.name}")
