"""
app/presentation/api/v1/emails.py
===================================
Envío de correos con log de auditoría (A.6 + A.13).

POST /reports/{eval_id}/send-email
    Genera/adjunta el PDF del informe de esa evaluación y lo envía por SMTP.
    Registra el resultado en `email_logs`. Plantilla por tipo de documento.

GET  /emails/logs
    Lista los últimos envíos (admin). Filtro opcional por patient_id.

GET  /emails/status
    Reporta si SMTP está configurado (sin exponer credenciales).
"""
from __future__ import annotations

import logging
import re

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field, field_validator

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

from datetime import UTC

from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession, EvaluationRepo, PatientRepo

logger = logging.getLogger("neurosoft.emails")

# Usamos el mismo prefijo /reports para mantener la ergonomía del cliente
email_send_router = APIRouter(prefix="/reports", tags=["Informes PDF"])
email_logs_router = APIRouter(prefix="/emails", tags=["Emails"])


# ─────────────────────────────────────────────────────────────
# DTOs
# ─────────────────────────────────────────────────────────────
class SendEmailDTO(BaseModel):
    to: list[str] = Field(..., min_length=1, description="Destinatarios principales.")
    cc: list[str] | None = None
    bcc: list[str] | None = None
    tipo: str = Field(default="informe", description="informe | evolucion | remision | rips | otro")
    subject: str | None = Field(default=None, description="Si se omite, usa plantilla.")
    body: str | None = Field(default=None, description="Si se omite, usa plantilla.")
    include_pdf: bool = Field(default=True, description="Adjuntar PDF del informe.")

    @field_validator("to", "cc", "bcc")
    @classmethod
    def _validate_emails(cls, v):
        if v is None:
            return v
        for addr in v:
            if not _EMAIL_RE.match((addr or "").strip()):
                raise ValueError(f"Dirección de correo inválida: {addr!r}")
        return v


class SendEmailResponse(BaseModel):
    ok: bool
    log_id: str
    status: str
    error: str | None = None
    recipient_to: str = ""
    subject: str = ""


# ─────────────────────────────────────────────────────────────
# Utilidades compartidas
# ─────────────────────────────────────────────────────────────
def _format_fecha(d) -> str:
    try:
        return d.strftime("%d/%m/%Y")
    except Exception:  # noqa: BLE001
        return str(d) if d else ""


def _build_ctx_from_eval(db, eval_id: str):
    from app.infrastructure.database.orm_models import (
        ConfigInstitucionORM,
        EvaluationORM,
        PatientORM,
        ProfessionalORM,
    )
    from app.infrastructure.email_service import TemplateContext

    ev = db.get(EvaluationORM, eval_id)
    if ev is None:
        raise HTTPException(404, detail=f"Evaluación '{eval_id}' no encontrada.")
    pat = db.get(PatientORM, ev.patient_id)
    if pat is None:
        raise HTTPException(404, detail="Paciente no encontrado.")
    prof = db.get(ProfessionalORM, pat.profesional_id) if pat.profesional_id else None
    inst = db.query(ConfigInstitucionORM).first()

    nombre = " ".join(x for x in [
        pat.primer_nombre or "", pat.segundo_nombre or "",
        pat.primer_apellido or "", pat.segundo_apellido or "",
    ] if x).strip()

    ctx = TemplateContext(
        patient_nombre=nombre or "(paciente)",
        patient_doc=pat.numero_documento or "",
        fecha=_format_fecha(ev.fecha or pat.fecha_atencion),
        profesional=(prof.nombre_completo if prof else "") or "",
        institucion=(inst.nombre if inst else "") or "Consultorio Neuropsicológico",
    )
    return ev, pat, prof, inst, ctx


