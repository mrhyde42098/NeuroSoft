"""
app/application/services/backup_service.py
==========================================
Orquestación unificada de backups cifrados (QW-8).

Manual y automático comparten: WAL checkpoint → crear_backup() Fernet →
registro ORM → retención configurable → copia externa opcional.
"""

from __future__ import annotations

import logging
import shutil
import uuid
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.dtos.clinical_history_dtos import BackupResponseDTO
from app.core.config import settings
from app.core.exceptions import ApplicationError
from app.infrastructure.backup import (
    aplicar_retencion_total,
    crear_backup,
    listar_backups,
)
from app.infrastructure.database.orm_models import (
    BackupRegistroORM,
    ConfigBackupScheduleORM,
    EvaluationORM,
    PatientORM,
)

logger = logging.getLogger("neurosoft.backup_service")

SCHEDULE_ROW_ID = "default"
Frequency = Literal["daily", "weekly", "monthly"]


@dataclass
class BackupScheduleConfig:
    enabled: bool = True
    frequency: Frequency = "daily"
    hour: int = 2
    minute: int = 0
    mantener_total: int = 5
    external_path: str | None = None


@dataclass
class BackupRunResult:
    registro: BackupRegistroORM
    ruta: Path
    tamano_bytes: int


def _wal_checkpoint(db: Session) -> None:
    try:
        db.execute(text("PRAGMA wal_checkpoint(FULL)"))
    except Exception:  # noqa: BLE001
        pass


def get_schedule_config(db: Session) -> BackupScheduleConfig:
    row = db.get(ConfigBackupScheduleORM, SCHEDULE_ROW_ID)
    if not row:
        row = ConfigBackupScheduleORM(id=SCHEDULE_ROW_ID)
        db.add(row)
        db.flush()
    return BackupScheduleConfig(
        enabled=bool(row.enabled),
        frequency=row.frequency or "daily",  # type: ignore[arg-type]
        hour=int(row.hour or 2),
        minute=int(row.minute or 0),
        mantener_total=int(row.mantener_total or 5),
        external_path=row.external_path,
    )


def save_schedule_config(db: Session, cfg: BackupScheduleConfig) -> BackupScheduleConfig:
    row = db.get(ConfigBackupScheduleORM, SCHEDULE_ROW_ID)
    if not row:
        row = ConfigBackupScheduleORM(id=SCHEDULE_ROW_ID)
        db.add(row)
    row.enabled = cfg.enabled
    row.frequency = cfg.frequency
    row.hour = max(0, min(23, cfg.hour))
    row.minute = max(0, min(59, cfg.minute))
    row.mantener_total = max(3, min(30, cfg.mantener_total))
    row.external_path = (cfg.external_path or "").strip() or None
    row.updated_at = datetime.now(UTC)
    db.flush()
    return get_schedule_config(db)


def run_backup(
    db: Session,
    *,
    notas: str | None = None,
    tipo: str = "manual",
    mantener_total: int | None = None,
    external_path: str | None = None,
) -> BackupRunResult:
    """Crea backup cifrado, registra en ORM y aplica retención."""
    db_path = settings.db_path
    if not db_path.exists():
        raise ApplicationError("Base de datos no encontrada.", code="DB_NOT_FOUND")

    schedule = get_schedule_config(db)
    retain = mantener_total if mantener_total is not None else schedule.mantener_total
    ext = external_path if external_path is not None else schedule.external_path

    _wal_checkpoint(db)

    ruta = crear_backup(notas=notas or f"Backup {tipo}")
    tamano = ruta.stat().st_size

    total_pac = db.query(PatientORM).filter_by(is_active=True).count()
    total_ev = db.query(EvaluationORM).count()

    registro = BackupRegistroORM(
        id=str(uuid.uuid4()),
        ruta_destino=str(ruta),
        tamano_bytes=tamano,
        total_pacientes=total_pac,
        total_evaluaciones=total_ev,
        exitoso=True,
        notas=notas,
        tipo=tipo,
    )
    db.add(registro)

    eliminados = aplicar_retencion_total(retain)
    if eliminados:
        logger.info("Retención backup: %d archivos eliminados (mantener=%d)", eliminados, retain)

    if ext:
        _copy_external(ruta, ext)

    return BackupRunResult(registro=registro, ruta=ruta, tamano_bytes=tamano)


