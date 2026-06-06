"""
app/presentation/api/v1/consentimientos.py
===========================================
Gestión de consentimientos firmados por el paciente.

Soporta cumplimiento de:
- Ley 1581/2012 (Habeas Data / Protección de Datos Personales).
- Consentimiento informado para evaluación neuropsicológica.
- Decreto 1377/2013 (Reglamentación habeas data).

Endpoints:
    GET    /consentimientos/textos           → textos vigentes por tipo
    POST   /consentimientos/                 → registrar firma
    GET    /consentimientos/                 → listar (filtro paciente/tipo)
    GET    /consentimientos/pendientes/{pid} → tipos que faltan firmar
    PATCH  /consentimientos/{id}/revocar     → revocar consentimiento
"""

from __future__ import annotations

import re
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel, Field, field_validator

from app.infrastructure.consent_pdf import build_consent_pdf, pdf_from_consent_record
from app.infrastructure.database.orm_models import ConsentimientoORM, PatientORM
from app.infrastructure.email_service import Attachment, is_configured, send_email
from app.presentation.dependencies import DbSession

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

consentimientos_router = APIRouter(prefix="/consentimientos", tags=["Consentimientos"])


# ─────────────────────────────────────────────────────────────
# Textos vigentes (versión 1.0 — editables desde aquí)
# ─────────────────────────────────────────────────────────────

TIPOS_VALIDOS = ("habeas_data", "evaluacion", "tratamiento", "telepsicologia")

TEXTOS_VIGENTES = {
    "habeas_data": {
        "version": "1.0",
        "titulo": "Autorización de Tratamiento de Datos Personales (Ley 1581 de 2012)",
        "texto": (
            "En cumplimiento de la Ley 1581 de 2012, el Decreto 1377 de 2013 y demás normas "
            "concordantes sobre protección de datos personales, autorizo de manera previa, "
            "expresa e informada a la IPS/profesional tratante para recolectar, almacenar, "
            "usar, circular y actualizar mis datos personales — incluyendo datos sensibles "
            "de salud — con las siguientes finalidades:\n\n"
            "1. Registro de historia clínica y atención en salud.\n"
            "2. Prestación de servicios de evaluación e intervención neuropsicológica.\n"
            "3. Emisión de informes, certificados y documentos requeridos.\n"
            "4. Facturación y reporte a entidades pagadoras (EPS, ARL, aseguradoras).\n"
            "5. Cumplimiento de obligaciones legales y reporte a autoridades sanitarias "
            "(RIPS, SIVIGILA, auditorías de calidad).\n"
            "6. Contacto para confirmación de citas, seguimiento y comunicación clínica.\n\n"
            "Conozco que mis datos serán tratados conforme a la Política de Tratamiento de Datos "
            "del prestador y que tengo derecho a conocer, actualizar, rectificar, suprimir mis "
            "datos o revocar esta autorización en cualquier momento, salvo cuando exista un deber "
            "legal o contractual que lo impida.\n\n"
            "Declaro haber leído y comprendido la presente autorización."
        ),
    },
    "evaluacion": {
        "version": "1.0",
        "titulo": "Consentimiento Informado — Evaluación Neuropsicológica",
        "texto": (
            "He sido informado(a) sobre la naturaleza, objetivos, procedimientos, duración "
            "aproximada, riesgos y beneficios de la evaluación neuropsicológica a la que voy "
            "a ser sometido(a).\n\n"
            "Entiendo que:\n"
            "• La evaluación consiste en pruebas estandarizadas que valoran funciones cognitivas "
            "(atención, memoria, lenguaje, funciones ejecutivas, habilidades visoespaciales, entre "
            "otras).\n"
            "• Los resultados serán interpretados a la luz de mi historia clínica y motivo de "
            "consulta.\n"
            "• La información y resultados son confidenciales y se rigen por secreto profesional, "
            "salvo las excepciones previstas por la ley.\n"
            "• Puedo formular preguntas, suspender la evaluación en cualquier momento y retirar este "
            "consentimiento sin perjuicio para la atención posterior.\n"
            "• El informe resultante se entregará al solicitante legítimo (yo, mi representante, "
            "médico tratante u otra entidad a la que expresamente autorice).\n\n"
            "Acepto voluntariamente someterme a la evaluación neuropsicológica en las condiciones "
            "descritas."
        ),
    },
    "tratamiento": {
        "version": "1.0",
        "titulo": "Consentimiento Informado — Intervención / Rehabilitación Neuropsicológica",
        "texto": (
            "He sido informado(a) del plan de intervención neuropsicológica, sus objetivos, "
            "frecuencia, duración estimada, alternativas terapéuticas, riesgos y beneficios "
            "esperados. Entiendo que la respuesta al tratamiento es individual y que no puede "
            "garantizarse un resultado específico.\n\n"
            "Autorizo voluntariamente el inicio del proceso terapéutico y me comprometo a "
            "asistir y colaborar según las indicaciones profesionales. Podré suspender el "
            "tratamiento en cualquier momento sin perjuicio para mi atención."
        ),
    },
    "telepsicologia": {
        "version": "1.0",
        "titulo": "Consentimiento — Atención Remota (Telepsicología)",
        "texto": (
            "Acepto recibir atención mediante videoconferencia u otro medio remoto seguro. "
            "Entiendo las limitaciones propias de la atención no presencial (dependencia de "
            "conectividad, imposibilidad de ciertos exámenes físicos y pruebas que requieren "
            "materiales manipulables) y acepto que se usen plataformas que cumplan con "
            "estándares de privacidad."
        ),
    },
}


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────


