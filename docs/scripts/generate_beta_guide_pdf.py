# -*- coding: utf-8 -*-
"""
Genera la Guía del Beta Tester de NeuroSoft App.

PDF profesional A4 con identidad visual editorial (paleta TEAL/NAVY,
tipografía mixta serif/sans). Enfocado a profesionales clínicos que
van a recibir el .exe Setup y necesitan saber:

  - Qué es NeuroSoft App
  - Qué puede hacer
  - Cómo instalarlo
  - Cómo testearlo
  - Cómo reportar feedback

Uso:
    python dist/generate_beta_guide_pdf.py
    → genera dist/GUIA_BETA_TESTER.pdf
"""
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, PageBreak,
    NextPageTemplate, Table, TableStyle, KeepTogether, HRFlowable,
)
from reportlab.pdfgen import canvas as canvas_module


# ─── Paleta NeuroSoft (editorial) ─────────────────────────────────
TEAL      = HexColor("#0D9488")
NAVY      = HexColor("#1E293B")
INK       = HexColor("#0F172A")
SLATE     = HexColor("#475569")
ASH       = HexColor("#94A3B8")
CREAM     = HexColor("#FDFBF7")
PAPER     = HexColor("#FCFAF4")
SOFT      = HexColor("#F1F5F9")
PLUM      = HexColor("#6D28D9")
AMBER     = HexColor("#B45309")
RUBY      = HexColor("#9F1239")
FOREST    = HexColor("#15803D")
OCEAN     = HexColor("#0369A1")
RULE      = HexColor("#E2E8F0")


# ─── Estilos ───────────────────────────────────────────────────────
def make_styles():
    return {
        "h1": ParagraphStyle(
            "h1", fontName="Helvetica-Bold", fontSize=24, textColor=NAVY,
            leading=30, spaceAfter=6,
        ),
        "h1_serif": ParagraphStyle(
            "h1_serif", fontName="Times-BoldItalic", fontSize=22, textColor=TEAL,
            leading=28, spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Helvetica-Bold", fontSize=15, textColor=NAVY,
            leading=20, spaceAfter=6, spaceBefore=14,
        ),
        "h3": ParagraphStyle(
            "h3", fontName="Helvetica-Bold", fontSize=11, textColor=NAVY,
            leading=15, spaceAfter=4, spaceBefore=8,
        ),
        "eyebrow": ParagraphStyle(
            "eyebrow", fontName="Helvetica-Bold", fontSize=8, textColor=TEAL,
            leading=12, spaceAfter=2, alignment=TA_LEFT,
        ),
        "lead": ParagraphStyle(
            "lead", fontName="Times-Italic", fontSize=12, textColor=SLATE,
            leading=18, spaceAfter=12, alignment=TA_JUSTIFY,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=10, textColor=INK,
            leading=15, spaceAfter=6, alignment=TA_JUSTIFY,
        ),
        "body_sm": ParagraphStyle(
            "body_sm", fontName="Helvetica", fontSize=9, textColor=SLATE,
            leading=13, spaceAfter=4, alignment=TA_JUSTIFY,
        ),
        "mono": ParagraphStyle(
            "mono", fontName="Courier-Bold", fontSize=9.5, textColor=NAVY,
            leading=14, spaceAfter=4,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=10, textColor=INK,
            leading=14, spaceAfter=3, leftIndent=14, bulletIndent=2,
        ),
        "footer": ParagraphStyle(
            "footer", fontName="Helvetica", fontSize=7, textColor=ASH,
            leading=10, alignment=TA_CENTER,
        ),
        "cover_brand": ParagraphStyle(
            "cover_brand", fontName="Helvetica-Bold", fontSize=10, textColor=TEAL,
            leading=14, alignment=TA_LEFT,
        ),
        "cover_title": ParagraphStyle(
            "cover_title", fontName="Helvetica-Bold", fontSize=44, textColor=NAVY,
            leading=50, alignment=TA_LEFT, spaceAfter=4,
        ),
        "cover_subtitle": ParagraphStyle(
            "cover_subtitle", fontName="Times-Italic", fontSize=20, textColor=TEAL,
            leading=26, alignment=TA_LEFT,
        ),
        "cover_meta": ParagraphStyle(
            "cover_meta", fontName="Helvetica-Bold", fontSize=8, textColor=SLATE,
            leading=11, alignment=TA_LEFT,
        ),
    }


