"""
app/infrastructure/report_service.py
======================================
Generador de Informe de Evaluación Neuropsicológica en PDF.

Usa ReportLab (puro Python, sin dependencias externas de sistema).
Genera un informe de 3-4 páginas con:
  - Encabezado institucional con logo (si disponible)
  - Información sociodemográfica del paciente
  - Antecedentes médicos y comportamentales
  - Observaciones clínicas por dominio
  - Gráfica Z horizontal (perfil cognitivo)
  - Tabla de puntajes completa
  - Impresión diagnóstica y recomendaciones
  - Firma del profesional

Dependencia: reportlab >= 4.0
    pip install reportlab
"""

from __future__ import annotations

import base64
import io
import json
import logging
from dataclasses import dataclass, field
from datetime import date

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Colores corporativos (configurables por PreferenciasInforme)
# ─────────────────────────────────────────────────────────────
AZUL_HEADER  = (0.07, 0.28, 0.55)   # #12468c
AZUL_SECCION = (0.18, 0.45, 0.71)   # #2e73b5
GRIS_CLARO   = (0.94, 0.94, 0.94)
GRIS_TEXTO   = (0.25, 0.25, 0.25)
ROJO_BAJO    = (0.77, 0.09, 0.29)   # #c4173a
NARANJA_LIM  = (0.96, 0.49, 0.17)   # #f57d2c
VERDE_PROM   = (0.17, 0.63, 0.17)   # #2ca12a
AZUL_SUP     = (0.10, 0.49, 0.82)   # #1a7dd1
BLANCO       = (1, 1, 1)
NEGRO        = (0, 0, 0)


def _nivel_color(z: float | None) -> tuple[float, float, float]:
    if z is None:
        return GRIS_TEXTO
    if z <= -2:
        return ROJO_BAJO
    if z <= -1:
        return NARANJA_LIM
    if z <= 1:
        return VERDE_PROM
    return AZUL_SUP


def _nivel_label(interp: str) -> str:
    mapping = {
        'Bajo': 'BAJO', 'Limítrofe': 'LIMÍTROFE',
        'Promedio Bajo': 'PROM. BAJO', 'Promedio': 'PROMEDIO',
        'Promedio Alto': 'PROM. ALTO', 'Superior': 'SUPERIOR',
        'Muy Superior': 'MUY SUPERIOR',
        'Normal': 'NORMAL', 'DL': 'DEP. LEVE', 'DE': 'DEP. ESTAB.',
    }
    for k, v in mapping.items():
        if k.lower() in interp.lower():
            return v
    return interp.upper()[:12]


# ─────────────────────────────────────────────────────────────
# Data container para el generador
# ─────────────────────────────────────────────────────────────

@dataclass
class ReportData:
    """
    Toda la información necesaria para generar el informe.
    Se construye en el use case antes de llamar a generate_pdf().
    """
    # Institución
    institucion_nombre: str = "Consultorio Neuropsicológico"
    institucion_nit:    str = ""
    institucion_dir:    str = ""
    institucion_tel:    str = ""
    logo_base64:        str | None = None

    # Paciente
    nombre_completo:    str = ""
    numero_documento:   str = ""
    tipo_documento:     str = "CC"
    fecha_nacimiento:   date | None = None
    fecha_atencion:     date | None = None
    edad_display:       str = ""
    sexo:               str = ""
    escolaridad:        str = ""
    lateralidad:        str = ""
    ocupacion:          str = ""
    ciudad:             str = ""
    acompanante:        str = ""
    remite:             str = ""
    orden_no:           str = ""
    eps:                str = ""
    poblacion:          str = ""

    # Historia clínica (campos opcionales - si no hay HC se omiten)
    motivo_consulta:        str = ""
    patologicos_medicos:    str = ""
    sensoriales_motores:    str = ""
    psiquiatricos:          str = ""
    farmacologicos:         str = ""
    traumaticos:            str = ""
    quirurgicos:            str = ""
    toxicos:                str = ""
    alergicos:              str = ""
    terapeuticos:           str = ""
    paraclinicos:           str = ""
    familiares:             str = ""
    vive_con:               str = ""
    abc:                    str = ""
    escolar_laboral:        str = ""
    patron_sueno:           str = ""
    patron_alimentacion:    str = ""
    comportamiento_animo:   str = ""

    # Observaciones clínicas por dominio
    obs_clinica_general:        str = ""
    obs_atencion:               str = ""
    obs_memoria:                str = ""
    obs_praxias_gnosias:        str = ""
    obs_lenguaje:               str = ""
    obs_funciones_ejecutivas:   str = ""
    obs_emociones:              str = ""
    obs_ci:                     str = ""
    obs_impresion_dx:           str = ""
    obs_funcionalidad:          str = ""
    obs_recomendaciones:        str = ""

    # Resultados del engine
    resultados:         list[dict] = field(default_factory=list)  # List[ResultadoPruebaDTO.model_dump()]
    protocolo:          str = ""
    puntos_debiles:     list[str] = field(default_factory=list)
    puntos_fuertes:     list[str] = field(default_factory=list)
    advertencias:       list[str] = field(default_factory=list)
    pruebas_realizadas: int = 0

    # Profesional
    profesional_nombre:    str = ""
    profesional_titulo:    str = ""
    profesional_registro:  str = ""
    firma_base64:          str | None = None

    # Código CIE-10 (de clinical_histories.codigo_cie10)
    codigo_cie10: str = ""
    codigo_cie10_desc: str = ""

    # Aviso legal
    aviso_legal: str = (
        "El diagnóstico presentado se realiza a partir del perfil neuropsicológico analizado "
        "en la evaluación y es válido con la información presentada durante la consulta. "
        "El diagnóstico final se dará en el contexto de un análisis multidisciplinar. "
        "Sus características se acercan o guardan relación con los criterios del CIE-10."
    )

    # ID de evaluación (lo usa la variante Pro para el footer/portada)
    eval_id: str = ""

    # Campos específicos de la variante "Inconcluso" — sólo se llenan si la
    # evaluación se cerró antes de completarse.
    informe_inconcluso_cat:  str = ""   # ej. "no_colabora", "fatiga", "tiempo"
    informe_inconcluso_nota: str = ""   # texto libre del clínico

    # §clinical-disclaimer-v2: estos campos quedan SOLO para trazabilidad
    # interna (tabla `ai_logs` y auditoría). NO se exponen en el PDF —
    # la cláusula de responsabilidad profesional se imprime siempre como
    # práctica estándar, sin destacar el uso de herramientas técnicas.
    ai_used: bool = False
    ai_prompts_used: list[str] = field(default_factory=list)


