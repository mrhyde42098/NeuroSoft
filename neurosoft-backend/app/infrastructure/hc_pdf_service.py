"""
app/infrastructure/hc_pdf_service.py
========================================
§QW-4 — Generador de PDF de Historia Clínica (sin evaluación).

Útil cuando una EPS/IPS solicita la HC sin necesidad de informe NPS,
o el clínico quiere imprimir la HC para anexar al expediente físico.

Reutiliza ReportLab; output A4 portrait con header, datos sociodemográficos,
4 tabs HC (Desarrollo, Antecedentes, Familiar-Social, Plan de Atención) y
firma del profesional.
"""
from __future__ import annotations

import io
import logging
from datetime import date, datetime
from typing import Any

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

logger = logging.getLogger("neurosoft.hc_pdf")

# Layout
PAGE_W, PAGE_H = A4
MARGIN_L = 18 * mm
MARGIN_R = 18 * mm
MARGIN_T = 18 * mm
MARGIN_B = 18 * mm
CONTENT_W = PAGE_W - MARGIN_L - MARGIN_R

# Colores (mantengamos consistente con report_pro/theme)
NAVY = (0.07, 0.20, 0.40)
TEAL = (0.05, 0.58, 0.53)
SLATE = (0.30, 0.34, 0.42)
LIGHT = (0.93, 0.94, 0.96)
GRAY = (0.55, 0.60, 0.66)


def _safe(v: Any, default: str = "—") -> str:
    """Convierte a string seguro. Vacíos/None → default."""
    if v is None:
        return default
    s = str(v).strip()
    return s if s else default


def _fmt_date(d) -> str:
    if d is None:
        return "—"
    if isinstance(d, (date, datetime)):
        return d.strftime("%d/%m/%Y")
    return str(d)


def _calc_age(birth: date | None) -> str:
    if not birth:
        return "—"
    today = date.today()
    years = today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    months = (today.month - birth.month) % 12
    return f"{years}a {months}m"


def generate_clinical_history_pdf(
    *,
    patient: Any,
    clinical_history: Any | None = None,
    institucion: Any | None = None,
    profesional: Any | None = None,
) -> bytes:
    """Genera PDF de Historia Clínica y devuelve bytes."""
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.setTitle(f"Historia Clínica - {_safe(getattr(patient, 'primer_apellido', ''))}")
    c.setAuthor((institucion and institucion.nombre) or "NeuroSoft")

    y = _draw_header(c, institucion)
    y = _draw_title(c, y)
    y = _draw_paciente_block(c, y, patient)
    y = _draw_atencion_block(c, y, clinical_history, profesional)
    y = _draw_hc_tabs(c, y, clinical_history)
    _draw_firma(c, profesional)
    _draw_footer(c, 1, 1)
    c.showPage()
    c.save()
    return buf.getvalue()


# ─────────────────────────────────────────────────────────────
# Bloques de dibujo
# ─────────────────────────────────────────────────────────────

def _draw_header(c, institucion) -> float:
    """Header con nombre institución y línea TEAL. Devuelve y inicial."""
    name = (institucion and institucion.nombre) or "Consultorio Neuropsicológico"
    direccion = (institucion and institucion.direccion) or ""
    tel = (institucion and institucion.telefono) or ""
    email = (institucion and institucion.email) or ""

    y = PAGE_H - MARGIN_T
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(MARGIN_L, y, name)
    y -= 5 * mm
    sub = " · ".join(x for x in [direccion, tel, email] if x)
    if sub:
        c.setFillColorRGB(*GRAY)
        c.setFont("Helvetica", 8)
        c.drawString(MARGIN_L, y, sub[:140])
    y -= 3 * mm
    c.setStrokeColorRGB(*TEAL)
    c.setLineWidth(1.2)
    c.line(MARGIN_L, y, PAGE_W - MARGIN_R, y)
    return y - 7 * mm


def _draw_title(c, y) -> float:
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(MARGIN_L, y, "HISTORIA CLÍNICA NEUROPSICOLÓGICA")
    c.setFillColorRGB(*SLATE)
    c.setFont("Helvetica", 9)
    c.drawRightString(PAGE_W - MARGIN_R, y + 2, f"Emitido: {_fmt_date(date.today())}")
    return y - 10 * mm


