"""
app/infrastructure/rehab_pdf_service.py
=========================================
Generador de PDF para el Plan de Rehabilitación Neuropsicológica.

A diferencia del informe de evaluación (report_service.py), este es un
documento más compacto (1-2 páginas) cuyo propósito es entregable al
paciente / cuidador como referencia del plan terapéutico firmado.

Estructura:
  • Encabezado institucional + identificación del paciente
  • Datos del plan (estado, fecha de inicio, frecuencia, dominios)
  • Objetivos y notas clínicas (texto libre)
  • Lista de actividades asignadas con dificultad y parámetros
  • Bloque de firma + hash SHA-256

Reutiliza la dependencia `reportlab` ya instalada en producción para el
informe de evaluación. NO comparte el `NeuroPDFGenerator` (ese es muy
específico al perfil cognitivo) — aquí mantenemos un generador minimal
más fácil de mantener.

Uso:
    from app.infrastructure.rehab_pdf_service import generate_rehab_plan_pdf
    pdf_bytes = generate_rehab_plan_pdf(plan_orm, patient_orm, institucion, profesional)
"""

from __future__ import annotations

import io
import json
import logging
from datetime import date, datetime
from typing import Any

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────
# Catálogo de etiquetas legibles (subset; cae a slug si falta)
# ─────────────────────────────────────────────────────────────
_DOMAIN_LABELS = {
    "atencion": "Atención",
    "memoria": "Memoria",
    "memoria_trabajo": "Memoria de trabajo",
    "funciones_ejecutivas": "Funciones ejecutivas",
    "lenguaje": "Lenguaje",
    "visoespacial": "Visoespacial",
    "velocidad_procesamiento": "Velocidad de procesamiento",
}

_ACTIVITY_LABELS = {
    "stroop": "Stroop (interferencia)",
    "n_back": "N-back (memoria de trabajo)",
    "fluencia_verbal": "Fluencia verbal",
    "tachado": "Tachado / búsqueda visual",
}


def _label_dominio(slug: str) -> str:
    return _DOMAIN_LABELS.get(slug, slug.replace("_", " ").capitalize())


def _label_actividad(slug: str) -> str:
    return _ACTIVITY_LABELS.get(slug, slug.replace("_", " ").capitalize())


def _safe_json(text: str | None) -> list:
    if not text:
        return []
    try:
        v = json.loads(text)
        return v if isinstance(v, list) else []
    except Exception:
        return []


def _fmt_date(d) -> str:
    if d is None:
        return "—"
    if isinstance(d, datetime):
        return d.strftime("%d/%m/%Y %H:%M")
    if isinstance(d, date):
        return d.strftime("%d/%m/%Y")
    return str(d)


