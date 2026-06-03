"""
app/infrastructure/rips_service.py
=====================================
Generador de Reporte RIPS para neuropsicología.

RIPS = Registro Individual de Prestación de Servicios de Salud
Resolución 3374 de 2000 — Ministerio de Salud Colombia

Genera el PDF de presentación al asegurador/EPS con:
  - CT: Datos de la transacción (prestador)
  - US: Usuarios atendidos
  - AC: Consultas externas
  - AT: Procedimientos (CUPS)

Dependencia: reportlab >= 4.0
"""

from __future__ import annotations

import io
import logging
from dataclasses import dataclass, field
from datetime import date, datetime

logger = logging.getLogger(__name__)

# Colores institucionales
AZUL      = (0.07, 0.28, 0.55)
AZUL_LITE = (0.18, 0.45, 0.71)
GRIS      = (0.94, 0.94, 0.94)
GRIS_T    = (0.25, 0.25, 0.25)
BLANCO    = (1, 1, 1)
NEGRO     = (0, 0, 0)


@dataclass
class RIPSData:
    """Datos para el reporte RIPS."""
    # Institución prestadora
    nombre_prestador:  str = ""
    nit_prestador:     str = ""
    codigo_habilitacion: str = ""
    ciudad:            str = "Bogotá"
    direccion:         str = ""
    telefono:          str = ""

    # Periodo
    fecha_inicio: date = field(default_factory=date.today)
    fecha_fin:    date = field(default_factory=date.today)

    # Profesional
    profesional_nombre:  str = ""
    profesional_registro: str = ""

    # Registros de atenciones
    atenciones: list[dict] = field(default_factory=list)
    # Cada atención: {
    #   tipo_doc, num_doc, nombre, fecha_nac, sexo,
    #   fecha_consulta, codigo_dx (CIE-10), dx_descripcion,
    #   cups, cups_descripcion, valor_copago
    # }