# ─────────────────────────────────────────────────────────────
# Endpoints
# ─────────────────────────────────────────────────────────────
@email_send_router.post(
    "/{eval_id}/send-email",
    response_model=SendEmailResponse,
    summary="Enviar informe de evaluación por correo (con log)",
    description=(
        "Genera el PDF del informe (si `include_pdf=True`) y lo envía por SMTP.\n\n"
        "Registra el resultado en `email_logs` (éxito o fallo). Las plantillas "
        "de asunto y cuerpo se resuelven según `tipo`, a menos que se pasen "
        "campos explícitos. Requiere `NEUROSOFT_SMTP_*` configurado."
    ),
)
def send_report_email(
    eval_id: str,
    dto: SendEmailDTO,
    request: Request,
    db: DbSession,
    eval_repo: EvaluationRepo,
    patient_repo: PatientRepo,
):
    from app.infrastructure.email_service import (
        DEFAULT_TEMPLATES,
        Attachment,
        render_template,
        send_email,
    )

    ev, pat, prof, inst, ctx = _build_ctx_from_eval(db, eval_id)

    # §QW-3: usar plantilla custom de BD si existe; fallback a DEFAULT_TEMPLATES
    from app.infrastructure.database.orm_models import ConfigEmailTemplateORM
    custom = db.query(ConfigEmailTemplateORM).filter_by(tipo=dto.tipo, activo=True).first()
    if custom is not None:
        tpl_subject = custom.subject or DEFAULT_TEMPLATES.get(dto.tipo, DEFAULT_TEMPLATES["otro"])["subject"]
        tpl_body = custom.body or DEFAULT_TEMPLATES.get(dto.tipo, DEFAULT_TEMPLATES["otro"])["body"]
    else:
        tpl = DEFAULT_TEMPLATES.get(dto.tipo, DEFAULT_TEMPLATES["otro"])
        tpl_subject = tpl["subject"]
        tpl_body = tpl["body"]
    subject = dto.subject or render_template(tpl_subject, ctx)
    body = dto.body or render_template(tpl_body, ctx)

    attachments: list[Attachment] = []
    if dto.include_pdf:
        try:
            from app.infrastructure.database.orm_models import ClinicalHistoryORM
            from app.infrastructure.report_service import (
                build_report_data_from_db,
                generate_report_pdf,
            )

            ev_domain = eval_repo.find_by_id(eval_id)

            hc = (
                db.query(ClinicalHistoryORM)
                .filter(ClinicalHistoryORM.patient_id == ev.patient_id)
                .order_by(ClinicalHistoryORM.fecha_atencion.desc())
                .first()
            )
            report_data = build_report_data_from_db(
                patient=pat,
                clinical_history=hc,
                evaluation_record=ev_domain,
                institucion=inst,
                profesional=prof,
            )
            pdf_bytes = generate_report_pdf(report_data)
            fname = (
                f"InformeNPS_{(pat.primer_apellido or '').strip()}"
                f"_{pat.numero_documento}.pdf"
            ).replace(" ", "_")
            attachments.append(Attachment(
                filename=fname, content=pdf_bytes, mime_type="application/pdf",
            ))
        except Exception as e:  # noqa: BLE001
            logger.warning("No se pudo adjuntar PDF (%s). Envío continúa sin adjunto.", e)

    result = send_email(
        db,
        to=[str(a) for a in dto.to],
        cc=[str(a) for a in (dto.cc or [])],
        bcc=[str(a) for a in (dto.bcc or [])],
        subject=subject,
        body=body,
        attachments=attachments,
        tipo=dto.tipo,
        patient_id=pat.id,
        evaluation_id=eval_id,
        actor_id=getattr(request.state, "user_id", None),
        actor_label=getattr(request.state, "user_role", None),
    )

    # Auditoría a nivel sistema
    try:
        from app.infrastructure.audit import record_event
        record_event(
            db,
            action="send_email" if result.ok else "send_email_failed",
            entity_type="evaluation",
            entity_id=eval_id,
            actor_id=getattr(request.state, "user_id", None),
            summary=f"Email tipo={dto.tipo} to={result.recipient_to[:120]} status={result.status}",
            request=request,
        )
    except Exception:  # noqa: BLE001
        pass

    if not result.ok:
        # 502 para no confundir con error del cliente — SMTP es un upstream
        raise HTTPException(status_code=502, detail=result.as_dict())
    return result.as_dict()


@email_logs_router.get(
    "",
    summary="Historial de envíos de correo",
    description="Lista los últimos envíos. Admin-only.",
)
def list_email_logs(
    db: DbSession,
    patient_id: str | None = Query(default=None),
    status: str | None = Query(default=None, description="sent | failed"),
    limit: int = Query(default=100, ge=1, le=1000),
    admin=Depends(require_admin),
):
    from app.infrastructure.database.orm_models import EmailLogORM

    q = db.query(EmailLogORM)
    if patient_id:
        q = q.filter(EmailLogORM.patient_id == patient_id)
    if status:
        q = q.filter(EmailLogORM.status == status)
    q = q.order_by(EmailLogORM.ts.desc()).limit(limit)
    out = []
    for r in q.all():
        out.append({
            "id": r.id,
            "ts": r.ts.isoformat() if r.ts else None,
            "actor_id": r.actor_id,
            "actor_label": r.actor_label,
            "patient_id": r.patient_id,
            "evaluation_id": r.evaluation_id,
            "tipo": r.tipo,
            "recipient_to": r.recipient_to,
            "recipient_cc": r.recipient_cc,
            "subject": r.subject,
            "status": r.status,
            "error_message": r.error_message,
        })
    return out