def _draw_paciente_block(c, y, patient) -> float:
    y = _section_title(c, y, "Datos del paciente")
    nombre = " ".join(x for x in [
        getattr(patient, "primer_nombre", ""), getattr(patient, "segundo_nombre", ""),
        getattr(patient, "primer_apellido", ""), getattr(patient, "segundo_apellido", ""),
    ] if x).strip() or "—"
    rows = [
        ("Nombre completo", nombre),
        ("Documento", f"{_safe(getattr(patient, 'tipo_documento', ''))} {_safe(getattr(patient, 'numero_documento', ''))}".strip()),
        ("Fecha nacimiento", _fmt_date(getattr(patient, "fecha_nacimiento", None))),
        ("Edad actual", _calc_age(getattr(patient, "fecha_nacimiento", None))),
        ("Sexo", _safe(getattr(patient, "sexo", ""))),
        ("Estado civil", _safe(getattr(patient, "estado_civil", ""))),
        ("Lateralidad", _safe(getattr(patient, "lateralidad", ""))),
        ("Escolaridad", _safe(getattr(patient, "escolaridad", ""))),
        ("Ocupación", _safe(getattr(patient, "ocupacion", ""))),
        ("Lugar de origen", _safe(getattr(patient, "ciudad_origen", ""))),
        ("Lugar de residencia", _safe(getattr(patient, "ciudad_residencia", ""))),
        ("Dirección", _safe(getattr(patient, "direccion", ""))),
        ("Teléfono", _safe(getattr(patient, "telefono", ""))),
        ("Email", _safe(getattr(patient, "email", ""))),
    ]
    return _draw_two_col_table(c, y, rows)


def _draw_atencion_block(c, y, hc, profesional) -> float:
    y = _section_title(c, y, "Datos de atención")
    if hc is None:
        c.setFillColorRGB(*GRAY)
        c.setFont("Helvetica-Oblique", 9)
        c.drawString(MARGIN_L, y, "Sin historia clínica registrada para este paciente.")
        return y - 6 * mm
    rows = [
        ("Fecha de atención", _fmt_date(getattr(hc, "fecha_atencion", None))),
        ("Profesional", (profesional and profesional.nombre_completo) or "—"),
        ("Registro profesional", (profesional and profesional.registro_profesional) or "—"),
        ("Motivo de consulta", _safe(getattr(hc, "motivo_consulta", ""))),
        ("Acompañante", _safe(getattr(hc, "acompanante_nombre", "") or getattr(hc, "acompanante", ""))),
        ("Remitido por", _safe(getattr(hc, "remitido_por", ""))),
    ]
    return _draw_two_col_table(c, y, rows)


def _draw_hc_tabs(c, y, hc) -> float:
    if hc is None:
        return y
    sections = [
        ("Antecedentes", [
            ("Personales (médicos)", getattr(hc, "antecedentes_personales", "")),
            ("Familiares", getattr(hc, "antecedentes_familiares", "")),
            ("Psiquiátricos", getattr(hc, "antecedentes_psiquiatricos", "")),
            ("Farmacológicos", getattr(hc, "farmacos_actuales", "")),
            ("Tóxicos", getattr(hc, "antecedentes_toxicos", "")),
            ("Quirúrgicos", getattr(hc, "antecedentes_quirurgicos", "")),
        ]),
        ("Historia del desarrollo", [
            ("Prenatal", getattr(hc, "desarrollo_prenatal", "")),
            ("Perinatal", getattr(hc, "desarrollo_perinatal", "")),
            ("Postnatal", getattr(hc, "desarrollo_postnatal", "")),
            ("Hitos del desarrollo", getattr(hc, "hitos_desarrollo", "")),
            ("Escolaridad", getattr(hc, "historia_escolar", "")),
        ]),
        ("Familiar y social", [
            ("Composición familiar", getattr(hc, "composicion_familiar", "")),
            ("Dinámica familiar", getattr(hc, "dinamica_familiar", "")),
            ("Red de apoyo", getattr(hc, "red_apoyo", "")),
            ("Situación social", getattr(hc, "situacion_social", "")),
        ]),
        ("Plan de atención", [
            ("Impresión diagnóstica inicial", getattr(hc, "impresion_diagnostica", "")),
            ("Plan de evaluación", getattr(hc, "plan_evaluacion", "")),
            ("Recomendaciones iniciales", getattr(hc, "recomendaciones_iniciales", "")),
        ]),
    ]
    for title, rows in sections:
        y = _section_title(c, y, title)
        for label, val in rows:
            y = _draw_label_paragraph(c, y, label, _safe(val))
            if y < MARGIN_B + 30 * mm:
                # Salta de página y vuelve a dibujar header simple
                c.showPage()
                y = PAGE_H - MARGIN_T
                c.setFillColorRGB(*GRAY)
                c.setFont("Helvetica-Oblique", 8)
                c.drawString(MARGIN_L, y, "(continuación) Historia Clínica Neuropsicológica")
                y -= 6 * mm
    return y


