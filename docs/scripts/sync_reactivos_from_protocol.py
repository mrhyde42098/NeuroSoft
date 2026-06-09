#!/usr/bin/env python3
"""
Sync REACTIVOS Pearson (WISC-IV / WAIS-III) desde protocolos JSON oficiales.

Fuente autoritativa (en orden):
  1. Capacitaciones Clínicas/protocolos/*.json  (manual físico del clínico)
  2. neurosoft-frontend/src/data/protocols/*.json (espejo en repo)

Salida:
  neurosoft-frontend/src/data/reactivosPearson.generated.js

Uso:
  python docs/scripts/sync_reactivos_from_protocol.py
  python docs/scripts/sync_reactivos_from_protocol.py --check   # solo diff counts
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PEARSON_WISC = {
    "NiWiscSem", "NiWiscVoc", "NiWiscCom", "NiWiscLN", "NiWiscMat", "NiWiscConD",
    "NiWiscAri", "NiWisFigInc", "NiWisInf", "NiWisPalCon",
}
PEARSON_WAIS = {
    "AdSemWais", "AdWAISV", "AdWAISI", "AdWAISC", "AdWAISA",
    "AdMatr", "AdWAISFI", "AdWAISL",
}


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def _proto_path(name: str) -> Path:
    cap = ROOT / "Capacitaciones Clínicas" / "protocolos" / name
    fe = ROOT / "neurosoft-frontend" / "src" / "data" / "protocols" / name
    if cap.exists():
        return cap
    if fe.exists():
        return fe
    raise FileNotFoundError(f"No se encontró {name} en Capacitaciones ni frontend/protocols")


def _item_num(raw) -> int | str:
    if raw == "M":
        return "M"
    return int(raw)


def _verbal_items(sub: dict) -> tuple[list, dict]:
    items: list = []
    max_per: dict = {}
    for it in sub.get("items") or []:
        num = _item_num(it.get("num"))
        entry: dict = {"n": num}
        pm = it.get("punt_max")
        if isinstance(num, int) and pm == 1:
            max_per[num] = 1
        if "par" in it:
            p = it["par"]
            entry["pair"] = f"{p[0]} — {p[1]}"
        elif "palabra" in it:
            entry["word"] = re.sub(r"\s*\(.*\)\s*$", "", it["palabra"]).strip()
            if it.get("tipo") == "dibujo":
                entry["ilustrado"] = True
        elif "pregunta" in it:
            entry["q"] = it["pregunta"]
        elif "imagen" in it:
            entry["imagen"] = it["imagen"]
            if it.get("respuesta"):
                entry["guia"] = it["respuesta"]
        if it.get("tiempo_seg"):
            entry["tiempo_seg"] = it["tiempo_seg"]
        items.append(entry)
    return items, max_per


def _ln_items(sub: dict) -> list:
    out = []
    for it in sub.get("items") or []:
        intentos = it.get("intentos") or []
        trials = [{"est": t["est"], "cor": t["cor"]} for t in intentos]
        first = intentos[0] if intentos else {}
        out.append({
            "n": int(it["num"]),
            "secuencia": first.get("est", ""),
            "respuesta": first.get("cor", ""),
            "trials": trials,
        })
    return out


def _visual_consigna(sub: dict, n: int, *, matrices: bool) -> str:
    inst = (sub.get("instruccion_general") or "").strip()
    if matrices:
        base = inst or "Señale cuál de las 5 opciones completa el diseño incompleto."
        return f"{base} (lámina {n})."
    base = inst or "Señale un dibujo de cada fila que forma un grupo con los de arriba."
    return f"{base} (lámina {n})."


def _visual_item(test_id: str, n: int, lamina, sub: dict, *, matrices: bool, clave=None) -> dict:
    lamina_n = lamina if isinstance(lamina, int) else n
    item = {
        "n": n,
        "lamina": lamina,
        "consigna": _visual_consigna(sub, lamina_n, matrices=matrices),
        "stimulus_ref": {"test_id": test_id, "item_id": str(lamina)},
    }
    if clave is not None:
        item["clave"] = clave
    return item


def _mat_items(test_id: str, sub: dict) -> list:
    rc = sub.get("respuestas_correctas")
    if isinstance(rc, list):
        return [_visual_item(test_id, i, i, sub, matrices=True, clave=c) for i, c in enumerate(rc, 1)]
    if isinstance(rc, dict):
        order: list[tuple[str, int]] = []
        for label in ("A", "B", "C"):
            if label in rc:
                order.append((label, rc[label]))
        for i in range(1, 27):
            k = str(i)
            if k in rc:
                order.append((k, rc[k]))
        return [
            _visual_item(test_id, i, lab, sub, matrices=True, clave=cl)
            for i, (lab, cl) in enumerate(order, 1)
        ]
    count = sub.get("items_count") or 0
    return [_visual_item(test_id, i, i, sub, matrices=True) for i in range(1, count + 1)]


def _pistas_items(sub: dict) -> list:
    out = []
    for it in sub.get("items") or []:
        pistas = it.get("pistas") or []
        out.append({
            "n": int(it["num"]),
            "pistas": pistas,
            "respuesta": it.get("respuesta", ""),
        })
    return out


def _cond_items(test_id: str, sub: dict) -> list:
    count = sub.get("items_count") or 28
    return [_visual_item(test_id, i, i, sub, matrices=False) for i in range(1, count + 1)]


def convert_subtest(test_id: str, sub: dict, proto_id: str) -> dict | None:
    tipo = sub.get("tipo", "")
    base = {
        "requires_license": True,
        "license_publisher": "Pearson / Editorial Manual Moderno",
        "source_protocol": proto_id,
        "label": sub.get("nombre", test_id),
    }
    if tipo == "verbal_con_respuestas":
        items, max_per = _verbal_items(sub)
        raw_items = sub.get("items") or []
        max_pm = max((it.get("punt_max") or 2) for it in raw_items) if raw_items else 2
        scoring = [0, 1] if max_pm <= 1 else [0, 1, 2]
        cfg = {**base, "type": "scored_items", "scoring": scoring, "items": items}
        if max_per:
            cfg["maxPerItem"] = max_per
        return cfg
    if tipo == "visual_con_tiempo":
        items, _ = _verbal_items(sub)
        tlim = (sub.get("reglas") or {}).get("tiempo_limite_seg", 20)
        return {**base, "type": "scored_items", "scoring": [0, 1], "items": items, "tiempo_seg": tlim}
    if tipo == "ensayos_secuencias":
        return {
            **base,
            "type": "ln_sequences",
            "maxTrials": sub.get("max_ensayos", 3),
            "items": _ln_items(sub),
        }
    if tipo == "seleccion_multiple":
        return {
            **base,
            "type": "visual_cuadernillo",
            "scoring": [0, 1],
            "opciones": 5,
            "manualRef": sub.get("materiales", "Cuaderno de estímulos WISC-IV"),
            "items": _mat_items(test_id, sub),
        }
    if tipo == "verbal_pistas":
        return {
            **base,
            "type": "verbal_pistas",
            "scoring": [0, 1],
            "items": _pistas_items(sub),
        }
    if tipo == "seleccion_visual":
        return {
            **base,
            "type": "visual_cuadernillo",
            "scoring": [0, 1],
            "opciones": 0,
            "manualRef": sub.get("materiales", "Libreta de estímulos WISC-IV"),
            "items": _cond_items(test_id, sub),
        }
    # Aritmética y similares con pregunta + tiempo
    if sub.get("items") and any("pregunta" in x for x in sub["items"]):
        items, _ = _verbal_items(sub)
        return {**base, "type": "scored_items", "scoring": [0, 1], "items": items}
    return None


def build_reactivos() -> dict:
    wisc = _load_json(_proto_path("wisc_iv_protocolo.json"))
    wais = _load_json(_proto_path("wais_iii_protocolo.json"))
    out: dict = {}
    for tid in PEARSON_WISC:
        sub = wisc["subtests"].get(tid)
        if not sub:
            print(f"WARN: {tid} no en WISC protocol", file=sys.stderr)
            continue
        cfg = convert_subtest(tid, sub, "wisc_iv_colombia")
        if cfg:
            out[tid] = cfg
    for tid in PEARSON_WAIS:
        sub = wais["subtests"].get(tid)
        if not sub:
            print(f"WARN: {tid} no en WAIS protocol", file=sys.stderr)
            continue
        cfg = convert_subtest(tid, sub, "wais_iii")
        if cfg:
            out[tid] = cfg
    return out


def _js_object(data: dict) -> str:
    """Serializa a JS object literal (JSON-compatible)."""
    return json.dumps(data, ensure_ascii=False, indent=2)


def write_generated(reactivos: dict) -> Path:
    out_path = ROOT / "neurosoft-frontend" / "src" / "data" / "reactivosPearson.generated.js"
    today = date.today().isoformat()
    body = _js_object(reactivos)
    content = f"""/* AUTO-GENERADO — NO EDITAR A MANO
 * Fuente: protocolos WISC-IV / WAIS-III (JSON)
 * Regenerar: python docs/scripts/sync_reactivos_from_protocol.py
 * Sync: {today}
 * Copyright Pearson / Manual Moderno — solo usuarios con licencia (pearsonProtected.js)
 */
export const REACTIVOS_PEARSON_SYNC_DATE = "{today}";

export const REACTIVOS_PEARSON = {body};
"""
    out_path.write_text(content, encoding="utf-8")
    return out_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Solo imprimir conteos")
    args = parser.parse_args()
    reactivos = build_reactivos()
    if args.check:
        for k, v in sorted(reactivos.items()):
            n = len(v.get("items") or [])
            print(f"{k}: type={v.get('type')} items={n}")
        return 0
    path = write_generated(reactivos)
    print(f"OK: {len(reactivos)} subtests -> {path}")
    # Smoke: Semejanzas par 1
    sem = reactivos.get("NiWiscSem", {}).get("items", [])
  # find n==1
    p1 = next((x for x in sem if x.get("n") == 1), None)
    if p1:
        print(f"  NiWiscSem[1] = {p1.get('pair')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
