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

import json
import math
from collections import defaultdict
from collections.abc import Sequence
from pathlib import Path

from .helpers import human_test_name

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
        bucket[dom]["tests"].append(
            {
                "nombre": human_test_name(
                    r.get("test_id", "") or "",
                    r.get("test_nombre", "") or "",
                ),
                "z": z,
                "pd": r.get("puntaje_bruto"),
                "pe": r.get("puntaje_escalar"),
            }
        )
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
        "indcomver": "ICV",
        "icv": "ICV",
        "indrazper": "IRP",
        "irp": "IRP",
        "icp": "IRP",
        "indmemtra": "IMT",
        "imt": "IMT",
        "indvelpro": "IVP",
        "ivp": "IVP",
        "tot": "CIT",
        "cit": "CIT",
        "indtot": "CIT",
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
            chunks.append("El perfil neuropsicológico evidencia debilidades en: " + "; ".join(sev_chunks) + ".")
        if strong:
            ch_strong = []
            for d, info in strong:
                qualifier = "muy" if info["mean_z"] >= FUERTE_MARCADO_Z else ""
                tag = f"{qualifier} alto, Z̄={info['mean_z']:+.1f}".strip()
                ch_strong.append(f"{d.lower()} ({tag})")
            chunks.append(
                "Por su parte, destacan como áreas preservadas o por encima del promedio: " + "; ".join(ch_strong) + "."
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
        [r for r in resultados if r.get("z_equivalente") is not None and r.get("tipo_metrica") != "ci"],
        key=lambda r: r["z_equivalente"],
    )
    if all_results and all_results[0]["z_equivalente"] <= DEBIL_Z:
        critical = all_results[:3]
        items = []
        for r in critical:
            if r.get("z_equivalente") > DEBIL_Z:
                break
            nombre = human_test_name(
                r.get("test_id", "") or "",
                r.get("test_nombre", "") or "",
            )
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


def build_executive_summary(
    resultados: Sequence[dict],
    *,
    paciente_nombre: str = "El paciente",
) -> dict[str, str]:
    """Resumen ejecutivo en pirámide invertida: 1 frase, 2-3 bullets, 1 implicación.

    Estructura:
      - ``conclusion``: el hallazgo más importante (CI o perfil global).
      - ``hallazgos``: 2-3 viñetas con puntos clave.
      - ``implicacion``: frase sobre el impacto funcional / curso de acción.
    """
    indices = _extract_ci_indices(resultados)
    domains = _domain_summary(resultados)

    if "CIT" in indices:
        cit = indices["CIT"]
        cat = _interpret_ci_range(cit)
        conclusion = f"{paciente_nombre} obtuvo un CIT de {cit} ({cat.lower()}), con un perfil "
        # Asimetría vs homogeneidad
        rest = {k: v for k, v in indices.items() if k != "CIT"}
        if rest and max(rest.values()) - min(rest.values()) >= 12:
            lo_k, lo_v = min(rest.items(), key=lambda kv: kv[1])
            conclusion += (
                f"asimétrico: {lo_k}={lo_v} es el índice más bajo. El CIT resume pero no captura la variabilidad."
            )
        else:
            conclusion += "homogéneo entre los índices compuestos."
    elif indices:
        idx_str = ", ".join(f"{k}={v}" for k, v in sorted(indices.items()))
        conclusion = f"Perfil de {paciente_nombre}: índices {idx_str}."
    else:
        # Sin CI: basarse en dominios
        if domains:
            mean_z_global = sum(d["mean_z"] for d in domains.values()) / len(domains)
            conclusion = (
                f"Perfil neuropsicológico global: Z̄={mean_z_global:+.1f}σ sobre {len(domains)} dominios evaluados."
            )
        else:
            conclusion = "Perfil neuropsicológico sin datos suficientes para un resumen global."

    # Hallazgos clave: top 1 debilidad + top 1 fortaleza
    hallazgos: list[str] = []
    if domains:
        weak = sorted(
            [(d, info) for d, info in domains.items() if info["mean_z"] <= DEBIL_Z],
            key=lambda x: x[1]["mean_z"],
        )
        strong = sorted(
            [(d, info) for d, info in domains.items() if info["mean_z"] >= FUERTE_Z],
            key=lambda x: -x[1]["mean_z"],
        )
        if weak:
            d, info = weak[0]
            sev = "severamente" if info["mean_z"] <= DEBIL_SEVERO_Z else "moderadamente"
            hallazgos.append(f"{d} {sev} descendido (Z̄={info['mean_z']:+.1f}σ)")
        if strong:
            d, info = strong[0]
            hallazgos.append(f"{d} preservado (Z̄={info['mean_z']:+.1f}σ)")
        if not weak and not strong:
            hallazgos.append("Rendimiento dentro del rango esperado en todos los dominios.")

    # Implicación funcional
    if "CIT" in indices and indices["CIT"] < 80:
        implicacion = (
            "El perfil sugiere necesidad de apoyos específicos en las áreas "
            "más descendidas; se recomienda intervención focalizada."
        )
    elif domains and any(d["mean_z"] <= DEBIL_SEVERO_Z for d in domains.values()):
        implicacion = (
            "Se recomienda intervención prioritaria en el dominio con mayor "
            "descenso, con seguimiento cercano de la evolución."
        )
    elif domains and any(d["mean_z"] <= DEBIL_Z for d in domains.values()):
        implicacion = (
            "Se sugiere intervención dirigida al dominio descendido, con monitoreo de respuesta a tratamiento."
        )
    else:
        implicacion = "El perfil es consistente con funcionalidad preservada; se recomienda seguimiento de rutina."

    return {
        "conclusion": conclusion.strip(),
        "hallazgos": hallazgos,
        "implicacion": implicacion,
    }


# ──────────────────────────────────────────────────────────
# Reservorio: sugerencia de cuadros clínicos por perfil
# ──────────────────────────────────────────────────────────

_RESERVORIO_PATH = Path(__file__).parent.parent.parent / "domain" / "data" / "reservorio_recomendaciones.json"


def _load_reservorio() -> dict:
    """Carga el reservorio clínico (lazy, con cache en módulo)."""
    if not hasattr(_load_reservorio, "_cache"):
        try:
            with open(_RESERVORIO_PATH, encoding="utf-8") as f:
                _load_reservorio._cache = json.load(f)  # type: ignore[attr-defined]
        except (OSError, ValueError):
            _load_reservorio._cache = {"grupos": {}}  # type: ignore[attr-defined]
    return _load_reservorio._cache  # type: ignore[attr-defined]


