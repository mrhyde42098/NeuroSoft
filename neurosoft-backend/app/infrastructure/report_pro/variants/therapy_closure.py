"""
Variante "Cierre/Alta terapÃ©utica" â€” para finalizar un proceso de psicoterapia.

A diferencia del informe Pro de evaluaciÃ³n neuropsicolÃ³gica, este informe
documenta el CIERRE de un plan terapÃ©utico (CBT, EMDR, sistÃ©mica, etc.) y
contiene:
  - Portada con sello "CIERRE TERAPÃ‰UTICO" en lugar del de evaluaciÃ³n
  - Motivo de cierre (alta, abandono, derivaciÃ³n, cambio de terapeuta)
  - Enfoque clÃ­nico utilizado y duraciÃ³n real del proceso
  - Objetivos terapÃ©uticos planteados vs cumplimiento alcanzado
  - Resumen narrativo de la evoluciÃ³n sesiÃ³n-a-sesiÃ³n
  - EvaluaciÃ³n de riesgo longitudinal (si hubo)
  - Recomendaciones de seguimiento post-alta
  - Sin grÃ¡ficos psicomÃ©tricos (no aplican)

Campos esperados en ReportData (todos opcionales â€” usa placeholders si faltan):
  therapy_plan       â€” dict con enfoque, diagnostico, motivo_consulta, fechas
  therapy_objectives â€” list de dicts con descripcion, progreso_pct, estado
  therapy_sessions_count â€” int total de sesiones realizadas
  therapy_risk_history   â€” list con niveles de riesgo a lo largo del proceso
  therapy_motivo_cierre  â€” str categorico
  therapy_nota_cierre    â€” str narrativo del clÃ­nico
"""
from __future__ import annotations

from ..base import NeuroPDFGeneratorPro
from ..helpers import (
    block_header,
    bullet,
    callout,
    draw_paragraph,
    draw_text,
    section_title,
)
from ..implicaciones import dominios_con_implicaciones
from ..theme import (
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SEMANTIC_OK,
    SEMANTIC_WARN,
    SLATE,
    SURFACE,
    WHITE,
)

# Plum â€” color del mÃ³dulo terapia (consistente con frontend)
PLUM = (0.427, 0.157, 0.847)  # #6D28D9


MOTIVO_CIERRE_LABELS = {
    "alta": "Alta por cumplimiento de objetivos terapÃ©uticos",
    "abandono": "Abandono del proceso por parte del paciente",
    "derivacion": "DerivaciÃ³n a otro profesional o servicio",
    "cambio_terapeuta": "Cambio de terapeuta por razones del paciente",
    "fin_contrato": "FinalizaciÃ³n del contrato terapÃ©utico previsto",
    "otros": "Otra razÃ³n clÃ­nica documentada",
}

ENFOQUE_LABELS = {
    "cbt": "Terapia Cognitivo-Conductual (CBT)",
    "act": "Terapia de AceptaciÃ³n y Compromiso (ACT)",
    "dbt": "Terapia DialÃ©ctico-Conductual (DBT)",
    "emdr": "EMDR (DesensibilizaciÃ³n por Movimientos Oculares)",
    "mbct": "Terapia Cognitiva Basada en Mindfulness (MBCT)",
    "ipt": "Psicoterapia Interpersonal (IPT)",
    "esquemas": "Terapia Centrada en Esquemas",
    "tf_cbt": "TF-CBT (CBT Focalizada en Trauma)",
    "cpt": "Terapia de Procesamiento Cognitivo (CPT)",
    "gottman": "MÃ©todo Gottman (pareja)",
    "eft_pareja": "Terapia Centrada en Emociones para Parejas (EFT-C)",
    "sistemica_estructural": "Terapia Estructural Familiar",
    "duelo_worden": "Modelo de Worden â€” 4 Tareas del Duelo",
    "duelo_neimeyer": "ReconstrucciÃ³n de Significado (Neimeyer)",
    "pgt": "Terapia de Duelo Prolongado (PGT)",
    "entrevista_motivacional": "Entrevista Motivacional",
    "humanistica": "Terapia Centrada en la Persona (Rogers)",
    "logoterapia": "Logoterapia (Frankl)",
    "compasion_cft": "Terapia Centrada en la CompasiÃ³n (CFT)",
}


