"""
app/presentation/api/v1/update.py
====================================
Sistema de actualizacion manual offline.

Flujo:
  1. Johan genera neurosoft-vX.Y.Z.nsupdate con build.py --make-update
  2. El clinico (rol=admin) sube el archivo desde ConfigPage > Actualizar sistema
  3. La app verifica la firma HMAC-SHA256 contra NEUROSOFT_UPDATE_HMAC_KEY,
     extrae los archivos, actualiza el frontend, reinicia el server
  4. Al reiniciar, el frontend detecta la nueva version y muestra WhatNewModal

Seguridad (S0.1 del PLAN_MAESTRO):
  - require_admin: solo rol admin puede aplicar actualizaciones.
  - HMAC-SHA256: el header X-Update-Signature (hex) debe coincidir con
    HMAC(NEUROSOFT_UPDATE_HMAC_KEY, body). Si no coincide -> 401.
  - Audit log: cada aplicacion queda registrada en `audit_log` con actor,
    version, tamano, SHA-256 del archivo y remote IP.
  - Path traversal: rechaza cualquier entrada del ZIP cuya ruta resuelta
    salga de `frontend_dist` (ej. `frontend/../../etc/passwd`).
"""

from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
import shutil
import tempfile
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException, Request, UploadFile

from app.infrastructure.auth.auth_service import hash_password  # noqa: F401  (mantenido por simetría con auth.py)
from app.infrastructure.database.orm_models import AuditLogORM
from app.presentation.api.v1.auth import require_admin
from app.presentation.dependencies import DbSession

logger = logging.getLogger(__name__)

update_router = APIRouter(prefix="/system", tags=["Sistema"])


def _resolve_hmac_key() -> str:
    """
    Devuelve la clave HMAC para validar firmas de .nsupdate.

    Prioridad:
      1) NEUROSOFT_UPDATE_HMAC_KEY (recomendado en .env de producción)
      2) Derivada determinística de SECRET_KEY (fallback dev)
    """
    explicit = os.getenv("NEUROSOFT_UPDATE_HMAC_KEY", "").strip()
    if explicit:
        return explicit
    # Fallback: derivar del SECRET_KEY para que dev/build no fallen,
    # pero loggeamos warning. En prod, configurar la variable explícita.
    from app.infrastructure.auth.auth_service import SECRET_KEY
    derived = hashlib.sha256(("nsupdate-hmac::" + SECRET_KEY).encode("utf-8")).hexdigest()
    logger.warning(
        "NEUROSOFT_UPDATE_HMAC_KEY no configurada; usando derivado de SECRET_KEY. "
        "Define la variable en .env antes de producción."
    )
    return derived


HMAC_KEY = _resolve_hmac_key()


def _safe_join(base: Path, *parts: str) -> Path | None:
    """
    Une `base / *parts` y verifica que el resultado siga dentro de `base`.
    Retorna None si hay escape (path traversal).
    """
    try:
        base_resolved = base.resolve(strict=False)
        candidate = (base.joinpath(*parts)).resolve(strict=False)
        # El resolved debe estar dentro del base (con prefix común)
        candidate.relative_to(base_resolved)
        return candidate
    except (ValueError, RuntimeError):
        return None