def _edad_poblacion(resultados: Sequence[dict], poblacion: str = "") -> str:
    """Determina la población del paciente.

    Prioriza el parámetro explícito ``poblacion`` (viene del ReportData);
    si está vacío, busca el campo ``poblacion`` en el primer resultado;
    si tampoco, devuelve ``adulto`` (default conservador).
    """
    if poblacion:
        return poblacion
    for r in resultados:
        p = r.get("poblacion")
        if p:
            return p
    return "adulto"


def sugerir_cuadros_clinicos(
    resultados: Sequence[dict],
    *,
    poblacion: str = "",
    max_cuadros: int = 2,
) -> list[dict]:
    """Detecta los cuadros clínicos más probables según el perfil del paciente.

    Estrategia heurística (orden de prioridad):
      1. Si Grober o memoria verbal cae en déficit severo en AM → demencia_alzheimer.
      2. Si el perfil es predominantemente subcortical (memoria+atención+FFE) en AM
         → dcl_amnesico.
      3. Si el CI total está en rango de discapacidad → discapacidad_cognitiva/discapacidad_intelectual_adulto.
      4. Si hay pruebas de cribado TDAH y atención/FEE están descendidas → tdah.
      5. Si hay screening de ansiedad o depresión positivos → depresion_ansiedad_tdah o ansiedad.
      6. Si el perfil es normal → perfil_normal / generales (prevención).

    Retorna una lista de ``{grupo, cuadro_id, label, recomendaciones}``.
    """
    resv = _load_reservorio()
    grupos = resv.get("grupos", {})
    poblacion = _edad_poblacion(resultados, poblacion=poblacion)
    if poblacion == "infantil":
        grupo_key = "infantil"
    elif poblacion == "adulto_mayor":
        grupo_key = "adulto_mayor"
    else:
        grupo_key = "adulto"

    # Datos clave del perfil
    cit = None
    for r in resultados:
        if r.get("tipo_metrica") == "ci" and r.get("test_id", "").endswith("Tot"):
            cit = r.get("puntaje_escalar")
            break
    if cit is None:
        for r in resultados:
            if r.get("tipo_metrica") == "ci":
                cit = r.get("puntaje_escalar")
                break

    domains = _domain_summary(resultados)
    weak_domains = {d for d, info in domains.items() if info["mean_z"] <= DEBIL_Z}
    severe_domains = {d for d, info in domains.items() if info["mean_z"] <= DEBIL_SEVERO_Z}

    # Detección de "memoria descendida" por test_id (Grober, Rey, WMS, etc.)
    # en lugar de depender del dominio_cognitivo (que a veces es "General").
    _MEMORIA_TESTS = (
        "Grober",
        "Rey",
        "WMS",
        "CVLT",
        "TAVEC",
        "TOMM",
        "MemoriaVerbal",
        "MemoriaVisual",
        "Recuerdo",
        "Evocacion",
        "Evocación",
    )
    mem_zs: list[float] = []
    for r in resultados:
        tid = str(r.get("test_id", ""))
        tnom = str(r.get("test_nombre", ""))
        z = r.get("z_equivalente")
        if z is None or r.get("tipo_metrica") == "ci":
            continue
        if any(tok in tid for tok in _MEMORIA_TESTS) or any(tok in tnom for tok in _MEMORIA_TESTS):
            mem_zs.append(z)
    mem_z = (sum(mem_zs) / len(mem_zs)) if mem_zs else None

    # Detección de screening TDAH (SNAP-IV, ASRS, Conners)
    _TDAH_SCREEN = ("SNAP", "ASRS", "Conners", "WURS", "Wender")
    has_tdah_screen = any(
        any(tok in str(r.get("test_id", "")) for tok in _TDAH_SCREEN)
        or any(tok in str(r.get("test_nombre", "")) for tok in _TDAH_SCREEN)
        for r in resultados
    )

    # Detección de screening ansiedad/depresión
    _DEP_SCREEN = ("BDI", "PHQ", "HADS", "Hamilton", "Beck", "Yesavage", "GDS")
    has_dep_screen = any(
        any(tok in str(r.get("test_id", "")) for tok in _DEP_SCREEN)
        or any(tok in str(r.get("test_nombre", "")) for tok in _DEP_SCREEN)
        for r in resultados
    )

    # Heurísticas por población
    matches: list[tuple[int, str, str]] = []  # (prioridad, cuadro_id, grupo_key)

    if grupo_key == "adulto_mayor":
        # Memoria severamente descendida + 2+ dominios severos → Alzheimer probable
        if mem_z is not None and mem_z <= DEBIL_SEVERO_Z and len(severe_domains) >= 2:
            matches.append((1, "demencia_alzheimer", grupo_key))
        # Memoria descendida + atención descendida → DCL amnésico
        elif mem_z is not None and mem_z <= DEBIL_Z and "Atención" in weak_domains:
            matches.append((2, "dcl_amnesico", grupo_key))
        # FFE severas + lenguaje descendido → FTD probable
        elif "Funciones Ejecutivas" in severe_domains and "Lenguaje" in weak_domains:
            matches.append((3, "ftd", grupo_key))
        # Screening depresión con perfil cognitivo descendido
        elif has_dep_screen and len(weak_domains) >= 2:
            matches.append((4, "desgaste_cuidador", grupo_key))
        # FFE y ≥3 dominios descendidos → intervención FFE
        elif "Funciones Ejecutivas" in weak_domains and len(weak_domains) >= 3:
            matches.append((5, "ffee_adulto_mayor", grupo_key))
        # Memoria descendida → recomendaciones específicas de memoria
        elif mem_z is not None and mem_z <= DEBIL_Z:
            matches.append((6, "memoria_demencia", grupo_key))
        elif not weak_domains:
            matches.append((99, "perfil_normal", grupo_key))
        else:
            matches.append((50, "generales", grupo_key))

    elif grupo_key == "infantil":
        # Discapacidad intelectual
        if cit is not None and cit < 70:
            matches.append((1, "discapacidad_cognitiva", grupo_key))
        elif cit is not None and 70 <= cit < 80:
            matches.append((2, "discapacidad_cognitiva", grupo_key))
        # TDAH: atención y FEE descendidas, o screening positivo
        elif has_tdah_screen and ("Atención" in weak_domains or "Funciones Ejecutivas" in weak_domains):
            matches.append((3, "tdah", grupo_key))
        elif "Atención" in weak_domains and "Funciones Ejecutivas" in weak_domains:
            matches.append((4, "tdah", grupo_key))
        # Dislexia / Discalculia
        elif any("compr" in d.lower() or "lect" in d.lower() for d in weak_domains):
            matches.append((5, "dislexia", grupo_key))
        # Ansiedad: screening positivo sin otro cuadro claro
        elif has_dep_screen and len(weak_domains) <= 2:
            matches.append((6, "ansiedad", grupo_key))
        elif "Funciones Ejecutivas" in weak_domains and len(weak_domains) == 1:
            matches.append((7, "ansiedad", grupo_key))
        # Trastornos visoespaciales / motores
        elif "Razonamiento Perceptual" in weak_domains or "Visoconstrucción" in weak_domains:
            matches.append((8, "trastornos_espaciales_motores", grupo_key))

    else:  # adulto
        if cit is not None and cit < 70:
            matches.append((1, "discapacidad_intelectual_adulto", grupo_key))
        # Depresión / ansiedad / TDAH adulto
        if has_dep_screen and ("Atención" in weak_domains and "Funciones Ejecutivas" in weak_domains):
            matches.append((2, "depresion_ansiedad_tdah", grupo_key))
        # TDAH adulto aislado
        elif has_tdah_screen and "Atención" in weak_domains:
            matches.append((3, "depresion_ansiedad_tdah", grupo_key))
        # Vascular
        if len(severe_domains) >= 2 and "Velocidad de Procesamiento" in weak_domains:
            matches.append((4, "riesgo_vascular", grupo_key))
        # TCE: memoria severamente descendida + atención
        if mem_z is not None and mem_z <= DEBIL_SEVERO_Z and "Atención" in weak_domains:
            matches.append((5, "tce", grupo_key))
        # Motores
        if "Velocidad de Procesamiento" in severe_domains and "Razonamiento Perceptual" in weak_domains:
            matches.append((6, "trastornos_motores_adulto", grupo_key))

    if not matches:
        # Fallback: ninguno
        return []

    # Ordenar por prioridad
    matches.sort(key=lambda x: x[0])
    selected = []
    for _, cuadro_id, gk in matches[:max_cuadros]:
        grupo = grupos.get(gk, {})
        cuadros = grupo.get("cuadros", {})
        cuadro = cuadros.get(cuadro_id)
        if cuadro:
            selected.append(
                {
                    "grupo": gk,
                    "grupo_label": grupo.get("label", gk),
                    "cuadro_id": cuadro_id,
                    "label": cuadro.get("label", cuadro_id),
                    "recomendaciones": cuadro.get("recomendaciones", []),
                }
            )
    return selected


