"""
app/infrastructure/scheduler_service.py
==========================================
Tareas programadas con APScheduler.

Tareas:
  - 08:00 diario: marca citas del día como "confirmada" si siguen en "programada"
  - 08:00 diario: log de citas del día para el profesional
  - 23:59 diario: marca como "no_asistio" las citas pasadas aún en "programada"
  - Cada hora: limpieza de tokens expirados (futuro)

Dependencia:
    pip install apscheduler

Integración en main.py:
    from app.infrastructure.scheduler_service import start_scheduler, stop_scheduler
    # En lifespan startup: start_scheduler()
    # En lifespan shutdown: stop_scheduler()
"""

from __future__ import annotations

import logging
from datetime import date, timedelta

logger = logging.getLogger(__name__)

_scheduler = None


# ─────────────────────────────────────────────────────────────
# TAREAS
# ─────────────────────────────────────────────────────────────


def _task_recordatorio_citas():
    """
    Ejecuta a las 08:00 diario.
    - Registra en log las citas del día.
    - Marca como 'confirmada' las citas de hoy que siguen en 'programada'.
    """
    try:
        from app.infrastructure.database.engine import get_session
        from app.infrastructure.database.orm_models import AppointmentORM

        db = next(get_session())
        hoy = date.today()

        citas_hoy = (
            db.query(AppointmentORM)
            .filter(
                AppointmentORM.fecha == hoy,
                AppointmentORM.estado.in_(["programada", "confirmada"]),
            )
            .all()
        )

        if not citas_hoy:
            logger.info("[Scheduler] Agenda: no hay citas para hoy (%s)", hoy)
            db.close()
            return

        logger.info("[Scheduler] Agenda del día %s: %d citas", hoy, len(citas_hoy))
        for c in citas_hoy:
            # PII: NO loguear nombres (Ley 1581). Sólo id del paciente.
            logger.info(
                "  %s  %-10s  patient_id=%s  [%s]",
                c.hora_inicio,
                c.tipo_cita,
                c.patient_id,
                c.estado,
            )
            # Auto-confirmar las que siguen en programada
            if c.estado == "programada":
                c.estado = "confirmada"
                c.recordatorio_env = True

        db.commit()
        db.close()
        logger.info("[Scheduler] Recordatorios procesados.")

    except Exception as e:
        logger.error("[Scheduler] Error en recordatorio de citas: %s", e)


