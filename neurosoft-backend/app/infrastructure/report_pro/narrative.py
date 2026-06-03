"""
report_pro.narrative
=====================
Generación de texto clínico *integrador* a partir de los resultados.

El objetivo NO es sustituir lo que el clínico escribe en la historia clínica
(`obs_*`), sino añadir una capa cuantitativa profesional que cite valores
específicos (CI, Z, percentiles, discrepancias) y los integre en frases
clínicamente correctas.

Toda la salida va en español neutro y se diseñó para sonar como informe real,
no como volcado mecánico de datos.
"""
from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence

# Umbrales clínicos estándar (Wechsler / DSM-5)
DEBIL_Z = -1.0
DEBIL_SEVERO_Z = -2.0
FUERTE_Z = 1.0
FUERTE_MARCADO_Z = 2.0


def _interpret_ci_range(ci: int) -> str:
    """Categoría descriptiva según rango de CI (Wechsler)."""
    if ci is None:
        return "—"
    if ci < 70:
        return "Extremadamente bajo"
    if ci < 80:
        return "Limítrofe"
    if ci < 90:
        return "Promedio bajo"
    if ci < 110:
        return "Promedio"
    if ci < 120:
        return "Promedio alto"
    if ci < 130:
        return "Superior"
    return "Muy superior"


def _percentil_from_z(z: float) -> float:
    """Percentil aproximado dado un Z (función de distribución normal estándar)."""
    return 0.5 * (1 + math.erf(z / math.sqrt(2))) * 100


def _domain_summary(resultados: Sequence[dict]) -> dict[str, dict]:
    """Resumen por dominio cognitivo: media Z, n, pruebas representativas."""
    bucket: dict[str, dict] = defaultdict(lambda: {"zs": [], "tests": []})
    for r in resultados:
        z = r.get("z_equivalente")
        if z is None:
            continue
        if r.get("tipo_metrica") == "ci":
            continue
        dom = (r.get("dominio_cognitivo") or "").strip()
        if not dom or dom.lower() in ("", "n/a"):
            continue
        bucket[dom]["zs"].append(float(z))
        bucket[dom]["tests"].append({
            "nombre": r.get("test_nombre", r.get("test_id", "")),
            "z": z,
            "pd": r.get("puntaje_bruto"),
            "pe": r.get("puntaje_escalar"),
        })
    out = {}
    for dom, info in bucket.items():
        zs = info["zs"]
        out[dom] = {
            "n": len(zs),
            "mean_z": sum(zs) / len(zs),
            "min_z": min(zs),
            "max_z": max(zs),
            "tests": sorted(info["tests"], key=lambda t: t["z"]),
        }
    return out


def _extract_ci_indices(resultados: Sequence[dict]) -> dict[str, int]:
    """Mapea ICV, IRP, IMT, IVP, CIT a sus valores numéricos."""
    mapping_keys = {
        "indcomver": "ICV", "icv": "ICV",
        "indrazper": "IRP", "irp": "IRP", "icp": "IRP",
        "indmemtra": "IMT", "imt": "IMT",
        "indvelpro": "IVP", "ivp": "IVP",
        "tot": "CIT", "cit": "CIT", "indtot": "CIT",
    }
    out: dict[str, int] = {}
    for r in resultados:
        if r.get("tipo_metrica") != "ci":
            continue
        score = r.get("puntaje_escalar")
        if score is None:
            continue
        raw_id = str(r.get("test_id", "")).lower()
        for key, alias in mapping_keys.items():
            if key in raw_id:
                out.setdefault(alias, int(score))
                break
    return out


# ──────────────────────────────────────────────────────────
# Generadores de texto
# ──────────────────────────────────────────────────────────

def build_synthesis_paragraphs(
    resultados: Sequence[dict],
    *,
    paciente_nombre: str = "El paciente",
    protocolo: str = "",
) -> list[str]:
    """Construye la *síntesis clínica integradora* como lista de párrafos."""
    paragraphs: list[str] = []
    indices = _extract_ci_indices(resultados)
    domains = _domain_summary(resultados)

    # ── Párrafo 1: cuadro general (CIT + categoría) ──
    if "CIT" in indices:
        cit = indices["CIT"]
        cat = _interpret_ci_range(cit)
        pcent = _percentil_from_z((cit - 100) / 15) if cit else None
        p1 = (
            f"{paciente_nombre} obtuvo un Cociente Intelectual Total (CIT) de "
            f"{cit}, ubicándose en la categoría {cat.lower()} "
            f"(percentil aproximado {pcent:.0f})."
        )
        # Comparativo con índices
        rest = {k: v for k, v in indices.items() if k != "CIT"}
        if rest:
            vals = sorted(rest.items(), key=lambda kv: kv[1])
            lo_k, lo_v = vals[0]
            hi_k, hi_v = vals[-1]
            if hi_v - lo_v >= 12:
                p1 += (
                    f" Se observa una variabilidad relevante entre sus índices "
                    f"compuestos: el más bajo corresponde a {lo_k} ({lo_v}) y el "
                    f"más alto a {hi_k} ({hi_v}), lo que sugiere un perfil "
                    f"asimétrico que conviene analizar por separado más que "
                    f"resumir en una única puntuación global."
                )
            else:
                p1 += (
                    f" Los índices compuestos muestran homogeneidad relativa "
                    f"(rango {lo_k}={lo_v} a {hi_k}={hi_v}), lo que respalda "
                    f"la interpretación del CIT como medida representativa."
                )
        paragraphs.append(p1)
    elif indices:
        # Sin CIT, pero hay índices
        idx_str = ", ".join(f"{k}={v}" for k, v in sorted(indices.items()))
        paragraphs.append(
            f"Sus índices compuestos fueron: {idx_str}. "
            "Dado que no se administró la batería completa, no se reporta "
            "Cociente Intelectual Total."
        )

    # ── Párrafo 2: dominios destacados ──
    if domains:
        weak = [(d, info) for d, info in domains.items() if info["mean_z"] <= DEBIL_Z]
        strong = [(d, info) for d, info in domains.items() if info["mean_z"] >= FUERTE_Z]
        weak.sort(key=lambda x: x[1]["mean_z"])
        strong.sort(key=lambda x: -x[1]["mean_z"])

        chunks = []
        if weak:
            sev_chunks = []
            for d, info in weak:
                qualifier = "severamente" if info["mean_z"] <= DEBIL_SEVERO_Z else "moderadamente"
                sev_chunks.append(f"{d.lower()} ({qualifier} disminuido, Z̄={info['mean_z']:+.1f})")
            chunks.append(
                "El perfil neuropsicológico evidencia debilidades en: "
                + "; ".join(sev_chunks) + "."
            )
        if strong:
            ch_strong = []
            for d, info in strong:
                qualifier = "muy" if info["mean_z"] >= FUERTE_MARCADO_Z else ""
                tag = f"{qualifier} alto, Z̄={info['mean_z']:+.1f}".strip()
                ch_strong.append(f"{d.lower()} ({tag})")
            chunks.append(
                "Por su parte, destacan como áreas preservadas o por encima del "
                "promedio: " + "; ".join(ch_strong) + "."
            )
        if not weak and not strong:
            chunks.append(
                "El perfil cognitivo se ubica globalmente dentro del rango "
                "normal esperado para la edad, sin debilidades ni fortalezas "
                "significativas en los dominios evaluados."
            )
        paragraphs.append(" ".join(chunks))

    # ── Párrafo 3: pruebas específicas más críticas (top 3 debilidades) ──
    all_results = sorted(
        [r for r in resultados
         if r.get("z_equivalente") is not None
         and r.get("tipo_metrica") != "ci"],
        key=lambda r: r["z_equivalente"],
    )
    if all_results and all_results[0]["z_equivalente"] <= DEBIL_Z:
        critical = all_results[:3]
        items = []
        for r in critical:
            if r.get("z_equivalente") > DEBIL_Z:
                break
            nombre = r.get("test_nombre", r.get("test_id", ""))
            z = r["z_equivalente"]
            interp = r.get("interpretacion", "")
            items.append(f"{nombre} (Z={z:+.2f}, {interp.lower()})")
        if items:
            paragraphs.append(
                "Entre las pruebas con mayor desviación se encuentran "
                + "; ".join(items)
                + ". Estos hallazgos orientan la formulación diagnóstica y la "
                "priorización de objetivos de intervención."
            )

    return paragraphs


