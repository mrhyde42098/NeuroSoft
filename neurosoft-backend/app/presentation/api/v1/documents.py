"""
app/presentation/api/v1/documents.py
======================================
Endpoints para documentos clínicos y backup.

POST /documents/rips            → generar RIPS PDF
GET  /documents/rips/{pid}      → RIPS del paciente (período)
GET  /backup/download           → descargar la BD como archivo
GET  /backup/list               → historial de backups
POST /backup/                   → crear backup manual

Además: PATCH y DELETE para evolución terapéutica.
"""

from __future__ import annotations

import shutil
from datetime import date, datetime
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import Response

from app.application.dtos.clinical_history_dtos import EvolTerapiaUpdateDTO
from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

# ─── RIPS ────────────────────────────────────────────────────
rips_router = APIRouter(prefix="/rips", tags=["RIPS"])


@rips_router.post(
    "/{patient_id}",
    response_class=Response,
    summary="Generar reporte RIPS de un paciente",
    description=(
        "Genera el PDF de RIPS con todas las atenciones del paciente "
        "en el período indicado (fecha_inicio → fecha_fin)."
    ),
    responses={200: {"content": {"application/pdf": {}}}},
)
def generate_rips(
    patient_id: str,
    fecha_inicio: str = Query(..., description="YYYY-MM-DD"),
    fecha_fin:    str = Query(..., description="YYYY-MM-DD"),
    profesional_id: str | None = Query(default=None),
    db: DbSession = None,
):
    from app.infrastructure.rips_service import build_rips_data_from_db, generate_rips_pdf

    try:
        fi = date.fromisoformat(fecha_inicio)
        ff = date.fromisoformat(fecha_fin)
    except ValueError:
        raise HTTPException(status_code=422, detail="Fechas deben tener formato YYYY-MM-DD.")

    try:
        rips_data = build_rips_data_from_db(
            patient_id=patient_id,
            fecha_inicio=fi,
            fecha_fin=ff,
            db=db,
            profesional_id=profesional_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

    try:
        pdf_bytes = generate_rips_pdf(rips_data)
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))

    nombre = f"RIPS_{patient_id[:8]}_{fi.strftime('%Y%m%d')}_{ff.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
    )


@rips_router.get(
    "/export",
    summary="Exportar RIPS mensual por profesional (TXT o ZIP)",
    description=(
        "Genera los archivos RIPS por **Resolución 2275/2023** del Ministerio "
        "de Salud de Colombia:\n\n"
        "- `CT.txt` — cabecera de transacción\n"
        "- `US.txt` — usuarios atendidos\n"
        "- `AC.txt` — consultas externas\n\n"
        "Filtra por profesional (opcional) y por rango de fechas de atención. "
        "`format=zip` (default) devuelve los 3 archivos comprimidos. "
        "`format=txt` devuelve solo AC.txt para inspección rápida."
    ),
    response_class=Response,
)
def export_rips(
    desde: str = Query(..., description="YYYY-MM-DD"),
    hasta: str = Query(..., description="YYYY-MM-DD"),
    professional_id: str | None = Query(default=None),
    numero_factura: str = Query(default="SIN-FACTURA"),
    codigo_prestador: str = Query(default=""),
    format: str = Query(default="zip", pattern="^(zip|txt)$"),
    db: DbSession = None,
):
    from app.infrastructure.rips_service import (
        generate_rips_monthly_txt,
        generate_rips_monthly_zip,
    )

    try:
        fi = date.fromisoformat(desde)
        ff = date.fromisoformat(hasta)
    except ValueError:
        raise HTTPException(422, "Fechas deben tener formato YYYY-MM-DD.")
    if ff < fi:
        raise HTTPException(422, "`hasta` debe ser >= `desde`.")

    if format == "zip":
        content = generate_rips_monthly_zip(
            db,
            professional_id=professional_id,
            desde=fi,
            hasta=ff,
            numero_factura=numero_factura,
            codigo_prestador=codigo_prestador,
        )
        nombre = (
            f"RIPS_{fi.strftime('%Y%m%d')}_{ff.strftime('%Y%m%d')}"
            f"{'_' + professional_id[:8] if professional_id else ''}.zip"
        )
        return Response(
            content=content,
            media_type="application/zip",
            headers={"Content-Disposition": f'attachment; filename="{nombre}"'},
        )

    # format=txt → solo AC.txt
    files = generate_rips_monthly_txt(
        db,
        professional_id=professional_id,
        desde=fi,
        hasta=ff,
        numero_factura=numero_factura,
        codigo_prestador=codigo_prestador,
    )
    return Response(
        content=files["AC.txt"],
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": (
                f'attachment; filename="AC_{fi.strftime("%Y%m%d")}'
                f'_{ff.strftime("%Y%m%d")}.txt"'
            )
        },
    )


# ─── BACKUP ──────────────────────────────────────────────────
backup_router_new = APIRouter(prefix="/backup", tags=["Backup"])


