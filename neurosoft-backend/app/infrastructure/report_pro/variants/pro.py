"""
Variante "Pro" — ambulatorio adulto/escolar.

Es la implementación canónica del informe Pro: portada + sociodemográfico +
motivo + antecedentes + observación + resultados (con todos los gráficos) +
síntesis integradora + impresión + recomendaciones + anexo + firma.

Hereda de ``NeuroPDFGeneratorPro`` sin sobreescribir ``_build_pages`` — los
defaults de la base ya producen la salida Pro completa.
"""

from __future__ import annotations

from ..base import NeuroPDFGeneratorPro


class ProGenerator(NeuroPDFGeneratorPro):
    VARIANT_LABEL = "Profesional"
    VARIANT_SUBTITLE = "Informe de Evaluación Neuropsicológica"
    USE_COVER = True
    INCLUDE_ANNEX = True
    INCLUDE_SINTESIS = True
    FAMILY_SUMMARY_BEFORE_RESULTS = True
    SCORE_TABLE_QUALITATIVE = True
