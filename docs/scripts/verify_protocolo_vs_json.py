#!/usr/bin/env python3
"""Compare protocol PDF extracts vs JSON protocol vs clinical.js REACTIVOS."""
import json
import re
from pathlib import Path

ROOT = Path(r"D:\NeuroSoftApp")
JSON_WISC = ROOT / "Capacitaciones Clínicas/protocolos/wisc_iv_protocolo.json"
JSON_WAIS = ROOT / "Capacitaciones Clínicas/protocolos/wais_iii_protocolo.json"
CLINICAL = ROOT / "neurosoft-frontend/src/data/clinical.js"
PDF_SEM = ROOT / "docs/generated/wisc_semejanzas_extract.txt"
PDF_DIG = ROOT / "docs/generated/wisc_digitos_extract.txt"


def load_json(p: Path) -> dict:
 return json.loads(p.read_text(encoding="utf-8-sig"))


def sem_pairs_from_json(data: dict) -> list[str]:
 items = data["subtests"]["NiWiscSem"]["items"]
 out = []
 for it in items:
 if "par" in it:
 par = it["par"]
 if isinstance(par, list):
 out.append(f"{par[0]} — {par[1]}")
 else:
 out.append(str(par))
 return out


def sem_pairs_from_clinical(text: str) -> list[str]:
 m = re.search(r"NiWiscSem:\{[^}]+items:\[(.*?)\]\}", text, re.S)
 if not m:
 return []
 return re.findall(r'pair:"([^"]+)"', m.group(1))


def voc_words_from_json(data: dict) -> list[str]:
 return [it.get("palabra", "").split("(")[0].strip() for it in data["subtests"]["NiWiscVoc"]["items"]]


def voc_words_from_clinical(text: str) -> list[str]:
 m = re.search(r"NiWiscVoc:\{[^}]+items:\[(.*?)\]\}", text, re.S)
 if not m:
 return []
 return re.findall(r'word:"([^"]+)"', m.group(1))


def digit_sequences_json(data: dict) -> dict:
 rdd = data["subtests"]["NiWiscRDD"]
 od = [(it["ensayo_a"], it["ensayo_b"]) for it in rdd["orden_directo"]["items"]]
 oi = [(it["ensayo_a"], it["ensayo_b"]) for it in rdd["orden_inverso"]["items"]]
 return {"directo": od, "inverso": oi}


def digit_sequences_clinical(text: str) -> dict:
 m = re.search(r"NiWiscRDD:\{.*?sections:\[(.*?)\]\}", text, re.S)
 if not m:
 return {"directo": [], "inverso": []}
 block = m.group(1)
 sections = re.findall(r"sequences:\[(.*?)\]", block, re.S)
 out = {"directo": [], "inverso": []}
 keys = ["directo", "inverso"]
 for i, sec in enumerate(sections[:2]):
 seqs = re.findall(r'a:"([^"]+)",b:"([^"]+)"', sec)
 out[keys[i]] = seqs
 return out


def pdf_contains_pairs(pdf_text: str, pairs: list[str]) -> dict[str, bool]:
 return {p: p.replace(" — ", " ").replace("—", " ").split()[0].lower() in pdf_text.lower() for p in pairs[:5]}


def main() -> None:
 wisc = load_json(JSON_WISC)
 clinical = CLINICAL.read_text(encoding="utf-8")

 j_sem = sem_pairs_from_json(wisc)
 c_sem = sem_pairs_from_clinical(clinical)
 j_voc = voc_words_from_json(wisc)
 c_voc = voc_words_from_clinical(clinical)
 j_dig = digit_sequences_json(wisc)
 c_dig = digit_sequences_clinical(clinical)

 pdf_sem = PDF_SEM.read_text(encoding="utf-8") if PDF_SEM.exists() else ""
 pdf_dig = PDF_DIG.read_text(encoding="utf-8") if PDF_DIG.exists() else ""

 print("=== NiWiscSem: JSON vs PDF de protocolo ===")
 for i, p in enumerate(j_sem[:5]):
 in_pdf = j_sem[i].split("—")[0].strip() in pdf_sem
 print(f" JSON {i+1}: {p} | PDF: {'OK' if in_pdf else 'MISSING'}")

 print("\n=== NiWiscSem: JSON vs clinical.js ===")
 print(f" JSON count: {len(j_sem)} | clinical count: {len(c_sem)}")
 for i in range(min(len(j_sem), len(c_sem))):
 match = j_sem[i].lower().replace(" ", "") == c_sem[i].lower().replace(" ", "")
 if not match:
 print(f" MISMATCH #{i+1}: JSON={j_sem[i]!r} | clinical={c_sem[i]!r}")
 if len(j_sem) != len(c_sem):
 print(f" COUNT DIFF: JSON has {len(j_sem)}, clinical has {len(c_sem)}")

 print("\n=== NiWiscVoc: JSON vs clinical.js (first 15) ===")
 print(f" JSON count: {len(j_voc)} | clinical count: {len(c_voc)}")
 for i in range(min(15, len(j_voc), len(c_voc))):
 jw = j_voc[i].split()[0] if j_voc[i] else ""
 cw = c_voc[i]
 ok = jw.lower() in cw.lower() or cw.lower() in jw.lower()
 if not ok:
 print(f" MISMATCH #{i+1}: JSON={jw!r} | clinical={cw!r}")

 print("\n=== NiWiscRDD directo item 1 ===")
 print(f" JSON: {j_dig['directo'][0]}")
 print(f" clinical: {c_dig['directo'][0] if c_dig['directo'] else 'N/A'}")
 print(f" PDF has 2-9 and 4-6: {'2 – 9' in pdf_dig or '2-9' in pdf_dig}")

 print("\n=== NiWiscRDD inverso item 1 ===")
 print(f" JSON: {j_dig['inverso'][0]}")
 print(f" clinical: {c_dig['inverso'][0] if c_dig['inverso'] else 'N/A'}")
 print(f" PDF has 2-1 and 1-3: {'2 – 1' in pdf_dig or '2-1' in pdf_dig}")


if __name__ == "__main__":
 main()
