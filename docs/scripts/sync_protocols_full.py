#!/usr/bin/env python3
"""
Fix encoding, strip legacy org refs, sync protocol JSONs, patch clinical.js REACTIVOS.
Source: Capacitaciones Clínicas/protocolos/*.json (verified vs protocolos Wechsler).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CAP = ROOT / "Capacitaciones Clínicas" / "protocolos"
FE_PROTO = ROOT / "neurosoft-frontend" / "src" / "data" / "protocols"
BE_PROTO = ROOT / "neurosoft-backend" / "data" / "protocols"
CLINICAL = ROOT / "neurosoft-frontend" / "src" / "data" / "clinical.js"

# WISC-IV Letras y Números — Manual de aplicación Wechsler (10 ítems × 3 ensayos)
WISC_LN_ITEMS = [
 {"num": 1, "intentos": [{"est": "L-1", "cor": "1-L"}] * 3},
 {"num": 2, "intentos": [{"est": "N-2", "cor": "2-N"}] * 3},
 {"num": 3, "intentos": [{"est": "B-5", "cor": "5-B"}] * 3},
 {"num": 4, "intentos": [{"est": "L-N-1", "cor": "1-L-N"}] * 3},
 {"num": 5, "intentos": [{"est": "L-N-2", "cor": "2-L-N"}] * 3},
 {"num": 6, "intentos": [{"est": "L-N-3", "cor": "3-L-N"}] * 3},
 {"num": 7, "intentos": [{"est": "F-R-3", "cor": "3-F-R"}] * 3},
 {"num": 8, "intentos": [{"est": "A-4-7", "cor": "4-7-A"}] * 3},
 {"num": 9, "intentos": [{"est": "M-S-3-4", "cor": "3-4-M-S"}] * 3},
 {"num": 10, "intentos": [{"est": "F-O-6-3", "cor": "3-6-F-O"}] * 3},
]

INS_PATTERNS = re.compile(
 r"|IN\&S|institutonys|901\.192\.434|Neurociencias y la Salud",
 re.IGNORECASE,
)

MOJIBAKE_REPLACEMENTS = (
 ("\u00c3\u00a1", "\u00e1"),
 ("\u00c3\u00a9", "\u00e9"),
 ("\u00c3\u00ad", "\u00ed"),
 ("\u00c3\u00b3", "\u00f3"),
 ("\u00c3\u00ba", "\u00fa"),
 ("\u00c3\u00b1", "\u00f1"),
 ("\u00c3\u0081", "\u00c1"),
 ("\u00c3\u0089", "\u00c9"),
 ("\u00c3\u008d", "\u00cd"),
 ("\u00c3\u0093", "\u00d3"),
 ("\u00c3\u009a", "\u00da"),
 ("\u00c3\u0091", "\u00d1"),
 ("\u00c2\u00bf", "\u00bf"),
 ("\u00e2\u20ac\u201d", "\u2014"),
 ("\u00e2\u20ac\u201c", "\u2013"),
 ("\u00e2\u20ac\u2122", "'"),
)


def fix_mojibake(text: str) -> str:
 if not isinstance(text, str):
 return text
 # Common UTF-8 Spanish mis-decodes (C3 xx read as C3 + wrong second char)
 text = (
 text.replace("\u00c3\u0161", "\u00da")
 .replace("\u00c3\u0160", "\u00da")
 .replace("\u00c3\u2030", "\u00c9")
 .replace("\u00c3\u201c", "\u00d3")
 .replace("\u00c3\u2014", "\u00d7")
 )
 if any(m in text for m in ("Ã", "â€", "Â")):
 try:
 text = text.encode("latin-1").decode("utf-8")
 except (UnicodeDecodeError, UnicodeEncodeError):
 pass
 for bad, good in MOJIBAKE_REPLACEMENTS:
 text = text.replace(bad, good)
 try:
 import ftfy # type: ignore

 return ftfy.fix_text(text)
 except ImportError:
 pass
 return text


def deep_fix(obj):
 if isinstance(obj, str):
 s = fix_mojibake(obj)
 if INS_PATTERNS.search(s):
 s = INS_PATTERNS.sub("", s)
 s = re.sub(r"\s{2,}", " ", s).strip()
 return s
 if isinstance(obj, list):
 return [deep_fix(x) for x in obj]
 if isinstance(obj, dict):
 return {k: deep_fix(v) for k, v in obj.items()}
 return obj


def normalize_protocol_meta(data: dict) -> None:
 data["institucion"] = ""
 pid = data.get("id", "")
 if isinstance(pid, str) and "_ins" in pid.lower():
 data["id"] = pid.replace("_ins_2024", "_2024").replace("_ins", "")
 name = data.get("nombre", "")
 name = re.sub(r"\s*.*$", "", name, flags=re.I)
 name = re.sub(r"\s*Colombia\s*—\s*", " — ", name)
 name = name.replace("\u00e2\u20ac\u201d", "\u2014").strip()
 if "wisc" in data.get("id", ""):
 data["nombre"] = "WISC-IV — Protocolo de aplicación (Wechsler · Manual Moderno)"
 elif "wais" in data.get("id", ""):
 data["nombre"] = "WAIS-III — Protocolo de aplicación (Wechsler · Manual Moderno)"
 elif name:
 data["nombre"] = fix_mojibake(name)


def js_str(s: str) -> str:
 return json.dumps(s, ensure_ascii=False)


def js_pair(par: list | str) -> str:
 if isinstance(par, list) and len(par) >= 2:
 return js_str(f"{par[0]} — {par[1]}")
 return js_str(str(par))


def gen_semejanzas(sub: dict, wisc: bool) -> str:
 max_per = {}
 items_js = []
 for it in sub.get("items", []):
 num = it.get("num")
 if num == "M":
 continue
 n = num
 par = it.get("par")
 if not par:
 continue
 pm = it.get("punt_max", 2)
 if pm == 1:
 max_per[int(n)] = 1
 items_js.append(f" {{n:{js_str(n)},pair:{js_pair(par)}}}")
 max_part = ""
 if max_per:
 inner = ",".join(f"{k}:{v}" for k, v in sorted(max_per.items()))
 max_part = f",maxPerItem:{{{inner}}}"
 label = "Semejanzas" if wisc else "Semejanzas WAIS-III"
 tid = "NiWiscSem" if wisc else "AdSemWais"
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1,2]"
 f"{max_part},items:[\n" + ",\n".join(items_js) + "\n ]},"
 )


def gen_vocabulario(sub: dict, tid: str, label: str) -> str:
 max_per = {}
 items_js = []
 for it in sub.get("items", []):
 n = it.get("num")
 pal = it.get("palabra", "")
 if "(" in pal:
 pal = pal.split("(")[0].strip()
 pm = it.get("punt_max", 2)
 if pm == 1 or it.get("tipo") == "dibujo":
 max_per[int(n)] = 1
 extra = ",ilustrado:true" if it.get("tipo") == "dibujo" else ""
 items_js.append(f" {{n:{n},word:{js_str(pal)}{extra}}}")
 max_part = ""
 if max_per:
 inner = ",".join(f"{k}:{v}" for k, v in sorted(max_per.items()))
 max_part = f",maxPerItem:{{{inner}}}"
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1,2]"
 f"{max_part},items:[\n" + ",\n".join(items_js) + "\n ]},"
 )


def gen_verbal_q(sub: dict, tid: str, label: str, field: str, scoring: str) -> str:
 items_js = []
 for it in sub.get("items", []):
 n = it.get("num")
 text = it.get(field, "")
 if field == "pregunta" and text.startswith("¿"):
 pass
 elif field == "pregunta" and text and not text.startswith("¿"):
 text = f"¿{text}?"
 items_js.append(f" {{n:{n},q:{js_str(text)}}}")
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:{scoring},items:[\n"
 + ",\n".join(items_js)
 + "\n ]},"
 )


def gen_figuras(sub: dict, tid: str, label: str) -> str:
 items_js = []
 for it in sub.get("items", []):
 n = it.get("num")
 img = it.get("imagen", f"Lamina {n}")
 q_text = f"{img} \u2014 \u00bfqu\u00e9 parte falta?"
 items_js.append(f" {{n:{n},q:{js_str(q_text)}}}")
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1],items:[\n"
 + ",\n".join(items_js)
 + "\n ]},"
 )


def gen_aritmetica(sub: dict, tid: str, label: str) -> str:
 items_js = []
 for it in sub.get("items", []):
 n = it.get("num")
 q = it.get("pregunta", "")
 items_js.append(f" {{n:{n},q:{js_str(q)}}}")
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1],items:[\n"
 + ",\n".join(items_js)
 + "\n ]},"
 )


def gen_matrices(sub: dict, tid: str, label: str, count: int) -> str:
 items_js = []
 for i in range(1, count + 1):
 q_text = f"Matriz {i} \u2014 completar en cuadernillo (5 opciones)"
 items_js.append(f" {{n:{i},q:{js_str(q_text)}}}")
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1],items:[\n"
 + ",\n".join(items_js)
 + "\n ]},"
 )


def gen_cond(sub: dict, tid: str, label: str, count: int) -> str:
 items_js = []
 for i in range(1, count + 1):
 q_text = f"Lamina {i} \u2014 agrupar por categoria (cuadernillo)"
 items_js.append(f" {{n:{i},q:{js_str(q_text)}}}")
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1],items:[\n"
 + ",\n".join(items_js)
 + "\n ]},"
 )


def gen_palabras_pistas(sub: dict, tid: str, label: str) -> str:
 items_js = []
 for it in sub.get("items", []):
 n = it.get("num")
 pistas = it.get("pistas", [])
 hint = pistas[0] if pistas else f"Ítem {n}"
 items_js.append(f" {{n:{n},q:{js_str(hint)}}}")
 return (
 f" {tid}:{{type:\"scored_items\",label:{js_str(label)},scoring:[0,1],items:[\n"
 + ",\n".join(items_js)
 + "\n ]},"
 )


def gen_digits(sub: dict, tid: str, label: str) -> str:
 def section(name: str, key: str, max_items: int) -> str:
 block = sub.get(key, {})
 seqs = block.get("items", [])
 parts = []
 for sq in seqs:
 a = sq.get("ensayo_a") or sq.get("a", "")
 b = sq.get("ensayo_b") or sq.get("b", "")
 parts.append(f"{{len:{sq.get('digitos', len(a.split('-')))},a:{js_str(a)},b:{js_str(b)}}}")
 return f"{{name:{js_str(name)},maxItems:{max_items},trials:2,sequences:[{','.join(parts)}]}}"

 od = section("Dígitos Directos", "orden_directo", 8)
 oi = section("Dígitos Inversos", "orden_inverso", 8)
 return (
 f" {tid}:{{type:\"digits\",label:{js_str(label)},sections:[{od},{oi}]}},"
 )


def gen_ln_items(sub: dict, tid: str, label: str, max_time: int) -> str:
 items = sub.get("items") or WISC_LN_ITEMS
 parts = []
 for it in items:
 n = it["num"]
 intentos = it.get("intentos", [])
 est = intentos[0]["est"] if intentos else f"Nivel {n}"
 trials = [i["est"] for i in intentos[:3]]
 while len(trials) < 3:
 trials.append(trials[-1] if trials else est)
 trials_js = ",".join(js_str(t) for t in trials)
 cor = intentos[0].get("cor", "") if intentos else ""
 desc = f"Números ascendente, letras A-Z · modelo {cor}"
 parts.append(
 f" {{n:{n},secuencia:{js_str(est)},desc:{js_str(desc)},trials:[{trials_js}]}}"
 )
 return (
 f" {tid}:{{type:\"items\",label:{js_str(label)},maxTime:{max_time},items:[\n"
 + ",\n".join(parts)
 + "\n ]},"
 )


def build_reactivos_blocks(wisc: dict, wais: dict) -> dict[str, str]:
 blocks = {}
 ws = wisc["subtests"]
 wa = wais["subtests"]

 blocks["NiWiscSem"] = gen_semejanzas(ws["NiWiscSem"], True)
 blocks["NiWiscVoc"] = gen_vocabulario(ws["NiWiscVoc"], "NiWiscVoc", "Vocabulario")
 blocks["NiWiscCom"] = gen_verbal_q(ws["NiWiscCom"], "NiWiscCom", "Comprensión", "pregunta", "[0,1,2]")
 blocks["NiWiscRDD"] = gen_digits(ws["NiWiscRDD"], "NiWiscRDD", "Retención de Dígitos")
 blocks["NiWisInf"] = gen_verbal_q(ws["NiWisInf"], "NiWisInf", "Información", "pregunta", "[0,1]")
 blocks["NiWiscAri"] = gen_aritmetica(ws["NiWiscAri"], "NiWiscAri", "Aritmética")
 blocks["NiWisFigInc"] = gen_figuras(ws["NiWisFigInc"], "NiWisFigInc", "Figuras Incompletas")
 blocks["NiWisPalCon"] = gen_palabras_pistas(ws["NiWisPalCon"], "NiWisPalCon", "Palabras en Contexto")
 blocks["NiWiscMat"] = gen_matrices(ws["NiWiscMat"], "NiWiscMat", "Matrices", 35)
 blocks["NiWiscConD"] = gen_cond(ws["NiWiscConD"], "NiWiscConD", "Conceptos con Dibujos", 28)

 ln_sub = dict(ws["NiWiscLN"])
 ln_sub["items"] = WISC_LN_ITEMS
 blocks["NiWiscLN"] = gen_ln_items(ln_sub, "NiWiscLN", "Letras y Números", 90)

 blocks["AdSemWais"] = gen_semejanzas(wa["AdSemWais"], False)
 blocks["AdWAISV"] = gen_vocabulario(wa["AdWAISV"], "AdWAISV", "Vocabulario WAIS-III")
 blocks["AdWAISI"] = gen_verbal_q(wa["AdWAISI"], "AdWAISI", "Información WAIS-III", "pregunta", "[0,1]")
 blocks["AdWAISC"] = gen_verbal_q(wa["AdWAISC"], "AdWAISC", "Comprensión WAIS-III", "pregunta", "[0,1,2]")
 blocks["AdWAISA"] = gen_aritmetica(wa["AdWAISA"], "AdWAISA", "Aritmética WAIS-III")
 blocks["AdWAISFI"] = gen_figuras(wa["AdWAISFI"], "AdWAISFI", "Figuras Incompletas WAIS-III")
 blocks["AdMatr"] = gen_matrices(wa["AdMatr"], "AdMatr", "Matrices WAIS-III", 26)
 blocks["AdDDir"] = gen_digits(wa["AdDDir"], "AdDDir", "Dígitos WAIS-III")
 blocks["AdWAISL"] = gen_ln_items(wa["AdWAISL"], "AdWAISL", "Letras y Números WAIS-III", 120)

 return blocks


def replace_reactivos_block(source: str, test_id: str, new_block: str) -> str:
 pattern = rf" {re.escape(test_id)}:\{{"
 m = re.search(pattern, source)
 if not m:
 raise ValueError(f"REACTIVOS block not found: {test_id}")
 start = m.start()
 depth = 0
 i = m.end() - 1
 while i < len(source):
 c = source[i]
 if c == "{":
 depth += 1
 elif c == "}":
 depth -= 1
 if depth == 0:
 end = i + 1
 if source[end : end + 1] == ",":
 end += 1
 return source[:start] + new_block + source[end:]
 i += 1
 raise ValueError(f"Unbalanced braces for {test_id}")


def process_protocol_file(path: Path) -> dict:
 raw = path.read_text(encoding="utf-8-sig")
 data = json.loads(raw)
 normalize_protocol_meta(data)
 data = deep_fix(data)
 if path.name == "wisc_iv_protocolo.json":
 data["subtests"]["NiWiscLN"]["items"] = deep_fix(WISC_LN_ITEMS)
 return data


def main() -> None:
 protocol_files = list(CAP.glob("*.json"))
 wisc_data = wais_data = None

 for path in protocol_files:
 data = process_protocol_file(path)
 out_text = json.dumps(data, ensure_ascii=False, indent=2) + "\n"
 path.write_text(out_text, encoding="utf-8")
 for dest_dir in (FE_PROTO, BE_PROTO):
 dest_dir.mkdir(parents=True, exist_ok=True)
 (dest_dir / path.name).write_text(out_text, encoding="utf-8")
 if path.name == "wisc_iv_protocolo.json":
 wisc_data = data
 if path.name == "wais_iii_protocolo.json":
 wais_data = data
 print(f"OK protocol {path.name}")

 if not wisc_data or not wais_data:
 raise SystemExit("Missing wisc/wais protocol")

 blocks = build_reactivos_blocks(wisc_data, wais_data)
 clinical = CLINICAL.read_text(encoding="utf-8")
 for tid, block in blocks.items():
 clinical = replace_reactivos_block(clinical, tid, block)
 print(f"OK REACTIVOS {tid}")

 CLINICAL.write_text(clinical, encoding="utf-8")
 print("Done — protocols + clinical.js updated")


if __name__ == "__main__":
 main()