@email_logs_router.get(
    "/status",
    summary="Estado de configuración SMTP",
    description="Informa si SMTP está configurado. NO expone credenciales.",
)
def smtp_status(db: DbSession):
    """§QW-2: usa config efectiva (BD si hay override, env vars si no)."""
    from app.infrastructure.email_service import get_effective_smtp_config, is_configured

    cfg = get_effective_smtp_config(db)
    return {
        "configured": is_configured(db),
        "source": cfg["source"],  # 'db' | 'env' | 'none'
        "host": cfg["host"] or None,
        "port": cfg["port"],
        "user_set": bool(cfg["user"]),
        "password_set": bool(cfg["password"]),
        "use_tls": cfg["use_tls"],
        "use_ssl": cfg["use_ssl"],
        "from": cfg["from_addr"] or cfg["user"] or None,
        "from_name": cfg["from_name"],
    }


# ═══════════════════════════════════════════════════════════════════════
# §QW-2: Configuración SMTP editable desde UI (admin)
# ═══════════════════════════════════════════════════════════════════════

smtp_config_router = APIRouter(prefix="/config", tags=["Config"], dependencies=[Depends(require_admin)])


class SmtpConfigDTO(BaseModel):
    host: str = Field(default="", max_length=120)
    port: int = Field(default=587, ge=1, le=65535)
    user: str = Field(default="", max_length=120)
    password: str | None = Field(default=None, description="Solo si se quiere cambiar; vacío = mantener.")
    from_addr: str = Field(default="", max_length=120)
    from_name: str = Field(default="NeuroSoft", max_length=120)
    use_tls: bool = True
    use_ssl: bool = False
    timeout_s: int = Field(default=30, ge=5, le=300)
    activo: bool = True


@smtp_config_router.get("/smtp", summary="Obtener configuración SMTP (sin password)")
def get_smtp_config(db: DbSession):
    from app.infrastructure.database.orm_models import ConfigSmtpORM
    row = db.get(ConfigSmtpORM, "1")
    if row is None:
        # Devolver defaults desde env (para que UI muestre algo)
        from app.core.config import settings
        return {
            "host": settings.smtp_host or "",
            "port": settings.smtp_port or 587,
            "user": settings.smtp_user or "",
            "password_set": bool(settings.smtp_password),
            "from_addr": settings.smtp_from or "",
            "from_name": settings.smtp_from_name or "NeuroSoft",
            "use_tls": settings.smtp_use_tls,
            "use_ssl": settings.smtp_use_ssl,
            "timeout_s": settings.smtp_timeout or 30,
            "activo": False,
            "source": "env" if settings.smtp_host else "none",
            "ultima_prueba": None,
            "ultima_prueba_ok": None,
            "ultima_prueba_msg": None,
        }
    return {
        "host": row.host or "",
        "port": row.port or 587,
        "user": row.user or "",
        "password_set": bool(row.password_enc),
        "from_addr": row.from_addr or "",
        "from_name": row.from_name or "NeuroSoft",
        "use_tls": bool(row.use_tls),
        "use_ssl": bool(row.use_ssl),
        "timeout_s": row.timeout_s or 30,
        "activo": bool(row.activo),
        "source": "db",
        "ultima_prueba": row.ultima_prueba.isoformat() if row.ultima_prueba else None,
        "ultima_prueba_ok": row.ultima_prueba_ok,
        "ultima_prueba_msg": row.ultima_prueba_msg,
    }


@smtp_config_router.put("/smtp", summary="Guardar configuración SMTP")
def put_smtp_config(dto: SmtpConfigDTO, db: DbSession):
    from app.infrastructure.crypto import encrypt
    from app.infrastructure.database.orm_models import ConfigSmtpORM

    row = db.get(ConfigSmtpORM, "1")
    if row is None:
        row = ConfigSmtpORM(id="1")
        db.add(row)

    row.host = dto.host.strip()
    row.port = dto.port
    row.user = dto.user.strip()
    # Password: solo se actualiza si se envió (None = mantener actual)
    if dto.password is not None:
        if dto.password == "":
            row.password_enc = None  # explícitamente borrar
        else:
            row.password_enc = encrypt(dto.password)
    row.from_addr = (dto.from_addr or "").strip()
    row.from_name = (dto.from_name or "NeuroSoft").strip()
    row.use_tls = dto.use_tls
    row.use_ssl = dto.use_ssl
    row.timeout_s = dto.timeout_s
    row.activo = dto.activo
    db.commit()
    return {"ok": True}


class SmtpTestDTO(BaseModel):
    to: str = Field(..., description="Email destinatario para la prueba.")


