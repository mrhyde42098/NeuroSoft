"""
Variante "Medicolegal" — informe para contextos forenses o pericial.

Características distintivas:
  - Bloque dedicado a **validez de síntomas** (Rey-15, TOMM, MMPI-2-RF, etc.).
  - Sección de **discusión sobre aculturación y escolaridad** (riesgos
    interpretativos en población colombiana con baja escolaridad).
  - Encabezado con sello legal y referencia a la solicitud / autoridad.
  - Sección "Alcance del informe" obligatoria (limita lo que se concluye).
  - El anexo siempre incluye definiciones operativas.

Las secciones nuevas se intentan poblar de la HC (campos ``obs_*``). Si no
hay contenido relevante, se incluye texto institucional por defecto.
"""
from __future__ import annotations

from ..base import NeuroPDFGeneratorPro
from ..helpers import (
    callout,
    draw_paragraph,
    section_title,
)
from ..theme import (
    FONT_SERIF,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SURFACE,
    TYPE,
)

VALIDEZ_TEMPLATE = (
    "No se incluyeron pruebas formales de validez de síntomas (PVT/SVT) en esta "
    "evaluación. La interpretación se realiza asumiendo que el paciente "
    "colaboró con esfuerzo óptimo, según la observación clínica directa. "
    "Para usos forenses, periciales o cuando hay incentivos secundarios "
    "evidentes, se recomienda complementar este informe con pruebas dedicadas "
    "de validez (p. ej. Rey-15, TOMM, MMPI-2-RF F/Fp scales)."
)

ACULTURACION_TEMPLATE = (
    "Los baremos empleados corresponden a la población colombiana cuando estuvo "
    "disponible (ENI-2, Neuronorma Colombia, Arango-Lasprilla & Rivera, 2017). "
    "Para pruebas sin normas locales se utilizaron las referencias originales, "
    "ajustando la interpretación al perfil sociocultural y escolar del "
    "evaluado. En contextos forenses esta consideración cobra especial "
    "relevancia: el desempeño puede verse modulado por escolaridad <8 años, "
    "bilingüismo, lengua materna no española o lateralidad mixta."
)

ALCANCE_TEMPLATE = (
    "Este informe describe el funcionamiento cognitivo y conductual del "
    "evaluado en el momento de la evaluación. No constituye por sí mismo "
    "un dictamen médico-legal ni de imputabilidad. La interpretación de los "
    "hallazgos en el marco de un proceso judicial o administrativo es "
    "competencia exclusiva de la autoridad o el equipo pericial al que se "
    "remite, quienes deberán integrarlo con la totalidad del acervo probatorio."
)


class MedicoLegalGenerator(NeuroPDFGeneratorPro):
    VARIANT_LABEL = "Medicolegal"
    VARIANT_SUBTITLE = "Informe Neuropsicológico para Contexto Pericial"
    USE_COVER = True
    INCLUDE_ANNEX = True

    def _build_pages(self, c, data) -> None:
        if self.USE_COVER:
            self._build_cover(c, data)
            c.showPage()

        y = self._page_top_with_header(c, data)
        y = self._section_alcance(c, data, y)
        y = self._section_sociodemografico(c, data, y)
        y = self._section_motivo_consulta(c, data, y)
        y = self._section_pruebas_aplicadas(c, data, y)
        y = self._section_antecedentes(c, data, y)
        y = self._section_observacion(c, data, y)
        y = self._section_validez_sintomas(c, data, y)
        y = self._section_resultados(c, data, y)
        y = self._section_aculturacion(c, data, y)
        y = self._section_sintesis(c, data, y)
        y = self._section_resumen_familia(c, data, y)
        y = self._section_impresion(c, data, y)
        y = self._section_recomendaciones(c, data, y)
        if self.INCLUDE_ANNEX:
            y = self._section_anexo(c, data, y)
        self._section_firma(c, data, y)

    # ──────────────────────────────────────────────────────────
    # Secciones específicas
    # ──────────────────────────────────────────────────────────

    def _section_alcance(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c, "Alcance del Informe",
            y, subtitle="Limitaciones y propósito del presente documento",
        )
        y = callout(
            c, ALCANCE_TEMPLATE, L.margin, y, L.content_w,
            accent=NAVY, fill=SURFACE, title="Lectura del informe", size=TYPE.body_sm,
        )
        return y - 8

    def _section_validez_sintomas(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=130)
        y = section_title(
            c, "Validez de Síntomas y Esfuerzo",
            y, subtitle="Consideración crítica para informe pericial",
        )
        y = callout(
            c, VALIDEZ_TEMPLATE, L.margin, y, L.content_w,
            accent=SEMANTIC_DEFICIT, fill=SURFACE,
            title="Advertencia metodológica", size=TYPE.body_sm,
        )
        return y - 8

    def _section_aculturacion(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=130)
        y = section_title(
            c, "Consideraciones de Aculturación y Escolaridad",
            y, subtitle="Modulación cultural y educativa de los hallazgos",
        )
        y = draw_paragraph(
            c, ACULTURACION_TEMPLATE, L.margin, y, L.content_w,
            font_name=FONT_SERIF, size=TYPE.body, color=NAVY,
            leading=TYPE.body * 1.45,
        )
        return y - 12
