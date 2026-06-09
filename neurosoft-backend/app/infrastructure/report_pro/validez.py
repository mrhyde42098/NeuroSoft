"""
Validez de síntomas — criterios Slick et al. 1999 + cortes TOMM/Rey-15.

Portado desde ``validezClinica.js`` (frontend) para informes médico-legales.
"""

from __future__ import annotations

from collections.abc import Sequence

REY15_CUTOFF_FAIL = 9  # ≤9 ítems → esfuerzo subóptimo (Boone et al.)
TOMM_TRIAL2_CUTOFF_FAIL = 45  # <45/50 en Trial 2 → esfuerzo subóptimo


def _extract_score(result: dict) -> float | int | None:
    for key in ("puntaje_bruto", "puntaje_escalar", "puntaje"):
        v = result.get(key)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                continue
    return None


def extraer_puntuaciones_validez(resultados: Sequence[dict]) -> dict[str, float | None]:
    """Extrae Rey-15 y TOMM Trial 2 desde ``resultados`` del informe."""
    rey15: float | None = None
    tomm_trial2: float | None = None
    tomm_fallback: float | None = None

    for r in resultados or []:
        tid = (r.get("test_id") or "").upper()
        nombre = (r.get("test_nombre") or r.get("nombre") or "").upper()
        score = _extract_score(r)
        if score is None:
            continue

        if tid == "REY15" or ("REY" in tid and "15" in tid) or "REY 15" in nombre:
            rey15 = score
            continue

        if tid == "TOMM" or "TOMM" in nombre:
            meta = r.get("metadata") or {}
            trial = meta.get("trial") or meta.get("ensayo") or meta.get("trial_num")
            nombre_low = nombre.lower()
            is_trial2 = (
                trial in (2, "2", "trial2", "trial_2", "ensayo2", "ensayo_2")
                or "trial 2" in nombre_low
                or "ensayo 2" in nombre_low
                or "ensayo ii" in nombre_low
            )
            if is_trial2:
                tomm_trial2 = score
            elif tomm_trial2 is None:
                tomm_fallback = score

    if tomm_trial2 is None and tomm_fallback is not None:
        tomm_trial2 = tomm_fallback

    return {"rey15": rey15, "tomm_trial2": tomm_trial2}


def _clasificar_rey15(score: float) -> str:
    if score <= REY15_CUTOFF_FAIL:
        return "suboptimo"
    return "valido"


def _clasificar_tomm_trial2(score: float) -> str:
    if score < TOMM_TRIAL2_CUTOFF_FAIL:
        return "suboptimo"
    return "valido"


def evaluar_validez_desde_resultados(
    resultados: Sequence[dict],
) -> dict[str, object]:
    """Evalúa pruebas de validez presentes en los resultados."""
    scores = extraer_puntuaciones_validez(resultados)
    rey15 = scores["rey15"]
    tomm_trial2 = scores["tomm_trial2"]

    lineas: list[str] = []
    svt_fallidas: list[str] = []
    tiene_pruebas = rey15 is not None or tomm_trial2 is not None

    if rey15 is not None:
        estado = _clasificar_rey15(rey15)
        if estado == "suboptimo":
            svt_fallidas.append("Rey 15-Item")
            lineas.append(
                f"Rey 15-Item: {int(rey15)}/15 (corte esperado >{REY15_CUTOFF_FAIL} ítems) — "
                "rendimiento por debajo del umbral, sugestivo de esfuerzo subóptimo."
            )
        else:
            lineas.append(
                f"Rey 15-Item: {int(rey15)}/15 (corte >{REY15_CUTOFF_FAIL}) — esfuerzo dentro del rango esperado."
            )

    if tomm_trial2 is not None:
        estado = _clasificar_tomm_trial2(tomm_trial2)
        if estado == "suboptimo":
            svt_fallidas.append("TOMM Trial 2")
            lineas.append(
                f"TOMM — Trial 2: {int(tomm_trial2)}/50 (corte clínico ≥{TOMM_TRIAL2_CUTOFF_FAIL}) — "
                "por debajo del umbral, sugestivo de esfuerzo subóptimo."
            )
        else:
            lineas.append(
                f"TOMM — Trial 2: {int(tomm_trial2)}/50 (corte ≥{TOMM_TRIAL2_CUTOFF_FAIL}) — "
                "esfuerzo dentro del rango esperado."
            )

    reserva = ""
    if svt_fallidas:
        reserva = (
            "Los resultados cognitivos deben interpretarse con reserva dado esfuerzo "
            f"subóptimo en pruebas de validez ({'; '.join(svt_fallidas)}). "
            "Se recomienda integrar criterios Slick (A–D) y el contexto forense antes "
            "de formular conclusiones definitivas sobre el daño neuropsicológico."
        )

    return {
        "tiene_pruebas": tiene_pruebas,
        "lineas": lineas,
        "svt_fallidas": svt_fallidas,
        "reserva_interpretativa": reserva,
        "rey15": rey15,
        "tomm_trial2": tomm_trial2,
    }


def construir_texto_validez_pdf(
    resultados: Sequence[dict],
    *,
    template_sin_pruebas: str,
) -> tuple[str, str, bool]:
    """Devuelve (cuerpo, título_callout, es_alerta).

    Si no hay pruebas de validez en resultados, retorna el template estático.
    """
    ev = evaluar_validez_desde_resultados(resultados)
    if not ev["tiene_pruebas"]:
        return template_sin_pruebas, "Advertencia metodológica", True

    partes = list(ev["lineas"])
    if ev["reserva_interpretativa"]:
        partes.append(str(ev["reserva_interpretativa"]))
    else:
        partes.append(
            "Con los indicadores de validez disponibles, no se evidencia esfuerzo "
            "subóptimo en las pruebas administradas. La interpretación cognitiva "
            "puede sostenerse con el grado de confianza habitual, integrando siempre "
            "la observación clínica y el contexto pericial."
        )

    es_alerta = bool(ev["svt_fallidas"])
    titulo = "Resultados de validez" if not es_alerta else "Alerta de validez — esfuerzo subóptimo"
    return "\n\n".join(partes), titulo, es_alerta
