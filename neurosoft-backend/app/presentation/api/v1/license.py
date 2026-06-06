"""
app/presentation/api/v1/license.py
====================================
§BLINDAJE-N1 — Endpoints de estado y activación de licencia.
"""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.infrastructure.license_manager import get_license_status

license_router = APIRouter(prefix="/license", tags=["Licencia"])


class ActivateRequest(BaseModel):
    key: str


class TrialRequest(BaseModel):
    days: int = 14


@license_router.get("/agreement-status", summary="Estado del acuerdo de uso (por equipo)")
def agreement_status():
    from app.infrastructure.install_agreement import get_agreement_status

    return get_agreement_status()


class AgreementAcceptRequest(BaseModel):
    user_name: str | None = None
    documento: str | None = None
    tarjeta_profesional: str | None = None


@license_router.post("/accept-agreement", summary="Registrar aceptación del acuerdo de uso")
def accept_agreement(req: AgreementAcceptRequest):
    from app.infrastructure.install_agreement import accept_agreement as _accept

    return {
        "status": "ok",
        "agreement": _accept(
            user_name=req.user_name,
            documento=req.documento,
            tarjeta_profesional=req.tarjeta_profesional,
        ),
    }


@license_router.get("/status", summary="Estado actual de la licencia")
def license_status():
    """Retorna el estado de la licencia: tipo, validez, días restantes, watermark."""
    lic = get_license_status()
    return lic.to_dict()


@license_router.post("/activate", summary="Activar licencia con clave")
def activate_license(req: ActivateRequest):
    """Activa una licencia a partir de una clave NSFT-XXXX-XXXX-XXXX-XXXX."""
    lic = get_license_status()
    success, message = lic.activate(req.key)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"status": "ok", "message": message, "license": lic.to_dict()}


@license_router.post("/trial", summary="Iniciar prueba gratuita")
def start_trial(req: TrialRequest):
    """Inicia un período de prueba gratuito."""
    lic = get_license_status()
    if lic.is_valid and not lic.is_trial:
        raise HTTPException(status_code=409, detail="Ya tienes una licencia activa. No necesitas prueba.")
    success = lic.start_trial(req.days)
    if not success:
        raise HTTPException(status_code=500, detail="Error al iniciar la prueba.")
    return {"status": "ok", "message": f"Prueba de {req.days} días iniciada.", "license": lic.to_dict()}