def build_strengths_weaknesses(resultados: Sequence[dict]) -> tuple[list[str], list[str]]:
    """Listas planas de fortalezas y debilidades (bullets) por prueba.

    Filtra a Z<=-1 y Z>=1, ordena por magnitud absoluta.
    """
    weak, strong = [], []
    for r in resultados:
        z = r.get("z_equivalente")
        if z is None or r.get("tipo_metrica") == "ci":
            continue
        nombre = r.get("test_nombre", r.get("test_id", ""))
        if z <= DEBIL_Z:
            weak.append((z, nombre, r.get("interpretacion", "")))
        elif z >= FUERTE_Z:
            strong.append((-z, nombre, r.get("interpretacion", "")))
    weak.sort()
    strong.sort()
    weak_str = [f"{n} — {i.lower()} (Z={z:+.2f})" for z, n, i in weak[:8]]
    strong_str = [f"{n} — {i.lower()} (Z={-z:+.2f})" for z, n, i in strong[:6]]
    return weak_str, strong_str


# ──────────────────────────────────────────────────────────
# Recomendaciones agrupadas por área y prioridad
# ──────────────────────────────────────────────────────────

PRIORIDAD_LABEL = {
    "alta": "Prioridad alta",
    "media": "Prioridad media",
    "baja": "Prioridad baja / seguimiento",
}


def parse_recomendaciones(text: str) -> dict[str, list[dict]]:
    """Parsea el texto de recomendaciones del clínico.

    Estrategia:
      1. Divide por líneas no vacías.
      2. Detecta prefijos: ``[ESCOLAR]``, ``[OCUPACIONAL]``, ``[TERAPÉUTICA]``,
         ``[MÉDICA]``, ``[FAMILIAR]``, ``[SEGUIMIENTO]``.
         Si no hay prefijo, va a ``General``.
      3. Detecta prefijos de prioridad: ``(alta)``, ``(media)``, ``(baja)``.
         Si no hay, asume ``media``.

    Devuelve dict ``{area: [{"texto": ..., "prioridad": ...}]}``.
    """
    if not text:
        return {}
    areas: dict[str, list[dict]] = defaultdict(list)
    AREA_PREFIXES = {
        "[ESCOLAR]": "Escolar",
        "[OCUPACIONAL]": "Ocupacional",
        "[TERAPEUTICA]": "Terapéutica",
        "[TERAPÉUTICA]": "Terapéutica",
        "[MEDICA]": "Médica",
        "[MÉDICA]": "Médica",
        "[FAMILIAR]": "Familiar",
        "[SEGUIMIENTO]": "Seguimiento",
        "[REHABILITACION]": "Rehabilitación",
        "[REHABILITACIÓN]": "Rehabilitación",
    }
    PRIORITY_TAGS = {
        "(alta)": "alta", "(media)": "media", "(baja)": "baja",
        "[alta]": "alta", "[media]": "media", "[baja]": "baja",
        "!!!": "alta", "!!": "media", "!": "baja",
    }
    raw_lines = [ln.strip() for ln in str(text).splitlines() if ln.strip()]
    # Caso simple: si no hay tags, generamos 1 bloque "General"
    if not any(tag in text.upper() for tag in AREA_PREFIXES):
        # Heurística: dividir por puntos finales o ";"
        chunks: list[str] = []
        for ln in raw_lines:
            # bullets tipo "- foo", "* foo", "1. foo"
            cleaned = ln.lstrip("-•*0123456789.) ").strip()
            if cleaned:
                chunks.append(cleaned)
        for c in chunks:
            areas["General"].append({"texto": c, "prioridad": "media"})
        return dict(areas)
    # Caso con tags
    for ln in raw_lines:
        area = "General"
        priority = "media"
        upper = ln.upper()
        for tag, name in AREA_PREFIXES.items():
            if tag in upper:
                area = name
                ln = ln.replace(tag, "", 1).replace(tag.lower(), "", 1).strip()
                break
        lower = ln.lower()
        for tag, name in PRIORITY_TAGS.items():
            if tag in lower:
                priority = name
                ln = ln.replace(tag, "").strip()
                break
        cleaned = ln.lstrip("-•*0123456789.) ").strip()
        if cleaned:
            areas[area].append({"texto": cleaned, "prioridad": priority})
    return dict(areas)


# ═══════════════════════════════════════════════════════════════════
# S2.5: 7 principios narrativos + cláusulas legales colombianas
# ═══════════════════════════════════════════════════════════════════
# La narrativa clínica debe cumplir SIETE principios éticos y técnicos
# (basados en Sattler 2008, Eisman 1962, Ley 1090/2006 art. 36).
# ═══════════════════════════════════════════════════════════════════