class TextoDTO(BaseModel):
    tipo: str
    version: str
    titulo: str
    texto: str


class FirmarDTO(BaseModel):
    patient_id: str
    tipo: str
    aceptado: bool = True
    firma_base64: str | None = None
    nombre_firmante: str | None = None
    relacion_firmante: str = "paciente"  # paciente | tutor | representante
    documento_firmante: str | None = None
    dispositivo: str | None = None
    profesional_id: str | None = None


class RevocarDTO(BaseModel):
    motivo: str | None = None


class ConsentimientoResponseDTO(BaseModel):
    id: str
    patient_id: str
    tipo: str
    version_texto: str
    aceptado: bool
    firma_base64: str | None = None
    nombre_firmante: str | None = None
    relacion_firmante: str | None = None
    documento_firmante: str | None = None
    fecha_firma: datetime
    fecha_revocado: datetime | None = None
    motivo_revocado: str | None = None
    vigente: bool


class PendientesDTO(BaseModel):
    patient_id: str
    pendientes: list[str]
    firmados: list[str]


class EnviarConsentimientoDTO(BaseModel):
    patient_id: str
    tipo: str
    to: list[str] = Field(..., min_length=1)
    consentimiento_id: str | None = None  # None = plantilla; id = copia firmada

    @field_validator("to")
    @classmethod
    def _validate_emails(cls, v):
        for addr in v:
            if not _EMAIL_RE.match((addr or "").strip()):
                raise ValueError(f"Correo inválido: {addr!r}")
        return v


class EnviarConsentimientoResponse(BaseModel):
    ok: bool
    log_id: str | None = None
    error: str | None = None


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────


def _to_dto(orm: ConsentimientoORM) -> ConsentimientoResponseDTO:
    return ConsentimientoResponseDTO(
        id=orm.id,
        patient_id=orm.patient_id,
        tipo=orm.tipo,
        version_texto=orm.version_texto or "1.0",
        aceptado=bool(orm.aceptado),
        firma_base64=orm.firma_base64,
        nombre_firmante=orm.nombre_firmante,
        relacion_firmante=orm.relacion_firmante,
        documento_firmante=orm.documento_firmante,
        fecha_firma=orm.fecha_firma,
        fecha_revocado=orm.fecha_revocado,
        motivo_revocado=orm.motivo_revocado,
        vigente=bool(orm.aceptado) and orm.fecha_revocado is None,
    )


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────


@consentimientos_router.get("/textos", response_model=list[TextoDTO])
def textos_vigentes():
    """Devuelve los textos vigentes de todos los tipos de consentimiento."""
    return [TextoDTO(tipo=k, **v) for k, v in TEXTOS_VIGENTES.items()]


@consentimientos_router.get("/textos/{tipo}", response_model=TextoDTO)
def texto_por_tipo(tipo: str):
    if tipo not in TEXTOS_VIGENTES:
        raise HTTPException(404, f"Tipo desconocido. Válidos: {TIPOS_VALIDOS}")
    return TextoDTO(tipo=tipo, **TEXTOS_VIGENTES[tipo])