@backup_router_new.get(
    "/download",
    summary="Descargar copia de la base de datos",
    description=(
        "Descarga el archivo SQLite completo como backup.\n\n"
        "**Importante:** Desconecta y guarda el archivo. "
        "Úsalo para restaurar en otro equipo o como copia de seguridad."
    ),
    response_class=Response,
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def download_database(db: DbSession, admin=Depends(require_admin)):

    from app.core.config import settings

    db_path = settings.db_path
    if not db_path.exists():
        raise HTTPException(status_code=404, detail="Base de datos no encontrada.")

    with open(db_path, "rb") as f:
        db_bytes = f.read()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename  = f"neurosoft_backup_{timestamp}.db"

    return Response(
        content=db_bytes,
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
            "Content-Length": str(len(db_bytes)),
        },
    )


@backup_router_new.post(
    "/",
    summary="Crear backup en el servidor",
    description="Copia la BD a la carpeta `data/backups/` del servidor.",
)
def create_server_backup(
    notas: str | None = Query(default=None),
    db: DbSession = None,
    admin=Depends(require_admin),
):
    from app.application.dtos.clinical_history_dtos import BackupRequestDTO
    from app.application.use_cases.clinical_history_use_cases import BackupUseCase

    dto = BackupRequestDTO(destino=None, notas=notas or "Backup manual")
    try:
        result = BackupUseCase(db).create_backup(dto)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@backup_router_new.get(
    "/list",
    summary="Historial de backups creados",
)
def list_backups(db: DbSession, admin=Depends(require_admin)):
    from app.application.use_cases.clinical_history_use_cases import BackupUseCase
    return BackupUseCase(db).list_backups()


@backup_router_new.post(
    "/restore",
    summary="Restaurar BD desde un archivo .db",
    description=(
        "Sube un archivo .db previamente generado por NeuroSoft y lo restaura. "
        "Antes de reemplazar la BD actual se crea un backup de seguridad en "
        "data/backups/pre_restore_<timestamp>.db. **Irreversible** — tras restaurar, "
        "los datos actuales quedarán en ese backup de seguridad."
    ),
)
async def restore_database(
    request: Request,
    archivo: UploadFile = File(..., description="Archivo .db a restaurar"),
    admin=Depends(require_admin),
):
    from app.core.config import settings
    from app.core.upload_validation import (
        SIG_SQLITE3,
        UploadValidationError,
        sanitize_filename,
        validate_upload_bytes,
    )
    from app.infrastructure.audit import record_event

    safe_name = sanitize_filename(archivo.filename)
    contenido = await archivo.read()
    try:
        validate_upload_bytes(
            contenido,
            max_bytes=settings.max_upload_backup_mb * 1024 * 1024,
            min_bytes=1024,
            allowed_extensions=[".db"],
            allowed_signatures=[SIG_SQLITE3],
            filename=safe_name,
            label="backup SQLite",
        )
    except UploadValidationError as exc:
        raise HTTPException(exc.status_code, str(exc))

    # Backup de seguridad antes de restaurar
    db_path = Path(settings.db_path)
    backups_dir = db_path.parent / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safety = backups_dir / f"pre_restore_{stamp}.db"
    if db_path.exists():
        shutil.copy2(db_path, safety)

    # Escribir el nuevo archivo
    try:
        db_path.write_bytes(contenido)
    except Exception as e:
        raise HTTPException(500, f"Error al escribir BD: {e}")

    # Registrar en auditoría del backup de seguridad (el nuevo log
    # podría no tener este registro; por eso lo metemos al safety).
    # Un fallo aquí no aborta la operación clínica, pero sí debe quedar en
    # los logs para detectar pérdida de trazabilidad.
    try:
        from app.infrastructure.database.engine import get_session
        from app.infrastructure.database.orm_models import AuditLogORM  # noqa: F401
        db2 = next(get_session())
        try:
            record_event(
                db2,
                action="restore",
                entity_type="backup",
                summary=f"Restore desde archivo ({safe_name}, {len(contenido)} bytes). "
                        f"Safety snapshot: {safety.name}",
                request=request,
            )
        finally:
            db2.close()
    except Exception as _audit_exc:  # noqa: BLE001
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "restore/backup: fallo al registrar auditoría (%s: %s)",
            type(_audit_exc).__name__, _audit_exc,
        )

    return {
        "ok": True,
        "bytes_restaurados": len(contenido),
        "safety_snapshot": str(safety.name),
        "mensaje": (
            "BD restaurada correctamente. Es recomendable reiniciar el servicio "
            "para liberar caches y conexiones previas."
        ),
    }