PRINCIPIOS_NARRATIVOS = [
    {
        "id": "P1",
        "titulo": "Integración cuantitativa-cualitativa",
        "descripcion": "Cada hallazgo numérico debe acompañarse de su significado clínico, no presentarse aislado. Un CI de 87 no dice nada sin contexto (edad, escolaridad, motivo de consulta).",
        "ejemplo": "❌ 'CI Total: 87.'  ✅ 'El CI Total de 87 (rango Promedio Bajo) sugiere un rendimiento intelectual general dentro de los límites esperados para su edad y escolaridad, con áreas específicas de dificultad descritas a continuación.'",
    },
    {
        "id": "P2",
        "titulo": "No patologizar variaciones normales",
        "descripcion": "Las puntuaciones bajas aisladas no constituyen diagnóstico. Solo se patologiza cuando hay: (a) cruce del umbral clínico, (b) impacto funcional, (c) duración significativa, (d) consistencia entre evaluadores.",
        "ejemplo": "❌ 'El paciente presenta déficit atencional.'  ✅ 'El paciente obtuvo puntuaciones en el rango limítrofe en tareas de atención sostenida; se recomienda complementar con observación conductual y, si se confirma, evaluar con criterios DSM-5-TR.'",
    },
    {
        "id": "P3",
        "titulo": "Citar normas colombianas cuando existan",
        "descripcion": "Si se aplican baremos de Neuronorma Colombia (Arango-Lasprilla & Rivera 2017), se debe mencionar explícitamente. Si se usan baremos internacionales (WISC-IV EUA), se debe aclarar la limitación transcultural.",
        "ejemplo": "✅ 'Las puntuaciones se interpretaron con baremos de Neuronorma Colombia (Arango-Lasprilla & Rivera, 2017), válidos para población adulta colombiana.'",
    },
    {
        "id": "P4",
        "titulo": "Lenguaje descriptivo, no definitivo",
        "descripcion": "Preferir 'sugiere', 'es consistente con', 'apoya la hipótesis de' sobre 'el paciente tiene' o 'es un caso de'. El informe es una hipótesis clínica, no un veredicto.",
        "ejemplo": "❌ 'El paciente tiene TDAH.'  ✅ 'El perfil neuropsicológico es consistente con un TDAH de predominio inatento (DSM-5-TR 314.00 / CIE-10 F90.0), pendiente de confirmación clínica integral.'",
    },
    {
        "id": "P5",
        "titulo": "Reconocer limitaciones del instrumento",
        "descripcion": "Todo test tiene limitaciones psicométricas. Mencionarlas protege al clínico y al paciente. Incluir: validez de síntomas, condiciones de aplicación, fatiga, medicación.",
        "ejemplo": "✅ 'Es importante señalar que el rendimiento del paciente pudo estar influenciado por la fatiga reportada al final de la sesión y por la ausencia de gafas correctivas que manifiesta usar habitualmente.'",
    },
    {
        "id": "P6",
        "titulo": "Recomendaciones accionables y graduadas",
        "descripcion": "Cada recomendación debe ser concreta, con responsable y plazo. Evitar 'se recomienda seguimiento' (sin decir quién, cuándo, cómo).",
        "ejemplo": "❌ 'Se recomienda intervención.'  ✅ 'Se sugiere inicio de terapia de rehabilitación cognitiva con frecuencia bisemanal (lunes y jueves), 12 sesiones, evaluación de progreso a la sesión 6 con ajuste de plan.'",
    },
    {
        "id": "P7",
        "titulo": "Firma, fecha, y huella de auditoría",
        "descripcion": "Todo informe debe terminar con: nombre del profesional, registro profesional, fecha, lugar, y código de verificación interno. Esto protege legalmente al clínico y al paciente.",
        "ejemplo": "✅ 'Firma: __________  Registro Profesional: __________  Fecha: __________  Código verificador: NS-{uuid8}'",
    },
]


# Cláusulas legales colombianas para incluir en informes
CLAUSULAS_LEGALES = {
    "ley_1090_2006": (
        "Este informe se emite bajo la responsabilidad profesional del psicólogo "
        "firmante, conforme al artículo 36 de la Ley 1090 de 2006 (Código "
        "Deontológico del Psicólogo en Colombia). El uso indebido de la información "
        "contenida en este documento está sujeto a las sanciones legales vigentes."
    ),
    "res_1995_1999": (
        "La historia clínica del paciente, incluyendo este informe, se conserva "
        "conforme a la Resolución 1995 de 1999, que establece las normas para el "
        "manejo de la historia clínica. La información es confidencial y su acceso "
        "se rige por el principio de habeas data (Ley 1581 de 2012)."
    ),
    "habeas_data": (
        "El paciente puede ejercer en cualquier momento sus derechos de acceso, "
        "rectificación, actualización y supresión de sus datos personales conforme "
        "a la Ley 1581 de 2012 y el Decreto 1377 de 2013, mediante solicitud "
        "escrita al responsable del tratamiento."
    ),
    "ia_clausula": (
        "Las secciones marcadas como [BORRADOR IA] fueron generadas con apoyo de "
        "inteligencia artificial y han sido revisadas y editadas por el "
        "profesional tratante, quien asume la responsabilidad del contenido final. "
        "Esta cláusula se incluye conforme a la Ley 1090 de 2006 sobre "
        "responsabilidad profesional del psicólogo."
    ),
    "responsabilidad": (
        "La impresión diagnóstica contenida en este informe es de carácter "
        "neuropsicológico y se basa en los hallazgos de la evaluación realizada. "
        "NO sustituye el diagnóstico clínico integral, que requiere correlación "
        "con la historia clínica completa, observación conductual y, cuando "
        "aplique, evaluación por otros profesionales de salud."
    ),
}


def aplicar_principios_en_narrativa(texto: str) -> str:
    """
    Post-procesa una narrativa para reforzar los 7 principios.
    Devuelve el texto original (los principios son guía editorial, no
    transformación automática). Esta función existe como hook para que
    el clínico pueda auditar su narrativa contra los principios.
    """
    # Por ahora no transforma: los principios son guía editorial.
    # Pero dejamos el hook para extensiones futuras (p.ej. detectar
    # lenguaje definitivo y suavizarlo).
    return texto


# F6.2 — Validador automático contra los 7 principios narrativos.
# Diseñado como checklist NO bloqueante: el clínico decide si aplicar las
# recomendaciones. El informe final lo firma él, no el algoritmo.
#
# Las heurísticas son deliberadamente conservadoras (alto recall, baja
# precision) para no insultar al clínico. Marcar un principio como
# "revisar" solo dispara una recomendación explícita en el pie de firma.
#


# Marcadores de "lenguaje definitivo" (anti-P4). Se aplica cuando un
# evaluador escribe "el paciente tiene X" sin matizar. La heurística es
# buscarlos como frases completas, no como subcadenas dentro de palabras
# (p.ej. no debe disparar "diagnóstico" dentro de "diagnóstica").
_LENGUAJE_DEFINITIVO = [
    r"\bel paciente tiene\b",
    r"\bpresenta (?:un|una|trastorno|déficit|discapacidad)\b",
    r"\bes un caso de\b",
    r"\bsufre de\b",
]


# Marcadores de P5 (reconocer limitaciones). Detección de muletillas que
# indican que el clínico reconoció algún factor contextual.
_LIMITACIONES_MARCADORES = [
    r"\b(?:fatiga|cansancio|ansiedad|sueño|medicación|gafas|audífono|motivación|esfuerzo)\b",
    r"\b(?:validez de síntomas|escala de validez|condiciones de aplicación|instrumento)\b",
    r"\b(?:limitación|limitaciones|advertir|tener en cuenta|considerar)\b",
]


# Marcadores de P3 (citar normas colombianas). Detección de baremos
# colombianos referenciados.
_NORMAS_COLOMBIANAS = [
    r"\bNeuronorma Colombia\b",
    r"\bArango[- ]Lasprilla\b",
    r"\bRivera\b",
    r"\bBaremos?\s+colombianos?\b",
    r"\bpoblaci[oó]n\s+colombiana\b",
]


# Marcadores de P6 (recomendaciones accionables). Patrones típicos de
# recomendaciones vagas que se deben re-escribir.
_RECOMENDACIONES_VAGAS = [
    r"\bse recomienda (?:seguimiento|intervenci[oó]n|tratamiento)\b",
    r"\b(?:se sugiere|sugerimos)\s+(?:atenci[oó]n|seguimiento)\b(?!\s+(?:bisemanal|semanal|con\s+frecuencia))",
]


