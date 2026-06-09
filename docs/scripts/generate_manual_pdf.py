# -*- coding: utf-8 -*-
"""
Genera el manual del beta tester de NeuroSoft en PDF con diseño profesional.
Identidad visual: TEAL #0D9488, NAVY #1E293B, CREAM #FDFBF7, Manrope.
"""
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, ListFlowable, ListItem, KeepTogether, HRFlowable,
    Image, FrameBreak,
)
from reportlab.platypus.flowables import Flowable
from reportlab.pdfgen import canvas as canvas_module
from reportlab.graphics.shapes import Drawing, Path, Circle, Rect, String
from reportlab.graphics import renderPDF
import re


# ─── Paleta NeuroSoft ─────────────────────────────────────────────
TEAL       = HexColor("#0D9488")
TEAL_DARK  = HexColor("#0F766E")
TEAL_LIGHT = HexColor("#67E8F9")
NAVY       = HexColor("#1E293B")
CREAM      = HexColor("#FDFBF7")
GRAY_TXT   = HexColor("#475569")
GRAY_MUTED = HexColor("#94A3B8")
GRAY_SOFT  = HexColor("#F1F5F9")
RED_CLIN   = HexColor("#BA1A1A")
AMBER      = HexColor("#F59E0B")
GREEN_OK   = HexColor("#10B981")


# ─── Estilos de párrafo ───────────────────────────────────────────
def make_styles():
    styles = {}
    styles["title_hero"] = ParagraphStyle(
        "title_hero", fontName="Helvetica-Bold", fontSize=42,
        textColor=NAVY, leading=48, alignment=TA_LEFT, spaceAfter=0,
    )
    styles["subtitle_hero"] = ParagraphStyle(
        "subtitle_hero", fontName="Helvetica", fontSize=16,
        textColor=TEAL, leading=22, alignment=TA_LEFT, spaceAfter=0,
    )
    styles["caption_hero"] = ParagraphStyle(
        "caption_hero", fontName="Helvetica-Bold", fontSize=9,
        textColor=GRAY_MUTED, leading=12, alignment=TA_LEFT, spaceAfter=0,
    )
    styles["h1"] = ParagraphStyle(
        "h1", fontName="Helvetica-Bold", fontSize=20,
        textColor=NAVY, leading=24, spaceBefore=10, spaceAfter=6,
    )
    styles["h2"] = ParagraphStyle(
        "h2", fontName="Helvetica-Bold", fontSize=14,
        textColor=TEAL_DARK, leading=18, spaceBefore=12, spaceAfter=6,
    )
    styles["h3"] = ParagraphStyle(
        "h3", fontName="Helvetica-Bold", fontSize=11,
        textColor=NAVY, leading=14, spaceBefore=8, spaceAfter=4,
    )
    styles["body"] = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=10,
        textColor=GRAY_TXT, leading=14, alignment=TA_JUSTIFY, spaceAfter=6,
    )
    styles["body_lead"] = ParagraphStyle(
        "body_lead", fontName="Helvetica", fontSize=11,
        textColor=NAVY, leading=16, alignment=TA_LEFT, spaceAfter=8,
    )
    styles["bullet"] = ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=10,
        textColor=GRAY_TXT, leading=14, leftIndent=14, bulletIndent=4, spaceAfter=2,
    )
    styles["caption"] = ParagraphStyle(
        "caption", fontName="Helvetica", fontSize=8.5,
        textColor=GRAY_MUTED, leading=11, alignment=TA_LEFT,
    )
    styles["label"] = ParagraphStyle(
        "label", fontName="Helvetica-Bold", fontSize=8,
        textColor=GRAY_MUTED, leading=10, alignment=TA_LEFT,
    )
    styles["mono"] = ParagraphStyle(
        "mono", fontName="Courier-Bold", fontSize=12,
        textColor=NAVY, leading=16, alignment=TA_LEFT,
    )
    styles["section_intro"] = ParagraphStyle(
        "section_intro", fontName="Helvetica-Oblique", fontSize=10.5,
        textColor=GRAY_TXT, leading=15, alignment=TA_JUSTIFY, spaceAfter=10,
    )
    styles["footer_disclaimer"] = ParagraphStyle(
        "footer_disclaimer", fontName="Helvetica-Oblique", fontSize=8,
        textColor=GRAY_MUTED, leading=11, alignment=TA_CENTER,
    )
    styles["body_welcome"] = ParagraphStyle(
        "body_welcome", fontName="Helvetica", fontSize=10.5,
        textColor=GRAY_TXT, leading=15, alignment=TA_JUSTIFY, spaceAfter=0,
    )
    return styles


