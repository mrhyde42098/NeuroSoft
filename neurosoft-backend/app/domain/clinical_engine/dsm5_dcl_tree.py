"""
app/domain/clinical_engine/dsm5_dcl_tree.py
===========================================
Árbol de decisión DSM-5 para clasificar:

    • Trastorno Neurocognitivo Leve  (TCL / minor NCD)      → ~ F067
    • Trastorno Neurocognitivo Mayor (TCM / major NCD)     → ~ F00–F03

Con su:
    • Subtipo cognitivo:  amnésico | no-amnésico
    • Extensión:          monodominio | multidominio
    • Etiología probable: EA, DLB, Vascular, FTD, TCE, EP, otras

Criterios DSM-5:
    Leve    — Declive cognitivo MODESTO respecto al nivel previo;
              NO interfiere con la autonomía en AVD instrumentales.
    Mayor   — Declive cognitivo SIGNIFICATIVO;
              SÍ interfiere con la autonomía en AVD.

En ambos casos se exige:
    • No ocurre exclusivamente durante delirium.
    • No se explica mejor por otro trastorno mental (ej. depresión mayor).

Este módulo es declarativo — no hace inferencia probabilística formal;
replica el árbol cualitativo que el clínico aplica en consulta.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

TipoDeclive = Literal["ninguno", "leve", "moderado", "significativo"]
Extension   = Literal["monodominio", "multidominio"]
Subtipo     = Literal["amnesico", "no_amnesico"]


# ─────────────────────────────────────────────────────────────
# Entrada
# ─────────────────────────────────────────────────────────────
@dataclass
class DCLInput:
    # Criterio A — declive cognitivo (por reporte + objetivo NPS)
    declive: TipoDeclive
    dominios_afectados: list[str] = field(default_factory=list)  # p. ej. ["memoria", "funciones_ejecutivas"]

    # Criterio B — interferencia funcional
    avd_afectadas: bool = False         # SÍ/NO afecta AVD instrumentales
    independencia_perdida: bool = False # SÍ/NO requiere asistencia para AVD básicas

    # Criterios de exclusión
    delirium_activo: bool = False
    otro_trastorno_mental: bool = False    # p. ej. depresión mayor que explique el cuadro

    # Pistas etiológicas (opcionales — refinan la salida)
    inicio_insidioso: bool = False
    progresion_gradual: bool = False
    escalonado_post_acv: bool = False
    factores_riesgo_vascular: bool = False
    alucinaciones_visuales: bool = False
    parkinsonismo: bool = False
    fluctuaciones_cognitivas: bool = False
    desinhibicion_precoz: bool = False
    apatia_marcada: bool = False
    antecedente_tce: bool = False
    edad: int | None = None


# ─────────────────────────────────────────────────────────────
# Salida
# ─────────────────────────────────────────────────────────────
@dataclass
class DCLResult:
    clasificacion: Literal["ninguno", "tcl", "tcm", "indeterminado"]
    clasificacion_label: str
    cie10_sugerido: str
    subtipo: Subtipo | None
    extension: Extension | None
    etiologias_probables: list[str]
    criterios_cumplidos: list[str]
    criterios_faltantes: list[str]
    notas: list[str]

    def as_dict(self) -> dict:
        return {
            "clasificacion":        self.clasificacion,
            "clasificacion_label":  self.clasificacion_label,
            "cie10_sugerido":       self.cie10_sugerido,
            "subtipo":              self.subtipo,
            "extension":            self.extension,
            "etiologias_probables": self.etiologias_probables,
            "criterios_cumplidos":  self.criterios_cumplidos,
            "criterios_faltantes":  self.criterios_faltantes,
            "notas":                self.notas,
        }


# ─────────────────────────────────────────────────────────────
# Motor
# ─────────────────────────────────────────────────────────────
def classify_dcl(entrada: DCLInput) -> DCLResult:
    cumplidos: list[str] = []
    faltantes: list[str] = []
    notas: list[str] = []

    # ── A) Declive cognitivo ──
    if entrada.declive in ("moderado", "significativo"):
        cumplidos.append("Declive cognitivo objetivado (criterio A).")
    elif entrada.declive == "leve":
        cumplidos.append("Declive cognitivo leve sugerido — revisar con NPS objetivo.")
    else:
        faltantes.append("No se objetiva declive cognitivo respecto al nivel premórbido.")

    # ── E) Exclusiones ──
    if entrada.delirium_activo:
        faltantes.append("Delirium activo — debe descartarse antes de diagnosticar NCD.")
        return DCLResult(
            clasificacion="indeterminado",
            clasificacion_label="Indeterminado — delirium activo",
            cie10_sugerido="",
            subtipo=None,
            extension=None,
            etiologias_probables=[],
            criterios_cumplidos=cumplidos,
            criterios_faltantes=faltantes,
            notas=["DSM-5 exige que el déficit NO ocurra exclusivamente durante un delirium. "
                   "Re-evaluar tras resolución del delirium."],
        )

    if entrada.otro_trastorno_mental:
        faltantes.append("Posible otro trastorno mental (p. ej. depresión mayor) que explique el cuadro.")
        notas.append("Considerar pseudodemencia depresiva. Re-evaluar tras tratamiento afectivo.")

    # ── Ningún declive = sin diagnóstico ──
    if entrada.declive == "ninguno":
        return DCLResult(
            clasificacion="ninguno",
            clasificacion_label="Sin evidencia de trastorno neurocognitivo",
            cie10_sugerido="Z031",  # Observación por sospecha de enfermedades
            subtipo=None,
            extension=None,
            etiologias_probables=[],
            criterios_cumplidos=cumplidos,
            criterios_faltantes=faltantes,
            notas=notas or ["Perfil dentro de límites esperados. Recomendar seguimiento rutinario."],
        )

    # ── Extensión: mono vs multi ──
    extension: Extension | None = None
    n_dominios = len(entrada.dominios_afectados)
    if n_dominios >= 2:
        extension = "multidominio"
        cumplidos.append(f"Multidominio ({n_dominios} dominios afectados).")
    elif n_dominios == 1:
        extension = "monodominio"
        cumplidos.append(f"Monodominio (solo '{entrada.dominios_afectados[0]}').")
    else:
        faltantes.append("No se especificaron dominios afectados; caracterización incompleta.")

    # ── Subtipo: amnésico vs no-amnésico ──
    subtipo: Subtipo | None = None
    dominios_lower = [d.lower() for d in entrada.dominios_afectados]
    if any("memoria" in d for d in dominios_lower):
        subtipo = "amnesico"
        cumplidos.append("Subtipo amnésico (memoria afectada).")
    elif n_dominios > 0:
        subtipo = "no_amnesico"
        cumplidos.append("Subtipo no-amnésico (memoria preservada).")

    # ── B) Interferencia con AVD ──
    es_mayor = entrada.avd_afectadas or entrada.independencia_perdida

    if es_mayor:
        clasificacion = "tcm"
        label = "Trastorno Neurocognitivo Mayor (TCM / Demencia)"
        cumplidos.append("Interferencia en AVD — criterio B cumplido para TCM.")
    else:
        # TCL solo si realmente hay declive moderado o significativo
        if entrada.declive in ("moderado", "significativo", "leve"):
            clasificacion = "tcl"
            label = "Trastorno Neurocognitivo Leve (TCL)"
            cumplidos.append("AVD preservadas — compatible con TCL.")
        else:
            return DCLResult(
                clasificacion="ninguno",
                clasificacion_label="Sin criterios suficientes para diagnóstico NCD",
                cie10_sugerido="Z031",
                subtipo=subtipo,
                extension=extension,
                etiologias_probables=[],
                criterios_cumplidos=cumplidos,
                criterios_faltantes=faltantes,
                notas=notas or ["Insuficiente evidencia para clasificar como TCL o TCM."],
            )

    # ── Etiología probable ──
    etiologias = _inferir_etiologias(entrada, subtipo, extension)

    # ── CIE-10 sugerido ──
    cie10 = _cie10_sugerido(clasificacion, etiologias, entrada)

    return DCLResult(
        clasificacion=clasificacion,
        clasificacion_label=label,
        cie10_sugerido=cie10,
        subtipo=subtipo,
        extension=extension,
        etiologias_probables=etiologias,
        criterios_cumplidos=cumplidos,
        criterios_faltantes=faltantes,
        notas=notas,
    )


# ─────────────────────────────────────────────────────────────
# Etiologías probables (modelo simple basado en pistas)
# ─────────────────────────────────────────────────────────────
def _inferir_etiologias(
    e: DCLInput,
    subtipo: Subtipo | None,
    extension: Extension | None,
) -> list[str]:
    """Devuelve etiologías ordenadas de más a menos probable."""
    scores: dict[str, int] = {
        "Enfermedad de Alzheimer":                   0,
        "Demencia vascular":                         0,
        "Demencia por cuerpos de Lewy":              0,
        "Demencia frontotemporal":                   0,
        "Enfermedad de Parkinson con demencia":      0,
        "Secuelar a TCE":                            0,
    }

    # EA — insidioso, gradual, amnésico multidominio
    if e.inicio_insidioso:                       scores["Enfermedad de Alzheimer"] += 2
    if e.progresion_gradual:                     scores["Enfermedad de Alzheimer"] += 2
    if subtipo == "amnesico":                    scores["Enfermedad de Alzheimer"] += 3
    if extension == "multidominio":              scores["Enfermedad de Alzheimer"] += 1

    # Vascular — escalonado, factores de riesgo
    if e.escalonado_post_acv:                    scores["Demencia vascular"] += 3
    if e.factores_riesgo_vascular:               scores["Demencia vascular"] += 2

    # Lewy — alucinaciones visuales, parkinsonismo, fluctuaciones
    if e.alucinaciones_visuales:                 scores["Demencia por cuerpos de Lewy"] += 3
    if e.parkinsonismo:                          scores["Demencia por cuerpos de Lewy"] += 2
    if e.fluctuaciones_cognitivas:               scores["Demencia por cuerpos de Lewy"] += 2

    # FTD — desinhibición, apatía, no-amnésico
    if e.desinhibicion_precoz:                   scores["Demencia frontotemporal"] += 3
    if e.apatia_marcada:                         scores["Demencia frontotemporal"] += 2
    if subtipo == "no_amnesico":                 scores["Demencia frontotemporal"] += 1

    # Parkinson con demencia
    if e.parkinsonismo and not e.alucinaciones_visuales:
        scores["Enfermedad de Parkinson con demencia"] += 2

    # TCE
    if e.antecedente_tce:                        scores["Secuelar a TCE"] += 3

    # Edad >= 80 refuerza EA; < 65 refuerza FTD
    if e.edad is not None:
        if e.edad >= 80:
            scores["Enfermedad de Alzheimer"] += 1
        if e.edad < 65:
            scores["Demencia frontotemporal"] += 1

    ordenadas = sorted(scores.items(), key=lambda kv: kv[1], reverse=True)
    return [nombre for nombre, s in ordenadas if s >= 2]


# ─────────────────────────────────────────────────────────────
# CIE-10 sugerido
# ─────────────────────────────────────────────────────────────
def _cie10_sugerido(
    clasificacion: str,
    etiologias: list[str],
    e: DCLInput,
) -> str:
    if clasificacion == "tcl":
        return "F067"  # Otros trastornos mentales específicos debidos a lesión/disfunción cerebral

    # TCM — CIE-10 por etiología probable más alta
    if not etiologias:
        return "F03X"  # Demencia no especificada

    top = etiologias[0]
    if top == "Enfermedad de Alzheimer":
        # Temprana (< 65) vs tardía (≥ 65)
        if e.edad is not None and e.edad < 65:
            return "F000"
        return "F001"
    if top == "Demencia vascular":
        return "F019"
    if top == "Demencia por cuerpos de Lewy":
        return "G318"
    if top == "Demencia frontotemporal":
        return "G311"
    if top == "Enfermedad de Parkinson con demencia":
        return "F023"
    if top == "Secuelar a TCE":
        return "F078"
    return "F03X"
