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
        textColor=NAVY, leading=24, spaceBefore=18, spaceAfter=8,
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
        textColor=NAVY, leading=16, alignment=TA_JUSTIFY, spaceAfter=8,
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
        bg = HexColor(self.color.hexval()[:-2] + "1A") if isinstance(self.color, HexColor) else self.color
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


class CredentialsBox(Flowable):
    """Caja destacada para mostrar las credenciales de Mayra."""
    def __init__(self, width=460):
        super().__init__()
        self.width = width
        self.height = 130

    def draw(self):
        c = self.canv
        # Fondo gradient simulado
        c.setFillColor(NAVY)
        c.roundRect(0, 0, self.width, self.height, 14, stroke=0, fill=1)
        # Borde acentos
        c.setFillColor(TEAL)
        c.roundRect(0, 0, 6, self.height, 3, stroke=0, fill=1)
        # Etiqueta superior
        c.setFillColor(TEAL_LIGHT)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(24, self.height - 22, "CREDENCIALES DE ACCESO · BETA TESTER")
        # Title
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(24, self.height - 42, "Mayra")
        # Username
        c.setFillColor(GRAY_MUTED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(24, self.height - 64, "USUARIO")
        c.setFillColor(colors.white)
        c.setFont("Courier-Bold", 14)
        c.drawString(24, self.height - 80, "mayra")
        # Password
        c.setFillColor(GRAY_MUTED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(180, self.height - 64, "CONTRASEÑA")
        c.setFillColor(TEAL_LIGHT)
        c.setFont("Courier-Bold", 14)
        c.drawString(180, self.height - 80, "MayraBeta2026!")
        # Rol
        c.setFillColor(GRAY_MUTED)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(380, self.height - 64, "ROL")
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(380, self.height - 80, "Profesional")
        # Footer warning
        c.setFillColor(AMBER)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(24, 18, "⚠  ESTAS CREDENCIALES SON ÚNICAMENTE PARA TI · NO LAS COMPARTAS")


class StepCard(Flowable):
    """Tarjeta de paso numerado con título e instrucciones."""
    def __init__(self, n, title, body, width=460):
        super().__init__()
        self.n = n
        self.title = title
        self.body = body
        self.width = width
        # Altura calculada dinámicamente según texto (estimación 11px/línea)
        words = self.body.split()
        lines_est, line_len = 1, 0
        for w in words:
            if line_len + len(w) + 1 > 76:
                lines_est += 1
                line_len = len(w)
            else:
                line_len += len(w) + 1
        self.height = 32 + lines_est * 13

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
        words = self.body.split()
        line, y = "", self.height - 34
        for w in words:
            if len(line) + len(w) + 1 > 76:
                c.drawString(42, y, line.strip())
                y -= 13
                line = w + " "
            else:
                line += w + " "
        if line.strip():
            c.drawString(42, y, line.strip())


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
        canvas.drawRightString(A4[0] - 2*cm, A4[1] - 1.4*cm, "MAYRA · CONFIDENCIAL")
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
    doc = BaseDocTemplate(
        out_path,
        pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="NeuroSoft — Manual del Beta Tester (Mayra)",
        author="Johan Salgado",
        subject="Manual de uso NeuroSoft para beta tester",
        creator="NeuroSoft App",
    )

    cover_frame = Frame(0, 0, A4[0], A4[1], leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0, id="cover")
    body_frame  = Frame(2*cm, 2*cm, A4[0] - 4*cm, A4[1] - 4*cm, id="body")

    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=header_footer_cover),
        PageTemplate(id="Body",  frames=[body_frame],  onPage=header_footer_body),
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

            # Subtítulo Mayra
            c.setFillColor(TEAL)
            c.setFont("Helvetica-Bold", 22)
            c.drawString(2*cm, H - 11.5*cm, "para Mayra")

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
            c.drawString(2.6*cm, box_y + 3.2*cm, "ACCESO RÁPIDO")
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(2.6*cm, box_y + 2.4*cm, "Tus credenciales personales")
            # Columnas user / pass
            c.setFillColor(GRAY_MUTED)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(2.6*cm, box_y + 1.6*cm, "USUARIO")
            c.drawString(8*cm, box_y + 1.6*cm, "CONTRASEÑA")
            c.drawString(14*cm, box_y + 1.6*cm, "ROL")
            c.setFillColor(colors.white)
            c.setFont("Courier-Bold", 13)
            c.drawString(2.6*cm, box_y + 0.7*cm, "mayra")
            c.setFillColor(TEAL_LIGHT)
            c.drawString(8*cm, box_y + 0.7*cm, "MayraBeta2026!")
            c.setFillColor(colors.white)
            c.setFont("Helvetica-Bold", 12)
            c.drawString(14*cm, box_y + 0.7*cm, "Profesional")

            # Pie de portada
            c.setFillColor(GRAY_MUTED)
            c.setFont("Helvetica", 8)
            c.drawString(2*cm, 2.5*cm, "Documento confidencial · Distribución exclusiva")
            c.setFont("Helvetica-Bold", 8)
            c.drawString(2*cm, 2*cm, "Johan Salgado")
            c.setFont("Helvetica", 8)
            c.drawString(2*cm, 1.6*cm, "jssalgadosa@unal.edu.co")
            c.drawRightString(W - 2*cm, 2*cm, "NeuroSoft App")
            c.drawRightString(W - 2*cm, 1.6*cm, "Mayo 2026")

    story.append(Cover())
    story.append(PageBreak())

    # ─── CAMBIO A PLANTILLA BODY ──────────────────────────────────
    from reportlab.platypus.doctemplate import NextPageTemplate
    story.append(NextPageTemplate("Body"))
    # NOTA: la portada usa Cover y a partir de aquí Body. Reportlab
    # ya está en la siguiente página después del PageBreak.

    # ─── BIENVENIDA ───────────────────────────────────────────────
    story.append(Spacer(1, 6))
    story.append(Paragraph("Bienvenida, Mayra", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "Gracias por aceptar probar <b>NeuroSoft App</b>, el sistema de evaluación "
        "neuropsicológica clínica diseñado para profesionales en Colombia. Tu "
        "experiencia como neuropsicóloga será el insumo más valioso para refinar "
        "el sistema antes de su lanzamiento público.",
        S["body_lead"]
    ))
    story.append(Paragraph(
        "Este manual te guiará desde la instalación hasta el primer informe completo, "
        "y te muestra cómo reportar bugs o sugerir mejoras. Si algo no es claro, "
        "escríbenos directamente a <font color='#0D9488'><b>jssalgadosa@unal.edu.co</b></font>.",
        S["body"]
    ))

    # Tabla de contenidos visual
    story.append(Spacer(1, 14))
    story.append(Paragraph("Contenido del manual", S["h2"]))
    toc_data = [
        ["1.", "Qué es NeuroSoft App",            "p. 3"],
        ["2.", "Tus credenciales de acceso",      "p. 3"],
        ["3.", "Instalación",                     "p. 4"],
        ["4.", "Primer arranque",                 "p. 4"],
        ["5.", "Flujo clínico paso a paso",       "p. 5"],
        ["6.", "Funcionalidades a probar",        "p. 7"],
        ["7.", "Cómo reportar bugs y sugerencias","p. 8"],
        ["8.", "Privacidad y datos de prueba",    "p. 8"],
        ["9.", "Atajos de teclado",               "p. 9"],
        ["10.", "Soporte y contacto",             "p. 9"],
    ]
    toc = Table(toc_data, colWidths=[1*cm, 12*cm, 2*cm])
    toc.setStyle(TableStyle([
        ("FONT", (0,0), (0,-1), "Helvetica-Bold", 10),
        ("FONT", (1,0), (1,-1), "Helvetica", 10),
        ("FONT", (2,0), (2,-1), "Helvetica-Bold", 9),
        ("TEXTCOLOR", (0,0), (0,-1), TEAL),
        ("TEXTCOLOR", (1,0), (1,-1), NAVY),
        ("TEXTCOLOR", (2,0), (2,-1), GRAY_MUTED),
        ("ALIGN", (2,0), (2,-1), "RIGHT"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ("TOPPADDING",    (0,0), (-1,-1), 6),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, GRAY_SOFT),
    ]))
    story.append(toc)
    story.append(PageBreak())

    # ─── SECCIÓN 1: Qué es NeuroSoft ──────────────────────────────
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
        "Asistente IA opcional para mejorar redacción de informes (Google Gemini, Anthropic Claude, OpenAI o Ollama local).",
    ]
    for f in feats:
        story.append(Paragraph("•  " + f, S["bullet"]))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Todo el procesamiento ocurre <b>en tu equipo</b>. Ningún dato clínico se envía "
        "a internet sin tu autorización explícita.",
        S["section_intro"]
    ))

    # ─── SECCIÓN 2: Credenciales ──────────────────────────────────
    story.append(Spacer(1, 12))
    story.append(Paragraph("2.  Tus credenciales de acceso", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "No tienes que crear cuenta. Cuando arranques la aplicación por primera vez, "
        "tu usuario beta tester ya estará configurado:",
        S["body"]
    ))
    story.append(Spacer(1, 6))
    story.append(CredentialsBox(width=460))
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
        story.append(StepCard(n, title, body, width=460))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ─── SECCIÓN 4: Primer arranque ───────────────────────────────
    story.append(Paragraph("4.  Primer arranque", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    story.append(Paragraph(
        "En la pantalla de inicio de sesión, escribe usuario <font face='Courier'><b>mayra</b></font> "
        "y contraseña <font face='Courier'><b>MayraBeta2026!</b></font>, luego clic en <b>Iniciar sesión</b>. "
        "¡Listo! Estás en el Dashboard principal de NeuroSoft.",
        S["body"]
    ))
    story.append(Spacer(1, 8))
    story.append(Paragraph("Lo primero que verás", S["h3"]))
    elements = [
        ("<b>Sidebar izquierdo</b>", "navegación principal agrupada en 4 secciones (Clínica, Evaluación, Rehabilitación, Herramientas)."),
        ("<b>Topbar superior</b>", "tu nombre y el contexto de la página actual."),
        ("<b>Dashboard</b>", "panel con KPIs vacíos al inicio (porque aún no hay pacientes), notificaciones y accesos rápidos."),
        ("<b>Botón flotante 🤖 (abajo-derecha)</b>", "Asistente IA — opcional, requiere configurar un proveedor."),
    ]
    bullet_table = Table(
        [[Paragraph(t, S["body"]), Paragraph(d, S["body"])] for t, d in elements],
        colWidths=[5*cm, 11*cm]
    )
    bullet_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(bullet_table)

    # ─── SECCIÓN 5: Flujo clínico paso a paso ─────────────────────
    story.append(Spacer(1, 14))
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
         "Sidebar → <b>Pacientes</b> → botón <b>+ Registrar paciente</b>. Llena nombre, apellidos, documento (puedes usar 00000000), fecha de nacimiento (afecta el protocolo sugerido), sexo, escolaridad y ocupación. Guardar."),
        ("2", "Documentar Historia Clínica",
         "Desde la lista, click en el nombre del paciente → pestaña <b>Historia Clínica</b>. Llena motivo de consulta, antecedentes e hipótesis diagnóstica. El selector de CIE-10 sugiere códigos según población. Botón <b>Consentimiento Informado</b> genera el PDF para firma."),
        ("3", "Aplicar evaluación",
         "Sidebar → <b>Evaluación → Aplicar</b>. Selecciona paciente. NeuroSoft sugiere protocolo automáticamente según edad. Aplica las pruebas: lee la instrucción, anota observaciones (panel derecho), ingresa el PD (puntaje directo), usa el cronómetro inline para pruebas con tiempo. Cuando termines, clic en <b>Finalizar</b>."),
        ("4", "Revisar resultados",
         "Se muestran automáticamente: puntajes escalares, Z y percentiles; índices compuestos (ICV, IRP, IMT, IVP, CIT) con interpretación; curva normativa Z animada; radar de dominios; alertas clínicas para rangos Bajo/Limítrofe; discrepancias entre índices con significancia."),
        ("5", "Redactar informe narrativo",
         "En la misma pantalla, 8 dominios para redactar: Apariencia, Atención, Memoria, Lenguaje, Funciones Ejecutivas, Visoespaciales, Impresión Diagnóstica y Recomendaciones. Botón <b>Auto-generar</b> crea borradores basados en los puntajes. Botón <b>Mejorar con IA</b> mejora redacción (requiere proveedor IA configurado)."),
        ("6", "Descargar informe",
         "Sidebar → <b>Informes</b>. Selecciona la evaluación. Botones <b>PDF · DOCX · XLSX</b>. El PDF incluye firma digital si la configuraste en Configuración."),
        ("7", "Comparativa Pre–Post (opcional)",
         "Si registras 2+ evaluaciones del mismo paciente: Sidebar → <b>Historial → Pre–Post</b>. Selecciona dos evaluaciones. Verás tabla de cambios, RCI (Reliable Change Index) por dominio, radar evolutivo y narrativa automática del cambio."),
    ]
    for n, title, body in flow_steps:
        story.append(StepCard(n, title, body, width=460))
        story.append(Spacer(1, 6))

    story.append(PageBreak())

    # ─── SECCIÓN 6: Funcionalidades a probar ──────────────────────
    story.append(Paragraph("6.  Funcionalidades a probar", S["h1"]))
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
        ["▲", "Asistente IA",                 "Probar conexión con Gemini gratuita."],
        ["▲", "Modo oscuro",                  "Activar desde el sidebar inferior."],
        ["▲", "Modo proyección",              "Útil para pantalla externa (ícono zoom)."],
        ["▲", "Rehabilitación cognitiva",     "Probar al menos 2 actividades (Stroop, N-back, etc.)."],
        ["○", "Cargas lentas",                "¿Alguna pantalla se demora notablemente?"],
        ["○", "Errores sin explicación",      "¿Mensajes técnicos que confunden?"],
        ["○", "Terminología clínica",         "¿Algún término te parece impreciso?"],
    ]
    func_table = Table(func_data, colWidths=[0.8*cm, 5*cm, 10*cm])
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
        ("TEXTCOLOR", (0,7), (0,10), AMBER),
        ("TEXTCOLOR", (0,11), (0,13), GRAY_MUTED),
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

    # ─── SECCIÓN 7: Reportar bugs ─────────────────────────────────
    story.append(Paragraph("7.  Cómo reportar bugs y sugerencias", S["h1"]))
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
        "Email: <font color='#0D9488'><b>jssalgadosa@unal.edu.co</b></font><br/>"
        "Asunto: <font face='Courier'>[NeuroSoft Beta] — &lt;título del bug&gt;</font>",
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
        colWidths=[16*cm]
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

    # ─── SECCIÓN 8: Privacidad ────────────────────────────────────
    story.append(Spacer(1, 14))
    story.append(Paragraph("8.  Privacidad y datos de prueba", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    privacy_box_data = [[
        Paragraph(
            "<b>Almacenamiento 100% local</b><br/>"
            "Todos los datos se guardan en <font face='Courier'>%APPDATA%/NeuroSoft/</font> en tu equipo. "
            "NeuroSoft no envía datos clínicos a servidores externos.",
            S["body"]
        ),
    ]]
    privacy_box = Table(privacy_box_data, colWidths=[16*cm])
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
        "Las funciones de IA en la nube (Gemini, Claude, OpenAI) son <b>opcionales</b>. Solo se activan si configuras una API key.",
        "Antes de enviar cualquier texto a IA, el sistema <b>sanitiza nombres, documentos y fechas</b> automáticamente.",
        "<b>Ley 1581 de 2012</b> (Colombia): los datos del paciente son datos sensibles. Para esta fase beta, te pedimos usar <b>exclusivamente datos ficticios o anonimizados</b>.",
        "Cuando termines la prueba, puedes <b>eliminar la carpeta</b> <font face='Courier'>%APPDATA%/NeuroSoft/</font> para borrar todo.",
    ]
    for p in privacy_items:
        story.append(Paragraph("•  " + p, S["bullet"]))

    story.append(PageBreak())

    # ─── SECCIÓN 9: Atajos de teclado ─────────────────────────────
    story.append(Paragraph("9.  Atajos de teclado", S["h1"]))
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
    sc_table = Table(sc_data, colWidths=[4*cm, 12*cm])
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

    # ─── SECCIÓN 10: Soporte ──────────────────────────────────────
    story.append(Spacer(1, 18))
    story.append(Paragraph("10.  Soporte y contacto", S["h1"]))
    story.append(HRFlowable(width="40%", thickness=2, color=TEAL, spaceAfter=10))
    contact_data = [
        ["Bugs y sugerencias",    "jssalgadosa@unal.edu.co"],
        ["Soporte técnico",        "jssalgadosa@unal.edu.co"],
        ["WhatsApp (urgencias)",  "Pídelo a Johan directamente"],
    ]
    contact_table = Table(contact_data, colWidths=[5*cm, 11*cm])
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
            "<font size=14 color='#0D9488'><b>Gracias, Mayra ❤</b></font><br/><br/>"
            "Tu feedback como profesional clínica activa es el insumo más valioso para "
            "que NeuroSoft realmente sirva al trabajo neuropsicológico colombiano. Cada "
            "bug que encuentres y cada sugerencia que hagas mejora el sistema para todos "
            "los colegas que lo usarán cuando salga al público.<br/><br/>"
            "<b>¡Adelante con la prueba!</b>",
            ParagraphStyle("thanks", fontName="Helvetica", fontSize=11,
                           textColor=NAVY, leading=16, alignment=TA_CENTER)
        )
    ]]
    thanks_box = Table(thanks_box_data, colWidths=[16*cm])
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
    out = sys.argv[1] if len(sys.argv) > 1 else "MANUAL_BETA_TESTER_MAYRA.pdf"
    build_manual(out)