def validar_principios_narrativa(
    texto: str,
    *,
    recomendaciones: str = "",
    poblacion_objetivo: str = "adulto_joven",
) -> dict:
    """
    F6.2 — Audita una narrativa contra los 7 principios narrativos.

    Devuelve un dict con:
        - ``cumple``: bool (todos los principios OK o sin obligación)
        - ``principios``: dict[id] = {"titulo", "estado", "detalle"}
            estado ∈ {"ok", "revisar", "no_aplica"}
        - ``resumen``: str legible para incluir en el pie de firma
        - ``alertas``: list[str] con las recomendaciones concretas

    La función es **no bloqueante**: el clínico puede ignorar las
    alertas. La auditoría se incluye como checklist en el bloque de
    firma para que el evaluador documente su revisión.

    Parámetros
    ----------
    texto : str
        Narrativa principal (síntesis + impresión diagnóstica).
    recomendaciones : str
        Texto de recomendaciones separado (para auditar P6).
    poblacion_objetivo : str
        ``"infantil"`` | ``"adulto_joven"`` | ``"adulto_mayor"``.

    Notas de diseño
    ---------------
    * Heurísticas conservadoras: marcan ``revisar`` solo con señales
      claras (lenguaje definitivo, recomendaciones vagas, ausencia de
      mención a baremos cuando aplica).
    * P1 (integración) y P7 (firma) no se auditan automáticamente —
      son responsabilidad del clínico. Se marcan como ``ok`` si la
      narrativa no es trivial, y se omite el detalle.
    * P3 solo es obligatorio cuando se usan baremos colombianos, lo
      cual se infiere del campo ``poblacion_objetivo``.
    """
    import re

    texto_lower = (texto or "").lower()
    rec_lower = (recomendaciones or "").lower()
    completo = (texto or "") + "\n" + (recomendaciones or "")

    principios: dict[str, dict] = {}

    # P1: Integración cuantitativa-cualitativa
    if len(texto.strip()) >= 200:
        principios["P1"] = {
            "titulo": "Integración cuantitativa-cualitativa",
            "estado": "ok",
            "detalle": "Narrativa con extensión suficiente para integrar hallazgos.",
        }
    else:
        principios["P1"] = {
            "titulo": "Integración cuantitativa-cualitativa",
            "estado": "revisar",
            "detalle": "Narrativa muy corta (<200 caracteres). Revisar si integra los hallazgos cuantitativos con su significado clínico.",
        }

    # P2: No patologizar variaciones normales
    # Si NO hay CI o puntaje explícito en el texto, marcar como no_aplica;
    # si los hay, verificar que aparezca un "sugiere" o "consistente con".
    tiene_puntuacion = bool(re.search(r"\b(?:CI|cociente|percentil|escalar|z[- ]?score|puntuaci[oó]n\s+z)\b", texto, re.IGNORECASE))
    if not tiene_puntuacion:
        principios["P2"] = {
            "titulo": "No patologizar variaciones normales",
            "estado": "no_aplica",
            "detalle": "No se detectaron puntuaciones explícitas en la narrativa.",
        }
    else:
        if re.search(r"\b(?:sugiere|consistente con|apoya|orienta a|compatible con|indicativo de)\b", texto, re.IGNORECASE):
            principios["P2"] = {
                "titulo": "No patologizar variaciones normales",
                "estado": "ok",
                "detalle": "Lenguaje hipotético detectado ('sugiere', 'consistente con').",
            }
        else:
            principios["P2"] = {
                "titulo": "No patologizar variaciones normales",
                "estado": "revisar",
                "detalle": "Se citan puntuaciones pero no se usan verbos hipotéticos. Considerar matizar el lenguaje.",
            }

    # P3: Citar normas colombianas
    if poblacion_objetivo in ("adulto_mayor", "infantil"):
        menciona_norma = any(re.search(p, completo, re.IGNORECASE) for p in _NORMAS_COLOMBIANAS)
        if menciona_norma:
            principios["P3"] = {
                "titulo": "Citar normas colombianas cuando existan",
                "estado": "ok",
                "detalle": "Se hace referencia a baremos colombianos.",
            }
        else:
            principios["P3"] = {
                "titulo": "Citar normas colombianas cuando existan",
                "estado": "revisar",
                "detalle": "Población {}: se recomienda mencionar baremo de Neuronorma Colombia (Arango-Lasprilla & Rivera, 2017).".format(
                    poblacion_objetivo
                ),
            }
    else:
        principios["P3"] = {
            "titulo": "Citar normas colombianas cuando existan",
            "estado": "no_aplica",
            "detalle": "Población adulto_joven: los baremos principales son WAIS-III con norma internacional; citarlo solo si aplica.",
        }

    # P4: Lenguaje descriptivo, no definitivo
    matches_p4 = [p for p in _LENGUAJE_DEFINITIVO if re.search(p, texto_lower, re.IGNORECASE)]
    if matches_p4:
        principios["P4"] = {
            "titulo": "Lenguaje descriptivo, no definitivo",
            "estado": "revisar",
            "detalle": "Se detectaron marcadores de lenguaje definitivo: '{}'. Considere suavizar a 'sugiere', 'es consistente con'.".format(
                ", ".join(matches_p4)
            ),
        }
    else:
        principios["P4"] = {
            "titulo": "Lenguaje descriptivo, no definitivo",
            "estado": "ok",
            "detalle": "Sin marcadores de lenguaje definitivo.",
        }

    # P5: Reconocer limitaciones del instrumento
    if any(re.search(p, completo, re.IGNORECASE) for p in _LIMITACIONES_MARCADORES):
        principios["P5"] = {
            "titulo": "Reconocer limitaciones del instrumento",
            "estado": "ok",
            "detalle": "Se mencionan factores contextuales o limitaciones.",
        }
    else:
        principios["P5"] = {
            "titulo": "Reconocer limitaciones del instrumento",
            "estado": "revisar",
            "detalle": "No se mencionan condiciones de aplicación, fatiga, medicación u otras limitaciones.",
        }

    # P6: Recomendaciones accionables y graduadas
    if not recomendaciones.strip():
        principios["P6"] = {
            "titulo": "Recomendaciones accionables y graduadas",
            "estado": "no_aplica",
            "detalle": "Sin sección de recomendaciones para auditar.",
        }
    else:
        vagas = [p for p in _RECOMENDACIONES_VAGAS if re.search(p, rec_lower, re.IGNORECASE)]
        if vagas:
            principios["P6"] = {
                "titulo": "Recomendaciones accionables y graduadas",
                "estado": "revisar",
                "detalle": "Recomendaciones vagas detectadas. Agregar responsable, frecuencia y plazo concretos.",
            }
        else:
            principios["P6"] = {
                "titulo": "Recomendaciones accionables y graduadas",
                "estado": "ok",
                "detalle": "Recomendaciones con verbos de acción y frecuencia/plazo.",
            }

    # P7: Firma, fecha, y huella de auditoría
    # No auditable automáticamente; se marca como 'ok' con nota.
    principios["P7"] = {
        "titulo": "Firma, fecha, y huella de auditoría",
        "estado": "ok",
        "detalle": "Verificar manualmente: nombre, tarjeta profesional, fecha, lugar, código verificador.",
    }

    # Resumen
    alertas = [
        f"[{pid}] {p['titulo']}: {p['detalle']}"
        for pid, p in principios.items()
        if p["estado"] == "revisar"
    ]
    cumple = all(p["estado"] in ("ok", "no_aplica") for p in principios.values())

    resumen_partes = []
    for pid in ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]:
        p = principios[pid]
        icono = {"ok": "✓", "revisar": "⚠", "no_aplica": "—"}[p["estado"]]
        resumen_partes.append(f"{icono} {pid} {p['titulo']}")
    resumen = "  ".join(resumen_partes)

    return {
        "cumple": cumple,
        "principios": principios,
        "alertas": alertas,
        "resumen": resumen,
    }


def clausula_legal(clave: str) -> str:
    """Devuelve una cláusula legal por clave, o cadena vacía si no existe."""
    return CLAUSULAS_LEGALES.get(clave, "")