class RIPSGenerator:
    """Genera el reporte RIPS en PDF."""

    PAGE_W = 595.27
    PAGE_H = 841.89
    MARGIN = 36
    CW     = PAGE_W - 72   # content width

    def generate(self, data: RIPSData) -> bytes:
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
        except ImportError:
            raise RuntimeError("reportlab no instalado. pip install reportlab")

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        c.setTitle(f"RIPS {data.fecha_inicio} a {data.fecha_fin}")

        y = self._draw_header(c, data)
        y = self._draw_ct(c, data, y)
        y = self._draw_us_ac(c, data, y)
        self._draw_footer(c, data)

        c.save()
        buffer.seek(0)
        return buffer.getvalue()

    def _draw_header(self, c, data: RIPSData) -> float:
        # Banda azul
        c.setFillColorRGB(*AZUL)
        c.rect(0, self.PAGE_H - 65, self.PAGE_W, 65, fill=1, stroke=0)

        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 14)
        c.drawString(self.MARGIN, self.PAGE_H - 26,
                     "Registro Individual de Prestación de Servicios de Salud")
        c.setFont("Helvetica", 9)
        c.drawString(self.MARGIN, self.PAGE_H - 40, "RIPS — Resolución 3374/2000")
        c.drawString(self.MARGIN, self.PAGE_H - 52,
                     f"Período: {data.fecha_inicio.strftime('%d/%m/%Y')} "
                     f"al {data.fecha_fin.strftime('%d/%m/%Y')}")

        c.setFont("Helvetica-Bold", 8)
        c.drawRightString(self.PAGE_W - self.MARGIN, self.PAGE_H - 26,
                          f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
        return self.PAGE_H - 72

    def _section(self, c, title: str, y: float) -> float:
        c.setFillColorRGB(*AZUL_LITE)
        c.rect(self.MARGIN, y - 14, self.CW, 14, fill=1, stroke=0)
        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 8.5)
        c.drawString(self.MARGIN + 4, y - 10, title)
        return y - 16

    def _row(self, c, label: str, value: str, x: float, y: float, w: float = 120) -> float:
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColorRGB(*GRIS_T)
        c.drawString(x, y, label + ":")
        c.setFont("Helvetica", 7.5)
        c.drawString(x + w, y, str(value or "—")[:50])
        return y - 11

    def _draw_ct(self, c, data: RIPSData, y: float) -> float:
        """Tabla CT — datos del prestador."""
        y -= 8
        y = self._section(c, "CT — Datos del Prestador de Servicios de Salud", y)

        col_w = self.CW / 2
        pairs = [
            ("Nombre del prestador", data.nombre_prestador, self.MARGIN, y),
            ("NIT", data.nit_prestador, self.MARGIN + col_w, y),
        ]
        for lbl, val, x, yy in pairs:
            self._row(c, lbl, val, x, yy, 110)
        y -= 13

        pairs2 = [
            ("Código habilitación", data.codigo_habilitacion, self.MARGIN, y),
            ("Ciudad", data.ciudad, self.MARGIN + col_w, y),
        ]
        for lbl, val, x, yy in pairs2:
            self._row(c, lbl, val, x, yy, 110)
        y -= 13

        pairs3 = [
            ("Dirección", data.direccion, self.MARGIN, y),
            ("Teléfono", data.telefono, self.MARGIN + col_w, y),
        ]
        for lbl, val, x, yy in pairs3:
            self._row(c, lbl, val, x, yy, 110)
        y -= 13

        # Profesional
        pairs4 = [
            ("Profesional", data.profesional_nombre, self.MARGIN, y),
            ("Registro prof.", data.profesional_registro, self.MARGIN + col_w, y),
        ]
        for lbl, val, x, yy in pairs4:
            self._row(c, lbl, val, x, yy, 110)
        return y - 16

    def _draw_us_ac(self, c, data: RIPSData, y: float) -> float:
        """Tablas US (usuarios) y AC (consultas) combinadas."""
        y -= 4
        # Totales
        y = self._section(c, f"US / AC — Atenciones del Período  (Total: {len(data.atenciones)})", y)

        if not data.atenciones:
            c.setFont("Helvetica", 8)
            c.setFillColorRGB(*GRIS_T)
            c.drawString(self.MARGIN + 4, y - 12, "No hay atenciones registradas en el período.")
            return y - 30

        # Headers de la tabla
        cols = [
            (self.MARGIN,       60,  "Documento"),
            (self.MARGIN + 62,  100, "Paciente"),
            (self.MARGIN + 164, 45,  "F. Atención"),
            (self.MARGIN + 211, 35,  "Edad"),
            (self.MARGIN + 248, 40,  "CIE-10"),
            (self.MARGIN + 290, 90,  "Diagnóstico"),
            (self.MARGIN + 382, 50,  "CUPS"),
            (self.MARGIN + 434, 50,  "Copago"),
        ]
        row_h = 12

        c.setFillColorRGB(*AZUL)
        c.rect(self.MARGIN, y - row_h, self.CW, row_h, fill=1, stroke=0)
        c.setFillColorRGB(*BLANCO)
        c.setFont("Helvetica-Bold", 6.5)
        for cx, cw, lbl in cols:
            c.drawString(cx + 2, y - 9, lbl)
        y -= row_h

        for i, at in enumerate(data.atenciones):
            if y < 60:
                c.showPage()
                self._draw_footer(c, data)
                y = self.PAGE_H - self.MARGIN

            if i % 2 == 0:
                c.setFillColorRGB(0.95, 0.95, 0.95)
                c.rect(self.MARGIN, y - row_h + 1, self.CW, row_h - 1, fill=1, stroke=0)

            c.setFont("Helvetica", 6.5)
            c.setFillColorRGB(*GRIS_T)

            values = [
                f"{at.get('tipo_doc','')} {at.get('num_doc','')}",
                str(at.get('nombre', ''))[:22],
                str(at.get('fecha_consulta', '')),
                self._calc_age(at.get('fecha_nac'), at.get('fecha_consulta')),
                str(at.get('codigo_dx', '')),
                str(at.get('dx_descripcion', ''))[:20],
                str(at.get('cups', '')),
                f"${at.get('valor_copago', 0):,}",
            ]
            for (cx, cw, _), val in zip(cols, values):
                c.drawString(cx + 2, y - 8, val[:int(cw/4.3)])

            y -= row_h

        # Totales al final
        y -= 8
        total_copagos = sum(at.get('valor_copago', 0) for at in data.atenciones)
        c.setFont("Helvetica-Bold", 7.5)
        c.setFillColorRGB(*GRIS_T)
        c.drawRightString(self.PAGE_W - self.MARGIN, y,
                          f"Total atenciones: {len(data.atenciones)}   "
                          f"Total copagos: ${total_copagos:,}")
        return y - 16

    def _draw_footer(self, c, data: RIPSData) -> None:
        c.setFillColorRGB(0.6, 0.6, 0.6)
        c.setFont("Helvetica", 6)
        c.drawString(self.MARGIN, 18,
                     f"RIPS — {data.nombre_prestador}  |  "
                     f"NIT {data.nit_prestador}  |  "
                     f"Documento confidencial")

    @staticmethod
    def _calc_age(fecha_nac, fecha_ref) -> str:
        try:
            if isinstance(fecha_nac, str):
                from datetime import date
                fn = date.fromisoformat(fecha_nac)
            else:
                fn = fecha_nac
            if isinstance(fecha_ref, str):
                fr = date.fromisoformat(str(fecha_ref))
            else:
                fr = fecha_ref or date.today()
            years = fr.year - fn.year - ((fr.month, fr.day) < (fn.month, fn.day))
            return str(years)
        except Exception:
            return "—"