# ──────────────────────────────────────────────────────────
# Glosario de pruebas administradas
# ──────────────────────────────────────────────────────────
#
# Descripciones operativas breves (1-2 líneas) que aparecen en el
# Anexo del informe. Sirven para que un clínico receptor o un familiar
# entienda qué mide cada prueba sin consultar el manual. Se actualiza
# manualmente con cada baremo nuevo integrado.

GLOSARIO_PRUEBAS: dict[str, dict[str, str]] = {
    # ── Wechsler infantil (WISC-IV) ──
    "NiWiscDC": {
        "nombre": "WISC-IV Dígitos en orden directo",
        "desc": "Span atencional directo: repetición de dígitos en el mismo orden. Evalúa atención y memoria de trabajo fonológica.",
    },
    "NiWiscSem": {
        "nombre": "WISC-IV Dígitos en orden inverso",
        "desc": "Span atencional inverso: repetición de dígitos en orden inverso. Evalúa memoria de trabajo y manipulación mental.",
    },
    "NiWiscVoc": {
        "nombre": "WISC-IV Vocabulario",
        "desc": "Definición de palabras. Evalúa comprensión verbal, riqueza léxica y concepto verbal.",
    },
    "NiWiscLN": {
        "nombre": "WISC-IV Letras-Números",
        "desc": "Intercalar letras y números en orden. Evalúa memoria de trabajo, secuenciación y atención dividida.",
    },
    "NiWiscCl": {
        "nombre": "WISC-IV Claves",
        "desc": "Transcribir símbolos bajo presión de tiempo. Evalúa velocidad de procesamiento, coordinación visomotora y atención.",
    },
    "NiWiscAri": {
        "nombre": "WISC-IV Aritmética",
        "desc": "Problemas aritméticos verbales con tiempo. Evalúa razonamiento cuantitativo, atención y memoria de trabajo.",
    },
    # ── Índices compuestos WISC-IV ──
    "NiWISCIndComVer": {
        "nombre": "WISC-IV Índice Comprensión Verbal",
        "desc": "Índice compuesto que resume razonamiento verbal, comprensión y conocimiento general.",
    },
    "NiWISCIndRazPer": {
        "nombre": "WISC-IV Índice Razonamiento Perceptual",
        "desc": "Índice compuesto que resume razonamiento no verbal, visualización y procesamiento espacial.",
    },
    "NiWISCIndMemTra": {
        "nombre": "WISC-IV Índice Memoria de Trabajo",
        "desc": "Índice compuesto que evalúa la capacidad de retener y manipular información temporalmente.",
    },
    "NiWISCIndVelPro": {
        "nombre": "WISC-IV Índice Velocidad de Procesamiento",
        "desc": "Índice compuesto que evalúa la velocidad para escanear, escribir y copiar información simple.",
    },
    "NiWISCTot": {
        "nombre": "WISC-IV Cociente Intelectual Total",
        "desc": "Síntesis de los cuatro índices compuestos. Es la medida más global del funcionamiento intelectual.",
    },
    # ── Wechsler adulto (WAIS-III) ──
    "AdWAISA": {
        "nombre": "WAIS-III Aritmética",
        "desc": "Problemas aritméticos cronometrados. Evalúa razonamiento cuantitativo, atención y memoria de trabajo.",
    },
    "AdWAISC": {
        "nombre": "WAIS-III Comprensión",
        "desc": "Resolución de problemas sociales prácticos. Evalúa juicio social, conocimiento práctico y razonamiento verbal.",
    },
    "AdWAISCC": {
        "nombre": "WAIS-III Claves de Símbolos",
        "desc": "Transcribir símbolos bajo presión de tiempo. Evalúa velocidad de procesamiento, aprendizaje asociativo y coordinación.",
    },
    "AdWAISFI": {
        "nombre": "WAIS-III Figuras Incompletas",
        "desc": "Identificar partes faltantes en figuras. Evalúa percepción visual, concentración y razonamiento perceptual.",
    },
    "AdWAISHI": {
        "nombre": "WAIS-III Historias",
        "desc": "Recuerdo de historias narradas. Evalúa memoria auditiva verbal y organización semántica.",
    },
    "AdWAISI": {
        "nombre": "WAIS-III Información",
        "desc": "Preguntas de conocimiento general. Evalúa cultura general, memoria de largo plazo y comprensión verbal.",
    },
    "AdWAISL": {
        "nombre": "WAIS-III Letras-Números",
        "desc": "Intercalar letras y números en orden. Evalúa memoria de trabajo, atención dividida y secuenciación.",
    },
    "AdWAISRO": {
        "nombre": "WAIS-III Diseño con Cubos (R.O.)",
        "desc": "Reproducir diseños con cubos. Evalúa visualización espacial, razonamiento perceptual y coordinación visomotora.",
    },
    "AdWAISV": {
        "nombre": "WAIS-III Vocabulario",
        "desc": "Definición de palabras. Evalúa comprensión verbal, riqueza léxica y concepto verbal.",
    },
    # ── Índices compuestos WAIS-III ──
    "AdWAISICV": {
        "nombre": "WAIS-III Índice Comprensión Verbal",
        "desc": "Índice compuesto que resume razonamiento verbal, comprensión y conocimiento.",
    },
    "AdWAISICP": {
        "nombre": "WAIS-III Índice Razonamiento Perceptual",
        "desc": "Índice compuesto que resume razonamiento no verbal y procesamiento espacial.",
    },
    "AdWAISIMT": {
        "nombre": "WAIS-III Índice Memoria de Trabajo",
        "desc": "Índice compuesto que evalúa retención y manipulación temporal de información.",
    },
    "AdWAISIVP": {
        "nombre": "WAIS-III Índice Velocidad de Procesamiento",
        "desc": "Índice compuesto que evalúa velocidad de escaneo y respuesta.",
    },
    "AdWAISEMan": {
        "nombre": "WAIS-III Índice Manipulación Mental",
        "desc": "Alias del Índice Memoria de Trabajo cuando se enfatiza la manipulación.",
    },
    "AdWAISTot": {
        "nombre": "WAIS-III Cociente Intelectual Total",
        "desc": "Síntesis de los cuatro índices compuestos. Medida global del funcionamiento intelectual.",
    },
    # ── Memoria: Grober-Buschke ──
    "ViGroberRLT": {
        "nombre": "Grober-Buschke Recuerdo Libre Total",
        "desc": "Suma de palabras recordadas en ensayo libre a lo largo de 3 ensayos. Evalúa codificación y consolidación de memoria verbal.",
    },
    "ViGroberMC_Tot": {
        "nombre": "Grober-Buschke Memoria Total (Rec + Recon)",
        "desc": "Recuerdo total (libre + clave) en cada ensayo. Evalúa capacidad máxima de recuperación con y sin clave.",
    },
    "ViGroberML_Tot": {
        "nombre": "Grober-Buschke Memoria Libre Total",
        "desc": "Recuerdo libre acumulado en los 3 ensayos. Evalúa aprendizaje y consolidación verbal.",
    },
    "ViGroberRT": {
        "nombre": "Grober-Buschke Recuerdo Total",
        "desc": "Recuerdo total (libre + clave) en el ensayo de evocación diferida. Evalúa memoria a largo plazo.",
    },
    # ── Memoria: Rey (AdFCRO_Rey) ──
    "AdFCRO_Rey": {
        "nombre": "Rey-Osterrieth Figura Compleja — Copia y Recuerdo",
        "desc": "Copia y reproducción diferida de la figura de Rey. Evalúa construcción visual, memoria visual y organización perceptual.",
    },
    # ── Atención: TMT ──
    "NiTMTA": {
        "nombre": "Trail Making Test A",
        "desc": "Unir números en orden ascendente. Evalúa atención visual, búsqueda visual y velocidad psicomotora.",
    },
    "NiTMTB": {
        "nombre": "Trail Making Test B",
        "desc": "Alternar entre números y letras. Evalúa atención dividida, flexibilidad cognitiva y función ejecutiva.",
    },
    "AdTMT_AB": {
        "nombre": "Trail Making Test A y B",
        "desc": "Versión adulta del TMT. A: atención sostenida. B: alternancia y flexibilidad cognitiva.",
    },
    "ViTMTA": {
        "nombre": "Trail Making Test A (AM)",
        "desc": "TMT-A baremado para adulto mayor. Evalúa atención, búsqueda visual y velocidad psicomotora.",
    },
    "ViTMTB": {
        "nombre": "Trail Making Test B (AM)",
        "desc": "TMT-B baremado para adulto mayor. Evalúa flexibilidad cognitiva y atención dividida.",
    },
    # ── Span dígitos ──
    "NiSpaDC": {
        "nombre": "Span Dígitos Directo",
        "desc": "Repetición de dígitos en orden directo. Evalúa span atencional y memoria de trabajo fonológica.",
    },
    "NiSpaDI": {
        "nombre": "Span Dígitos Inverso",
        "desc": "Repetición de dígitos en orden inverso. Evalúa memoria de trabajo y manipulación mental.",
    },
    "AdSpaDC": {
        "nombre": "Span Dígitos Directo (Ad)",
        "desc": "Versión adulta del span de dígitos directo. Evalúa atención y memoria de trabajo.",
    },
    "AdSpaDI": {
        "nombre": "Span Dígitos Inverso (Ad)",
        "desc": "Versión adulta del span de dígitos inverso. Evalúa memoria de trabajo.",
    },
    # ── Fluidez verbal ──
    "AdFluidezAnimales": {
        "nombre": "Fluidez Verbal Semántica — Animales",
        "desc": "Producir nombres de animales en 1 minuto. Evalúa lenguaje, fluencia semántica y acceso al léxico.",
    },
    "AdFluidezFrutas": {
        "nombre": "Fluidez Verbal Semántica — Frutas",
        "desc": "Producir nombres de frutas en 1 minuto. Evalúa acceso léxico-semántico.",
    },
    "AdFluidezLetraF": {
        "nombre": "Fluidez Verbal Fonológica — F",
        "desc": "Palabras que empiezan por F. Evalúa fluencia fonológica, búsqueda activa y control ejecutivo.",
    },
    "AdFluidezLetraA": {
        "nombre": "Fluidez Verbal Fonológica — A",
        "desc": "Palabras que empiezan por A. Evalúa fluencia fonológica.",
    },
    "AdFluidezLetraS": {
        "nombre": "Fluidez Verbal Fonológica — S",
        "desc": "Palabras que empiezan por S. Evalúa fluencia fonológica.",
    },
    "NiFluidezAnimales": {
        "nombre": "Fluidez Verbal Semántica — Animales (Ni)",
        "desc": "Versión infantil de la fluencia semántica de animales.",
    },
    "NiFluidezFrutas": {
        "nombre": "Fluidez Verbal Semántica — Frutas (Ni)",
        "desc": "Versión infantil de la fluencia semántica de frutas.",
    },
    # ── Stroop ──
    "AdStroopC": {
        "nombre": "Test de Stroop — Color",
        "desc": "Nombrar el color de la tinta de palabras incongruentes. Evalúa inhibición y control atencional.",
    },
    "AdStroopP": {
        "nombre": "Test de Stroop — Palabra",
        "desc": "Leer palabras de colores. Evalúa velocidad de lectura automatizada.",
    },
    "AdStroopPC": {
        "nombre": "Test de Stroop — Palabra-Color",
        "desc": "Versión completa del Stroop con condiciones de lectura, color e interferencia.",
    },
    # ── Depresión y ansiedad (cribado) ──
    "AdBeck": {
        "nombre": "Inventario de Depresión de Beck (BDI-II)",
        "desc": "Auto-reporte de 21 ítems sobre síntomas depresivos en las últimas 2 semanas. Evalúa severidad de depresión.",
    },
    "AdBDI": {"nombre": "BDI-II (alias)", "desc": "Alias del Inventario de Depresión de Beck-II."},
    "AdPHQ9": {
        "nombre": "PHQ-9",
        "desc": "Cuestionario de 9 ítems sobre sintomatología depresiva según criterios DSM-IV. Útil en atención primaria.",
    },
    "ViYesavage": {
        "nombre": "Escala de Depresión Geriátrica (GDS-15)",
        "desc": "Escala de 15 ítems diseñada para detectar depresión en adultos mayores. Reduce falsos positivos por síntomas somáticos.",
    },
    "AdYesavage": {"nombre": "GDS-15 (alias)", "desc": "Alias de la Escala de Depresión Geriátrica de Yesavage."},
    "AdHARS": {
        "nombre": "Escala de Ansiedad de Hamilton (HARS)",
        "desc": "Escala heteroaplicada de 14 ítems que evalúa severidad de ansiedad.",
    },
    "AdEAD": {
        "nombre": "Escala de Ansiedad de Beck (BAI)",
        "desc": "Auto-reporte de 21 ítems sobre síntomas ansiosos en la última semana. Evalúa severidad de ansiedad.",
    },
    # ── Actividades de la vida diaria ──
    "EscLawton": {
        "nombre": "Escala de Lawton y Brody (IADL)",
        "desc": "Evalúa la capacidad funcional instrumental: uso de teléfono, compras, manejo de dinero, etc.",
    },
    "AdLawton": {
        "nombre": "Lawton y Brody (IADL) — Adulto",
        "desc": "Versión para adultos de la escala de actividades instrumentales de la vida diaria.",
    },
    "ViLawton": {
        "nombre": "Lawton y Brody (IADL) — Adulto Mayor",
        "desc": "Versión para adulto mayor de la escala IADL de Lawton.",
    },
    # ── Minimental y Montreal ──
    "AdMMSE": {
        "nombre": "Mini-Mental State Examination (MMSE)",
        "desc": "Cribado breve de 30 puntos que evalúa orientación, registro, atención, recuerdo y lenguaje.",
    },
    "AdMOCA": {
        "nombre": "Montreal Cognitive Assessment (MoCA)",
        "desc": "Cribado breve de 30 puntos, más sensible que MMSE para detectar deterioro cognitivo leve. Evalúa dominios frontales y visoespaciales.",
    },
    # ── Síntomas psicóticos / validez ──
    "NiPANSS": {
        "nombre": "PANSS (versión infantil)",
        "desc": "Escala de síntomas positivos y negativos para esquizofrenia. Adaptación para población adolescente.",
    },
    # ── TDAH / Discapacidad intelectual ──
    "AdWAIS": {
        "nombre": "WAIS-III (batería completa)",
        "desc": "Batería completa de Wechsler para adultos con todos los subtests e índices.",
    },
    "AdWAISWMI": {
        "nombre": "Índice Memoria de Trabajo WAIS",
        "desc": "Índice compuesto de memoria de trabajo derivado de Aritmética y Letras-Números.",
    },
    # ── INECO / escalas ejecutivas ──
    "AdINECO": {
        "nombre": "Batería INECO Frontal Screening",
        "desc": "Cribado breve de funciones ejecutivas (memoria de trabajo, inhibición, planificación, flexibilidad).",
    },
    # ── ENI-2 infantil ──
    "NiENIMem": {"nombre": "ENI-2 Memoria", "desc": "Batería neuropsicológica infantil ENI-2 — subpruebas de memoria."},
    "NiENILen": {
        "nombre": "ENI-2 Lenguaje",
        "desc": "Batería neuropsicológica infantil ENI-2 — subpruebas de lenguaje.",
    },
    # ── Rey Verbal (AdFCRO_Ver) ──
    "AdFCRO_Ver": {
        "nombre": "Rey Auditiva Verbal",
        "desc": "Recuerdo de una lista de palabras en 5 ensayos. Evalúa aprendizaje verbal, consolidación y reconocimiento.",
    },
    # ── Discriminación perceptual ──
    "NiDiscPer": {
        "nombre": "Discriminación Perceptual",
        "desc": "Evalúa la capacidad de discriminar entre estímulos visuales similares.",
    },
}