@consentimientos_router.post("/", response_model=ConsentimientoResponseDTO, status_code=201)
def firmar_consentimiento(dto: FirmarDTO, db: DbSession, request: Request):
    if dto.tipo not in TIPOS_VALIDOS:
        raise HTTPException(422, f"Tipo inválido. Válidos: {TIPOS_VALIDOS}")
    pat = db.query(PatientORM).filter_by(id=dto.patient_id).first()
    if not pat:
        raise HTTPException(404, "Paciente no encontrado")
    texto = TEXTOS_VIGENTES[dto.tipo]

    ip = request.client.host if request.client else None
    ua = request.headers.get("user-agent", "")[:400] if request else None

    orm = ConsentimientoORM(
        id=str(uuid.uuid4()),
        patient_id=dto.patient_id,
        profesional_id=dto.profesional_id,
        tipo=dto.tipo,
        version_texto=texto["version"],
        texto_completo=texto["texto"],
        aceptado=bool(dto.aceptado),
        firma_base64=dto.firma_base64,
        nombre_firmante=dto.nombre_firmante or " ".join(filter(None, [pat.primer_nombre, pat.primer_apellido])),
        relacion_firmante=dto.relacion_firmante,
        documento_firmante=dto.documento_firmante or pat.numero_documento,
        ip_registro=ip,
        dispositivo=dto.dispositivo or ua,
        fecha_firma=datetime.now(UTC),
    )
    db.add(orm)
    db.commit()
    db.refresh(orm)
    return _to_dto(orm)


@consentimientos_router.get("/", response_model=list[ConsentimientoResponseDTO])
def listar_consentimientos(
    db: DbSession,
    patient_id: str | None = None,
    tipo: str | None = None,
    solo_vigentes: bool = False,
):
    q = db.query(ConsentimientoORM)
    if patient_id:
        q = q.filter(ConsentimientoORM.patient_id == patient_id)
    if tipo:
        q = q.filter(ConsentimientoORM.tipo == tipo)
    q = q.order_by(ConsentimientoORM.fecha_firma.desc())
    items = q.all()
    if solo_vigentes:
        items = [i for i in items if i.aceptado and i.fecha_revocado is None]
    return [_to_dto(i) for i in items]


@consentimientos_router.get("/pendientes/{patient_id}", response_model=PendientesDTO)
def pendientes_paciente(patient_id: str, db: DbSession):
    """Devuelve los tipos de consentimiento que aún no tiene firmados vigentes el paciente."""
    pat = db.query(PatientORM).filter_by(id=patient_id).first()
    if not pat:
        raise HTTPException(404, "Paciente no encontrado")
    firmados_vigentes = {
        c.tipo
        for c in db.query(ConsentimientoORM).filter_by(patient_id=patient_id, aceptado=True).all()
        if c.fecha_revocado is None
    }
    # habeas_data y evaluacion son obligatorios para poder registrar HC/evaluación
    obligatorios = {"habeas_data", "evaluacion"}
    pendientes = sorted(obligatorios - firmados_vigentes)
    return PendientesDTO(
        patient_id=patient_id,
        pendientes=pendientes,
        firmados=sorted(firmados_vigentes),
    )


@consentimientos_router.get("/pdf/plantilla/{tipo}")
def pdf_plantilla_consentimiento(tipo: str, patient_id: str, db: DbSession):
    """PDF imprimible del texto vigente (sin firma) para firma presencial."""
    if tipo not in TEXTOS_VIGENTES:
        raise HTTPException(404, f"Tipo desconocido. Válidos: {TIPOS_VALIDOS}")
    pat = db.query(PatientORM).filter_by(id=patient_id).first()
    if not pat:
        raise HTTPException(404, "Paciente no encontrado")
    meta = TEXTOS_VIGENTES[tipo]
    pdf = build_consent_pdf(
        titulo=meta["titulo"],
        texto=meta["texto"],
        version=meta["version"],
        patient=pat,
        borrador=True,
    )
    fname = f"consentimiento_{tipo}_{pat.numero_documento or 'paciente'}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{fname}"'},
    )


