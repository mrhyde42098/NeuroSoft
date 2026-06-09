"""
report_pro.base
================
``NeuroPDFGeneratorPro`` — clase base para todas las variantes del informe Pro.

Decisiones de diseño:

* Usa el **Canvas API** (mismo patrón que el ``NeuroPDFGenerator`` estándar)
  para tener control fino sobre tipografía, posicionamiento y gráficos custom.
* Implementa paginación "X de Y" con la receta canónica de ReportLab
  (``_make_numbered_canvas_class``): guardar estados de página y re-renderizar
  con el total conocido.
* Las variantes (Pro, Pediátrica, Medicolegal, Junta Médica, Inconcluso)
  heredan de esta clase y sobreescriben los métodos ``_build_*`` que necesiten.
"""

from __future__ import annotations

import base64
import io
import logging

from .charts import (
    draw_bell_curve_with_ci,
    draw_ci_kpi_row,
    draw_discrepancies,
    draw_domain_radar,
    draw_z_profile,
)
from .helpers import (
    block_header,
    bullet,
    callout,
    divider,
    draw_paragraph,
    draw_table,
    draw_text,
    field_grid,
    info_box,
    measure_info_box,
    section_subtitle,
    section_title,
    two_column_blocks,
)
from .narrative import (
    build_strengths_weaknesses,
    build_synthesis_paragraphs,
    detectar_modo_voz,
    frase_cualitativa_resultado,
    generar_resumen_paciente,
    parse_edad_anos,
    parse_recomendaciones,
    puente_impresion_lenguaje_claro,
)
from .theme import (
    ACCENT,
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SANS_ITALIC,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    FONT_SERIF_ITALIC,
    HAIRLINE,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SEMANTIC_LIMITE,
    SEMANTIC_PROMEDIO,
    SEMANTIC_SUPERIOR,
    SLATE,
    SLATE_LIGHT,
    SURFACE,
    TEAL_DARK,
    TYPE,
    ensure_fonts_registered,
    semantic_color_for_z,
)

logger = logging.getLogger(__name__)


# Color claro decorativo (sub-banda de portada). Definido aquí para no
# contaminar theme.py — específico del header de portada.
TEAL_LIGHT_PALE = (0.553, 0.847, 0.788)


# ──────────────────────────────────────────────────────────
# NORMOGRAMA COLOMBIANO — referencia jurídica del informe
# ──────────────────────────────────────────────────────────
# Versión sincronizada con ``normogramaVersion.js`` en el frontend
# en el frontend. Mantener ambas en lockstep; bumpear al modificar cualquiera
# de las 17 normas listadas en ``BLOQUE_LEGAL_NORMOGRAMA``.
NORMOGRAMA_VERSION = "2026.06"


# ──────────────────────────────────────────────────────────
# Canvas con paginación X de Y (receta canónica ReportLab)
# ──────────────────────────────────────────────────────────


def _make_numbered_canvas_class(footer_drawer):
    """Subclase de Canvas que pospone el dibujo del footer hasta save()."""
    from reportlab.pdfgen.canvas import Canvas

    class _NumberedCanvas(Canvas):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._saved_page_states: list[dict] = []

        def showPage(self):
            self._saved_page_states.append(dict(self.__dict__))
            self._startPage()

        def save(self):
            self._saved_page_states.append(dict(self.__dict__))
            total = len(self._saved_page_states)
            for i, state in enumerate(self._saved_page_states):
                self.__dict__.update(state)
                if footer_drawer:
                    footer_drawer(self, i + 1, total)
                if i < total - 1:
                    Canvas.showPage(self)
            Canvas.save(self)

    return _NumberedCanvas


# ──────────────────────────────────────────────────────────
# Generador base
# ──────────────────────────────────────────────────────────