def _task_recordatorio_email_manana():
    """
    §QW-7 Ejecuta a las 18:00 diario.
    Envía un email recordatorio a cada paciente con cita MAÑANA cuyo email
    esté registrado. Solo envía si SMTP está configurado y aún no se envió.
    Usa la plantilla 'recordatorio' (editable en Ajustes → Plantillas).
    """
    try:
        from app.infrastructure.database.engine import get_session
        from app.infrastructure.database.orm_models import (
            AppointmentORM,
            ConfigEmailTemplateORM,
            ConfigInstitucionORM,
            PatientORM,
            ProfessionalORM,
        )
        from app.infrastructure.email_service import (
            TemplateContext,
            is_configured,
            send_email,
        )

        db = next(get_session())
        if not is_configured(db):
            logger.info("[Scheduler] SMTP no configurado — recordatorio_email_manana omitido.")
            db.close()
            return

        manana = date.today() + timedelta(days=1)
        citas = (
            db.query(AppointmentORM)
            .filter(
                AppointmentORM.fecha == manana,
                AppointmentORM.estado.in_(["programada", "confirmada"]),
                AppointmentORM.recordatorio_env == False,  # noqa: E712
            )
            .all()
        )
        if not citas:
            logger.info("[Scheduler] No hay citas para mañana (%s).", manana)
            db.close()
            return

        # Buscar plantilla custom 'recordatorio' o usar default inline
        tpl_row = db.query(ConfigEmailTemplateORM).filter_by(tipo="recordatorio", activo=True).first()
        DEFAULT_SUBJECT = "Recordatorio de cita — {fecha} — {institucion}"
        DEFAULT_BODY = (
            "Estimado/a {patient_nombre},\n\n"
            "Le recordamos su cita de {tipo_cita} programada para el "
            "{fecha} a las {hora}.\n\n"
            "Por favor confirme asistencia o reprograme respondiendo a este correo.\n\n"
            "Atentamente,\n{profesional}\n{institucion}"
        )
        tpl_subject = (tpl_row.subject if tpl_row else None) or DEFAULT_SUBJECT
        tpl_body = (tpl_row.body if tpl_row else None) or DEFAULT_BODY

        inst = db.query(ConfigInstitucionORM).first()
        inst_nombre = (inst.nombre if inst else "") or "Consultorio Neuropsicológico"
        enviados = 0
        for c in citas:
            try:
                pat = db.get(PatientORM, c.patient_id)
                if not pat or not (pat.email or "").strip():
                    continue
                prof = db.get(ProfessionalORM, c.profesional_id) if c.profesional_id else None
                ctx = TemplateContext(
                    patient_nombre=(pat.primer_nombre or "") + " " + (pat.primer_apellido or ""),
                    patient_doc=pat.numero_documento or "",
                    fecha=c.fecha.strftime("%d/%m/%Y"),
                    profesional=(prof.nombre_completo if prof else "") or "",
                    institucion=inst_nombre,
                )
                # Extender con hora + tipo_cita (variables custom)
                extra = {**ctx.as_dict(), "hora": c.hora_inicio or "", "tipo_cita": c.tipo_cita or "consulta"}
                subject = tpl_subject.format_map(_SafeMap(extra))
                body = tpl_body.format_map(_SafeMap(extra))

                result = send_email(
                    db,
                    to=[pat.email.strip()],
                    subject=subject,
                    body=body,
                    tipo="recordatorio",
                    patient_id=pat.id,
                    actor_label="scheduler_recordatorio",
                )
                if result.ok:
                    c.recordatorio_env = True
                    enviados += 1
                else:
                    logger.warning("[Scheduler] No se envió recordatorio a %s: %s", pat.email, result.error)
            except Exception as e:  # noqa: BLE001
                logger.warning("[Scheduler] Error en cita %s: %s", c.id, e)
        db.commit()
        db.close()
        logger.info("[Scheduler] Recordatorios mañana: %d/%d enviados.", enviados, len(citas))
    except Exception as e:  # noqa: BLE001
        logger.error("[Scheduler] Error en recordatorio_email_manana: %s", e)


class _SafeMap(dict):
    def __missing__(self, k):
        return "{" + k + "}"


def _task_marcar_no_asistio():
    """
    Ejecuta a las 23:59 diario.
    Marca como 'no_asistio' las citas de días anteriores que aún están
    en estado 'programada' o 'confirmada'.
    """
    try:
        from app.infrastructure.database.engine import get_session
        from app.infrastructure.database.orm_models import AppointmentORM

        db = next(get_session())
        ayer = date.today() - timedelta(days=1)

        citas_perdidas = (
            db.query(AppointmentORM)
            .filter(
                AppointmentORM.fecha <= ayer,
                AppointmentORM.estado.in_(["programada", "confirmada"]),
            )
            .all()
        )

        count = len(citas_perdidas)
        for c in citas_perdidas:
            c.estado = "no_asistio"

        db.commit()
        db.close()

        if count:
            logger.info("[Scheduler] %d cita(s) marcadas como 'no_asistio'.", count)

    except Exception as e:
        logger.error("[Scheduler] Error en tarea no_asistio: %s", e)


def _task_backup_automatico():
    """QW-8 — delega en backup_service (cifrado + retención + registro ORM)."""
    from app.application.services.backup_service import run_scheduled_backup

    run_scheduled_backup()