# ──────────────────────────────────────────────────────────
# Glosario de términos técnicos estándar
# ──────────────────────────────────────────────────────────
#
# Términos técnicos (no nombres de pruebas) que se incluyen en el anexo
# del informe. Son estables (no dependen del baremo del paciente) y se
# filtran dinámicamente según los términos que aparezcan en el informe.

GLOSARIO_TERMINOS: dict[str, str] = {
    "CI / CIT": "Cociente Intelectual Total. Medida global del funcionamiento intelectual con media 100 y desviación 15. Rango normal: 90-109. <70: déficit; 70-79: limítrofe; 80-89: promedio bajo; 110-119: promedio alto; 120-129: superior; ≥130: muy superior.",
    "ICV (Índice Comprensión Verbal)": "Índice compuesto WISC-IV/WAIS-III que resume razonamiento verbal, comprensión y conocimiento. Subtests típicos: Vocabulario, Semejanzas, Información, Comprensión.",
    "IRP (Índice Razonamiento Perceptual)": "Índice compuesto WISC-IV/WAIS-III que resume razonamiento no verbal, visualización y procesamiento espacial. Subtests típicos: Diseño con Cubos, Figuras Incompletas, Matrices, Rompecabezas visuales.",
    "IMT (Índice Memoria de Trabajo)": "Índice compuesto WISC-IV/WAIS-III que evalúa la capacidad de retener y manipular información temporalmente. Subtests típicos: Dígitos, Letras-Números, Aritmética.",
    "IVP (Índice Velocidad de Procesamiento)": "Índice compuesto WISC-IV/WAIS-III que evalúa la velocidad para escanear, escribir y copiar información simple. Subtests típicos: Claves, Búsqueda de Símbolos.",
    "Puntuación Z": "Desvío en unidades de desviación estándar respecto al grupo normativo. Z = (PD − μ) / σ. Z=0 equivale a la media. Z ≤ −1 indica rendimiento bajo el promedio. Z ≤ −2 indica déficit clínico (2σ por debajo de la media).",
    "Puntaje escalar (PE)": "Subtests Wechsler (WISC-IV, WAIS-III) con media 10 y desviación 3. Rango 1-19. PE 8-12 ≈ promedio (±0.67σ). PE ≤ 7 = bajo. PE ≥ 13 = superior.",
    "Percentil": "Porcentaje de la población normativa con desempeño igual o inferior al del paciente. Percentil 50 = mediana. Percentil 25 = primer cuartil. Z=0 ≈ percentil 50; Z=+1 ≈ percentil 84; Z=−1 ≈ percentil 16.",
    "Discrepancia significativa": "Diferencia entre dos índices compuestos que excede el umbral crítico de Wechsler. Tabla base: ICV-IRP (11/15), ICV-IMT (12/16), ICV-IVP (15/19), IRP-IMT (13/17), IRP-IVP (15/19), IMT-IVP (16/20). El primer umbral es p<.15 (tendencia); el segundo es p<.05 (significativa).",
    "Banda semántica": "Intervalo cualitativo del Z que resume el hallazgo: severo (Z≤−2, déficit), moderado (−2<Z≤−1, debilidad), promedio (−1<Z≤+1, rango normal), superior (Z>+1, fortaleza).",
    "RCI (Reliable Change Index)": "Índice de Cambio Confiable de Jacobson-Truax (1991). Mide si la diferencia entre dos evaluaciones del mismo paciente excede el error de medición. RCI > 1.96 indica cambio confiable al 95% de confianza. Se usa en seguimientos.",
    "DSM-5 / CIE-10": "DSM-5: Manual Diagnóstico y Estadístico de los Trastornos Mentales (APA, 5ª ed.). CIE-10: Clasificación Internacional de Enfermedades (OMS, 10ª rev.). NeuroSoft codifica el diagnóstico en CIE-10.",
}