# ═══════════════════════════════════════════════════════════════════
# S3.2: Helpers para versión paciente del informe
# ═══════════════════════════════════════════════════════════════════
# Lenguaje claro, sin percentiles, sin jerga. Para el paciente y su familia.
# Basado en guía "Cómo comunicar resultados neuropsicológicos" (Sattler 2008,
# adaptado a paciente colombiano promedio, escolaridad media).
# ═══════════════════════════════════════════════════════════════════


# Mapeo técnico → lenguaje claro. Probado contra escolaridad media
# colombiana; para menor escolaridad se recomienda apoyo verbal del clínico.
MAPEO_LENGUAJE_CLARO = {
    # CI / inteligencia
    "CI Total": "tu rendimiento intelectual general",
    "Coeficiente Intelectual Total": "tu rendimiento intelectual general",
    "Inteligencia": "la forma en que tu cerebro resuelve problemas",
    "funcionamiento intelectual": "tu capacidad para pensar y resolver problemas",

    # Memoria
    "Memoria de Trabajo": "la capacidad de mantener información en mente mientras haces otra cosa",
    "memoria auditiva": "la capacidad de recordar lo que escuchas",
    "memoria visual": "la capacidad de recordar lo que ves",
    "memoria de trabajo": "tu memoria activa, como la mesa de trabajo mental",

    # Atención
    "Atención Sostenida": "la capacidad de mantener la atención por ratos largos",
    "Atención Selectiva": "la capacidad de filtrar lo que importa y dejar de lado lo que distrae",
    "atención": "tu capacidad de concentrarte",

    # Funciones ejecutivas
    "Funciones Ejecutivas": "tus habilidades para planificar, organizarte y controlar impulsos",
    "control inhibitorio": "la capacidad de detener una respuesta automática",
    "flexibilidad cognitiva": "la capacidad de cambiar de tarea o de estrategia",
    "planificación": "la capacidad de organizar pasos para lograr una meta",

    # Lenguaje
    "Comprensión Verbal": "la comprensión de lo que te dicen",
    "Expresión Verbal": "la forma en que te expresas con palabras",
    "fluidez verbal": "la facilidad para producir palabras",

    # Velocidad
    "Velocidad de Procesamiento": "qué tan rápido tu cerebro hace tareas sencillas",
    "velocidad": "la rapidez con que procesas información",

    # Visuoespacial
    "Razonamiento Visuoespacial": "la capacidad de imaginar y manipular formas en tu mente",
    "habilidades visuoespaciales": "la capacidad de manejar formas y espacios",

    # Clasificación bandas
    "Superior": "muy por encima del promedio",
    "Promedio Alto": "por encima del promedio",
    "Promedio": "dentro del rango esperado",
    "Promedio Bajo": "un poco por debajo del promedio",
    "Bajo": "por debajo del promedio",
    "Muy Bajo": "muy por debajo del promedio",

    # Diagnósticos
    "TDAH": "dificultades de atención",
    "TEA": "condiciones del neurodesarrollo que afectan la comunicación y la interacción social",
    "Discapacidad Intelectual": "condiciones que afectan el aprendizaje y la vida diaria",
    "Depresión": "estado de ánimo bajo persistente",
    "Ansiedad": "preocupación intensa y persistente",
    "TEPT": "secuelas emocionales después de un evento muy estresante",
}


def traducir_termino(termino: str) -> str:
    """Traduce un término técnico a lenguaje claro."""
    if not termino:
        return ""
    # Búsqueda exacta
    if termino in MAPEO_LENGUAJE_CLARO:
        return MAPEO_LENGUAJE_CLARO[termino]
    # Búsqueda case-insensitive (solo si NO hubo match exacto)
    termino_norm = termino.strip().lower()
    for k, v in MAPEO_LENGUAJE_CLARO.items():
        if k.strip().lower() == termino_norm:
            return v
    # Si no se encuentra, devolver el original (no se debe inventar)
    return termino


def banda_a_lenguaje_claro(banda: str) -> str:
    """Traduce una banda de clasificación a una frase clara para el paciente."""
    if not banda or banda == "—":
        return "dentro del rango esperado"
    return MAPEO_LENGUAJE_CLARO.get(banda, banda)


def generar_resumen_paciente(
    resultados: list[dict],
    paciente_nombre: str = "",
    recomendaciones: list[str] | None = None,
) -> dict:
    """
    Genera un resumen en lenguaje claro para el paciente.

    Devuelve un dict con secciones:
      - 'saludo': bienvenida cálida
      - 'que_hicimos': descripción de la evaluación
      - 'que_encontramos': hallazgos en lenguaje claro (sin percentiles)
      - 'fortalezas': qué se hace bien
      - 'areas_apoyo': en qué se puede trabajar
      - 'que_recomendamos': plan de acción claro
      - 'preguntas_frecuentes': FAQ para el paciente
    """
    nombre = paciente_nombre.split()[0] if paciente_nombre else "tú"

    saludo = (
        f"Este es un resumen de la evaluación que se realizó {nombre}. "
        "Está escrito en un lenguaje sencillo para que sea fácil de entender. "
        "Tu psicólogo o psicóloga te explicará los detalles y resolverá "
        "cualquier duda que tengas."
    )

    que_hicimos = (
        "Realizamos varias pruebas que miden cómo funciona tu cerebro en "
        "distintas situaciones: memoria, atención, lenguaje, razonamiento y "
        "la velocidad con la que procesas información. Las pruebas son como "
        "\"pequeños retos\" que se resuelven con papel, lápiz y a veces con cubos "
        "o figuras. No hay respuestas buenas ni malas: lo que nos interesa es "
        "conocer cómo trabaja tu mente."
    )

    # Procesar resultados: agrupar por dominio
    bandas_paciente: list[str] = []
    fortalezas: list[str] = []
    areas_apoyo: list[str] = []
    for r in resultados or []:
        nombre_test = r.get("nombre", r.get("test_id", ""))
        banda = r.get("clasificacion") or r.get("interpretacion", "")
        if not nombre_test:
            continue
        termino_claro = traducir_termino(nombre_test)
        banda_clara = banda_a_lenguaje_claro(banda)
        if banda in ("Superior", "Promedio Alto", "Promedio"):
            fortalezas.append(
                f"En {termino_claro}, tu rendimiento fue {banda_clara}."
            )
        elif banda in ("Promedio Bajo", "Bajo"):
            areas_apoyo.append(
                f"En {termino_claro}, tu rendimiento fue {banda_clara}. "
                "Esto se puede trabajar con práctica y apoyo."
            )
        elif banda == "Muy Bajo":
            areas_apoyo.append(
                f"En {termino_claro}, encontramos un rendimiento {banda_clara}. "
                "Es importante que converses con tu psicólogo/a sobre "
                "qué significa esto y qué apoyos podrían ayudarte."
            )
        if banda:
            bandas_paciente.append(banda)

    if not fortalezas and not areas_apoyo:
        que_encontramos = (
            "Aún no tenemos suficientes resultados para darte un resumen "
            "detallado. Conversa con tu psicólogo/a al respecto."
        )
    else:
        frases: list[str] = []
        if fortalezas:
            frases.append(
                "Las áreas donde te fue bien incluyen: " +
                " ".join(fortalezas[:3])
            )
        if areas_apoyo:
            frases.append(
                "Las áreas donde se recomienda trabajar incluyen: " +
                " ".join(areas_apoyo[:3])
            )
        que_encontramos = " ".join(frases)

    if recomendaciones:
        recs_paciente = []
        for r in recomendaciones[:5]:
            r_low = r.lower()
            if "escolar" in r_low or "colegio" in r_low:
                recs_paciente.append(
                    "En el colegio/academia: puede ser útil hablar con tus "
                    "profesores para explorar apoyos como tiempo extra en "
                    "exámenes o actividades adaptadas."
                )
            elif "terap" in r_low:
                recs_paciente.append(
                    "Sobre la terapia: continúa con tus sesiones según lo "
                    "acordado. Si tienes dudas, coméntalas con tu terapeuta."
                )
            elif "medic" in r_low or "psiquiatr" in r_low:
                recs_paciente.append(
                    "Sobre la consulta médica: si tu psicólogo/a lo sugiere, "
                    "agenda una cita con psiquiatría para discutir opciones "
                    "de tratamiento."
                )
            else:
                recs_paciente.append(
                    f"Recomendación: {r} (consulta con tu psicólogo/a para "
                    "detalles específicos)."
                )
        que_recomendamos = " ".join(recs_paciente[:4])
    else:
        que_recomendamos = (
            "Tu psicólogo/a te explicará las recomendaciones específicas "
            "para tu caso en la sesión de devolución. Algunas recomendaciones "
            "comunes incluyen: técnicas de estudio, estrategias de "
            "organización, o sesiones de seguimiento."
        )

    preguntas_frecuentes = [
        (
            "¿Mis resultados son permanentes?",
            "No necesariamente. El cerebro puede cambiar con el tiempo, "
            "especialmente con práctica y los apoyos adecuados. Los "
            "resultados que obtuviste son una foto del momento actual."
        ),
        (
            "¿Por qué algunos resultados son mejores que otros?",
            "Es completamente normal. Todas las personas tienen áreas donde "
            "son más fuertes y áreas donde pueden mejorar. Esto no significa "
            "que haya algo mal en ti."
        ),
        (
            "¿Necesito otro tipo de evaluaciones?",
            "Tu psicólogo/a te dirá si se necesitan otros estudios "
            "(por ejemplo, evaluación pedagógica, médica, o del lenguaje). "
            "No te preocupes si no entiendes algún término: puedes preguntar "
            "siempre."
        ),
    ]

    return {
        "saludo": saludo,
        "que_hicimos": que_hicimos,
        "que_encontramos": que_encontramos,
        "fortalezas": fortalezas,
        "areas_apoyo": areas_apoyo,
        "que_recomendamos": que_recomendamos,
        "preguntas_frecuentes": preguntas_frecuentes,
    }