def _copy_external(ruta: Path, external_path: str) -> None:
    dest_dir = Path(external_path)
    try:
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / ruta.name
        shutil.copy2(ruta, dest)
        logger.info("Backup copiado a ruta externa: %s", dest)
    except OSError as e:
        logger.warning("No se pudo copiar backup a %s: %s", external_path, e)


def notify_backup_failure(db: Session, error: str) -> None:
    """Email al admin si SMTP está configurado (patrón QW-7)."""
    try:
        from app.infrastructure.database.orm_models import ConfigInstitucionORM
        from app.infrastructure.email_service import is_configured, send_email

        if not is_configured(db):
            return
        inst = db.query(ConfigInstitucionORM).first()
        inst_nombre = (inst.nombre if inst else "") or "NeuroSoft"
        to_email = (inst.email if inst else "") or ""
        if not to_email.strip():
            return
        send_email(
            db,
            to=[to_email.strip()],
            subject=f"[{inst_nombre}] Fallo en backup automático",
            body=(
                "El backup programado de NeuroSoft no se completó.\n\n"
                f"Error: {error}\n\n"
                "Revise Configuración → Respaldo y cree un backup manual."
            ),
        )
    except Exception as e:  # noqa: BLE001
        logger.warning("No se pudo enviar email de fallo de backup: %s", e)


def run_scheduled_backup() -> None:
    """Entry point del APScheduler."""
    from app.infrastructure.audit import record_event
    from app.infrastructure.database.engine import get_session

    db = next(get_session())
    try:
        cfg = get_schedule_config(db)
        if not cfg.enabled:
            logger.info("[Scheduler] Backup automático deshabilitado en config.")
            return
        result = run_backup(
            db,
            notas="Backup automático programado",
            tipo="automatico",
        )
        record_event(
            db,
            action="backup",
            entity_type="backup",
            summary=f"Backup automático cifrado ({result.tamano_bytes / 1024:.1f} KB)",
        )
        db.commit()
        logger.info("[Scheduler] Backup automático OK: %s", result.ruta)
    except Exception as e:
        db.rollback()
        logger.error("[Scheduler] Error en backup automático: %s", e)
        try:
            notify_backup_failure(db, str(e))
            db.commit()
        except Exception:  # noqa: BLE001
            db.rollback()
    finally:
        db.close()


def to_response_dto(registro: BackupRegistroORM, *, integridad: str = "ok") -> BackupResponseDTO:
    ruta = registro.ruta_destino or ""
    nombre = Path(ruta).name if ruta else None
    cifrado = nombre.endswith(".enc.gz") if nombre else False
    return BackupResponseDTO(
        id=registro.id,
        fecha=registro.fecha.isoformat(),
        ruta_destino=nombre or ruta,
        tamano_kb=round((registro.tamano_bytes or 0) / 1024, 1),
        total_pacientes=registro.total_pacientes or 0,
        total_evaluaciones=registro.total_evaluaciones or 0,
        exitoso=bool(registro.exitoso),
        notas=registro.notas,
        integridad=integridad,
        tipo=registro.tipo or "manual",
        cifrado=cifrado,
    )


def list_unified_backups(db: Session, limit: int = 30) -> list[BackupResponseDTO]:
    """Combina registros ORM con archivos cifrados en disco."""
    registros = db.query(BackupRegistroORM).order_by(BackupRegistroORM.fecha.desc()).limit(limit).all()
    seen_paths = {r.ruta_destino for r in registros if r.ruta_destino}
    out = [to_response_dto(r) for r in registros if r.exitoso]

    for meta in listar_backups():
        path_str = str(meta.ruta)
        if path_str in seen_paths:
            continue
        out.append(
            BackupResponseDTO(
                id=path_str,
                fecha=meta.timestamp.isoformat(),
                ruta_destino=meta.ruta.name,
                tamano_kb=round(meta.tamano_bytes / 1024, 1),
                total_pacientes=0,
                total_evaluaciones=0,
                exitoso=True,
                notas=meta.notas,
                integridad="ok",
                tipo="automatico",
                cifrado=True,
            )
        )

    out.sort(key=lambda x: x.fecha, reverse=True)
    return out[:limit]
