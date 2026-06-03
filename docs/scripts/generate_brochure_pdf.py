# -*- coding: utf-8 -*-
"""
Genera el dossier informativo de NeuroSoft App en PDF.
Documento de presentación profesional con identidad editorial:
NAVY protagonista, TEAL acento minoritario, tipografía mixta.

Para público mixto: el creador, colaboradores potenciales, comités,
profesionales que evalúan el producto.
"""
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, HRFlowable, KeepTogether,
)
from reportlab.platypus.flowables import Flowable
from reportlab.platypus.doctemplate import NextPageTemplate


# ═══ Paleta editorial NeuroSoft ════════════════════════════════════════
NAVY       = HexColor("#1E293B")
INK        = HexColor("#0F172A")
STONE      = HexColor("#475569")
ASH        = HexColor("#94A3B8")
CREAM      = HexColor("#FDFBF7")
PAPER      = HexColor("#FCFAF4")
TEAL       = HexColor("#0D9488")
TEAL_DARK  = HexColor("#0F766E")
TEAL_PALE  = HexColor("#CCFBF1")
PLUM       = HexColor("#6D28D9")
AMBER      = HexColor("#B45309")
FOREST     = HexColor("#15803D")
RUBY       = HexColor("#9F1239")
OCEAN      = HexColor("#0369A1")
SOFT_GRAY  = HexColor("#F1F5F9")
DIVIDER    = HexColor("#E2E8F0")