@update_router.post(
    "/update",
    summary="Aplicar actualizacion desde archivo .nsupdate (solo admin, requiere firma HMAC)",
)
def apply_update(
    request: Request,
    file: UploadFile,
    admin: Annotated[object, Depends(require_admin)],
    db: DbSession,
    x_update_signature: Annotated[str | None, Header(alias="X-Update-Signature")] = None,
):
    """
    Recibe un archivo .nsupdate (ZIP) firmado y lo aplica.

    Headers obligatorios:
      Authorization:        Bearer <admin JWT>
      X-Update-Signature:   HMAC-SHA256(NEUROSOFT_UPDATE_HMAC_KEY, body) en hex

    El ZIP contiene:
      - manifest.json: { version, fecha, cambios[], frontend_hash }
      - frontend/ : archivos de la nueva build del frontend
    """
    # 1) Validacion de firma HMAC (antes de tocar disco, antes que nada)
    if not x_update_signature:
        raise HTTPException(
            status_code=401,
            detail="Falta header X-Update-Signature (HMAC-SHA256 en hex).",
        )
    if not file.filename or not file.filename.endswith(".nsupdate"):
        raise HTTPException(400, "El archivo debe tener extension .nsupdate")

    try:
        content = file.file.read()
    except Exception as e:
        raise HTTPException(400, f"Error leyendo archivo: {e}")

    expected = hmac.new(HMAC_KEY.encode("utf-8"), content, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, x_update_signature.strip().lower()):
        logger.warning(
            "Firma HMAC invalida para %s (esperado %s..., recibido %s...)",
            file.filename, expected[:8], x_update_signature[:8],
        )
        raise HTTPException(
            status_code=401,
            detail="Firma HMAC invalida. El archivo .nsupdate no es auténtico.",
        )

    # 2) Validaciones de tamano
    if len(content) < 1024:
        raise HTTPException(400, "Archivo demasiado pequeno")
    if len(content) > 200 * 1024 * 1024:
        raise HTTPException(400, "Archivo demasiado grande (max 200 MB)")

    file_sha256 = hashlib.sha256(content).hexdigest()

    tmp: Path | None = None
    version = "unknown"
    try:
        with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tf:
            tf.write(content)
            tmp = Path(tf.name)

        with zipfile.ZipFile(tmp, "r") as zf:
            # 3) Validar manifest
            names = zf.namelist()
            if "manifest.json" not in names:
                raise HTTPException(400, "Archivo .nsupdate invalido: falta manifest.json")

            manifest_raw = zf.read("manifest.json").decode("utf-8")
            manifest = json.loads(manifest_raw)
            version = manifest.get("version", "unknown")

            logger.info(
                "Aplicando actualizacion v%s desde archivo %s (sha256=%s)",
                version, file.filename, file_sha256[:12],
            )

            # 4) Extraer SOLO entradas con prefijo `frontend/` y sin path traversal
            frontend_dist = Path("neurosoft-frontend") / "dist"
            frontend_dist_resolved = frontend_dist.resolve(strict=False)
            if not frontend_dist.exists():
                frontend_dist.mkdir(parents=True, exist_ok=True)
                frontend_dist_resolved = frontend_dist.resolve(strict=False)

            extracted_count = 0
            for name in names:
                if name == "manifest.json" or name.startswith("__MACOSX"):
                    continue
                if not name.startswith("frontend/"):
                    continue

                # Rechazar paths absolutos, con `..` o cualquier intento de escape
                # _safe_join valida que el resultado caiga dentro de frontend_dist
                rel = name[len("frontend/"):]
                if not rel or rel.endswith("/"):
                    # entrada de directorio: ignorar (se crea con mkdir arriba)
                    continue
                # Normalizar separadores y rechazar `..` directamente por si
                # zipfile.ZipFile no normalizara en Windows
                parts = rel.replace("\\", "/").split("/")
                if any(p in ("..", "") for p in parts[:-1]) or ".." in parts:
                    logger.error("Path traversal detectado en .nsupdate: %s", name)
                    raise HTTPException(
                        400,
                        f"Entrada insegura rechazada: {name}",
                    )
                dest = _safe_join(frontend_dist, *parts)
                if dest is None:
                    logger.error("Path traversal resuelto fuera de dist: %s", name)
                    raise HTTPException(
                        400,
                        f"Entrada insegura rechazada: {name}",
                    )

                dest.parent.mkdir(parents=True, exist_ok=True)
                with zf.open(name) as src_f:
                    dest.write_bytes(src_f.read())
                extracted_count += 1

            # 5) Persistir info de actualizacion para que el frontend la detecte
            update_info = {
                "version": version,
                "fecha": manifest.get("fecha", ""),
                "aplicada_en": datetime.now(UTC).isoformat(),
                "sha256": file_sha256,
                "tamano_bytes": len(content),
                "actor": getattr(admin, "username", None) or str(getattr(admin, "id", "")),
            }
            update_path = Path("data") / "last_update.json"
            update_path.parent.mkdir(parents=True, exist_ok=True)
            update_path.write_text(
                json.dumps(update_info, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    except HTTPException:
        raise
    except zipfile.BadZipFile:
        raise HTTPException(400, "Archivo .nsupdate corrupto o no es un ZIP valido.")
    except Exception as e:
        logger.exception("Error aplicando actualizacion")
        raise HTTPException(500, f"Error al aplicar actualizacion: {e}")
    finally:
        if tmp and tmp.exists():
            tmp.unlink(missing_ok=True)

    # 6) Audit log: trazabilidad no repudiable (Resolución 1995/1999)
    try:
        entry = AuditLogORM(
            ts=datetime.now(UTC),
            actor_id=str(getattr(admin, "id", "")) or None,
            actor_label=(getattr(admin, "username", "") or "")[:120] or None,
            action="update_applied",
            entity_type="system",
            entity_id=None,
            summary=(f"Actualizacion v{version} aplicada "
                     f"({file.filename}, {len(content)} bytes)")[:300],
            changes=json.dumps(
                {
                    "version": version,
                    "filename": file.filename,
                    "tamano_bytes": len(content),
                    "sha256": file_sha256,
                    "manifest": {k: v for k, v in manifest.items() if k in ("version", "fecha", "frontend_hash")},
                },
                ensure_ascii=False,
            )[:20000],
            ip=(request.client.host if request.client else None),
        )
        db.add(entry)
        db.commit()
    except Exception as _exc:
        # Si falla el audit, NO revertimos la actualizacion (ya se aplicó);
        # solo lo loggeamos para investigación.
        logger.exception("No se pudo registrar audit de actualizacion: %s", _exc)

    return {
        "ok": True,
        "version": version,
        "mensaje": f"Actualizacion v{version} aplicada. Reiniciando servidor...",
        "sha256": file_sha256,
    }