def _task_backup_integrity_check():
    """
    Ejecuta semanalmente (domingo 03:00).
    Verifica integridad SQLite de los últimos 5 backups cifrados (.enc.gz).
    """
    try:
        import sqlite3
        import tempfile
        from pathlib import Path as _Path

        from app.infrastructure.backup import listar_backups, restaurar_backup

        backups = listar_backups()[:5]
        if not backups:
            return

        corrupted = []
        for meta in backups:
            tmp = _Path(tempfile.mkdtemp()) / "check.db"
            try:
                restaurar_backup(meta.ruta, target_path=tmp)
                conn = sqlite3.connect(f"file:{tmp}?mode=ro", uri=True)
                result = conn.execute("PRAGMA integrity_check").fetchone()
                conn.close()
                if result[0] != "ok":
                    corrupted.append((meta.ruta.name, str(result[0])))
            except Exception as exc:
                corrupted.append((meta.ruta.name, str(exc)))
            finally:
                try:
                    tmp.unlink(missing_ok=True)
                    tmp.parent.rmdir()
                except OSError:
                    pass

        if corrupted:
            logger.warning(
                "[Scheduler] %d backups cifrados con problemas: %s",
                len(corrupted),
                [c[0] for c in corrupted],
            )
        else:
            logger.info("[Scheduler] Integridad de backups cifrados OK: %d archivos", len(backups))

    except Exception as e:
        logger.error("[Scheduler] Error en verificacion de integridad: %s", e)


def _task_purge_token_blacklist():
    """
    Ejecuta cada hora. Elimina entradas ya caducadas (`expires_at` < ahora)
    de `token_blacklist`. Una vez pasado el `exp` del JWT, el decode falla
    por sí solo: mantener el registro solo acumula basura.
    """
    try:
        from app.infrastructure.auth.auth_service import purge_expired_blacklist_entries
        from app.infrastructure.database.engine import get_session

        db = next(get_session())
        try:
            deleted = purge_expired_blacklist_entries(db)
            db.commit()
            if deleted:
                logger.info("[Scheduler] Blacklist purgada: %d tokens expirados", deleted)
        finally:
            db.close()
    except Exception as e:
        logger.error("[Scheduler] Error purgando token_blacklist: %s", e)


def _prune_old_backups(keep_daily: int = 30) -> None:
    """Conserva los últimos keep_daily backups diarios; mantiene backups de domingo."""
    try:
        from pathlib import Path

        from app.core.config import settings

        backups_dir = Path(settings.db_path).parent / "backups"
        if not backups_dir.exists():
            return

        archivos = sorted(
            (p for p in backups_dir.glob("*.db") if p.is_file()),
            key=lambda p: p.stat().st_mtime,
            reverse=True,
        )
        keep = set(archivos[:keep_daily])
        for arch in archivos[keep_daily:]:
            # Conservar los de domingo (weekday == 6)
            try:
                from datetime import datetime as _dt

                if _dt.fromtimestamp(arch.stat().st_mtime).weekday() == 6:
                    keep.add(arch)
                    continue
                arch.unlink()
                logger.info("[Scheduler] Prune backup: %s", arch.name)
            except Exception as e:
                logger.warning("[Scheduler] No se pudo eliminar %s: %s", arch.name, e)
    except Exception as e:
        logger.warning("[Scheduler] Prune backups falló: %s", e)


# ─────────────────────────────────────────────────────────────
# BACKUP SCHEDULE (QW-8)
# ─────────────────────────────────────────────────────────────


def _backup_cron_trigger(cfg):
    """Construye CronTrigger según frecuencia configurada."""
    from apscheduler.triggers.cron import CronTrigger

    freq = cfg.frequency or "daily"
    if freq == "weekly":
        return CronTrigger(day_of_week="sun", hour=cfg.hour, minute=cfg.minute)
    if freq == "monthly":
        return CronTrigger(day=1, hour=cfg.hour, minute=cfg.minute)
    return CronTrigger(hour=cfg.hour, minute=cfg.minute)