# ═══════════════════════════════════════════════════════════════════
# F9.2 — 7 principios de redacción clínica (extraídos del plan maestro)
# ═══════════════════════════════════════════════════════════════════
# Estos 7 principios son DIFERENTES de los 7 principios éticos de
# PRINCIPIOS_NARRATIVOS (más arriba). Los de aquí son de ESTILO Y
# ESTRUCTURA del informe, basados en Sattler 2008, Eisman 1962, CONFIL
# 2012 y la práctica clínica estándar 2024 (APA Publications Manual 7th).
#
# Aplica SOLO a las variantes "profesionales" del informe
# (pro, pediatrico, medicolegal, junta_medica). La variante "paciente"
# usa lenguaje accesible (verificar_legible_paciente).
# ═══════════════════════════════════════════════════════════════════


PRINCIPIOS_REDACCION_2024 = [
    {
        "id": "R1",
        "titulo": "Bottom-up (de dominios a funciones, no de pruebas a dominios)",
        "descripcion": (
            "La organización debe ir de DOMINIOS a FUNCIONES, no al revés. "
            "❌ 'En la prueba WCST el paciente obtuvo X → interpretamos que "
            "tiene alteración en funciones ejecutivas'. "
            "✅ 'En el dominio de funciones ejecutivas se observa alteración "
            "en la capacidad de set-shifting, documentada con la prueba WCST'."
        ),
        "auditable_auto": False,
        "motivo_no_auto": "Estructura narrativa — el clínico decide el orden en su texto libre.",
    },
    {
        "id": "R2",
        "titulo": "En niños no usar 'conserva'; usar 'rinde acorde a lo esperado'",
        "descripcion": (
            "El término 'conserva' (de la escuela piagetiana) implica que algo "
            "se preserva respecto a un estado anterior. En neuropsicología "
            "infantil se prefiere 'rinde acorde a lo esperado para su edad y "
            "escolaridad' o 'dentro de los rangos esperados para su grupo "
            "normativo'. Aplica solo a informes con poblacion='infantil'."
        ),
        "auditable_auto": True,
        "motivo_no_auto": None,
    },
    {
        "id": "R3",
        "titulo": "Prefijo 'DIS-' en adultos para déficits",
        "descripcion": (
            "En informes de ADULTOS, los déficits se prefijan con 'DIS-' para "
            "diferenciarlos de variaciones del desarrollo (p. ej. 'función "
            "DIS-atencional' vs 'función atencional'). Esto facilita la "
            "lectura por otros profesionales y el seguimiento longitudinal. "
            "NO se aplica a niños (en ellos las variaciones son propias del "
            "desarrollo)."
        ),
        "auditable_auto": True,
        "motivo_no_auto": None,
    },
    {
        "id": "R4",
        "titulo": "No repetir información del paciente entre secciones",
        "descripcion": (
            "Cada mención del paciente en una sección debe aportar información "
            "nueva. ❌ 'El paciente, de 35 años, ingeniero...' repetido en 4 "
            "secciones. ✅ Datos sociodemográficos solo en la sección inicial; "
            "las secciones de resultados y análisis pueden usar 'el evaluado' "
            "o 'el paciente' sin re-listar la información."
        ),
        "auditable_auto": False,
        "motivo_no_auto": "Requiere análisis de coherencia global del texto, fuera del alcance del validador automático.",
    },
    {
        "id": "R5",
        "titulo": "Hablar de la FUNCIÓN no de la PRUEBA",
        "descripcion": (
            "❌ 'El paciente obtuvo puntaje bajo en WCST (X errores)' → "
            "❌ 'El puntaje en WCST fue de 30 (percentil 5)'. "
            "✅ 'El paciente presenta dificultades en funciones ejecutivas, "
            "particularmente en la capacidad de flexibilidad cognitiva y "
            "resolución de problemas, documentadas con un rendimiento "
            "significativamente bajo en tareas de set-shifting (WCST)."
        ),
        "auditable_auto": True,
        "motivo_no_auto": None,
    },
    {
        "id": "R6",
        "titulo": "Considerar desarrollo (no comparar 6 años con 16)",
        "descripcion": (
            "Los baremos siempre deben ser por edad (y escolaridad cuando "
            "aplique). Comparar un niño de 6 con baremos de 16 es un error "
            "metodológico grave. El informe debe mencionar el baremo "
            "utilizado para cada prueba."
        ),
        "auditable_auto": True,
        "motivo_no_auto": None,
    },
    {
        "id": "R7",
        "titulo": "Usar algoritmos diagnósticos como árbol (basado en práctica estándar)",
        "descripcion": (
            "El informe debe integrar los hallazgos cuantitativos en hipótesis "
            "diagnósticas siguiendo un árbol de decisión (criterios DSM-5-TR). "
            "Ejemplo: TDAH + IRP-bajo + IMT-bajo = screening positivo → "
            "correlación clínica. No diagnosticar sin (a) cruce del umbral "
            "clínico, (b) impacto funcional, (c) consistencia entre "
            "evaluadores, (d) duración significativa."
        ),
        "auditable_auto": False,
        "motivo_no_auto": "Depende del juicio clínico integral — no automatizable.",
    },
]