def make_styles():
    """Estilos editoriales mixed-serif/sans."""
    s = {}
    s["hero_eyebrow"] = ParagraphStyle(
        "hero_eyebrow", fontName="Helvetica-Bold", fontSize=9,
        textColor=TEAL, leading=12, alignment=TA_LEFT,
        spaceAfter=8,
    )
    s["hero_title"] = ParagraphStyle(
        "hero_title", fontName="Times-Bold", fontSize=44,
        textColor=NAVY, leading=50, alignment=TA_LEFT, spaceAfter=4,
    )
    s["hero_subtitle"] = ParagraphStyle(
        "hero_subtitle", fontName="Times-Italic", fontSize=18,
        textColor=TEAL, leading=24, alignment=TA_LEFT, spaceAfter=0,
    )
    s["eyebrow"] = ParagraphStyle(
        "eyebrow", fontName="Helvetica-Bold", fontSize=8,
        textColor=STONE, leading=11, alignment=TA_LEFT,
        spaceAfter=4,
    )
    s["eyebrow_teal"] = ParagraphStyle(
        "eyebrow_teal", fontName="Helvetica-Bold", fontSize=8,
        textColor=TEAL, leading=11, alignment=TA_LEFT, spaceAfter=4,
    )
    s["eyebrow_plum"] = ParagraphStyle(
        "eyebrow_plum", fontName="Helvetica-Bold", fontSize=8,
        textColor=PLUM, leading=11, alignment=TA_LEFT, spaceAfter=4,
    )
    s["h1"] = ParagraphStyle(
        "h1", fontName="Times-Bold", fontSize=24,
        textColor=NAVY, leading=30, alignment=TA_LEFT,
        spaceBefore=4, spaceAfter=8,
    )
    s["h2"] = ParagraphStyle(
        "h2", fontName="Times-Bold", fontSize=16,
        textColor=NAVY, leading=22, alignment=TA_LEFT,
        spaceBefore=14, spaceAfter=6,
    )
    s["h3"] = ParagraphStyle(
        "h3", fontName="Helvetica-Bold", fontSize=11,
        textColor=NAVY, leading=15, alignment=TA_LEFT,
        spaceBefore=10, spaceAfter=4,
    )
    s["lead"] = ParagraphStyle(
        "lead", fontName="Times-Roman", fontSize=13,
        textColor=INK, leading=20, alignment=TA_LEFT,
        spaceAfter=12,
    )
    s["body"] = ParagraphStyle(
        "body", fontName="Helvetica", fontSize=10,
        textColor=INK, leading=15, alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    s["body_muted"] = ParagraphStyle(
        "body_muted", fontName="Helvetica", fontSize=9.5,
        textColor=STONE, leading=14, alignment=TA_JUSTIFY,
        spaceAfter=8,
    )
    s["bullet"] = ParagraphStyle(
        "bullet", fontName="Helvetica", fontSize=10,
        textColor=INK, leading=15, alignment=TA_LEFT,
        leftIndent=14, bulletIndent=2,
        spaceAfter=4,
    )
    s["pullquote"] = ParagraphStyle(
        "pullquote", fontName="Times-Italic", fontSize=14,
        textColor=NAVY, leading=22, alignment=TA_LEFT,
        leftIndent=14, spaceBefore=10, spaceAfter=10,
    )
    s["small"] = ParagraphStyle(
        "small", fontName="Helvetica", fontSize=8.5,
        textColor=STONE, leading=12, alignment=TA_LEFT,
    )
    s["mono"] = ParagraphStyle(
        "mono", fontName="Courier", fontSize=9,
        textColor=NAVY, leading=13, alignment=TA_LEFT,
    )
    s["page_label"] = ParagraphStyle(
        "page_label", fontName="Helvetica-Bold", fontSize=7,
        textColor=ASH, leading=10, alignment=TA_LEFT,
    )
    s["footer_brand"] = ParagraphStyle(
        "footer_brand", fontName="Helvetica-Bold", fontSize=8,
        textColor=STONE, leading=11, alignment=TA_LEFT,
    )
    return s


# ═══ Flowables custom ══════════════════════════════════════════════════
class HeroCover(Flowable):
    """Portada editorial sobria. NAVY arriba, contenido en CREAM."""
    def __init__(self):
        super().__init__()
        self.width = A4[0]
        self.height = A4[1]

    def draw(self):
        c = self.canv
        W, H = A4

        # Fondo CREAM
        c.setFillColor(CREAM)
        c.rect(0, 0, W, H, stroke=0, fill=1)

        # Banda NAVY superior (3 cm)
        c.setFillColor(NAVY)
        c.rect(0, H - 3*cm, W, 3*cm, stroke=0, fill=1)
        # Acento TEAL bajo la banda
        c.setFillColor(TEAL)
        c.rect(0, H - 3*cm - 0.18*cm, W, 0.18*cm, stroke=0, fill=1)

        # Logo + brand en banda navy
        cx, cy, r = 2.5*cm, H - 1.5*cm, 0.55*cm
        c.setFillColor(TEAL)
        c.circle(cx, cy, r, stroke=0, fill=1)
        c.setStrokeColor(colors.white)
        c.setLineWidth(1.6)
        c.setLineCap(1)
        p = c.beginPath()
        p.moveTo(cx - r*0.45, cy - r*0.1)
        p.curveTo(cx - r*0.55, cy + r*0.25, cx - r*0.25, cy + r*0.5, cx, cy + r*0.45)
        p.curveTo(cx + r*0.25, cy + r*0.5, cx + r*0.55, cy + r*0.25, cx + r*0.45, cy - r*0.1)
        c.drawPath(p, stroke=1, fill=0)
        p2 = c.beginPath()
        p2.moveTo(cx, cy + r*0.45)
        p2.lineTo(cx, cy - r*0.3)
        c.drawPath(p2, stroke=1, fill=0)

        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 16)
        c.drawString(3.5*cm, H - 1.7*cm + 1, "Neuro")
        c.setFillColor(TEAL_PALE)
        c.setFont("Times-Italic", 17)
        c.drawString(3.5*cm + c.stringWidth("Neuro", "Helvetica-Bold", 16), H - 1.7*cm, "Soft")
        c.setFillColor(ASH)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(3.5*cm, H - 2.15*cm, "G E S T I Ó N    C L Í N I C A")

        # Etiqueta categoria (eyebrow) — derecha de la banda
        c.setFillColor(TEAL_PALE)
        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(W - 2.5*cm, H - 1.5*cm + 4, "D O S S I E R    I N F O R M A T I V O")
        c.setFillColor(ASH)
        c.setFont("Helvetica", 8)
        c.drawRightString(W - 2.5*cm, H - 2.0*cm, "Mayo 2026")

        # Bloque central — título
        c.setFillColor(TEAL)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2.5*cm, H - 7*cm, "QUÉ ES, CÓMO FUNCIONA, A DÓNDE VA")

        c.setFillColor(NAVY)
        c.setFont("Times-Bold", 60)
        c.drawString(2.5*cm, H - 10*cm, "NeuroSoft")
        c.setFillColor(TEAL)
        c.setFont("Times-BoldItalic", 60)
        c.drawString(2.5*cm + c.stringWidth("NeuroSoft", "Times-Bold", 60) + 6, H - 10*cm, "App")

        # Línea decorativa
        c.setStrokeColor(TEAL)
        c.setLineWidth(2)
        c.line(2.5*cm, H - 11*cm, 7*cm, H - 11*cm)

        # Subtítulo descriptivo
        c.setFillColor(STONE)
        c.setFont("Times-Italic", 16)
        c.drawString(2.5*cm, H - 12*cm, "Sistema clínico integral para profesionales de la")
        c.drawString(2.5*cm, H - 12.7*cm, "psicología y neuropsicología.")

        c.setFillColor(STONE)
        c.setFont("Helvetica", 11)
        c.drawString(2.5*cm, H - 14*cm, "Evaluación neuropsicológica. Psicoterapia. Aprendizaje continuo.")
        c.drawString(2.5*cm, H - 14.6*cm, "Diseñado en Colombia. Offline-first. Datos clínicos en tu equipo.")

        # Bloque de 3 pilares en grid
        y0 = 5.5*cm
        col_w = (W - 5*cm) / 3
        pilares = [
            ("01", "Evaluación", "Baremos colombianos · WISC-IV · WAIS-III · Neuronorma AM · 168 pruebas"),
            ("02", "Psicoterapia", "Notas SOAP · 23 enfoques · Riesgo suicida · Telepsicología"),
            ("03", "Aprender", "Biblioteca clínica · Spaced repetition · Casos · Glosario interactivo"),
        ]
        for i, (num, title, desc) in enumerate(pilares):
            x = 2.5*cm + i * col_w
            # Marca diagonal
            c.setStrokeColor(TEAL)
            c.setLineWidth(2)
            c.line(x, y0 + 1.6*cm, x + 0.7*cm, y0 + 1.6*cm)
            # Número
            c.setFillColor(ASH)
            c.setFont("Times-BoldItalic", 26)
            c.drawString(x, y0 + 0.4*cm, num)
            # Título
            c.setFillColor(NAVY)
            c.setFont("Helvetica-Bold", 13)
            c.drawString(x + 1.8*cm, y0 + 0.9*cm, title)
            # Descripción wrap
            c.setFillColor(STONE)
            c.setFont("Helvetica", 8)
            words = desc.split()
            line, ypos = "", y0 + 0.2*cm
            for w in words:
                test = (line + " " + w).strip()
                if c.stringWidth(test, "Helvetica", 8) > col_w - 2*cm:
                    c.drawString(x + 1.8*cm, ypos, line)
                    ypos -= 10
                    line = w
                else:
                    line = test
            if line: c.drawString(x + 1.8*cm, ypos, line)

        # Footer portada
        c.setStrokeColor(DIVIDER)
        c.setLineWidth(0.5)
        c.line(2.5*cm, 3*cm, W - 2.5*cm, 3*cm)

        c.setFillColor(STONE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(2.5*cm, 2.4*cm, "Johan Sebastián Salgado Sarmiento")
        c.setFillColor(ASH)
        c.setFont("Helvetica", 8)
        c.drawString(2.5*cm, 1.9*cm, "Psicólogo · Creador y propietario del software")
        c.drawString(2.5*cm, 1.5*cm, "jssalgadosa@unal.edu.co")

        # Versión / nota legal portada
        c.setFillColor(ASH)
        c.setFont("Helvetica", 7)
        c.drawRightString(W - 2.5*cm, 2.4*cm, "Documento confidencial")
        c.drawRightString(W - 2.5*cm, 1.9*cm, "Distribución bajo autorización del autor")
        c.drawRightString(W - 2.5*cm, 1.5*cm, "© 2026 · Todos los derechos reservados")


class PageDivider(Flowable):
    """Línea horizontal sutil de divisor de sección."""
    def __init__(self, color=DIVIDER, thickness=0.5, width=460, spacing=10):
        super().__init__()
        self.width = width
        self.height = thickness + spacing * 2
        self.color = color
        self.thickness = thickness
        self.spacing = spacing

    def draw(self):
        c = self.canv
        c.setStrokeColor(self.color)
        c.setLineWidth(self.thickness)
        c.line(0, self.spacing, self.width, self.spacing)


class StatBlock(Flowable):
    """Bloque de 3 estadísticas grandes para abrir sección."""
    def __init__(self, stats, width=460):
        super().__init__()
        self.stats = stats  # list of (numero, etiqueta)
        self.width = width
        self.height = 80

    def draw(self):
        c = self.canv
        cols = len(self.stats)
        col_w = self.width / cols
        for i, (num, lbl) in enumerate(self.stats):
            x = i * col_w
            # Línea decorativa
            c.setStrokeColor(TEAL)
            c.setLineWidth(2)
            c.line(x, self.height - 6, x + 0.6*cm, self.height - 6)
            # Número
            c.setFillColor(NAVY)
            c.setFont("Times-Bold", 36)
            c.drawString(x, self.height - 50, str(num))
            # Etiqueta
            c.setFillColor(STONE)
            c.setFont("Helvetica-Bold", 8)
            c.drawString(x, 10, lbl.upper())


class ModuleCard(Flowable):
    """Tarjeta editorial de módulo con color de marca."""
    def __init__(self, num, title, subtitle, body, accent=TEAL, width=460):
        super().__init__()
        self.num = num
        self.title = title
        self.subtitle = subtitle
        self.body = body
        self.accent = accent
        self.width = width
        # altura aproximada por longitud
        self.height = 110 + max(0, (len(body) // 90) * 14)

    def draw(self):
        c = self.canv
        # Borde izquierdo de marca
        c.setFillColor(self.accent)
        c.rect(0, 0, 4, self.height, stroke=0, fill=1)
        # Número grande gris
        c.setFillColor(ASH)
        c.setFont("Times-BoldItalic", 38)
        c.drawString(16, self.height - 42, self.num)
        # Etiqueta de categoría
        c.setFillColor(self.accent)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(70, self.height - 18, "M Ó D U L O".upper())
        # Título
        c.setFillColor(NAVY)
        c.setFont("Times-Bold", 18)
        c.drawString(70, self.height - 40, self.title)
        # Subtítulo
        c.setFillColor(STONE)
        c.setFont("Helvetica", 10)
        c.drawString(70, self.height - 56, self.subtitle)
        # Body wrap
        c.setFillColor(INK)
        c.setFont("Helvetica", 9.5)
        words = self.body.split()
        line, ypos = "", self.height - 78
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, "Helvetica", 9.5) > self.width - 80:
                c.drawString(70, ypos, line)
                ypos -= 13
                line = w
            else:
                line = test
        if line: c.drawString(70, ypos, line)


# ═══ Header & footer ═══════════════════════════════════════════════════
def header_footer_cover(canvas, doc):
    pass  # portada se dibuja sola

def header_footer_body(canvas, doc):
    canvas.saveState()
    W, H = A4
    # Banda NAVY sutil arriba
    canvas.setFillColor(NAVY)
    canvas.rect(0, H - 0.18*cm, W, 0.18*cm, stroke=0, fill=1)
    # Brand mini
    canvas.setFillColor(STONE)
    canvas.setFont("Helvetica-Bold", 7)
    canvas.drawString(2*cm, H - 1*cm, "NEUROSOFT  APP")
    canvas.setFillColor(ASH)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(2*cm + 2.6*cm, H - 1*cm, "·  Dossier informativo  ·  2026")
    # Número de página
    canvas.setFillColor(STONE)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawRightString(W - 2*cm, H - 1*cm, f"Pág. {doc.page - 1:02d}")
    # Footer
    canvas.setFillColor(DIVIDER)
    canvas.setLineWidth(0.4)
    canvas.line(2*cm, 1.5*cm, W - 2*cm, 1.5*cm)
    canvas.setFillColor(ASH)
    canvas.setFont("Helvetica", 7)
    canvas.drawString(2*cm, 1*cm, "© 2026 Johan Sebastián Salgado Sarmiento")
    canvas.drawRightString(W - 2*cm, 1*cm, "Distribución bajo autorización")
    canvas.restoreState()


# ═══ Construcción ══════════════════════════════════════════════════════
def build(out_path):
    doc = BaseDocTemplate(
        out_path, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="NeuroSoft App — Dossier informativo",
        author="Johan Sebastián Salgado Sarmiento",
        subject="Presentación del producto NeuroSoft App",
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

    # ── PORTADA ─────────────────────────────────────────────────────────
    story.append(HeroCover())
    story.append(PageBreak())
    story.append(NextPageTemplate("Body"))

    # ── RESUMEN EJECUTIVO ───────────────────────────────────────────────
    story.append(Paragraph("Resumen", S["hero_eyebrow"]))
    story.append(Paragraph("Qué es NeuroSoft App", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))
    story.append(Paragraph(
        "NeuroSoft App es un sistema clínico de escritorio para profesionales de "
        "la psicología y la neuropsicología. Integra en un solo lugar la "
        "<b>evaluación neuropsicológica completa</b> — con baremos colombianos y "
        "latinoamericanos — y la <b>psicoterapia recurrente</b> — sesiones SOAP, "
        "planes con objetivos SMART y seguimiento de riesgo suicida.",
        S["lead"]
    ))
    story.append(Paragraph(
        "El software se ejecuta <b>localmente en el equipo del profesional</b>. "
        "Los datos clínicos nunca salen del computador sin autorización explícita. "
        "Funciona sin conexión a internet y opcionalmente conecta con asistentes "
        "de IA (Google Gemini, Anthropic Claude, OpenAI o Ollama local) para "
        "mejorar la redacción de informes — sanitizando primero datos identificables.",
        S["body"]
    ))
    story.append(Paragraph(
        "Está pensado para psicólogos clínicos en consultorio privado y "
        "consultorios pequeños (1-5 profesionales) en Colombia, con especial "
        "cuidado en el cumplimiento de la Ley 1581 de 2012 (Habeas Data), la "
        "Resolución 1995 de 1999 (Historia Clínica) y los lineamientos del "
        "Colegio Colombiano de Psicólogos.",
        S["body"]
    ))

    story.append(Spacer(1, 10))
    story.append(PageDivider())

    # KPIs / cifras de proyecto
    story.append(Paragraph("Hoy, el sistema integra", S["eyebrow"]))
    story.append(Spacer(1, 4))
    story.append(StatBlock([
        ("168", "Pruebas neuropsicológicas"),
        ("23",  "Enfoques terapéuticos"),
        ("16",  "Actividades de rehabilitación"),
    ]))
    story.append(StatBlock([
        ("6",   "Variantes de informe PDF"),
        ("13+", "Escalas de tamizaje"),
        ("10",  "Skills clínicas automatizadas"),
    ]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Cifras a la fecha de cierre de este dossier (mayo 2026). El catálogo "
        "se expande continuamente con la skill <i>investigar-terapia</i> que "
        "integra literatura científica reciente.",
        S["small"]
    ))
    story.append(PageBreak())

    # ── LOS 3 PILARES ──────────────────────────────────────────────────
    story.append(Paragraph("Arquitectura del producto", S["hero_eyebrow"]))
    story.append(Paragraph("Tres pilares, una sola plataforma", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))
    story.append(Paragraph(
        "El producto se organiza en tres pilares funcionales que comparten la "
        "misma base de pacientes, profesionales, agenda y configuración. Esto "
        "evita silos de información y permite que la práctica clínica fluya "
        "naturalmente entre evaluación, intervención y formación continua.",
        S["body"]
    ))

    story.append(Spacer(1, 8))
    story.append(ModuleCard("01", "Evaluación neuropsicológica",
        "Cobertura WISC-IV, WAIS-III, Neuronorma Adulto Mayor y escalas de tamizaje.",
        "Aplicación guiada con cronómetro inline, sugerencia automática de "
        "protocolo según edad, captura de PD ítem por ítem, motor de baremos "
        "que calcula escalares, Z, percentiles e índices compuestos (ICV, IRP, "
        "IMT, IVP, CIT). Genera informes en seis variantes — profesional, "
        "pediátrico, medicolegal, junta médica, inconcluso, estándar — con "
        "gráficos clínicos serios (radar, curva gaussiana, discrepancias).",
        accent=TEAL))
    story.append(Spacer(1, 10))

    story.append(ModuleCard("02", "Psicoterapia",
        "Sesiones SOAP, planes terapéuticos, riesgo suicida, modalidad mixta.",
        "Notas SOAP estructuradas (Subjetivo, Objetivo, Análisis, Plan), planes "
        "terapéuticos con enfoque clínico (CBT, EMDR, DBT, ACT, sistémica, "
        "Gottman, EFT-pareja, Worden, PGT, etc.) y objetivos SMART medibles. "
        "Evaluación de riesgo suicida estandarizada con historial longitudinal. "
        "Firma irreversible con SHA-256. Soporte para telepsicología y consulta "
        "telefónica.",
        accent=PLUM))
    story.append(Spacer(1, 10))

    story.append(ModuleCard("03", "Aprender (próximamente)",
        "Biblioteca clínica searchable + spaced repetition + simulador de casos.",
        "Tercer pilar del roadmap. Convertirá los datos clínicos del sistema en "
        "material educativo: biblioteca de 168 pruebas con instrucciones, "
        "tarjetas Anki integradas con algoritmo FSRS, casos simulados con "
        "respuesta-experto, quizzes auto-evaluativos y glosario interactivo con "
        "tooltips embebidos. Dirigido a estudiantes de pregrado/posgrado y "
        "profesionales en formación continua.",
        accent=OCEAN))
    story.append(PageBreak())

    # ── COBERTURA CLÍNICA ──────────────────────────────────────────────
    story.append(Paragraph("Cobertura clínica", S["hero_eyebrow"]))
    story.append(Paragraph("Qué incluye el motor", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))

    story.append(Paragraph(
        "El motor clínico de NeuroSoft App combina 15 estrategias de cálculo "
        "psicométrico distintas (escalar por rango, z-score, suma a índice, "
        "T-score, percentil, clasificación fija, etc.) sobre una base de 168 "
        "pruebas con sus baremos oficiales. Las fuentes están documentadas "
        "internamente: edición colombiana de Wechsler, Neuronorma Colombia "
        "(Arango-Lasprilla &amp; Rivera 2017), ENI-2 (Matute, Rosselli, Ardila, "
        "Ostrosky), manuales originales de cada escala clínica.",
        S["body"]
    ))

    story.append(Paragraph("Baterías de inteligencia", S["h2"]))
    story.append(Paragraph("·  <b>WISC-IV</b> — 15 subpruebas. Índices ICV, IRP, IMT, IVP y CIT.", S["bullet"]))
    story.append(Paragraph("·  <b>WAIS-III</b> — 14 subpruebas. Índices ICV, IOP, IMT, IVP, CIE.", S["bullet"]))
    story.append(Paragraph("·  Discrepancia mayor entre índices con cálculo de ICG/ICC alternativos (Flanagan &amp; Kaufman 2009).", S["bullet"]))

    story.append(Paragraph("Baterías neuropsicológicas", S["h2"]))
    story.append(Paragraph("·  <b>ENI-2</b> — Evaluación Neuropsicológica Infantil (atención, memoria, lenguaje, lectura, escritura, matemáticas, función ejecutiva).", S["bullet"]))
    story.append(Paragraph("·  <b>Neuronorma Adulto Mayor</b> — 33+ pruebas adaptadas con ajustes por edad y escolaridad: TMT-A/B, Stroop, Fluidez (P, M, Animales), FCRO, Grober &amp; Buschke, MMSE, Yesavage, Lawton, Kertesz/FBI.", S["bullet"]))
    story.append(Paragraph("·  <b>Adulto Joven</b> — STAI, ASRS, BDI-II, CVLT, BNT, FCRO, TMT, SDMT, Stroop, Matrices.", S["bullet"]))
    story.append(Paragraph("·  <b>Validez de síntomas</b> — Rey 15-Item Test (Boone et al. 2002), con corte 9 ítems y reconocimiento.", S["bullet"]))

    story.append(Paragraph("Escalas de tamizaje", S["h2"]))
    escalas = [
        ("Estado de ánimo", "PHQ-9, BDI-II, GAD-7, BAI, HADS, Yesavage GDS-15"),
        ("Adicciones", "AUDIT, DAST-10"),
        ("Funcionalidad", "Barthel, Lawton, FAQ"),
        ("Infantil/Adolescente", "Vanderbilt (TDAH), M-CHAT-R/F (TEA), SCARED-5, SNAP-IV"),
        ("Cognición", "MMSE, MoCA, ACE-III, CDR-SoB"),
        ("Cuidador", "Zarit-7 (sobrecarga del cuidador)"),
        ("Conducta", "NPI-Q (neuropsiquiátrico)"),
    ]
    for grupo, lista in escalas:
        story.append(Paragraph(f"·  <b>{grupo}:</b> {lista}.", S["bullet"]))

    story.append(Paragraph("Enfoques terapéuticos (módulo psicoterapia)", S["h2"]))
    story.append(Paragraph(
        "El catálogo se construyó con base en literatura de eficacia (APA "
        "Div 12 Society of Clinical Psychology, NICE Guidelines, Cochrane "
        "Reviews). Cada enfoque incluye nivel de evidencia, indicaciones, "
        "contraindicaciones, duración típica, estructura por fases, técnicas "
        "clave, escalas de outcome y referencias fundacionales.",
        S["body"]
    ))

    enfoques = [
        ("Individual adulto", "CBT/TCC · ACT · DBT · MBCT · IPT · Esquemas · PDT breve · Logoterapia · PCT-Rogers · CFT (compasión)"),
        ("Trauma", "EMDR · TF-CBT · CPT"),
        ("Pareja", "Método Gottman · EFT-Couples (Sue Johnson) · CBCT"),
        ("Familia", "Sistémica Estructural (Minuchin) · FBT-Maudsley (TCA adolescente)"),
        ("Duelo", "Worden 4 tareas · Neimeyer (significado) · PGT (duelo prolongado)"),
        ("Adicciones", "Entrevista Motivacional (Miller-Rollnick) · Modelo Transteórico"),
        ("Niños / adolescentes", "PMT/Parental · TF-CBT · Incredible Years"),
    ]
    for cat, lista in enfoques:
        story.append(Paragraph(f"·  <b>{cat}:</b> {lista}.", S["bullet"]))

    story.append(PageBreak())

    # ── REHABILITACIÓN ─────────────────────────────────────────────────
    story.append(Paragraph("Rehabilitación cognitiva", S["hero_eyebrow"]))
    story.append(Paragraph("Actividades interactivas y telerehab", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))
    story.append(Paragraph(
        "El módulo de rehabilitación incluye 16 actividades cognitivas "
        "interactivas que se pueden aplicar en consulta o asignar como tarea "
        "domiciliaria mediante un link público anonimizado. El sistema notifica "
        "al profesional cuando el paciente completa una sesión y registra "
        "métricas objetivas (tiempo de reacción, aciertos, errores) para "
        "análisis longitudinal.",
        S["body"]
    ))
    actividades = [
        ("Atención", "CPT (Continuous Performance Test) · Go/No-Go INECO · Tachado · Stroop computarizado"),
        ("Memoria de trabajo", "N-back · Corsi (forward/backward) · Spaced Retrieval (Camp)"),
        ("Función ejecutiva", "Wisconsin-like (set-shifting) · Tower of London · Fluidez verbal"),
        ("Cognición social", "Reading the Mind in the Eyes · Reconocimiento Ekman (expresiones)"),
        ("Procesamiento", "Rotación mental · Denominación con claves"),
        ("Vida diaria (ecológicas)", "AVD-Dinero (manejo cotidiano de billetes y monedas)"),
    ]
    for cat, lista in actividades:
        story.append(Paragraph(f"·  <b>{cat}:</b> {lista}.", S["bullet"]))

    story.append(Spacer(1, 12))
    story.append(Paragraph(
        "Cada actividad puede configurarse en dificultad y frecuencia. Las "
        "métricas individuales se agregan en un dashboard de adherencia que "
        "muestra evolución por dominio cognitivo a lo largo de las semanas.",
        S["body_muted"]
    ))

    story.append(PageBreak())

    # ── INFORMES ────────────────────────────────────────────────────────
    story.append(Paragraph("Generación de informes", S["hero_eyebrow"]))
    story.append(Paragraph("Seis variantes profesionales", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))
    story.append(Paragraph(
        "Los resultados de cada evaluación se materializan en un informe PDF "
        "con identidad visual editorial. Cada variante adapta secciones, "
        "narrativa y gráficos al contexto clínico específico.",
        S["body"]
    ))

    variantes = [
        ("Profesional (recomendada)", "Adulto/escolar ambulatorio estándar. Portada dedicada, radar de dominios, curva gaussiana del perfil Z, tabla de discrepancias entre índices, narrativa integradora y firma."),
        ("Pediátrica", "Suma historia del desarrollo, observación de juego, escala de cooperación y lenguaje observacional infantil. Diseño con elementos visuales más cálidos."),
        ("Medicolegal", "Incluye validez de síntomas, discusión sobre aculturación y escolaridad, alcance del informe ante autoridades. Diseño formal con anexos."),
        ("Junta médica", "Versión ejecutiva de 2 páginas, sin portada ni antecedentes detallados, foco en conclusiones diagnósticas y recomendaciones."),
        ("Inconclusa", "Para casos donde la evaluación no pudo completarse (rechazo, fatiga, comorbilidad). Sello visual de 'INCONCLUSO' + razón categorizada + nota clínica."),
        ("Estándar (legacy)", "Plantilla histórica conservada por compatibilidad con flujos previos."),
    ]
    for nom, desc in variantes:
        story.append(Paragraph(f"<b>·  {nom}.</b> {desc}", S["bullet"]))

    story.append(Spacer(1, 8))
    story.append(Paragraph("Exportación adicional", S["h3"]))
    story.append(Paragraph(
        "Cada evaluación también se puede exportar a Word (DOCX) para edición "
        "manual posterior, y a Excel (XLSX) como matriz de puntajes para análisis "
        "comparativos o investigación.",
        S["body"]
    ))

    story.append(PageBreak())

    # ── ARQUITECTURA TÉCNICA ───────────────────────────────────────────
    story.append(Paragraph("Arquitectura", S["hero_eyebrow"]))
    story.append(Paragraph("Cómo está construido", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))

    story.append(Paragraph(
        "NeuroSoft App es una aplicación de escritorio para Windows construida "
        "con tecnologías modernas pero empaquetada como un único ejecutable "
        "que se instala mediante un asistente convencional (Inno Setup). Esto "
        "permite que profesionales sin formación técnica la usen como cualquier "
        "otra aplicación, sin tener que configurar servidores, bases de datos "
        "o navegadores especiales.",
        S["body"]
    ))

    arq = [
        ("Frontend", "React 18 + Vite + Tailwind CSS. Single Page App con navegación por estado. Tipografía mixta: Manrope (sans) para cuerpo y Lora (serif) para títulos editoriales."),
        ("Backend", "FastAPI + SQLAlchemy 2.0 + SQLite + Alembic. Clean Architecture (domain / application / infrastructure / presentation)."),
        ("Motor clínico", "Núcleo en domain/clinical_engine — 15 estrategias de cálculo psicométrico que operan sobre BD_NEURO_MAESTRA.json (168 pruebas, 112.643 claves de baremo)."),
        ("Empaquetado", "PyInstaller convierte backend Python + frontend compilado en NeuroSoft.exe (41 MB). Inno Setup genera el instalador NeuroSoft-Setup.exe (1.4 GB con Ollama incluido)."),
        ("IA opcional", "Conecta con Google Gemini, Anthropic Claude, OpenAI o Ollama local. El instalador trae OllamaSetup.exe bundleado: al primer arranque se instala silenciosamente para tener IA local sin requerir API keys."),
        ("Datos", "SQLite local en %APPDATA%/NeuroSoft/. Los datos nunca salen del equipo del profesional. Auto-guardado de evaluaciones e informes en localStorage cada 30 segundos."),
    ]
    for nom, desc in arq:
        story.append(Paragraph(f"<b>{nom}.</b> {desc}", S["bullet"]))

    story.append(Paragraph("Distribución y entrega", S["h2"]))
    story.append(Paragraph(
        "El usuario recibe un único archivo <font face='Courier'>NeuroSoft-Setup.exe</font> de aproximadamente "
        "1.4 GB que instala todo lo necesario en su equipo (binario principal, instalador de "
        "Ollama, manual del beta tester). La instalación dura 1-2 minutos. No "
        "requiere conexión a internet en uso normal — solo para activar el "
        "asistente de IA en la nube o descargar modelos locales adicionales.",
        S["body"]
    ))

    story.append(PageBreak())

    # ── PRIVACIDAD ─────────────────────────────────────────────────────
    story.append(Paragraph("Privacidad y normativa", S["hero_eyebrow"]))
    story.append(Paragraph("Cumplimiento clínico-legal en Colombia", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))

    story.append(Paragraph(
        "El proyecto fue diseñado desde el inicio con el marco normativo "
        "colombiano para datos clínicos sensibles como criterio de diseño, "
        "no como capa final.",
        S["lead"]
    ))

    normas = [
        ("Ley 1581 de 2012 (Habeas Data)",
         "Los datos del paciente son datos sensibles. El software permite ejercer los derechos ARCO "
         "(acceso, rectificación, cancelación, oposición) mediante exportación completa de la "
         "información del paciente a JSON descargable."),
        ("Resolución 1995 de 1999 (Historia Clínica)",
         "Estructura de historia clínica completa con todos los campos exigidos, audit log inmutable "
         "de cada modificación, optimistic locking para prevenir sobrescrituras concurrentes."),
        ("Ley 1090 de 2006 (Código Deontológico)",
         "El software es herramienta de apoyo, no reemplaza el juicio clínico. Cada informe lleva "
         "disclaimer profesional, identificación del profesional firmante y datos del registro."),
        ("Consentimiento informado",
         "Sistema completo de consentimientos firmados digitalmente (Habeas Data, evaluación, "
         "telepsicología) con trazabilidad de versión del texto aceptado y posibilidad de revocación."),
        ("Sanitización en IA externa",
         "Cuando el profesional usa asistencia de IA en la nube, el sistema sanitiza automáticamente "
         "nombres, documentos y fechas antes de enviar el texto. Lo recomendado es usar Ollama local "
         "(incluido en el instalador) para no enviar nada fuera del equipo."),
        ("Almacenamiento local",
         "100% de los datos clínicos viven en SQLite local en %APPDATA%/NeuroSoft/. No hay servidor "
         "central. No hay sincronización en la nube por defecto. Respaldos manuales bajo control "
         "del profesional."),
    ]
    for nom, desc in normas:
        story.append(Paragraph(f"<b>·  {nom}.</b> {desc}", S["bullet"]))

    story.append(PageBreak())

    # ── DIFERENCIADORES ────────────────────────────────────────────────
    story.append(Paragraph("Posicionamiento", S["hero_eyebrow"]))
    story.append(Paragraph("Qué diferencia a NeuroSoft", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))

    story.append(Paragraph(
        "El mercado global de software para psicología clínica está dominado "
        "por plataformas como SimplePractice, TheraNest, NovoPsych y Quenza. "
        "Todas son productos SaaS basados en la nube, optimizados para "
        "consultorios estadounidenses, sin baremos locales y con suscripciones "
        "mensuales en dólares.",
        S["body"]
    ))

    story.append(Paragraph("Diferenciadores de NeuroSoft", S["h2"]))
    diffs = [
        ("Baremos colombianos integrados", "Único sistema con motor de cálculo psicométrico que aplica directamente las normas Neuronorma-Colombia (Arango-Lasprilla &amp; Rivera) y la edición colombiana de WISC/WAIS, sin necesidad de conversiones manuales."),
        ("Offline-first y privacidad por diseño", "Los datos clínicos nunca salen del equipo. No hay servidor central que pueda ser comprometido ni proveedor cloud al que confiar información sensible de pacientes."),
        ("Licencia única, sin suscripción", "Modelo de adquisición tradicional. El profesional paga una vez (o recibe acceso beta) y posee el software en su equipo, sin riesgo de quedarse sin acceso por impago de suscripción."),
        ("Integración eval-terapia", "Único producto que combina evaluación neuropsicológica completa y psicoterapia recurrente en el mismo flujo, compartiendo paciente, historia clínica y agenda."),
        ("Catálogo terapéutico curado", "23 enfoques con evidencia clasificada (A-tradicional), referencias fundacionales, escalas de outcome recomendadas y disponibilidad en español. Crece con literatura científica reciente."),
        ("IA local incluida", "Trae instalador de Ollama empaquetado. Los profesionales pueden usar IA para mejorar redacción sin enviar nada a servidores externos ni pagar API keys."),
        ("Open architecture", "Extensible: agregar nuevas pruebas, escalas, actividades de rehab o enfoques terapéuticos sigue patrones documentados y no requiere modificar el núcleo."),
    ]
    for nom, desc in diffs:
        story.append(Paragraph(f"<b>·  {nom}.</b> {desc}", S["bullet"]))

    story.append(PageBreak())

    # ── ROADMAP ────────────────────────────────────────────────────────
    story.append(Paragraph("Hoja de ruta", S["hero_eyebrow"]))
    story.append(Paragraph("Qué viene en los próximos meses", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))

    story.append(Paragraph(
        "El roadmap se organiza en tres fases. La primera ya está en producción "
        "con usuarios reales en pruebas. La segunda llega a beta en los próximos "
        "meses. La tercera está en diseño conceptual.",
        S["body"]
    ))

    fases = [
        ("Fase actual — Evaluación", FOREST, "En producción",
         "Sistema completo de evaluación neuropsicológica con seis variantes de informe PDF, "
         "rehabilitación cognitiva con 16 actividades interactivas y telerehab, integración "
         "con asistentes de IA, y manual del beta tester. Pruebas controladas en curso con "
         "profesionales colombianos."),
        ("Fase 2 — Psicoterapia", AMBER, "Beta en 2026",
         "Módulo de sesiones terapéuticas con notas SOAP, planes con objetivos SMART, evaluación "
         "longitudinal de riesgo suicida (C-SSRS), telepsicología integrada, tareas terapéuticas "
         "domiciliarias e informes de cierre/derivación. Backend completo, frontend MVP en construcción."),
        ("Fase 3 — Aprender", OCEAN, "Diseño conceptual",
         "Módulo educativo con biblioteca clínica searchable, spaced repetition (algoritmo FSRS), "
         "simulador de casos clínicos con respuesta-experto, quizzes auto-evaluativos y glosario "
         "interactivo. Dirigido a estudiantes y profesionales en formación continua."),
    ]
    for nom, color, estado, desc in fases:
        # Bloque editorial por fase
        story.append(Paragraph(
            f'<font color="{color.hexval()}" face="Helvetica-Bold" size="8">·  {estado.upper()}</font>',
            S["small"]
        ))
        story.append(Paragraph(nom, S["h2"]))
        story.append(Paragraph(desc, S["body"]))
        story.append(Spacer(1, 6))

    story.append(Spacer(1, 10))
    story.append(Paragraph(
        '"NeuroSoft no busca competir con software internacional. Busca llenar '
        'un vacío real: dar a los profesionales colombianos de psicología y '
        'neuropsicología una herramienta diseñada con su realidad — sus baremos, '
        'su marco legal, su práctica clínica concreta — en lugar de adaptar '
        'soluciones pensadas para otro contexto."',
        S["pullquote"]
    ))

    story.append(PageBreak())

    # ── SOBRE EL AUTOR ────────────────────────────────────────────────
    story.append(Paragraph("Sobre el autor", S["hero_eyebrow"]))
    story.append(Paragraph("Johan Sebastián Salgado Sarmiento", S["h1"]))
    story.append(HRFlowable(width="35%", thickness=2, color=TEAL, spaceAfter=14))

    story.append(Paragraph(
        "NeuroSoft App es el proyecto de Johan Sebastián Salgado Sarmiento, "
        "psicólogo, único creador y propietario del software. El sistema fue "
        "diseñado desde la práctica clínica real, no como ejercicio académico "
        "ni producto comercial generalista. Cada feature responde a un "
        "problema concreto identificado en la consulta cotidiana.",
        S["body"]
    ))
    story.append(Paragraph(
        "El desarrollo es continuo y se apoya en literatura científica reciente, "
        "casos clínicos verificados como ground-truth para los cálculos "
        "psicométricos, y feedback estructurado de profesionales beta-testers "
        "que usan el sistema con sus propios pacientes (con datos ficticios "
        "durante esta fase).",
        S["body"]
    ))

    story.append(Spacer(1, 14))
    story.append(Paragraph("Contacto", S["h3"]))

    contact_data = [
        ["Correo profesional",   "jssalgadosa@unal.edu.co"],
        ["Estado del producto",  "Beta cerrada con profesionales seleccionados"],
        ["Modalidad de distribución",  "Instalador único bajo autorización del autor"],
        ["Soporte y feedback",   "Email directo al autor"],
    ]
    t = Table(contact_data, colWidths=[5.5*cm, 10*cm])
    t.setStyle(TableStyle([
        ("FONT", (0,0), (0,-1), "Helvetica-Bold", 9),
        ("FONT", (1,0), (1,-1), "Helvetica", 10),
        ("TEXTCOLOR", (0,0), (0,-1), STONE),
        ("TEXTCOLOR", (1,0), (1,-1), NAVY),
        ("TOPPADDING", (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LINEBELOW", (0,0), (-1,-1), 0.4, DIVIDER),
        ("VALIGN", (0,0), (-1,-1), "TOP"),
    ]))
    story.append(t)

    story.append(Spacer(1, 20))

    # Bloque de cierre — manifiesto
    story.append(Paragraph(
        '<font color="#0D9488" face="Helvetica-Bold" size="8">P R I N C I P I O S    D E L    P R O D U C T O</font>',
        S["small"]
    ))
    story.append(Spacer(1, 6))

    principios = [
        "Los datos clínicos del paciente nunca salen del equipo del profesional sin autorización explícita.",
        "Una falla silenciosa en el cálculo de un CI puede producir un diagnóstico incorrecto. La precisión psicométrica no se negocia.",
        "El software es herramienta de apoyo. Ningún resultado automatizado reemplaza el juicio profesional del psicólogo o neuropsicólogo.",
        "La normativa colombiana — Ley 1581, Resolución 1995, Ley 1090 — no es trámite final; es criterio de diseño.",
        "Cada feature responde a un problema concreto de la consulta. No hay funcionalidades decorativas.",
    ]
    for p in principios:
        story.append(Paragraph(
            f'<font face="Times-Italic" size="11" color="#0F172A">— {p}</font>',
            ParagraphStyle("p_principio", fontName="Times-Italic", fontSize=11,
                           textColor=INK, leading=18, alignment=TA_LEFT,
                           leftIndent=14, spaceAfter=8)
        ))

    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=DIVIDER))
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Este documento es propiedad intelectual de Johan Sebastián Salgado "
        "Sarmiento. Su distribución requiere autorización explícita del autor. "
        "El producto NeuroSoft App, así como su marca, código fuente, modelo de "
        "datos clínicos y arquitectura, están protegidos por derechos de autor.",
        S["small"]
    ))

    doc.build(story)
    print(f"PDF generado: {out_path}")


if __name__ == "__main__":
    import sys
    out = sys.argv[1] if len(sys.argv) > 1 else "NEUROSOFT_DOSSIER.pdf"
    build(out)