def reschedule_backup_job() -> None:
    """Reprograma el job backup_automatico según config_backup_schedule."""
    global _scheduler
    if _scheduler is None:
        return
    try:
        from app.application.services.backup_service import get_schedule_config
        from app.infrastructure.database.engine import get_session

        db = next(get_session())
        try:
            cfg = get_schedule_config(db)
        finally:
            db.close()

        if not cfg.enabled:
            try:
                _scheduler.remove_job("backup_automatico")
            except Exception:  # noqa: BLE001
                pass
            logger.info("[Scheduler] Backup automático deshabilitado.")
            return

        trigger = _backup_cron_trigger(cfg)
        _scheduler.add_job(
            _task_backup_automatico,
            trigger=trigger,
            id="backup_automatico",
            replace_existing=True,
            name=f"Backup automático ({cfg.frequency})",
        )
        logger.info(
            "[Scheduler] Backup reprogramado: %s %02d:%02d",
            cfg.frequency,
            cfg.hour,
            cfg.minute,
        )
    except Exception as e:
        logger.warning("[Scheduler] No se pudo reprogramar backup: %s", e)
        from apscheduler.triggers.cron import CronTrigger

        _scheduler.add_job(
            _task_backup_automatico,
            trigger=CronTrigger(hour=2, minute=0),
            id="backup_automatico",
            replace_existing=True,
            name="Backup automático diario",
        )


def get_backup_job_times() -> dict:
    """Devuelve next_run_at del job backup si el scheduler está activo."""
    global _scheduler
    if not _scheduler:
        return {}
    job = _scheduler.get_job("backup_automatico")
    if not job or not job.next_run_time:
        return {}
    return {"next_run_at": job.next_run_time.isoformat()}


# ─────────────────────────────────────────────────────────────
# ARRANQUE / APAGADO
# ─────────────────────────────────────────────────────────────


def start_scheduler() -> None:
    """Inicia el scheduler de tareas programadas."""
    global _scheduler

    try:
        from apscheduler.schedulers.background import BackgroundScheduler
        from apscheduler.triggers.cron import CronTrigger
    except ImportError:
        logger.warning(
            "[Scheduler] APScheduler no instalado. Las tareas programadas no correrán. pip install apscheduler"
        )
        return

    _scheduler = BackgroundScheduler(timezone="America/Bogota")

    # Recordatorio diario 08:00
    _scheduler.add_job(
        _task_recordatorio_citas,
        trigger=CronTrigger(hour=8, minute=0),
        id="recordatorio_citas",
        replace_existing=True,
        name="Recordatorio de citas diarias",
    )

    # Marcar no_asistio a las 23:59
    _scheduler.add_job(
        _task_marcar_no_asistio,
        trigger=CronTrigger(hour=23, minute=59),
        id="marcar_no_asistio",
        replace_existing=True,
        name="Marcar citas no atendidas",
    )

    # §QW-7: Recordatorio email anticipación 1 día — 18:00
    _scheduler.add_job(
        _task_recordatorio_email_manana,
        trigger=CronTrigger(hour=18, minute=0),
        id="recordatorio_email_manana",
        replace_existing=True,
        name="Recordatorio por correo de citas de mañana",
    )

    # Backup automático — trigger desde config DB (default 02:00 diario)
    reschedule_backup_job()

    # Verificacion de integridad de backups SEMANAL domingo 03:00
    _scheduler.add_job(
        _task_backup_integrity_check,
        trigger=CronTrigger(day_of_week="sun", hour=3, minute=0),
        id="backup_integrity_check",
        replace_existing=True,
        name="Verificación semanal de integridad de backups",
    )

    # Purga de tokens revocados ya caducados, cada hora.
    _scheduler.add_job(
        _task_purge_token_blacklist,
        trigger=CronTrigger(minute=15),  # cada hora al minuto 15
        id="purge_token_blacklist",
        replace_existing=True,
        name="Purga blacklist de tokens",
    )

    _scheduler.start()
    logger.info(
        "[Scheduler] ✅ Iniciado — recordatorio 08:00, no_asistio 23:59, backup diario 02:00, purga blacklist cada hora"
    )


def stop_scheduler() -> None:
    """Detiene el scheduler limpiamente."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Detenido.")
    _scheduler = None