@backup_router_new.delete(
    "/{nombre_archivo}",
    summary="Eliminar un backup del servidor",
    status_code=204,
)
def delete_backup(
    nombre_archivo: str,
    request: Request,
    admin=Depends(require_admin),
):
    from app.core.config import settings
    from app.infrastructure.audit import record_event
    from app.infrastructure.database.engine import get_session

    if "/" in nombre_archivo or "\\" in nombre_archivo or ".." in nombre_archivo:
        raise HTTPException(400, "Nombre de archivo inválido.")
    backups_dir = Path(settings.db_path).parent / "backups"
    ruta = backups_dir / nombre_archivo
    if not ruta.exists() or not ruta.is_file():
        raise HTTPException(404, "Backup no encontrado.")
    try:
        ruta.unlink()
    except Exception as e:
        raise HTTPException(500, f"Error al eliminar: {e}")
    try:
        db = next(get_session())
        try:
            record_event(
                db,
                action="delete",
                entity_type="backup",
                summary=f"Backup eliminado: {nombre_archivo}",
                request=request,
            )
        finally:
            db.close()
    except Exception as _audit_exc:  # noqa: BLE001
        import logging as _logging
        _logging.getLogger(__name__).warning(
            "delete_backup: fallo al registrar auditoría (%s: %s)",
            type(_audit_exc).__name__, _audit_exc,
        )
    return None


# ─── EVOLUCIÓN TERAPIA: PATCH + ARCHIVE ──────────────────────
evol_extra_router = APIRouter(prefix="/evolucion", tags=["Evolución Terapia NPs"])


@evol_extra_router.patch(
    "/{sesion_id}",
    summary="Actualizar sesión de evolución terapéutica",
    description=(
        "Actualiza campos editables de una sesión **activa**. Sesiones "
        "archivadas no se pueden modificar (Res. 1995: la historia clínica "
        "es inmutable una vez archivada). Todos los cambios se registran en "
        "el audit log."
    ),
)
def update_evolucion(
    sesion_id: str,
    body: EvolTerapiaUpdateDTO,
    request: Request,
    db: DbSession,
):
    from app.infrastructure.audit import record_event
    from app.infrastructure.database.orm_models import EvolTerapiaORM

    orm = db.get(EvolTerapiaORM, sesion_id)
    if orm is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    if orm.archived_at is not None:
        raise HTTPException(
            status_code=409,
            detail=(
                "La sesión está archivada: no se permite modificarla "
                "(Resolución 1995 de 1999 — historia clínica inmutable)."
            ),
        )

    changes: dict[str, list] = {}
    updates = body.model_dump(exclude_unset=True, exclude_none=True)
    for field, new_val in updates.items():
        old_val = getattr(orm, field, None)
        if old_val != new_val:
            changes[field] = [
                old_val.isoformat() if hasattr(old_val, "isoformat") else old_val,
                new_val.isoformat() if hasattr(new_val, "isoformat") else new_val,
            ]
            setattr(orm, field, new_val)
    db.flush()

    if changes:
        actor_id = getattr(request.state, "user_id", None)
        record_event(
            db,
            action="update",
            entity_type="evolucion",
            entity_id=orm.id,
            actor_id=actor_id,
            summary=f"Actualización sesión {orm.id[:8]} ({len(changes)} campos)",
            changes=changes,
            request=request,
            commit=False,  # viaja con el commit del endpoint
        )

    return {
        "id": orm.id,
        "patient_id": orm.patient_id,
        "fecha_sesion": orm.fecha_sesion.isoformat() if orm.fecha_sesion else None,
        "numero_sesion": orm.numero_sesion,
        "objetivos": orm.objetivos,
        "actividades": orm.actividades,
        "plan_trabajo": orm.plan_trabajo,
        "campos_modificados": list(changes.keys()),
    }


@evol_extra_router.delete(
    "/{sesion_id}",
    status_code=204,
    summary="Archivar sesión de evolución terapéutica (soft-delete)",
    description=(
        "Archiva (soft-delete) una sesión de evolución. La fila **no se "
        "elimina físicamente** porque la Resolución 1995 de 1999 del "
        "Ministerio de Salud obliga a conservar la historia clínica. "
        "Marca `archived_at`, `archived_by` y `archived_reason` y la retira "
        "de los listados por defecto. Queda asiento completo en el audit log."
    ),
)
def delete_evolucion(
    sesion_id: str,
    request: Request,
    db: DbSession,
    reason: str | None = Query(
        default=None,
        max_length=500,
        description="Motivo del archivo — exigido por trazabilidad clínica.",
    ),
):
    from app.infrastructure.audit import record_event
    from app.infrastructure.database.orm_models import EvolTerapiaORM

    orm = db.get(EvolTerapiaORM, sesion_id)
    if orm is None:
        raise HTTPException(status_code=404, detail="Sesión no encontrada.")
    if orm.archived_at is not None:
        # Idempotente: si ya está archivada, devolvemos 204 igual para que
        # el cliente pueda reintentar sin romper UX.
        return None

    actor_id = getattr(request.state, "user_id", None)
    motivo = (reason or "archivo sin motivo especificado").strip()[:500]

    orm.archived_at = datetime.utcnow()
    orm.archived_by = actor_id
    orm.archived_reason = motivo
    db.flush()

    record_event(
        db,
        action="archive",
        entity_type="evolucion",
        entity_id=orm.id,
        actor_id=actor_id,
        summary=f"Archivo sesión evolución (paciente {orm.patient_id[:8]})",
        changes={"reason": motivo},
        request=request,
        commit=False,
    )
    return None