# ─────────────────────────────────────────────────────────────
# Generador
# ─────────────────────────────────────────────────────────────
def generate_rehab_plan_pdf(
    plan,
    patient,
    institucion: Any | None = None,
    profesional: Any | None = None,
) -> bytes:
    """
    Genera el PDF del plan de rehabilitación.

    Args:
        plan:        RehabPlanORM (debe tener signed_at != None)
        patient:     PatientORM
        institucion: ConfigInstitucionORM | None
        profesional: ProfessionalORM | None

    Returns:
        bytes con el PDF.

    Raises:
        RuntimeError: si reportlab no está instalado.
        ValueError:   si el plan no está firmado.
    """
    if plan.signed_at is None:
        raise ValueError("El plan no está firmado. Solo planes firmados pueden exportarse a PDF.")

    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import cm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as e:
        raise RuntimeError(
            "reportlab no está instalado. Ejecute: pip install reportlab"
        ) from e

    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Plan de Rehabilitación Neuropsicológica",
        author=getattr(profesional, "nombre_completo", None) or "NeuroSoft",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle("h1", parent=styles["Heading1"], fontSize=16,
                        textColor=colors.HexColor("#0d9488"), spaceAfter=10)
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], fontSize=12,
                        textColor=colors.HexColor("#1e293b"), spaceBefore=10, spaceAfter=6)
    body = ParagraphStyle("body", parent=styles["BodyText"], fontSize=10, leading=14)
    small = ParagraphStyle("small", parent=styles["BodyText"], fontSize=8,
                           textColor=colors.HexColor("#64748b"), leading=10)

    story = []

    # ── Encabezado institucional ─────────────────────────────
    inst_nombre = getattr(institucion, "nombre", None) or "NeuroSoft"
    inst_nit = getattr(institucion, "nit", None) or ""
    inst_dir = getattr(institucion, "direccion", None) or ""
    inst_tel = getattr(institucion, "telefono", None) or ""
    story.append(Paragraph(inst_nombre, h1))
    if inst_nit or inst_dir or inst_tel:
        meta = " · ".join([x for x in (inst_nit, inst_dir, inst_tel) if x])
        story.append(Paragraph(meta, small))
    story.append(Spacer(1, 0.4 * cm))

    story.append(Paragraph("Plan de Rehabilitación Neuropsicológica", h2))

    # ── Datos del paciente ───────────────────────────────────
    nombre_pac = " ".join(filter(None, [
        getattr(patient, "primer_nombre", ""),
        getattr(patient, "segundo_nombre", "") or "",
        getattr(patient, "primer_apellido", ""),
        getattr(patient, "segundo_apellido", "") or "",
    ])).strip()
    pat_rows = [
        ["Paciente", nombre_pac or "—"],
        ["Documento", f"{getattr(patient, 'tipo_documento', '') or '—'} {getattr(patient, 'numero_documento', '') or ''}"],
        ["Fecha de nacimiento", _fmt_date(getattr(patient, "fecha_nacimiento", None))],
        ["Sexo", getattr(patient, "sexo", "—") or "—"],
    ]
    t = Table(pat_rows, colWidths=[5 * cm, 11 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9),
        ("FONT", (1, 0), (1, -1), "Helvetica", 9),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # ── Datos del plan ───────────────────────────────────────
    story.append(Paragraph("Datos del plan", h2))
    dominios = _safe_json(getattr(plan, "dominios_json", None))
    dominios_label = ", ".join(_label_dominio(s) for s in dominios) or "—"
    plan_rows = [
        ["ID del plan", str(plan.id)],
        ["Estado", str(plan.estado)],
        ["Fecha de inicio", _fmt_date(plan.fecha_inicio)],
        ["Fecha estimada de fin", _fmt_date(getattr(plan, "fecha_fin_estimada", None))],
        ["Frecuencia (sesiones/semana)", str(plan.frecuencia_semanal or "—")],
        ["Dominios objetivo", dominios_label],
    ]
    t = Table(plan_rows, colWidths=[5.5 * cm, 10.5 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9),
        ("FONT", (1, 0), (1, -1), "Helvetica", 9),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))

    # ── Objetivos clínicos ───────────────────────────────────
    if plan.objetivos:
        story.append(Paragraph("Objetivos terapéuticos", h2))
        story.append(Paragraph(plan.objetivos.replace("\n", "<br/>"), body))
        story.append(Spacer(1, 0.3 * cm))

    # ── Actividades asignadas ────────────────────────────────
    actividades = _safe_json(getattr(plan, "actividades_json", None))
    if actividades:
        story.append(Paragraph(f"Actividades asignadas ({len(actividades)})", h2))
        rows = [["#", "Actividad", "Dificultad", "Parámetros"]]
        for i, a in enumerate(actividades, start=1):
            slug = a.get("slug", "—") if isinstance(a, dict) else "—"
            dif = a.get("dificultad", "—") if isinstance(a, dict) else "—"
            params = a.get("parametros") if isinstance(a, dict) else None
            params_txt = ", ".join(f"{k}={v}" for k, v in (params or {}).items()) or "—"
            rows.append([str(i), _label_actividad(slug), str(dif), params_txt])
        t = Table(rows, colWidths=[1 * cm, 7 * cm, 2.5 * cm, 5.5 * cm])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0d9488")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9),
            ("FONT", (0, 1), (-1, -1), "Helvetica", 9),
            ("ALIGN", (0, 0), (0, -1), "CENTER"),
            ("ALIGN", (2, 0), (2, -1), "CENTER"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

    # ── Notas ────────────────────────────────────────────────
    if getattr(plan, "notas", None):
        story.append(Paragraph("Notas clínicas", h2))
        story.append(Paragraph(plan.notas.replace("\n", "<br/>"), body))
        story.append(Spacer(1, 0.4 * cm))

    # ── Bloque de firma ──────────────────────────────────────
    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph("Firma digital", h2))
    firma_rows = [
        ["Firmado por", str(getattr(plan, "signed_by_label", "") or "—")],
        ["Fecha de firma", _fmt_date(plan.signed_at)],
        ["Hash SHA-256", str(getattr(plan, "signature_sha256", "") or "—")],
    ]
    t = Table(firma_rows, colWidths=[4 * cm, 12 * cm])
    t.setStyle(TableStyle([
        ("FONT", (0, 0), (0, -1), "Helvetica-Bold", 9),
        ("FONT", (1, 0), (1, -1), "Helvetica", 8),
        ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#e2e8f0")),
        ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#f1f5f9")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(t)

    story.append(Spacer(1, 0.6 * cm))
    story.append(Paragraph(
        "Este documento es la copia firmada e inmutable del plan de rehabilitación. "
        "Cualquier modificación posterior queda registrada en el historial de auditoría.",
        small,
    ))

    doc.build(story)
    return buf.getvalue()