def build_strengths_weaknesses(resultados: Sequence[dict]) -> tuple[list[str], list[str]]:
    """Listas planas de fortalezas y debilidades (bullets) por prueba.

    Filtra a Z<=-1 y Z>=1, ordena por magnitud absoluta.
    """
    weak, strong = [], []
    for r in resultados:
        z = r.get("z_equivalente")
        if z is None or r.get("tipo_metrica") == "ci":
            continue
        nombre = human_test_name(
            r.get("test_id", "") or "",
            r.get("test_nombre", "") or "",
        )
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
        "(alta)": "alta",
        "(media)": "media",
        "(baja)": "baja",
        "[alta]": "alta",
        "[media]": "media",
        "[baja]": "baja",
        "!!!": "alta",
        "!!": "media",
        "!": "baja",
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
    tiene_puntuacion = bool(
        re.search(r"\b(?:CI|cociente|percentil|escalar|z[- ]?score|puntuaci[oó]n\s+z)\b", texto, re.IGNORECASE)
    )
    if not tiene_puntuacion:
        principios["P2"] = {
            "titulo": "No patologizar variaciones normales",
            "estado": "no_aplica",
            "detalle": "No se detectaron puntuaciones explícitas en la narrativa.",
        }
    else:
        if re.search(
            r"\b(?:sugiere|consistente con|apoya|orienta a|compatible con|indicativo de)\b", texto, re.IGNORECASE
        ):
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
                "detalle": f"Población {poblacion_objetivo}: se recomienda mencionar baremo de Neuronorma Colombia (Arango-Lasprilla & Rivera, 2017).",
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
    alertas = [f"[{pid}] {p['titulo']}: {p['detalle']}" for pid, p in principios.items() if p["estado"] == "revisar"]
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
    "Limítrofe": "en el límite del rango esperado",
    "Limitrofe": "en el límite del rango esperado",
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