# ─────────────────────────────────────────────────────────────
# Generador principal
# ─────────────────────────────────────────────────────────────

class NeuroPDFGenerator:
    """
    Genera el informe de evaluación neuropsicológica en PDF.

    Uso:
        gen = NeuroPDFGenerator()
        pdf_bytes = gen.generate(report_data)
    """

    # Medidas de página A4 en puntos (1pt = 1/72 inch)
    PAGE_W = 595.27
    PAGE_H = 841.89
    MARGIN = 36          # ~1.27cm
    CONTENT_W = PAGE_W - 2 * MARGIN
    COL_LEFT  = MARGIN
    COL_RIGHT = PAGE_W - MARGIN

    def generate(self, data: ReportData) -> bytes:
        """Genera el PDF y retorna los bytes."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            raise RuntimeError(
                "reportlab no está instalado. "
                "Ejecuta: pip install reportlab"
            )

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setTitle(f"Informe Neuropsicológico — {data.nombre_completo}")
        c.setAuthor(data.profesional_nombre or "NeuroSoft")
        c.setSubject("Evaluación Neuropsicológica")

        # ── Página 1: Encabezado + Sociodemográfico + Antecedentes ──
        y = self._draw_header(c, data)
        y = self._draw_section_sociodemografico(c, data, y)
        y = self._draw_section_antecedentes(c, data, y)
        y = self._draw_section_funcional(c, data, y)

        # ── Página 2+: Observaciones clínicas + Resultados ──
        if y < 200:
            c.showPage()
            y = self.PAGE_H - self.MARGIN

        y = self._draw_section_observacion(c, data, y)

        # Resultados: tabla + gráfica Z
        if data.resultados:
            if y < 250:
                c.showPage()
                y = self.PAGE_H - self.MARGIN
            y = self._draw_section_resultados(c, data, y)

        # ── Página final: IDx + Recomendaciones + Firma ──
        if y < 200:
            c.showPage()
            y = self.PAGE_H - self.MARGIN

        y = self._draw_section_impresion(c, data, y)
        y = self._draw_section_recomendaciones(c, data, y)
        self._draw_firma(c, data, y)
        self._draw_footer(c, data)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    # ──────────────────────────────────────────────────────────
    # ENCABEZADO
    # ──────────────────────────────────────────────────────────

    def _draw_header(self, c, data: ReportData) -> float:

        # Fondo azul header
        c.setFillColorRGB(*AZUL_HEADER)
        c.rect(0, self.PAGE_H - 75, self.PAGE_W, 75, fill=1, stroke=0)

        # Logo (si existe)
        logo_drawn = False
        if data.logo_base64:
            try:
                img_bytes = base64.b64decode(data.logo_base64)
                img_reader = __import__('reportlab.lib.utils', fromlist=['ImageReader']).ImageReader(io.BytesIO(img_bytes))
                c.drawImage(img_reader, self.MARGIN, self.PAGE_H - 68, width=55, height=55,
                            preserveAspectRatio=True, mask='auto')
                logo_drawn = True
            except Exception as _e:
                logger.warning("Logo no se pudo decodificar para PDF: %s", _e)

        x_title = self.MARGIN + (65 if logo_drawn else 0)

        # Título del informe
        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_title, self.PAGE_H - 28, "Informe de Evaluación")
        c.setFont("Helvetica-Bold", 16)
        c.drawString(x_title, self.PAGE_H - 46, "Neuropsicológica")

        # Datos institución (derecha)
        c.setFont("Helvetica", 7.5)
        right_x = self.COL_RIGHT
        c.drawRightString(right_x, self.PAGE_H - 22, data.institucion_nombre)
        if data.institucion_nit:
            c.drawRightString(right_x, self.PAGE_H - 32, f"NIT {data.institucion_nit}")
        if data.institucion_dir:
            c.drawRightString(right_x, self.PAGE_H - 42, data.institucion_dir)
        if data.institucion_tel:
            c.drawRightString(right_x, self.PAGE_H - 52, data.institucion_tel)

        # Caja naranja de orden/fechas
        c.setFillColorRGB(0.95, 0.40, 0.10)
        c.rect(self.COL_RIGHT - 120, self.PAGE_H - 75, 120, 75, fill=1, stroke=0)
        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 7)
        box_x = self.COL_RIGHT - 115
        c.drawString(box_x, self.PAGE_H - 14, "F. Entrega")
        c.setFont("Helvetica", 7)
        c.drawString(box_x, self.PAGE_H - 24, data.fecha_atencion.strftime("%d/%m/%Y") if data.fecha_atencion else "—")
        c.setFont("Helvetica-Bold", 7)
        c.drawString(box_x, self.PAGE_H - 36, "Orden No")
        c.setFont("Helvetica-Bold", 9)
        c.drawString(box_x, self.PAGE_H - 47, data.orden_no or data.numero_documento or "—")
        c.setFont("Helvetica-Bold", 7)
        c.drawString(box_x, self.PAGE_H - 59, "Fecha Atención")
        c.setFont("Helvetica", 7)
        c.drawString(box_x, self.PAGE_H - 69, data.fecha_atencion.strftime("%d/%m/%Y") if data.fecha_atencion else "—")

        return self.PAGE_H - 80

    # ──────────────────────────────────────────────────────────
    # HELPERS
    # ──────────────────────────────────────────────────────────

    def _section_title(self, c, title: str, y: float) -> float:
        """Dibuja un título de sección con fondo azul."""
        h = 14
        c.setFillColorRGB(*AZUL_SECCION)
        c.rect(self.MARGIN, y - h, self.CONTENT_W, h, fill=1, stroke=0)
        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(self.MARGIN + 4, y - 10, title)
        return y - h - 4

    def _field_row(self, c, label: str, value: str, x: float, y: float, w: float = 180) -> float:
        """Dibuja label + valor en una línea."""
        c.setFillColorRGB(*GRIS_TEXTO)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(x, y, label)
        c.setFont("Helvetica", 7.5)
        # Truncate if too long
        max_chars = max(1, int(w / 4.5))
        val = str(value or "—")[:max_chars]
        c.drawString(x + len(label) * 5 + 3, y, val)
        return y - 11

    def _text_block(self, c, text: str, x: float, y: float, w: float, min_y: float = 100) -> float:
        """Dibuja un bloque de texto con word-wrap simple."""
        if not text or text.strip() in ('', 'N/A', 'n/a'):
            return y
        c.setFont("Helvetica", 7.5)
        c.setFillColorRGB(*GRIS_TEXTO)
        words = str(text).split()
        line = ""
        chars_per_line = max(1, int(w / 4.3))
        for word in words:
            if len(line) + len(word) + 1 <= chars_per_line:
                line = line + " " + word if line else word
            else:
                if y < min_y:
                    c.showPage()
                    y = self.PAGE_H - self.MARGIN
                    self._draw_footer(c, None)
                c.drawString(x, y, line)
                y -= 10
                line = word
        if line:
            c.drawString(x, y, line)
            y -= 10
        return y

    def _check_page(self, c, y: float, need: float = 60, data=None) -> float:
        if y < need:
            c.showPage()
            if data:
                self._draw_footer(c, data)
            return self.PAGE_H - self.MARGIN
        return y

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: SOCIODEMOGRÁFICO
    # ──────────────────────────────────────────────────────────

    def _draw_section_sociodemografico(self, c, data: ReportData, y: float) -> float:
        y -= 4
        y = self._section_title(c, "Información Sociodemográfica", y)

        # Fila 1: nombre y documento
        c.setFillColorRGB(*GRIS_CLARO)
        c.rect(self.MARGIN, y - 12, self.CONTENT_W, 12, fill=1, stroke=0)
        c.setFillColorRGB(*GRIS_TEXTO)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(self.MARGIN + 3, y - 9, "Nombre completo")
        c.setFont("Helvetica", 7.5)
        c.drawString(self.MARGIN + 70, y - 9, data.nombre_completo)
        c.setFont("Helvetica-Bold", 7.5)
        c.drawString(self.COL_RIGHT - 120, y - 9, "Documento")
        c.setFont("Helvetica", 7.5)
        c.drawString(self.COL_RIGHT - 75, y - 9, f"{data.numero_documento}  {data.tipo_documento}")
        y -= 14

        # Filas de datos en cuadrícula
        rows = [
            [("Edad", data.edad_display), ("Estado Civil", ""), ("Escolaridad", data.escolaridad), ("Ocupación", data.ocupacion)],
            [("Fecha nacimiento", data.fecha_nacimiento.strftime("%d/%m/%Y") if data.fecha_nacimiento else ""), ("Ciudad", data.ciudad), ("Acompañante", data.acompanante), ("Lateralidad", data.lateralidad)],
            [("Teléfono", ""), ("Dirección", ""), ("Correo", ""), ("Remite", data.remite)],
        ]
        col_w = self.CONTENT_W / 4
        for row in rows:
            for i, (lbl, val) in enumerate(row):
                cx = self.MARGIN + i * col_w
                c.setFont("Helvetica-Bold", 7)
                c.setFillColorRGB(*GRIS_TEXTO)
                c.drawString(cx + 3, y - 3, lbl)
                c.setFont("Helvetica", 7)
                c.drawString(cx + 3, y - 12, str(val or "—")[:22])
            # Bottom border
            c.setStrokeColorRGB(0.8, 0.8, 0.8)
            c.line(self.MARGIN, y - 14, self.COL_RIGHT, y - 14)
            y -= 16

        return y - 2

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: ANTECEDENTES
    # ──────────────────────────────────────────────────────────

    def _draw_section_antecedentes(self, c, data: ReportData, y: float) -> float:
        y -= 4
        # Motivo de consulta (si existe)
        if data.motivo_consulta and data.motivo_consulta not in ('N/A', ''):
            y = self._section_title(c, "Motivo de Consulta", y)
            y = self._text_block(c, data.motivo_consulta, self.MARGIN + 3, y, self.CONTENT_W - 6)
            y -= 4

        y = self._section_title(c, "Antecedentes Médicos y Comportamentales", y)

        # Dos columnas
        col_w = self.CONTENT_W / 2 - 4
        antec_left = [
            ("Patológicos / Médicos", data.patologicos_medicos),
            ("Sensoriales / Motores", data.sensoriales_motores),
            ("Psiquiátricos", data.psiquiatricos),
            ("Farmacológicos", data.farmacologicos),
            ("Traumáticos", data.traumaticos),
        ]
        antec_right = [
            ("Alérgicos", data.alergicos),
            ("Tóxicos", data.toxicos),
            ("Terapéuticos", data.terapeuticos),
            ("Quirúrgicos", data.quirurgicos),
            ("Familiares", data.familiares),
        ]

        start_y = y
        y_left = start_y
        y_right = start_y
        mid_x = self.MARGIN + col_w + 6

        for (lbl_l, val_l), (lbl_r, val_r) in zip(antec_left, antec_right):
            # Left
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            c.drawString(self.MARGIN + 3, y_left, lbl_l)
            y_left -= 11
            y_left = self._text_block(c, val_l or "(-)", self.MARGIN + 3, y_left, col_w)
            y_left -= 2

            # Right
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(mid_x + 3, y_right, lbl_r)
            y_right -= 11
            y_right = self._text_block(c, val_r or "(-)", mid_x + 3, y_right, col_w)
            y_right -= 2

        y = min(y_left, y_right) - 2

        # Paraclínicos (ancho completo)
        if data.paraclinicos and data.paraclinicos not in ('N/A', ''):
            c.setFont("Helvetica-Bold", 7.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            c.drawString(self.MARGIN + 3, y, "Paraclínicos")
            y -= 11
            y = self._text_block(c, data.paraclinicos, self.MARGIN + 3, y, self.CONTENT_W - 6)

        return y - 2

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: FAMILIAR / SOCIAL / FUNCIONAL
    # ──────────────────────────────────────────────────────────

    def _draw_section_funcional(self, c, data: ReportData, y: float) -> float:
        items = [
            ("Vive Con", data.vive_con),
            ("ABC (Actividades básicas)", data.abc),
            ("Escolar / Laboral", data.escolar_laboral),
            ("Patrón de Sueño", data.patron_sueno),
            ("Patrón de Alimentación", data.patron_alimentacion),
            ("Comportamiento / Ánimo", data.comportamiento_animo),
        ]
        # Only draw if there's content
        has_content = any(v and v not in ('N/A', '') for _, v in items)
        if not has_content:
            return y

        y -= 4
        y = _check = self._check_page(c, y, 80)
        y = self._section_title(c, "Familiar / Social / Funcional", y)

        for lbl, val in items:
            if val and val not in ('N/A', ''):
                y = self._check_page(c, y, 30)
                c.setFont("Helvetica-Bold", 7.5)
                c.setFillColorRGB(*GRIS_TEXTO)
                c.drawString(self.MARGIN + 3, y, lbl)
                y -= 11
                y = self._text_block(c, val, self.MARGIN + 3, y, self.CONTENT_W - 6)
                y -= 3

        return y

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: OBSERVACIÓN CLÍNICA
    # ──────────────────────────────────────────────────────────

    def _draw_section_observacion(self, c, data: ReportData, y: float) -> float:
        obs_sections = [
            ("Observación Clínica General", data.obs_clinica_general),
            ("Atención", data.obs_atencion),
            ("Memoria", data.obs_memoria),
            ("Praxias / Gnosias", data.obs_praxias_gnosias),
            ("Lenguaje", data.obs_lenguaje),
            ("Funciones Ejecutivas", data.obs_funciones_ejecutivas),
            ("Emociones / Comportamiento", data.obs_emociones),
            ("Cociente Intelectual", data.obs_ci),
            ("Funcionalidad", data.obs_funcionalidad),
        ]

        has_obs = any(v and v not in ('N/A','') for _, v in obs_sections)
        if not has_obs:
            return y

        y -= 4
        y = self._check_page(c, y, 80)
        y = self._section_title(c, "Observación Clínica", y)

        # Two column layout for observations
        col_w = self.CONTENT_W / 2 - 4
        mid_x = self.MARGIN + col_w + 6

        left_obs  = obs_sections[:5]
        right_obs = obs_sections[5:]

        # Render interleaved so columns stay balanced
        i_l, i_r = 0, 0
        while i_l < len(left_obs) or i_r < len(right_obs):
            y = self._check_page(c, y, 40)
            start_block = y

            # left item
            if i_l < len(left_obs):
                lbl, val = left_obs[i_l]
                if val and val not in ('N/A',''):
                    c.setFont("Helvetica-Bold", 7.5)
                    c.setFillColorRGB(*GRIS_TEXTO)
                    c.drawString(self.MARGIN + 3, start_block, lbl)
                    y_l = self._text_block(c, val, self.MARGIN + 3, start_block - 11, col_w)
                else:
                    y_l = start_block
                i_l += 1
            else:
                y_l = start_block

            # right item
            if i_r < len(right_obs):
                lbl, val = right_obs[i_r]
                if val and val not in ('N/A',''):
                    c.setFont("Helvetica-Bold", 7.5)
                    c.setFillColorRGB(*GRIS_TEXTO)
                    c.drawString(mid_x + 3, start_block, lbl)
                    y_r = self._text_block(c, val, mid_x + 3, start_block - 11, col_w)
                else:
                    y_r = start_block
                i_r += 1
            else:
                y_r = start_block

            y = min(y_l, y_r) - 6

        return y

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: RESULTADOS + GRÁFICA Z
    # ──────────────────────────────────────────────────────────

    def _draw_section_resultados(self, c, data: ReportData, y: float) -> float:
        y -= 4
        y = self._check_page(c, y, 200)

        # ── Título del protocolo ──
        y = self._section_title(c, f"Resultados — {data.protocolo or 'Evaluación'}", y)

        # ── Filtrar resultados con escalar (excluir CI/índices para la gráfica Z) ──
        resultados = data.resultados
        # Separar escalares de índices CI
        escalares = [r for r in resultados if r.get('puntaje_escalar') is not None
                     and r.get('tipo_metrica') not in ('ci',)
                     and r.get('z_equivalente') is not None]
        indices_ci = [r for r in resultados if r.get('tipo_metrica') == 'ci'
                      and r.get('puntaje_escalar') is not None]

        # ── CI boxes si existen ──
        if indices_ci:
            y = self._draw_ci_boxes(c, indices_ci, y)
            y -= 4

        # ── Gráfica Z (pagina internamente si >25 pruebas) ──
        if escalares:
            y = self._draw_z_chart(c, escalares, y)
            y -= 6

        # ── Tabla de puntajes ──
        if resultados:
            y = self._check_page(c, y, 60)
            y = self._draw_score_table(c, resultados, y)

        return y

    def _draw_ci_boxes(self, c, indices: list, y: float) -> float:
        """Dibuja cajas de CI en una fila horizontal."""
        n = len(indices)
        if n == 0:
            return y
        box_w = min(100, (self.CONTENT_W - (n - 1) * 6) / n)
        x_start = self.MARGIN + (self.CONTENT_W - (box_w * n + (n - 1) * 6)) / 2

        for i, r in enumerate(indices):
            bx = x_start + i * (box_w + 6)
            val = r.get('puntaje_escalar', 0) or 0
            interp = r.get('interpretacion', '')
            color = _nivel_color(r.get('z_equivalente'))

            # Box border
            c.setStrokeColorRGB(*color)
            c.setFillColorRGB(0.97, 0.97, 0.97)
            c.roundRect(bx, y - 44, box_w, 44, 4, fill=1, stroke=1)

            # Value
            c.setFillColorRGB(*color)
            c.setFont("Helvetica-Bold", 22)
            val_str = str(int(val)) if val else "—"
            c.drawCentredString(bx + box_w / 2, y - 28, val_str)

            # Name (small) — siempre vía human_test_name para que no se cuele
            # un identificador técnico tipo "NiWiscDC" en la cajita del KPI.
            from .report_pro.helpers import human_test_name
            nombre = human_test_name(
                r.get('test_id', '') or '',
                r.get('test_nombre', '') or '',
            )
            nombre = nombre.replace('Ind ', '').replace('NiWISC', '').strip()[:14]
            c.setFont("Helvetica", 6.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            c.drawCentredString(bx + box_w / 2, y - 38, nombre)

            # Label
            c.setFont("Helvetica-Bold", 6)
            c.setFillColorRGB(*color)
            c.drawCentredString(bx + box_w / 2, y - 9, _nivel_label(interp))

        return y - 50

    def _draw_z_chart(self, c, resultados: list, y: float) -> float:
        """Gráfica Z horizontal — réplica exacta del informe de referencia.
        Pagina automáticamente cuando hay >25 pruebas."""
        # Eje: -3 a +3 sigmas
        Z_MIN, Z_MAX = -3.0, 3.0
        z_range = Z_MAX - Z_MIN

        label_w   = 145   # ancho de la etiqueta izquierda
        val_w     = 30    # ancho del valor derecho
        track_w   = self.CONTENT_W - label_w - val_w - 6
        track_x   = self.MARGIN + label_w + 3
        row_h     = 14
        bar_h     = 8

        def _draw_z_header(c, y):
            """Dibuja encabezado de ejes de la gráfica Z."""
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            c.drawString(self.MARGIN + 3, y, "Nombre Prueba")
            for z_val in [-3, -2, -1, 0, 1, 2, 3]:
                px = track_x + (z_val - Z_MIN) / z_range * track_w
                c.drawCentredString(px, y, str(z_val))
            c.drawString(track_x + track_w + 3, y, "Z")
            return y - 4

        y = _draw_z_header(c, y)

        # Zona de normalidad (área sombreada)
        norm_x = track_x + ((-1) - Z_MIN) / z_range * track_w
        norm_w = 2 / z_range * track_w

        for r in resultados:
            z = r.get('z_equivalente')
            if z is None:
                continue

            # ── Paginación: si no cabe la siguiente fila, saltar página ──
            if y - row_h < 60:
                c.showPage()
                y = self.PAGE_H - self.MARGIN
                y = _draw_z_header(c, y)

            from .report_pro.helpers import human_test_name
            nombre = human_test_name(
                r.get('test_id', '') or '',
                r.get('test_nombre', '') or '',
            )[:28]
            color = _nivel_color(z)

            # Fondo sutil de fila
            c.setFillColorRGB(0.98, 0.98, 0.98)
            c.rect(self.MARGIN, y - row_h + 2, self.CONTENT_W, row_h - 1, fill=1, stroke=0)

            # Zona normal (azul muy suave)
            c.setFillColorRGB(0.85, 0.92, 0.98)
            c.rect(norm_x, y - bar_h + 1, norm_w, bar_h, fill=1, stroke=0)

            # Línea central (Z=0)
            center_x = track_x + (0 - Z_MIN) / z_range * track_w
            c.setStrokeColorRGB(0.7, 0.7, 0.7)
            c.setLineWidth(0.5)
            c.line(center_x, y - row_h + 2, center_x, y + 2)

            # Barra de Z
            bar_pct = max(0.0, min(1.0, (z - Z_MIN) / z_range))
            bar_px  = track_x + bar_pct * track_w
            zero_px = track_x + ((0 - Z_MIN) / z_range) * track_w
            bx = min(bar_px, zero_px)
            bw = abs(bar_px - zero_px)
            if bw < 1:
                bw = 1
            c.setFillColorRGB(*color)
            c.rect(bx, y - bar_h + 1, bw, bar_h, fill=1, stroke=0)

            # Label nombre
            c.setFont("Helvetica", 6.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            c.drawString(self.MARGIN + 3, y - 5, nombre)

            # Valor Z
            z_str = f"{z:+.1f}" if z is not None else "—"
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColorRGB(*color)
            c.drawString(track_x + track_w + 3, y - 5, z_str)

            y -= row_h

        # Leyenda
        y -= 4
        c.setFont("Helvetica", 6)
        c.setFillColorRGB(*GRIS_TEXTO)
        leyenda = (
            "Rango Normal -1 a 1 (σ): área sombreada. "
            "Puntos débiles: Z < -1. "
            "Puntos fuertes: Z > 1."
        )
        c.drawString(self.MARGIN + 3, y, leyenda)
        return y - 10

    def _draw_score_table(self, c, resultados: list, y: float) -> float:
        """Tabla compacta de todos los puntajes."""
        # Headers
        cols = [
            (self.MARGIN + 3, 160, "Prueba"),
            (self.MARGIN + 165, 35, "PD"),
            (self.MARGIN + 202, 35, "Escalar"),
            (self.MARGIN + 239, 45, "Nivel"),
            (self.MARGIN + 286, self.CONTENT_W - 286, "Dominio"),
        ]
        row_h = 11

        c.setFillColorRGB(*AZUL_SECCION)
        c.rect(self.MARGIN, y - row_h, self.CONTENT_W, row_h, fill=1, stroke=0)
        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 6.5)
        for cx, cw, lbl in cols:
            c.drawString(cx, y - 8, lbl)
        y -= row_h

        for i, r in enumerate(resultados):
            y = self._check_page(c, y, 15)
            # Alternate row background
            if i % 2 == 0:
                c.setFillColorRGB(0.96, 0.96, 0.96)
                c.rect(self.MARGIN, y - row_h + 1, self.CONTENT_W, row_h - 1, fill=1, stroke=0)

            z = r.get('z_equivalente')
            color = _nivel_color(z)
            interp = r.get('interpretacion', '')

            c.setFont("Helvetica", 6.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            from .report_pro.helpers import human_test_name
            nombre = human_test_name(
                r.get('test_id', '') or '',
                r.get('test_nombre', '') or '',
            )[:34]
            c.drawString(self.MARGIN + 3, y - 7, nombre)

            pd = r.get('puntaje_bruto')
            c.drawString(self.MARGIN + 165, y - 7, str(int(pd)) if pd is not None else "—")

            esc = r.get('puntaje_escalar')
            c.setFont("Helvetica-Bold", 6.5)
            c.setFillColorRGB(*color)
            c.drawString(self.MARGIN + 202, y - 7, str(int(esc)) if esc is not None else "—")

            c.setFont("Helvetica", 6.5)
            c.drawString(self.MARGIN + 239, y - 7, _nivel_label(interp)[:12])

            c.setFillColorRGB(*GRIS_TEXTO)
            dom = str(r.get('dominio_cognitivo', ''))[:28]
            c.drawString(self.MARGIN + 286, y - 7, dom)

            y -= row_h

        return y - 4

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: IMPRESIÓN DIAGNÓSTICA
    # ──────────────────────────────────────────────────────────

    def _draw_section_impresion(self, c, data: ReportData, y: float) -> float:
        has_dx = data.obs_impresion_dx and data.obs_impresion_dx not in ('N/A', '')
        has_cie = data.codigo_cie10 and data.codigo_cie10.strip()
        if not has_dx and not has_cie:
            return y
        y -= 4
        y = self._check_page(c, y, 80)
        y = self._section_title(c, "I.Dx — Impresión Diagnóstica", y)
        # CIE-10 con descripción
        if has_cie:
            cie_label = "CIE-10:"
            cie_val = data.codigo_cie10.strip()
            if data.codigo_cie10_desc:
                cie_val += f"  —  {data.codigo_cie10_desc}"
            c.setFillColorRGB(*AZUL_SECCION)
            c.setFont("Helvetica-Bold", 7.5)
            c.drawString(self.MARGIN + 3, y, cie_label)
            c.setFont("Helvetica", 7.5)
            c.setFillColorRGB(*GRIS_TEXTO)
            c.drawString(self.MARGIN + 38, y, cie_val[:110])
            y -= 13
        if has_dx:
            y = self._text_block(c, data.obs_impresion_dx, self.MARGIN + 3, y, self.CONTENT_W - 6)
        return y - 4

    # ──────────────────────────────────────────────────────────
    # SECCIÓN: RECOMENDACIONES
    # ──────────────────────────────────────────────────────────

    def _draw_section_recomendaciones(self, c, data: ReportData, y: float) -> float:
        if not data.obs_recomendaciones or data.obs_recomendaciones in ('N/A', ''):
            return y
        y -= 4
        y = self._check_page(c, y, 80)
        y = self._section_title(c, "Recomendaciones", y)
        y = self._text_block(c, data.obs_recomendaciones, self.MARGIN + 3, y, self.CONTENT_W - 6)
        return y - 4

    # ──────────────────────────────────────────────────────────
    # FIRMA
    # ──────────────────────────────────────────────────────────

    def _draw_firma(self, c, data: ReportData, y: float) -> None:
        y -= 20
        y = self._check_page(c, y, 80)

        # Aviso legal (pequeño)
        y -= 4
        c.setFillColorRGB(0.4, 0.4, 0.4)
        c.setFont("Helvetica", 6)
        aviso_words = data.aviso_legal.split()
        line, lines = "", []
        for w in aviso_words:
            if len(line) + len(w) + 1 <= 110:
                line = line + " " + w if line else w
            else:
                lines.append(line)
                line = w
        if line:
            lines.append(line)
        for ln in lines:
            c.drawString(self.MARGIN + 3, y, ln)
            y -= 8

        y -= 8

        # Firma block
        firma_x = self.COL_RIGHT - 160
        c.setStrokeColorRGB(0.2, 0.2, 0.2)
        c.setLineWidth(0.8)
        c.line(firma_x, y, self.COL_RIGHT, y)

        # Imagen de firma si existe
        if data.firma_base64:
            try:
                from reportlab.lib.utils import ImageReader
                img_bytes = base64.b64decode(data.firma_base64)
                img = ImageReader(io.BytesIO(img_bytes))
                c.drawImage(img, firma_x + 20, y + 2, width=100, height=35,
                            preserveAspectRatio=True, mask='auto')
            except Exception as _e:
                logger.warning("Firma no se pudo decodificar para PDF: %s", _e)

        y -= 10
        c.setFillColorRGB(*NEGRO)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(firma_x + 80, y, data.profesional_nombre or "")
        y -= 11
        c.setFont("Helvetica", 7)
        c.drawCentredString(firma_x + 80, y, data.profesional_titulo or "")
        if data.profesional_registro:
            y -= 9
            c.drawCentredString(firma_x + 80, y, f"Reg. {data.profesional_registro}")

        # Institución
        c.setFillColorRGB(*AZUL_HEADER)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(self.MARGIN + 3, y - 20, data.institucion_nombre)
        c.setFont("Helvetica", 7)
        c.drawString(self.MARGIN + 3, y - 30, data.institucion_dir)

    # ──────────────────────────────────────────────────────────
    # FOOTER (número de página)
    # ──────────────────────────────────────────────────────────

    def _draw_footer(self, c, data) -> None:
        if c is None:
            return
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica", 6)
        if data:
            c.drawString(self.MARGIN, 20,
                f"{data.institucion_nombre}  ·  "
                f"Tel: {data.institucion_tel}  ·  "
                f"Informe Neuropsicológico — Confidencial")


# ─────────────────────────────────────────────────────────────
# Función de conveniencia para el use case
# ─────────────────────────────────────────────────────────────

def _lookup_cie10_desc(code: str) -> str:
    """Retorna la descripción del código CIE-10 desde el catálogo neuropsicológico."""
    if not code:
        return ""
    try:
        from app.domain.entities.configuration import CIE10_NEUROPSICOLOGIA
        code_upper = code.upper().strip()
        for item in CIE10_NEUROPSICOLOGIA:
            if item.get("codigo", "").upper() == code_upper:
                return item.get("descripcion", "")
    except Exception as _e:
        logger.debug("CIE-10 lookup falló para código '%s': %s", code, _e)
    return ""


def generate_report_pdf(report_data: ReportData, template: str = "estandar") -> bytes:
    """Punto de entrada público.

    Args:
        report_data: instancia poblada de ReportData.
        template:    identificador de plantilla. Valores soportados:
                     ``"estandar"`` (NeuroPDFGenerator histórico) y las
                     variantes Pro: ``"pro"``, ``"pediatrico"``,
                     ``"medicolegal"``, ``"junta_medica"``, ``"inconcluso"``.
                     Cualquier valor desconocido cae a ``"estandar"``.
    Returns:
        bytes con el PDF generado.
    """
    key = (template or "estandar").strip().lower()
    if key == "estandar":
        return NeuroPDFGenerator().generate(report_data)
    try:
        from app.infrastructure.report_pro import VARIANTES_DISPONIBLES, generate_pro_pdf
    except ImportError as e:
        logger.error("No se pudo importar report_pro: %s — usando 'estandar'.", e)
        return NeuroPDFGenerator().generate(report_data)
    if key not in VARIANTES_DISPONIBLES:
        logger.warning("Plantilla desconocida %r — usando 'pro'.", key)
        key = "pro"
    return generate_pro_pdf(report_data, template=key)


def build_report_data_from_db(
    patient,
    clinical_history,
    evaluation_record,
    institucion,
    profesional,
    observations: dict = None,
) -> ReportData:
    """
    Construye un ReportData a partir de los objetos del dominio.

    Args:
        patient:           PatientORM o entidad Paciente
        clinical_history:  ClinicalHistoryORM (puede ser None)
        evaluation_record: EvaluationRecord (puede ser None)
        institucion:       ConfiguracionInstitucion
        profesional:       Profesional (puede ser None)
        observations:      dict {dominio: texto} de la tabla observations (puede ser None)
                           Complementa campos vacíos en clinical_history.
    """
    def _get(obj, attr, default=""):
        val = getattr(obj, attr, default) or default
        return str(val) if val not in (None, "N/A") else ""

    # Helper que prioriza HC; si vacío, usa observations table como fallback
    obs = observations or {}

    def _obs_field(hc_val: str, dominio: str) -> str:
        """Retorna hc_val si no está vacío; si no, el texto del dominio en observations."""
        if hc_val and hc_val not in ('', 'N/A'):
            return hc_val
        return obs.get(dominio, "")

    hc = clinical_history
    ev = evaluation_record

    return ReportData(
        # Institución
        institucion_nombre=_get(institucion, 'nombre', 'Consultorio Neuropsicológico'),
        institucion_nit=_get(institucion, 'nit'),
        institucion_dir=_get(institucion, 'direccion'),
        institucion_tel=_get(institucion, 'telefono'),
        logo_base64=getattr(institucion, 'logo_base64', None),

        # Paciente
        nombre_completo=(
            f"{_get(patient,'primer_nombre')} "
            f"{_get(patient,'segundo_nombre')} "
            f"{_get(patient,'primer_apellido')} "
            f"{_get(patient,'segundo_apellido')}"
        ).strip(),
        numero_documento=_get(patient, 'numero_documento'),
        tipo_documento=_get(patient, 'tipo_documento', 'CC'),
        fecha_nacimiento=getattr(patient, 'fecha_nacimiento', None),
        fecha_atencion=getattr(patient, 'fecha_atencion', None),
        edad_display=getattr(ev, 'edad_display', None) or "",
        sexo="Masculino" if _get(patient, 'sexo') == 'H' else "Femenino",
        escolaridad=_get(patient, 'escolaridad'),
        lateralidad=_get(patient, 'lateralidad', 'Diestro'),
        ocupacion=_get(patient, 'ocupacion'),
        ciudad=_get(patient, 'ciudad'),
        acompanante=_get(patient, 'acompanante'),
        remite=_get(patient, 'remite'),
        orden_no=_get(patient, 'orden_medica_no'),
        eps=_get(patient, 'eps'),
        poblacion=getattr(ev, 'poblacion', '') or "",

        # Historia clínica
        motivo_consulta=_get(hc, 'motivo_consulta') if hc else "",
        patologicos_medicos=_get(hc, 'patologicos_medicos') if hc else "",
        sensoriales_motores=_get(hc, 'sensoriales_motores') if hc else "",
        psiquiatricos=_get(hc, 'psiquiatricos') if hc else "",
        farmacologicos=_get(hc, 'farmacologicos') if hc else "",
        traumaticos=_get(hc, 'traumaticos') if hc else "",
        quirurgicos=_get(hc, 'quirurgicos') if hc else "",
        toxicos=_get(hc, 'toxicos') if hc else "",
        alergicos=_get(hc, 'alergicos') if hc else "",
        terapeuticos=_get(hc, 'terapeuticos') if hc else "",
        paraclinicos=_get(hc, 'paraclinicos') if hc else "",
        familiares=_get(hc, 'familiares') if hc else "",
        vive_con=_get(hc, 'vive_con') if hc else "",
        abc=_get(hc, 'abc') if hc else "",
        escolar_laboral=_get(hc, 'escolar_laboral') if hc else "",
        patron_sueno=_get(hc, 'patron_sueno') if hc else "",
        patron_alimentacion=_get(hc, 'patron_alimentacion') if hc else "",
        comportamiento_animo=_get(hc, 'comportamiento_animo') if hc else "",

        # Observaciones clínicas — prioriza HC; usa tabla observations como fallback
        obs_clinica_general=_obs_field(_get(hc, 'obs_clinica_general') if hc else "", "apariencia_conducta"),
        obs_atencion=_obs_field(_get(hc, 'obs_atencion') if hc else "", "atencion_concentracion"),
        obs_memoria=_obs_field(_get(hc, 'obs_memoria') if hc else "", "memoria"),
        obs_praxias_gnosias=_obs_field(_get(hc, 'obs_praxias_gnosias') if hc else "", "habilidades_visoespaciales"),
        obs_lenguaje=_obs_field(_get(hc, 'obs_lenguaje') if hc else "", "lenguaje"),
        obs_funciones_ejecutivas=_obs_field(_get(hc, 'obs_funciones_ejecutivas') if hc else "", "funciones_ejecutivas"),
        obs_emociones=_obs_field(_get(hc, 'obs_emociones') if hc else "", "socio_emocional"),
        obs_ci=_get(hc, 'obs_ci') if hc else "",
        obs_impresion_dx=_obs_field(_get(hc, 'obs_impresion_dx') if hc else "", "impresion_diagnostica"),
        obs_funcionalidad=_get(hc, 'obs_funcionalidad') if hc else "",
        obs_recomendaciones=_obs_field(_get(hc, 'obs_recomendaciones') if hc else "", "recomendaciones"),

        # CIE-10
        codigo_cie10=_get(hc, 'codigo_cie10') if hc else "",
        codigo_cie10_desc=_lookup_cie10_desc(_get(hc, 'codigo_cie10') if hc else ""),

        # Resultados — el ORM guarda JSON en `resultados_json` (no hay attr `resultados`).
        # Hay que deserializarlo; si no, la sección de resultados del PDF queda vacía.
        resultados=json.loads(getattr(ev, 'resultados_json', '[]') or '[]') if ev else [],
        puntos_debiles=json.loads(getattr(ev, 'puntos_debiles_json', '[]') or '[]') if ev else [],
        puntos_fuertes=json.loads(getattr(ev, 'puntos_fuertes_json', '[]') or '[]') if ev else [],
        advertencias=json.loads(getattr(ev, 'advertencias_json', '[]') or '[]') if ev else [],
        pruebas_realizadas=getattr(ev, 'pruebas_realizadas', 0) or 0,
        protocolo=getattr(ev, 'protocolo', '') or "",

        # Profesional
        profesional_nombre=_get(profesional, 'nombre_completo') if profesional else "",
        profesional_titulo=(
            f"{_get(profesional,'titulo')} {_get(profesional,'especialidad')}"
        ).strip() if profesional else "",
        profesional_registro=_get(profesional, 'numero_registro') if profesional else "",
        firma_base64=getattr(profesional, 'firma_base64', None) if profesional else None,

        # Identificador de evaluación (usado por la variante Pro en footer/portada)
        eval_id=_get(ev, 'id') if ev else "",

        # Campos específicos de la variante "Inconcluso" — ausentes en el ORM
        # antiguo, por eso usamos getattr con default.
        informe_inconcluso_cat=str(getattr(ev, 'informe_inconcluso_cat', '') or '') if ev else "",
        informe_inconcluso_nota=str(getattr(ev, 'informe_inconcluso_nota', '') or '') if ev else "",
    )
