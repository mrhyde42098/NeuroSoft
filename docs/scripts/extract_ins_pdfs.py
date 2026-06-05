#!/usr/bin/env python3
"""Extract WISC/WAIS protocol text from IN&S PDFs for verification."""
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader  # type: ignore

DRIVE = Path(r"D:\NeuroSoftApp\Capacitaciones Clínicas\drive-download-20260322T041708Z-3-001")
OUT = Path(__file__).resolve().parents[1] / "generated"


def extract_pdf(name: str, pages: list[int] | None = None) -> str:
    path = DRIVE / name
    reader = PdfReader(str(path))
    texts = []
    indices = pages if pages else range(len(reader.pages))
    for i in indices:
        t = reader.pages[i].extract_text() or ""
        texts.append(f"\n--- PAGE {i + 1} ---\n{t}")
    return "\n".join(texts)


def find_pages(name: str, patterns: list[str], max_pages: int = 80) -> dict[str, list[int]]:
    path = DRIVE / name
    reader = PdfReader(str(path))
    found: dict[str, list[int]] = {p: [] for p in patterns}
    for i, page in enumerate(reader.pages[:max_pages]):
        t = (page.extract_text() or "").lower()
        for p in patterns:
            if p.lower() in t:
                found[p].append(i + 1)
    return found


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    wisc_path = DRIVE / "WISC IV IN&S.pdf"
    wais_path = DRIVE / "WAIS III IN&S.pdf"
    print(f"WISC pages: {len(PdfReader(str(wisc_path)).pages)}")
    print(f"WAIS pages: {len(PdfReader(str(wais_path)).pages)}")

    wisc_hits = find_pages(
        "WISC IV IN&S.pdf",
        ["Semejanzas", "Vocabulario", "Retención de dígitos", "Retencion de digitos", "Información", "Informacion"],
    )
    wais_hits = find_pages(
        "WAIS III IN&S.pdf",
        ["Semejanzas", "Vocabulario", "Información", "Informacion", "Figuras Incompletas"],
    )
    print("WISC section pages:", wisc_hits)
    print("WAIS section pages:", wais_hits)

    # Extract first hit pages for key subtests
    def around(pages: list[int], n: int = 3) -> list[int]:
        if not pages:
            return []
        start = max(0, pages[0] - 1)
        return list(range(start, start + n))

    wisc_sem_pages = around(wisc_hits.get("Semejanzas", []), 4)
    wisc_voc_pages = around(wisc_hits.get("Vocabulario", []), 6)
    wisc_rdd_pages = around(wisc_hits.get("Retención de dígitos", []) or wisc_hits.get("Retencion de digitos", []), 3)
    wisc_inf_pages = around(wisc_hits.get("Información", []) or wisc_hits.get("Informacion", []), 4)

    wais_sem_pages = around(wais_hits.get("Semejanzas", []), 3)
    wais_voc_pages = around(wais_hits.get("Vocabulario", []), 4)

    samples = {
        "wisc_semejanzas_extract.txt": extract_pdf("WISC IV IN&S.pdf", [p - 1 for p in wisc_sem_pages]),
        "wisc_vocabulario_extract.txt": extract_pdf("WISC IV IN&S.pdf", [p - 1 for p in wisc_voc_pages]),
        "wisc_digitos_extract.txt": extract_pdf("WISC IV IN&S.pdf", [p - 1 for p in wisc_rdd_pages]),
        "wisc_informacion_extract.txt": extract_pdf("WISC IV IN&S.pdf", [p - 1 for p in wisc_inf_pages]),
        "wais_semejanzas_extract.txt": extract_pdf("WAIS III IN&S.pdf", [p - 1 for p in wais_sem_pages]),
        "wais_vocabulario_extract.txt": extract_pdf("WAIS III IN&S.pdf", [p - 1 for p in wais_voc_pages]),
    }

    for fname, content in samples.items():
        out = OUT / fname
        out.write_text(content, encoding="utf-8")
        print(f"Wrote {out} ({len(content)} chars)")

    # Quick compare Semejanzas item 1
    sem_text = samples["wisc_semejanzas_extract.txt"]
    for needle in ["Leche", "Agua", "Rojo", "Azul", "Gato", "Ratón", "Manzana", "Banano"]:
        print(f"  Sem WISC '{needle}':", "YES" if needle.lower() in sem_text.lower() else "NO")

    voc_text = samples["wisc_vocabulario_extract.txt"]
    for needle in ["Sombrilla", "Reloj", "Ladrón", "Obedecer", "Coche", "Cubeta"]:
        print(f"  Voc WISC '{needle}':", "YES" if needle.lower() in voc_text.lower() else "NO")


if __name__ == "__main__":
    main()
