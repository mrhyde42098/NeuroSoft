"""
app/infrastructure/email_service.py
=====================================
Servicio de envío de correos con registro (A.6 + A.13 del gap report).

Capabilities:
    • Conexión SMTP STARTTLS (Office 365, Gmail app-password) o SSL directo.
    • Plantillas por tipo de documento: informe | evolución | remisión.
    • Renderizado con Python `str.format()` usando placeholders seguros:
        {patient_nombre}, {patient_doc}, {fecha}, {profesional}, {institucion}
    • Adjuntos binarios (PDFs/DOCXs ya generados por reports_service).
    • Registro inmutable en `EmailLogORM` (éxito y fallo).
    • Nunca levanta excepciones no controladas al caller: devuelve SendResult.

Seguridad:
    - No envía si SMTP_HOST está vacío (feature-flag implícito).
    - No registra la contraseña SMTP en el log (solo host+user).
    - Trunca `body_preview` a 4000 chars para no saturar la BD.
"""

from __future__ import annotations

import json
import logging
import smtplib
import ssl
import uuid
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from typing import Any

from sqlalchemy.orm import Session

from app.core.config import settings

logger = logging.getLogger("neurosoft.email")


# ─────────────────────────────────────────────────────────────
# Plantillas por tipo de documento
# ─────────────────────────────────────────────────────────────
DEFAULT_TEMPLATES: dict[str, dict[str, str]] = {
    "informe": {
        "subject": "Informe de Evaluación Neuropsicológica — {patient_nombre}",
        "body": (
            "Estimado/a,\n\n"
            "Adjunto el informe de evaluación neuropsicológica correspondiente a "
            "{patient_nombre} (documento {patient_doc}), con fecha {fecha}.\n\n"
            "Este documento es confidencial y su uso se restringe al contexto clínico. "
            "Ante cualquier inquietud, puede contactarnos.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        ),
    },
    "evolucion": {
        "subject": "Evolución Terapéutica — {patient_nombre}",
        "body": (
            "Estimado/a,\n\n"
            "Adjunto la evolución terapéutica de {patient_nombre} "
            "(documento {patient_doc}), correspondiente a la sesión del {fecha}.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        ),
    },
    "remision": {
        "subject": "Remisión — {patient_nombre}",
        "body": (
            "Estimado/a colega,\n\n"
            "Adjunto documento de remisión de {patient_nombre} "
            "(documento {patient_doc}) con fecha {fecha}. Agradezco su atención.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        ),
    },
    "rips": {
        "subject": "RIPS — {patient_nombre}",
        "body": (
            "Estimado/a,\n\nAdjunto RIPS correspondiente a {patient_nombre} "
            "(documento {patient_doc}) con fecha {fecha}.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        ),
    },
    "recordatorio": {
        "subject": "Recordatorio de cita — {fecha} — {institucion}",
        "body": (
            "Estimado/a {patient_nombre},\n\n"
            "Le recordamos su cita programada para el {fecha} a las {hora}.\n\n"
            "Por favor confirme asistencia o reprograme respondiendo a este correo.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        ),
    },
    "otro": {
        "subject": "Documento clínico — {patient_nombre}",
        "body": (
            "Estimado/a,\n\nAdjunto documento clínico solicitado para "
            "{patient_nombre} (documento {patient_doc}), fecha {fecha}.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        ),
    },
}


@dataclass
class Attachment:
    filename: str
    content: bytes
    mime_type: str = "application/pdf"


@dataclass
class SendResult:
    ok: bool
    log_id: str
    status: str  # 'sent' | 'failed'
    error: str | None = None
    recipient_to: str = ""
    subject: str = ""

    def as_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "log_id": self.log_id,
            "status": self.status,
            "error": self.error,
            "recipient_to": self.recipient_to,
            "subject": self.subject,
        }


@dataclass
class TemplateContext:
    patient_nombre: str = ""
    patient_doc: str = ""
    fecha: str = ""
    profesional: str = ""
    institucion: str = ""

    def as_dict(self) -> dict[str, str]:
        return {
            "patient_nombre": self.patient_nombre,
            "patient_doc": self.patient_doc,
            "fecha": self.fecha,
            "profesional": self.profesional,
            "institucion": self.institucion,
        }


def render_template(tpl: str, ctx: TemplateContext) -> str:
    """Renderiza placeholders {xxx}. Tolerante: ignora keys faltantes."""

    class _SafeDict(dict):
        def __missing__(self, key):
            return "{" + key + "}"

    try:
        return tpl.format_map(_SafeDict(ctx.as_dict()))
    except Exception as e:  # noqa: BLE001
        logger.warning("Error renderizando plantilla: %s", e)
        return tpl


def get_effective_smtp_config(db=None) -> dict:
    """
    §QW-2: Devuelve la configuración SMTP "efectiva".

    Precedencia: BD (ConfigSmtpORM, fila activa) > env vars (settings.smtp_*).
    Las contraseñas en BD se almacenan cifradas con Fernet — se descifran aquí.

    Args:
        db: Session opcional. Si se pasa, se usa la fila de BD si existe.
            Si no se pasa, solo se devuelven los env vars.

    Returns:
        dict con keys: host, port, user, password, from_addr, from_name,
        use_tls, use_ssl, timeout, source ('db' | 'env' | 'none').
    """
    cfg = {
        "host": getattr(settings, "smtp_host", "") or "",
        "port": getattr(settings, "smtp_port", 587) or 587,
        "user": getattr(settings, "smtp_user", "") or "",
        "password": getattr(settings, "smtp_password", "") or "",
        "from_addr": getattr(settings, "smtp_from", "") or "",
        "from_name": getattr(settings, "smtp_from_name", "NeuroSoft") or "NeuroSoft",
        "use_tls": getattr(settings, "smtp_use_tls", True),
        "use_ssl": getattr(settings, "smtp_use_ssl", False),
        "timeout": getattr(settings, "smtp_timeout", 30),
        "source": "env" if (getattr(settings, "smtp_host", "")) else "none",
    }
    if db is not None:
        try:
            from app.infrastructure.crypto import decrypt
            from app.infrastructure.database.orm_models import ConfigSmtpORM

            row = db.get(ConfigSmtpORM, "1")
            if row is not None and row.activo and (row.host or "").strip():
                cfg["host"] = row.host or cfg["host"]
                cfg["port"] = row.port or cfg["port"]
                cfg["user"] = row.user or cfg["user"]
                # Decrypt only si hay password guardado
                dec = decrypt(row.password_enc) if row.password_enc else None
                if dec is not None:
                    cfg["password"] = dec
                cfg["from_addr"] = row.from_addr or cfg["from_addr"]
                cfg["from_name"] = row.from_name or cfg["from_name"]
                cfg["use_tls"] = bool(row.use_tls) if row.use_tls is not None else cfg["use_tls"]
                cfg["use_ssl"] = bool(row.use_ssl) if row.use_ssl is not None else cfg["use_ssl"]
                cfg["timeout"] = row.timeout_s or cfg["timeout"]
                cfg["source"] = "db"
        except Exception as e:  # noqa: BLE001
            logger.warning("No se pudo leer ConfigSmtpORM: %s", e)
    return cfg


def is_configured(db=None) -> bool:
    """True si hay SMTP mínimamente configurado para intentar envíos.

    §QW-2: ahora también acepta un Session para chequear si hay override en BD.
    """
    cfg = get_effective_smtp_config(db)
    return bool(cfg["host"]) and bool(cfg["user"])


# ─────────────────────────────────────────────────────────────
# Envío
# ─────────────────────────────────────────────────────────────
def send_email(
    db: Session,
    *,
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachments: list[Attachment] | None = None,
    tipo: str = "informe",
    patient_id: str | None = None,
    evaluation_id: str | None = None,
    documento_id: str | None = None,
    actor_id: str | None = None,
    actor_label: str | None = None,
) -> SendResult:
    """
    Envía correo con adjuntos y registra el resultado en `email_logs`.
    Nunca lanza — siempre retorna SendResult.
    """

    log_id = str(uuid.uuid4())
    to_clean = [a.strip() for a in (to or []) if a and a.strip()]
    cc_clean = [a.strip() for a in (cc or []) if a and a.strip()]
    bcc_clean = [a.strip() for a in (bcc or []) if a and a.strip()]

    if not to_clean:
        _persist_log(
            db,
            log_id=log_id,
            tipo=tipo,
            status="failed",
            error="Sin destinatarios",
            subject=subject,
            recipient_to="",
            recipient_cc=", ".join(cc_clean),
            recipient_bcc=", ".join(bcc_clean),
            body_preview=body,
            attachments=attachments or [],
            actor_id=actor_id,
            actor_label=actor_label,
            patient_id=patient_id,
            evaluation_id=evaluation_id,
            documento_id=documento_id,
        )
        return SendResult(ok=False, log_id=log_id, status="failed", error="Sin destinatarios", subject=subject)

    # §QW-2: usar config efectiva (BD si existe, env vars como fallback)
    cfg = get_effective_smtp_config(db)
    if not (cfg["host"] and cfg["user"]):
        msg = "SMTP no configurado (Ajustes → Comunicaciones, o NEUROSOFT_SMTP_*)."
        _persist_log(
            db,
            log_id=log_id,
            tipo=tipo,
            status="failed",
            error=msg,
            subject=subject,
            recipient_to=", ".join(to_clean),
            recipient_cc=", ".join(cc_clean),
            recipient_bcc=", ".join(bcc_clean),
            body_preview=body,
            attachments=attachments or [],
            actor_id=actor_id,
            actor_label=actor_label,
            patient_id=patient_id,
            evaluation_id=evaluation_id,
            documento_id=documento_id,
        )
        return SendResult(
            ok=False, log_id=log_id, status="failed", error=msg, recipient_to=", ".join(to_clean), subject=subject
        )

    # Construir mensaje
    msg = EmailMessage()
    from_addr = (cfg["from_addr"] or cfg["user"]).strip()
    from_name = (cfg["from_name"] or "NeuroSoft").strip()
    msg["From"] = formataddr((from_name, from_addr))
    msg["To"] = ", ".join(to_clean)
    if cc_clean:
        msg["Cc"] = ", ".join(cc_clean)
    msg["Subject"] = subject or "(sin asunto)"
    msg.set_content(body or "")

    for att in attachments or []:
        if att.content is None:
            continue
        maintype, _, subtype = (att.mime_type or "application/octet-stream").partition("/")
        msg.add_attachment(
            att.content,
            maintype=maintype or "application",
            subtype=subtype or "octet-stream",
            filename=att.filename or "attachment",
        )

    all_rcpts = to_clean + cc_clean + bcc_clean

    # §QW-2: Envío usa la config efectiva (BD o env)
    try:
        if cfg["use_ssl"]:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(
                cfg["host"],
                cfg["port"] or 465,
                timeout=cfg["timeout"],
                context=context,
            ) as s:
                s.login(cfg["user"], cfg["password"])
                s.send_message(msg, from_addr=from_addr, to_addrs=all_rcpts)
        else:
            with smtplib.SMTP(
                cfg["host"],
                cfg["port"] or 587,
                timeout=cfg["timeout"],
            ) as s:
                s.ehlo()
                if cfg["use_tls"]:
                    s.starttls(context=ssl.create_default_context())
                    s.ehlo()
                if cfg["password"]:
                    s.login(cfg["user"], cfg["password"])
                s.send_message(msg, from_addr=from_addr, to_addrs=all_rcpts)

        _persist_log(
            db,
            log_id=log_id,
            tipo=tipo,
            status="sent",
            error=None,
            subject=msg["Subject"],
            recipient_to=", ".join(to_clean),
            recipient_cc=", ".join(cc_clean),
            recipient_bcc=", ".join(bcc_clean),
            body_preview=body,
            attachments=attachments or [],
            actor_id=actor_id,
            actor_label=actor_label,
            patient_id=patient_id,
            evaluation_id=evaluation_id,
            documento_id=documento_id,
            smtp_host_override=cfg["host"],
            smtp_user_override=cfg["user"],
        )
        return SendResult(
            ok=True, log_id=log_id, status="sent", recipient_to=", ".join(to_clean), subject=msg["Subject"]
        )
    except Exception as e:  # noqa: BLE001
        logger.exception("Error enviando correo")
        _persist_log(
            db,
            log_id=log_id,
            tipo=tipo,
            status="failed",
            error=str(e)[:480],
            subject=msg["Subject"],
            recipient_to=", ".join(to_clean),
            recipient_cc=", ".join(cc_clean),
            recipient_bcc=", ".join(bcc_clean),
            body_preview=body,
            attachments=attachments or [],
            actor_id=actor_id,
            actor_label=actor_label,
            patient_id=patient_id,
            evaluation_id=evaluation_id,
            documento_id=documento_id,
        )
        return SendResult(
            ok=False,
            log_id=log_id,
            status="failed",
            error=str(e)[:480],
            recipient_to=", ".join(to_clean),
            subject=msg["Subject"],
        )


def _persist_log(
    db: Session,
    *,
    log_id: str,
    tipo: str,
    status: str,
    error: str | None,
    subject: str,
    recipient_to: str,
    recipient_cc: str,
    recipient_bcc: str,
    body_preview: str,
    attachments: list[Attachment],
    actor_id: str | None,
    actor_label: str | None,
    patient_id: str | None,
    evaluation_id: str | None,
    documento_id: str | None,
    smtp_host_override: str | None = None,
    smtp_user_override: str | None = None,
) -> None:
    from app.infrastructure.database.orm_models import EmailLogORM

    try:
        entry = EmailLogORM(
            id=log_id,
            actor_id=actor_id,
            actor_label=(actor_label or "")[:120] or None,
            patient_id=patient_id,
            evaluation_id=evaluation_id,
            documento_id=documento_id,
            tipo=tipo[:30],
            recipient_to=(recipient_to or "")[:500],
            recipient_cc=(recipient_cc or "")[:500] or None,
            recipient_bcc=(recipient_bcc or "")[:500] or None,
            subject=(subject or "")[:400],
            body_preview=(body_preview or "")[:4000] or None,
            attachments_json=json.dumps(
                [{"filename": a.filename, "size": len(a.content or b"")} for a in attachments],
                ensure_ascii=False,
            )
            if attachments
            else None,
            status=status,
            error_message=(error or "")[:500] or None,
            smtp_host=((smtp_host_override or getattr(settings, "smtp_host", "")) or "")[:120] or None,
            smtp_user=((smtp_user_override or getattr(settings, "smtp_user", "")) or "")[:120] or None,
        )
        db.add(entry)
        db.commit()
    except Exception:  # noqa: BLE001
        try:
            db.rollback()
        except Exception:  # noqa: BLE001
            pass
        logger.exception("No se pudo persistir EmailLog")
