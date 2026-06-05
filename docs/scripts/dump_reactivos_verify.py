#!/usr/bin/env python3
"""Dump REACTIVOS WISC/WAIS for human verification."""
import json
import re
from pathlib import Path

CLINICAL = Path(__file__).resolve().parents[2] / "neurosoft-frontend" / "src" / "data" / "clinical.js"
text = CLINICAL.read_text(encoding="utf-8")

IDS = [
    "NiWiscSem", "NiWiscVoc", "NiWiscCom", "NiWiscRDD", "NiWisInf", "NiWiscAri",
    "NiWisFigInc", "NiWisPalCon", "NiWiscMat", "NiWiscConD", "NiWiscLN",
    "AdSemWais", "AdWAISV", "AdWAISI", "AdWAISC", "AdWAISA", "AdWAISFI",
    "AdMatr", "AdDDir", "AdWAISL",
]


def extract_block(body: str, tid: str) -> str | None:
    m = re.search(rf"  {re.escape(tid)}:\{{", body)
    if not m:
        return None
    d = 0
    j = m.end() - 1
    while j < len(body):
        if body[j] == "{":
            d += 1
        elif body[j] == "}":
            d -= 1
            if d == 0:
                return body[m.start() : j + 1]
        j += 1
    return None


m = re.search(r"export const REACTIVOS\s*=\s*\{", text)
start = m.end()
depth = 1
i = start
while i < len(text) and depth:
    if text[i] == "{":
        depth += 1
    elif text[i] == "}":
        depth -= 1
    i += 1
body = text[start : i - 1]

for tid in IDS:
    block = extract_block(body, tid)
    if not block:
        print(f"\n### {tid}\nMISSING\n")
        continue
    typ = re.search(r'type:"([^"]+)"', block)
    placeholder = "requires_protocol_text:true" in block
    print(f"\n### {tid}")
    print(f"- type: {typ.group(1) if typ else '?'}")
    print(f"- placeholder: {placeholder}")
    pairs = re.findall(r"\{n:(\d+),pair:\"([^\"]+)\"\}", block)
    if pairs:
        for n, p in pairs:
            print(f"  {n}. {p}")
        continue
    words = re.findall(r"\{n:(\d+),word:\"([^\"]+)\"", block)
    if words:
        for n, w in words:
            il = ", ilustrado" if f"n:{n},word:" in block and "ilustrado:true" in block.split(f"n:{n}")[1][:40] else ""
            print(f"  {n}. {w}{il}")
        continue
    qs = re.findall(r"\{n:(\d+),q:\"([^\"]+)\"\}", block)
    if qs and tid not in ("NiWiscMat", "NiWiscConD", "AdMatr"):
        for n, q in qs:
            print(f"  {n}. {q}")
        continue
    if tid in ("NiWiscMat", "AdMatr", "NiWiscConD"):
        for n, q in qs:
            print(f"  {n}. {q}")
        continue
    if tid in ("NiWiscRDD", "AdDDir"):
        for sec in re.finditer(
            r'name:"([^"]+)".*?sequences:\[(.*?)\]\}(?:,\{name:|\])',
            block,
            re.S,
        ):
            name = sec.group(1)
            seqs = re.findall(r'a:"([^"]+)",b:"([^"]+)"', sec.group(2))
            print(f"  [{name}]")
            for i, (a, b) in enumerate(seqs, 1):
                print(f"    {i}. A={a}  B={b}")
        continue
    if tid in ("NiWiscLN", "AdWAISL"):
        for item in re.finditer(
            r'\{n:(\d+),secuencia:"([^"]+)"[^}]*trials:\[([^\]]+)\]',
            block,
        ):
            print(f"  {item.group(1)}. est={item.group(2)}  trials={item.group(3)}")
        continue
    figs = re.findall(r"\{n:(\d+),q:\"([^\"]+)\"\}", block)
    if figs:
        for n, q in figs:
            print(f"  {n}. {q}")