# ─── Header + Footer ───────────────────────────────────────────────
def draw_header_footer(canvas, doc):
    canvas.saveState()
    w, h = A4
    if doc.page == 1:
        canvas.restoreState()
        return

    # Header line
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(0.5)
    canvas.line(2 * cm, h - 1.5 * cm, w - 2 * cm, h - 1.5 * cm)

    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(TEAL)
    canvas.drawString(2 * cm, h - 1.2 * cm, "NEUROSOFT APP")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(SLATE)
    canvas.drawRightString(
        w - 2 * cm, h - 1.2 * cm,
        "Guía del Beta Tester · Edición 2026"
    )

    # Footer
    canvas.setStrokeColor(RULE)
    canvas.line(2 * cm, 1.5 * cm, w - 2 * cm, 1.5 * cm)

    canvas.setFont("Helvetica", 7)
    canvas.setFillColor(ASH)
    canvas.drawString(2 * cm, 1.0 * cm, "Johan Salgado · jssalgadosa@unal.edu.co")
    canvas.drawRightString(w - 2 * cm, 1.0 * cm, f"Página {doc.page}")

    canvas.restoreState()


# ─── Cover ─────────────────────────────────────────────────────────
def draw_cover(canvas, doc):
    """Diseño editorial: banda lateral teal + bloque tipográfico mixto."""
    canvas.saveState()
    w, h = A4

    # Banda lateral izquierda
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, 2.5 * cm, h, fill=1, stroke=0)

    # Acento teal sobre la banda
    canvas.setFillColor(TEAL)
    canvas.rect(0, h * 0.6, 2.5 * cm, h * 0.05, fill=1, stroke=0)

    # Texto vertical en la banda
    canvas.saveState()
    canvas.translate(1.25 * cm, h * 0.25)
    canvas.rotate(90)
    canvas.setFont("Helvetica-Bold", 10)
    canvas.setFillColor(CREAM)
    canvas.drawString(0, 0, "GUÍA DEL BETA TESTER · 2026")
    canvas.restoreState()

    # Eyebrow
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(TEAL)
    canvas.drawString(3.5 * cm, h - 4 * cm, "NEUROSOFT APP")

    # Línea decorativa
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(2)
    canvas.line(3.5 * cm, h - 4.3 * cm, 5.5 * cm, h - 4.3 * cm)

    # Título principal — bloque grande
    canvas.setFont("Helvetica-Bold", 46)
    canvas.setFillColor(NAVY)
    canvas.drawString(3.5 * cm, h - 7 * cm, "Bienvenido")

    canvas.setFont("Times-BoldItalic", 32)
    canvas.setFillColor(TEAL)
    canvas.drawString(3.5 * cm, h - 9 * cm, "al programa de beta testing.")

    # Lead
    canvas.setFont("Times-Italic", 14)
    canvas.setFillColor(SLATE)
    text = canvas.beginText(3.5 * cm, h - 11 * cm)
    text.setLeading(20)
    for line in [
        "Esta guía explica qué es NeuroSoft App,",
        "qué puedes hacer con ella, cómo instalarla y",
        "cómo reportar feedback durante el periodo de prueba.",
    ]:
        text.textLine(line)
    canvas.drawText(text)

    # Metadata bloque
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(SLATE)
    canvas.drawString(3.5 * cm, 5 * cm, "DESARROLLADO POR")
    canvas.setFont("Helvetica-Bold", 12)
    canvas.setFillColor(NAVY)
    canvas.drawString(3.5 * cm, 4.4 * cm, "Johan Sebastián Salgado Sarmiento")
    canvas.setFont("Helvetica", 10)
    canvas.setFillColor(SLATE)
    canvas.drawString(3.5 * cm, 4.0 * cm, "Psicólogo · Universidad Nacional de Colombia")
    canvas.setFont("Helvetica-Oblique", 9)
    canvas.setFillColor(TEAL)
    canvas.drawString(3.5 * cm, 3.5 * cm, "jssalgadosa@unal.edu.co")

    # Stamp inferior
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.8)
    canvas.line(3.5 * cm, 2.5 * cm, w - 2 * cm, 2.5 * cm)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(TEAL)
    canvas.drawString(3.5 * cm, 2.0 * cm, "SOFTWARE CLÍNICO · USO INVESTIGATIVO · LEY 1090 / 1581 / 1616")

    canvas.restoreState()


# ─── Helpers ────────────────────────────────────────────────────────
def callout(title, body, color, S):
    """Caja de aviso con barra lateral."""
    tbl = Table(
        [[Paragraph(f"<b>{title}</b>", S["h3"]),],
         [Paragraph(body, S["body_sm"])]],
        colWidths=[16 * cm],
    )
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LINEBEFORE", (0, 0), (-1, -1), 3, color),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return tbl


def kpi_row(items, S):
    """Fila de KPIs editoriales."""
    cells = []
    for value, label, color in items:
        cell = [
            Paragraph(
                f'<font color="{"#" + color.hexval()[2:]}">'
                f'<b>{value}</b></font>',
                ParagraphStyle("kpi_v", fontName="Times-Bold", fontSize=28,
                              leading=32, alignment=TA_LEFT, textColor=color),
            ),
            Paragraph(label, S["eyebrow"]),
        ]
        cells.append(cell)
    tbl = Table([cells], colWidths=[None] * len(items))
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 16),
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
    ]))
    return tbl


