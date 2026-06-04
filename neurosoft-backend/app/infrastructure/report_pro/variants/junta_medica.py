"""
Variante "Junta Médica / Interconsulta" — versión ejecutiva en 2 páginas.

Características:
  - SIN portada dedicada (toda la información cabe en 1-2 páginas).
  - Header expandido con sello "Documento para Junta Médica".
  - Bloque inicial con resumen ejecutivo: motivo de interconsulta + datos clave.
  - Resultados condensados (sólo KPIs + síntesis cuantitativa).
  - Hipótesis diagnósticas + preguntas a la junta destacadas.
  - Sin antecedentes detallados ni anexo (ya conocidos por la junta).

Pensada para impresión de 2 páginas que circulan en reuniones clínicas.
"""
from __future__ import annotations

from ..base import NeuroPDFGeneratorPro
from ..charts import draw_ci_kpi_row
from ..helpers import (
    block_header,
    bullet,
    callout,
    draw_paragraph,
    section_title,
)
from ..narrative import build_strengths_weaknesses, build_synthesis_paragraphs
from ..theme import (
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SEMANTIC_SUPERIOR,
    SLATE,
    SURFACE,
    TEAL,
    TEAL_PALE,
    TYPE,
)


class JuntaMedicaGenerator(NeuroPDFGeneratorPro):
    VARIANT_LABEL = "Junta Médica"
    VARIANT_SUBTITLE = "Documento Ejecutivo para Interconsulta / Junta"
    USE_COVER = False
    INCLUDE_ANNEX = False

    def _build_pages(self, c, data) -> None:
        y = self._page_top_with_header(c, data)
        y = self._section_sello_junta(c, data, y)
        y = self._section_datos_resumen(c, data, y)
        y = self._section_motivo_interconsulta(c, data, y)
        y = self._section_resumen_ejecutivo(c, data, y)
        y = self._section_resultados_condensados(c, data, y)
        y = self._section_hipotesis_y_preguntas(c, data, y)
        y = self._section_recomendaciones(c, data, y)
        self._section_firma(c, data, y)

    # ──────────────────────────────────────────────────────────
    # Bloques específicos
    # ──────────────────────────────────────────────────────────

    def _section_sello_junta(self, c, data, y: float) -> float:
        L = LAYOUT
        # Cinta NAVY ancho completo con sello
        c.setFillColorRGB(*NAVY)
        c.rect(L.margin, y - 36, L.content_w, 36, fill=1, stroke=0)
        c.setFillColorRGB(*TEAL)
        c.rect(L.margin, y - 40, L.content_w, 4, fill=1, stroke=0)

        from ..helpers import draw_text
        draw_text(
            c, "DOCUMENTO PARA JUNTA MÉDICA", L.margin + 12, y - 18,
            font_name=FONT_SERIF_BOLD, size=TYPE.title_h2, color=TEAL_PALE,
        )
        draw_text(
            c, "Síntesis ejecutiva — apto para discusión interdisciplinaria",
            L.margin + 12, y - 30,
            font_name=FONT_SANS, size=TYPE.caption, color=TEAL_PALE,
        )

        if data.fecha_atencion:
            draw_text(
                c, data.fecha_atencion.strftime("%d / %m / %Y"),
                L.page_w - L.margin - 12, y - 22,
                font_name=FONT_SANS_BOLD, size=TYPE.body, color=TEAL_PALE,
                align="right",
            )
        return y - 50

    def _section_datos_resumen(self, c, data, y: float) -> float:
        """Datos clave en una sola fila compacta."""
        L = LAYOUT
        from ..helpers import draw_text
        # Tarjeta horizontal compacta
        c.setFillColorRGB(*SURFACE)
        c.rect(L.margin, y - 50, L.content_w, 50, fill=1, stroke=0)
        c.setStrokeColorRGB(*TEAL)
        c.setLineWidth(0.5)
        c.line(L.margin, y - 50, L.margin + L.content_w, y - 50)

        # Tres columnas: paciente · sociodemo · administrativo
        col_w = L.content_w / 3

        def _trio(label: str, value: str, x: float, y0: float) -> None:
            draw_text(
                c, label.upper(), x, y0 - 10,
                font_name=FONT_SANS_BOLD, size=TYPE.micro, color=SLATE,
            )
            draw_text(
                c, str(value or "—"), x, y0 - 24,
                font_name=FONT_SERIF, size=TYPE.body_sm, color=NAVY,
            )

        _trio("PACIENTE", data.nombre_completo, L.margin + 8, y)
        _trio("DOCUMENTO",
              f"{data.tipo_documento} {data.numero_documento}",
              L.margin + 8, y - 22)

        _trio("EDAD", data.edad_display, L.margin + col_w + 8, y)
        _trio("ESCOLARIDAD / OCUPACIÓN",
              f"{data.escolaridad}  ·  {data.ocupacion or '—'}".strip(),
              L.margin + col_w + 8, y - 22)

        _trio("PROTOCOLO", data.protocolo or "—",
              L.margin + 2 * col_w + 8, y)
        _trio("CIE-10",
              (data.codigo_cie10 or "—") + (f"  ·  {data.codigo_cie10_desc[:24]}" if data.codigo_cie10_desc else ""),
              L.margin + 2 * col_w + 8, y - 22)

        return y - 60

    def _section_motivo_interconsulta(self, c, data, y: float) -> float:
        if not data.motivo_consulta:
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=70)
        y = section_title(
            c, "Motivo de Interconsulta",
            y, subtitle="Pregunta clínica que motiva la presentación",
        )
        y = draw_paragraph(
            c, data.motivo_consulta, L.margin, y, L.content_w,
            font_name=FONT_SERIF, size=TYPE.body, color=NAVY,
            leading=TYPE.body * 1.4,
        )
        return y - 10

    def _section_resultados_condensados(self, c, data, y: float) -> float:
        if not data.resultados:
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=180)
        y = section_title(
            c, "Resultados Clave",
            y, subtitle="Síntesis cuantitativa",
        )
        # KPIs (CI compuestos)
        n_ci = sum(1 for r in data.resultados if r.get("tipo_metrica") == "ci")
        if n_ci:
            y = draw_ci_kpi_row(c, data.resultados, y) - 6

        # Síntesis narrativa (sólo 1-2 párrafos)
        paras = build_synthesis_paragraphs(
            data.resultados,
            paciente_nombre=(data.nombre_completo.split()[0] if data.nombre_completo else "El paciente"),
            protocolo=data.protocolo,
        )
        for p in paras[:2]:  # máximo 2 párrafos
            y = self._ensure_room(c, data, y, need=50)
            y = draw_paragraph(
                c, p, L.margin, y, L.content_w,
                font_name=FONT_SERIF, size=TYPE.body_sm, color=NAVY,
                leading=TYPE.body_sm * 1.5,
            ) - 4

        # Lista breve de fortalezas/debilidades
        weak, strong = build_strengths_weaknesses(data.resultados)
        if weak or strong:
            y = self._ensure_room(c, data, y, need=100)
            col_w = (L.content_w - 16) / 2
            y_w = y_s = y
            if weak:
                y_w = block_header(c, "Debilidades", y_w, color=SEMANTIC_DEFICIT)
                for item in weak[:4]:
                    y_w = bullet(c, item, L.margin, y_w, col_w) - 2
            if strong:
                y_s = block_header(c, "Fortalezas", y_s, color=SEMANTIC_SUPERIOR)
                for item in strong[:3]:
                    y_s = bullet(c, item, L.margin + col_w + 16, y_s, col_w) - 2
            y = min(y_w, y_s)
        return y - 8

    def _section_hipotesis_y_preguntas(self, c, data, y: float) -> float:
        """Impresión diagnóstica + preguntas explícitas para la junta."""
        L = LAYOUT
        has_dx = data.obs_impresion_dx and data.obs_impresion_dx not in ("N/A", "")
        if not has_dx and not data.codigo_cie10:
            return y
        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c, "Hipótesis Diagnóstica y Preguntas a la Junta",
            y, subtitle="Síntesis interpretativa",
        )
        # CIE-10
        if data.codigo_cie10:
            cie_text = f"CIE-10: {data.codigo_cie10}"
            if data.codigo_cie10_desc:
                cie_text += f"  ·  {data.codigo_cie10_desc}"
            y = callout(
                c, cie_text, L.margin, y, L.content_w,
                accent=NAVY, fill=SURFACE,
                title="Diagnóstico tentativo", size=TYPE.body_sm,
            )
            y -= 4
        if has_dx:
            y = draw_paragraph(
                c, data.obs_impresion_dx, L.margin, y, L.content_w,
                font_name=FONT_SERIF, size=TYPE.body_sm, color=NAVY,
                leading=TYPE.body_sm * 1.5,
            ) - 6
        return y - 4