def frase_cualitativa_resultado(r: dict) -> str:
    """Frase breve para columna 'Qué significa' en tabla de resultados."""
    from .helpers import human_test_name

    nombre = human_test_name(
        r.get("test_id", "") or "",
        r.get("test_nombre", "") or r.get("nombre", "") or "",
    )
    banda = r.get("clasificacion") or r.get("interpretacion", "")
    banda_clara = banda_a_lenguaje_claro(str(banda))
    if banda in ("Bajo", "Muy Bajo"):
        return f"Por debajo de lo esperado en {nombre.lower()}"
    if banda in ("Promedio Bajo", "Limítrofe", "Limitrofe"):
        return f"Rendimiento {banda_clara}"
    if banda in ("Superior", "Promedio Alto"):
        return f"Fortaleza: {banda_clara}"
    return banda_clara or "Dentro del rango esperado"


def parse_edad_anos(edad_display: str | None) -> int | None:
    """Extrae años desde ``edad_display`` (ej. ``10a``, ``36 años``)."""
    import re

    if not edad_display:
        return None
    m = re.search(r"(\d+)", str(edad_display))
    return int(m.group(1)) if m else None


def detectar_modo_voz(edad_anos: int | None) -> str:
    """Determina registro narrativo: paciente, cuidador o pediátrico-cuidador."""
    if edad_anos is not None and edad_anos < 18:
        return "pediatrico_cuidador"
    if edad_anos is not None and edad_anos >= 65:
        return "cuidador"
    return "paciente"


def puente_impresion_lenguaje_claro(
    codigo_cie10: str = "",
    codigo_desc: str = "",
) -> str:
    """Frase puente empática antes de la impresión diagnóstica codificada."""
    desc = (codigo_desc or "").strip()
    if desc:
        return (
            f"En palabras sencillas, la conclusión clínica apunta a: {desc}. "
            "El código CIE-10 que aparece abajo es la forma estandarizada que "
            "usan médicos y EPS; no define a la persona ni su valor."
        )
    if codigo_cie10:
        return (
            "En palabras sencillas, los hallazgos se resumen en la impresión "
            "diagnóstica del profesional. El código CIE-10 es un lenguaje "
            "administrativo; su psicólogo/a le explicará qué significa para su caso."
        )
    return (
        "En palabras sencillas, la impresión diagnóstica resume lo que los "
        "resultados y la entrevista sugieren. Converse con su profesional "
        "para aclarar dudas antes de tomar decisiones."
    )