def section_title(eyebrow_text, title, italic_part, S):
    """Encabezado editorial: eyebrow teal + título serif/italic mixto."""
    flow = []
    flow.append(HRFlowable(width="100%", thickness=1, color=TEAL, spaceBefore=0, spaceAfter=4))
    flow.append(Paragraph(eyebrow_text, S["eyebrow"]))
    flow.append(Paragraph(
        f'{title} <i><font color="{"#" + TEAL.hexval()[2:]}">{italic_part}</font></i>',
        S["h1"],
    ))
    flow.append(Spacer(1, 6))
    return flow


def bullets(items, S, color=TEAL):
    """Lista de bullets con punto teal."""
    rows = []
    hex_color = "#" + color.hexval()[2:]
    for item in items:
        rows.append([
            Paragraph(f'<font color="{hex_color}"><b>·</b></font>',
                     ParagraphStyle("b_dot", fontName="Helvetica-Bold",
                                   fontSize=12, textColor=color, leading=14)),
            Paragraph(item, S["body"]),
        ])
    tbl = Table(rows, colWidths=[0.6 * cm, 16.4 * cm])
    tbl.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
    ]))
    return tbl


# ─── Construir contenido ───────────────────────────────────────────
def build_content(S):
    F = []

    # ═════════ COVER (página 1 — sin frame normal) ═════════
    # NextPageTemplate asegura que la página 2 en adelante use el frame Normal,
    # no el Cover (que no tiene márgenes y dibuja el fondo decorativo).
    F.append(NextPageTemplate("Normal"))
    F.append(PageBreak())

    # ═════════ § 1. Qué es NeuroSoft App ═════════
    F.extend(section_title(
        "01 · INTRODUCCIÓN",
        "Qué es",
        "NeuroSoft App.",
        S,
    ))

    F.append(Paragraph(
        "<b>NeuroSoft App</b> es un sistema integral para la práctica clínica de "
        "psicólogos y neuropsicólogos en Colombia. Combina evaluación neuropsicológica "
        "computarizada, rehabilitación cognitiva, sesiones de psicoterapia con notas "
        "SOAP, telemedicina y un asistente de IA local — todo en una sola aplicación "
        "de escritorio que se instala como un programa cualquiera.",
        S["body"],
    ))
    F.append(Spacer(1, 4))
    F.append(Paragraph(
        "Tiene cargados <b>168 baremos colombianos</b> y latinoamericanos "
        "(Neuronorma Colombia, Arango-Lasprilla & Rivera 2015, ENI-2, WISC-IV, "
        "WAIS-III, MoCA-S Bogotá). El motor de scoring calcula automáticamente "
        "escalares, índices, percentiles y discrepancias clínicas.",
        S["body"],
    ))

    F.append(Spacer(1, 12))
    F.append(kpi_row([
        ("168", "PRUEBAS CON BAREMOS", TEAL),
        ("3", "PILARES CLÍNICOS", NAVY),
        ("45+", "RECURSOS EDUCATIVOS", PLUM),
        ("100%", "OFFLINE-CAPABLE", FOREST),
    ], S))

    F.append(Spacer(1, 14))
    F.append(callout(
        "Estado actual",
        "Versión <b>2.0.0</b> — Beta cerrada con profesionales seleccionados. "
        "Los baremos están verificados con casos clínicos reales (no es un simulador). "
        "Todo el procesamiento ocurre en tu computadora; ningún dato del paciente "
        "se envía a servidores externos.",
        TEAL, S,
    ))

    # ═════════ § 2. Los tres pilares ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "02 · ARQUITECTURA",
        "Los tres",
        "pilares clínicos.",
        S,
    ))

    F.append(Paragraph(
        "NeuroSoft se organiza en tres pilares complementarios. Cada uno "
        "puede usarse de forma independiente, pero se diseñaron para flujos "
        "integrados (evaluar → tratar → educar al paciente).",
        S["lead"],
    ))

    # Pilar 1
    F.append(Paragraph("PILAR 1 · EVALUACIÓN NEUROPSICOLÓGICA", S["eyebrow"]))
    F.append(Paragraph(
        '<font color="#1E293B"><b>Aplicar, calificar y redactar</b></font> '
        '<i><font color="#0D9488">en una sola sesión.</font></i>',
        S["h2"],
    ))
    F.append(bullets([
        "<b>Aplicación guiada</b>: cronómetro de subtests, conductas observables por test, "
        "ítem por ítem cuando aplica, autosave cada 30 segundos.",
        "<b>168 pruebas con baremos colombianos</b> distribuidas por población "
        "(92 infantil, 30 adulto joven, 64 adulto mayor) — disponibles en el menú "
        "«Aprender · Pruebas disponibles».",
        "<b>10 estrategias de cálculo</b>: escalar, índice compuesto, percentil, "
        "puntaje Z, ajuste por escolaridad, etc. Cubre WISC-IV, WAIS-III, ENI-2, "
        "Neuronorma, Stroop, TMT, FCRO, MoCA, MMSE, GADS, GROBER, entre otras.",
        "<b>Discrepancias entre índices</b> con tablas Flanagan & Kaufman, e "
        "indicadores de validez de síntomas (Rey 15-item).",
        "<b>Informes PDF profesionales</b>: 7 variantes (Pro adulto, Pediátrico, "
        "Medicolegal, Junta Médica, Inconcluso, Cierre terapéutico, Estándar).",
        "<b>Re-test con RCI</b>: comparativo Pre-Post con Reliable Change Index "
        "(Jacobson & Truax 1991) para detectar cambios clínicamente significativos.",
    ], S))

    F.append(Spacer(1, 10))

    # Pilar 2
    F.append(Paragraph("PILAR 2 · PSICOTERAPIA + REHABILITACIÓN", S["eyebrow"]))
    F.append(Paragraph(
        '<font color="#1E293B"><b>Sesiones SOAP, tareas-casa</b></font> '
        '<i><font color="#0D9488">y entrenamiento cognitivo.</font></i>',
        S["h2"],
    ))
    F.append(bullets([
        "<b>Notas SOAP estructuradas</b> (Subjetivo, Objetivo, Análisis, Plan) con "
        "modalidad (presencial, telepsicología, telefónica), modalidad de riesgo "
        "suicida (C-SSRS), alianza terapéutica y estado emocional pre-post.",
        "<b>23 enfoques terapéuticos catalogados</b>: TCC, DBT, ACT, EMDR, Schema "
        "Therapy, Sistémica, Logoterapia, Mindfulness, entre otros.",
        "<b>Tareas terapéuticas entre sesiones</b> (Kazantzis et al. 2016, g≈0.48): "
        "registros de pensamientos, autorregistros conductuales, exposición, "
        "activación conductual, habilidades DBT, psicoeducación.",
        "<b>16 actividades de rehabilitación cognitiva</b>: Stroop, N-Back, Corsi "
        "(forward y backward), CPT, Go/No-Go, Fluidez verbal, Set Shifting, "
        "Tachado, Rotación Mental, Reconocimiento Ekman, Spaced Retrieval, Torre "
        "de Londres, Mente en los Ojos, AVD-Dinero, y más.",
        "<b>Telerehab</b>: el paciente recibe un link público (sin login) para "
        "completar actividades desde casa. El clínico ve adherencia en tiempo real.",
        "<b>Firma irreversible de sesiones</b> conforme a Resolución 1995 de 1999.",
    ], S))

    F.append(Spacer(1, 10))

    # Pilar 3
    F.append(Paragraph("PILAR 3 · APRENDER (BIBLIOTECA + PRUEBAS)", S["eyebrow"]))
    F.append(Paragraph(
        '<font color="#1E293B"><b>Bibliografía curada</b></font> '
        '<i><font color="#0D9488">y catálogo de pruebas disponibles.</font></i>',
        S["h2"],
    ))
    F.append(bullets([
        "<b>Biblioteca clínica</b> con 45+ recursos curados en 9 categorías: "
        "Neuropsicología, Psicoterapia, Infantil, Adulto Mayor, Instrumentos, "
        "Ética y Legal Colombia, Investigación, Rehabilitación.",
        "<b>Pruebas disponibles</b>: catálogo navegable de las 168 pruebas con "
        "baremos, filtrable por población, fuente normativa y tipo de cálculo.",
        "Cada ficha indica autor, año, fuente, formato (PDF abierto / suscripción / "
        "libro físico) y nivel (básico / intermedio / avanzado).",
    ], S))

    # ═════════ § 3. Instalación ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "03 · INSTALACIÓN",
        "Cómo poner",
        "NeuroSoft a funcionar.",
        S,
    ))

    F.append(Paragraph(
        "Recibes un único archivo: <b>NeuroSoft-Setup.exe</b> (~1.4 GB). "
        "Es un instalador estándar de Windows — funciona igual que cualquier "
        "otro programa que hayas instalado.",
        S["lead"],
    ))

    F.append(Paragraph("REQUISITOS MÍNIMOS DEL SISTEMA", S["eyebrow"]))
    req = [
        ["Sistema operativo", "Windows 10 o Windows 11 (64-bit)"],
        ["Procesador", "Intel i5 / AMD Ryzen 5 o superior"],
        ["Memoria RAM", "8 GB (16 GB recomendado si usarás IA local)"],
        ["Espacio en disco", "5 GB (incluye Ollama opcional)"],
        ["Conexión a internet", "Solo para instalar y opcional al usar IA externa"],
    ]
    req_tbl = Table(req, colWidths=[5 * cm, 12 * cm])
    req_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (1, 0), (1, -1), SLATE),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    F.append(req_tbl)
    F.append(Spacer(1, 14))

    F.append(Paragraph("PASOS PARA INSTALAR", S["eyebrow"]))
    F.append(Paragraph(
        '<font color="#1E293B"><b>Tres clicks</b></font> '
        '<i><font color="#0D9488">y estás listo.</font></i>',
        S["h2"],
    ))
    F.append(bullets([
        "<b>1. Doble-click</b> en <font face=\"Courier\">NeuroSoft-Setup.exe</font>. "
        "Si Windows muestra «SmartScreen impidió el inicio…», pulsa "
        "«Más información» → «Ejecutar de todas formas» (el archivo no está "
        "firmado digitalmente porque es beta).",
        "<b>2. Sigue el asistente</b>: aceptar términos → elegir carpeta de "
        "instalación (default: <font face=\"Courier\">C:\\Program Files\\NeuroSoft</font>) → "
        "elegir si crear acceso directo en el escritorio.",
        "<b>3. Al finalizar</b>, marca «Abrir el Manual del Beta Tester» (opcional) y "
        "lanza NeuroSoft desde el menú Inicio o el ícono del escritorio.",
    ], S))

    F.append(Spacer(1, 12))
    F.append(callout(
        "Primer arranque (puede tardar ~30 segundos)",
        "La primera vez que abres NeuroSoft, el programa crea la base de datos "
        "local en <font face=\"Courier\">%APPDATA%\\NeuroSoft\\</font> y carga los "
        "168 baremos en memoria. Verás una pantalla de carga «Preparando tu "
        "consultorio…» — es normal. Si pasados 12 segundos sigue en blanco, "
        "aparecerá un botón <b>«Reintentar (limpiar caché)»</b>.",
        AMBER, S,
    ))

    F.append(Spacer(1, 10))
    F.append(Paragraph("CREDENCIALES DE ACCESO", S["eyebrow"]))
    F.append(Paragraph(
        '<font color="#1E293B"><b>Tu usuario</b></font> '
        '<i><font color="#0D9488">de beta tester.</font></i>',
        S["h2"],
    ))
    cred = [
        ["Usuario", "beta"],
        ["Contraseña", "BetaTester2026!"],
        ["Rol", "Profesional (sin permisos administrativos)"],
    ]
    cred_tbl = Table(cred, colWidths=[5 * cm, 12 * cm])
    cred_tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Courier-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
        ("TEXTCOLOR", (1, 0), (1, -1), TEAL),
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
    ]))
    F.append(cred_tbl)
    F.append(Spacer(1, 6))
    F.append(Paragraph(
        "Puedes cambiar tu contraseña desde <i>Configuración → Mi cuenta</i> en "
        "cualquier momento. Si olvidas la contraseña, contacta al desarrollador.",
        S["body_sm"],
    ))

    # ═════════ § 4. Cómo testear ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "04 · CÓMO TESTEAR",
        "Plan de prueba",
        "sugerido.",
        S,
    ))

    F.append(Paragraph(
        "No hace falta probar todo de una. Te sugiero recorrer NeuroSoft en "
        "<b>4 sesiones cortas</b> de 30-45 minutos cada una, simulando un "
        "caso clínico real. Anota lo que te parezca raro, lento, confuso, "
        "incorrecto o simplemente bonito.",
        S["lead"],
    ))

    F.append(Paragraph("SESIÓN 1 · ALTA Y EVALUACIÓN (45 MIN)", S["eyebrow"]))
    F.append(bullets([
        "Crear paciente nuevo desde <i>Pacientes → Registrar</i>.",
        "Llenar la Historia Clínica (atajos: Alt+H abre el panel de atajos).",
        "Aplicar una evaluación corta (recomendado: WISC-IV con un niño "
        "imaginario de 10 años) — al menos 5-6 subtests.",
        "Pulsar Finalizar y revisar el informe en <i>Resultados</i>.",
        "Generar un PDF en variante <b>«Pro»</b> y otro en variante "
        "<b>«Pediátrico»</b>; comparar.",
    ], S))
    F.append(Spacer(1, 8))

    F.append(Paragraph("SESIÓN 2 · PSICOTERAPIA (30 MIN)", S["eyebrow"]))
    F.append(bullets([
        "Ir a <i>Psicoterapia → Sesiones clínicas</i>, seleccionar el paciente.",
        "Crear un Plan terapéutico (enfoque sugerido: TCC) con 2 objetivos SMART.",
        "Registrar una sesión SOAP: completar las 4 secciones, marcar riesgo, "
        "asignar 1-2 tareas terapéuticas entre sesiones.",
        "Firmar la sesión y verificar que queda bloqueada para edición.",
    ], S))
    F.append(Spacer(1, 8))

    F.append(Paragraph("SESIÓN 3 · REHABILITACIÓN (30 MIN)", S["eyebrow"]))
    F.append(bullets([
        "Ir a <i>Rehabilitación → Plan & Actividades</i>.",
        "Crear plan de rehab con 2-3 actividades (sugeridas: Stroop, Corsi).",
        "Ejecutar una actividad y verificar que el cronómetro y la captura "
        "de respuestas funcionan.",
        "Probar el modo <b>Telerehab</b>: generar link público y abrirlo en otra "
        "pestaña/dispositivo para simular al paciente desde casa.",
    ], S))
    F.append(Spacer(1, 8))

    F.append(Paragraph("SESIÓN 4 · APRENDER + CONFIG (20 MIN)", S["eyebrow"]))
    F.append(bullets([
        "Explorar <i>Aprender → Biblioteca clínica</i> y filtrar por categoría.",
        "Ver <i>Aprender → Pruebas disponibles</i> y revisar 2-3 fichas.",
        "Probar modo oscuro (Alt+D) y revisar contraste en varias pantallas.",
        "Generar un backup desde <i>Configuración → Respaldo</i>.",
        "Revisar la <b>Configuración</b>: los tabs ahora están agrupados en "
        "3 secciones (Mi consultorio / Datos clínicos / Sistema) — ¿es más fácil "
        "encontrar lo que buscas?",
    ], S))

    F.append(Spacer(1, 12))
    F.append(callout(
        "Novedades UI en esta build (mayo 2026)",
        "<b>Dashboard rediseñado</b>: ahora incluye un banner de bienvenida con "
        "descripción de cada módulo, para que quede claro qué hace el sistema "
        "desde el primer uso.<br/><br/>"
        "<b>Panel de conductas observadas más ancho</b> en Aplicar Evaluación: "
        "el sidebar derecho pasó de 320 px a 416 px, y ahora es fijo (sticky) "
        "mientras navegas las instrucciones — más espacio para las notas clínicas.<br/><br/>"
        "<b>Screening reorganizado</b>: las escalas se agrupan en tarjetas por "
        "categoría (Cognitivo / Emocional / TDAH / Conductual / Funcional / "
        "Trauma) con iconos, en vez de una fila interminable de botones.<br/><br/>"
        "<b>Configuración en 3 grupos</b>: los 13 tabs se presentan en una tabla "
        "claramente separada por sección con descripción de qué contiene cada una.",
        TEAL, S,
    ))

    # ═════════ § 5. Cómo reportar ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "05 · CÓMO REPORTAR",
        "Tu feedback es",
        "lo más valioso.",
        S,
    ))

    F.append(Paragraph(
        "Cualquier formato sirve: email, WhatsApp, mensaje de voz, screenshot, "
        "lo que sea más rápido para ti. Lo importante es que <b>NO te "
        "autocensures</b> — si algo te parece mal, díme, aunque sea cosmético.",
        S["lead"],
    ))

    F.append(Paragraph("PARA UN BUG O PROBLEMA", S["eyebrow"]))
    F.append(bullets([
        "<b>Qué pantalla</b> estabas viendo (ej. «Aplicar evaluación, subtest "
        "Vocabulario WISC-IV»).",
        "<b>Qué hiciste</b> antes de que pasara (la secuencia de clicks).",
        "<b>Qué esperabas</b> que pasara.",
        "<b>Qué pasó</b> realmente (cita textual del mensaje si hubo).",
        "<b>Screenshot</b> si es visual.",
    ], S))

    F.append(Spacer(1, 10))
    F.append(Paragraph("PARA UNA SUGERENCIA / MEJORA UX", S["eyebrow"]))
    F.append(bullets([
        "<b>Qué hacías</b> y qué te incomodó o te pareció lento.",
        "<b>Cómo lo harías tú</b> (aunque sea una idea informal).",
        "<b>Cuánto te molestó</b>: bloqueante / molesto / cosmético.",
    ], S))

    F.append(Spacer(1, 10))
    F.append(Paragraph("PARA UNA DUDA CLÍNICA", S["eyebrow"]))
    F.append(bullets([
        "<b>Qué prueba o cálculo</b> te genera dudas.",
        "<b>Caso concreto</b>: edad, sexo, escolaridad, PD ingresado.",
        "<b>Qué resultado obtuviste</b> y por qué te parece raro.",
        "<b>Con qué fuente</b> normativa esperarías comparar (manual, libro, paper).",
    ], S))

    F.append(Spacer(1, 14))
    F.append(callout(
        "Canal de comunicación",
        "Email: <b>jssalgadosa@unal.edu.co</b>  ·  "
        "WhatsApp / mensaje directo · Respuesta esperada en <b>24-48 horas</b>.<br/>"
        "Acumulo feedback de todos los beta testers y libero builds nuevas "
        "cada 1-2 semanas con los fixes priorizados.",
        TEAL, S,
    ))

    F.append(Spacer(1, 14))
    F.append(callout(
        "Lo que NO necesito que reportes",
        "Cambios de copia menores («mejor decir 'paciente' que 'usuario'») los "
        "estoy puliendo paso a paso. Tampoco fuentes ni colores — ya cerramos la "
        "identidad visual. Enfócate en <b>clínica, scoring, flujos de trabajo</b> "
        "y <b>cualquier cosa que rompa o confunda</b>.",
        SLATE, S,
    ))

    # ═════════ § 6. Sobre la IA ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "06 · ASISTENTE IA",
        "Cómo funciona",
        "el asistente clínico.",
        S,
    ))

    F.append(Paragraph(
        "NeuroSoft incluye un <b>Asistente IA</b> que ayuda a mejorar la "
        "redacción de informes, sugerir hipótesis diagnósticas, y explicar "
        "discrepancias entre índices. La IA es <b>opcional</b> — todo el resto "
        "del programa funciona sin ella.",
        S["lead"],
    ))

    F.append(Paragraph("MODOS DISPONIBLES", S["eyebrow"]))
    modos = [
        [
            Paragraph("<b>Modo 1 · Ollama local</b>", S["h3"]),
            Paragraph(
                "Modelo de IA corriendo en tu computadora. <b>100% privado</b> "
                "(ningún dato sale de tu equipo). Requiere instalar Ollama (~700 MB) y "
                "descargar un modelo (~4-6 GB). Recomendado: Llama 3.1 8B. "
                "El setup automático lo deja listo si tienes RAM ≥ 8GB.",
                S["body_sm"],
            ),
        ],
        [
            Paragraph("<b>Modo 2 · API externa</b>", S["h3"]),
            Paragraph(
                "Conecta con Anthropic Claude o OpenAI GPT-4 vía API key tuya. "
                "Más capaz que Ollama local, pero <b>envía el texto a servidores "
                "externos</b>. Solo usar con texto anonimizado (no nombres ni "
                "documentos de identidad). Configurar en <i>Asistente IA → "
                "Proveedor</i>.",
                S["body_sm"],
            ),
        ],
        [
            Paragraph("<b>Modo 3 · Apagado</b>", S["h3"]),
            Paragraph(
                "Sin IA. Todas las funciones clínicas (evaluación, scoring, "
                "informes, rehab, sesiones) siguen funcionando exactamente igual.",
                S["body_sm"],
            ),
        ],
    ]
    for row in modos:
        modo_tbl = Table([row], colWidths=[5 * cm, 12 * cm])
        modo_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, -1), 0.4, RULE),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ]))
        F.append(modo_tbl)

    F.append(Spacer(1, 14))
    F.append(Paragraph("QUÉ ESPERAR DE LA IA EN ESTA BETA", S["eyebrow"]))
    F.append(Paragraph(
        '<font color="#1E293B"><b>Útil para borradores</b></font> '
        '<i><font color="#0D9488">— nunca para reemplazar tu juicio clínico.</font></i>',
        S["h2"],
    ))
    F.append(bullets([
        "<b>Mejorar redacción de observaciones</b>: pulir gramática, evitar "
        "regionalismos, mantener tono clínico formal.",
        "<b>Sugerir hipótesis diagnósticas</b> dado un patrón de puntajes — la IA "
        "muestra DSM-5 / CIE-10 candidatos, tú decides cuáles aplican.",
        "<b>Explicar discrepancias entre índices</b> en lenguaje accesible para "
        "la familia o el remitente.",
        "<b>Generar plan de rehabilitación inicial</b> a partir de los dominios "
        "bajos detectados.",
    ], S))

    F.append(Spacer(1, 12))
    F.append(callout(
        "Limitaciones y responsabilidad clínica",
        "La IA puede equivocarse — especialmente con baremos no estándar o "
        "casos atípicos. <b>El informe final es responsabilidad del clínico</b>, "
        "no de la IA. NeuroSoft incluye disclaimers automáticos en cada salida IA "
        "que recuerdan revisar manualmente antes de firmar. <br/><br/>"
        "Si la IA dice una barbaridad, <b>repórtalo</b> — me ayuda a afinar los "
        "prompts del sistema.",
        RUBY, S,
    ))

    # ═════════ § 7. Privacidad ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "07 · PRIVACIDAD Y LEGAL",
        "Tus datos clínicos",
        "están en tu computadora.",
        S,
    ))

    F.append(Paragraph(
        "NeuroSoft cumple con el marco legal colombiano para datos clínicos:",
        S["body"],
    ))
    F.append(Spacer(1, 4))
    F.append(bullets([
        "<b>Ley 1581 de 2012 · Habeas Data</b>: datos sensibles solo en tu equipo, "
        "ninguna sincronización en la nube por defecto.",
        "<b>Ley 1090 de 2006 · Código Deontológico</b>: secreto profesional, "
        "consentimiento informado guiado en el alta del paciente.",
        "<b>Resolución 1995 de 1999 · Historia Clínica</b>: trazabilidad de "
        "cambios (audit log), firma irreversible de sesiones, conservación.",
        "<b>Ley 1616 de 2013 · Salud Mental</b>: enfoque integral, derecho a la "
        "atención digna.",
    ], S))

    F.append(Spacer(1, 12))
    F.append(Paragraph("DÓNDE QUEDAN TUS DATOS", S["eyebrow"]))
    F.append(Paragraph(
        "Toda la información del paciente vive en una base de datos SQLite local "
        "en:",
        S["body"],
    ))
    F.append(Spacer(1, 4))
    path_tbl = Table([[
        Paragraph(
            '<font color="#0D9488">C:\\Users\\&lt;TuUsuario&gt;\\AppData\\Roaming\\NeuroSoft\\neurosoft.db</font>',
            S["mono"],
        )
    ]], colWidths=[17 * cm])
    path_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT),
        ("LEFTPADDING", (0, 0), (-1, -1), 14),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    F.append(path_tbl)

    F.append(Spacer(1, 8))
    F.append(Paragraph(
        "Puedes generar backups manuales (.db) desde <i>Configuración → Respaldo</i>. "
        "Recomiendo hacer uno por semana durante el periodo de prueba — los pegas "
        "en tu OneDrive / Drive personal y listo.",
        S["body"],
    ))

    F.append(Spacer(1, 14))
    F.append(callout(
        "Si decides dejar de usar NeuroSoft",
        "Puedes desinstalar el programa desde <i>Configuración de Windows → Apps</i>. "
        "<b>La carpeta <font face=\"Courier\">%APPDATA%\\NeuroSoft</font> NO se borra "
        "automáticamente</b> — contiene tus datos clínicos. Bórrala manualmente "
        "solo si estás segura de no querer recuperar las evaluaciones realizadas.",
        AMBER, S,
    ))

    # ═════════ § 8. Cierre ═════════
    F.append(PageBreak())
    F.extend(section_title(
        "08 · CIERRE",
        "Gracias por",
        "acompañar este proyecto.",
        S,
    ))

    F.append(Paragraph(
        "NeuroSoft App nace de una frustración personal — los softwares clínicos "
        "existentes en Colombia son caros, fragmentados o no tienen baremos "
        "locales. Construirlo solo ha sido difícil; tenerte como beta tester "
        "lo hace más fácil.",
        S["lead"],
    ))
    F.append(Spacer(1, 6))
    F.append(Paragraph(
        "Cada error que reportas, cada sugerencia, cada «esto está confuso» "
        "termina convirtiéndose en una mejora concreta. Las primeras cinco "
        "betas previas ya cambiaron decenas de cosas: el flujo de evaluación, "
        "los textos clínicos, los baremos, la estética del informe.",
        S["body"],
    ))
    F.append(Spacer(1, 6))
    F.append(Paragraph(
        "Toma tu tiempo, no hay deadline duro. Si tienes una semana ocupada, "
        "pausa. Si encuentras algo raro, escríbelo — incluso si dudas si vale "
        "la pena reportarlo. Casi siempre vale.",
        S["body"],
    ))

    F.append(Spacer(1, 30))
    F.append(HRFlowable(width="50%", thickness=1, color=TEAL,
                       spaceBefore=0, spaceAfter=8, hAlign="LEFT"))
    F.append(Paragraph(
        '<i><font color="#0D9488" size="14">— Johan Sebastián Salgado Sarmiento</font></i>',
        ParagraphStyle("sig", fontName="Times-Italic", fontSize=14,
                      textColor=TEAL, leading=18),
    ))
    F.append(Paragraph(
        "Psicólogo · Universidad Nacional de Colombia",
        S["body_sm"],
    ))
    F.append(Paragraph(
        "Mayo 2026",
        S["body_sm"],
    ))

    return F


# ─── Main ───────────────────────────────────────────────────────────
def main(output_path="GUIA_BETA_TESTER.pdf"):
    S = make_styles()

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2.2 * cm,
        bottomMargin=2 * cm,
        title="Guía del Beta Tester · NeuroSoft App",
        author="Johan Sebastián Salgado Sarmiento",
        subject="Manual de instalación y prueba",
    )

    # Frame para la cover (sin márgenes)
    cover_frame = Frame(0, 0, A4[0], A4[1], leftPadding=0, rightPadding=0,
                       topPadding=0, bottomPadding=0, id="cover")
    # Frame para páginas normales
    normal_frame = Frame(doc.leftMargin, doc.bottomMargin,
                        doc.width, doc.height, id="normal")

    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[cover_frame], onPage=draw_cover),
        PageTemplate(id="Normal", frames=[normal_frame], onPage=draw_header_footer),
    ])

    F = build_content(S)
    doc.build(F)
    print(f"[OK] PDF generado: {output_path}")


if __name__ == "__main__":
    import sys
    output = sys.argv[1] if len(sys.argv) > 1 else "GUIA_BETA_TESTER.pdf"
    main(output)
