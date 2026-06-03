"""
mcp-servers/baremos/server.py
==============================
MCP Server local de NeuroSoft — expone baremos de BD_NEURO_MAESTRA.json
como herramientas invocables desde Claude Code.

§mcp-baremos (2026-05-19): permite consultar baremos clínicos sin tener
que arrancar la SPA. Útil para auditorías ad-hoc, generación de fixtures
de test, y análisis comparativo con literatura.

Herramientas expuestas:
  - list_pruebas(poblacion=None, search=None)
      Lista todas las pruebas, opcionalmente filtradas.
  - get_prueba(test_id)
      Detalle completo de una prueba: tipo_calculo, tipo_metrica, n_baremos.
  - get_baremo_value(test_id, key)
      Devuelve el valor del baremo para una clave específica.
  - get_baremo_keys(test_id, limit=20)
      Lista las primeras N claves del baremo para inspección.
  - count_pruebas_por_poblacion()
      Stats: cuántas pruebas hay por población (infantil/joven/mayor).
  - get_ajuste_escolaridad(test_id, escolaridad)
      Devuelve el ajuste +N PD por escolaridad (Neuronorma AM).
  - score_prueba(test_id, pd, edad_anios, edad_meses=0, sexo=None,
                  escolaridad=None)
      Aplica el motor de scoring oficial y devuelve el escalar/CI
      interpretado. Útil para verificar manualmente contra informes
      reales (Caso 1: Jesús, Caso 2: Blanca del CLAUDE.md backend).

Uso en Claude Code:
  Registrar en `~/.claude/mcp.json` o en el proyecto:
    {
      "mcpServers": {
        "neurosoft-baremos": {
          "command": "D:/NeuroSoftApp/mcp-servers/baremos/venv/Scripts/python.exe",
          "args": ["D:/NeuroSoftApp/mcp-servers/baremos/server.py"]
        }
      }
    }
  Reiniciar Claude Code → las herramientas aparecen como
  `mcp__neurosoft-baremos__list_pruebas`, etc.
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Any, Optional

from mcp.server.fastmcp import FastMCP

# ─── Logging hacia stderr (stdout es JSON-RPC del MCP) ────────────────
logging.basicConfig(
    level=logging.INFO,
    format="[neurosoft-baremos-mcp] %(levelname)s | %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("neurosoft-baremos-mcp")


# ─── Localización del BD_NEURO_MAESTRA.json ────────────────────────────
def _find_baremo_path() -> Path:
    """
    Busca BD_NEURO_MAESTRA.json en orden:
      1. NEUROSOFT_BAREMO_PATH (env var)
      2. Junto al .exe instalado (modo producción)
      3. neurosoft-backend/data/ (modo dev)
      4. %APPDATA%/NeuroSoft/ (instalación local)
    """
    import os
    env = os.getenv("NEUROSOFT_BAREMO_PATH")
    if env and Path(env).exists():
        return Path(env)

    candidates = [
        Path(__file__).resolve().parents[2] / "neurosoft-backend" / "data" / "BD_NEURO_MAESTRA.json",
        Path(os.getenv("APPDATA", "")) / "NeuroSoft" / "BD_NEURO_MAESTRA.json",
        Path("D:/NeuroSoftApp/neurosoft-backend/data/BD_NEURO_MAESTRA.json"),
    ]
    for c in candidates:
        if c.exists():
            return c
    raise FileNotFoundError(
        "No encontré BD_NEURO_MAESTRA.json. Define NEUROSOFT_BAREMO_PATH "
        "o coloca el archivo en neurosoft-backend/data/."
    )


_BAREMO_PATH = _find_baremo_path()
logger.info(f"Cargando baremos desde: {_BAREMO_PATH}")
_BAREMOS = json.loads(_BAREMO_PATH.read_text(encoding="utf-8"))
_BATERIAS = _BAREMOS.get("baterias", {})

# Construir índice plano test_id → (poblacion, prueba)
_INDEX: dict[str, tuple[str, dict]] = {}
for poblacion, pruebas in _BATERIAS.items():
    if not isinstance(pruebas, dict):
        continue
    for tid, p in pruebas.items():
        if tid.startswith("_") or not isinstance(p, dict):
            continue
        _INDEX[tid] = (poblacion, p)

logger.info(f"Índice construido: {len(_INDEX)} pruebas")


# ─── MCP Server ────────────────────────────────────────────────────────
mcp = FastMCP(
    "neurosoft-baremos",
    instructions=(
        "Servidor MCP de NeuroSoft que expone los baremos clínicos colombianos. "
        f"Hay {len(_INDEX)} pruebas indexadas en {len(_BATERIAS)} poblaciones "
        "(infantil, adulto_joven, adulto_mayor). Usa las herramientas para "
        "consultar baremos, verificar valores, calcular escalares sin tener "
        "que arrancar la SPA."
    ),
)


@mcp.tool()
def list_pruebas(
    poblacion: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 50,
) -> dict[str, Any]:
    """
    Lista pruebas con baremos. Filtros opcionales:
      - poblacion: 'infantil' | 'adulto_joven' | 'adulto_mayor'
      - search: substring case-insensitive en id o nombre
      - limit: máximo de resultados (default 50)
    """
    q = (search or "").lower().strip()
    results = []
    for tid, (pop, p) in _INDEX.items():
        if poblacion and pop != poblacion:
            continue
        nombre = p.get("nombre", "")
        if q and q not in tid.lower() and q not in nombre.lower():
            continue
        results.append({
            "id": tid,
            "nombre": nombre,
            "poblacion": pop,
            "tipo_calculo": p.get("tipo_calculo"),
            "tipo_metrica": p.get("tipo_metrica"),
            "n_baremos": len(p.get("baremos") or {}),
        })
    results.sort(key=lambda r: (r["poblacion"], r["nombre"]))
    return {
        "total_matched": len(results),
        "returned": min(len(results), limit),
        "pruebas": results[:limit],
    }


@mcp.tool()
def get_prueba(test_id: str) -> dict[str, Any]:
    """
    Detalle completo de una prueba (sin todos los baremos, solo metadata).
    """
    if test_id not in _INDEX:
        return {"error": f"Prueba '{test_id}' no encontrada"}
    pop, p = _INDEX[test_id]
    baremos = p.get("baremos") or {}
    sample_keys = list(baremos.keys())[:5]
    return {
        "id": test_id,
        "nombre": p.get("nombre"),
        "poblacion": pop,
        "tipo_calculo": p.get("tipo_calculo"),
        "tipo_metrica": p.get("tipo_metrica"),
        "n_baremos": len(baremos),
        "muestra_claves": sample_keys,
        "muestra_valores": {k: baremos[k] for k in sample_keys},
        "fuente_estimada": _fuente_estimada(test_id, pop),
    }


@mcp.tool()
def get_baremo_value(test_id: str, key: str) -> dict[str, Any]:
    """
    Devuelve el valor del baremo para una clave específica.
    Ejemplos de claves según tipo_calculo:
      - rango_puntaje:    "{año}{bracket_meses}{pd}" → "104730"
      - wais_range:       "{rango_edad}{pd}"          → "253442"
      - desconocido:      "{rango_am}{pd}"            → "6062237"
      - z_score:          "{edad}"                    → "10"
      - suma_a_indice:    "{suma_escalares}"          → "26"
    """
    if test_id not in _INDEX:
        return {"error": f"Prueba '{test_id}' no encontrada"}
    _, p = _INDEX[test_id]
    baremos = p.get("baremos") or {}
    if key not in baremos:
        return {
            "error": f"Clave '{key}' no existe en baremo de {test_id}",
            "tipo_calculo": p.get("tipo_calculo"),
            "claves_cercanas": [k for k in baremos.keys() if key in k][:10],
        }
    return {
        "test_id": test_id,
        "key": key,
        "value": baremos[key],
        "tipo_metrica": p.get("tipo_metrica"),
    }


@mcp.tool()
def get_baremo_keys(test_id: str, limit: int = 20) -> dict[str, Any]:
    """Lista las primeras N claves del baremo para inspección visual."""
    if test_id not in _INDEX:
        return {"error": f"Prueba '{test_id}' no encontrada"}
    _, p = _INDEX[test_id]
    baremos = p.get("baremos") or {}
    keys = list(baremos.keys())
    return {
        "test_id": test_id,
        "total_keys": len(keys),
        "showing": min(limit, len(keys)),
        "keys": keys[:limit],
        "values_sample": {k: baremos[k] for k in keys[:limit]},
    }


@mcp.tool()
def count_pruebas_por_poblacion() -> dict[str, Any]:
    """
    Stats globales: cuántas pruebas por población, por tipo_calculo,
    total de claves de baremo en BD.
    """
    by_pop: dict[str, int] = {}
    by_tipo: dict[str, int] = {}
    total_keys = 0
    for tid, (pop, p) in _INDEX.items():
        by_pop[pop] = by_pop.get(pop, 0) + 1
        tc = p.get("tipo_calculo") or "_desconocido"
        by_tipo[tc] = by_tipo.get(tc, 0) + 1
        total_keys += len(p.get("baremos") or {})
    return {
        "total_pruebas": len(_INDEX),
        "por_poblacion": by_pop,
        "por_tipo_calculo": by_tipo,
        "total_claves_baremo": total_keys,
        "baremo_version": _BAREMOS.get("version", "desconocida"),
    }


@mcp.tool()
def get_ajuste_escolaridad(test_id: str, escolaridad: str) -> dict[str, Any]:
    """
    Devuelve el ajuste +N PD por escolaridad (solo aplica a Neuronorma AM).
    Escolaridad: 'Analfabeta' | 'Primaria Incompleta' | 'Primaria' |
                 'Secundaria Incompleta' | 'Secundaria' | 'Universitaria'.
    """
    am = _BATERIAS.get("adulto_mayor", {})
    ajustes = am.get("_ajustes_escolaridad", {})
    test_ajustes = ajustes.get(test_id, {})
    if not test_ajustes:
        return {
            "test_id": test_id,
            "ajuste": 0,
            "nota": "Esta prueba no requiere ajuste por escolaridad (solo Neuronorma AM lo usa).",
        }
    ajuste = test_ajustes.get(escolaridad, 0)
    return {
        "test_id": test_id,
        "escolaridad": escolaridad,
        "ajuste_pd": ajuste,
        "todos_los_ajustes": test_ajustes,
    }


@mcp.tool()
def score_prueba(
    test_id: str,
    pd: float,
    edad_anios: int,
    edad_meses: int = 0,
    sexo: Optional[str] = None,
    escolaridad: Optional[str] = None,
) -> dict[str, Any]:
    """
    Aplica el motor oficial de scoring de NeuroSoft a una prueba.
    Útil para verificar manualmente contra informes reales.

    Ejemplo (Caso 1 — Jesús, 16a 11m, M, Secundaria Incompleta):
      score_prueba("NiWiscDC", pd=53, edad_anios=16, edad_meses=11,
                    sexo="M", escolaridad="Secundaria Incompleta")
      → debe devolver escalar=11 (verificado contra informe real).

    Ejemplo (Caso 2 — Blanca, 80a 5m, F, Primaria Incompleta):
      score_prueba("ViTMTA", pd=239, edad_anios=80, edad_meses=5,
                    sexo="F", escolaridad="Primaria Incompleta")
      → debe devolver escalar=6.
    """
    # Para usar el motor real sin importar todo el backend, hacemos lookup
    # directo del baremo basado en tipo_calculo. Esto reproduce la lógica
    # principal sin requerir SQLAlchemy y deps pesadas.
    if test_id not in _INDEX:
        return {"error": f"Prueba '{test_id}' no encontrada"}
    pop, prueba = _INDEX[test_id]
    tipo_calculo = prueba.get("tipo_calculo")
    baremos = prueba.get("baremos") or {}

    # Aplicar ajuste de escolaridad si aplica (solo Neuronorma AM)
    pd_ajustado = pd
    if pop == "adulto_mayor" and escolaridad:
        am = _BATERIAS.get("adulto_mayor", {})
        ajustes = am.get("_ajustes_escolaridad", {}).get(test_id, {})
        ajuste = ajustes.get(escolaridad, 0)
        pd_ajustado = pd + ajuste

    pd_int = int(pd_ajustado)

    if tipo_calculo == "rango_puntaje":
        bracket = "03" if edad_meses < 4 else ("47" if edad_meses < 8 else "811")
        key = f"{edad_anios}{bracket}{pd_int}"
    elif tipo_calculo == "wais_range":
        rango = _wais_range(edad_anios)
        key = f"{rango}{pd_int}"
        # §mcp-bug-fix-2026-05-19: el motor real (strategies.py:202-209) tiene
        # un fallback inteligente — si la clave WAIS no existe, prueba claves
        # AM. Caso confirmado: ViGroberRLT está etiquetada wais_range en BD
        # pero realmente usa claves Neuronorma AM (formato "5056xx"). Sin este
        # fallback, el MCP devuelve "no encontrada" para pruebas Grober AM.
        if key not in baremos and edad_anios >= 50:
            am_rango = _am_range(edad_anios)
            if am_rango:
                am_key = f"{am_rango}{pd_int}"
                if am_key in baremos:
                    raw = baremos[am_key]
                    # raw puede ser escalar o [rango, pd, score]
                    score = raw[2] if isinstance(raw, list) and len(raw) >= 3 else raw
                    return {
                        "test_id": test_id, "pd": pd, "pd_ajustado": pd_ajustado,
                        "tipo_calculo": tipo_calculo,
                        "key_buscada": am_key,
                        "result": score,
                        "tipo_metrica": prueba.get("tipo_metrica"),
                        "note": "fallback AM aplicado (prueba wais_range con claves Neuronorma)",
                    }
    elif tipo_calculo == "desconocido":
        rango = _am_range(edad_anios)
        if rango is None:
            return {
                "test_id": test_id,
                "pd": pd,
                "edad_anios": edad_anios,
                "tipo_calculo": tipo_calculo,
                "result": None,
                "metadata": {"sin_norma": True,
                             "motivo": f"Edad {edad_anios} fuera del rango Neuronorma AM (50-90)."},
            }
        key = f"{rango}{pd_int}"
    elif tipo_calculo == "z_score":
        key = str(edad_anios)
        if key in baremos:
            params = baremos[key]
            if isinstance(params, list) and len(params) == 2:
                mu, sigma = float(params[0]), float(params[1])
                if sigma == 0:
                    return {
                        "test_id": test_id, "pd": pd, "pd_ajustado": pd_ajustado,
                        "tipo_calculo": tipo_calculo, "key_buscada": key,
                        "result": None,
                        "metadata": {"sin_norma": True, "motivo": "sigma=0"},
                    }
                z = round((pd - mu) / sigma, 2)
                return {
                    "test_id": test_id, "pd": pd, "pd_ajustado": pd_ajustado,
                    "tipo_calculo": tipo_calculo, "key_buscada": key,
                    "z_score": z,
                    "media": mu, "sigma": sigma,
                }
        return {
            "test_id": test_id, "key_buscada": key,
            "error": f"No hay parámetros z-score para edad {edad_anios}",
        }
    elif tipo_calculo == "suma_a_indice":
        key = str(pd_int)
    elif tipo_calculo == "escolaridad_pc50":
        esc_code = (escolaridad or "")[0].upper() if escolaridad else ""
        key = f"{edad_anios}{esc_code}"
    elif tipo_calculo == "clasificacion_fija":
        key = str(pd_int)
    elif tipo_calculo == "puntaje_directo_a_t":
        key = str(pd_int)
    else:
        return {
            "test_id": test_id,
            "tipo_calculo": tipo_calculo,
            "error": (
                f"tipo_calculo '{tipo_calculo}' no implementado en el MCP. "
                "Usa el motor de scoring oficial del backend para esta prueba."
            ),
        }

    if key in baremos:
        return {
            "test_id": test_id,
            "pd": pd,
            "pd_ajustado": pd_ajustado,
            "tipo_calculo": tipo_calculo,
            "key_buscada": key,
            "result": baremos[key],
            "tipo_metrica": prueba.get("tipo_metrica"),
        }
    return {
        "test_id": test_id,
        "pd": pd,
        "pd_ajustado": pd_ajustado,
        "tipo_calculo": tipo_calculo,
        "key_buscada": key,
        "result": None,
        "error": f"Clave '{key}' no existe en baremo. PD fuera de rango.",
    }


# ─── Helpers ───────────────────────────────────────────────────────────
def _wais_range(edad: int) -> str:
    if 16 <= edad <= 19: return "1619"
    if 20 <= edad <= 24: return "2024"
    if 25 <= edad <= 34: return "2534"
    if 35 <= edad <= 54: return "3554"
    if 55 <= edad <= 69: return "5569"
    return "7000"


def _am_range(edad: int) -> Optional[str]:
    """
    Banda de edad Neuronorma AM. Devuelve None si la edad está FUERA del
    rango de aplicación (< 50). Antes (bug detectado 2026-05-19) cualquier
    edad < 50 caía al fallback "8190" como si fuera adulto mayor extremo,
    devolviendo escalares falsos para pruebas que NO aplican a esa edad.
    """
    if edad < 50: return None
    if 50 <= edad <= 56: return "5056"
    if 57 <= edad <= 59: return "5759"
    if 60 <= edad <= 62: return "6062"
    if 63 <= edad <= 65: return "6365"
    if 66 <= edad <= 68: return "6668"
    if 69 <= edad <= 71: return "6971"
    if 72 <= edad <= 74: return "7274"
    if 75 <= edad <= 77: return "7577"
    if 78 <= edad <= 80: return "7880"
    return "8190"


def _fuente_estimada(test_id: str, poblacion: str) -> str:
    tid = test_id.lower()
    if "wisc" in tid: return "WISC-IV (Pearson Colombia)"
    if "wais" in tid: return "WAIS-III (Pearson Colombia)"
    if tid.startswith("ni") and poblacion == "infantil":
        return "ENI-2 (Matute, Rosselli, Ardila, Ostrosky 2013)"
    if tid.startswith("vi") and poblacion == "adulto_mayor":
        return "Neuronorma Colombia (Peña-Casanova, Montañés 2021)"
    if tid.startswith("ad"):
        return "Arango-Lasprilla & Rivera LATAM 2015"
    return "Otra fuente"


# ─── Resources (lectura directa de archivos) ───────────────────────────
@mcp.resource("baremo://stats")
def baremo_stats_resource() -> str:
    """Stats globales del baremo en formato leíble (no-tool)."""
    stats = count_pruebas_por_poblacion()
    lines = [
        f"# Baremo NeuroSoft — estadísticas globales",
        f"",
        f"Total pruebas: {stats['total_pruebas']}",
        f"Versión: {stats['baremo_version']}",
        f"Claves de baremo: {stats['total_claves_baremo']:,}",
        f"",
        f"## Por población",
    ]
    for pop, n in sorted(stats["por_poblacion"].items()):
        lines.append(f"  - {pop}: {n}")
    lines.append("\n## Por tipo_calculo")
    for tc, n in sorted(stats["por_tipo_calculo"].items(), key=lambda x: -x[1]):
        lines.append(f"  - {tc}: {n}")
    return "\n".join(lines)


# ─── Entry point ───────────────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("Iniciando MCP server neurosoft-baremos vía stdio")
    mcp.run()
