"""
S5.x — Frente 7: Auditoría exhaustiva de baremos de pruebas marcadas ✅
(NO modifica `BD_NEURO_MAESTRA.json` — solo lectura).

Este script genera un reporte de salud de los baremos: completitud, gaps,
rango, distribución, y posibles anomalías. Pensado para ejecutarse antes
de un release y como evidencia de cumplimiento (Res 1995/1999 art. 11 +
Ley 1581/2012 — calidad del dato clínico).

Uso:
    python scripts/audit_baremos_18.py \
        --baremos data/BD_NEURO_MAESTRA.json \
        --out docs/AUDITORIA_BAREMOS_DETALLADA.md

Si no se especifica --baremos, usa la ruta por defecto.
Si no se especifica --out, escribe a stdout.
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Las pruebas marcadas en el PLAN_MAESTRO_GLOBAL.md §7.2
# (Antes 18 — ahora 25 entradas tras ampliar a más screenings/atencional)
PRUEBAS_MARCADAS = {
    "AdWAISCC": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISV": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISRO": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISFI": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISHI": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISI": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISL": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-1",
        "expectativa_claves": "rango escalar 1-19",
    },
    "AdWAISICV": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-2 (suma a CI)",
        "expectativa_claves": "rango CI 40-160",
    },
    "AdWAISICP": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-3 (suma a CI)",
        "expectativa_claves": "rango CI 40-160",
    },
    "AdWAISIMT": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-4 (suma a CI)",
        "expectativa_claves": "rango CI 40-160",
    },
    "AdWAISIVP": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-5 (suma a CI)",
        "expectativa_claves": "rango CI 40-160",
    },
    "AdWASIEVer": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-6",
        "expectativa_claves": "rango escalar",
    },
    "AdWAISEMan": {
        "categoria": "wais_iii",
        "tabla_referencia": "WAIS-III Tabla A-7",
        "expectativa_claves": "rango escalar",
    },
    "EscYesavage": {
        "categoria": "screening",
        "tabla_referencia": "Sheikh 1986 / Martínez de la Iglesia 2002",
        "expectativa_claves": "0/1 puntos; 15 ítems",
    },
    "MMSE": {
        "categoria": "screening",
        "tabla_referencia": "Folstein 1975 / Rosselli 2000 Col",
        "expectativa_claves": "0-30 puntos",
    },
    "AdBeck": {
        "categoria": "screening",
        "tabla_referencia": "Beck 1996 BDI-II",
        "expectativa_claves": "0-63 puntos (21 ítems × 3)",
    },
    "EscLawton": {
        "categoria": "screening",
        "tabla_referencia": "Lawton Brody 1969",
        "expectativa_claves": "0-8 (mujer) / 0-5 (hombre)",
    },
    "EscKertesz": {
        "categoria": "screening",
        "tabla_referencia": "Kertesz 1982 (WAB)",
        "expectativa_claves": "0-100 puntos",
    },
    "SDMT": {
        "categoria": "atencion_velocidad",
        "tabla_referencia": "Smith 1982",
        "expectativa_claves": "PD→percentil",
    },
    "ViTMTA": {
        "categoria": "atencion_velocidad",
        "tabla_referencia": "Reitan 1958 / Tombaugh 2004 (Neuronorma AM)",
        "expectativa_claves": "rango_am pd",
    },
    "ViTMTB": {
        "categoria": "atencion_velocidad",
        "tabla_referencia": "Reitan 1958 / Tombaugh 2004 (Neuronorma AM)",
        "expectativa_claves": "rango_am pd",
    },
    "NiFCROCop": {
        "categoria": "visuoespacial",
        "tabla_referencia": "Meyers & Meyers 1995",
        "expectativa_claves": "PD→escalar",
    },
    "NiFCRORec": {
        "categoria": "visuoespacial",
        "tabla_referencia": "Meyers & Meyers 1995",
        "expectativa_claves": "PD→escalar",
    },
    "FluidP": {
        "categoria": "lenguaje",
        "tabla_referencia": "Benton 1967 / Arango-Lasprilla 2017",
        "expectativa_claves": "PD→percentil",
    },
    "FluidAnim": {
        "categoria": "lenguaje",
        "tabla_referencia": "Benton 1967 / Arango-Lasprilla 2017",
        "expectativa_claves": "PD→percentil",
    },
}

# Pruebas de cribado/tamizaje con baremos FIJOS por diseño del instrumento
# (no más de ~10 keys aunque la prueba esté correctamente baremizada).
# Esto evita que el script marque como "cobertura_baja" instrumentos que
# intencionalmente tienen clasificación discreta (BDI-II, Lawton, Yesavage,
# Pfeffer, Hamilton, C-SSRS, Kertesz WAB, etc.).
SHORT_FORM_BAREMOS: Dict[str, str] = {
    "AdBeck": "BDI-II: 4 bandas Mínima/Leve/Moderada/Severa (Beck 1996).",
    "EscBeck": "BDI-I: 4 bandas (Beck 1988). Idem AdBeck.",
    "EscLawton": "Lawton IADL: DS/DE/DL/N (forma corta LatinAm).",
    "EscYesavage": "GDS-15: 0-15 puntos; baremo discreto.",
    "EscPfeffer": "Pfeffer FAQ: 0-30 puntos; baremo discreto.",
    "EscHamilton": "HAM-D: baremo discreto por bandas.",
    "CSSRS": "C-SSRS: nivel de riesgo discreto.",
    "EscKertesz": "WAB: 0-100 puntos; baremo discreto por cortes.",
    "MMSE": "Folstein MMSE: 0-30 puntos; baremo discreto por escolaridad.",
    "MoCA": "Nasreddine MoCA: 0-30 puntos; baremo discreto.",
    "Minimental": "Variante MMSE: baremo discreto.",
}

# Pruebas con baremo en revisión clínica — requieren override Python
# porque el dato crudo en BD es incorrecto o está codificado de forma
# heredada del Excel VBA original.
#
# F7.2 (2026-06-03): AdBeck fue corregido directamente en BD
# (autorización one-time del propietario). El override Python está
# deshabilitado (LEGACY en adbeck.py). Se retira AdBeck de esta lista.
BAREMOS_EN_REVISION: Dict[str, str] = {
    # Vacío por ahora. Próximas correcciones se agregarán aquí.
}


def _flatten_baremos(baremos: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """Aplana el árbol baterias.*.subtests.* a un dict {testId: Prueba}."""
    out: Dict[str, Dict[str, Any]] = {}
    for categoria, contenido in baremos.items():
        if categoria.startswith("_"):
            continue
        if not isinstance(contenido, dict):
            continue
        # Caso 1: baterias.infantil.NiWiscDC...
        sub = contenido.get("subtests") or contenido
        for test_id, test_def in sub.items():
            if isinstance(test_def, dict) and "baremos" in test_def:
                out[test_id] = test_def
    return out


def _auditar_prueba(test_id: str, test_def: Dict[str, Any]) -> Dict[str, Any]:
    """Audita una prueba individual y devuelve un dict con métricas."""
    info = PRUEBAS_MARCADAS.get(test_id, {})
    baremos = test_def.get("baremos", {}) or {}
    n_claves = len(baremos)
    tipo_calculo = test_def.get("tipo_calculo", "desconocido")
    tipo_metrica = test_def.get("tipo_metrica", "desconocido")

    claves_list = list(baremos.keys())
    primera_clave = claves_list[0] if claves_list else None
    ultima_clave = claves_list[-1] if claves_list else None

    # Distribución de valores
    escalares: List[float] = []
    for v in baremos.values():
        if isinstance(v, (int, float)):
            escalares.append(float(v))
        elif isinstance(v, list) and v:
            # A veces los baremos guardan [media, sd] o [PE, percentil]
            for x in v:
                if isinstance(x, (int, float)):
                    escalares.append(float(x))
                    break

    distribucion = {}
    if escalares:
        distribucion = {
            "min": min(escalares),
            "max": max(escalares),
            "media": round(statistics.mean(escalares), 2),
            "mediana": round(statistics.median(escalares), 2),
        }

    # Anomalías simples
    anomalias: List[str] = []
    if n_claves == 0:
        anomalias.append("SIN BAREMOS")
    # Cobertura baja: no aplica a SHORT_FORM_BAREMOS (cribados con baremo
    # discreto por diseño) ni a BAREMOS_EN_REVISION (override Python).
    if n_claves < 10 and test_id not in SHORT_FORM_BAREMOS and test_id not in BAREMOS_EN_REVISION:
        anomalias.append(f"cobertura_baja (n={n_claves})")
    if escalares and min(escalares) < 0:
        anomalias.append(f"valor_minimo_negativo ({min(escalares)})")
    if escalares and max(escalares) > 200:
        anomalias.append(f"valor_maximo_atipico ({max(escalares)})")

    return {
        "test_id": test_id,
        "categoria": info.get("categoria", "?"),
        "tabla_referencia": info.get("tabla_referencia", "?"),
        "expectativa": info.get("expectativa_claves", "?"),
        "tipo_calculo": tipo_calculo,
        "tipo_metrica": tipo_metrica,
        "n_claves": n_claves,
        "primera_clave": primera_clave,
        "ultima_clave": ultima_clave,
        "distribucion": distribucion,
        "anomalias": anomalias,
        "short_form": test_id in SHORT_FORM_BAREMOS,
        "en_revision": test_id in BAREMOS_EN_REVISION,
    }


def _render_markdown(reporte: Dict[str, Any]) -> str:
    """Renderiza el reporte a Markdown."""
    out: List[str] = []
    out.append("# Auditoría Detallada de Baremos — 18 Pruebas Marcadas ✅")
    out.append("")
    out.append(
        f"> **Generado:** {reporte['fecha']}  ·  "
        f"**Versión del motor:** {reporte['motor_version']}  ·  "
        f"**Total pruebas en BD:** {reporte['total_pruebas_bd']}"
    )
    out.append("")
    out.append(
        "Esta auditoría es de **sólo lectura**: NO modifica "
        "`BD_NEURO_MAESTRA.json`. Identifica cobertura, gaps y posibles "
        "anomalías en los baremos de las 18 pruebas marcadas ✅ en el "
        "`PLAN_MAESTRO_GLOBAL.md` §7.2."
    )
    out.append("")
    out.append(
        "> **Nota:** Algunas pruebas marcadas viven en "
        "`src/data/screening.js` (módulo de tamizaje) en lugar de "
        "`BD_NEURO_MAESTRA.json` (motor clínico). El presente script audita "
        "esta última fuente. La auditoría del módulo screening vive en "
        "`/audit-completo` (skill)."
    )
    out.append("")

    # Resumen ejecutivo
    out.append("## 1. Resumen ejecutivo")
    out.append("")
    out.append(f"- Pruebas auditadas: **{reporte['n_auditadas']}**")
    out.append(f"- Pruebas encontradas en BD: **{reporte['n_encontradas']}**")
    out.append(f"- Pruebas NO encontradas: **{reporte['n_no_encontradas']}**")
    n_anomalias = sum(len(p.get("anomalias", [])) for p in reporte["auditorias"])
    out.append(f"- Anomalías detectadas: **{n_anomalias}**")
    n_sin_baremos = sum(
        1 for p in reporte["auditorias"] if p.get("n_claves", 0) == 0
    )
    out.append(f"- Pruebas sin baremos: **{n_sin_baremos}**")
    out.append("")

    # Detalle por prueba
    out.append("## 2. Detalle por prueba")
    out.append("")
    out.append(
        "| Test ID | Categoría | Tipo cálculo | N claves | "
        "Min | Max | Forma | Anomalías |"
    )
    out.append("|---|---|---|---:|---:|---:|---|---|")
    for p in reporte["auditorias"]:
        dist = p.get("distribucion", {})
        anomalias_str = (
            ", ".join(p["anomalias"]) if p.get("anomalias") else "—"
        )
        forma = "✏️ revisión" if p.get("en_revision") else (
            "✔ short-form" if p.get("short_form") else "—"
        )
        out.append(
            f"| `{p['test_id']}` | {p['categoria']} | "
            f"{p['tipo_calculo']} | {p['n_claves']} | "
            f"{dist.get('min', '—')} | {dist.get('max', '—')} | "
            f"{forma} | {anomalias_str} |"
        )
    out.append("")

    # Baremos en revisión clínica (override Python)
    if BAREMOS_EN_REVISION:
        out.append("## 3. Baremos en revisión clínica (override Python)")
        out.append("")
        out.append(
            "Las siguientes pruebas tienen un baremo **heredado del Excel VBA "
            "original** que no representa clasificaciones clínicas válidas. "
            "Se aplica un override Python (`app/domain/clinical_engine/overrides/`) "
            "que se activa **antes** de la consulta a `BD_NEURO_MAESTRA.json`. "
            "Esto es parte del plan de migración F7.2 (`docs/PLAN_MIGRACION_BAREMOS.md`)."
        )
        out.append("")
        for test_id, motivo in BAREMOS_EN_REVISION.items():
            out.append(f"- **`{test_id}`** — {motivo}")
        out.append("")

    # Pruebas no encontradas
    if reporte["no_encontradas"]:
        out.append("## 4. Pruebas marcadas no encontradas en BD")
        out.append("")
        for t in reporte["no_encontradas"]:
            out.append(f"- `{t}`")
        out.append("")

    # Recomendaciones
    out.append("## 5. Recomendaciones")
    out.append("")
    out.append(
        "1. Para cada prueba con `cobertura_baja` (n<10), evaluar si la "
        "población clínica requiere más cobertura. Si no aplica, documentar "
        "y mantener."
    )
    out.append(
        "2. Para pruebas con `valor_maximo_atipico` (>200), verificar contra "
        "el manual original. NO modificar sin consulta al autor."
    )
    out.append(
        "3. Pruebas NO encontradas: evaluar si el id está mal escrito o si "
        "realmente no está implementado (ver §7.2 del plan maestro)."
    )
    out.append(
        "4. Esta auditoría debe ejecutarse antes de cada release y el "
        "reporte debe adjuntarse a la documentación clínica del sistema."
    )
    out.append("")
    out.append("---")
    out.append("")
    out.append(
        f"**Normograma aplicable:** Resolución 1995 de 1999 art. 11 (calidad "
        f"del dato clínico) · Ley 1581 de 2012 (Habeas Data) · ISO/IEC "
        f"25012 (calidad de datos)."
    )
    out.append("")
    out.append(f"**Generado por:** `scripts/audit_baremos_18.py`")
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--baremos",
        default="data/BD_NEURO_MAESTRA.json",
        help="Ruta a BD_NEURO_MAESTRA.json",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Archivo de salida (Markdown). Si se omite, imprime a stdout.",
    )
    args = parser.parse_args()

    baremos_path = Path(args.baremos)
    if not baremos_path.exists():
        print(f"ERROR: no se encontró {baremos_path}", file=sys.stderr)
        return 1

    with open(baremos_path, "r", encoding="utf-8") as f:
        bd = json.load(f)

    motor_version = "?"
    try:
        from app.core.config import settings

        motor_version = settings.app_version
    except Exception:
        pass

    # Determinar raíz de baremos
    if "baterias" in bd:
        baremos_root = bd["baterias"]
    else:
        baremos_root = bd

    flat = _flatten_baremos(baremos_root)

    auditorias: List[Dict[str, Any]] = []
    no_encontradas: List[str] = []
    for test_id in sorted(PRUEBAS_MARCADAS.keys()):
        if test_id in flat:
            auditorias.append(_auditar_prueba(test_id, flat[test_id]))
        else:
            no_encontradas.append(test_id)

    reporte = {
        "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "motor_version": motor_version,
        "total_pruebas_bd": len(flat),
        "n_auditadas": len(PRUEBAS_MARCADAS),
        "n_encontradas": len(auditorias),
        "n_no_encontradas": len(no_encontradas),
        "auditorias": auditorias,
        "no_encontradas": no_encontradas,
    }

    md = _render_markdown(reporte)
    if args.out:
        Path(args.out).write_text(md, encoding="utf-8")
        print(f"Reporte escrito en: {args.out}")
    else:
        # Configurar stdout a UTF-8 en Windows (soporta emojis / ✅)
        try:
            sys.stdout.reconfigure(encoding="utf-8")
        except Exception:
            pass
        print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