def generate_rips_pdf(data: RIPSData) -> bytes:
    return RIPSGenerator().generate(data)


# ═══════════════════════════════════════════════════════════════════════
# RIPS mensual por profesional — Resolución 2275/2023
# ═══════════════════════════════════════════════════════════════════════
"""
Formato texto plano (pipe-delimited) de la Resolución 2275/2023 Minsalud.
Generamos 3 archivos:

    CT.txt — transacción (cabecera del envío)
        NroFactura | CodPrestador | TipoNota | NumeroNota

    US.txt — usuarios atendidos (1 línea por paciente único)
        tipo_doc | num_doc | cod_entidad_admin | tipo_usuario |
        primer_apellido | segundo_apellido | primer_nombre | segundo_nombre |
        edad | unidad_edad | sexo | cod_depto | cod_municipio | zona_residencia

    AC.txt — consulta externa (1 línea por atención)
        NroFactura | CodPrestador | tipo_doc | num_doc | fecha_consulta |
        num_autoriza | cod_consulta_CUPS | finalidad_consulta | causa_externa |
        cod_dx_ppal | cod_dx_rel1 | cod_dx_rel2 | cod_dx_rel3 |
        tipo_dx_ppal | valor_consulta | valor_cuota_mod | valor_neto_pagar

Los campos faltantes se dejan vacíos (separador doble) salvo los obligatorios,
que se rellenan con placeholders conservadores.
"""
import zipfile as _zipfile


def _pipe(*fields) -> str:
    """Join de campos RIPS con el separador oficial '|'."""
    return "|".join("" if f is None else str(f) for f in fields)


def _calc_edad_anios(fn, fr) -> int:
    try:
        if isinstance(fn, str):
            fn = date.fromisoformat(fn)
        if isinstance(fr, str):
            fr = date.fromisoformat(fr)
        if not fn or not fr:
            return 0
        return fr.year - fn.year - ((fr.month, fr.day) < (fn.month, fn.day))
    except Exception:
        return 0


