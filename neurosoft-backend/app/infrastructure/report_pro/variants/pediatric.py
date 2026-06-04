"""
Variante "Pediátrica" — informe para población pediátrica.

Diferencias respecto a Pro:
  - Subtítulo "Informe Neuropsicológico Pediátrico"
  - Sección extra de **observación de juego** (cuando hay observaciones específicas)
  - Sección extra de **escala de cooperación / contingencias conductuales**
  - Antecedentes específicos pediátricos (perinatales, desarrollo) en bloque resaltado
  - Recomendaciones agrupadas con énfasis en escolar/familiar
  - Tono narrativo adaptado: en la portada y el header se usa "menor evaluado"

Las secciones específicas se activan si la HC trae texto coherente. Si no,
se omiten silenciosamente y el informe se ve igual al Pro.
"""
from __future__ import annotations

from ..base import NeuroPDFGeneratorPro
from ..helpers import (
    block_header,
    callout,
    draw_paragraph,
    section_title,
)
from ..theme import (
    FONT_SANS,
    LAYOUT,
    SLATE,
    TEAL,
    TEAL_PALE,
    TYPE,
)


class PediatricGenerator(NeuroPDFGeneratorPro):
    VARIANT_LABEL = "Pediátrica"
    VARIANT_SUBTITLE = "Informe Neuropsicológico Pediátrico"
    USE_COVER = True
    INCLUDE_ANNEX = True

    def _build_pages(self, c, data) -> None:
        if self.USE_COVER:
            self._build_cover(c, data)
            c.showPage()

        y = self._page_top_with_header(c, data)
        y = self._section_sociodemografico(c, data, y)
        y = self._section_motivo_consulta(c, data, y)
        y = self._section_antecedentes_pediatricos(c, data, y)
        y = self._section_pruebas_aplicadas(c, data, y)
        y = self._section_antecedentes(c, data, y)
        y = self._section_observacion(c, data, y)
        y = self._section_observacion_juego_y_cooperacion(c, data, y)
        y = self._section_resultados(c, data, y)
        y = self._section_sintesis(c, data, y)
        y = self._section_resumen_familia(c, data, y)
        y = self._section_impresion(c, data, y)
        y = self._section_recomendaciones(c, data, y)
        if self.INCLUDE_ANNEX:
            y = self._section_anexo(c, data, y)
        self._section_firma(c, data, y)

    # ──────────────────────────────────────────────────────────
    # Sección específica: antecedentes pediátricos resaltados
    # ──────────────────────────────────────────────────────────

    def _section_antecedentes_pediatricos(self, c, data, y: float) -> float:
        """Resalta antecedentes del desarrollo, familiares y escolares.

        Los datos vienen de los campos estándar de HC. ``familiares`` se usa
        correctamente como "antecedentes familiares" (NO como perinatales).
        Perinatales se reconstruye desde ``patologicos_medicos`` si contiene
        información gestacional.
        """
        L = LAYOUT
        # Detectar si patologicos_medicos contiene info perinatal/prenatal.
        perinatal_text = ""
        pat = (data.patologicos_medicos or "").lower()
        prenatal_keywords = (
            "embarazo", "gestación", "gestacion", "prenatal", "perinatal",
            "parto", "cesárea", "cesarea", "prematurez", "prematuro",
            "bajo peso", "hipoxia", "sufrimiento fetal", "ictericia neonatal",
        )
        if any(kw in pat for kw in prenatal_keywords):
            perinatal_text = data.patologicos_medicos

        bloques = [
            ("Perinatales y prenatales", perinatal_text),
            ("Desarrollo motor y del lenguaje", data.sensoriales_motores),
            ("Trayectoria escolar", data.escolar_laboral),
            ("Comportamiento y ánimo", data.comportamiento_animo),
            ("Antecedentes familiares", data.familiares),
        ]
        bloques = [(lbl, val) for lbl, val in bloques
                   if val and val not in ("N/A", "", "(-)", "-")]
        if not bloques:
            return y

        y = self._ensure_room(c, data, y, need=140)
        y = section_title(
            c, "Historia del Desarrollo",
            y, subtitle="Hitos relevantes en la trayectoria evolutiva",
        )
        for lbl, val in bloques:
            y = self._ensure_room(c, data, y, need=60)
            y = block_header(c, lbl, y)
            y = draw_paragraph(
                c, val, L.margin, y, L.content_w,
                font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
            ) - 6
        return y - 4

    # ──────────────────────────────────────────────────────────
    # Sección específica: observación de juego + cooperación
    # ──────────────────────────────────────────────────────────

    def _section_observacion_juego_y_cooperacion(self, c, data, y: float) -> float:
        L = LAYOUT
        # Usamos obs_emociones + obs_clinica_general como fuente heurística;
        # si existen palabras clave de juego/cooperación, lo destacamos.
        full = " ".join([
            str(data.obs_clinica_general or ""),
            str(data.obs_emociones or ""),
        ]).lower()
        marcadores = ("juego", "coopera", "rapport", "contingen", "atención conjunta",
                      "berrinche", "rabieta", "iniciativa", "imaginación")
        has_marker = any(m in full for m in marcadores)
        if not has_marker:
            return y

        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c, "Observación Conductual Pediátrica",
            y, subtitle="Cooperación, juego e interacción durante la evaluación",
        )
        text = (
            "Durante la evaluación se atendió específicamente a la calidad del "
            "rapport, la cooperación con las tareas, la respuesta a contingencias "
            "y, cuando fue pertinente, las características del juego (simbólico, "
            "funcional, paralelo). Los hallazgos relevantes se integran a "
            "continuación junto con la observación clínica general."
        )
        y = callout(
            c, text, L.margin, y, L.content_w,
            accent=TEAL, fill=TEAL_PALE,
            title="Marco observacional pediátrico",
            size=TYPE.body_sm,
        )
        return y - 8