def _limpiar_texto_recomendacion(texto: str) -> str:
    import re

    t = texto.strip()
    t = re.sub(r"^\[[^\]]+\]\s*", "", t)
    t = re.sub(r"^\((alta|media|baja)\)\s*", "", t, flags=re.IGNORECASE)
    return t.strip()


def _recomendaciones_para_familia(
    recomendaciones: list[str],
    modo_voz: str,
) -> list[str]:
    """Convierte recomendaciones clínicas a viñetas familiares preservando texto tagged."""
    items: list[str] = []
    for r in recomendaciones[:6]:
        raw = r.strip()
        if not raw:
            continue
        limpio = _limpiar_texto_recomendacion(raw)
        r_low = raw.lower()
        if "[escolar]" in r_low or "colegio" in r_low or "escolar" in r_low:
            if modo_voz == "pediatrico_cuidador":
                items.append(f"Colegio: {limpio}")
            else:
                items.append(f"En el colegio o academia: {limpio}")
        elif "terap" in r_low:
            items.append(f"Terapia: {limpio}")
        elif "medic" in r_low or "psiquiatr" in r_low or "[médica]" in r_low or "[medica]" in r_low:
            items.append(f"Consulta médica: {limpio}")
        elif "[familiar]" in r_low:
            items.append(f"En casa y familia: {limpio}")
        elif "[seguimiento]" in r_low:
            items.append(f"Seguimiento: {limpio}")
        else:
            items.append(limpio)
    return items