class NeuroPDFGeneratorPro:
    """Generador base Pro. Las variantes sobreescriben ``_build_pages``."""

    #: Nombre visible de la variante (lo sobreescriben las subclases)
    VARIANT_LABEL: str = "Profesional"
    #: Subtítulo para la portada (opcional)
    VARIANT_SUBTITLE: str = "Informe de Evaluación Neuropsicológica"
    #: ¿Esta variante usa portada dedicada? (Junta Médica = False)
    USE_COVER: bool = True
    #: ¿Mostrar anexo de definiciones operativas?
    INCLUDE_ANNEX: bool = True
    #: ¿Incluir síntesis clínica integradora (narrativa automática)?
    INCLUDE_SINTESIS: bool = False
    #: ¿Ubicar Resumen para la Familia antes de resultados técnicos?
    FAMILY_SUMMARY_BEFORE_RESULTS: bool = False
    #: ¿Columna cualitativa «Qué significa» en tabla de puntajes?
    SCORE_TABLE_QUALITATIVE: bool = False

    #: Módulos gráficos en sección resultados (orden de renderizado).
    CHART_MODULES: tuple[str, ...] = (
        "kpi_discrepancies",
        "z_profile",
        "bell_curve",
        "radar",
        "score_table",
    )
    #: Máximo bloques gráficos por página (kpi+discrepancias = 1 bloque).
    MAX_CHART_BLOCKS_PER_PAGE: int = 2
    CHART_MODULE_MIN_HEIGHT: dict[str, float] = {
        "kpi_discrepancies": 200.0,
        "z_profile": 130.0,
        "bell_curve": 170.0,
        "radar": 290.0,
        "score_table": 150.0,
    }

    # ──────────────────────────────────────────────────────────
    # Entry point
    # ──────────────────────────────────────────────────────────

    def generate(self, data) -> bytes:
        """Construye y retorna los bytes del PDF."""
        from app.core.branding import clinical_brand

        ensure_fonts_registered()

        buffer = io.BytesIO()
        NumberedCanvas = _make_numbered_canvas_class(self._draw_footer_factory(data))

        from reportlab.lib.pagesizes import A4

        c = NumberedCanvas(buffer, pagesize=A4)
        brand = (data.institucion_nombre or "").strip() or clinical_brand()
        c.setTitle(f"Informe Neuropsicológico — {data.nombre_completo}")
        c.setAuthor(data.profesional_nombre or brand)
        c.setSubject(f"Evaluación Neuropsicológica — {self.VARIANT_LABEL}")
        c.setCreator(brand)
        c.setKeywords(
            "Neuropsicología,Informe,{},{}".format(
                data.codigo_cie10 or "sin-CIE10",
                data.eval_id[:8] if getattr(data, "eval_id", "") else "sin-id",
            )
        )
        c.setProducer(f"{brand} — Informes clínicos")

        self._build_pages(c, data)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    # ──────────────────────────────────────────────────────────
    # Construcción de páginas (SOBREESCRIBIR en subclases)
    # ──────────────────────────────────────────────────────────

    def _build_pages(self, c, data) -> None:
        """Orquesta las secciones. Las subclases pueden customizar el orden."""
        if self.USE_COVER:
            self._build_cover(c, data)
            c.showPage()

        # Informe COMPLETO / ORIGINAL: consigna verbatim lo que el profesional
        # diligencia, con todas las áreas presentes (estilo ficha clínica). NO usa
        # narrativa generada por IA — eso queda reservado a las variantes
        # cortas (paciente, junta médica, etc.).
        y = self._page_top_with_header(c, data)
        y = self._section_sociodemografico(c, data, y)
        y = self._section_motivo_consulta(c, data, y)
        y = self._section_antecedentes(c, data, y)
        y = self._section_historia_psicosocial(c, data, y)
        y = self._section_pruebas_aplicadas(c, data, y)
        y = self._section_observacion(c, data, y)
        if self.FAMILY_SUMMARY_BEFORE_RESULTS:
            y = self._section_resumen_familia(c, data, y)
        y = self._section_resultados(c, data, y)
        if self.INCLUDE_SINTESIS:
            y = self._section_sintesis(c, data, y)
        y = self._section_analisis_dominio(c, data, y)
        if not self.FAMILY_SUMMARY_BEFORE_RESULTS:
            y = self._section_resumen_familia(c, data, y)
        y = self._section_impresion(c, data, y)
        y = self._section_recomendaciones(c, data, y)
        if self.INCLUDE_ANNEX:
            y = self._section_anexo(c, data, y)
        self._section_firma(c, data, y)

    # ──────────────────────────────────────────────────────────
    # Helpers de paginación con header automático
    # ──────────────────────────────────────────────────────────

    def _new_page(self, c, data) -> float:
        """Salta a una página nueva y dibuja el header. Retorna el ``y`` inicial."""
        c.showPage()
        return self._page_top_with_header(c, data)

    def _ensure_room(self, c, data, y: float, need: float = 80.0) -> float:
        """Si no caben ``need`` puntos, salta de página con header."""
        if y - need < LAYOUT.content_bottom:
            return self._new_page(c, data)
        return y

    # ──────────────────────────────────────────────────────────
    # PORTADA
    # ──────────────────────────────────────────────────────────

    def _build_cover(self, c, data) -> None:
        """Portada estilo membrete editorial clínico.

        Sin banda navy de bloque ni tarjeta flotante: una columna editorial
        anclada por una *spine rule* de acento, membrete arriba, un bloque de
        título tipográfico, y los datos del paciente en una rejilla tabular con
        hairlines. Pensada para leerse como un informe clínico, no un dashboard.
        """
        L = LAYOUT
        W, H, M = L.page_w, L.page_h, L.margin
        x = M + 16  # columna de contenido (después de la spine)
        right = W - M

        # ── Spine: regla vertical de acento a toda la altura (firma) ──
        c.setFillColorRGB(*ACCENT)
        c.rect(M, M, 2.2, H - 2 * M, fill=1, stroke=0)

        # ── Membrete (masthead) ──
        top = H - M
        tx = x
        if data.logo_base64:
            try:
                from reportlab.lib.utils import ImageReader

                img = ImageReader(io.BytesIO(base64.b64decode(data.logo_base64)))
                c.drawImage(
                    img,
                    x,
                    top - 34,
                    width=34,
                    height=34,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                tx = x + 44
            except Exception as e:
                logger.debug("Logo portada no se pudo dibujar: %s", e)
        draw_text(
            c,
            data.institucion_nombre or "Consultorio Neuropsicológico",
            tx,
            top - 14,
            font_name=FONT_SERIF_BOLD,
            size=TYPE.title_h2,
            color=NAVY,
        )
        sub = "   ·   ".join([s for s in (data.institucion_dir, data.institucion_tel) if s])
        if sub:
            draw_text(
                c,
                sub,
                tx,
                top - 27,
                font_name=FONT_SANS,
                size=TYPE.caption,
                color=SLATE,
            )
        if data.institucion_nit:
            draw_text(
                c,
                f"NIT {data.institucion_nit}",
                right,
                top - 14,
                font_name=FONT_SANS,
                size=TYPE.caption,
                color=SLATE,
                align="right",
            )
        mh_y = top - 40
        c.setStrokeColorRGB(*HAIRLINE)
        c.setLineWidth(0.7)
        c.line(x, mh_y, right, mh_y)

        # ── Bloque de título tipográfico ──
        ty = H * 0.70
        c.setFillColorRGB(*ACCENT)
        c.rect(x, ty + 19, 34, 2.4, fill=1, stroke=0)
        draw_text(
            c,
            "EVALUACIÓN NEUROPSICOLÓGICA",
            x,
            ty + 5,
            font_name=FONT_SANS_BOLD,
            size=TYPE.caption,
            color=ACCENT,
        )
        draw_text(
            c,
            "Informe de Evaluación",
            x,
            ty - 28,
            font_name=FONT_SERIF_BOLD,
            size=30,
            color=NAVY,
        )
        draw_text(
            c,
            "Neuropsicológica",
            x,
            ty - 60,
            font_name=FONT_SERIF_BOLD,
            size=30,
            color=NAVY,
        )
        draw_text(
            c,
            f"Variante {self.VARIANT_LABEL}",
            x,
            ty - 82,
            font_name=FONT_SERIF_ITALIC,
            size=TYPE.body,
            color=SLATE,
        )

        # ── Panel del paciente (rejilla tabular con hairlines) ──
        panel_top = ty - 116
        draw_text(
            c,
            "PACIENTE",
            x,
            panel_top,
            font_name=FONT_SANS_BOLD,
            size=TYPE.caption,
            color=ACCENT,
        )
        draw_text(
            c,
            data.nombre_completo or "—",
            x,
            panel_top - 22,
            font_name=FONT_SERIF_BOLD,
            size=TYPE.title_h1,
            color=NAVY,
        )
        rows = [
            (
                "Documento",
                f"{data.tipo_documento or ''} {data.numero_documento or ''}".strip(),
                "Fecha de nacimiento",
                data.fecha_nacimiento.strftime("%d/%m/%Y") if data.fecha_nacimiento else "—",
            ),
            ("Edad", data.edad_display, "Sexo", data.sexo),
            ("Escolaridad", data.escolaridad, "Lateralidad", data.lateralidad),
            (
                "Fecha de evaluación",
                data.fecha_atencion.strftime("%d/%m/%Y") if data.fecha_atencion else "—",
                "Orden N°",
                data.orden_no,
            ),
        ]
        colw = (right - x) / 2
        ry = panel_top - 46

        def _cell(label: str, value: str, cx: float, cy: float) -> None:
            draw_text(
                c,
                label.upper(),
                cx,
                cy,
                font_name=FONT_SANS_BOLD,
                size=TYPE.micro,
                color=SLATE,
            )
            draw_text(
                c,
                str(value or "—"),
                cx,
                cy - 12,
                font_name=FONT_SANS,
                size=TYPE.body,
                color=NAVY,
            )

        c.setStrokeColorRGB(*HAIRLINE)
        c.setLineWidth(0.4)
        c.line(x, ry + 12, right, ry + 12)
        for l1, v1, l2, v2 in rows:
            _cell(l1, v1, x, ry)
            _cell(l2, v2, x + colw, ry)
            ry -= 32
            c.setStrokeColorRGB(*HAIRLINE)
            c.setLineWidth(0.4)
            c.line(x, ry + 12, right, ry + 12)
        if data.protocolo:
            _cell("Protocolo aplicado", data.protocolo[:90], x, ry - 4)

        # ── Pie: firmante + nota legal ──
        if data.profesional_nombre:
            py = M + 100
            c.setStrokeColorRGB(*ACCENT)
            c.setLineWidth(1.2)
            c.line(x, py + 30, x + 46, py + 30)
            draw_text(
                c,
                "ELABORADO POR",
                x,
                py + 16,
                font_name=FONT_SANS_BOLD,
                size=TYPE.micro,
                color=SLATE,
            )
            draw_text(
                c,
                data.profesional_nombre,
                x,
                py,
                font_name=FONT_SERIF_BOLD,
                size=TYPE.title_h2,
                color=NAVY,
            )
            extra = " · ".join(
                [
                    s
                    for s in (
                        data.profesional_titulo,
                        f"Reg. {data.profesional_registro}" if data.profesional_registro else "",
                    )
                    if s
                ]
            )
            if extra:
                draw_text(
                    c,
                    extra,
                    x,
                    py - 14,
                    font_name=FONT_SANS,
                    size=TYPE.body_sm,
                    color=SLATE,
                )

        legal_y = M + 24
        c.setStrokeColorRGB(*HAIRLINE)
        c.setLineWidth(0.5)
        c.line(x, legal_y + 14, right, legal_y + 14)
        draw_text(
            c,
            "Documento confidencial — Ley 1581 de 2012 (Habeas Data) · Resolución 1995 de 1999 (Historia Clínica).",
            x,
            legal_y,
            font_name=FONT_SANS,
            size=TYPE.micro,
            color=SLATE,
        )
        eval_id = getattr(data, "eval_id", "") or ""
        if eval_id:
            draw_text(
                c,
                f"ID {eval_id}",
                right,
                legal_y,
                font_name=FONT_SANS,
                size=TYPE.micro,
                color=SLATE_LIGHT,
                align="right",
            )

    # ──────────────────────────────────────────────────────────
    # HEADER (cada página interna)
    # ──────────────────────────────────────────────────────────

    def _page_top_with_header(self, c, data) -> float:
        L = LAYOUT
        # Spine de acento a la izquierda (coherente con la portada)
        c.setFillColorRGB(*ACCENT)
        c.rect(L.margin, L.page_h - 50, 2.2, 28, fill=1, stroke=0)

        # Logo pequeño + nombre institución (izquierda)
        text_x = L.margin + 12
        if data.logo_base64:
            try:
                from reportlab.lib.utils import ImageReader

                img = ImageReader(io.BytesIO(base64.b64decode(data.logo_base64)))
                c.drawImage(
                    img,
                    L.margin + 10,
                    L.page_h - 42,
                    width=22,
                    height=22,
                    preserveAspectRatio=True,
                    mask="auto",
                )
                text_x = L.margin + 40
            except Exception as _exc:
                # §A4-fix: imagen del logo institucional corrupta o ilegible.
                # No es bloqueante para el informe, pero queda registro.
                logger.warning("No se pudo dibujar el logo institucional en el header: %s", _exc)
        draw_text(
            c,
            data.institucion_nombre[:55],
            text_x,
            L.page_h - 26,
            font_name=FONT_SERIF_BOLD,
            size=TYPE.body_sm,
            color=NAVY,
        )
        draw_text(
            c,
            self.VARIANT_SUBTITLE,
            text_x,
            L.page_h - 36,
            font_name=FONT_SANS_ITALIC,
            size=TYPE.micro + 0.5,
            color=SLATE,
        )

        # Línea funcional del informe: orden + fechas (centro)
        orden = (data.orden_no or "").strip()
        if not orden and getattr(data, "eval_id", ""):
            orden = str(data.eval_id)[:12]
        meta_parts = []
        if orden:
            meta_parts.append(f"Orden {orden}")
        if data.fecha_atencion:
            meta_parts.append(f"Atención {data.fecha_atencion.strftime('%d/%m/%Y')}")
        if meta_parts:
            draw_text(
                c,
                "  ·  ".join(meta_parts),
                L.page_w / 2,
                L.page_h - 26,
                font_name=FONT_SANS,
                size=TYPE.micro,
                color=SLATE,
                align="center",
            )

        # Datos paciente (derecha)
        if data.nombre_completo:
            draw_text(
                c,
                data.nombre_completo[:46],
                L.page_w - L.margin,
                L.page_h - 26,
                font_name=FONT_SANS_BOLD,
                size=TYPE.body_sm,
                color=NAVY,
                align="right",
            )
            sub = []
            if data.tipo_documento and data.numero_documento:
                sub.append(f"{data.tipo_documento} {data.numero_documento}")
            if data.fecha_atencion:
                sub.append(data.fecha_atencion.strftime("%d/%m/%Y"))
            if sub:
                draw_text(
                    c,
                    " · ".join(sub),
                    L.page_w - L.margin,
                    L.page_h - 36,
                    font_name=FONT_SANS,
                    size=TYPE.micro + 0.5,
                    color=SLATE,
                    align="right",
                )

        # Línea separadora
        c.setStrokeColorRGB(*HAIRLINE)
        c.setLineWidth(0.5)
        c.line(L.margin, L.page_h - 44, L.page_w - L.margin, L.page_h - 44)

        return L.page_h - 60

    # ──────────────────────────────────────────────────────────
    # FOOTER (paginación + cita legal)
    # ──────────────────────────────────────────────────────────

    def _draw_footer_factory(self, data):
        """Devuelve una closure ``(c, page_num, total_pages) → None``."""
        (data.institucion_nombre or "").strip() or "Consultorio"
        eval_id = (getattr(data, "eval_id", "") or "")[:8]

        def _draw(c, page_num: int, total_pages: int) -> None:
            # No dibujar footer en portada (página 1 si USE_COVER=True)
            if self.USE_COVER and page_num == 1:
                return
            L = LAYOUT
            # Hairline cálida
            c.setStrokeColorRGB(*HAIRLINE)
            c.setLineWidth(0.5)
            c.line(L.margin, L.margin_bottom_footer - 8, L.page_w - L.margin, L.margin_bottom_footer - 8)
            base_y = L.margin_bottom_footer - 20
            # Izquierda: variante (corto, sin colisión con el centro)
            draw_text(
                c,
                f"Variante {self.VARIANT_LABEL}",
                L.margin,
                base_y,
                font_name=FONT_SANS,
                size=TYPE.micro,
                color=SLATE,
            )
            # Centro: cita legal + normograma
            draw_text(
                c,
                f"Confidencial · Ley 1581/2012 · Res. 1995/1999 · Normograma {NORMOGRAMA_VERSION}",
                L.page_w / 2,
                base_y,
                font_name=FONT_SANS,
                size=TYPE.micro,
                color=SLATE_LIGHT,
                align="center",
            )
            # Derecha: paginación + eval_id
            right = f"Página {page_num} de {total_pages}"
            if eval_id:
                right += f"  ·  ID {eval_id}"
            draw_text(
                c,
                right,
                L.page_w - L.margin,
                base_y,
                font_name=FONT_SANS_BOLD,
                size=TYPE.micro,
                color=NAVY,
                align="right",
            )

        return _draw

    # ──────────────────────────────────────────────────────────
    # SECCIONES (compartidas — subclases pueden sobreescribir)
    # ──────────────────────────────────────────────────────────

    def _section_sociodemografico(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=200)
        y = section_title(c, "Información Sociodemográfica", y)
        # Nombre completo en su propia fila ancha (legibilidad)
        y = field_grid(
            c,
            [
                ("Nombre completo", data.nombre_completo),
                ("Documento", f"{data.tipo_documento or ''} {data.numero_documento or ''}".strip()),
            ],
            L.margin,
            y,
            L.content_w,
            cols=2,
        )
        items = [
            ("Fecha de nacimiento", data.fecha_nacimiento.strftime("%d/%m/%Y") if data.fecha_nacimiento else "—"),
            ("Edad", data.edad_display),
            ("Sexo", data.sexo),
            ("Escolaridad", data.escolaridad),
            ("Ocupación", data.ocupacion),
            ("Lateralidad", data.lateralidad),
            ("Ciudad", data.ciudad),
            ("Acompañante", data.acompanante),
            ("Remite", data.remite),
            ("EPS / Asegurador", data.eps),
            ("Orden N°", data.orden_no),
            ("Fecha de atención", data.fecha_atencion.strftime("%d/%m/%Y") if data.fecha_atencion else "—"),
        ]
        y = field_grid(c, items, L.margin, y, L.content_w, cols=3)
        return y - 14

    def _section_motivo_consulta(self, c, data, y: float) -> float:
        L = LAYOUT
        need = 40 + measure_info_box(data.motivo_consulta, L.content_w, size=TYPE.body)
        y = self._ensure_room(c, data, y, need=min(need, 260))
        y = section_title(c, "Motivo de Consulta", y)
        y = info_box(
            c,
            "Motivo referido por el consultante",
            data.motivo_consulta,
            L.margin,
            y,
            L.content_w,
            size=TYPE.body,
        )
        return y - 14

    def _section_pruebas_aplicadas(self, c, data, y: float) -> float:
        """Tabla limpia con las pruebas administradas."""
        if not data.resultados or not data.protocolo or len(data.resultados) < 1:
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=110)
        y = section_title(
            c,
            "Pruebas Aplicadas",
            y,
            subtitle=f"Protocolo: {data.protocolo}",
        )
        rows = []
        for r in data.resultados:
            from .helpers import human_test_name

            nombre = human_test_name(
                r.get("test_id", "") or "",
                r.get("test_nombre", "") or "",
            )
            dominio = str(r.get("dominio_cognitivo", "—"))
            dur = r.get("duracion_estimada", "—")
            rows.append([nombre, dominio, str(dur)])
        col_widths = [L.content_w * 0.52, L.content_w * 0.33, L.content_w * 0.15]
        # Paginar manualmente la tabla
        row_h = 16
        while rows:
            available = max(1, int((y - L.content_bottom - 30) // row_h))
            chunk, rows = rows[:available], rows[available:]
            y = draw_table(
                c,
                ["Prueba", "Dominio", "Dur."],
                chunk,
                col_widths,
                L.margin,
                y,
                row_h=row_h,
                size=TYPE.body_sm,
            )
            if rows:
                y = self._new_page(c, data)
        return y - 12

    def _render_boxes(
        self, c, data, items, y: float, *, cols: int = 2, gap: float = 12.0, size: float = TYPE.body_sm
    ) -> float:
        """Renderiza una lista de (etiqueta, valor) como ``info_box`` en columnas.

        Muestra TODAS las cajas aunque el valor esté vacío (placeholder), igual
        que el formato informe NPS. Pagina por filas para no partir una caja.
        """
        L = LAYOUT
        col_w = (L.content_w - (cols - 1) * gap) / cols
        # Procesar en filas de `cols` cajas; cada fila tiene la altura de su caja
        # más alta y se mantiene unida.
        for i in range(0, len(items), cols):
            row = items[i : i + cols]
            heights = [measure_info_box(v, col_w, size=size) for _, v in row]
            row_h = max(heights) if heights else 30.0
            y = self._ensure_room(c, data, y, need=row_h + 8)
            row_top = y
            bottoms = []
            for j, (lbl, val) in enumerate(row):
                bx = L.margin + j * (col_w + gap)
                # Igualar alturas dentro de la fila estirando con padding visual:
                bottoms.append(info_box(c, lbl, val, bx, row_top, col_w, size=size))
            y = min(bottoms) - 8
        return y

    def _section_antecedentes(self, c, data, y: float) -> float:
        antec = [
            ("Patológicos / Médicos", data.patologicos_medicos),
            ("Alérgicos", data.alergicos),
            ("Sensoriales / Motores", data.sensoriales_motores),
            ("Tóxicos", data.toxicos),
            ("Psiquiátricos", data.psiquiatricos),
            ("Terapéuticos", data.terapeuticos),
            ("Farmacológicos", data.farmacologicos),
            ("Quirúrgicos", data.quirurgicos),
            ("Traumáticos", data.traumaticos),
            ("Familiares", data.familiares),
            ("Paraclínicos", data.paraclinicos),
        ]
        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c,
            "Antecedentes Médicos",
            y,
            subtitle="Historia clínica relevante — todas las áreas se consignan aunque no se reporten",
        )
        return self._render_boxes(c, data, antec, y, cols=2) - 4

    def _section_historia_psicosocial(self, c, data, y: float) -> float:
        """Historia familiar, social y funcional (estilo ficha clínica)."""
        items = [
            ("Vive con", data.vive_con),
            ("Actividades básicas cotidianas (ABC)", data.abc),
            ("Escolar / Laboral", data.escolar_laboral),
            ("Patrón de sueño", data.patron_sueno),
            ("Patrón de alimentación", data.patron_alimentacion),
            ("Comportamiento / Ánimo", data.comportamiento_animo),
        ]
        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c,
            "Historia Familiar, Social y Funcional",
            y,
        )
        return self._render_boxes(c, data, items, y, cols=2) - 4

    def _section_resumen_ejecutivo(self, c, data, y: float) -> float:
        """Resumen ejecutivo en pirámide invertida: conclusión → hallazgos → implicación.

        Va inmediatamente después de los antecedentes (visible en página 2)
        y antes de los resultados crudos. Pensado para clínicos que solo
        leen 30 segundos del informe.
        """
        from .narrative import build_executive_summary

        L = LAYOUT
        if not data.resultados:
            return y
        ej = build_executive_summary(
            data.resultados,
            paciente_nombre=(data.nombre_completo.split()[0] if data.nombre_completo else "El paciente"),
        )
        # El callout necesita ~80-120 pts según hallazgos.
        y = self._ensure_room(c, data, y, need=140)
        y = section_title(
            c,
            "Resumen Ejecutivo",
            y,
            subtitle="Pirámide invertida: conclusión, hallazgos, implicación",
        )
        # 1) Conclusión
        y = callout(
            c,
            ej["conclusion"],
            L.margin,
            y,
            L.content_w,
            accent=NAVY,
            fill=SURFACE,
            title="Conclusión",
            size=TYPE.body,
        )
        y -= 6
        # 2) Hallazgos
        if ej.get("hallazgos"):
            y = self._ensure_room(c, data, y, need=60)
            y = block_header(c, "Hallazgos clave", y, color=TEAL_DARK)
            for h in ej["hallazgos"][:3]:
                y = self._ensure_room(c, data, y, need=22)
                y = bullet(c, h, L.margin, y - 2, L.content_w) - 1
            y -= 2
        # 3) Implicación
        y = self._ensure_room(c, data, y, need=60)
        y = callout(
            c,
            ej["implicacion"],
            L.margin,
            y,
            L.content_w,
            accent=SEMANTIC_LIMITE,
            fill=SURFACE,
            title="Implicación",
            size=TYPE.body_sm,
        )
        return y - 6

    def _section_observacion(self, c, data, y: float) -> float:
        """Observación clínica conductual durante la administración (verbatim)."""
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=120)
        y = section_title(
            c,
            "Observación Clínica",
            y,
            subtitle="Apariencia, actitud y conducta durante la evaluación",
        )
        y = info_box(
            c,
            "Observación general",
            data.obs_clinica_general,
            L.margin,
            y,
            L.content_w,
            size=TYPE.body,
        )
        return y - 14

    def _section_analisis_dominio(self, c, data, y: float) -> float:
        """Análisis cualitativo por dominio cognitivo — texto verbatim del clínico.

        Réplica del bloque "Resultados por área" del formato informe NPS: cada dominio
        se consigna aunque no se diligencie. Es el análisis que el profesional
        escribe a partir de los puntajes; NO se genera con IA.
        """
        dominios = [
            ("Atención y concentración", data.obs_atencion),
            ("Memoria y aprendizaje", data.obs_memoria),
            ("Praxias y gnosias", data.obs_praxias_gnosias),
            ("Lenguaje", data.obs_lenguaje),
            ("Funciones ejecutivas", data.obs_funciones_ejecutivas),
            ("Emociones y comportamiento", data.obs_emociones),
            ("Cociente intelectual", data.obs_ci),
            ("Funcionalidad / AVD", data.obs_funcionalidad),
        ]
        y = self._ensure_room(c, data, y, need=140)
        y = section_title(
            c,
            "Análisis por Dominio",
            y,
            subtitle="Lectura clínica de cada dominio a partir de los puntajes",
        )
        return self._render_boxes(c, data, dominios, y, cols=2, size=TYPE.body_sm) - 4

    def _chart_module_applicable(self, data, module_id: str) -> bool:
        if not data.resultados:
            return False
        n_z = sum(1 for r in data.resultados if r.get("z_equivalente") is not None and r.get("tipo_metrica") != "ci")
        sum(1 for r in data.resultados if r.get("tipo_metrica") == "ci")
        if module_id == "kpi_discrepancies":
            return True
        if module_id == "z_profile":
            return n_z >= 1
        if module_id == "bell_curve":
            return n_z >= 5
        if module_id == "radar":
            return n_z >= 2
        return module_id == "score_table"

    def _draw_chart_module(self, c, data, y: float, module_id: str) -> float:
        if module_id == "kpi_discrepancies":
            ci_y_before = y
            y = draw_ci_kpi_row(c, data.resultados, y)
            if y < ci_y_before:
                y -= 4
            n_ci = sum(1 for r in data.resultados if r.get("tipo_metrica") == "ci")
            if n_ci >= 2:
                y = draw_discrepancies(c, data.resultados, y)
            return y - 6
        if module_id == "z_profile":
            return draw_z_profile(c, data.resultados, y) - 6
        if module_id == "bell_curve":
            return draw_bell_curve_with_ci(c, data.resultados, y) - 6
        if module_id == "radar":
            y_before = y
            y = draw_domain_radar(c, data.resultados, y)
            return (y - 6) if y < y_before else y - 6
        if module_id == "score_table":
            return self._draw_score_table(c, data, data.resultados, y) - 8
        return y

    def _section_resultados(self, c, data, y: float) -> float:
        if not data.resultados:
            return y

        y = self._ensure_room(c, data, y, need=240)
        y = section_title(
            c,
            "Resultados Cuantitativos",
            y,
            subtitle="Puntajes por prueba y perfil cognitivo del paciente",
        )

        blocks_on_page = 0
        for module_id in self.CHART_MODULES:
            if not self._chart_module_applicable(data, module_id):
                continue
            min_h = self.CHART_MODULE_MIN_HEIGHT.get(module_id, 120.0)
            if blocks_on_page >= self.MAX_CHART_BLOCKS_PER_PAGE:
                y = self._new_page(c, data)
                blocks_on_page = 0
            y = self._ensure_room(c, data, y, need=min_h)
            if y - min_h < LAYOUT.content_bottom:
                y = self._new_page(c, data)
                blocks_on_page = 0
            y = self._draw_chart_module(c, data, y, module_id)
            if module_id != "score_table":
                blocks_on_page += 1

        return y

    def _kwargs_resumen_paciente(self, data) -> dict:
        edad = parse_edad_anos(getattr(data, "edad_display", None))
        return {
            "edad_anos": edad,
            "modo_voz": detectar_modo_voz(edad),
        }

    def _draw_score_table(self, c, data, resultados, y: float) -> float:
        L = LAYOUT
        cualitativa = self.SCORE_TABLE_QUALITATIVE
        if cualitativa:
            col_widths = [
                L.content_w * 0.26,
                L.content_w * 0.08,
                L.content_w * 0.09,
                L.content_w * 0.08,
                L.content_w * 0.14,
                L.content_w * 0.35,
            ]
            headers = ["Prueba", "PD", "Escalar/CI", "Z", "Interpretación", "Qué significa"]
        else:
            col_widths = [
                L.content_w * 0.38,
                L.content_w * 0.10,
                L.content_w * 0.12,
                L.content_w * 0.10,
                L.content_w * 0.30,
            ]
            headers = ["Prueba", "PD", "Escalar/CI", "Z", "Interpretación"]
        rows = []
        row_colors = []
        for r in resultados:
            from .helpers import human_test_name

            nombre = human_test_name(
                r.get("test_id", "") or "",
                r.get("test_nombre", "") or "",
            )
            pd = r.get("puntaje_bruto")
            esc = r.get("puntaje_escalar")
            z = r.get("z_equivalente")
            interp = str(r.get("interpretacion", "—"))
            row = [
                nombre,
                str(int(pd)) if pd is not None else "—",
                str(int(esc)) if esc is not None else "—",
                f"{z:+.2f}" if z is not None else "—",
                interp,
            ]
            if cualitativa:
                row.append(frase_cualitativa_resultado(r))
            rows.append(row)
            row_colors.append(semantic_color_for_z(z))
        # Paginación
        row_h = 16
        while rows:
            available = max(1, int((y - L.content_bottom - 30) // row_h))
            chunk, rows = rows[:available], rows[available:]
            colors_chunk, row_colors = row_colors[:available], row_colors[available:]
            y = draw_table(
                c,
                headers,
                chunk,
                col_widths,
                L.margin,
                y,
                row_h=row_h,
                size=TYPE.body_sm,
                row_colors=colors_chunk,
            )
            if rows:
                y = self._new_page(c, data)
        if cualitativa:
            y = (
                draw_paragraph(
                    c,
                    "Filas en color: verde = rango esperado; ámbar/rojo = por debajo. "
                    "Consulte el anexo para definiciones de Z, CI y percentiles.",
                    L.margin,
                    y,
                    L.content_w,
                    font_name=FONT_SANS_ITALIC,
                    size=TYPE.caption,
                    color=SLATE,
                    leading=TYPE.caption * 1.35,
                )
                - 4
            )
        return y - 4

    def _section_sintesis(self, c, data, y: float) -> float:
        """Síntesis clínica integradora generada desde los resultados."""
        if not data.resultados:
            return y
        L = LAYOUT
        paragraphs = build_synthesis_paragraphs(
            data.resultados,
            paciente_nombre=(data.nombre_completo.split()[0] if data.nombre_completo else "El paciente"),
            protocolo=data.protocolo,
        )
        if not paragraphs:
            return y

        y = self._ensure_room(c, data, y, need=180)
        y = section_title(
            c,
            "Síntesis Clínica Integradora",
            y,
            subtitle="Lectura cuantitativa de los hallazgos",
        )
        for p in paragraphs:
            y = self._ensure_room(c, data, y, need=60)
            y = (
                draw_paragraph(
                    c,
                    p,
                    L.margin,
                    y,
                    L.content_w,
                    font_name=FONT_SERIF,
                    size=TYPE.body,
                    color=NAVY,
                    leading=TYPE.body * 1.45,
                )
                - 6
            )

        # Fortalezas / debilidades en dos columnas
        weak, strong = build_strengths_weaknesses(data.resultados)
        if weak or strong:
            y = self._ensure_room(c, data, y, need=140)
            col_w = (L.content_w - 16) / 2
            x_left = L.margin
            x_right = L.margin + col_w + 16
            y_w = y_s = y
            if weak:
                y_w = block_header(c, "Áreas con desempeño disminuido", y_w, color=SEMANTIC_DEFICIT, x=x_left)
                for item in weak[:6]:
                    y_w = bullet(c, item, x_left, y_w, col_w) - 2
            if strong:
                y_s = block_header(
                    c, "Áreas con desempeño preservado / superior", y_s, color=SEMANTIC_SUPERIOR, x=x_right
                )
                for item in strong[:5]:
                    y_s = bullet(c, item, x_right, y_s, col_w) - 2
            y = min(y_w, y_s)
        return y - 10

    def _section_resumen_familia(self, c, data, y: float) -> float:
        """Lenguaje enriquecido para padres / cuidadores / paciente.

        Utiliza ``generar_resumen_paciente`` (narrative.py) que ya traduce
        cada hallazgo técnico a frases cotidianas con ejemplos. Va en una
        sección visualmente diferenciada (callout warm + iconografía) para
        que cualquier adulto no-clínico la pueda leer.
        """
        L = LAYOUT
        if not data.resultados or not data.nombre_completo:
            return y
        recomendaciones = []
        if data.obs_recomendaciones and data.obs_recomendaciones not in ("N/A", ""):
            for grupo in parse_recomendaciones(data.obs_recomendaciones).values():
                for it in grupo:
                    recomendaciones.append(it["texto"])
        resumen = generar_resumen_paciente(
            resultados=data.resultados,
            paciente_nombre=data.nombre_completo,
            recomendaciones=recomendaciones,
            **self._kwargs_resumen_paciente(data),
        )
        modo_voz = resumen.get("modo_voz", "paciente")
        if not resumen:
            return y
        y = self._ensure_room(c, data, y, need=380)
        y = section_title(
            c,
            "Resumen para la Familia",
            y,
            subtitle="Lenguaje sencillo para padres, cuidadores y paciente",
        )
        # ── Saludo ──
        if resumen.get("saludo"):
            y = callout(
                c,
                resumen["saludo"],
                L.margin,
                y,
                L.content_w,
                accent=SEMANTIC_PROMEDIO,
                fill=SURFACE,
                title="Saludo",
                size=TYPE.body_sm,
            )
            y -= 6
        # ── Qué hicimos ──
        if resumen.get("que_hicimos"):
            y = self._ensure_room(c, data, y, need=80)
            y = block_header(c, "¿Qué hicimos en la evaluación?", y)
            y = (
                draw_paragraph(
                    c,
                    resumen["que_hicimos"],
                    L.margin,
                    y,
                    L.content_w,
                    font_name=FONT_SERIF,
                    size=TYPE.body_sm,
                    color=NAVY,
                    leading=TYPE.body_sm * 1.45,
                )
                - 4
            )
        # ── Qué encontramos ──
        if resumen.get("que_encontramos"):
            y = self._ensure_room(c, data, y, need=100)
            y = block_header(c, "¿Qué encontramos?", y)
            y = (
                draw_paragraph(
                    c,
                    resumen["que_encontramos"],
                    L.margin,
                    y,
                    L.content_w,
                    font_name=FONT_SERIF,
                    size=TYPE.body_sm,
                    color=NAVY,
                    leading=TYPE.body_sm * 1.45,
                )
                - 4
            )
        # ── Implicaciones para la vida diaria (NUEVO) ──
        from .implicaciones import dominios_con_implicaciones, titulo_implicacion_humano

        implicaciones = dominios_con_implicaciones(data.resultados)
        if implicaciones:
            y = self._ensure_room(c, data, y, need=140)
            y = block_header(
                c,
                "Implicaciones para la vida diaria",
                y,
                color=SEMANTIC_LIMITE,
            )
            y_intro = (
                draw_paragraph(
                    c,
                    "Esto es lo que podría notarse en la vida cotidiana:",
                    L.margin,
                    y,
                    L.content_w,
                    font_name=FONT_SANS,
                    size=TYPE.body_sm,
                    color=SLATE,
                    leading=TYPE.body_sm * 1.4,
                )
                - 2
            )
            y = y_intro
            for impl in implicaciones[:4]:
                y = self._ensure_room(c, data, y, need=80)
                dom = str(impl["dominio"])
                nivel = impl["nivel"]
                color = SEMANTIC_DEFICIT if nivel == "severo" else SEMANTIC_LIMITE
                titulo_impl = titulo_implicacion_humano(
                    dom,
                    nombre_paciente=data.nombre_completo or "",
                    modo_voz=modo_voz,
                )
                y = block_header(
                    c,
                    titulo_impl,
                    y,
                    color=color,
                )
                for ej in impl["ejemplos"][:3]:
                    y = self._ensure_room(c, data, y, need=28)
                    y = bullet(c, ej, L.margin, y - 2, L.content_w) - 1
                # Estrategias condensadas en una línea
                if impl["estrategias"]:
                    estr_txt = "Apoyos sugeridos: " + " · ".join(impl["estrategias"][:2])
                    y = self._ensure_room(c, data, y, need=24)
                    y = (
                        draw_paragraph(
                            c,
                            estr_txt,
                            L.margin + 8,
                            y,
                            L.content_w - 8,
                            font_name=FONT_SANS,
                            size=TYPE.caption,
                            color=TEAL_DARK,
                            leading=TYPE.caption * 1.35,
                        )
                        - 4
                    )
            y -= 4
        # ── Fortalezas + Áreas de apoyo en dos columnas (helper corregido) ──
        y = self._ensure_room(c, data, y, need=140)
        y = two_column_blocks(
            c,
            x=L.margin,
            y=y,
            width=L.content_w,
            gap=14,
            left_title="Fortalezas (lo que se hace bien)",
            left_color=SEMANTIC_SUPERIOR,
            left_items=resumen.get("fortalezas", []),
            right_title="Áreas para apoyar (en qué trabajar)",
            right_color=SEMANTIC_DEFICIT,
            right_items=resumen.get("areas_apoyo", []),
            ensure_room_fn=self._ensure_room,
        )
        y -= 8
        # ── Recomendaciones para la familia ──
        rec_items = resumen.get("que_recomendamos_items") or []
        if rec_items:
            y = self._ensure_room(c, data, y, need=80)
            y = block_header(c, "¿Qué recomendamos?", y)
            for i, item in enumerate(rec_items[:6], start=1):
                y = self._ensure_room(c, data, y, need=28)
                y = bullet(c, f"{i}. {item}", L.margin, y, L.content_w, size=TYPE.body_sm) - 2
            y -= 4
        elif resumen.get("que_recomendamos"):
            y = self._ensure_room(c, data, y, need=80)
            y = block_header(c, "¿Qué recomendamos?", y)
            y = (
                draw_paragraph(
                    c,
                    resumen["que_recomendamos"],
                    L.margin,
                    y,
                    L.content_w,
                    font_name=FONT_SERIF,
                    size=TYPE.body_sm,
                    color=NAVY,
                    leading=TYPE.body_sm * 1.45,
                )
                - 4
            )
        # ── FAQ ──
        if resumen.get("preguntas_frecuentes"):
            y = self._ensure_room(c, data, y, need=80)
            y = block_header(c, "Preguntas frecuentes", y)
            for faq in resumen["preguntas_frecuentes"][:5]:
                y = self._ensure_room(c, data, y, need=50)
                if isinstance(faq, dict):
                    pregunta = faq.get("pregunta", "")
                    respuesta = faq.get("respuesta", "")
                else:
                    pregunta = str(faq[0]) if len(faq) > 0 else ""
                    respuesta = str(faq[1]) if len(faq) > 1 else ""
                if pregunta and respuesta:
                    y = (
                        draw_paragraph(
                            c,
                            pregunta,
                            L.margin,
                            y,
                            L.content_w,
                            font_name=FONT_SANS_BOLD,
                            size=TYPE.body_sm,
                            color=NAVY,
                            leading=TYPE.body_sm * 1.4,
                        )
                        - 2
                    )
                    y = (
                        draw_paragraph(
                            c,
                            respuesta,
                            L.margin + 14,
                            y,
                            L.content_w - 14,
                            font_name=FONT_SANS,
                            size=TYPE.body_sm,
                            color=SLATE,
                            leading=TYPE.body_sm * 1.4,
                        )
                        - 4
                    )
        return y

    def _section_impresion(self, c, data, y: float) -> float:
        has_cie = bool(data.codigo_cie10 and data.codigo_cie10.strip())
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=160)
        y = section_title(c, "Impresión Diagnóstica", y, subtitle="Conclusión clínica · CIE-10 / DSM-5")

        puente = puente_impresion_lenguaje_claro(
            codigo_cie10=(data.codigo_cie10 or "").strip(),
            codigo_desc=(data.codigo_cie10_desc or "").strip(),
        )
        y = callout(
            c,
            puente,
            L.margin,
            y,
            L.content_w,
            accent=SEMANTIC_PROMEDIO,
            fill=SURFACE,
            title="En palabras sencillas",
            size=TYPE.body_sm,
        )
        y -= 6

        if has_cie:
            cie_text = f"Código CIE-10: {data.codigo_cie10.strip()}"
            if data.codigo_cie10_desc:
                cie_text += f"  ·  {data.codigo_cie10_desc}"
            y = callout(
                c,
                cie_text,
                L.margin,
                y,
                L.content_w,
                accent=NAVY,
                fill=SURFACE,
                title="Diagnóstico codificado",
                size=TYPE.body,
            )
            y -= 6
        # Texto verbatim del clínico (siempre se consigna el campo)
        y = info_box(
            c,
            "Impresión diagnóstica del profesional",
            data.obs_impresion_dx,
            L.margin,
            y,
            L.content_w,
            size=TYPE.body,
            placeholder="Pendiente de diligenciar por el profesional.",
        )
        return y - 12

    def _section_recomendaciones(self, c, data, y: float) -> float:
        """Recomendaciones — texto verbatim del clínico (sin generación IA).

        Si el profesional escribió viñetas o agrupó por área, se respeta el
        formato. Si el campo está vacío, se consigna el área igualmente.
        """
        L = LAYOUT
        tiene_obs = bool(data.obs_recomendaciones and data.obs_recomendaciones not in ("N/A", ""))
        y = self._ensure_room(c, data, y, need=140)
        y = section_title(
            c,
            "Recomendaciones",
            y,
            subtitle="Plan de manejo formulado por el profesional",
        )

        if not tiene_obs:
            y = info_box(
                c,
                "Recomendaciones",
                "",
                L.margin,
                y,
                L.content_w,
                size=TYPE.body,
                placeholder="Pendiente de diligenciar por el profesional.",
            )
            return y - 12

        grouped = parse_recomendaciones(data.obs_recomendaciones)
        if list(grouped.keys()) == ["General"]:
            for it in grouped["General"]:
                y = self._ensure_room(c, data, y, need=32)
                y = bullet(c, it["texto"], L.margin, y, L.content_w, size=TYPE.body) - 4
        else:
            priority_color = {
                "alta": SEMANTIC_DEFICIT,
                "media": SEMANTIC_LIMITE,
                "baja": SEMANTIC_PROMEDIO,
            }
            for area in sorted(grouped.keys()):
                items = grouped[area]
                if not items:
                    continue
                y = self._ensure_room(c, data, y, need=64)
                y = block_header(c, area, y)
                order = {"alta": 0, "media": 1, "baja": 2}
                items_sorted = sorted(items, key=lambda x: order.get(x["prioridad"], 1))
                for it in items_sorted:
                    y = self._ensure_room(c, data, y, need=32)
                    color = priority_color.get(it["prioridad"], SLATE)
                    draw_text(
                        c,
                        "●",
                        L.margin,
                        y,
                        font_name=FONT_SANS_BOLD,
                        size=TYPE.body,
                        color=color,
                    )
                    y = (
                        draw_paragraph(
                            c,
                            it["texto"],
                            L.margin + 14,
                            y,
                            L.content_w - 14,
                            font_name=FONT_SANS,
                            size=TYPE.body,
                            color=NAVY,
                        )
                        - 4
                    )
                y -= 6
        return y - 8

    def _section_anexo(self, c, data, y: float) -> float:
        """Anexo de definiciones operativas."""
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=240)
        y = section_title(
            c,
            "Anexo — Definiciones Operativas",
            y,
            subtitle="Convenciones interpretativas utilizadas en este informe",
        )
        defs = [
            (
                "Cociente Intelectual (CI)",
                "Puntuación estándar con media 100 y desviación 15. CIT menor a 70 sugiere déficit; "
                "70-79 limítrofe; 80-89 promedio bajo; 90-109 promedio; 110-119 promedio alto; "
                "120-129 superior; ≥130 muy superior.",
            ),
            (
                "Puntaje escalar (PE)",
                "Subtests Wechsler — media 10, desviación 3. PE de 8-12 equivale al rango promedio.",
            ),
            (
                "Puntuación Z",
                "Desvío en unidades de desviación estándar respecto al grupo normativo. "
                "Z = (PD − μ) / σ. Z ≤ −1 indica rendimiento bajo el promedio; Z ≤ −2 indica déficit clínico.",
            ),
            ("Percentil", "Porcentaje de la población normativa con desempeño igual o inferior al del paciente."),
            (
                "Discrepancia significativa",
                "Diferencia entre índices que excede el umbral de Wechsler. "
                "Líneas críticas: p<.15 (·····) sugieren tendencia; p<.05 (─────) indican diferencia confiable.",
            ),
            (
                "Reliable Change Index (RCI)",
                "Jacobson-Truax. RCI > 1.96 indica cambio confiable (p<.05) entre evaluaciones repetidas. "
                "Se reporta sólo en informes de seguimiento.",
            ),
        ]
        for term, body in defs:
            y = self._ensure_room(c, data, y, need=44)
            draw_text(
                c,
                term,
                L.margin,
                y,
                font_name=FONT_SANS_BOLD,
                size=TYPE.body_sm,
                color=TEAL_DARK,
            )
            y -= 12
            y = (
                draw_paragraph(
                    c,
                    body,
                    L.margin + 6,
                    y,
                    L.content_w - 6,
                    font_name=FONT_SANS,
                    size=TYPE.body_sm,
                    color=SLATE,
                )
                - 6
            )

        # ─── Glosario de términos técnicos ───
        y -= 4
        y = self._ensure_room(c, data, y, need=80)
        y = section_subtitle(
            c,
            "Glosario: palabras técnicas que usamos",
            y,
        )
        y = self._render_glosario_terminos(c, data, y)
        return y

    def _render_glosario_terminos(self, c, data, y: float) -> float:
        """Glosario de términos técnicos estándar (estable, no depende de BD).

        Solo incluye términos que aparecen en el informe del paciente
        (filtrado por presencia en los resultados o en el texto del informe).
        """
        L = LAYOUT
        from .narrative import GLOSARIO_TERMINOS

        # Detectar qué términos aplica mencionar
        # Construir string de búsqueda con todos los datos relevantes del informe
        contenido = ""
        if data.resultados:
            for r in data.resultados:
                contenido += " " + str(r.get("test_nombre", ""))
                contenido += " " + str(r.get("dominio_cognitivo", ""))
                contenido += " " + str(r.get("interpretacion", ""))
        contenido = contenido.lower()
        # Términos que siempre se incluyen (independiente de presencia)
        obligatorios = {"z", "ci"}
        # Términos condicionales
        items: list[tuple[str, str]] = []
        for term, desc in GLOSARIO_TERMINOS.items():
            clave = term.lower().split()[0]  # primer token
            if clave in obligatorios or any(tok in contenido for tok in (term.lower(), clave)):
                items.append((term, desc))
            if len(items) >= 10:
                break
        if not items:
            return y
        y = (
            draw_paragraph(
                c,
                "Definiciones operativas de los términos técnicos utilizados en este informe.",
                L.margin,
                y,
                L.content_w,
                font_name=FONT_SANS,
                size=TYPE.caption,
                color=SLATE,
                leading=TYPE.caption * 1.4,
            )
            - 4
        )
        for term, desc in items:
            y = self._ensure_room(c, data, y, need=32)
            draw_text(
                c,
                term,
                L.margin,
                y,
                font_name=FONT_SANS_BOLD,
                size=TYPE.caption,
                color=TEAL_DARK,
            )
            y -= 11
            y = (
                draw_paragraph(
                    c,
                    desc,
                    L.margin + 6,
                    y,
                    L.content_w - 6,
                    font_name=FONT_SANS,
                    size=TYPE.caption,
                    color=SLATE,
                    leading=TYPE.caption * 1.35,
                )
                - 4
            )
        return y

    def _section_firma(self, c, data, y: float) -> None:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=180)
        y = divider(c, y)
        y = (
            draw_paragraph(
                c,
                data.aviso_legal,
                L.margin,
                y,
                L.content_w,
                font_name=FONT_SANS,
                size=TYPE.micro + 1,
                color=SLATE,
                leading=8,
            )
            - 14
        )

        # §clinical-disclaimer-v2 (2026-05-18): cláusula estándar de
        # responsabilidad profesional. Antes solo aparecía cuando había uso
        # de IA registrado, lo cual implicaba destacar el uso de la
        # herramienta — el clínico pidió matizar. Ahora se imprime SIEMPRE
        # como práctica clínica estándar, alineada con Ley 1090 art. 2 y 36
        # y Resolución 1995. No expone qué herramientas técnicas se usaron.
        from app.domain.clinical_engine.ai_prompts import AI_USAGE_DISCLAIMER

        y = self._ensure_room(c, data, y, need=60)
        y = (
            draw_paragraph(
                c,
                AI_USAGE_DISCLAIMER,
                L.margin,
                y,
                L.content_w,
                font_name=FONT_SANS,
                size=TYPE.micro + 1,
                color=SLATE,
                leading=8,
            )
            - 14
        )

        firma_x = L.page_w - L.margin - 180
        firma_w = 180

        if data.firma_base64:
            try:
                from reportlab.lib.utils import ImageReader

                img = ImageReader(io.BytesIO(base64.b64decode(data.firma_base64)))
                c.drawImage(
                    img,
                    firma_x + 20,
                    y - 38,
                    width=140,
                    height=40,
                    preserveAspectRatio=True,
                    mask="auto",
                )
            except Exception as _exc:
                # §A4-fix: la firma escaneada del clínico falló al dibujarse.
                # Esto SÍ es relevante — el informe firmado va sin firma visual.
                logger.warning("No se pudo dibujar la firma escaneada en el informe: %s", _exc)
        c.setStrokeColorRGB(*NAVY)
        c.setLineWidth(0.8)
        c.line(firma_x, y - 44, firma_x + firma_w, y - 44)
        draw_text(
            c,
            data.profesional_nombre or "—",
            firma_x + firma_w / 2,
            y - 56,
            font_name=FONT_SERIF_BOLD,
            size=TYPE.body_sm,
            color=NAVY,
            align="center",
        )
        if data.profesional_titulo:
            draw_text(
                c,
                data.profesional_titulo,
                firma_x + firma_w / 2,
                y - 67,
                font_name=FONT_SANS,
                size=TYPE.caption,
                color=SLATE,
                align="center",
            )
        if data.profesional_registro:
            draw_text(
                c,
                f"Registro Profesional: {data.profesional_registro}",
                firma_x + firma_w / 2,
                y - 77,
                font_name=FONT_SANS,
                size=TYPE.caption,
                color=SLATE,
                align="center",
            )
