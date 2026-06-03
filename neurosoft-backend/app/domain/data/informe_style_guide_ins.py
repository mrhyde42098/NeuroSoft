"""
app/domain/data/informe_style_guide_ins.py
==========================================
Reglas de estilo institucional para informes neuropsicológicos. Se inyectan
en los system prompts de los endpoints de IA (narrate, improve) cuando el
contexto lo amerita (informes infantiles, WISC-IV, etc.).

La marca mostrada en el prompt se toma de `settings.clinical_brand`
(ver `app/core/branding.py`).

Fuentes clínicas:
  - Protocolos internos de informe NPS WISC
  - Análisis de Discrepancias WISC-IV (Flanagan & Kaufman, 2009)
"""
from __future__ import annotations

from collections.abc import Iterable

# ─────────────────────────────────────────────────────────────
# Reglas duras — se incluyen verbatim en el system prompt
# ─────────────────────────────────────────────────────────────

INS_STYLE_RULES: list[str] = [
    "Enfoque bottom-up: describe primero los datos observados y el funcionamiento cognitivo, antes de integrar con diagnóstico o hipótesis.",
    "NO uses las palabras «conserva», «preserva» ni «mantiene intacto» al describir funciones cognitivas en niños. En cambio, describe el nivel esperado para la edad o el desempeño observado.",
    "Usa el prefijo DIS- en lugar de A- (escribe «disfasia», «dislexia», «disgrafia», no «afasia» ni «alexia») cuando hablas de niños.",
    "No repitas información que ya aparece en gráficos, tablas o resultados numéricos. El texto debe aportar interpretación, no repetir cifras.",
    "No menciones nombres de pruebas específicas en el cuerpo narrativo. Habla de la función cognitiva evaluada (atención sostenida, memoria verbal, etc.), no del test (WISC, WMS, TMT).",
    "Considera el momento del desarrollo del paciente: los hallazgos tienen significado distinto según la etapa (preescolar, escolar, adolescencia, adulto joven, adulto mayor).",
    "No apiles diagnósticos. Si el niño presenta TDAH más dispraxia más retraso de lenguaje, el diagnóstico probablemente NO sea TDAH puro: revisa la hipótesis global.",
    "Usa español clínico colombiano, preciso y sobrio. Evita tecnicismos innecesarios y jerga coloquial.",
    "Nunca inventes datos, puntuaciones ni observaciones. Si un dato no está disponible, dilo explícitamente.",
    "Estructura del informe WISC infantil (orden sugerido): OBSERVACIÓN CLÍNICA → ATENCIÓN → PRAXIAS/GNOSIAS → LENGUAJE → FUNCIONES EJECUTIVAS → FUNCIONALIDAD → COCIENTE INTELECTUAL → IMPRESIÓN DIAGNÓSTICA → RECOMENDACIONES. En WISC-IV la sección MEMORIA no aplica — omítela.",
]


# Modelos teóricos de referencia — se citan si la narrativa
# menciona atención, lenguaje, memoria.
INS_THEORY_MODELS: dict[str, str] = {
    "atencion": "Modelo de Solberg-Mateer (atención focalizada, sostenida, selectiva, alternante, dividida).",
    "memoria":  "Modelos de Tulving y Atkinson-Shiffrin (registro sensorial, CP, MLP, episódica, semántica, procedimental).",
    "lenguaje": "Modelo de Ellis-Young (procesamiento fonológico, léxico, semántico y sintáctico).",
    "ffee":     "Modelo de Luria y Stuss (control inhibitorio, flexibilidad, planeación, memoria de trabajo).",
    "visoespacial": "Modelo de la corriente dorsal vs ventral (Ungerleider-Mishkin).",
    "praxias":  "Modelo de Liepmann (ideomotora, ideatoria, constructiva).",
}


# Prefijos que el motor reemplaza antes de emitir — evita «aprecio de
# afasia» cuando el paciente es un niño.
INS_TERM_REPLACEMENTS_PEDIATRIC: dict[str, str] = {
    "afasia": "disfasia",
    "alexia": "dislexia",
    "agrafia": "disgrafia",
    "acalculia": "discalculia",
    "apraxia": "dispraxia",
    "agnosia": "disgnosia",
}


# ─────────────────────────────────────────────────────────────
# Helpers para inyectar en system prompts
# ─────────────────────────────────────────────────────────────

def build_ins_style_suffix(
    *,
    is_pediatric: bool = False,
    test: str | None = None,
    dominios: Iterable[str] | None = None,
) -> str:
    """
    Devuelve un bloque de texto listo para concatenar a `_build_system` en ai.py.

    Se incluyen las reglas duras siempre, y se añaden modelos teóricos sólo
    para los dominios relevantes.
    """
    try:
        from app.core.branding import clinical_brand
        _brand = clinical_brand()
    except Exception:
        _brand = "institucional"
    partes: list[str] = [
        f"Sigue ESTRICTAMENTE las reglas de estilo {_brand} al redactar:",
    ]
    for i, regla in enumerate(INS_STYLE_RULES, 1):
        partes.append(f"{i}. {regla}")

    if is_pediatric:
        partes.append(
            "\nEste paciente es pediátrico: nunca uses «conserva» ni «preserva», "
            "usa prefijo DIS- (dislexia, dispraxia, disfasia, discalculia) y "
            "considera el hito del desarrollo correspondiente."
        )

    if test and "wisc" in test.lower():
        partes.append(
            "\nEste es un informe WISC-IV: OMITE la sección de MEMORIA (no aplica al WISC). "
            "No menciones «WISC» en el texto narrativo — habla de la función cognitiva."
        )

    if dominios:
        modelos: list[str] = []
        for d in dominios:
            key = (d or "").strip().lower()
            if key in INS_THEORY_MODELS:
                modelos.append(f"- {key}: {INS_THEORY_MODELS[key]}")
        if modelos:
            partes.append("\nReferencias teóricas aplicables:")
            partes.extend(modelos)

    return "\n".join(partes)


def apply_pediatric_term_replacements(text: str) -> str:
    """Reemplaza términos A- por DIS- en texto pediátrico."""
    if not text:
        return text
    out = text
    for bad, good in INS_TERM_REPLACEMENTS_PEDIATRIC.items():
        # Reemplazo case-insensitive preservando mayúscula inicial
        for variant in (bad, bad.capitalize(), bad.upper()):
            if variant in out:
                repl = good if variant == bad else (good.capitalize() if variant == bad.capitalize() else good.upper())
                out = out.replace(variant, repl)
    return out


__all__ = [
    "INS_STYLE_RULES",
    "INS_THEORY_MODELS",
    "INS_TERM_REPLACEMENTS_PEDIATRIC",
    "build_ins_style_suffix",
    "apply_pediatric_term_replacements",
]
