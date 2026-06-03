"""
Variante "Inconcluso" — para evaluaciones que no pudieron completarse.

Características:
  - Sello rojo "EVALUACIÓN INCONCLUSA" en portada.
  - Sección dedicada con la **razón categórica** y **nota clínica** que el
    profesional registró al cerrar prematuramente la evaluación.
  - Tabla de pruebas con tag visual "PARCIAL" en los subtests no terminados.
  - Resultados sólo si hay puntajes calculables; si no, se omite la sección.
  - Anexo de Definiciones Operativas omitido (no aplica).
  - **Recomendaciones de continuidad** en lugar del listado completo.

Los campos ``informe_inconcluso_cat`` e ``informe_inconcluso_nota`` deben venir
en ``ReportData``. Si no están, se usan textos placeholder.
"""
from __future__ import annotations

from ..base import NeuroPDFGeneratorPro
from ..helpers import (
    callout,
    draw_paragraph,
    draw_text,
    section_title,
)
from ..theme import (
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SLATE,
    SURFACE,
    TYPE,
    WHITE,
)

RAZON_LABELS = {
    "no_colabora": "Falta de colaboración del paciente",
    "fatiga": "Fatiga / agotamiento del paciente",
    "interrupcion_medica": "Interrupción por razón médica",
    "no_entiende": "Dificultad de comprensión de instrucciones",
    "tiempo": "Restricción de tiempo de la sesión",
    "logistica": "Razón logística externa",
    "abandono": "Abandono de la evaluación",
    "otros": "Otra razón clínica",
}


class InconclusoGenerator(NeuroPDFGeneratorPro):
    VARIANT_LABEL = "Inconclusa"
    VARIANT_SUBTITLE = "Informe de Evaluación Inconclusa"
    USE_COVER = True
    INCLUDE_ANNEX = False

    def _build_cover(self, c, data) -> None:
        # Reutilizamos la portada base y añadimos sello "INCONCLUSO" encima.
        super()._build_cover(c, data)
        L = LAYOUT
        # Sello diagonal rojo arriba a la derecha
        c.saveState()
        c.translate(L.page_w - 110, L.page_h - 160)
        c.rotate(-18)
        c.setFillColorRGB(*SEMANTIC_DEFICIT)
        c.roundRect(-90, -22, 180, 44, 6, fill=1, stroke=0)
        draw_text(
            c, "EVALUACIÓN", 0, 4,
            font_name=FONT_SANS_BOLD, size=10, color=WHITE, align="center",
        )
        draw_text(
            c, "INCONCLUSA", 0, -10,
            font_name=FONT_SANS_BOLD, size=12, color=WHITE, align="center",
        )
        c.restoreState()

    def _build_pages(self, c, data) -> None:
        if self.USE_COVER:
            self._build_cover(c, data)
            c.showPage()

        y = self._page_top_with_header(c, data)
        y = self._section_razon_y_nota(c, data, y)
        y = self._section_sociodemografico(c, data, y)
        y = self._section_motivo_consulta(c, data, y)
        y = self._section_pruebas_aplicadas(c, data, y)
        y = self._section_antecedentes(c, data, y)
        y = self._section_observacion(c, data, y)
        y = self._section_resultados_parciales(c, data, y)
        y = self._section_recomendaciones_continuidad(c, data, y)
        self._section_firma(c, data, y)

    # ──────────────────────────────────────────────────────────
    # Secciones específicas
    # ──────────────────────────────────────────────────────────

    def _section_razon_y_nota(self, c, data, y: float) -> float:
        L = LAYOUT
        razon_cat = getattr(data, "informe_inconcluso_cat", "") or "otros"
        nota = (getattr(data, "informe_inconcluso_nota", "") or "").strip()
        razon_label = RAZON_LABELS.get(razon_cat, RAZON_LABELS["otros"])

        y = self._ensure_room(c, data, y, need=160)
        y = section_title(
            c, "Razón por la cual la evaluación está inconclusa",
            y, subtitle="Categoría y observación clínica",
        )
        y = callout(
            c, razon_label, L.margin, y, L.content_w,
            accent=SEMANTIC_DEFICIT, fill=SURFACE,
            title="Categoría", size=TYPE.body_sm,
        )
        y -= 6
        if nota:
            y = self._ensure_room(c, data, y, need=70)
            y = draw_paragraph(
                c, nota, L.margin, y, L.content_w,
                font_name=FONT_SERIF, size=TYPE.body, color=NAVY,
                leading=TYPE.body * 1.45,
            ) - 4
        else:
            y = draw_paragraph(
                c,
                "El profesional cerró la evaluación antes de completar el "
                "protocolo planificado, registrando la categoría anterior. "
                "No se aportó nota clínica adicional.",
                L.margin, y, L.content_w,
                font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
            ) - 4
        return y - 6

    def _section_resultados_parciales(self, c, data, y: float) -> float:
        """Si hay resultados parciales, los mostramos sin gráficos avanzados."""
        if not data.resultados:
            return y
        # Sólo pruebas con puntaje calculado
        with_score = [r for r in data.resultados
                      if r.get("puntaje_escalar") is not None
                      or r.get("z_equivalente") is not None]
        if not with_score:
            return y

        L = LAYOUT
        y = self._ensure_room(c, data, y, need=160)
        y = section_title(
            c, "Resultados Parciales",
            y, subtitle="Interpretación cautelosa — protocolo incompleto",
        )
        y = callout(
            c,
            "Los siguientes puntajes corresponden a pruebas administradas "
            "completamente. La interpretación clínica debe contemplar que el "
            "protocolo previsto no se concluyó, por lo que cualquier conclusión "
            "diagnóstica con base en estos datos será necesariamente preliminar.",
            L.margin, y, L.content_w,
            accent=SEMANTIC_DEFICIT, fill=SURFACE,
            title="Aviso interpretativo", size=TYPE.body_sm,
        )
        y -= 6
        y = self._draw_score_table(c, data, with_score, y)
        return y - 8

    def _section_recomendaciones_continuidad(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=140)
        y = section_title(
            c, "Recomendaciones de Continuidad",
            y, subtitle="Plan sugerido para completar la evaluación",
        )

        # Si el profesional registró recomendaciones específicas, las usamos.
        if data.obs_recomendaciones and data.obs_recomendaciones not in ("N/A", ""):
            y = draw_paragraph(
                c, data.obs_recomendaciones, L.margin, y, L.content_w,
                font_name=FONT_SERIF, size=TYPE.body_sm, color=NAVY,
                leading=TYPE.body_sm * 1.5,
            ) - 6

        # Plan genérico de continuidad
        plan = (
            "Se sugiere programar una sesión complementaria en un plazo no "
            "mayor a cuatro semanas para completar el protocolo iniciado, "
            "preservando la validez normativa de los puntajes ya obtenidos. "
            "En caso de cambio de circunstancias clínicas o contextuales que "
            "modifique el motivo de consulta, se recomienda reiniciar el "
            "proceso de evaluación con un nuevo encuadre."
        )
        y = draw_paragraph(
            c, plan, L.margin, y, L.content_w,
            font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
            leading=TYPE.body_sm * 1.5,
        )
        return y - 12