# Anti-marcadores para R2 (no usar "conserva" en niños)
_R2_ANTIMARCADORES = [
    r"\bconserva\b",
    r"\bpreserva\b",
    r"\bconservad[oa]\b",
]


# Marcadores de funciones (R5) — verbos que indican que el clínico está
# hablando de la FUNCIÓN (bien) y no solo del puntaje (mal).
_R5_MARCADORES_FUNCION = [
    r"\bcapacidad de\b",
    r"\bdificultad(es)? en\b",
    r"\bfunci[oó]n(es)?\s+(?:atencional|mnésica|ejecutiva|visuoespacial|verbal)\b",
    r"\brendimiento en\b",
    r"\bdesempe[ñn]o en\b",
    r"\bDIS-(?:atencional|mnésico|ejecutivo)\b",
    r"\bhabilidades?\s+de\b",
]


# Marcadores de baremos nombrados (R6) — para verificar que el informe
# cita los baremos por edad.
_R6_MARCADORES_BAREMOS = [
    r"\bbaremos?\s+(?:de|para|con|seg[uú]n)\b",
    r"\bNeuronorma\b",
    r"\bArango[- ]Lasprilla\b",
    r"\bWISC[- ]?IV\b",
    r"\bWAIS[- ]?III\b",
    r"\bforma\s+corta\b",
    r"\bpor\s+edad\b",
    r"\bgrupo\s+normativo\b",
    r"\bpara\s+su\s+edad\b",
]


def validar_principios_redaccion_2024(
    texto: str,
    *,
    poblacion_objetivo: str = "adulto_joven",
    edad: int = None,
    menciona_baremos: bool = None,
) -> dict:
    """
    F9.2 — Audita una narrativa contra los 7 principios de redacción 2024.

    Diferencia con ``validar_principios_narrativa``: aquí se audita el
    ESTILO y la ESTRUCTURA del texto (no la ética clínica).

    Parámetros
    ----------
    texto : str
        Narrativa completa del informe (sin el bloque de firma).
    poblacion_objetivo : str
        ``"infantil"`` | ``"adulto_joven"`` | ``"adulto_mayor"``.
    edad : int, opcional
        Edad del paciente — útil para heurísticas futuras.
    menciona_baremos : bool, opcional
        Si se pasa explícitamente, se usa para R6; si es None, se
        infiere del texto.

    Devuelve un dict con la misma estructura que
    ``validar_principios_narrativa``:
        - ``cumple``: bool
        - ``principios``: dict[id] → {titulo, estado, detalle, auditable_auto}
        - ``alertas``: list[str]
        - ``resumen``: str
    """
    import re

    texto_lower = (texto or "").lower()
    es_infantil = poblacion_objetivo == "infantil"
    es_adulto = poblacion_objetivo in ("adulto_joven", "adulto_mayor")

    principios: dict[str, dict] = {}

    # R1: Bottom-up — no auditable automáticamente
    principios["R1"] = {
        "titulo": PRINCIPIOS_REDACCION_2024[0]["titulo"],
        "estado": "no_aplica",
        "detalle": "Estructura narrativa — verificar manualmente que el orden va de dominios a funciones.",
        "auditable_auto": False,
    }

    # R2: No usar "conserva" en niños
    if es_infantil:
        matches = [p for p in _R2_ANTIMARCADORES if re.search(p, texto_lower, re.IGNORECASE)]
        if matches:
            principios["R2"] = {
                "titulo": PRINCIPIOS_REDACCION_2024[1]["titulo"],
                "estado": "revisar",
                "detalle": (
                    "Informe infantil contiene términos no recomendados ('conserva', "
                    "'preserva'). Preferir 'rinde acorde a lo esperado para su "
                    "edad' o 'dentro de los rangos esperados para su grupo "
                    "normativo'."
                ),
                "auditable_auto": True,
            }
        else:
            principios["R2"] = {
                "titulo": PRINCIPIOS_REDACCION_2024[1]["titulo"],
                "estado": "ok",
                "detalle": "Sin uso de 'conserva'/'preserva'. Lenguaje apropiado para infantil.",
                "auditable_auto": True,
            }
    else:
        principios["R2"] = {
            "titulo": PRINCIPIOS_REDACCION_2024[1]["titulo"],
            "estado": "no_aplica",
            "detalle": "R2 aplica solo a población infantil.",
            "auditable_auto": True,
        }

    # R3: Prefijo DIS- en adultos para déficits
    if es_adulto:
        # Buscar términos de déficit: 'déficit', 'alteración', 'disfunción'
        # precedidos o no de DIS-.
        deficit_terms = re.findall(
            r"\b(d[ée]ficit|alteraci[oó]n|disfunci[oó]n|disfuncion|problema)\s+"
            r"(atencional|mn[eé]sic[oa]|ejecutiv[oa]|visuoespacial|verbal|de\s+memoria)",
            texto_lower,
            re.IGNORECASE,
        )
        if not deficit_terms:
            principios["R3"] = {
                "titulo": PRINCIPIOS_REDACCION_2024[2]["titulo"],
                "estado": "no_aplica",
                "detalle": "No se mencionan déficits específicos para validar el prefijo DIS-.",
                "auditable_auto": True,
            }
        else:
            with_dis = sum(1 for m in re.finditer(
                r"\bDIS-(?:atencional|mn[eé]sic[oa]|ejecutiv[oa]|visuoespacial|verbal)",
                texto, re.IGNORECASE,
            ))
            ratio = with_dis / max(1, len(deficit_terms))
            if ratio >= 0.5:
                principios["R3"] = {
                    "titulo": PRINCIPIOS_REDACCION_2024[2]["titulo"],
                    "estado": "ok",
                    "detalle": f"Prefijo DIS- usado en {with_dis}/{len(deficit_terms)} menciones de déficit.",
                    "auditable_auto": True,
                }
            else:
                principios["R3"] = {
                    "titulo": PRINCIPIOS_REDACCION_2024[2]["titulo"],
                    "estado": "revisar",
                    "detalle": (
                        f"Prefijo DIS- usado en {with_dis}/{len(deficit_terms)} déficits. "
                        "En adultos, prefijar consistentemente con DIS- para diferenciar "
                        "de variaciones del desarrollo."
                    ),
                    "auditable_auto": True,
                }
    else:
        principios["R3"] = {
            "titulo": PRINCIPIOS_REDACCION_2024[2]["titulo"],
            "estado": "no_aplica",
            "detalle": "R3 aplica solo a adultos.",
            "auditable_auto": True,
        }

    # R4: No repetir información del paciente entre secciones
    principios["R4"] = {
        "titulo": PRINCIPIOS_REDACCION_2024[3]["titulo"],
        "estado": "no_aplica",
        "detalle": "Requiere análisis de coherencia global — verificar manualmente.",
        "auditable_auto": False,
    }

    # R5: Hablar de la FUNCIÓN no de la PRUEBA
    # Detectar si el texto menciona pruebas por su nombre.
    pruebas_mencionadas = re.findall(
        r"\b(WCST|Stroop|TMT[- ]?[AB]|Trail\s+Making|WISC|WAIS|MoCA|MMSE|Test\s+de\s+\w+|Cubos\s+de\s+Kohs|Figura\s+Compleja\s+de\s+Rey)\b",
        texto, re.IGNORECASE,
    )
    if not pruebas_mencionadas:
        principios["R5"] = {
            "titulo": PRINCIPIOS_REDACCION_2024[4]["titulo"],
            "estado": "no_aplica",
            "detalle": "No se mencionan pruebas específicas en el texto.",
            "auditable_auto": True,
        }
    else:
        # ¿Hay función verbalizada junto con la mención de la prueba?
        funciones_count = sum(1 for p in _R5_MARCADORES_FUNCION if re.search(p, texto, re.IGNORECASE))
        if funciones_count >= 1:
            principios["R5"] = {
                "titulo": PRINCIPIOS_REDACCION_2024[4]["titulo"],
                "estado": "ok",
                "detalle": f"Mención de {len(pruebas_mencionadas)} pruebas con {funciones_count} referencias a funciones.",
                "auditable_auto": True,
            }
        else:
            principios["R5"] = {
                "titulo": PRINCIPIOS_REDACCION_2024[4]["titulo"],
                "estado": "revisar",
                "detalle": (
                    f"Se mencionan {len(pruebas_mencionadas)} pruebas por nombre pero no se "
                    "describe la FUNCIÓN afectada. Preferir 'dificultad en la capacidad de…' "
                    "sobre 'puntaje bajo en…'."
                ),
                "auditable_auto": True,
            }

    # R6: Considerar desarrollo (citar baremos por edad)
    if menciona_baremos is None:
        menciona_baremos = any(re.search(p, texto, re.IGNORECASE) for p in _R6_MARCADORES_BAREMOS)
    if menciona_baremos:
        principios["R6"] = {
            "titulo": PRINCIPIOS_REDACCION_2024[5]["titulo"],
            "estado": "ok",
            "detalle": "El informe cita baremos por edad (Neuronorma, WISC-IV, WAIS-III o equivalente).",
            "auditable_auto": True,
        }
    else:
        principios["R6"] = {
            "titulo": PRINCIPIOS_REDACCION_2024[5]["titulo"],
            "estado": "revisar",
            "detalle": "No se identifica cita explícita de baremos por edad. Agregar referencia al baremo usado (p. ej. 'baremos de Neuronorma Colombia, Arango-Lasprilla & Rivera 2017').",
            "auditable_auto": True,
        }

    # R7: Algoritmos diagnósticos como árbol — no auditable
    principios["R7"] = {
        "titulo": PRINCIPIOS_REDACCION_2024[6]["titulo"],
        "estado": "no_aplica",
        "detalle": "Depende del juicio clínico integral — verificar manualmente.",
        "auditable_auto": False,
    }

    # Resumen
    alertas = [
        f"[{pid}] {p['titulo']}: {p['detalle']}"
        for pid, p in principios.items()
        if p["estado"] == "revisar"
    ]
    cumple = all(p["estado"] in ("ok", "no_aplica") for p in principios.values())

    resumen_partes = []
    for pid in ["R1", "R2", "R3", "R4", "R5", "R6", "R7"]:
        p = principios[pid]
        icono = {"ok": "✓", "revisar": "⚠", "no_aplica": "—"}[p["estado"]]
        resumen_partes.append(f"{icono} {pid} {p['titulo'][:50]}")
    resumen = "  ".join(resumen_partes)

    return {
        "cumple": cumple,
        "principios": principios,
        "alertas": alertas,
        "resumen": resumen,
    }