def _draw_firma(c, profesional) -> None:
    """Bloque de firma al pie. Si no hay firma_base64 → solo línea."""
    if profesional is None:
        return
    y = MARGIN_B + 35 * mm
    c.setStrokeColorRGB(*SLATE)
    c.setLineWidth(0.6)
    c.line(MARGIN_L + 15 * mm, y, MARGIN_L + 85 * mm, y)
    c.setFillColorRGB(*NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(MARGIN_L + 15 * mm, y - 4 * mm, _safe(getattr(profesional, "nombre_completo", "")))
    c.setFillColorRGB(*GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(MARGIN_L + 15 * mm, y - 8 * mm, _safe(getattr(profesional, "titulo", "")))
    rp = getattr(profesional, "registro_profesional", "")
    if rp:
        c.drawString(MARGIN_L + 15 * mm, y - 12 * mm, f"Registro: {rp}")


def _draw_footer(c, page_num, total) -> None:
    c.setFillColorRGB(*GRAY)
    c.setFont("Helvetica", 7)
    txt = ("Documento confidencial. Ley 1581/2012 (Habeas Data Colombia) · "
           "Resolución 1995/1999 (Historia Clínica)")
    c.drawString(MARGIN_L, MARGIN_B / 2, txt)
    c.drawRightString(PAGE_W - MARGIN_R, MARGIN_B / 2, f"Página {page_num}")


# ─────────────────────────────────────────────────────────────
# Helpers de dibujo
# ─────────────────────────────────────────────────────────────

def _section_title(c, y, title: str) -> float:
    c.setFillColorRGB(*TEAL)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(MARGIN_L, y, title.upper())
    c.setStrokeColorRGB(*TEAL)
    c.setLineWidth(0.4)
    c.line(MARGIN_L, y - 2, PAGE_W - MARGIN_R, y - 2)
    return y - 7 * mm


def _draw_two_col_table(c, y, rows: list[tuple[str, str]]) -> float:
    """Tabla 2 columnas: label en gris, valor en negro."""
    label_x = MARGIN_L
    value_x = MARGIN_L + 55 * mm
    value_w = PAGE_W - MARGIN_R - value_x
    for label, value in rows:
        # Wrap del valor
        lines = _wrap_text(c, value, value_w, "Helvetica", 9)
        _h = max(5, len(lines)) * mm
        c.setFillColorRGB(*GRAY)
        c.setFont("Helvetica", 9)
        c.drawString(label_x, y, label)
        c.setFillColorRGB(0.10, 0.13, 0.18)
        c.setFont("Helvetica", 9)
        for i, ln in enumerate(lines):
            c.drawString(value_x, y - i * (3.6 * mm), ln)
        y -= max(5 * mm, len(lines) * 3.6 * mm + 1 * mm)
    return y - 2 * mm


def _draw_label_paragraph(c, y, label: str, text: str) -> float:
    c.setFillColorRGB(*GRAY)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(MARGIN_L, y, label.upper())
    y -= 4 * mm
    c.setFillColorRGB(0.10, 0.13, 0.18)
    c.setFont("Helvetica", 9)
    lines = _wrap_text(c, text, CONTENT_W, "Helvetica", 9)
    for ln in lines:
        c.drawString(MARGIN_L, y, ln)
        y -= 3.6 * mm
    return y - 1.5 * mm


def _wrap_text(c, text: str, max_w: float, font: str, size: float) -> list[str]:
    """Word-wrap simple usando stringWidth de canvas."""
    text = (text or "").replace("\r", "")
    if not text or text == "—":
        return ["—"]
    out: list[str] = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            out.append("")
            continue
        line = ""
        for w in words:
            test = (line + " " + w).strip()
            if c.stringWidth(test, font, size) <= max_w:
                line = test
            else:
                if line:
                    out.append(line)
                line = w
        if line:
            out.append(line)
    return out
