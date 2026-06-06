"""Generación de PDF para consentimientos informados (imprimir / enviar por correo)."""
from __future__ import annotations

import base64
import io
from datetime import datetime

from app.infrastructure.database.orm_models import ConsentimientoORM, PatientORM


def _wrap_text(c, text: str, x: float, y: float, max_w: float, line_h: float = 12) -> float:
    words = (text or "").replace("\r", "").split()
    line = ""
    for w in words:
        trial = f"{line} {w}".strip()
        if c.stringWidth(trial, "Helvetica", 9) <= max_w:
            line = trial
        else:
            if line:
                c.drawString(x, y, line)
                y -= line_h
            line = w
    if line:
        c.drawString(x, y, line)
        y -= line_h
    for para in (text or "").split("\n"):
        if not para.strip():
            y -= line_h * 0.5
    return y


def _draw_paragraphs(c, text: str, x: float, y: float, max_w: float, page_h: float, margin: float) -> float:
    for block in (text or "").split("\n"):
        block = block.strip()
        if not block:
            y -= 8
            continue
        while block:
            chunk = block
            while chunk and c.stringWidth(chunk, "Helvetica", 9) > max_w:
                chunk = chunk[:-1]
            if not chunk:
                break
            if y < margin + 40:
                c.showPage()
                y = page_h - margin
            c.drawString(x, y, chunk)
            y -= 12
            block = block[len(chunk):].lstrip()
    return y


def build_consent_pdf(
    *,
    titulo: str,
    texto: str,
    version: str,
    patient: PatientORM | None = None,
    firmante: str | None = None,
    documento_firmante: str | None = None,
    relacion: str | None = None,
    fecha_firma: datetime | None = None,
    firma_base64: str | None = None,
    borrador: bool = False,
) -> bytes:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas

    buf = io.BytesIO()
    w, h = letter
    margin = 54
    c = canvas.Canvas(buf, pagesize=letter)
    c.setTitle(titulo)
    c.setAuthor("NeuroSoft")

    y = h - margin
    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, "NeuroSoft — Consentimiento informado")
    y -= 22
    c.setFont("Helvetica-Bold", 11)
    c.drawString(margin, y, titulo)
    y -= 16
    c.setFont("Helvetica", 8)
    c.drawString(margin, y, f"Versión del texto: {version}")
    y -= 14

    if patient:
        nombre = " ".join(filter(None, [patient.primer_nombre, patient.segundo_nombre, patient.primer_apellido, patient.segundo_apellido]))
        c.drawString(margin, y, f"Paciente: {nombre} · Doc: {patient.numero_documento or '—'}")
        y -= 12
    if borrador:
        c.setFillColorRGB(0.85, 0.45, 0.1)
        c.drawString(margin, y, "BORRADOR — Imprimir para firma presencial o firma digital en NeuroSoft")
        c.setFillColorRGB(0, 0, 0)
        y -= 16

    c.setFont("Helvetica", 9)
    y = _draw_paragraphs(c, texto, margin, y - 8, w - 2 * margin, h, margin)

    if firmante or firma_base64 or fecha_firma:
        if y < margin + 120:
            c.showPage()
            y = h - margin
        y -= 20
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y, "Firma y constancia")
        y -= 14
        c.setFont("Helvetica", 9)
        if firmante:
            c.drawString(margin, y, f"Firmante: {firmante} ({relacion or 'titular'})")
            y -= 12
        if documento_firmante:
            c.drawString(margin, y, f"Documento: {documento_firmante}")
            y -= 12
        if fecha_firma:
            c.drawString(margin, y, f"Fecha: {fecha_firma.strftime('%d/%m/%Y %H:%M UTC')}")
            y -= 12
        if firma_base64 and firma_base64.startswith("data:image"):
            try:
                raw = firma_base64.split(",", 1)[1]
                img_bytes = base64.b64decode(raw)
                from reportlab.lib.utils import ImageReader
                img = ImageReader(io.BytesIO(img_bytes))
                c.drawImage(img, margin, y - 55, width=180, height=50, preserveAspectRatio=True, mask="auto")
                y -= 65
            except Exception:
                pass

    c.setFont("Helvetica-Oblique", 7)
    c.drawString(margin, 30, "Documento generado por NeuroSoft. Conservar copia para el expediente clínico.")
    c.save()
    buf.seek(0)
    return buf.getvalue()


def pdf_from_consent_record(consent: ConsentimientoORM, patient: PatientORM | None, textos: dict | None = None) -> bytes:
    meta = (textos or {}).get(consent.tipo, {})
    titulo = meta.get("titulo", consent.tipo)
    return build_consent_pdf(
        titulo=titulo,
        texto=consent.texto_completo or "",
        version=consent.version_texto or "1.0",
        patient=patient,
        firmante=consent.nombre_firmante,
        documento_firmante=consent.documento_firmante,
        relacion=consent.relacion_firmante,
        fecha_firma=consent.fecha_firma,
        firma_base64=consent.firma_base64,
        borrador=False,
    )