def generar_resumen_paciente(
    resultados: list[dict],
    paciente_nombre: str = "",
    recomendaciones: list[str] | None = None,
    *,
    modo_voz: str | None = None,
    edad_anos: int | None = None,
) -> dict:
    """
    Genera un resumen en lenguaje claro para el paciente.

    Devuelve un dict con secciones:
      - 'saludo': bienvenida cálida
      - 'que_hicimos': descripción de la evaluación
      - 'que_encontramos': hallazgos en lenguaje claro (sin percentiles)
      - 'fortalezas': qué se hace bien
      - 'areas_apoyo': en qué se puede trabajar
      - 'que_recomendamos': plan de acción claro (texto continuo)
      - 'que_recomendamos_items': viñetas numerables para PDF
      - 'preguntas_frecuentes': FAQ para el paciente
      - 'modo_voz': registro narrativo usado
    """
    if modo_voz is None:
        modo_voz = detectar_modo_voz(edad_anos)

    nombre = paciente_nombre.split()[0] if paciente_nombre else ""
    if modo_voz == "pediatrico_cuidador":
        ref = nombre or "su hijo/a"
        saludo = (
            f"Este es un resumen de la evaluación de {ref}. "
            "Está escrito en lenguaje sencillo para que usted, como madre, padre "
            "o cuidador, pueda entender los hallazgos. Su psicólogo/a le explicará "
            "los detalles y resolverá cualquier duda en la sesión de devolución."
        )
        que_hicimos = (
            "Realizamos varias pruebas que miden cómo funciona el cerebro de "
            "su hijo/a en distintas situaciones: memoria, atención, lenguaje, "
            "razonamiento y velocidad de procesamiento. Las pruebas son como "
            '"pequeños retos" con papel, lápiz y a veces cubos o figuras. '
            "No hay respuestas buenas ni malas: buscamos conocer cómo trabaja "
            "su mente para orientar apoyos en casa y en el colegio."
        )
        _sujeto = "su hijo/a"
        _verbo_rindio = "mostró un rendimiento"
    elif modo_voz == "cuidador":
        ref = nombre or "su familiar evaluado"
        saludo = (
            f"Este es un resumen de la evaluación de {ref}. "
            "Está escrito en lenguaje sencillo para que usted, como cuidador/a "
            "o familiar, pueda entender los hallazgos y coordinar los próximos "
            "pasos con la EPS, neurología o el equipo tratante."
        )
        que_hicimos = (
            "Realizamos pruebas que miden memoria, atención, lenguaje, "
            "razonamiento y otras funciones del día a día. El objetivo es "
            "entender qué puede hacer su familiar de forma independiente y "
            "qué apoyos prácticos facilitan el cuidado en casa."
        )
        _sujeto = "su familiar"
        _verbo_rindio = "mostró un rendimiento"
    else:
        ref = nombre or "ti"
        saludo = (
            f"Este es un resumen de la evaluación que se realizó a {ref}. "
            "Está escrito en un lenguaje sencillo para que sea fácil de entender. "
            "Tu psicólogo o psicóloga te explicará los detalles y resolverá "
            "cualquier duda que tengas."
        )
        que_hicimos = (
            "Realizamos varias pruebas que miden cómo funciona tu cerebro en "
            "distintas situaciones: memoria, atención, lenguaje, razonamiento y "
            "la velocidad con la que procesas información. Las pruebas son como "
            '"pequeños retos" que se resuelven con papel, lápiz y a veces con cubos '
            "o figuras. No hay respuestas buenas ni malas: lo que nos interesa es "
            "conocer cómo trabaja tu mente."
        )
        _sujeto = "tu"
        _verbo_rindio = "tu rendimiento fue"

    # Procesar resultados: agrupar por dominio
    bandas_paciente: list[str] = []
    fortalezas: list[str] = []
    areas_apoyo: list[str] = []
    for r in resultados or []:
        nombre_test = r.get("test_nombre") or r.get("nombre") or r.get("test_id") or ""
        banda = r.get("clasificacion") or r.get("interpretacion", "")
        if not nombre_test:
            continue
        termino_claro = traducir_termino(nombre_test)
        banda_clara = banda_a_lenguaje_claro(banda)
        if banda in ("Superior", "Promedio Alto", "Promedio", "Limítrofe", "Promedio Bajo"):
            # Limítrofe y Promedio Bajo pueden ser tanto fortaleza relativa
            # como área de apoyo según el contexto. Marcamos ambos.
            if banda in ("Promedio Bajo",):
                areas_apoyo.append(
                    f"En {termino_claro}, {_sujeto} {_verbo_rindio} {banda_clara}. "
                    "Esto se puede trabajar con práctica y apoyo."
                )
            elif banda in ("Limítrofe", "Limitrofe"):
                areas_apoyo.append(
                    f"En {termino_claro}, {_sujeto} {_verbo_rindio} {banda_clara}. Vale la pena acompañarlo de cerca."
                )
            else:
                fortalezas.append(f"En {termino_claro}, {_sujeto} {_verbo_rindio} {banda_clara}.")
        elif banda in ("Bajo", "Muy Bajo"):
            if modo_voz == "paciente":
                areas_apoyo.append(
                    f"En {termino_claro}, encontramos un rendimiento {banda_clara}. "
                    "Es importante que converses con tu psicólogo/a sobre "
                    "qué significa esto y qué apoyos podrían ayudarte."
                )
            else:
                areas_apoyo.append(
                    f"En {termino_claro}, encontramos un rendimiento {banda_clara} en {_sujeto}. "
                    "Converse con su psicólogo/a sobre qué significa esto y qué apoyos "
                    "podrían ayudar."
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
            frases.append("Las áreas donde te fue bien incluyen: " + " ".join(fortalezas[:3]))
        if areas_apoyo:
            frases.append("Las áreas donde se recomienda trabajar incluyen: " + " ".join(areas_apoyo[:3]))
        que_encontramos = " ".join(frases)

    if recomendaciones:
        recs_paciente = _recomendaciones_para_familia(recomendaciones, modo_voz)
        que_recomendamos = " ".join(recs_paciente[:4])
    else:
        recs_paciente = []
        if modo_voz == "pediatrico_cuidador":
            que_recomendamos = (
                "Su psicólogo/a le explicará las recomendaciones específicas "
                "para su hijo/a en la sesión de devolución. Algunas sugerencias "
                "comunes incluyen: coordinación con el colegio, rutinas en casa "
                "y seguimiento terapéutico."
            )
        elif modo_voz == "cuidador":
            que_recomendamos = (
                "Su psicólogo/a le orientará sobre los próximos pasos: controles "
                "con neurología, apoyos en casa, terapia ocupacional o "
                "rehabilitación cognitiva según el caso."
            )
        else:
            que_recomendamos = (
                "Su psicólogo/a le explicará las recomendaciones específicas "
                "en la sesión de devolución. Algunas sugerencias comunes incluyen: "
                "técnicas de estudio, estrategias de organización o seguimiento."
            )

    # FAQ adaptadas al paciente (no hardcoded): priorizamos las relevantes.
    preguntas_frecuentes: list[tuple[str, str]] = []

    # 1. ¿Son permanentes? — siempre relevante.
    preguntas_frecuentes.append(
        (
            "¿Mis resultados son permanentes?",
            "No necesariamente. El cerebro puede cambiar con el tiempo, "
            "especialmente con práctica, con los apoyos adecuados y con un buen "
            "ambiente. Estos resultados son una foto del momento actual: tu "
            "psicólogo/a te ayudará a entender qué puede cambiar y qué se "
            "mantiene más estable.",
        )
    )

    # 2. ¿Por qué algunos puntajes son mejores que otros? — siempre relevante.
    preguntas_frecuentes.append(
        (
            "¿Por qué algunos resultados son mejores que otros?",
            "Es completamente normal. Todas las personas tienen áreas donde "
            "son más fuertes y áreas donde pueden mejorar. Esto NO significa "
            "que haya algo mal: el cerebro humano es diverso y cada uno tiene "
            "su propio perfil.",
        )
    )

    # 3. FAQ condicional: si hubo puntajes muy bajos.
    if any(b in ("Bajo", "Muy Bajo") for b in bandas_paciente):
        preguntas_frecuentes.append(
            (
                "¿Qué significa un puntaje 'bajo' o 'muy bajo'?",
                "Significa que, comparado con personas de la misma edad y nivel "
                "educativo, esa función específica rindió por debajo de lo "
                "esperado. NO es un diagnóstico en sí mismo. Es una señal para "
                "profundizar, entrenar y apoyar esa área. Tu psicólogo/a te "
                "explicará si requiere intervención profesional adicional.",
            )
        )
    # 4. FAQ condicional: si hubo puntajes en CI.
    tiene_ci = any(r.get("tipo_metrica") == "ci" for r in (resultados or []))
    if tiene_ci:
        preguntas_frecuentes.append(
            (
                "¿Qué es el 'cociente intelectual' (CI)?",
                "El CI es un número que resume el rendimiento global en "
                "diversas pruebas. NO define tu inteligencia total ni tu valor "
                "como persona: es solo una medida parcial de ciertas habilidades "
                "de razonamiento, memoria y atención. Varía según el contexto, "
                "la fatiga, el ánimo del día y muchos otros factores.",
            )
        )
    # 5. FAQ condicional: si hubo puntajes destacados altos.
    if any(b in ("Superior", "Promedio Alto") for b in bandas_paciente):
        preguntas_frecuentes.append(
            (
                "¿Qué hago con las áreas donde me fue muy bien?",
                "¡Celebra y potencia esas fortalezas! Pueden ser tu ancla para "
                "compensar las áreas que requieren más esfuerzo. Compartir esto "
                "con tu familia, colegio o terapeuta les permite diseñar "
                "estrategias que aprovechen lo que mejor te sale.",
            )
        )
    # 6. FAQ condicional: si el paciente es menor de edad.
    if not areas_apoyo:
        preguntas_frecuentes.append(
            (
                "¿Necesito otro tipo de evaluaciones?",
                "Tu psicólogo/a te dirá si se necesitan otros estudios "
                "(por ejemplo, evaluación pedagógica, médica, o del lenguaje). "
                "No te preocupes si no entiendes algún término: puedes preguntar "
                "siempre.",
            )
        )

    return {
        "saludo": saludo,
        "que_hicimos": que_hicimos,
        "que_encontramos": que_encontramos,
        "fortalezas": fortalezas,
        "areas_apoyo": areas_apoyo,
        "que_recomendamos": que_recomendamos,
        "que_recomendamos_items": recs_paciente,
        "preguntas_frecuentes": preguntas_frecuentes,
        "modo_voz": modo_voz,
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
            with_dis = sum(
                1
                for m in re.finditer(
                    r"\bDIS-(?:atencional|mn[eé]sic[oa]|ejecutiv[oa]|visuoespacial|verbal)",
                    texto,
                    re.IGNORECASE,
                )
            )
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
        texto,
        re.IGNORECASE,
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
    alertas = [f"[{pid}] {p['titulo']}: {p['detalle']}" for pid, p in principios.items() if p["estado"] == "revisar"]
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
    "encabezado": ("INFORME NEUROPSICOLÓGICO CONFIDENCIAL — DOCUMENTO CLÍNICO LEGAL"),
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
    partes.append(f"Uso previsto: {uso_previsto or CLAUSULAS_INFORME_PROFESIONAL['uso_previsto_default']}")
    partes.append(f"Limitaciones: {limitaciones or CLAUSULAS_INFORME_PROFESIONAL['limitaciones_default']}")
    partes.append(f"Lugar: {lugar or '—'}")
    partes.append("")
    partes.append(CLAUSULAS_INFORME_PROFESIONAL["responsabilidad_profesional"])
    return "\n".join(partes)