class TherapyClosureGenerator(NeuroPDFGeneratorPro):
    """Variante de cierre de proceso terapÃ©utico."""

    VARIANT_LABEL = "Cierre TerapÃ©utico"
    VARIANT_SUBTITLE = "Informe de Cierre del Proceso PsicoterapÃ©utico"
    USE_COVER = True
    INCLUDE_ANNEX = False

    def _build_cover(self, c, data) -> None:
        """Portada con sello PLUM 'CIERRE TERAPÃ‰UTICO' en lugar del estÃ¡ndar."""
        super()._build_cover(c, data)
        L = LAYOUT
        # Sello diagonal violeta arriba a la derecha
        c.saveState()
        c.translate(L.page_w - 120, L.page_h - 170)
        c.rotate(-15)
        c.setFillColorRGB(*PLUM)
        c.roundRect(-95, -24, 190, 48, 6, fill=1, stroke=0)
        draw_text(
            c, "CIERRE", 0, 6,
            font_name=FONT_SANS_BOLD, size=11, color=WHITE, align="center",
        )
        draw_text(
            c, "TERAPÃ‰UTICO", 0, -10,
            font_name=FONT_SANS_BOLD, size=12, color=WHITE, align="center",
        )
        c.restoreState()

    def _build_pages(self, c, data) -> None:
        """Estructura del informe de cierre. No usa grÃ¡ficos de scoring."""
        if self.USE_COVER:
            self._build_cover(c, data)
            c.showPage()

        # 1. Datos del paciente + datos del proceso
        y = self._page_top_with_header(c, data)
        y = self._section_sociodemografico(c, data, y)

        # 2. Marco del proceso terapÃ©utico
        y = self._ensure_room(c, data, y, 180)
        y = section_title(c, "Marco del proceso", y)
        y = self._draw_marco_terapeutico(c, data, y)

        # 3. Motivo de cierre â€” bloque destacado
        y = self._ensure_room(c, data, y, 120)
        y = section_title(c, "Motivo del cierre", y)
        y = self._draw_motivo_cierre(c, data, y)

        # 4. Objetivos planteados vs cumplimiento
        y = self._ensure_room(c, data, y, 200)
        y = section_title(c, "Objetivos terapÃ©uticos: cumplimiento", y)
        y = self._draw_objetivos_evolucion(c, data, y)

        # 5. EvoluciÃ³n narrativa (sÃ­ntesis del proceso)
        y = self._ensure_room(c, data, y, 150)
        y = section_title(c, "SÃ­ntesis del proceso", y)
        y = self._draw_sintesis_proceso(c, data, y)

        # 6. Historial de riesgo (si aplica)
        if getattr(data, "therapy_risk_history", None):
            y = self._ensure_room(c, data, y, 100)
            y = section_title(c, "EvaluaciÃ³n longitudinal de riesgo", y)
            y = self._draw_riesgo_longitudinal(c, data, y)

        # 6b. Implicaciones vida diaria (si hay resultados de evaluaciÃ³n disponibles)
        if getattr(data, "resultados", None):
            y = self._ensure_room(c, data, y, 140)
            y = section_title(c, "Implicaciones para la vida diaria", y)
            y = self._draw_implicaciones_diarias(c, data, y)

        # 7. Recomendaciones post-alta
        y = self._ensure_room(c, data, y, 150)
        y = section_title(c, "Recomendaciones de seguimiento", y)
        y = self._draw_recomendaciones_cierre(c, data, y)

        # 8. Firma
        self._section_firma(c, data, y)

    # â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€ Secciones nuevas â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€

    def _draw_marco_terapeutico(self, c, data, y: float) -> float:
        """Bloque con enfoque, fechas, duraciÃ³n real y diagnÃ³stico."""
        L = LAYOUT
        plan = getattr(data, "therapy_plan", {}) or {}
        enfoque_id = plan.get("enfoque_principal", "")
        enfoque_label = ENFOQUE_LABELS.get(enfoque_id, enfoque_id or "Enfoque no especificado")
        dx_principal = plan.get("diagnostico_principal", "â€”")
        dx_secundario = plan.get("diagnostico_secundario", "")
        motivo = plan.get("motivo_consulta", "â€”")
        fecha_inicio = plan.get("fecha_inicio", "â€”")
        fecha_cierre = plan.get("fecha_cierre", "â€”")
        sesiones_real = getattr(data, "therapy_sessions_count", 0)
        duracion_estim = plan.get("duracion_estimada_sesiones", "â€”")

        # PequeÃ±a tabla descriptiva
        rows = [
            ("Enfoque clÃ­nico principal", enfoque_label),
            ("DiagnÃ³stico CIE-10", f"{dx_principal}{f' Â· {dx_secundario}' if dx_secundario else ''}"),
            ("Fecha de inicio", str(fecha_inicio)),
            ("Fecha de cierre", str(fecha_cierre)),
            ("Sesiones realizadas / estimadas", f"{sesiones_real} / {duracion_estim}"),
        ]
        for label, value in rows:
            draw_text(c, label, L.margin, y - 4,
                      font_name=FONT_SANS_BOLD, size=8, color=SLATE)
            draw_text(c, str(value), L.margin + 180, y - 4,
                      font_name=FONT_SANS, size=10, color=NAVY)
            y -= 16

        # Motivo de consulta (texto largo, pÃ¡rrafo)
        y -= 4
        draw_text(c, "Motivo de consulta inicial:", L.margin, y - 4,
                  font_name=FONT_SANS_BOLD, size=8, color=SLATE)
        y -= 16
        y = draw_paragraph(c, motivo, L.margin, y,
                           w=L.page_w - L.margin - L.margin,
                           font_name=FONT_SERIF, size=10, color=NAVY)
        return y - 8

    def _draw_motivo_cierre(self, c, data, y: float) -> float:
        """Callout destacado con el motivo de cierre + nota narrativa."""
        motivo_cat = getattr(data, "therapy_motivo_cierre", None)
        label = MOTIVO_CIERRE_LABELS.get(motivo_cat, motivo_cat or "Sin especificar")
        nota = getattr(data, "therapy_nota_cierre", "") or "Sin nota narrativa del clínico al cierre."

        # Color según motivo — alta=verde, abandono=ámbar, derivación=ocean, otros=plum
        color = SEMANTIC_OK
        if motivo_cat == "abandono":
            color = SEMANTIC_WARN
        elif motivo_cat == "derivacion":
            color = (0.012, 0.412, 0.631)  # ocean
        elif motivo_cat in ("cambio_terapeuta",):
            color = SLATE

        L = LAYOUT
        y = callout(c, label, L.margin, y, L.content_w, accent=color)
        y -= 4
        y = draw_paragraph(c, nota, LAYOUT.margin, y,
                           w=LAYOUT.page_w - LAYOUT.margin - LAYOUT.margin,
                           font_name=FONT_SERIF, size=10, color=NAVY)
        return y - 8

    def _draw_objetivos_evolucion(self, c, data, y: float) -> float:
        """Lista de objetivos con barra de progreso por cada uno."""
        L = LAYOUT
        objetivos = getattr(data, "therapy_objectives", []) or []
        if not objetivos:
            draw_text(c, "No se documentaron objetivos terapÃ©uticos formalmente.",
                      L.margin, y - 4,
                      font_name=FONT_SERIF, size=10, color=SLATE)
            return y - 24

        for i, obj in enumerate(objetivos, 1):
            desc = obj.get("descripcion", "")
            progreso = int(obj.get("progreso_pct", 0) or 0)
            estado = obj.get("estado", "activo")
            criterios = obj.get("criterios_medibles", "")

            # NÃºmero + descripciÃ³n
            draw_text(c, f"{i:02d}", L.margin, y - 4,
                      font_name=FONT_SERIF_BOLD, size=12, color=PLUM)
            y_text = draw_paragraph(
                c, desc, L.margin + 28, y,
                w=L.page_w - L.margin - L.margin - 28,
                font_name=FONT_SANS, size=10, color=NAVY,
            )
            # Criterios medibles
            if criterios:
                y_text = draw_paragraph(
                    c, f"Criterio: {criterios}", L.margin + 28, y_text - 2,
                    w=L.page_w - L.margin - L.margin - 28,
                    font_name=FONT_SERIF, size=8.5, color=SLATE,
                )
            # Barra de progreso
            y_bar = y_text - 10
            bar_x = L.margin + 28
            bar_w = L.page_w - L.margin - L.margin - 28 - 60
            bar_h = 6
            # Fondo
            c.setFillColorRGB(*SURFACE)
            c.roundRect(bar_x, y_bar, bar_w, bar_h, 3, fill=1, stroke=0)
            # Progreso
            color_bar = SEMANTIC_OK if progreso >= 75 else SEMANTIC_WARN if progreso >= 40 else SEMANTIC_DEFICIT
            if progreso > 0:
                c.setFillColorRGB(*color_bar)
                c.roundRect(bar_x, y_bar, bar_w * min(progreso, 100) / 100, bar_h, 3, fill=1, stroke=0)
            # Texto % y estado
            draw_text(c, f"{progreso}%", bar_x + bar_w + 6, y_bar - 1,
                      font_name=FONT_SANS_BOLD, size=9, color=color_bar)
            estado_lbl = {"cumplido": "Cumplido", "activo": "En proceso",
                          "modificado": "Modificado", "abandonado": "Abandonado"}.get(estado, estado)
            draw_text(c, estado_lbl, bar_x + bar_w + 6, y_bar - 12,
                      font_name=FONT_SANS, size=7.5, color=SLATE)
            y = y_bar - 24

        return y

    def _draw_sintesis_proceso(self, c, data, y: float) -> float:
        """Texto narrativo del clÃ­nico que resume la evoluciÃ³n del paciente."""
        sintesis = getattr(data, "therapy_sintesis", None) \
                   or getattr(data, "therapy_nota_cierre", None) \
                   or ("Espacio reservado para la narrativa integradora del proceso. "
                       "El clÃ­nico deberÃ­a redactar aquÃ­: estado al inicio vs estado al cierre, "
                       "hitos significativos, dificultades superadas, recursos del paciente que "
                       "se hicieron visibles, y cambios observables en su funcionamiento.")
        return draw_paragraph(
            c, sintesis, LAYOUT.margin, y,
            w=LAYOUT.page_w - LAYOUT.margin - LAYOUT.margin,
            font_name=FONT_SERIF, size=10, color=NAVY,
        )

    def _draw_riesgo_longitudinal(self, c, data, y: float) -> float:
        """Mini-timeline de evaluaciones de riesgo a lo largo del proceso."""
        L = LAYOUT
        riesgos = getattr(data, "therapy_risk_history", []) or []
        if not riesgos:
            return y

        NIVEL_COLOR = {
            "ninguno": SEMANTIC_OK,
            "leve":     SEMANTIC_WARN,
            "moderado": (0.706, 0.325, 0.035),  # naranja oscuro
            "alto":     SEMANTIC_DEFICIT,
            "inminente":(0.498, 0.114, 0.180),   # ruby oscuro
        }

        draw_text(c, f"Evaluaciones registradas: {len(riesgos)}",
                  L.margin, y - 4,
                  font_name=FONT_SANS, size=9, color=SLATE)
        y -= 18

        # Render simple tipo lÃ­nea
        for ev in riesgos[:10]:  # mÃ¡ximo 10 entradas
            fecha = ev.get("fecha", "")
            nivel = ev.get("nivel", "ninguno")
            color = NIVEL_COLOR.get(nivel, SLATE)
            c.setFillColorRGB(*color)
            c.circle(L.margin + 6, y, 4, fill=1, stroke=0)
            draw_text(c, str(fecha)[:10], L.margin + 20, y - 3,
                      font_name=FONT_SANS, size=8.5, color=SLATE)
            draw_text(c, nivel.replace("_", " ").title(),
                      L.margin + 120, y - 3,
                      font_name=FONT_SANS_BOLD, size=8.5, color=color)
            y -= 14
        return y - 4

    def _draw_recomendaciones_cierre(self, c, data, y: float) -> float:
        """Recomendaciones especÃ­ficas para el post-cierre."""
        recs = (getattr(data, "recomendaciones", None) or "").strip()
        if not recs:
            recs = ("Reservado para recomendaciones del clÃ­nico al cierre. "
                    "Ejemplos tÃ­picos: continuar con prÃ¡cticas trabajadas en sesiÃ³n, "
                    "considerar terapia de mantenimiento, monitoreo a 3/6 meses, "
                    "contactar nuevamente si reaparecen sÃ­ntomas, derivaciÃ³n a otro "
                    "profesional si aplica.")
        return draw_paragraph(
            c, recs, LAYOUT.margin, y,
            w=LAYOUT.page_w - LAYOUT.margin - LAYOUT.margin,
            font_name=FONT_SERIF, size=10, color=NAVY,
        )

    def _draw_implicaciones_diarias(self, c, data, y: float) -> float:
        """Traduce dominios debilitados a ejemplos de vida cotidiana post-alta.

        Usa la misma fuente de verdad que el informe Pro (implicaciones.py) para
        que la familia y el paciente encuentren el mismo lenguaje en ambos
        informes. Especialmente Ãºtil para el cierre: la transiciÃ³n a "despuÃ©s"
        necesita saber quÃ© Ã¡reas apoyar en casa.
        """
        L = LAYOUT
        items = dominios_con_implicaciones(data.resultados)
        if not items:
            draw_text(
                c, "No se identificaron dominios debilitados relevantes.",
                L.margin, y - 4, font_name=FONT_SERIF, size=9.5, color=SLATE,
            )
            return y - 22

        draw_text(
            c, ("Para sostener los avances logrados en el proceso terapÃ©utico, "
                "tenga en cuenta cÃ³mo estas Ã¡reas se manifiestan en la vida diaria:"),
            L.margin, y - 4,
            font_name=FONT_SERIF, size=9.5, color=NAVY,
        )
        y -= 18

        for it in items[:3]:
            dom = it["dominio"]
            nivel = it["nivel"]
            z = it["z_promedio"]
            y = self._ensure_room(c, data, y, 80)
            y = block_header(
                c, f"{dom}  Â·  ZÌ„={z:+.1f}Ïƒ ({nivel})", y, color=PLUM,
            )
            ejemplos = it.get("ejemplos", [])[:2]
            estrategias = it.get("estrategias", [])[:2]
            for ej in ejemplos:
                y = self._ensure_room(c, data, y, 30)
                y = bullet(c, ej, L.margin, y - 2,
                          L.page_w - L.margin - L.margin) - 1
            if estrategias:
                y -= 4
                draw_text(
                    c, "Estrategias de apoyo:", L.margin, y - 4,
                    font_name=FONT_SANS_BOLD, size=8, color=SLATE,
                )
                y -= 14
                for es in estrategias:
                    y = self._ensure_room(c, data, y, 30)
                    y = bullet(c, es, L.margin + 12, y - 2,
                              L.page_w - L.margin - L.margin - 12) - 1
            y -= 6
        return y



