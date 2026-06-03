"""
app/presentation/api/v1/baremos_info.py
=========================================
Endpoint para inspeccionar qué baremos están cargados, su versión,
checksum y metadata clínica (fuentes normativas, rango etario, idioma).

Sprint 9 — primer paso del refactor a baremos múltiples. Permite que
el frontend muestre al clínico qué fuentes está usando el sistema.
La capacidad de **alternar** baremo según protocolo (Neuronorma
Colombia vs Arango-Lasprilla vs ENI-2) se difiere a una iteración
posterior.

Rutas:
  GET /api/v1/baremos/info        → metadata + estadísticas del baremo cargado
  GET /api/v1/baremos/sources     → lista de fuentes normativas declaradas
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException

baremos_info_router = APIRouter(prefix="/baremos", tags=["📐 Baremos"])


def _loader():
    """Obtiene el singleton del loader sin importar al toplevel
    (lazy import para no romper tests que no cargan baremos)."""
    from app.domain.clinical_engine.baremos_loader import BaremosLoader
    return BaremosLoader.instance()


@baremos_info_router.get(
    "/info",
    summary="Metadata del baremo activo",
    description=(
        "Retorna versión, checksum SHA-256, ruta del archivo y "
        "estadísticas (número de pruebas por población) del baremo "
        "actualmente cargado en el motor de scoring. Útil para que el "
        "informe pueda citar correctamente la fuente normativa."
    ),
)
def get_baremos_info() -> dict[str, Any]:
    try:
        loader = _loader()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Baremos no cargados: {e}")

    meta = getattr(loader, "_meta", {}) or {}
    # Contar pruebas por población
    by_pop: dict[str, int] = {}
    for prueba in loader._index.values():  # noqa: SLF001
        pop = getattr(prueba, "poblacion", None) or "desconocido"
        by_pop[pop] = by_pop.get(pop, 0) + 1

    from app.domain.clinical_engine.baremos_overlays import get_overlays_for_settings
    overlays = get_overlays_for_settings()

    return {
        "version": loader.baremo_version,
        "checksum_sha256": loader.baremo_checksum,
        "path": str(loader._baremo_path) if loader._baremo_path else None,  # noqa: SLF001
        "total_pruebas": len(loader._index),  # noqa: SLF001
        "pruebas_por_poblacion": by_pop,
        "meta": {
            k: v for k, v in meta.items()
            if k not in ("baterias",) and not k.startswith("_")
        },
        "interpretaciones": {
            "escalar":  meta.get("interpretacion_escalar"),
            "ci":       meta.get("interpretacion_ci"),
            "t":        meta.get("interpretacion_t"),
        },
        "overlays_disponibles": overlays,
        "overlay_count": len(overlays),
    }


@baremos_info_router.get(
    "/pruebas",
    summary="Catálogo público de pruebas con baremos disponibles",
    description=(
        "Devuelve metadata pública (id, nombre, población, tipo) de TODAS "
        "las pruebas con baremos cargados — sin exponer los valores "
        "numéricos de los baremos en sí. Útil para construir un catálogo "
        "navegable en el frontend ('¿qué pruebas tengo disponibles para "
        "esta población?')."
    ),
)
def list_pruebas() -> dict[str, Any]:
    """
    Catálogo de pruebas. Por cada prueba reporta:
      - id, nombre, poblacion, tipo_calculo, tipo_metrica
      - n_baremos: cuántas claves de baremo tiene cargadas
      - fuente_estimada: cuál de las 6 fuentes normativas conocidas
        cubre esta prueba (heurística por id/nombre).
    """
    try:
        loader = _loader()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Baremos no cargados: {e}")

    # Mapeo heurístico id-prefix → fuente normativa
    def _fuente(test_id: str, nombre: str, poblacion: str) -> str:
        tid = test_id.lower()
        if tid.startswith("niwisc") or "wisc" in tid:
            return "wisc_iv_pearson"
        if tid.startswith("adwais") or "wais" in tid:
            return "wais_iii_pearson"
        if tid.startswith("ni") and poblacion == "infantil":
            # ENI-2 cubre la mayoría de las pruebas infantiles no-WISC
            return "eni_2_colombia"
        if tid.startswith("vi") and poblacion == "adulto_mayor":
            return "neuronorma_colombia"
        if tid.startswith("ad"):
            return "arango_lasprilla_2015"
        return "otro"

    catalogo: list[dict[str, Any]] = []
    for prueba in loader._index.values():  # noqa: SLF001
        try:
            n_baremos = len(prueba.baremos or {})
        except Exception:
            n_baremos = 0
        catalogo.append({
            "id": prueba.id,
            "nombre": prueba.nombre,
            "poblacion": prueba.poblacion,
            "tipo_calculo": prueba.tipo_calculo,
            "tipo_metrica": prueba.tipo_metrica,
            "n_baremos": n_baremos,
            "fuente_estimada": _fuente(prueba.id, prueba.nombre, prueba.poblacion),
        })

    # Ordenamos: por población (infantil → joven → mayor) y luego nombre
    pop_order = {"infantil": 0, "adulto_joven": 1, "adulto_mayor": 2}
    catalogo.sort(key=lambda r: (pop_order.get(r["poblacion"], 99), r["nombre"]))

    return {
        "total": len(catalogo),
        "por_poblacion": {
            "infantil":     sum(1 for r in catalogo if r["poblacion"] == "infantil"),
            "adulto_joven": sum(1 for r in catalogo if r["poblacion"] == "adulto_joven"),
            "adulto_mayor": sum(1 for r in catalogo if r["poblacion"] == "adulto_mayor"),
        },
        "pruebas": catalogo,
    }


@baremos_info_router.get(
    "/overlays",
    summary="Baremos adicionales detectados en data/baremos/",
    description=(
        "Lista los archivos JSON adicionales en `data/baremos/` (Sprint 9). "
        "Cada archivo es un overlay que el motor de scoring puede usar "
        "explícitamente en una iteración futura. Por ahora sólo se "
        "reporta su presencia + metadata."
    ),
)
def get_overlays_list() -> list[dict[str, Any]]:
    from app.domain.clinical_engine.baremos_overlays import get_overlays_for_settings
    return get_overlays_for_settings()


@baremos_info_router.get(
    "/sources",
    summary="Fuentes normativas declaradas",
    description=(
        "Lista las fuentes normativas (referencias bibliográficas) que "
        "componen el baremo cargado. Cada test puede pertenecer a una "
        "fuente diferente — los datos colombianos están integrados con "
        "Neuronorma Colombia (Peña-Casanova/Montañés), Arango-Lasprilla "
        "& Rivera 2015 (multicéntrico LATAM) y ENI-2 Manizales."
    ),
)
def get_baremo_sources() -> list[dict[str, Any]]:
    """Catálogo estático de fuentes normativas conocidas. En el futuro
    se mapeará dinámicamente a partir del campo `fuente` por test."""
    return [
        {
            "id": "neuronorma_colombia",
            "nombre": "Neuronorma Colombia",
            "autores": "Peña-Casanova J., Montañés P. et al.",
            "anio": 2021,
            "edad_min": 50, "edad_max": 90,
            "pruebas_cubiertas": [
                "Boston Naming Test (BNT)",
                "FCSRT — Free and Cued Selective Reminding",
                "Fluidez semántica y fonológica",
                "Stroop",
                "Rey-Osterrieth (copia y memoria)",
                "SDMT",
                "TMT A-B",
                "Tower of London",
                "Token Test",
                "Span de Dígitos (forward/backward)",
                "Cubos de Corsi",
                "Wisconsin modificado (M-WCST)",
            ],
            "cita": "Peña-Casanova et al. *Neuronorma Colombia: aportes y características metodológicas*. Neurología (Elsevier) 2021.",
        },
        {
            "id": "arango_lasprilla_2015",
            "nombre": "Arango-Lasprilla & Rivera (LATAM)",
            "autores": "Arango-Lasprilla J.C., Rivera D. et al.",
            "anio": 2015,
            "edad_min": 18, "edad_max": 90,
            "pruebas_cubiertas": [
                "HVLT-R", "BVMT-R", "Rey-Osterrieth", "Stroop",
                "M-WCST", "TMT", "BTA", "Fluidez fonológica/semántica",
                "BNT (forma corta)",
            ],
            "cita": "Arango-Lasprilla, Rivera et al. *Commonly used Neuropsychological Tests for Spanish Speakers*. NeuroRehabilitation 2015.",
            "muestra_total": 5402,
        },
        {
            "id": "eni_2_colombia",
            "nombre": "ENI-2 — Evaluación Neuropsicológica Infantil",
            "autores": "Matute E., Rosselli M., Ardila A., Ostrosky-Solís F.",
            "anio": 2013,
            "edad_min": 5, "edad_max": 16,
            "pruebas_cubiertas": [
                "Atención", "Habilidades constructivas",
                "Codificación de memoria", "Habilidades perceptuales",
                "Lenguaje", "Lectura", "Escritura", "Aritmética",
                "Habilidades espaciales", "Conceptos", "Funciones ejecutivas",
            ],
            "cita": "Matute, Rosselli, Ardila, Ostrosky-Solís. ENI-2. Manual Moderno 2013.",
        },
        {
            "id": "wisc_iv_pearson",
            "nombre": "WISC-IV — Versión colombiana",
            "autores": "Wechsler D. (adaptación Pearson)",
            "anio": 2003,
            "edad_min": 6, "edad_max": 16,
            "pruebas_cubiertas": [
                "15 subtests WISC-IV + Formas Cortas Sattler 2010",
            ],
            "cita": "Pearson Clinical. WISC-IV adaptación al español.",
        },
        {
            "id": "wais_iii_pearson",
            "nombre": "WAIS-III — Versión colombiana",
            "autores": "Wechsler D. (adaptación Pearson)",
            "anio": 1999,
            "edad_min": 17, "edad_max": 89,
            "pruebas_cubiertas": ["13 subtests WAIS-III"],
            "cita": "Pearson Clinical. WAIS-III adaptación al español.",
        },
        {
            "id": "moca_pedraza_colombia",
            "nombre": "MoCA-S — Validación Bogotá",
            "autores": "Pedraza O.L. et al.",
            "anio": 2016,
            "edad_min": 60, "edad_max": 90,
            "cortes": "≤20 sugiere DCL; ≤17 sugiere demencia leve (ajustar por escolaridad)",
            "cita": "Pedraza et al. *Confiabilidad, validez de criterio y discriminante del MoCA*. Acta Médica Colombiana 2016.",
        },
    ]
