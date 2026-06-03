"""
app/presentation/api/v1/errors.py
====================================
Recepcion de crash reports desde el frontend (ErrorBoundary).

Los errores se guardan en un archivo de log rotativo para que:
  1. El desarrollador pueda diagnosticar bugs reportados por beta testers
  2. No dependa de la BD (si la BD esta rota, igual se registra el crash)

Formato: JSON lines (un objeto JSON por linea) en data/crash_reports.jsonl
"""

import json
import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

errors_router = APIRouter(prefix="/errors", tags=["Sistema"])


class CrashReportDTO(BaseModel):
    error_message: str = Field(..., description="Mensaje del error (error.message)")
    error_stack: str = Field("", description="Stack trace (primeros 2000 chars)")
    route: str = Field("", description="Ruta donde ocurrio el crash")
    component_stack: str = Field("", description="Component stack de React")
    app_version: str = Field("", description="Version de la app (si esta disponible)")
    user_agent: str = Field("", description="Navegador / WebView info")


@errors_router.post("", summary="Registrar crash del frontend")
def report_crash(request: Request, report: CrashReportDTO):
    """
    Recibe un crash report desde el ErrorBoundary del frontend.

    No lanza excepciones — si falla el guardado, solo loggea.
    Esto asegura que un crash durante el reporte de crash no
    genere un loop infinito.
    """
    entry = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "error": report.error_message[:500],
        "stack": report.error_stack[:2000],
        "route": report.route[:200],
        "component_stack": report.component_stack[:1000] if report.component_stack else None,
        "version": report.app_version or "unknown",
        "ua": report.user_agent[:200],
        "ip": request.client.host if request.client else None,
    }

    try:
        from pathlib import Path
        log_path = Path("data") / "crash_reports.jsonl"
        log_path.parent.mkdir(parents=True, exist_ok=True)

        with open(log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logger.info("Crash report recibido: %s", report.error_message[:80])
    except Exception as exc:
        logger.warning("No se pudo guardar crash report: %s", exc)

    return {"received": True}
