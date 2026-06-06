"""
app/presentation/api/v1/clinical_extras.py
==========================================
Endpoints auxiliares del motor clínico institucional.

GET  /rips/classification
    Cataloga diagnósticos → CIE-10 por rango etario (RIPS 2025).
GET  /wisc/forma-corta/cit
    Estima CIT WISC-IV (Forma Corta Sattler, 2010).
POST /wisc/discrepancia
    Analiza discrepancia entre los 4 índices WISC-IV.

GET  /baterias/alternas
    Catálogo de protocolos alternos para casos especiales (hipoacusia,
    discapacidad visual, motora, analfabetismo, etc.).
POST /memoria/grober-buschke
    Puntuación e interpretación del Grober-Buschke / FCSRT.
POST /dcl/clasificar
    Árbol de decisión DSM-5 para TCL/TCM + subtipo + etiología.
GET  /recomendaciones
    Reservorio institucional de recomendaciones por grupo etario y cuadro clínico.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Usamos los prefijos existentes donde encaja el recurso
rips_catalog_router = APIRouter(prefix="/rips", tags=["RIPS"])
wisc_router = APIRouter(prefix="/wisc", tags=["WISC-IV"])
baterias_router = APIRouter(prefix="/baterias", tags=["Baterías alternas"])
memoria_router = APIRouter(prefix="/memoria", tags=["Memoria"])
dcl_router = APIRouter(prefix="/dcl", tags=["DCL / DSM-5"])
recs_router = APIRouter(prefix="/recomendaciones", tags=["Recomendaciones"])


# ─────────────────────────────────────────────────────────────
# Carga y caché del catálogo RIPS
# ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_rips_catalog() -> dict:
    path = Path(__file__).resolve().parents[4] / "app" / "domain" / "data" / "rips_classification.json"
    return json.loads(path.read_text(encoding="utf-8"))


@rips_catalog_router.get(
    "/classification",
    summary="Catálogo de diagnósticos → CIE-10 por edad",
    description=(
        "Devuelve el mapeo DIAGNÓSTICO → CIE-10 según la clasificación "
        "RIPS institucional 2025. Sin filtros: todas las poblaciones. Con "
        "`?population=...`: sólo esa población. Con `?age=N`: la "
        "población que contiene esa edad."
    ),
)
def get_rips_classification(
    population: Literal["nino_preescolar", "nino", "adulto", "adulto_mayor"] | None = Query(default=None),
    age: int | None = Query(default=None, ge=0, le=120),
):
    catalog = _load_rips_catalog()
    pops = catalog["populations"]

    # Si se pasó age, calcular a qué población pertenece
    if age is not None and population is None:
        for key, pop in pops.items():
            lo, hi = pop["age_range"]
            if lo <= age <= hi:
                population = key  # type: ignore[assignment]
                break
        if population is None:
            raise HTTPException(404, detail=f"No hay población definida para edad={age}.")

    if population is not None:
        if population not in pops:
            raise HTTPException(404, detail=f"Población desconocida: {population}.")
        return {
            "version": catalog["version"],
            "population": population,
            "label": pops[population]["label"],
            "age_range": pops[population]["age_range"],
            "diagnoses": pops[population]["diagnoses"],
        }

    return {
        "version": catalog["version"],
        "source": catalog["source"],
        "notes": catalog["notes"],
        "populations": pops,
    }


# ─────────────────────────────────────────────────────────────
# WISC-IV — Forma Corta (Sattler, 2010)
# ─────────────────────────────────────────────────────────────
class WiscCitResponse(BaseModel):
    suma_escalares: int
    forma: int
    cit_estimado: int
    interpretacion: str
    source: str


@wisc_router.get(
    "/forma-corta/cit",
    response_model=WiscCitResponse,
    summary="CIT estimado WISC-IV por Forma Corta (Sattler, 2010)",
    description=(
        "Estima el CIT a partir de la suma de 4 puntuaciones escalares. "
        "forma=1 → DC+CD+MT+FI · forma=2 → VB+SE+CM+PC. Rango válido: 4–76."
    ),
)
def wisc_forma_corta_cit(
    suma: int = Query(..., ge=4, le=76, description="Suma de escalares (4–76)"),
    forma: int = Query(default=1, ge=1, le=2, description="1=DC+CD+MT+FI, 2=VB+SE+CM+PC"),
):
    from app.domain.clinical_engine.wisc_discrepancy import estimate_cit_forma_corta

    try:
        return estimate_cit_forma_corta(suma, forma)
    except ValueError as e:
        raise HTTPException(422, detail=str(e))


# ─────────────────────────────────────────────────────────────
# WISC-IV — Análisis de discrepancia
# ─────────────────────────────────────────────────────────────
class DiscrepanciaDTO(BaseModel):
    icv: float | None = Field(default=None, ge=40, le=160, description="Índice de Comprensión Verbal")
    irp: float | None = Field(default=None, ge=40, le=160, description="Índice de Razonamiento Perceptivo")
    imt: float | None = Field(default=None, ge=40, le=160, description="Índice de Memoria de Trabajo")
    ivp: float | None = Field(default=None, ge=40, le=160, description="Índice de Velocidad de Procesamiento")


@wisc_router.post(
    "/discrepancia",
    summary="Análisis de discrepancia entre índices WISC-IV",
    description=(
        "Detecta discrepancia significativa (≥ 23 pts = 1.5 DE) entre los "
        "cuatro índices principales del WISC-IV. Recomienda ICG o ICC "
        "cuando el CIT no es interpretable como medida unitaria (criterio "
        "Flanagan & Kaufman, 2009; protocolo institucional)."
    ),
)
def wisc_discrepancia(dto: DiscrepanciaDTO):
    from app.domain.clinical_engine.wisc_discrepancy import detect_discrepancy

    result = detect_discrepancy(dto.icv, dto.irp, dto.imt, dto.ivp)
    return result.as_dict()


# ─────────────────────────────────────────────────────────────
# Item 4 — Catálogo de Baterías Alternas
# ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_baterias_catalog() -> dict:
    path = Path(__file__).resolve().parents[4] / "app" / "domain" / "data" / "baterias_alternas.json"
    return json.loads(path.read_text(encoding="utf-8"))


@baterias_router.get(
    "/alternas",
    summary="Catálogo de protocolos alternos",
    description=(
        "Devuelve baterías neuropsicológicas adaptadas por condición "
        "(hipoacusia, discapacidad visual, visual-auditiva, motora, "
        "analfabetismo) y grupo etario (niño, adulto, adulto_mayor). "
        "Filtros opcionales: ?condicion= y ?grupo="
    ),
)
def get_baterias_alternas(
    condicion: Literal["hipoacusia", "discapacidad_visual", "visual_auditiva", "motora", "analfabeta"] | None = Query(
        default=None
    ),
    grupo: Literal["nino", "adulto", "adulto_mayor"] | None = Query(default=None),
):
    cat = _load_baterias_catalog()
    conds = cat["conditions"]

    if condicion is not None:
        if condicion not in conds:
            raise HTTPException(404, detail=f"Condición desconocida: {condicion}.")
        cond = conds[condicion]
        if grupo is not None:
            if grupo not in cond["batteries"]:
                raise HTTPException(404, detail=f"Grupo etario '{grupo}' no disponible para '{condicion}'.")
            return {
                "version": cat["version"],
                "condicion": condicion,
                "label": cond["label"],
                "grupo": grupo,
                "general_notes": cond.get("general_notes", []),
                "battery": cond["batteries"][grupo],
            }
        return {
            "version": cat["version"],
            "condicion": condicion,
            "label": cond["label"],
            "general_notes": cond.get("general_notes", []),
            "batteries": cond["batteries"],
        }

    return {
        "version": cat["version"],
        "source": cat["source"],
        "notes": cat["notes"],
        "conditions": conds,
    }


# ─────────────────────────────────────────────────────────────
# Item 6 — Motor Grober-Buschke
# ─────────────────────────────────────────────────────────────
class WordEntry(BaseModel):
    palabra: str
    categoria: str


class GroberTrialDTO(BaseModel):
    libre: list[str] = Field(default_factory=list)
    con_clave: list[str] = Field(default_factory=list)
    intrusiones: list[str] = Field(default_factory=list)


class GroberDiferidoDTO(BaseModel):
    libre: list[str] = Field(default_factory=list)
    con_clave: list[str] = Field(default_factory=list)
    intrusiones: list[str] = Field(default_factory=list)


class GroberReconocimientoDTO(BaseModel):
    aciertos: int = Field(default=0, ge=0, le=16)
    falsos_positivos: int = Field(default=0, ge=0, le=16)
    total_dianas: int = Field(default=16, ge=1, le=32)
    total_distractores: int = Field(default=16, ge=1, le=32)


class GroberRequest(BaseModel):
    trials: list[GroberTrialDTO]
    diferido: GroberDiferidoDTO | None = None
    reconocimiento: GroberReconocimientoDTO | None = None
    word_list: list[WordEntry] | None = None


@memoria_router.post(
    "/grober-buschke",
    summary="Puntúa e interpreta un test Grober-Buschke / FCSRT",
    description=(
        "Recibe los ensayos de aprendizaje (libre + con clave), "
        "recobro diferido y reconocimiento. Devuelve totales, "
        "beneficio de clave, discriminabilidad en reconocimiento y "
        "clasificación del patrón (amnésico / disejecutivo / mixto / normal)."
    ),
)
def post_grober_buschke(dto: GroberRequest):
    from app.domain.clinical_engine.grober_buschke import (
        GroberDiferido,
        GroberReconocimiento,
        GroberTrial,
        score_grober_buschke,
    )

    try:
        trials = [GroberTrial(libre=t.libre, con_clave=t.con_clave, intrusiones=t.intrusiones) for t in dto.trials]
        dif = None
        if dto.diferido is not None:
            dif = GroberDiferido(
                libre=dto.diferido.libre,
                con_clave=dto.diferido.con_clave,
                intrusiones=dto.diferido.intrusiones,
            )
        reco = None
        if dto.reconocimiento is not None:
            reco = GroberReconocimiento(
                aciertos=dto.reconocimiento.aciertos,
                falsos_positivos=dto.reconocimiento.falsos_positivos,
                total_dianas=dto.reconocimiento.total_dianas,
                total_distractores=dto.reconocimiento.total_distractores,
            )
        wl = [w.model_dump() for w in dto.word_list] if dto.word_list else None
        r = score_grober_buschke(trials, dif, reco, wl)
        return r.as_dict()
    except ValueError as e:
        raise HTTPException(422, detail=str(e))


# ─────────────────────────────────────────────────────────────
# Item 8 — Árbol DSM-5 para TCL/TCM
# ─────────────────────────────────────────────────────────────
class DCLRequest(BaseModel):
    declive: Literal["ninguno", "leve", "moderado", "significativo"]
    dominios_afectados: list[str] = Field(default_factory=list)

    avd_afectadas: bool = False
    independencia_perdida: bool = False
    delirium_activo: bool = False
    otro_trastorno_mental: bool = False

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
    edad: int | None = Field(default=None, ge=0, le=120)


@dcl_router.post(
    "/clasificar",
    summary="Árbol DSM-5 para TCL / TCM + subtipo + etiología probable",
    description=(
        "Aplica los criterios DSM-5 de trastorno neurocognitivo leve/mayor "
        "y, con las pistas etiológicas opcionales, sugiere las etiologías "
        "probables (EA, vascular, Lewy, FTD, EP, TCE) y un CIE-10 orientador."
    ),
)
def post_dcl_clasificar(dto: DCLRequest):
    from app.domain.clinical_engine.dsm5_dcl_tree import DCLInput, classify_dcl

    entrada = DCLInput(**dto.model_dump())
    return classify_dcl(entrada).as_dict()


# ─────────────────────────────────────────────────────────────
# Item 14 — Reservorio de recomendaciones
# ─────────────────────────────────────────────────────────────
@lru_cache(maxsize=1)
def _load_reservorio() -> dict:
    path = Path(__file__).resolve().parents[4] / "app" / "domain" / "data" / "reservorio_recomendaciones.json"
    return json.loads(path.read_text(encoding="utf-8"))


@recs_router.get(
    "",
    summary="Reservorio de recomendaciones por cuadro clínico",
    description=(
        "Devuelve recomendaciones agrupadas por grupo etario "
        "(infantil, adulto, adulto_mayor) y cuadro clínico. "
        "Filtros opcionales: ?grupo= y ?cuadro="
    ),
)
def get_recomendaciones(
    grupo: Literal["infantil", "adulto", "adulto_mayor"] | None = Query(default=None),
    cuadro: str | None = Query(default=None),
):
    cat = _load_reservorio()
    grupos = cat["grupos"]

    if grupo is not None:
        if grupo not in grupos:
            raise HTTPException(404, detail=f"Grupo desconocido: {grupo}.")
        g = grupos[grupo]
        if cuadro is not None:
            if cuadro not in g["cuadros"]:
                raise HTTPException(404, detail=f"Cuadro '{cuadro}' no disponible en grupo '{grupo}'.")
            c = g["cuadros"][cuadro]
            return {
                "version": cat["version"],
                "grupo": grupo,
                "grupo_label": g["label"],
                "cuadro": cuadro,
                "cuadro_label": c["label"],
                "recomendaciones": c["recomendaciones"],
            }
        return {
            "version": cat["version"],
            "grupo": grupo,
            "grupo_label": g["label"],
            "cuadros": g["cuadros"],
        }

    return {
        "version": cat["version"],
        "source": cat["source"],
        "notes": cat["notes"],
        "grupos": grupos,
    }