@smtp_config_router.post("/smtp/test", summary="Enviar email de prueba")
def test_smtp_config(dto: SmtpTestDTO, db: DbSession, request: Request):
    """Envía un correo de prueba. Registra resultado en BD."""
    from datetime import datetime

    from app.infrastructure.database.orm_models import ConfigSmtpORM
    from app.infrastructure.email_service import send_email

    to = (dto.to or "").strip()
    if not _EMAIL_RE.match(to):
        raise HTTPException(400, detail=f"Email inválido: {to!r}")

    result = send_email(
        db,
        to=[to],
        subject="Prueba de configuración SMTP — NeuroSoft App",
        body=(
            "Este es un correo de prueba enviado desde NeuroSoft App.\n\n"
            "Si lo recibiste correctamente, la configuración SMTP está funcionando.\n\n"
            "Hora del envío (UTC): " + datetime.now(UTC).isoformat()
        ),
        tipo="otro",
        actor_id=getattr(request.state, "user_id", None),
        actor_label="prueba_smtp",
    )

    # Guardar resultado de la prueba en la fila SMTP
    try:
        row = db.get(ConfigSmtpORM, "1")
        if row is not None:
            row.ultima_prueba = datetime.now(UTC)
            row.ultima_prueba_ok = result.ok
            row.ultima_prueba_msg = (result.error or "OK")[:480]
            db.commit()
    except Exception:  # noqa: BLE001
        db.rollback()

    if not result.ok:
        raise HTTPException(status_code=502, detail=result.as_dict())
    return {"ok": True, "to": to, "log_id": result.log_id}


# ═══════════════════════════════════════════════════════════════════════
# §QW-3: Plantillas de email editables (admin)
# ═══════════════════════════════════════════════════════════════════════

email_tpl_router = APIRouter(prefix="/config", tags=["Config"], dependencies=[Depends(require_admin)])

_TIPOS_VALIDOS = ("informe", "remision", "evolucion", "rips", "recordatorio", "otro")


class EmailTemplateDTO(BaseModel):
    tipo: str = Field(..., description="informe | remision | evolucion | rips | otro")
    subject: str = Field(default="", max_length=400)
    body: str = Field(default="")
    activo: bool = True

    @field_validator("tipo")
    @classmethod
    def _validate_tipo(cls, v):
        if v not in _TIPOS_VALIDOS:
            raise ValueError(f"tipo debe ser uno de: {', '.join(_TIPOS_VALIDOS)}")
        return v


@email_tpl_router.get("/email-templates", summary="Listar plantillas de email")
def list_email_templates(db: DbSession):
    """Devuelve todas las plantillas (default si no hay override en BD)."""
    from app.infrastructure.database.orm_models import ConfigEmailTemplateORM
    from app.infrastructure.email_service import DEFAULT_TEMPLATES

    rows = {r.tipo: r for r in db.query(ConfigEmailTemplateORM).all()}
    out = []
    for tipo in _TIPOS_VALIDOS:
        row = rows.get(tipo)
        default = DEFAULT_TEMPLATES.get(tipo, DEFAULT_TEMPLATES["otro"])
        out.append({
            "tipo": tipo,
            "subject": row.subject if row else default["subject"],
            "body": row.body if row else default["body"],
            "activo": bool(row.activo) if row else True,
            "default_subject": default["subject"],
            "default_body": default["body"],
            "source": "db" if row else "default",
            "updated_at": row.updated_at.isoformat() if row and row.updated_at else None,
        })
    return out


@email_tpl_router.put("/email-templates/{tipo}", summary="Guardar plantilla de email")
def put_email_template(tipo: str, dto: EmailTemplateDTO, db: DbSession):
    if tipo != dto.tipo:
        raise HTTPException(400, detail="El tipo del path y del body no coinciden")
    import uuid

    from app.infrastructure.database.orm_models import ConfigEmailTemplateORM

    row = db.query(ConfigEmailTemplateORM).filter_by(tipo=tipo).first()
    if row is None:
        row = ConfigEmailTemplateORM(id=str(uuid.uuid4())[:10], tipo=tipo)
        db.add(row)
    row.subject = dto.subject
    row.body = dto.body
    row.activo = dto.activo
    db.commit()
    return {"ok": True}


@email_tpl_router.delete("/email-templates/{tipo}", summary="Restaurar plantilla default (borrar override)")
def delete_email_template(tipo: str, db: DbSession):
    from app.infrastructure.database.orm_models import ConfigEmailTemplateORM
    row = db.query(ConfigEmailTemplateORM).filter_by(tipo=tipo).first()
    if row is not None:
        db.delete(row)
        db.commit()
    return {"ok": True}