@consentimientos_router.get("/{item_id}/pdf")
def pdf_consentimiento_firmado(item_id: str, db: DbSession):
    """PDF del consentimiento ya firmado (incluye firma si existe)."""
    orm = db.query(ConsentimientoORM).filter_by(id=item_id).first()
    if not orm:
        raise HTTPException(404, "Consentimiento no encontrado")
    pat = db.query(PatientORM).filter_by(id=orm.patient_id).first()
    pdf = pdf_from_consent_record(orm, pat, TEXTOS_VIGENTES)
    fname = f"consentimiento_firmado_{orm.tipo}_{item_id[:8]}.pdf"
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'inline; filename="{fname}"'},
    )


@consentimientos_router.post("/enviar-email", response_model=EnviarConsentimientoResponse)
def enviar_consentimiento_email(dto: EnviarConsentimientoDTO, db: DbSession):
    """
    Envía el consentimiento por correo (plantilla o copia firmada).
    Requiere SMTP configurado en Ajustes → Comunicaciones.
    """
    if dto.tipo not in TEXTOS_VIGENTES:
        raise HTTPException(422, f"Tipo inválido. Válidos: {TIPOS_VALIDOS}")
    pat = db.query(PatientORM).filter_by(id=dto.patient_id).first()
    if not pat:
        raise HTTPException(404, "Paciente no encontrado")
    if not is_configured(db):
        raise HTTPException(503, "SMTP no configurado. Vaya a Ajustes → Comunicaciones.")

    nombre = " ".join(filter(None, [pat.primer_nombre, pat.primer_apellido]))
    if dto.consentimiento_id:
        orm = db.query(ConsentimientoORM).filter_by(id=dto.consentimiento_id).first()
        if not orm or orm.patient_id != dto.patient_id:
            raise HTTPException(404, "Consentimiento no encontrado")
        meta_titulo = TEXTOS_VIGENTES.get(orm.tipo, {}).get("titulo", orm.tipo)
        pdf = pdf_from_consent_record(orm, pat, TEXTOS_VIGENTES)
        subject = f"Copia firmada — {meta_titulo} — {nombre}"
        body = (
            f"Adjunto encontrará la copia del consentimiento informado firmado "
            f"para {nombre} (doc. {pat.numero_documento}).\n\n"
            "Conserve este documento para su expediente.\n\n"
            "— NeuroSoft"
        )
        fname = f"consentimiento_firmado_{orm.tipo}.pdf"
    else:
        meta = TEXTOS_VIGENTES[dto.tipo]
        pdf = build_consent_pdf(
            titulo=meta["titulo"],
            texto=meta["texto"],
            version=meta["version"],
            patient=pat,
            borrador=True,
        )
        subject = f"Consentimiento informado — {meta['titulo']} — {nombre}"
        body = (
            f"Adjunto el documento de consentimiento para revisión y firma "
            f"de {nombre}.\n\n"
            "Puede imprimirlo y firmarlo en consultorio, o firmarlo digitalmente "
            "desde NeuroSoft (Historia Clínica → Consentimientos).\n\n"
            "— NeuroSoft"
        )
        fname = f"consentimiento_{dto.tipo}.pdf"

    result = send_email(
        db,
        to=dto.to,
        subject=subject,
        body=body,
        attachments=[Attachment(filename=fname, content=pdf, mime_type="application/pdf")],
        tipo="consentimiento",
        patient_id=dto.patient_id,
        documento_id=dto.consentimiento_id,
    )
    return EnviarConsentimientoResponse(ok=result.ok, log_id=result.log_id, error=result.error)


@consentimientos_router.patch("/{item_id}/revocar", response_model=ConsentimientoResponseDTO)
def revocar_consentimiento(item_id: str, dto: RevocarDTO, db: DbSession):
    orm = db.query(ConsentimientoORM).filter_by(id=item_id).first()
    if not orm:
        raise HTTPException(404, "Consentimiento no encontrado")
    if orm.fecha_revocado is not None:
        raise HTTPException(400, "El consentimiento ya se encuentra revocado")
    orm.fecha_revocado = datetime.now(UTC)
    orm.motivo_revocado = dto.motivo
    db.commit()
    db.refresh(orm)
    return _to_dto(orm)
