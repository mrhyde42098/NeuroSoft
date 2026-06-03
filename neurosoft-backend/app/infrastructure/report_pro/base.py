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
    draw_ci_kpi_row,
    draw_discrepancies,
    draw_domain_radar,
    draw_normal_curve,
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
    measure_paragraph_height,
    section_subtitle,
    section_title,
    two_column_layout,
)
from .narrative import (
    build_strengths_weaknesses,
    build_synthesis_paragraphs,
    parse_recomendaciones,
)
from .theme import (
    CREAM,
    FONT_SANS,
    FONT_SANS_BOLD,
    FONT_SERIF,
    FONT_SERIF_BOLD,
    LAYOUT,
    NAVY,
    SEMANTIC_DEFICIT,
    SEMANTIC_LIMITE,
    SEMANTIC_PROMEDIO,
    SEMANTIC_SUPERIOR,
    SLATE,
    SLATE_LIGHT,
    SURFACE,
    TEAL,
    TEAL_DARK,
    TEAL_PALE,
    TYPE,
    WHITE,
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
# Versión sincronizada con ``plantillasDocumentales.NORMOGRAMA_COLOMBIANO_VERSION``
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

    # ──────────────────────────────────────────────────────────
    # Entry point
    # ──────────────────────────────────────────────────────────

    def generate(self, data) -> bytes:
        """Construye y retorna los bytes del PDF."""
        ensure_fonts_registered()

        buffer = io.BytesIO()
        NumberedCanvas = _make_numbered_canvas_class(self._draw_footer_factory(data))

        from reportlab.lib.pagesizes import A4
        c = NumberedCanvas(buffer, pagesize=A4)
        c.setTitle(f"Informe Neuropsicológico — {data.nombre_completo}")
        c.setAuthor(data.profesional_nombre or "NeuroSoft")
        c.setSubject(f"Evaluación Neuropsicológica — {self.VARIANT_LABEL}")
        c.setCreator("NeuroSoft App")

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

        y = self._page_top_with_header(c, data)
        y = self._section_sociodemografico(c, data, y)
        y = self._section_motivo_consulta(c, data, y)
        y = self._section_pruebas_aplicadas(c, data, y)
        y = self._section_antecedentes(c, data, y)
        y = self._section_observacion(c, data, y)
        y = self._section_resultados(c, data, y)
        y = self._section_sintesis(c, data, y)
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
        L = LAYOUT

        # ── Banda superior NAVY de fondo ──
        c.setFillColorRGB(*NAVY)
        c.rect(0, L.page_h - 220, L.page_w, 220, fill=1, stroke=0)
        # Acento TEAL diagonal abajo
        c.setFillColorRGB(*TEAL)
        c.rect(0, L.page_h - 224, L.page_w, 4, fill=1, stroke=0)

        # Logo institución (si existe)
        x_logo = L.margin
        if data.logo_base64:
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(io.BytesIO(base64.b64decode(data.logo_base64)))
                c.drawImage(
                    img, x_logo, L.page_h - 80,
                    width=60, height=60,
                    preserveAspectRatio=True, mask="auto",
                )
            except Exception as e:
                logger.debug("Logo no se pudo dibujar: %s", e)

        # Nombre institución
        draw_text(
            c, data.institucion_nombre, x_logo + 72, L.page_h - 40,
            font_name=FONT_SERIF_BOLD, size=TYPE.title_h2, color=WHITE,
        )
        sub_lines = [s for s in (data.institucion_dir, data.institucion_tel) if s]
        for i, ln in enumerate(sub_lines):
            draw_text(
                c, ln, x_logo + 72, L.page_h - 56 - i * 10,
                font_name=FONT_SANS, size=TYPE.caption, color=TEAL_PALE,
            )
        if data.institucion_nit:
            draw_text(
                c, f"NIT {data.institucion_nit}", L.page_w - L.margin, L.page_h - 40,
                font_name=FONT_SANS, size=TYPE.caption, color=TEAL_PALE, align="right",
            )

        # Título principal
        title_y = L.page_h - 130
        draw_text(
            c, "INFORME DE EVALUACIÓN", L.page_w / 2, title_y,
            font_name=FONT_SERIF_BOLD, size=TYPE.title_hero, color=WHITE, align="center",
        )
        draw_text(
            c, "NEUROPSICOLÓGICA", L.page_w / 2, title_y - 28,
            font_name=FONT_SERIF_BOLD, size=TYPE.title_hero, color=WHITE, align="center",
        )
        draw_text(
            c, f"— Variante {self.VARIANT_LABEL} —", L.page_w / 2, title_y - 50,
            font_name=FONT_SANS, size=TYPE.body, color=TEAL_LIGHT_PALE, align="center",
        )

        # ── Tarjeta central con datos paciente ──
        card_y_top = L.page_h - 270
        card_h = 240
        card_x = L.margin + 20
        card_w = L.content_w - 40

        c.setFillColorRGB(*CREAM)
        c.setStrokeColorRGB(*TEAL)
        c.setLineWidth(1.0)
        c.roundRect(card_x, card_y_top - card_h, card_w, card_h, 8, fill=1, stroke=1)
        # Acento superior
        c.setFillColorRGB(*TEAL)
        c.rect(card_x, card_y_top - 8, card_w, 8, fill=1, stroke=0)

        # Etiqueta "PACIENTE"
        draw_text(
            c, "PACIENTE", card_x + 18, card_y_top - 28,
            font_name=FONT_SANS_BOLD, size=TYPE.caption, color=TEAL_DARK,
        )
        # Nombre del paciente
        draw_text(
            c, data.nombre_completo or "—", card_x + 18, card_y_top - 50,
            font_name=FONT_SERIF_BOLD, size=TYPE.title_h1, color=NAVY,
        )

        # Datos resumen — dos columnas
        fila_y = card_y_top - 75
        col_w = (card_w - 40) / 2

        def _kv(label: str, value: str, x: float, y: float) -> None:
            draw_text(
                c, label.upper(), x, y,
                font_name=FONT_SANS_BOLD, size=TYPE.micro + 0.5, color=SLATE,
            )
            draw_text(
                c, str(value or "—"), x, y - 12,
                font_name=FONT_SANS, size=TYPE.body, color=NAVY,
            )

        col1_x = card_x + 18
        col2_x = card_x + 18 + col_w + 20

        _kv("DOCUMENTO", f"{data.tipo_documento} {data.numero_documento}", col1_x, fila_y)
        _kv("FECHA NACIMIENTO",
            data.fecha_nacimiento.strftime("%d/%m/%Y") if data.fecha_nacimiento else "—",
            col2_x, fila_y)

        fila_y -= 32
        _kv("EDAD", data.edad_display, col1_x, fila_y)
        _kv("SEXO", data.sexo, col2_x, fila_y)

        fila_y -= 32
        _kv("ESCOLARIDAD", data.escolaridad, col1_x, fila_y)
        _kv("LATERALIDAD", data.lateralidad, col2_x, fila_y)

        fila_y -= 32
        _kv("FECHA DE EVALUACIÓN",
            data.fecha_atencion.strftime("%d/%m/%Y") if data.fecha_atencion else "—",
            col1_x, fila_y)
        _kv("ORDEN N°", data.orden_no, col2_x, fila_y)

        # ── Protocolo aplicado ──
        if data.protocolo:
            divider_y = card_y_top - card_h + 50
            c.setStrokeColorRGB(*SLATE_LIGHT)
            c.setLineWidth(0.4)
            c.line(card_x + 18, divider_y, card_x + card_w - 18, divider_y)
            draw_text(
                c, "PROTOCOLO APLICADO", card_x + 18, divider_y - 14,
                font_name=FONT_SANS_BOLD, size=TYPE.micro + 0.5, color=SLATE,
            )
            draw_text(
                c, data.protocolo[:80], card_x + 18, divider_y - 26,
                font_name=FONT_SERIF, size=TYPE.body, color=NAVY,
            )

        # ── Profesional firmante (al pie) ──
        if data.profesional_nombre:
            prof_y = L.margin + 110
            draw_text(
                c, "ELABORADO POR", L.page_w / 2, prof_y + 26,
                font_name=FONT_SANS_BOLD, size=TYPE.caption, color=SLATE, align="center",
            )
            draw_text(
                c, data.profesional_nombre, L.page_w / 2, prof_y + 10,
                font_name=FONT_SERIF_BOLD, size=TYPE.title_h2, color=NAVY, align="center",
            )
            if data.profesional_titulo:
                draw_text(
                    c, data.profesional_titulo, L.page_w / 2, prof_y - 4,
                    font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE, align="center",
                )
            if data.profesional_registro:
                draw_text(
                    c, f"Registro: {data.profesional_registro}", L.page_w / 2, prof_y - 16,
                    font_name=FONT_SANS, size=TYPE.caption, color=SLATE, align="center",
                )

        # ── Footer legal en portada ──
        legal_y = L.margin + 30
        legal_text = (
            "Documento confidencial protegido por la Ley 1581 de 2012 (Habeas Data) "
            "y la Resolución 1995 de 1999 (Historia Clínica)."
        )
        draw_text(
            c, legal_text, L.page_w / 2, legal_y,
            font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE, align="center",
        )
        # ID de evaluación si está disponible
        eval_id = getattr(data, "eval_id", "") or ""
        if eval_id:
            draw_text(
                c, f"ID de evaluación: {eval_id}", L.page_w / 2, legal_y - 12,
                font_name=FONT_SANS, size=TYPE.micro, color=SLATE_LIGHT, align="center",
            )

    # ──────────────────────────────────────────────────────────
    # HEADER (cada página interna)
    # ──────────────────────────────────────────────────────────

    def _page_top_with_header(self, c, data) -> float:
        L = LAYOUT
        # Banda blanca + acento teal
        c.setFillColorRGB(*TEAL)
        c.rect(0, L.page_h - 4, L.page_w, 4, fill=1, stroke=0)

        # Logo pequeño + nombre institución (izquierda)
        if data.logo_base64:
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(io.BytesIO(base64.b64decode(data.logo_base64)))
                c.drawImage(
                    img, L.margin, L.page_h - 38,
                    width=22, height=22,
                    preserveAspectRatio=True, mask="auto",
                )
            except Exception as _exc:
                # §A4-fix: imagen del logo institucional corrupta o ilegible.
                # No es bloqueante para el informe, pero queda registro.
                logger.warning("No se pudo dibujar el logo institucional en el header: %s", _exc)
        draw_text(
            c, data.institucion_nombre[:55], L.margin + 28, L.page_h - 26,
            font_name=FONT_SERIF_BOLD, size=TYPE.body_sm, color=NAVY,
        )
        draw_text(
            c, self.VARIANT_SUBTITLE,
            L.margin + 28, L.page_h - 36,
            font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE,
        )

        # Datos paciente (derecha)
        if data.nombre_completo:
            draw_text(
                c, data.nombre_completo[:46], L.page_w - L.margin, L.page_h - 26,
                font_name=FONT_SANS_BOLD, size=TYPE.body_sm, color=NAVY, align="right",
            )
            sub = []
            if data.tipo_documento and data.numero_documento:
                sub.append(f"{data.tipo_documento} {data.numero_documento}")
            if data.fecha_atencion:
                sub.append(data.fecha_atencion.strftime("%d/%m/%Y"))
            if sub:
                draw_text(
                    c, " · ".join(sub), L.page_w - L.margin, L.page_h - 36,
                    font_name=FONT_SANS, size=TYPE.micro + 0.5, color=SLATE, align="right",
                )

        # Línea separadora
        c.setStrokeColorRGB(*SLATE_LIGHT)
        c.setLineWidth(0.3)
        c.line(L.margin, L.page_h - 44, L.page_w - L.margin, L.page_h - 44)

        return L.page_h - 60

    # ──────────────────────────────────────────────────────────
    # FOOTER (paginación + cita legal)
    # ──────────────────────────────────────────────────────────

    def _draw_footer_factory(self, data):
        """Devuelve una closure ``(c, page_num, total_pages) → None``."""
        institucion = data.institucion_nombre or "NeuroSoft App"
        eval_id = (getattr(data, "eval_id", "") or "")[:8]

        def _draw(c, page_num: int, total_pages: int) -> None:
            # No dibujar footer en portada (página 1 si USE_COVER=True)
            if self.USE_COVER and page_num == 1:
                return
            L = LAYOUT
            # Línea
            c.setStrokeColorRGB(*SLATE_LIGHT)
            c.setLineWidth(0.3)
            c.line(L.margin, L.margin_bottom_footer - 8,
                   L.page_w - L.margin, L.margin_bottom_footer - 8)
            # Texto izquierda: institución + cita legal corta + versión normograma
            left = (
                f"{institucion}  ·  Confidencial — Ley 1581/2012 · Res. 1995/1999"
                f"  ·  Normograma {NORMOGRAMA_VERSION}"
            )
            draw_text(
                c, left, L.margin, L.margin_bottom_footer - 20,
                font_name=FONT_SANS, size=TYPE.micro, color=SLATE,
            )
            # Centro: variante
            draw_text(
                c, f"Variante {self.VARIANT_LABEL}", L.page_w / 2,
                L.margin_bottom_footer - 20,
                font_name=FONT_SANS, size=TYPE.micro, color=SLATE_LIGHT, align="center",
            )
            # Derecha: paginación + eval_id
            right = f"Página {page_num} de {total_pages}"
            if eval_id:
                right += f"  ·  ID {eval_id}"
            draw_text(
                c, right, L.page_w - L.margin, L.margin_bottom_footer - 20,
                font_name=FONT_SANS_BOLD, size=TYPE.micro, color=NAVY, align="right",
            )

        return _draw

    # ──────────────────────────────────────────────────────────
    # SECCIONES (compartidas — subclases pueden sobreescribir)
    # ──────────────────────────────────────────────────────────

    def _section_sociodemografico(self, c, data, y: float) -> float:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=180)
        y = section_title(c, "Información Sociodemográfica", y)
        items = [
            ("Nombre", data.nombre_completo),
            ("Documento", f"{data.tipo_documento} {data.numero_documento}"),
            ("Fecha de nacimiento",
             data.fecha_nacimiento.strftime("%d/%m/%Y") if data.fecha_nacimiento else "—"),
            ("Edad", data.edad_display),
            ("Sexo", data.sexo),
            ("Escolaridad", data.escolaridad),
            ("Lateralidad", data.lateralidad),
            ("Ocupación", data.ocupacion),
            ("Ciudad", data.ciudad),
            ("Acompañante", data.acompanante),
            ("Remite", data.remite),
            ("EPS / Asegurador", data.eps),
        ]
        y = two_column_layout(
            c, items, L.margin, y,
            column_w=(L.content_w - 16) / 2, gap=16,
            size=TYPE.body_sm,
        )
        return y - 12

    def _section_motivo_consulta(self, c, data, y: float) -> float:
        if not data.motivo_consulta or data.motivo_consulta in ("N/A", ""):
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=80)
        y = section_title(c, "Motivo de Consulta", y)
        y = draw_paragraph(
            c, data.motivo_consulta, L.margin, y, L.content_w,
            font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
        )
        return y - 14

    def _section_pruebas_aplicadas(self, c, data, y: float) -> float:
        """Tabla limpia con las pruebas administradas."""
        if not data.resultados or not data.protocolo or len(data.resultados) < 2:
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=110)
        y = section_title(
            c, "Pruebas Aplicadas",
            y,
            subtitle=f"Protocolo: {data.protocolo}",
        )
        rows = []
        for r in data.resultados:
            nombre = str(r.get("test_nombre", r.get("test_id", "")))
            dominio = str(r.get("dominio_cognitivo", "—"))[:30]
            dur = r.get("duracion_estimada", "—")
            rows.append([nombre[:38], dominio, str(dur)])
        col_widths = [L.content_w * 0.45, L.content_w * 0.35, L.content_w * 0.20]
        # Paginar manualmente la tabla
        row_h = 13
        while rows:
            available = max(1, int((y - L.content_bottom - 30) // row_h))
            chunk, rows = rows[:available], rows[available:]
            y = draw_table(
                c, ["Prueba", "Dominio", "Dur."], chunk, col_widths,
                L.margin, y, row_h=row_h, size=TYPE.caption,
            )
            if rows:
                y = self._new_page(c, data)
        return y - 12

    def _section_antecedentes(self, c, data, y: float) -> float:
        L = LAYOUT
        antec = [
            ("Patológicos / Médicos", data.patologicos_medicos),
            ("Sensoriales / Motores", data.sensoriales_motores),
            ("Psiquiátricos", data.psiquiatricos),
            ("Farmacológicos", data.farmacologicos),
            ("Traumáticos", data.traumaticos),
            ("Quirúrgicos", data.quirurgicos),
            ("Tóxicos", data.toxicos),
            ("Alérgicos", data.alergicos),
            ("Terapéuticos", data.terapeuticos),
            ("Paraclínicos", data.paraclinicos),
            ("Familiares", data.familiares),
        ]
        antec = [(lbl, val) for lbl, val in antec
                 if val and val not in ("N/A", "", "(-)", "-")]
        if not antec:
            return y

        y = self._ensure_room(c, data, y, need=120)
        y = section_title(c, "Antecedentes", y)

        col_w = (L.content_w - 16) / 2
        col1_y = col2_y = y
        for i, (lbl, val) in enumerate(antec):
            is_left = (i % 2 == 0)
            target_x = L.margin if is_left else L.margin + col_w + 16
            target_y = col1_y if is_left else col2_y
            block_h = 14 + measure_paragraph_height(
                val, col_w, font_name=FONT_SANS, size=TYPE.body_sm,
            )
            # Si el bloque no cabe, salto de página y reseteo ambas columnas
            if target_y - block_h < LAYOUT.content_bottom + 40:
                new_y = self._new_page(c, data)
                col1_y = col2_y = new_y
                target_y = new_y
            target_y = block_header(c, lbl, target_y)
            target_y = draw_paragraph(
                c, val, target_x, target_y, col_w,
                font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
            ) - 6
            if is_left:
                col1_y = target_y
            else:
                col2_y = target_y
        return min(col1_y, col2_y) - 8

    def _section_observacion(self, c, data, y: float) -> float:
        L = LAYOUT
        secs = [
            ("Apariencia y conducta", data.obs_clinica_general),
            ("Atención y concentración", data.obs_atencion),
            ("Memoria", data.obs_memoria),
            ("Praxias y gnosias", data.obs_praxias_gnosias),
            ("Lenguaje", data.obs_lenguaje),
            ("Funciones ejecutivas", data.obs_funciones_ejecutivas),
            ("Emociones y comportamiento", data.obs_emociones),
            ("Cociente intelectual (observación)", data.obs_ci),
            ("Funcionalidad / AVDs", data.obs_funcionalidad),
        ]
        secs = [(lbl, val) for lbl, val in secs
                if val and val not in ("N/A", "")]
        if not secs:
            return y

        y = self._ensure_room(c, data, y, need=160)
        y = section_title(
            c, "Observación Clínica",
            y, subtitle="Hallazgos cualitativos durante la administración",
        )

        for lbl, val in secs:
            y = self._ensure_room(c, data, y, need=80)
            y = block_header(c, lbl, y)
            y = draw_paragraph(
                c, val, L.margin, y, L.content_w,
                font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
            ) - 8
        return y - 4

    def _section_resultados(self, c, data, y: float) -> float:
        if not data.resultados:
            return y

        # ─── KPI row de CI ───
        y = self._ensure_room(c, data, y, need=240)
        y = section_title(
            c, "Resultados Cuantitativos",
            y, subtitle="Puntajes estandarizados y perfil cognitivo",
        )

        ci_y_before = y
        y = draw_ci_kpi_row(c, data.resultados, y)
        if y < ci_y_before:
            y -= 6

        # ─── Discrepancias entre índices ───
        n_ci = sum(1 for r in data.resultados if r.get("tipo_metrica") == "ci")
        if n_ci >= 2:
            y = self._ensure_room(c, data, y, need=160)
            y = draw_discrepancies(c, data.resultados, y)
            y -= 6

        # ─── Radar de dominios ───
        y = self._ensure_room(c, data, y, need=280)
        y_before = y
        y = draw_domain_radar(c, data.resultados, y)
        if y < y_before:
            y -= 6

        # ─── Curva normal con marcadores ───
        n_z = sum(
            1 for r in data.resultados
            if r.get("z_equivalente") is not None
            and r.get("tipo_metrica") != "ci"
        )
        if n_z >= 5:
            y = self._ensure_room(c, data, y, need=160)
            y = draw_normal_curve(c, data.resultados, y)
            y -= 6

        # ─── Perfil Z horizontal ───
        if n_z >= 1:
            y = self._ensure_room(c, data, y, need=120)
            y = section_subtitle(c, "Perfil Z por prueba", y)
            y = draw_z_profile(c, data.resultados, y)
            y -= 6

        # ─── Tabla detallada de puntajes ───
        y = self._ensure_room(c, data, y, need=140)
        y = section_subtitle(c, "Tabla detallada de puntajes", y)
        y = self._draw_score_table(c, data, data.resultados, y)
        return y - 8

    def _draw_score_table(self, c, data, resultados, y: float) -> float:
        L = LAYOUT
        col_widths = [
            L.content_w * 0.30, L.content_w * 0.13, L.content_w * 0.13,
            L.content_w * 0.13, L.content_w * 0.31,
        ]
        headers = ["Prueba", "PD", "Escalar/CI", "Z", "Interpretación"]
        rows = []
        row_colors = []
        for r in resultados:
            nombre = str(r.get("test_nombre", r.get("test_id", "")))[:34]
            pd = r.get("puntaje_bruto")
            esc = r.get("puntaje_escalar")
            z = r.get("z_equivalente")
            interp = str(r.get("interpretacion", "—"))[:28]
            rows.append([
                nombre,
                str(int(pd)) if pd is not None else "—",
                str(int(esc)) if esc is not None else "—",
                f"{z:+.2f}" if z is not None else "—",
                interp,
            ])
            row_colors.append(semantic_color_for_z(z))
        # Paginación
        row_h = 13
        while rows:
            available = max(1, int((y - L.content_bottom - 30) // row_h))
            chunk, rows = rows[:available], rows[available:]
            colors_chunk, row_colors = row_colors[:available], row_colors[available:]
            y = draw_table(
                c, headers, chunk, col_widths,
                L.margin, y, row_h=row_h, size=TYPE.body_sm,
                row_colors=colors_chunk,
            )
            if rows:
                y = self._new_page(c, data)
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
            c, "Síntesis Clínica Integradora",
            y, subtitle="Lectura cuantitativa de los hallazgos",
        )
        for p in paragraphs:
            y = self._ensure_room(c, data, y, need=60)
            y = draw_paragraph(
                c, p, L.margin, y, L.content_w,
                font_name=FONT_SERIF, size=TYPE.body, color=NAVY,
                leading=TYPE.body * 1.45,
            ) - 6

        # Fortalezas / debilidades en dos columnas
        weak, strong = build_strengths_weaknesses(data.resultados)
        if weak or strong:
            y = self._ensure_room(c, data, y, need=140)
            col_w = (L.content_w - 16) / 2
            y_w = y_s = y
            if weak:
                y_w = block_header(c, "Áreas con desempeño disminuido", y_w, color=SEMANTIC_DEFICIT)
                for item in weak[:6]:
                    y_w = bullet(c, item, L.margin, y_w, col_w) - 2
            if strong:
                y_s = block_header(c, "Áreas con desempeño preservado / superior",
                                   y_s, color=SEMANTIC_SUPERIOR)
                for item in strong[:5]:
                    y_s = bullet(c, item, L.margin + col_w + 16, y_s, col_w) - 2
            y = min(y_w, y_s)
        return y - 10

    def _section_impresion(self, c, data, y: float) -> float:
        has_dx = data.obs_impresion_dx and data.obs_impresion_dx not in ("N/A", "")
        has_cie = bool(data.codigo_cie10 and data.codigo_cie10.strip())
        if not has_dx and not has_cie:
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=140)
        y = section_title(c, "Impresión Diagnóstica", y, subtitle="DSM-5 / CIE-10")

        if has_cie:
            cie_text = f"Código CIE-10: {data.codigo_cie10.strip()}"
            if data.codigo_cie10_desc:
                cie_text += f"  ·  {data.codigo_cie10_desc}"
            y = callout(
                c, cie_text, L.margin, y, L.content_w,
                accent=NAVY, fill=SURFACE, title="Diagnóstico codificado",
                size=TYPE.body_sm,
            )
            y -= 4
        if has_dx:
            y = draw_paragraph(
                c, data.obs_impresion_dx, L.margin, y, L.content_w,
                font_name=FONT_SERIF, size=TYPE.body, color=NAVY,
                leading=TYPE.body * 1.45,
            ) - 6
        return y

    def _section_recomendaciones(self, c, data, y: float) -> float:
        if not data.obs_recomendaciones or data.obs_recomendaciones in ("N/A", ""):
            return y
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=160)
        y = section_title(
            c, "Recomendaciones",
            y, subtitle="Plan de manejo agrupado por área y prioridad",
        )

        grouped = parse_recomendaciones(data.obs_recomendaciones)
        # Sólo "General" → lista plana
        if list(grouped.keys()) == ["General"]:
            for it in grouped["General"]:
                y = self._ensure_room(c, data, y, need=30)
                y = bullet(c, it["texto"], L.margin, y, L.content_w) - 2
            return y - 8

        priority_color = {
            "alta": SEMANTIC_DEFICIT,
            "media": SEMANTIC_LIMITE,
            "baja": SEMANTIC_PROMEDIO,
        }
        for area in sorted(grouped.keys()):
            items = grouped[area]
            if not items:
                continue
            y = self._ensure_room(c, data, y, need=60)
            y = block_header(c, area, y)
            order = {"alta": 0, "media": 1, "baja": 2}
            items_sorted = sorted(items, key=lambda x: order.get(x["prioridad"], 1))
            for it in items_sorted:
                y = self._ensure_room(c, data, y, need=30)
                color = priority_color.get(it["prioridad"], SLATE)
                draw_text(
                    c, "●", L.margin, y,
                    font_name=FONT_SANS_BOLD, size=TYPE.body, color=color,
                )
                y = draw_paragraph(
                    c, it["texto"], L.margin + 12, y, L.content_w - 12,
                    font_name=FONT_SANS, size=TYPE.body_sm, color=NAVY,
                ) - 2
            y -= 6
        return y - 6

    def _section_anexo(self, c, data, y: float) -> float:
        """Anexo de definiciones operativas."""
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=240)
        y = section_title(
            c, "Anexo — Definiciones Operativas",
            y, subtitle="Convenciones interpretativas utilizadas en este informe",
        )
        defs = [
            ("Cociente Intelectual (CI)",
             "Puntuación estándar con media 100 y desviación 15. CIT menor a 70 sugiere déficit; "
             "70-79 limítrofe; 80-89 promedio bajo; 90-109 promedio; 110-119 promedio alto; "
             "120-129 superior; ≥130 muy superior."),
            ("Puntaje escalar (PE)",
             "Subtests Wechsler — media 10, desviación 3. PE de 8-12 equivale al rango promedio."),
            ("Puntuación Z",
             "Desvío en unidades de desviación estándar respecto al grupo normativo. "
             "Z = (PD − μ) / σ. Z ≤ −1 indica rendimiento bajo el promedio; Z ≤ −2 indica déficit clínico."),
            ("Percentil",
             "Porcentaje de la población normativa con desempeño igual o inferior al del paciente."),
            ("Discrepancia significativa",
             "Diferencia entre índices que excede el umbral de Wechsler. "
             "Líneas críticas: p<.15 (·····) sugieren tendencia; p<.05 (─────) indican diferencia confiable."),
            ("Reliable Change Index (RCI)",
             "Jacobson-Truax. RCI > 1.96 indica cambio confiable (p<.05) entre evaluaciones repetidas. "
             "Se reporta sólo en informes de seguimiento."),
        ]
        for term, body in defs:
            y = self._ensure_room(c, data, y, need=44)
            draw_text(
                c, term, L.margin, y,
                font_name=FONT_SANS_BOLD, size=TYPE.body_sm, color=TEAL_DARK,
            )
            y -= 12
            y = draw_paragraph(
                c, body, L.margin + 6, y, L.content_w - 6,
                font_name=FONT_SANS, size=TYPE.body_sm, color=SLATE,
            ) - 6
        return y

    def _section_firma(self, c, data, y: float) -> None:
        L = LAYOUT
        y = self._ensure_room(c, data, y, need=180)
        y = divider(c, y)
        y = draw_paragraph(
            c, data.aviso_legal, L.margin, y, L.content_w,
            font_name=FONT_SANS, size=TYPE.micro + 1, color=SLATE,
            leading=8,
        ) - 14

        # §clinical-disclaimer-v2 (2026-05-18): cláusula estándar de
        # responsabilidad profesional. Antes solo aparecía cuando había uso
        # de IA registrado, lo cual implicaba destacar el uso de la
        # herramienta — el clínico pidió matizar. Ahora se imprime SIEMPRE
        # como práctica clínica estándar, alineada con Ley 1090 art. 2 y 36
        # y Resolución 1995. No expone qué herramientas técnicas se usaron.
        from app.domain.clinical_engine.ai_prompts import AI_USAGE_DISCLAIMER
        y = self._ensure_room(c, data, y, need=60)
        y = draw_paragraph(
            c, AI_USAGE_DISCLAIMER, L.margin, y, L.content_w,
            font_name=FONT_SANS, size=TYPE.micro + 1, color=SLATE,
            leading=8,
        ) - 14

        firma_x = L.page_w - L.margin - 180
        firma_w = 180

        if data.firma_base64:
            try:
                from reportlab.lib.utils import ImageReader
                img = ImageReader(io.BytesIO(base64.b64decode(data.firma_base64)))
                c.drawImage(
                    img, firma_x + 20, y - 38,
                    width=140, height=40,
                    preserveAspectRatio=True, mask="auto",
                )
            except Exception as _exc:
                # §A4-fix: la firma escaneada del clínico falló al dibujarse.
                # Esto SÍ es relevante — el informe firmado va sin firma visual.
                logger.warning("No se pudo dibujar la firma escaneada en el informe: %s", _exc)
        c.setStrokeColorRGB(*NAVY)
        c.setLineWidth(0.8)
        c.line(firma_x, y - 44, firma_x + firma_w, y - 44)
        draw_text(
            c, data.profesional_nombre or "—",
            firma_x + firma_w / 2, y - 56,
            font_name=FONT_SERIF_BOLD, size=TYPE.body_sm, color=NAVY, align="center",
        )
        if data.profesional_titulo:
            draw_text(
                c, data.profesional_titulo,
                firma_x + firma_w / 2, y - 67,
                font_name=FONT_SANS, size=TYPE.caption, color=SLATE, align="center",
            )
        if data.profesional_registro:
            draw_text(
                c, f"Registro Profesional: {data.profesional_registro}",
                firma_x + firma_w / 2, y - 77,
                font_name=FONT_SANS, size=TYPE.caption, color=SLATE, align="center",
            )