def generate_rips_monthly_txt(
    db,
    *,
    professional_id: str | None,
    desde: date,
    hasta: date,
    numero_factura: str = "SIN-FACTURA",
    codigo_prestador: str = "",
) -> dict[str, bytes]:
    """
    Genera dict {filename: bytes} con CT.txt, US.txt, AC.txt filtrando por
    profesional_id y rango de fechas (fecha_atencion del paciente y fecha
    de la evaluación, lo que incluye tanto consultas registradas como
    evaluaciones formalizadas).
    """
    from app.infrastructure.database.orm_models import (
        ConfigInstitucionORM,
        EvaluationORM,
        PatientORM,
    )

    inst = db.query(ConfigInstitucionORM).first()
    if not codigo_prestador and inst:
        codigo_prestador = (inst.nit or "")[:12] or "SIN-COD"

    # Consulta base: evaluaciones del rango
    q = (
        db.query(EvaluationORM, PatientORM)
        .join(PatientORM, PatientORM.id == EvaluationORM.patient_id)
        .filter(EvaluationORM.fecha >= desde, EvaluationORM.fecha <= hasta)
    )
    if professional_id:
        q = q.filter(PatientORM.profesional_id == professional_id)
    rows = q.order_by(EvaluationORM.fecha.asc()).all()

    # US.txt: paciente único (por documento)
    us_seen: set[str] = set()
    us_lines: list[str] = []
    ac_lines: list[str] = []

    for ev, pat in rows:
        tdoc = (pat.tipo_documento or "CC")[:2]
        ndoc = (pat.numero_documento or "")[:20]
        edad = _calc_edad_anios(pat.fecha_nacimiento, ev.fecha)
        # unidad de edad: 1=años, 2=meses, 3=días
        sexo = (pat.sexo or "M")[:1].upper()
        if sexo not in ("M", "F"):
            sexo = "M"
        key_us = f"{tdoc}|{ndoc}"
        if key_us not in us_seen:
            us_lines.append(_pipe(
                tdoc, ndoc,
                (pat.eps or "")[:6],        # cod_entidad_administradora (EPS)
                "01",                        # tipo_usuario (01=contributivo como default)
                (pat.primer_apellido or "")[:30],
                (pat.segundo_apellido or "")[:30],
                (pat.primer_nombre or "")[:20],
                (pat.segundo_nombre or "")[:20],
                edad,
                1,                           # unidad de edad = años
                sexo,
                "11",                        # cod_depto placeholder
                "001",                       # cod_municipio placeholder
                "U",                         # U=urbano, R=rural
            ))
            us_seen.add(key_us)

        # AC.txt: 1 línea por consulta/evaluación
        cie = (pat.codigo_rips or "F809")[:4]
        cups = (pat.cups or "890201")[:10]
        finalidad = (pat.finalidad_consulta or "10")[:2]
        ac_lines.append(_pipe(
            numero_factura,
            codigo_prestador,
            tdoc, ndoc,
            ev.fecha.strftime("%d/%m/%Y") if ev.fecha else "",
            (pat.orden_medica_no or "")[:15],   # numero_autorizacion
            cups,                                # cod_consulta CUPS
            finalidad,                           # finalidad
            "13",                                # causa externa (13=otra)
            cie,                                 # dx principal
            "", "", "",                          # dx relacionados 1/2/3
            "1",                                 # tipo dx ppal (1=impresion dx)
            0,                                   # valor consulta
            0,                                   # valor cuota moderadora
            0,                                   # valor neto a pagar
        ))

    # CT.txt: una línea de cabecera
    ct_lines = [
        _pipe(
            numero_factura,
            codigo_prestador,
            "",                                   # tipo_nota vacío
            "",                                   # numero_nota vacío
        ),
    ]

    def _as_bytes(lines: list[str]) -> bytes:
        return ("\r\n".join(lines) + "\r\n").encode("utf-8-sig")

    return {
        "CT.txt": _as_bytes(ct_lines),
        "US.txt": _as_bytes(us_lines),
        "AC.txt": _as_bytes(ac_lines),
    }


