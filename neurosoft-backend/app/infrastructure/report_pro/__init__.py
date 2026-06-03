"""
app.infrastructure.report_pro
==============================
Generador de informes neuropsicológicos *Pro* — diseño premium con:
  - Tipografía Inter/Lora (con fallback a Helvetica/Times)
  - Paleta TEAL/NAVY (identidad NeuroSoft)
  - Portada dedicada + header/footer institucional con paginado X/Y
  - Gráficos clínicos: radar de dominios, gaussiana, discrepancias
  - Narrativa integradora derivada de los resultados
  - Variantes: Pro (ambulatorio), Pediátrica, Medicolegal, Junta Médica, Inconcluso

Entry point público:
    >>> from app.infrastructure.report_pro import generate_pro_pdf
    >>> pdf_bytes = generate_pro_pdf(report_data, template="pro")

Variantes soportadas (case-insensitive):
    "pro"          → variants/pro.py (ambulatorio adulto/escolar)
    "pediatrico"   → variants/pediatric.py
    "medicolegal"  → variants/medicolegal.py
    "junta_medica" → variants/junta_medica.py
    "inconcluso"   → variants/inconcluso.py
"""
from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.report_service import ReportData

__all__ = ["generate_pro_pdf", "VARIANTES_DISPONIBLES"]

VARIANTES_DISPONIBLES = (
    "pro",
    "pediatrico",
    "medicolegal",
    "junta_medica",
    "inconcluso",
    "therapy_closure",   # cierre/alta de proceso psicoterapéutico
    "paciente",          # versión en lenguaje claro para el paciente
)


def generate_pro_pdf(report_data: ReportData, template: str = "pro") -> bytes:
    """Despacha a la variante correcta y retorna los bytes del PDF.

    Args:
        report_data: instancia de ReportData ya construida por el use case.
        template:   identificador de la variante (lowercase). Ver
                    VARIANTES_DISPONIBLES. Si no coincide, usa "pro".
    """
    key = (template or "pro").strip().lower()
    if key == "pediatrico":
        from .variants.pediatric import PediatricGenerator
        return PediatricGenerator().generate(report_data)
    if key == "medicolegal":
        from .variants.medicolegal import MedicoLegalGenerator
        return MedicoLegalGenerator().generate(report_data)
    if key == "junta_medica":
        from .variants.junta_medica import JuntaMedicaGenerator
        return JuntaMedicaGenerator().generate(report_data)
    if key == "inconcluso":
        from .variants.inconcluso import InconclusoGenerator
        return InconclusoGenerator().generate(report_data)
    if key == "therapy_closure":
        from .variants.therapy_closure import TherapyClosureGenerator
        return TherapyClosureGenerator().generate(report_data)
    if key == "paciente":
        from .variants.paciente import PacienteGenerator
        return PacienteGenerator().generate(report_data)
    # default
    from .variants.pro import ProGenerator
    return ProGenerator().generate(report_data)
