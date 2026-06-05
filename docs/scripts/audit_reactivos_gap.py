#!/usr/bin/env python3
"""Gap analysis: Capacitaciones protocolos vs clinical.js REACTIVOS."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    cap_wisc = load_json(ROOT / "Capacitaciones Clínicas/protocolos/wisc_iv_protocolo.json")
    cap_wais = load_json(ROOT / "Capacitaciones Clínicas/protocolos/wais_iii_protocolo.json")
    clinical = (ROOT / "neurosoft-frontend/src/data/clinical.js").read_text(encoding="utf-8")

    placeholders = re.findall(r"(\w+):\{[^}]*requires_protocol_text:true", clinical)
    print("=== REACTIVOS con placeholder (requires_protocol_text) ===")
    for t in placeholders:
        print(f"  {t}")

    print("\n=== WISC — subtests en Capacitaciones ===")
    for sid, sub in cap_wisc["subtests"].items():
        items = sub.get("items", [])
        print(f"  {sid}: {sub.get('nombre')} | items={len(items)} | tipo={sub.get('tipo')}")

    print("\n=== WAIS — subtests en Capacitaciones ===")
    for sid, sub in cap_wais["subtests"].items():
        items = sub.get("items", [])
        extra = ""
        if "orden_directo" in sub:
            extra += f" OD={len(sub['orden_directo']['items'])}"
        if "orden_inverso" in sub:
            extra += f" OI={len(sub['orden_inverso']['items'])}"
        if "respuestas_correctas" in sub:
            extra += f" matrices={len(sub['respuestas_correctas'])}"
        print(f"  {sid}: {sub.get('nombre')} | items={len(items)}{extra}")

    # Semejanzas WISC compare
    sem_cap = cap_wisc["subtests"]["NiWiscSem"]["items"]
    sem_pairs_cap = [f"{i.get('num')}: {i.get('par')}" for i in sem_cap if "par" in i]
    print("\n=== NiWiscSem — pares en Capacitaciones (muestra) ===")
    for p in sem_pairs_cap[:5]:
        print(f"  {p}")
    print(f"  ... total pares: {len(sem_pairs_cap)}")

    # Extract clinical sem pairs
    m = re.search(r"NiWiscSem:\{[^}]+items:\[(.*?)\]\}", clinical, re.S)
    if m:
        pairs_cl = re.findall(r'pair:"([^"]+)"', m.group(1))
        print("\n=== NiWiscSem — pares en clinical.js ===")
        for i, p in enumerate(pairs_cl[:5], 1):
            print(f"  {i}: {p}")
        print(f"  ... total: {len(pairs_cl)}")


if __name__ == "__main__":
    main()
