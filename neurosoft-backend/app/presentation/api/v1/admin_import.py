"""
app/presentation/api/v1/admin_import.py
========================================
Endpoints de administración / migración legacy.

POST /admin/import-legacy-xlsm
    Sube un archivo MISISTEMAV1.xlsm (libro Excel con macros deshabilitadas)
    y ejecuta la migración ETL hacia las tablas ORM actuales. Idempotente:
    si (numero_documento, fecha_atencion) ya existe, se omite.

Solo admin. Requiere openpyxl instalado en el servidor.
"""
from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

logger = logging.getLogger("neurosoft.admin_import")

admin_router = APIRouter(prefix="/admin", tags=["Admin"])


@admin_router.post(
    "/import-legacy-xlsm",
    summary="Migrar datos desde MISISTEMAV1.xlsm",
    description=(
        "Lee el libro Excel legacy y vuelca sus hojas a las tablas ORM:\n\n"
        "- `DBRecepcion` → `patients`\n"
        "- `DBHC` → `clinical_histories` (47 campos de desarrollo/antecedentes/plan)\n"
        "- `DBObser` → campos `obs_*` de la HC\n"
        "- `DBScore` → `evaluations` (puntajes brutos serializados en JSON)\n"
        "- `DBETN` → `evolucion_terapia`\n\n"
        "**Idempotente**: si ya existe un paciente con la misma clave "
        "`(numero_documento, fecha_atencion)` se omite sin error.\n\n"
        "Requiere rol `admin`."
    ),
)
async def import_legacy_xlsm(
    request: Request,
    archivo: UploadFile = File(..., description="Archivo .xlsm (MISISTEMAV1)"),
    db: DbSession = None,
    admin=Depends(require_admin),
):
    from app.core.config import settings
    from app.core.upload_validation import (
        OOXML_SIGNATURES,
        UploadValidationError,
        sanitize_filename,
        validate_upload_bytes,
    )

    safe_name = sanitize_filename(archivo.filename)
    contenido = await archivo.read()
    try:
        validate_upload_bytes(
            contenido,
            max_bytes=settings.max_upload_xlsm_mb * 1024 * 1024,
            min_bytes=1024,
            allowed_extensions=[".xlsm", ".xlsx"],
            allowed_signatures=OOXML_SIGNATURES,
            filename=safe_name,
            label="libro Excel legacy",
        )
    except UploadValidationError as exc:
        raise HTTPException(exc.status_code, str(exc))

    # Volcar a archivo temporal (openpyxl necesita ruta en disco en read_only)
    tmp = tempfile.NamedTemporaryFile(
        delete=False, suffix=Path(safe_name).suffix or ".xlsm"
    )
    try:
        tmp.write(contenido)
        tmp.flush()
        tmp.close()
        tmp_path = Path(tmp.name)

        from app.infrastructure.legacy_import_service import import_legacy_xlsm as _run

        try:
            report = _run(
                tmp_path,
                db,
                actor_id=getattr(admin, "id", None),
                actor_label=getattr(admin, "username", None) or getattr(admin, "nombre_completo", None),
                default_profesional_id=getattr(admin, "profesional_id", None),
            )
        except RuntimeError as e:
            raise HTTPException(503, detail=str(e))
        except FileNotFoundError as e:
            raise HTTPException(500, detail=str(e))
        except Exception as e:  # noqa: BLE001
            logger.exception("Error importando xlsm")
            raise HTTPException(500, detail=f"Error procesando xlsm: {e}")

        return {
            "ok": True,
            "archivo": safe_name,
            "bytes": len(contenido),
            **report.as_dict(),
        }
    finally:
        try:
            Path(tmp.name).unlink(missing_ok=True)
        except Exception:  # noqa: BLE001
            pass