# ═══════════════════════════════════════════════════════════════════
# F9.3 — Cláusulas legales obligatorias en el encabezado del PDF
# ═══════════════════════════════════════════════════════════════════
# Bloques fijos que aparecen en el encabezado y pie de TODAS las
# variantes profesionales. Se inyectan en el bloque de firma cuando
# se genera el PDF.
# ═══════════════════════════════════════════════════════════════════


CLAUSULAS_INFORME_PROFESIONAL = {
    "encabezado": (
        "INFORME NEUROPSICOLÓGICO CONFIDENCIAL — DOCUMENTO CLÍNICO LEGAL"
    ),
    "declaracion_confidencialidad": (
        "Este documento contiene información clínica protegida por la Ley 1581 "
        "de 2012 (Habeas Data), la Resolución 1995 de 1999 (Historia Clínica) y "
        "el artículo 36 de la Ley 1090 de 2006 (Secreto Profesional del "
        "Psicólogo). Su reproducción, distribución o divulgación no autorizada "
        "está sujeta a las sanciones legales vigentes."
    ),
    "responsabilidad_profesional": (
        "El presente informe se emite bajo la responsabilidad profesional del "
        "psicólogo firmante, quien certifica que la evaluación fue realizada "
        "conforme a los estándares técnicos y éticos de la práctica "
        "neuropsicológica colombiana."
    ),
    "uso_previsto_default": "Uso clínico",
    "limitaciones_default": (
        "Evaluación aplicada en una sola sesión. Los resultados describen el "
        "rendimiento del paciente en el momento de la evaluación y pueden "
        "verse influenciados por factores transitorios (fatiga, ansiedad, "
        "medicación, condiciones de salud)."
    ),
}


def construir_bloque_legal_encabezado(
    *,
    nombre_profesional: str = "",
    tarjeta_profesional: str = "",
    universidad: str = "",
    resolucion: str = "",
    nombre_paciente: str = "",
    edad_display: str = "",
    fecha_evaluacion: str = "",
    objetivo: str = "",
    uso_previsto: str = None,
    limitaciones: str = None,
    lugar: str = "",
) -> str:
    """
    F9.3 — Construye el bloque legal/legal del encabezado (encabezado +
    identificación del profesional + identificación del paciente + objetivo +
    uso previsto + limitaciones + fecha/lugar).

    Pensado para inyectarse al inicio del PDF profesional.
    """
    partes: list[str] = []
    partes.append(CLAUSULAS_INFORME_PROFESIONAL["encabezado"])
    partes.append("")
    partes.append(CLAUSULAS_INFORME_PROFESIONAL["declaracion_confidencialidad"])
    partes.append("")
    partes.append("Profesional responsable:")
    partes.append(f"  Nombre: {nombre_profesional or '—'}")
    partes.append(f"  Tarjeta Profesional: {tarjeta_profesional or '—'}")
    partes.append(f"  Universidad: {universidad or '—'}")
    partes.append(f"  Resolución: {resolucion or '—'}")
    partes.append("")
    partes.append("Paciente:")
    partes.append(f"  Nombre: {nombre_paciente or '—'}")
    partes.append(f"  Edad: {edad_display or '—'}")
    partes.append(f"  Fecha de evaluación: {fecha_evaluacion or '—'}")
    partes.append("")
    partes.append(f"Objetivo del informe: {objetivo or '—'}")
    partes.append(
        f"Uso previsto: {uso_previsto or CLAUSULAS_INFORME_PROFESIONAL['uso_previsto_default']}"
    )
    partes.append(
        f"Limitaciones: {limitaciones or CLAUSULAS_INFORME_PROFESIONAL['limitaciones_default']}"
    )
    partes.append(f"Lugar: {lugar or '—'}")
    partes.append("")
    partes.append(CLAUSULAS_INFORME_PROFESIONAL["responsabilidad_profesional"])
    return "\n".join(partes)