# ─── Logo cerebro NeuroSoft (SVG simplificado a Drawing) ──────────
class BrainLogo(Flowable):
    """Logo circular del cerebro NeuroSoft, ~size px de lado."""
    def __init__(self, size=80):
        super().__init__()
        self.size = size
        self.width = size
        self.height = size

    def draw(self):
        c = self.canv
        s = self.size
        # Círculo fondo con gradiente simulado (color sólido teal)
        c.setFillColor(TEAL)
        c.circle(s/2, s/2, s/2, stroke=0, fill=1)
        # Líneas que sugieren un cerebro estilizado (curvas en blanco)
        c.setStrokeColor(colors.white)
        c.setLineWidth(s*0.045)
        c.setLineCap(1)  # round
        # Hemisferio izquierdo
        p = c.beginPath()
        p.moveTo(s*0.30, s*0.42)
        p.curveTo(s*0.20, s*0.55, s*0.30, s*0.70, s*0.45, s*0.68)
        c.drawPath(p, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(s*0.30, s*0.42)
        p.curveTo(s*0.35, s*0.30, s*0.45, s*0.30, s*0.50, s*0.40)
        c.drawPath(p, stroke=1, fill=0)
        # Hemisferio derecho
        p = c.beginPath()
        p.moveTo(s*0.70, s*0.42)
        p.curveTo(s*0.80, s*0.55, s*0.70, s*0.70, s*0.55, s*0.68)
        c.drawPath(p, stroke=1, fill=0)
        p = c.beginPath()
        p.moveTo(s*0.70, s*0.42)
        p.curveTo(s*0.65, s*0.30, s*0.55, s*0.30, s*0.50, s*0.40)
        c.drawPath(p, stroke=1, fill=0)
        # Conexión central
        c.setFillColor(colors.white)
        c.circle(s*0.50, s*0.50, s*0.045, stroke=0, fill=1)


# ─── Cajas y banners decorativos ──────────────────────────────────
class InfoBox(Flowable):
    """Cuadro coloreado con icono y texto. Para credenciales, avisos, etc."""
    def __init__(self, title, body, color_hex=TEAL, width=460, icon="●"):
        super().__init__()
        self.title = title
        self.body = body
        self.color = color_hex
        self.width = width
        self.icon = icon
        # Calcular altura aprox por longitud del body
        self.height = 28 + max(20, len(body) // 60 * 13)

    def draw(self):
        c = self.canv
        # Fondo
        c.setFillColor(HexColor("#F8FAFC"))
        c.roundRect(0, 0, self.width, self.height, 8, stroke=0, fill=1)
        # Borde izquierdo grueso (acento)
        c.setFillColor(self.color)
        c.rect(0, 0, 5, self.height, stroke=0, fill=1)
        # Icono circular
        c.setFillColor(self.color)
        c.circle(28, self.height - 16, 10, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(28, self.height - 19, self.icon)
        # Title
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(48, self.height - 18, self.title)
        # Body (wrap a mano simple)
        c.setFillColor(GRAY_TXT)
        c.setFont("Helvetica", 9.5)
        words = self.body.split()
        line, y = "", self.height - 33
        max_chars = 70
        for w in words:
            if len(line) + len(w) + 1 > max_chars:
                c.drawString(48, y, line.strip())
                y -= 12
                line = w + " "
            else:
                line += w + " "
        if line.strip():
            c.drawString(48, y, line.strip())


class Divider(Flowable):
    """Línea divisora horizontal sutil."""
    def __init__(self, width=460, color=GRAY_SOFT, thickness=1):
        super().__init__()
        self.width = width
        self.height = thickness + 2
        self.color = color
        self.thickness = thickness

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        c.line(0, 1, self.width, 1)


class StepCard(Flowable):
    """Tarjeta de paso numerado con título e instrucciones."""

    @staticmethod
    def _estimate_lines(text: str, chars_per_line: int = 68) -> int:
        plain = re.sub(r"<[^>]+>", "", text)
        words = plain.split()
        lines, line_len = 1, 0
        for w in words:
            wlen = len(w) + 1
            if line_len + wlen > chars_per_line:
                lines += 1
                line_len = wlen
            else:
                line_len += wlen
        return max(1, lines)

    def __init__(self, n, title, body, width=460):
        super().__init__()
        self.n = n
        self.title = title
        self.body = body
        self.width = width
        lines_est = self._estimate_lines(body)
        self.height = 38 + lines_est * 14 + 6

    def draw(self):
        c = self.canv
        # Fondo
        c.setFillColor(HexColor("#F8FAFC"))
        c.roundRect(0, 0, self.width, self.height, 8, stroke=0, fill=1)
        # Bola con número
        c.setFillColor(TEAL)
        c.circle(20, self.height - 18, 12, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(20, self.height - 22, str(self.n))
        # Title
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(42, self.height - 20, self.title)
        # Body wrap
        c.setFillColor(GRAY_TXT)
        c.setFont("Helvetica", 9.5)
        words = re.sub(r"<[^>]+>", " ", self.body).split()
        line, y = "", self.height - 34
        for w in words:
            if len(line) + len(w) + 1 > 68:
                c.drawString(42, y, line.strip())
                y -= 14
                line = w + " "
            else:
                line += w + " "
        if line.strip() and y >= 6:
            c.drawString(42, y, line.strip())


class CredentialsBox(Flowable):
    """Caja genérica para credenciales entregadas por el administrador."""
    def __init__(self, width=460):
        super().__init__()
        self.width = width
        self.height = 108

    def draw(self):
        c = self.canv
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self.width, self.height, 14, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.roundRect(0, 0, 6, self.height, 3, stroke=0, fill=1)
        c.setFillColor(TEAL_LIGHT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(24, self.height - 22, "CREDENCIALES DE ACCESO · BETA TESTER")
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(24, self.height - 42, "Usuario y contraseña de tu clínica")
        c.setFillColor(GRAY_MUTED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(24, self.height - 62, "USUARIO")
        c.drawString(180, self.height - 62, "CONTRASEÑA")
        c.drawString(300, self.height - 62, "ROL")
        c.setFillColor(colors.white)
        c.setFont("Helvetica", 10)
        c.drawString(24, self.height - 78, "Del administrador")
        c.drawString(180, self.height - 78, "Personal / temporal")
        c.drawString(300, self.height - 78, "Profesional")
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(24, 14, "No compartas estas credenciales fuera de tu consultorio")


class WelcomePagePanel(Flowable):
    """Bienvenida a ancho completo del marco (wrap usa availWidth del frame)."""

    _INTRO_HTML = (
        "NeuroSoft App apoya tu trabajo de evaluación neuropsicológica en Colombia. "
        "En las siguientes páginas encontrarás cómo instalar el programa, activar la licencia "
        "y completar un caso de prueba hasta el informe en PDF.<br/><br/>"
        "Te guiamos paso a paso: desde la instalación hasta tu primer informe clínico.<br/><br/>"
        "<i>¿Dudas? Escríbele al administrador de tu clínica o al equipo NeuroSoft.</i>"
    )
    _STEPS = (
        ("1", "Instalar", "Ejecuta NeuroSoft-Setup.exe"),
        ("2", "Activar", "Ingresa tu clave de licencia"),
        ("3", "Registrar", "Crea un paciente de prueba"),
        ("4", "Informar", "Genera tu primer PDF"),
    )

    def __init__(self, styles):
        super().__init__()
        self.S = styles
        self.width = 0
        self.height = 0
        self._pad = 18
        self._intro = Paragraph(self._INTRO_HTML, styles["body_welcome"])

    def _intro_box_h(self):
        _, h = self._intro.wrap(self.width - 2 * self._pad, 10000)
        return h + 28

    def wrap(self, availWidth, availHeight):
        self.width = availWidth
        intro_h = self._intro_box_h()
        self.height = 30 + 16 + 18 + 14 + intro_h + 24 + 18 + 88 + 14 + 62
        return self.width, self.height

    @staticmethod
    def _draw_step_card(c, x, y, w, h, num, title, body):
        c.setFillColor(colors.white)
        c.roundRect(x, y, w, h, 8, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#CBD5E1"))
        c.setLineWidth(0.6)
        c.roundRect(x, y, w, h, 8, stroke=1, fill=0)
        cx = x + w / 2
        c.setFillColor(TEAL)
        c.circle(cx, y + h - 18, 12, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(cx, y + h - 22, num)
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 10.5)
        c.drawCentredString(cx, y + h - 38, title)
        c.setFillColor(GRAY_TXT)
        c.setFont("Helvetica", 8.5)
        max_w = w - 12
        words = body.split()
        line, lines = "", []
        for word in words:
            trial = (line + " " + word).strip()
            if c.stringWidth(trial, "Helvetica", 8.5) <= max_w:
                line = trial
            else:
                if line:
                    lines.append(line)
                line = word
        if line:
            lines.append(line)
        for i, ln in enumerate(lines[:3]):
            c.drawCentredString(cx, y + h - 52 - i * 11, ln)

    def draw(self):
        c = self.canv
        w, top = self.width, self.height
        cx = w / 2

        y = top - 26
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(cx, y, "Bienvenida, beta tester")

        y -= 14
        line_w = w * 0.44
        c.setStrokeColor(TEAL)
        c.setLineWidth(2)
        c.line((w - line_w) / 2, y, (w + line_w) / 2, y)

        y -= 20
        c.setFillColor(NAVY)
        c.setFont("Helvetica", 11)
        c.drawCentredString(cx, y, "Gracias por acompañarnos en esta fase de prueba.")

        intro_h = self._intro_box_h()
        y -= 14 + intro_h
        c.setFillColor(HexColor("#F0FDFA"))
        c.roundRect(0, y, w, intro_h, 10, stroke=0, fill=1)
        c.setStrokeColor(HexColor("#99F6E4"))
        c.setLineWidth(0.8)
        c.roundRect(0, y, w, intro_h, 10, stroke=1, fill=0)
        c.setFillColor(TEAL)
        c.roundRect(0, y, 4, intro_h, 2, stroke=0, fill=1)
        self._intro.drawOn(c, self._pad + 6, y + 14)

        y -= 24
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(cx, y, "Tu recorrido en cuatro pasos")

        card_h, gap = 84, 12
        y -= 10 + card_h
        card_w = (w - 3 * gap) / 4
        for i, step in enumerate(self._STEPS):
            self._draw_step_card(c, i * (card_w + gap), y, card_w, card_h, *step)

        y -= 14
        foot_h = 52
        y -= foot_h
        c.setFillColor(HexColor("#F8FAFC"))
        c.roundRect(0, y, w, foot_h, 8, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.rect(0, y, 5, foot_h, stroke=0, fill=1)
        c.setFillColor(TEAL)
        c.circle(28, y + foot_h - 18, 10, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(28, y + foot_h - 21, "!")
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(48, y + foot_h - 20, "Datos ficticios")
        c.setFillColor(GRAY_TXT)
        c.setFont("Helvetica", 9.5)
        c.drawString(
            48, y + 12,
            "Usa solo datos ficticios durante la prueba. Ley 1581 de 2012 — Protección de datos personales en Colombia.",
        )


# ─── Header & Footer de cada página (excepto portada) ─────────────
def header_footer(canvas, doc, is_cover=False):
    canvas.saveState()
    if not is_cover:
        # Header: barra fina TEAL arriba
        canvas.setFillColor(TEAL)
        canvas.rect(0, A4[1] - 8, A4[0], 8, stroke=0, fill=1)
        # Header text
        canvas.setFillColor(GRAY_MUTED)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawString(2*cm, A4[1] - 1.4*cm, "NEUROSOFT APP · MANUAL DEL BETA TESTER")
        canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.4*cm, "BETA TESTER · CONFIDENCIAL")
        # Footer: número de página + email
        canvas.setFillColor(GRAY_MUTED)
        canvas.setFont("Helvetica", 8)
        canvas.drawString(2*cm, 1.2*cm, "Soporte: jssalgadosa@unal.edu.co")
        canvas.drawRightString(A4[0] - 2*cm, 1.2*cm, f"Página {doc.page}")
        canvas.setStrokeColor(GRAY_SOFT)
        canvas.setLineWidth(0.5)
        canvas.line(2*cm, 1.5*cm, A4[0] - 2*cm, 1.5*cm)
    canvas.restoreState()


def header_footer_cover(canvas, doc):
    header_footer(canvas, doc, is_cover=True)


def header_footer_body(canvas, doc):
    header_footer(canvas, doc, is_cover=False)


# ─── Construcción del documento ───────────────────────────────────
def build_manual(out_path):
    # Ancho útil del cuerpo (evita desborde en tablas y cajas fijas a 460 pt)
    BODY_W = A4[0] - 4 * cm
    BOX_W = BODY_W - 12

    doc = BaseDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2.6*cm, bottomMargin=2.4*cm,
        title="NeuroSoft — Manual del Beta Tester",
        author="NeuroSoft",
        subject="Manual de uso NeuroSoft para beta testers",
        creator="NeuroSoft App",
    )

    full_frame = Frame(0, 0, A4[0], A4[1], leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="full")
    body_frame = Frame(2*cm, 2.4*cm, A4[0] - 4*cm, A4[1] - 5*cm, id="body")

    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[full_frame], onPage=header_footer_cover),
        PageTemplate(id="Body", frames=[body_frame], onPage=header_footer_body),
    ])

    S = make_styles()
    story = []

    # ─── PORTADA ───────────────────────────────────────────────────
    # Usaremos un canvas a mano vía un Flowable que pinte toda la portada.
    class Cover(Flowable):
        def __init__(self):
            super().__init__()
            self.width = A4[0]
            self.height = A4[1]

        def draw(self):
            c = self.canv
            W, H = A4[0], A4[1]
            # Fondo CREAM
            c.setFillColor(CREAM)
            c.rect(0, 0, W, H, stroke=0, fill=1)
            # Banda superior NAVY → TEAL
            c.setFillColor(NAVY)
            c.rect(0, H - 5*cm, W, 5*cm, stroke=0, fill=1)
            c.setFillColor(TEAL)
            c.rect(0, H - 5*cm - 0.3*cm, W, 0.3*cm, stroke=0, fill=1)
            # Logo cerebro arriba izquierda
            cx, cy, r = 3*cm, H - 2.5*cm, 1*cm
            c.setFillColor(TEAL)
            c.circle(cx, cy, r, stroke=0, fill=1)
            c.setStrokeColor(colors.white)
            c.setLineWidth(2)
            c.setLineCap(1)
            # cerebro estilizado
            p = c.beginPath()
            p.moveTo(cx - r*0.4, cy - r*0.1)
            p.curveTo(cx - r*0.6, cy + r*0.2, cx - r*0.3, cy + r*0.5, cx, cy + r*0.4)
            p.curveTo(cx + r*0.3, cy + r*0.5, cx + r*0.6, cy + r*0.2, cx + r*0.4, cy - r*0.1)
            c.drawPath(p, stroke=1, fill=0)
            p2 = c.beginPath()
            p2.moveTo(cx, cy + r*0.4)
            p2.lineTo(cx, cy - r*0.3)
            c.drawPath(p2, stroke=1, fill=0)
            # Brand
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 28)
            c.drawString(5*cm, H - 2.2*cm, "Neuro")
            c.setFillColor(TEAL_LIGHT)
            c.drawString(5*cm + c.stringWidth("Neuro", "Helvetica-Bold", 28), H - 2.2*cm, "Soft")
            c.setFillColor(GRAY_MUTED)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(5*cm, H - 3*cm, "G E S T I Ó N    C L Í N I C A    N E U R O P S I C O L Ó G I C A")

            # Sección central — título grande
            c.setFillColor(GRAY_MUTED)
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2*cm, H - 8*cm, "MANUAL")
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 48)
            c.drawString(2*cm, H - 10*cm, "Beta Tester")

            # Subtítulo
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(2*cm, H - 11.5*cm, "para profesionales clínicos")

            # Línea decorativa TEAL
            c.setStrokeColor(TEAL)
            c.setLineWidth(3)
            c.line(2*cm, H - 12.3*cm, 7*cm, H - 12.3*cm)

            # Descripción
            c.setFillColor(GRAY_TXT)
            c.setFont("Helvetica", 11)
            c.drawString(2*cm, H - 13.5*cm, "Guía completa de uso y testing")
            c.drawString(2*cm, H - 14*cm, "Sistema de evaluación neuropsicológica clínica")

            # Box de credenciales rápidas (parte inferior)
            box_y = 4*cm
            c.setFillColor(NAVY)
            c.roundRect(2*cm, box_y, W - 4*cm, 4*cm, 14, stroke=0, fill=1)
            c.setFillColor(TEAL)
            c.roundRect(2*cm, box_y, 0.25*cm, 4*cm, 3, stroke=0, fill=1)
            c.setFillColor(TEAL_LIGHT)
            c.setFont("Helvetica-Bold", 9)
            c.drawString(2.6*cm, box_y + 3.2*cm, "PRIMER ACCESO")
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(2.6*cm, box_y + 2.4*cm, "Credenciales de tu clínica")
            c.setFillColor(GRAY_MUTED)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(2.6*cm, box_y + 1.6*cm, "USUARIO")
            c.drawString(8*cm, box_y + 1.6*cm, "CONTRASEÑA")
            c.drawString(14*cm, box_y + 1.6*cm, "ROL")
            c.setFillColor(colors.white)
            c.setFont("Helvetica", 10)
            c.drawString(2.6*cm, box_y + 0.7*cm, "Del administrador")
            c.drawString(8*cm, box_y + 0.7*cm, "Personal / temporal")
            c.drawString(13.5*cm, box_y + 0.7*cm, "Profesional")

            # Pie de portada
            c.setFillColor(GRAY_MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(2*cm, 2.5*cm, "Documento confidencial · Distribución exclusiva")
            c.setFont("Helvetica-Bold", 8)
            c.drawString(2*cm, 2*cm, "NeuroSoft App")
            c.setFont("Helvetica", 8)
            c.drawString(2*cm, 1.6*cm, "Manual beta tester")
            c.drawRightString(W - 2*cm, 2*cm, "Junio 2026")

    story.append(Cover())
    story.append(PageBreak())

    # ─── BIENVENIDA (plantilla Body — evita solapamientos de canvas absoluto) ─
    from reportlab.platypus.doctemplate import NextPageTemplate

    story.append(NextPageTemplate("Body"))
    story.append(WelcomePagePanel(S))
    story.append(PageBreak())

    # ─── ÍNDICE ───────────────────────────────────────────────────
    story.append(Paragraph("Contenido del manual", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    toc_data = [
        ["1.", "Qué es NeuroSoft App",            "p. 4"],
        ["2.", "Tus credenciales de acceso",      "p. 5"],
        ["3.", "Instalación",                     "p. 6"],
        ["4.", "Primer arranque",                 "p. 7"],
        ["5.", "Flujo clínico paso a paso",       "p. 8"],
        ["6.", "Centro de Aprendizaje",          "p. 10"],
        ["7.", "Funcionalidades a probar",        "p. 11"],
        ["8.", "Cómo reportar bugs y sugerencias","p. 12"],
        ["9.", "Privacidad y datos de prueba",    "p. 13"],
        ["10.", "Atajos de teclado",               "p. 14"],
        ["11.", "Soporte y contacto",             "p. 14"],
    ]
    toc = Table(toc_data, colWidths=[BODY_W * 0.07, BODY_W * 0.78, BODY_W * 0.15])
    toc.setStyle(TableStyle([
        ("FONT", (0,0), (0,-1), "Helvetica-Bold", 10),
        ("FONT", (1,0), (1,-1), "Helvetica", 10),
        ("FONT", (2,0), (2,-1), "Helvetica-Bold", 9),
        ("TEXTCOLOR", (0,0), (0,-1), TEAL),
        ("TEXTCOLOR", (1,0), (1,-1), NAVY),
        ("TEXTCOLOR", (2,0), (2,-1), GRAY_MUTED),
        ("ALIGN", (2,0), (2,-1), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, GRAY_SOFT),
    ]))
    story.append(toc)
    story.append(PageBreak())

    # ─── SECCIÓN 1: Qué es NeuroSoft (página dedicada) ────────────
    story.append(Paragraph("1.  Qué es NeuroSoft App", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "NeuroSoft es una aplicación de escritorio para psicólogos clínicos y "
        "neuropsicólogos que permite gestionar todo el ciclo de evaluación clínica "
        "desde un solo lugar:",
        S["body"]
    ))
    feats = [
        "Registro de pacientes y gestión de historia clínica completa.",
        "Aplicación de baterías estandarizadas: WISC-IV, WAIS-III, Neuronorma Colombia (Adulto Mayor), MMSE, MoCA, BDI-II, GDS-15, BARTHEL, LAWTON y más.",
        "Cálculo automático de puntajes escalares, Z, percentiles e índices compuestos (ICV, IRP, IMT, IVP, CIT).",
        "Generación de informes profesionales en PDF, DOCX y XLSX.",
        "Comparativa longitudinal Pre–Post con Índice de Cambio Confiable (RCI · Jacobson & Truax, 1991).",
        "Planes de rehabilitación cognitiva con actividades interactivas (Stroop, N-back, Corsi, Tower of London, etc.).",
    ]
    for f in feats:
        story.append(Paragraph("•  " + f, S["bullet"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Todo el procesamiento ocurre <b>en tu equipo</b>. Ningún dato clínico se envía "
        "a internet sin tu autorización explícita.",
        S["section_intro"]
    ))
    story.append(PageBreak())

    # ─── SECCIÓN 2: Credenciales ──────────────────────────────────
    story.append(Paragraph("2.  Tus credenciales de acceso", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "No tienes que crear cuenta. Cuando arranques la aplicación por primera vez, "
        "tu usuario beta tester ya estará configurado:",
        S["body"]
    ))
    story.append(Spacer(1, 6))
    story.append(CredentialsBox(width=BOX_W))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "<b>Si crees que alguien más conoce tu contraseña</b>, cámbiala desde "
        "<i>Configuración → Cuenta → Cambiar contraseña</i>.",
        S["caption"]
    ))
    story.append(PageBreak())

    # ─── SECCIÓN 3: Instalación ───────────────────────────────────
    story.append(Paragraph("3.  Instalación", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph("Requisitos mínimos", S["h3"]))
    reqs = [
        "Windows 10 o superior (64 bits).",
        "4 GB de RAM (8 GB recomendado).",
        "2 GB de espacio en disco.",
        "No requiere conexión a internet para uso clínico.",
    ]
    for r in reqs:
        story.append(Paragraph("•  " + r, S["bullet"]))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Pasos de instalación", S["h3"]))
    inst = [
        ("1", "Descarga el instalador", "Te enviamos <b>NeuroSoft-Setup.exe</b> por Google Drive. Descárgalo a tu equipo."),
        ("2", "Ejecuta el instalador", "Doble-click en <b>NeuroSoft-Setup.exe</b>. Si Windows muestra «Windows protegió tu PC», haz clic en <b>Más información → Ejecutar de todas formas</b> (es seguro, el binario es nuestro)."),
        ("3", "Elige la carpeta de instalación", "El instalador te preguntará dónde guardar NeuroSoft. Por defecto sugiere <font face='Courier'>C:\\Program Files\\NeuroSoft</font>. Puedes cambiarla si prefieres."),
        ("4", "Acepta y termina", "Click en <b>Instalar</b>. En 1-2 minutos terminará. Se creará un acceso directo en tu escritorio y en el menú Inicio."),
        ("5", "Abre la aplicación", "Doble-click en el ícono <b>NeuroSoft</b> de tu escritorio. Se abrirá una ventana en tu navegador con la pantalla de inicio de sesión."),
    ]
    for n, title, body in inst:
        story.append(StepCard(n, title, body, width=BOX_W))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ─── SECCIÓN 4: Primer arranque ───────────────────────────────
    story.append(Paragraph("4.  Primer arranque", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "Tras instalar, el programa solicitará tu <b>clave de licencia</b> (formato "
        "<font face='Courier'>NSFT-XXXX-…</font>) enviada por el administrador. "
        "Luego verás el <b>acuerdo de uso</b> — se acepta <b>una sola vez por equipo</b> "
        "(Ley 1090/2006, 1581/2012, derechos de autor de pruebas). "
        "Inicia sesión con las credenciales que recibiste por separado.",
        S["body"]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Lo primero que verás", S["h3"]))
    elements = [
        ("<b>Menú lateral</b>", "acceso a Pacientes, Evaluación, Rehabilitación y otras herramientas."),
        ("<b>Barra superior</b>", "muestra tu nombre y en qué pantalla estás."),
        ("<b>Pantalla de inicio</b>", "resumen de pacientes, citas y accesos rápidos. Al principio puede verse vacío hasta que registres datos."),
        ("<b>Acuerdo de uso</b>", "ventana legal al primer arranque en cada equipo (solo una vez)."),
        ("<b>Configuración → Institución</b>", "nombre, logo y datos de tu consultorio en los informes PDF."),
    ]
    bullet_table = Table(
        [[Paragraph(t, S["body"]), Paragraph(d, S["body"])] for t, d in elements],
        colWidths=[BODY_W * 0.32, BODY_W * 0.68]
    )
    bullet_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(bullet_table)
    story.append(PageBreak())

    # ─── SECCIÓN 5: Flujo clínico paso a paso ─────────────────────
    story.append(Paragraph("5.  Flujo clínico paso a paso", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "<b>Recomendación:</b> Para una prueba realista, usa datos <b>ficticios</b> o de un "
        "caso clínico documentado en la literatura. No uses datos reales de pacientes "
        "durante esta fase beta (Ley 1581 de 2012).",
        S["section_intro"]
    ))

    flow_steps = [
        ("1", "Registrar un paciente de prueba",
         "Menú lateral → <b>Pacientes</b> → <b>+ Registrar paciente</b>. Completa nombre, apellidos, documento (puedes usar 00000000), fecha de nacimiento, sexo, escolaridad y ocupación. Guardar."),
        ("2", "Documentar Historia Clínica",
         "En la lista, abre el paciente → pestaña <b>Historia Clínica</b>. Motivo de consulta, antecedentes e hipótesis diagnóstica. El selector de CIE-10 sugiere códigos según edad. <b>Consentimiento Informado</b> genera el PDF para firma."),
        ("3", "Aplicar evaluación",
         "Menú lateral → <b>Evaluación → Aplicar</b>. Selecciona paciente. El programa sugiere el protocolo según la edad. Lee la instrucción, anota observaciones, ingresa el puntaje directo y usa el cronómetro si la prueba lo requiere. Al terminar, <b>Finalizar</b>."),
        ("4", "Revisar resultados",
         "Verás puntajes escalares, percentiles e índices (ICV, IRP, IMT, IVP, CIT), gráficas por dominio y alertas cuando un resultado queda bajo o límite."),
        ("5", "Redactar informe narrativo",
         "En la misma pantalla hay 8 apartados: Apariencia, Atención, Memoria, Lenguaje, Funciones Ejecutivas, Visoespaciales, Impresión Diagnóstica y Recomendaciones. <b>Auto-generar</b> crea un borrador a partir de los puntajes para que tú lo revises."),
        ("6", "Descargar informe",
         "Menú lateral → <b>Informes</b>. Elige la evaluación. Descarga en <b>PDF, DOCX o XLSX</b>. El PDF puede incluir tu firma si la configuraste."),
        ("7", "Comparativa Pre–Post (opcional)",
         "Con dos o más evaluaciones del mismo paciente: <b>Historial → Pre–Post</b>. Compara cambios por dominio y el índice de cambio confiable (RCI)."),
    ]
    for n, title, body in flow_steps:
        story.append(StepCard(n, title, body, width=BOX_W))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ─── SECCIÓN 6: Centro de Aprendizaje ─────────────────────────
    story.append(Paragraph("6.  Centro de Aprendizaje", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "Menú lateral → <b>Centro de aprendizaje</b>. Espacio de formación con glosario, "
        "tarjetas de repaso, cuestionarios, artículos, simulador de casos y protocolos paso a paso.",
        S["body_lead"]
    ))
    aprender_items = [
        ("Glosario", "120 términos con definición, ejemplo y fuente bibliográfica."),
        ("Tarjetas", "50 tarjetas con repaso espaciado — el progreso se guarda en tu equipo."),
        ("Cuestionarios", "6 cuestionarios (WISC, Neuronorma, ética, validez, WAIS, demencias)."),
        ("Artículos", "11 lecturas editoriales (MoCA, Neuronorma, informe NPS, validez, Res. 1995)."),
        ("Simulador", "11 casos clínicos sintéticos con interpretación experta."),
        ("Protocolos", "6 guías paso a paso (TDAH, demencia, CBT, crisis, WAIS, TEA)."),
        ("Rutas guiadas", "4 itinerarios de estudio (NPS sem 1, AM, ética, adulto joven)."),
        ("Pruebas", "Catálogo vivo de baremos disponibles en NeuroSoft."),
    ]
    for titulo, desc in aprender_items:
        story.append(Paragraph(f"<b>{titulo}:</b> {desc}", S["bullet"]))

    story.append(PageBreak())

    # ─── SECCIÓN 7: Funcionalidades a probar ──────────────────────
    story.append(Paragraph("7.  Funcionalidades a probar", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "Tu feedback es especialmente valioso en las siguientes áreas. Marca con un "
        "check mental lo que vayas probando.",
        S["body"]
    ))

    # Tabla de funcionalidades por prioridad
    func_data = [
        ["", "ÁREA / FUNCIONALIDAD", "QUÉ EVALUAR"],
        ["■", "Cálculo de puntajes",         "¿Los escalares y CI coinciden con tu lectura manual?"],
        ["■", "Sugerencia de protocolo",     "¿Sugiere el correcto según la edad?"],
        ["■", "Flujo de aplicación",         "¿La interfaz es intuitiva durante la sesión?"],
        ["■", "Generación de PDF",           "¿El informe se ve profesional? ¿faltan datos?"],
        ["■", "Auto-generador observaciones","¿Los borradores son útiles como punto de partida?"],
        ["■", "Pre–Post + RCI",              "¿La interpretación del cambio confiable es clara?"],
        ["▲", "Centro de Aprendizaje",        "Glosario, tarjetas, cuestionarios, simulador y protocolos."],
        ["▲", "Config institución + logo",     "Informes PDF con marca de tu consultorio."],
        ["▲", "Modo oscuro",                  "Activar desde el menú inferior izquierdo."],
        ["▲", "Modo proyección",              "Útil para pantalla externa (ícono zoom)."],
        ["▲", "Rehabilitación cognitiva",     "Probar al menos 2 actividades (Stroop, N-back, etc.)."],
        ["○", "Cargas lentas",                "¿Alguna pantalla se demora notablemente?"],
        ["○", "Errores sin explicación",      "¿Mensajes técnicos que confunden?"],
        ["○", "Terminología clínica",         "¿Algún término te parece impreciso?"],
    ]
    func_table = Table(func_data, colWidths=[BODY_W * 0.06, BODY_W * 0.32, BODY_W * 0.62])
    func_table.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 8),
        ("TEXTCOLOR", (0,0), (-1,0), GRAY_MUTED),
        ("BACKGROUND", (0,0), (-1,0), GRAY_SOFT),
        ("BOTTOMPADDING", (0,0), (-1,0), 6),
        ("TOPPADDING", (0,0), (-1,0), 6),
        # Cuerpo
        ("FONT", (0,1), (0,-1), "Helvetica-Bold", 12),
        ("FONT", (1,1), (1,-1), "Helvetica-Bold", 9),
        ("FONT", (2,1), (2,-1), "Helvetica", 9),
        ("TEXTCOLOR", (1,1), (1,-1), NAVY),
        ("TEXTCOLOR", (2,1), (2,-1), GRAY_TXT),
        ("ALIGN", (0,0), (0,-1), "CENTER"),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BOTTOMPADDING", (0,1), (-1,-1), 5),
        ("TOPPADDING", (0,1), (-1,-1), 5),
        ("LINEBELOW", (0,1), (-1,-1), 0.3, GRAY_SOFT),
        # Color de los iconos prioridad
        ("TEXTCOLOR", (0,1), (0,6), RED_CLIN),
        ("TEXTCOLOR", (0,7), (0,11), AMBER),
        ("TEXTCOLOR", (0,12), (0,14), GRAY_MUTED),
    ]))
    story.append(func_table)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "<font color='#BA1A1A'>■</font> Prioridad alta  ·  "
        "<font color='#F59E0B'>▲</font> Prioridad media  ·  "
        "<font color='#94A3B8'>○</font> Observaciones generales",
        S["caption"]
    ))

    story.append(PageBreak())

    # ─── SECCIÓN 8: Reportar bugs ─────────────────────────────────
    story.append(Paragraph("8.  Cómo reportar bugs y sugerencias", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph("Para cada hallazgo, por favor envíanos:", S["body"]))
    for b in [
        "Qué hiciste (pasos a reproducir, en orden).",
        "Qué esperabas que pasara.",
        "Qué pasó realmente.",
        "Captura de pantalla si aplica.",
        "Severidad: bloqueante / molesto / cosmético.",
    ]:
        story.append(Paragraph("•  " + b, S["bullet"]))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Canal preferido", S["h3"]))
    story.append(Paragraph(
        "Canal: contacto del administrador de tu clínica o titular NeuroSoft.<br/>"
        "Asunto sugerido: <font face='Courier'>[NeuroSoft Beta] — &lt;título del bug&gt;</font>",
        S["body"]
    ))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Plantilla rápida", S["h3"]))
    plantilla = (
        "TÍTULO: &lt;descripción breve&gt;<br/>"
        "SEVERIDAD: bloqueante / molesto / cosmético<br/>"
        "PASOS:<br/>"
        "&nbsp;&nbsp;1. ...<br/>"
        "&nbsp;&nbsp;2. ...<br/>"
        "&nbsp;&nbsp;3. ...<br/>"
        "ESPERABA: ...<br/>"
        "PASÓ: ...<br/>"
        "CAPTURA: &lt;adjunta imagen&gt;<br/>"
        "SO: Windows 10 / 11"
    )
    # Caja "código"
    code_table = Table(
        [[Paragraph(plantilla, ParagraphStyle("code", fontName="Courier", fontSize=8.5, textColor=NAVY, leading=12))]],
        colWidths=[BODY_W]
    )
    code_table.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), GRAY_SOFT),
        ("BOX", (0,0), (-1,-1), 0.5, TEAL),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(code_table)
    story.append(PageBreak())

    # ─── SECCIÓN 9: Privacidad ────────────────────────────────────
    story.append(Paragraph("9.  Privacidad y datos de prueba", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    privacy_box_data = [[
        Paragraph(
            "<b>Almacenamiento 100% local</b><br/>"
            "Todos los datos se guardan en <font face='Courier'>%APPDATA%/NeuroSoft/</font> en tu equipo. "
            "NeuroSoft no envía datos clínicos a servidores externos.",
            S["body"]
        ),
    ]]
    privacy_box = Table(privacy_box_data, colWidths=[BODY_W])
    privacy_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HexColor("#ECFDF5")),
        ("BOX", (0,0), (-1,-1), 1, GREEN_OK),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING", (0,0), (-1,-1), 12),
        ("RIGHTPADDING", (0,0), (-1,-1), 12),
    ]))
    story.append(privacy_box)
    story.append(Spacer(1, 8))
    privacy_items = [
        "<b>Ley 1581 de 2012</b> (Colombia): los datos del paciente son sensibles. En esta fase beta usa <b>solo datos ficticios o anonimizados</b>.",
        "Cuando termines la prueba, puedes <b>eliminar la carpeta</b> <font face='Courier'>%APPDATA%/NeuroSoft/</font> para borrar todo el contenido.",
    ]
    for p in privacy_items:
        story.append(Paragraph("•  " + p, S["bullet"]))

    story.append(PageBreak())

    # ─── SECCIÓN 10: Atajos de teclado ────────────────────────────
    story.append(Paragraph("10.  Atajos de teclado", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    sc_data = [
        ["ATAJO", "ACCIÓN"],
        ["Alt + P", "Ir a Pacientes"],
        ["Alt + E", "Ir a Evaluación"],
        ["Alt + R", "Ir a Rehabilitación"],
        ["Alt + H", "Alternar alto contraste"],
        ["Alt + D", "Alternar modo oscuro"],
        ["Alt + +", "Aumentar tamaño de fuente"],
        ["Alt + −", "Reducir tamaño de fuente"],
        ["Espacio", "Iniciar/Pausar cronómetro"],
    ]
    sc_table = Table(sc_data, colWidths=[BODY_W * 0.28, BODY_W * 0.72])
    sc_table.setStyle(TableStyle([
        ("FONT", (0,0), (-1,0), "Helvetica-Bold", 8),
        ("BACKGROUND", (0,0), (-1,0), NAVY),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("TOPPADDING", (0,0), (-1,0), 8),
        ("BOTTOMPADDING", (0,0), (-1,0), 8),
        ("FONT", (0,1), (0,-1), "Courier-Bold", 11),
        ("FONT", (1,1), (1,-1), "Helvetica", 10),
        ("TEXTCOLOR", (0,1), (0,-1), TEAL_DARK),
        ("TEXTCOLOR", (1,1), (1,-1), NAVY),
        ("ALIGN", (0,1), (0,-1), "CENTER"),
        ("BOTTOMPADDING", (0,1), (-1,-1), 8),
        ("TOPPADDING", (0,1), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, GRAY_SOFT]),
        ("LINEBELOW", (0,1), (-1,-1), 0.3, GRAY_SOFT),
    ]))
    story.append(sc_table)

    # ─── SECCIÓN 11: Soporte ──────────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(Paragraph("11.  Soporte y contacto", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    contact_data = [
        ["Bugs y sugerencias",    "Administrador de tu clínica / titular NeuroSoft"],
        ["Soporte técnico",        "Mismo canal de activación de licencia"],
        ["Documentación",          "Manual PDF incluido en el instalador"],
    ]
    contact_table = Table(contact_data, colWidths=[BODY_W * 0.32, BODY_W * 0.68])
    contact_table.setStyle(TableStyle([
        ("FONT", (0,0), (0,-1), "Helvetica-Bold", 10),
        ("FONT", (1,0), (1,-1), "Helvetica", 10),
        ("TEXTCOLOR", (0,0), (0,-1), NAVY),
        ("TEXTCOLOR", (1,0), (1,-1), TEAL_DARK),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, GRAY_SOFT),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
    ]))
    story.append(contact_table)

    # ─── CIERRE — Agradecimientos ─────────────────────────────────
    story.append(Spacer(1, 30))
    thanks_box_data = [[
        Paragraph(
            "<font size=14 color='#0D9488'><b>Gracias por ser beta tester</b></font><br/><br/>"
            "Tu feedback como profesional clínico es el insumo más valioso para "
            "refinar NeuroSoft antes del lanzamiento. Cada bug reportado y cada sugerencia "
            "mejora el sistema para toda la comunidad neuropsicológica colombiana.<br/><br/>"
            "<b>¡Adelante con la prueba!</b>",
            ParagraphStyle("thanks", fontName="Helvetica", fontSize=11,
                           textColor=NAVY, leading=16, alignment=TA_CENTER)
        )
    ]]
    thanks_box = Table(thanks_box_data, colWidths=[BODY_W])
    thanks_box.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CREAM),
        ("BOX", (0,0), (-1,-1), 1.5, TEAL),
        ("TOPPADDING", (0,0), (-1,-1), 18),
        ("BOTTOMPADDING", (0,0), (-1,-1), 18),
        ("LEFTPADDING", (0,0), (-1,-1), 16),
        ("RIGHTPADDING", (0,0), (-1,-1), 16),
    ]))
    story.append(thanks_box)

    # Disclaimer final
    story.append(Spacer(1, 16))
    story.append(Paragraph(
        "NeuroSoft App · Sistema de apoyo clínico — Los resultados deben interpretarse "
        "siempre en el contexto de la evaluación completa y el juicio profesional del "
        "neuropsicólogo. No sustituye la formación clínica.",
        S["footer_disclaimer"]
    ))

    doc.build(story)
    print(f"PDF generado: {out_path}")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    default = Path(__file__).resolve().parents[2] / "dist" / "MANUAL_BETA_TESTER.pdf"
    out = sys.argv[1] if len(sys.argv) > 1 else str(default)
    build_manual(out)