def generate_rips_monthly_zip(
    db,
    *,
    professional_id: str | None,
    desde: date,
    hasta: date,
    numero_factura: str = "SIN-FACTURA",
    codigo_prestador: str = "",
) -> bytes:
    """Empaqueta los 3 archivos en un ZIP binario en memoria."""
    files = generate_rips_monthly_txt(
        db,
        professional_id=professional_id,
        desde=desde,
        hasta=hasta,
        numero_factura=numero_factura,
        codigo_prestador=codigo_prestador,
    )
    buffer = io.BytesIO()
    with _zipfile.ZipFile(buffer, "w", _zipfile.ZIP_DEFLATED) as zf:
        for fname, fbytes in files.items():
            zf.writestr(fname, fbytes)
    buffer.seek(0)
    return buffer.getvalue()


def build_rips_data_from_db(
    patient_id: str,
    fecha_inicio: date,
    fecha_fin: date,
    db,
    profesional_id: str | None = None,
) -> RIPSData:
    """
    Construye un RIPSData consultando la BD.
    Busca todas las atenciones del paciente en el período.
    """

    from app.infrastructure.database.orm_models import (
        ConfigInstitucionORM,
        EvaluationORM,
        PatientORM,
        ProfessionalORM,
    )

    # Institución
    inst = db.query(ConfigInstitucionORM).first()

    # Paciente
    patient = db.get(PatientORM, patient_id)
    if patient is None:
        raise ValueError(f"Paciente {patient_id} no encontrado.")

    # Profesional
    prof = None
    if profesional_id:
        prof = db.get(ProfessionalORM, profesional_id)
    elif patient.profesional_id:
        prof = db.get(ProfessionalORM, patient.profesional_id)

    # Evaluaciones del período
    evaluaciones = (
        db.query(EvaluationORM)
        .filter(
            EvaluationORM.patient_id == patient_id,
            EvaluationORM.fecha >= fecha_inicio,
            EvaluationORM.fecha <= fecha_fin,
            EvaluationORM.is_latest.is_(True),
        )
        .order_by(EvaluationORM.fecha)
        .all()
    )

    def _get(obj, attr, default=""):
        return str(getattr(obj, attr, None) or default)

    nombre = " ".join(filter(None, [
        _get(patient, 'primer_nombre'),
        _get(patient, 'primer_apellido'),
    ]))

    atenciones = []
    for ev in evaluaciones:
        atenciones.append({
            "tipo_doc":       _get(patient, 'tipo_documento', 'CC'),
            "num_doc":        _get(patient, 'numero_documento'),
            "nombre":         nombre,
            "fecha_nac":      patient.fecha_nacimiento.isoformat() if patient.fecha_nacimiento else "",
            "sexo":           _get(patient, 'sexo'),
            "fecha_consulta": ev.fecha.isoformat() if ev.fecha else "",
            "codigo_dx":      _get(patient, 'codigo_rips', 'F809'),
            "dx_descripcion": "Evaluación Neuropsicológica",
            "cups":           _get(patient, 'cups', '890201'),
            "valor_copago":   0,
        })

    return RIPSData(
        nombre_prestador=_get(inst, 'nombre', 'Consultorio') if inst else 'Consultorio',
        nit_prestador=_get(inst, 'nit') if inst else '',
        codigo_habilitacion='',
        ciudad=_get(inst, 'ciudad', 'Bogotá') if inst else 'Bogotá',
        direccion=_get(inst, 'direccion') if inst else '',
        telefono=_get(inst, 'telefono') if inst else '',
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        profesional_nombre=_get(prof, 'nombre_completo') if prof else '',
        profesional_registro=_get(prof, 'registro_profesional') if prof else '',
        atenciones=atenciones,
    )
